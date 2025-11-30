import os
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.validators import validate_title
from app.core.exceptions import bad_request, not_found, forbidden, unprocessable, unauthorized, payload_too_large
from app.models.db import Post, PostLike, Tag, User, Comment
from app.schemas import PostCreateReq, PostUpdateReq
from app.services.model_client import predict_image, summarize_text, auto_tag_text, analyze_sentiment
from app.services import post_vector_service

UPLOAD_DIR = os.path.abspath("./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def create_post_controller(req: PostCreateReq, user_id: int, db: Session):
    """게시글 작성 컨트롤러"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise unauthorized()

    if not req.title or not req.content:
        raise unprocessable("missing_fields", {"required": ["title", "content"]})
    
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

    post = Post(
        user_id=user_id,
        title=req.title,
        content=req.content,
        image_url=str(req.image_url) if req.image_url else None,
        board_type=req.board_type,
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


def get_posts_controller(page: int = 1, limit: int = 10, user_id: int = None, board_type: str = "couple", db: Session = None):
    """게시글 목록 조회 컨트롤러"""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10
    
    offset = (page - 1) * limit
    
    # Total count
    total = db.query(func.count(Post.id)).filter(Post.board_type == board_type).scalar()
    
    # Query posts
    posts = db.query(Post).filter(Post.board_type == board_type)\
        .order_by(Post.created_at.desc())\
        .offset(offset).limit(limit).all()
    
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
        
        posts_data.append({
            "post_id": post.id,
            "user_id": post.user_id,
            "nickname": post.user.nickname if post.user else "알 수 없음",
            "title": post.title,
            "content": post.content,
            "image_url": post.image_url,
            "board_type": post.board_type,
            "tags": [t.name for t in post.tags],
            "summary": post.summary,
            "sentiment_label": post.sentiment_label,
            "like_count": like_count,
            "view_count": post.view_count,
            "comment_count": comment_count,
            "liked": liked
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
        raise not_found("post_not_found")
    
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
        field is None for field in (req.title, req.content, req.image_url)
    ):
        raise bad_request("invalid_request")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise not_found("post_not_found")
    
    if post.user_id != user_id:
        raise forbidden()
    
    if req.title is not None:
        validate_title(req.title)
        post.title = req.title
    
    if req.content is not None:
        post.content = req.content
    
    if req.image_url is not None:
        post.image_url = str(req.image_url)
    
    db.commit()
    db.refresh(post)
    
    return {"post_id": post_id}


def delete_post_controller(post_id: int, user_id: int, db: Session):
    """게시글 삭제 컨트롤러"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise not_found("post_not_found")
    
    if post.user_id != user_id:
        raise forbidden()
    
    # CASCADE로 인해 관련 댓글과 좋아요는 자동 삭제됨
    db.delete(post)
    db.commit()
    
    return {"post_id": post_id}


def toggle_like_controller(post_id: int, user_id: int, db: Session):
    """좋아요 토글 컨트롤러"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise not_found("post_not_found")
    
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
        raise not_found("post_not_found")
    
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
        raise bad_request("invalid_file_type", {"allowed": ["jpg", "png", "jpeg"]})
    
    if len(file_data) > 5 * 1024 * 1024:
        raise payload_too_large("file_too_large", {"max_size": "5MB"})
    
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
