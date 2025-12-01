import os
import uuid
from sqlalchemy.orm import Session
from app.core.validators import validate_nickname
from app.core.exceptions import bad_request, conflict, unauthorized, payload_too_large
from app.core.error_codes import ErrorCode
from app.models.db import User, Post, Comment, PostLike
from app.schemas import NicknamePatchReq, PasswordUpdateReq

UPLOAD_DIR = os.path.abspath("./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def upload_profile_image_controller(file_content_type: str, file_data: bytes, filename: str):
    """프로필 이미지 업로드 컨트롤러"""
    if not file_data:
        raise bad_request("file_required", ErrorCode.FILE_REQUIRED)
    
    if file_content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise bad_request("invalid_file_type", ErrorCode.INVALID_FILE_TYPE, {"allowed": ["jpg", "png", "jpeg"]})
    
    if len(file_data) > 5 * 1024 * 1024:
        raise payload_too_large("file_too_large", ErrorCode.FILE_TOO_LARGE, {"max_size": "5MB"})
    
    name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, name)
    
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    # 실제 서빙되는 URL 반환 (로컬 개발 환경)
    # 프로덕션에서는 실제 CDN URL로 변경 필요
    url = f"http://localhost:8101/uploads/{name}"
    return {"profile_image_url": url}


def update_profile_controller(req: NicknamePatchReq, user_id: int, db: Session):
    """프로필(닉네임, 프로필 이미지) 수정 컨트롤러"""
    validate_nickname(req.nickname, raise_validation_failed=True)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise unauthorized("unauthorized_user", ErrorCode.UNAUTHORIZED)
    
    # 중복 검사 (본인 닉네임은 허용)
    existing_user = db.query(User).filter(User.nickname == req.nickname).first()
    if existing_user and existing_user.id != user_id:
        raise conflict("duplicate_nickname", ErrorCode.DUPLICATE_NICKNAME)
    
    user.nickname = req.nickname
    # 프로필 이미지 URL이 제공된 경우 업데이트
    if req.profile_image_url is not None:
        user.profile_image_url = req.profile_image_url
    
    db.commit()
    db.refresh(user)
    
    return {
        "nickname": user.nickname,
        "profile_image_url": user.profile_image_url
    }


def delete_user_controller(user_id: int, db: Session):
    """회원 탈퇴 컨트롤러"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise unauthorized("unauthorized_user", ErrorCode.UNAUTHORIZED)
    
    # CASCADE로 인해 관련 데이터 자동 삭제됨
    # (posts, comments, post_likes는 외래키 CASCADE 설정됨)
    
    db.delete(user)
    db.commit()
    
    return None


def update_password_controller(req: PasswordUpdateReq, user_id: int, db: Session):
    """비밀번호 변경 컨트롤러"""
    from app.core.validators import validate_password_pair
    
    validate_password_pair(req.password, req.password_check, raise_validation_failed=True)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise unauthorized("unauthorized_user", ErrorCode.UNAUTHORIZED)
    
    if user.password != req.old_password:
        raise bad_request("invalid_credentials", ErrorCode.INVALID_CREDENTIALS)
    
    user.password = req.password
    db.commit()
    
    return None
