import os
import uuid
from app.core.validators import validate_title
from app.core.exceptions import bad_request, not_found, forbidden, unprocessable, unauthorized
from app.models.memory import POSTS, COMMENTS, COUNTERS, LIKES, USERS, Post
from app.schemas import PostCreateReq, PostUpdateReq
from app.services.model_client import predict_image, summarize_text, auto_tag_text, analyze_sentiment

UPLOAD_DIR = os.path.abspath("./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def create_post_controller(req: PostCreateReq, user_id: int):
    """게시글 작성 컨트롤러"""
    if user_id not in USERS:
        raise unauthorized()

    if not req.title or not req.content:
        raise unprocessable("missing_fields", {"required": ["title", "content"]})
    
    validate_title(req.title)
    
    pid = COUNTERS["post"]
    COUNTERS["post"] += 1
    
    # AI 서비스 호출 (비동기 병렬 처리 가능하지만 여기선 순차 호출)
    tags = await auto_tag_text(req.content)
    summary_res = await summarize_text(req.content)
    summary = summary_res.get("summary") if summary_res else None
    
    sentiment_res = await analyze_sentiment(req.content)
    sentiment_score = None
    sentiment_label = None
    if sentiment_res:
        sentiment_score = sentiment_res.get("confidence")
        sentiment_label = sentiment_res.get("label")

    post = Post(
        id=pid,
        user_id=user_id,
        title=req.title,
        content=req.content,
        image_url=str(req.image_url) if req.image_url else None,
        board_type=req.board_type,
        tags=tags,
        summary=summary,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        like_count=0,
        view_count=0
    )
    
    POSTS[pid] = post
    return {"post_id": pid}


def get_posts_controller(page: int = 1, limit: int = 10, user_id: int = None, board_type: str = "couple"):
    """게시글 목록 조회 컨트롤러"""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10
    
    # board_type 필터링
    all_posts = [p for p in POSTS.values() if p.board_type == board_type]
    total = len(all_posts)
    
    # 최신순 정렬 (ID 역순)
    sorted_posts = sorted(all_posts, key=lambda x: x.id, reverse=True)
    
    # 페이지네이션
    start = (page - 1) * limit
    end = start + limit
    paginated_posts = sorted_posts[start:end]
    
    posts_data = []
    for post in paginated_posts:
        user = USERS.get(post.user_id)
        comment_count = len([c for c in COMMENTS.values() if c.post_id == post.id])
        
        # 좋아요 여부 확인
        liked = False
        if user_id and post.id in LIKES:
            liked = user_id in LIKES[post.id]
        
        posts_data.append({
            "post_id": post.id,
            "user_id": post.user_id,
            "nickname": user.nickname if user else "알 수 없음",
            "title": post.title,
            "content": post.content,
            "image_url": post.image_url,
            "board_type": post.board_type,
            "tags": post.tags,
            "summary": post.summary,
            "sentiment_label": post.sentiment_label,
            "like_count": post.like_count,
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


def get_post_controller(post_id: int, user_id: int = None):
    """게시글 상세 조회 컨트롤러"""
    post = POSTS.get(post_id)
    if not post:
        raise not_found("post_not_found")
    
    user = USERS.get(post.user_id)
    comments = [c for c in COMMENTS.values() if c.post_id == post.id]
    
    # 댓글 정보 포함
    comments_data = []
    for comment in comments:
        comment_user = USERS.get(comment.user_id)
        comments_data.append({
            "comment_id": comment.id,
            "user_id": comment.user_id,
            "nickname": comment_user.nickname if comment_user else "알 수 없음",
            "content": comment.content
        })
    
    liked = False
    if user_id and post_id in LIKES:
        liked = user_id in LIKES[post_id]
    
    return {
        "post_id": post.id,
        "user_id": post.user_id,
        "nickname": user.nickname if user else "알 수 없음",
        "title": post.title,
        "content": post.content,
        "image_url": post.image_url,
        "board_type": post.board_type,
        "tags": post.tags,
        "summary": post.summary,
        "sentiment_label": post.sentiment_label,
        "like_count": post.like_count,
        "view_count": post.view_count,
        "liked": liked,
        "comments": comments_data
    }


def update_post_controller(post_id: int, req: PostUpdateReq, user_id: int):
    """게시글 수정 컨트롤러"""
    if not req or all(
        field is None for field in (req.title, req.content, req.image_url)
    ):
        raise bad_request("invalid_request")

    post = POSTS.get(post_id)
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
    
    return {"post_id": post_id}


def delete_post_controller(post_id: int, user_id: int):
    """게시글 삭제 컨트롤러"""
    post = POSTS.get(post_id)
    if not post:
        raise not_found("post_not_found")
    
    if post.user_id != user_id:
        raise forbidden()
    
    # 관련 댓글 삭제
    comments_to_delete = [cid for cid, c in COMMENTS.items() if c.post_id == post_id]
    for cid in comments_to_delete:
        COMMENTS.pop(cid, None)
    
    # 좋아요 정보 삭제
    LIKES.pop(post_id, None)
    
    POSTS.pop(post_id, None)
    return {"post_id": post_id}


def toggle_like_controller(post_id: int, user_id: int):
    """좋아요 토글 컨트롤러"""
    post = POSTS.get(post_id)
    if not post:
        raise not_found("post_not_found")
    
    LIKES.setdefault(post_id, set())
    
    if user_id in LIKES[post_id]:
        LIKES[post_id].remove(user_id)
        liked = False
    else:
        LIKES[post_id].add(user_id)
        liked = True
    
    post.like_count = len(LIKES[post_id])
    
    return {
        "post_id": post_id,
        "like_count": post.like_count,
        "liked": liked
    }


def increment_view_controller(post_id: int):
    """조회수 증가 컨트롤러"""
    post = POSTS.get(post_id)
    if not post:
        raise not_found("post_not_found")
    
    post.view_count += 1
    return {
        "post_id": post_id,
        "view_count": post.view_count
    }


async def upload_post_image_controller(file_content_type: str, file_data: bytes, filename: str):
    """게시글 이미지 업로드 컨트롤러 + 이미지 분류"""
    from app.core.exceptions import payload_too_large
    
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
