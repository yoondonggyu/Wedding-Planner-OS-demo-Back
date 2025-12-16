import os
import uuid
from pathlib import Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from app.core.validators import validate_title
from app.core.exceptions import bad_request, not_found, forbidden, unprocessable, unauthorized, payload_too_large
from app.core.error_codes import ErrorCode
from app.models.db import Post, PostLike, Tag, User, Comment
from app.schemas import PostCreateReq, PostUpdateReq
from app.services.model_client import predict_image, summarize_text, auto_tag_text, analyze_sentiment
from app.services import post_vector_service, ocr_service
from app.core.couple_helpers import get_user_couple_id, get_couple_filter_with_user

UPLOAD_DIR = os.path.abspath("./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
UPLOAD_BASE_URL = os.getenv("UPLOAD_BASE_URL", "http://localhost:8000").rstrip("/")
MAX_VAULT_FILE_SIZE = 10 * 1024 * 1024  # 10MB
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif", ".tif", ".tiff", ".heic"}


def _is_image_file(filename: str, content_type: str | None) -> bool:
    if content_type and content_type.lower().startswith("image/"):
        return True
    suffix = Path(filename or "").suffix.lower()
    return suffix in IMAGE_EXTENSIONS


def _build_upload_url(filename: str) -> str:
    return f"{UPLOAD_BASE_URL}/uploads/{filename}"


async def create_post_controller(req: PostCreateReq, user_id: int, db: Session):
    """게시글 작성 컨트롤러"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise unauthorized("unauthorized_user", ErrorCode.UNAUTHORIZED)

    if not req.title or not req.content:
        raise unprocessable("missing_fields", ErrorCode.MISSING_FIELDS, {"required": ["title", "content"]})
    
    validate_title(req.title)
    
    # AI 서비스 호출 (실패해도 게시글 작성은 성공)
    tags_list = []
    summary = None
    sentiment_score = None
    sentiment_label = None
    
    try:
        tags_list = await auto_tag_text(req.content)
        if not tags_list:
            tags_list = []
        print(f"✅ 자동 태그 생성 성공: {tags_list}")
    except Exception as e:
        print(f"⚠️ 자동 태그 생성 실패 (게시글 작성은 계속 진행): {e}")
        tags_list = []
    
    try:
        summary_res = await summarize_text(req.content)
        summary = summary_res.get("summary") if summary_res else None
        if summary:
            print(f"✅ 요약 생성 성공: {summary[:50]}...")
    except Exception as e:
        print(f"⚠️ 요약 생성 실패 (게시글 작성은 계속 진행): {e}")
        summary = None
    
    try:
        sentiment_res = await analyze_sentiment(req.content)
        if sentiment_res:
            sentiment_score = sentiment_res.get("confidence")
            sentiment_label = sentiment_res.get("label")
            print(f"✅ 감성 분석 성공: {sentiment_label} (신뢰도: {sentiment_score})")
    except Exception as e:
        print(f"⚠️ 감성 분석 실패 (게시글 작성은 계속 진행): {e}")
        sentiment_score = None
        sentiment_label = None

    # Handle Tags
    db_tags = []
    if tags_list:  # tags_list가 None이 아니고 비어있지 않을 때만 처리
        for tag_name in tags_list:
            if tag_name and tag_name.strip():  # 빈 문자열 체크
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.flush()  # Get ID
                db_tags.append(tag)

    # 커플 ID 가져오기
    couple_id = get_user_couple_id(user_id, db)
    
    # 카테고리 검증
    from app.core.categories import is_valid_category
    category = req.category if req.category and is_valid_category(req.category) else None
    
    # vendor_id 검증 (제공된 경우)
    vendor_id = None
    if req.vendor_id:
        from app.models.db.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.id == req.vendor_id).first()
        if vendor:
            vendor_id = req.vendor_id
    
    post = Post(
        user_id=user_id,
        couple_id=couple_id,  # 커플 공유
        vendor_id=vendor_id,  # 업체 연결 (리뷰 작성 시)
        title=req.title,
        content=req.content,
        image_url=str(req.image_url) if req.image_url else None,
        board_type=req.board_type,
        category=category,  # 카테고리 추가
        tags=db_tags,
        summary=summary,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        view_count=0
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # 게시글 벡터화 (비동기, 실패해도 게시글 작성은 성공)
    try:
        post_vector_service.vectorize_post(post)
        print(f"✅ 게시글 벡터화 완료: post_id={post.id}")
    except Exception as e:
        print(f"⚠️ 게시글 벡터화 실패 (게시글 작성은 계속 진행): {e}")
    
    return {"post_id": post.id}


def get_posts_controller(page: int = 1, limit: int = 10, user_id: int = None, board_type: str = "couple", category: str = None, vendor_type: str = None, db: Session = None):
    """게시글 목록 조회 컨트롤러 (커플 데이터 공유)"""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10
    
    offset = (page - 1) * limit
    
    # "커플 전용 공간" (private)과 "문서 보관함" (vault)은 커플이 연결된 사용자만 조회 가능
    if board_type == "private" or board_type == "vault":
        if not user_id:
            # 로그인하지 않은 경우 빈 결과 반환
            return {
                "posts": [],
                "total": 0,
                "page": page,
                "limit": limit
            }
        
        # 커플이 연결되어 있는지 확인
        couple_id = get_user_couple_id(user_id, db)
        if not couple_id:
            # 커플이 연결되어 있지 않은 경우 빈 결과 반환
            return {
                "posts": [],
                "total": 0,
                "page": page,
                "limit": limit
            }
        
        # 커플 전용 공간/문서 보관함은 해당 couple_id의 게시글만 조회
        total = db.query(func.count(Post.id)).filter(
            Post.board_type == board_type,
            Post.couple_id == couple_id
        ).scalar()
        
        posts = db.query(Post).filter(
            Post.board_type == board_type,
            Post.couple_id == couple_id
        ).order_by(Post.created_at.desc())\
        .offset(offset).limit(limit).all()
    else:
        # 공개 게시판 타입 (couple, planner, venue_review) - 모든 사용자가 볼 수 있음
        # 로그인 여부와 관계없이 전체 게시글 조회
        from app.models.db.vendor import Vendor, VendorType
        from sqlalchemy.orm import joinedload
        from app.core.categories import is_valid_category
        
        query = db.query(Post).options(joinedload(Post.vendor)).filter(Post.board_type == board_type)
        count_query = db.query(func.count(Post.id)).filter(Post.board_type == board_type)
        
        # category 필터 적용
        if category and is_valid_category(category):
            query = query.filter(Post.category == category)
            count_query = count_query.filter(Post.category == category)
        
        # vendor_type 필터 적용
        if vendor_type:
            try:
                vendor_type_enum = VendorType(vendor_type)
                # Post.vendor_id를 통해 Vendor를 join
                query = query.join(Vendor, Post.vendor_id == Vendor.id).filter(Vendor.vendor_type == vendor_type_enum)
                count_query = count_query.join(Vendor, Post.vendor_id == Vendor.id).filter(Vendor.vendor_type == vendor_type_enum)
            except ValueError:
                # 잘못된 vendor_type인 경우 필터링하지 않음
                pass
        
        total = count_query.scalar()
        posts = query.order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
    
    posts_data = []
    for post in posts:
        comment_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()
        
        # 좋아요 개수 계산
        like_count = db.query(func.count(PostLike.id)).filter(PostLike.post_id == post.id).scalar()
        
        liked = False
        if user_id:
            like_exists = db.query(PostLike).filter(
                PostLike.post_id == post.id, 
                PostLike.user_id == user_id
            ).first()
            if like_exists:
                liked = True
        
        # vendor 정보 추가
        vendor_data = None
        if post.vendor:
            vendor_data = {
                "id": post.vendor.id,
                "name": post.vendor.name,
                "vendor_type": post.vendor.vendor_type.value if hasattr(post.vendor.vendor_type, 'value') else str(post.vendor.vendor_type)
            }
        
        posts_data.append({
            "post_id": post.id,
            "user_id": post.user_id,
            "nickname": post.user.nickname if post.user else "알 수 없음",
            "title": post.title,
            "content": post.content,
            "image_url": post.image_url,
            "board_type": post.board_type,
            "category": post.category,  # 카테고리 추가
            "tags": [t.name for t in post.tags],
            "summary": post.summary,
            "sentiment_label": post.sentiment_label,
            "like_count": like_count,
            "view_count": post.view_count,
            "comment_count": comment_count,
            "liked": liked,
            "vendor": vendor_data
        })
    
    return {
        "posts": posts_data,
        "total": total,
        "page": page,
        "limit": limit
    }


def get_post_controller(post_id: int, user_id: int = None, db: Session = None):
    """게시글 상세 조회 컨트롤러"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise not_found("post_not_found", ErrorCode.POST_NOT_FOUND)
    
    # "커플 전용 공간" (private)과 "문서 보관함" (vault)은 커플이 연결된 사용자만 조회 가능
    if post.board_type == "private" or post.board_type == "vault":
        if not user_id:
            raise forbidden("forbidden", ErrorCode.FORBIDDEN)
        
        # 커플이 연결되어 있는지 확인
        couple_id = get_user_couple_id(user_id, db)
        if not couple_id or post.couple_id != couple_id:
            # 커플이 연결되어 있지 않거나 다른 커플의 게시글인 경우 접근 불가
            raise forbidden("forbidden", ErrorCode.FORBIDDEN)
    
    # 공개 게시판(couple, planner, venue_review)은 로그인한 사용자만 상세 조회 가능
    if post.board_type in ["couple", "planner", "venue_review"]:
        if not user_id:
            raise forbidden("forbidden", ErrorCode.FORBIDDEN, {"error": "로그인이 필요한 기능입니다."})
    
    liked = False
    if user_id:
        like_exists = db.query(PostLike).filter(
            PostLike.post_id == post_id, 
            PostLike.user_id == user_id
        ).first()
        if like_exists:
            liked = True
    
    # 조회수 증가
    post.view_count += 1
    db.commit()
    
    comments_data = []
    for comment in post.comments:
        comments_data.append({
            "comment_id": comment.id,
            "user_id": comment.user_id,
            "nickname": comment.user.nickname if comment.user else "알 수 없음",
            "content": comment.content
        })
    
    like_count = db.query(func.count(PostLike.id)).filter(PostLike.post_id == post_id).scalar()
    
    return {
        "post_id": post.id,
        "user_id": post.user_id,
        "nickname": post.user.nickname if post.user else "알 수 없음",
        "title": post.title,
        "content": post.content,
        "image_url": post.image_url,
        "board_type": post.board_type,
        "category": post.category,  # 카테고리 추가
        "tags": [t.name for t in post.tags],
        "summary": post.summary,
        "sentiment_label": post.sentiment_label,
        "like_count": like_count,
        "view_count": post.view_count,
        "liked": liked,
        "comments": comments_data
    }


def update_post_controller(post_id: int, req: PostUpdateReq, user_id: int, db: Session):
    """게시글 수정 컨트롤러"""
    if not req or all(
        field is None for field in (req.title, req.content, req.image_url, req.category)
    ):
        raise bad_request("invalid_request", ErrorCode.INVALID_REQUEST)

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise not_found("post_not_found", ErrorCode.POST_NOT_FOUND)
    
    if post.user_id != user_id:
        raise forbidden("forbidden", ErrorCode.FORBIDDEN)
    
    if req.title is not None:
        validate_title(req.title)
        post.title = req.title
    
    if req.content is not None:
        post.content = req.content
    
    if req.image_url is not None:
        post.image_url = str(req.image_url)
    
    # 카테고리 업데이트
    if req.category is not None:
        from app.core.categories import is_valid_category
        if req.category and is_valid_category(req.category):
            post.category = req.category
        elif req.category == "":  # 빈 문자열이면 NULL로 설정
            post.category = None
    
    db.commit()
    db.refresh(post)
    
    return {"post_id": post_id}


def delete_post_controller(post_id: int, user_id: int, db: Session):
    """게시글 삭제 컨트롤러"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise not_found("post_not_found", ErrorCode.POST_NOT_FOUND)
    
    if post.user_id != user_id:
        raise forbidden("forbidden", ErrorCode.FORBIDDEN)
    
    # CASCADE로 인해 관련 댓글과 좋아요는 자동 삭제됨
    db.delete(post)
    db.commit()
    
    return {"post_id": post_id}


def toggle_like_controller(post_id: int, user_id: int, db: Session):
    """좋아요 토글 컨트롤러"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise not_found("post_not_found", ErrorCode.POST_NOT_FOUND)
    
    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == user_id
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        liked = False
    else:
        new_like = PostLike(post_id=post_id, user_id=user_id)
        db.add(new_like)
        liked = True
    
    db.commit()
    
    # 좋아요 개수 계산
    like_count = db.query(func.count(PostLike.id)).filter(PostLike.post_id == post_id).scalar()
    
    return {
        "post_id": post_id,
        "like_count": like_count,
        "liked": liked
    }


def increment_view_controller(post_id: int, db: Session):
    """조회수 증가 컨트롤러"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise not_found("post_not_found", ErrorCode.POST_NOT_FOUND)
    
    post.view_count += 1
    db.commit()
    db.refresh(post)
    
    return {
        "post_id": post_id,
        "view_count": post.view_count
    }


async def upload_post_image_controller(file_content_type: str, file_data: bytes, filename: str):
    """게시글 이미지 업로드 컨트롤러 + 이미지 분류"""
    if file_content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise bad_request("invalid_file_type", ErrorCode.INVALID_FILE_TYPE, {"allowed": ["jpg", "png", "jpeg"]})
    
    if len(file_data) > 5 * 1024 * 1024:
        raise payload_too_large("file_too_large", ErrorCode.FILE_TOO_LARGE, {"max_size": "5MB"})
    
    name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, name)
    
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    url = f"https://cdn.example.com/{name}"
    
    # 🎯 Model API 호출 (이미지 분류) - 비동기로 처리
    prediction_result = None
    prediction_error = None
    try:
        prediction = await predict_image(file_data, filename)
        if prediction:
            class_name = prediction.get("class_name", "Unknown")
            confidence = prediction.get("confidence_score", 0)
            prediction_result = {
                "class_name": class_name,
                "confidence_score": confidence
            }
            print(f"✅ 이미지 분류 결과: {class_name} (신뢰도: {confidence:.2%})")
        else:
            from app.services.model_client import get_model_api_base_url
            current_url = get_model_api_base_url()
            current_port = current_url.split(":")[-1].split("/")[0]
            prediction_error = f"Model API가 None을 반환했습니다. Model API 서버(포트 {current_port})가 실행 중인지 확인하세요."
            print(f"⚠️ {prediction_error}")
    except Exception as e:
        # Model API 실패해도 업로드는 성공 처리
        prediction_error = f"Model API 호출 실패: {str(e)}"
        print(f"⚠️ 이미지 분류 실패 (업로드는 성공): {e}")
    
    result = {"image_url": url}
    if prediction_result:
        result["prediction"] = prediction_result  # Model API 결과 포함
    elif prediction_error:
        result["prediction_error"] = prediction_error  # 에러 정보 포함 (디버깅용)
    
    return result


async def upload_document_with_ocr_controller(
    file_content_type: str,
    file_data: bytes,
    filename: str,
    document_title: str,
    user_id: int,
    db: Session
):
    """문서 업로드 + OCR 처리 컨트롤러 (문서 보관함)"""
    if not file_data:
        raise bad_request("file_required", ErrorCode.FILE_REQUIRED)
    
    if len(file_data) > MAX_VAULT_FILE_SIZE:
        raise payload_too_large(
            "file_too_large",
            ErrorCode.FILE_TOO_LARGE,
            {"max_size": "10MB"}
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise unauthorized("unauthorized_user", ErrorCode.UNAUTHORIZED)
    
    couple_id = get_user_couple_id(user_id, db)
    if not couple_id:
        raise forbidden("couple_required", ErrorCode.FORBIDDEN)
    
    safe_filename = Path(filename or "document").name
    normalized_title = (document_title or "").strip()
    if not normalized_title:
        normalized_title = Path(safe_filename).stem or "문서"
    validate_title(normalized_title)
    
    stored_name = f"{uuid.uuid4().hex}_{safe_filename}"
    file_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(file_path, "wb") as dest:
        dest.write(file_data)
    file_url = _build_upload_url(stored_name)
    
    text, error = await ocr_service.extract_text_from_document(
        file_data=file_data,
        filename=safe_filename,
        content_type=file_content_type
    )
    
    if not text:
        return {
            "post_id": None,
            "ocr_text": None,
            "ocr_error": error or "문서에서 텍스트를 추출하지 못했습니다.",
            "file_url": file_url
        }
    
    content = text.strip()
    # 원본 파일 경로를 내용 상단에 추가하여 첨부파일 접근 경로를 제공
    content_with_source = f"[원본 파일] {file_url}\n\n{content}" if file_url else content
    
    summary = None
    try:
        summary_res = await summarize_text(content)
        summary = summary_res.get("summary") if summary_res else None
    except Exception as exc:
        print(f"⚠️ 문서 요약 실패: {exc}")
    
    tags_list = []
    try:
        tags_list = await auto_tag_text(content)
    except Exception as exc:
        print(f"⚠️ 문서 자동 태그 생성 실패: {exc}")
        tags_list = []
    
    db_tags = []
    if tags_list:
        for tag_name in tags_list:
            cleaned = (tag_name or "").strip()
            if not cleaned:
                continue
            tag = db.query(Tag).filter(Tag.name == cleaned).first()
            if not tag:
                tag = Tag(name=cleaned)
                db.add(tag)
                db.flush()
            db_tags.append(tag)
    
    post = Post(
        user_id=user_id,
        couple_id=couple_id,
        title=normalized_title,
        content=content_with_source,
        image_url=file_url if _is_image_file(safe_filename, file_content_type) else None,
        board_type="vault",
        category="document",
        summary=summary,
        tags=db_tags,
        sentiment_score=None,
        sentiment_label=None,
        view_count=0
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    try:
        post_vector_service.vectorize_post(post)
    except Exception as exc:
        print(f"⚠️ 문서 벡터화 실패 (post_id={post.id}): {exc}")
    
    return {
        "post_id": post.id,
        "title": post.title,
        "ocr_text": content,
        "summary": summary,
        "file_url": file_url,
        "ocr_error": None,
        "tags": [tag.name for tag in db_tags]
    }
