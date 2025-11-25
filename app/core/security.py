from datetime import datetime, timedelta
from typing import Optional
from fastapi import Header, HTTPException, status
from jose import JWTError, jwt
from app.core.exceptions import unauthorized
from app.core.database import get_db
from app.models.db import User
from sqlalchemy.orm import Session

# JWT 설정
SECRET_KEY = "wedding-os-secret-key-change-in-production"  # TODO: 환경 변수로 변경
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증 및 디코딩"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user_id(
    authorization: Optional[str] = Header(None)
) -> int:
    """JWT 토큰에서 user_id 추출 (필수 인증)"""
    if not authorization:
        raise unauthorized()
    
    # "Bearer <token>" 형식에서 토큰 추출
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise unauthorized()
    except ValueError:
        raise unauthorized()
    
    payload = verify_token(token)
    if not payload:
        raise unauthorized()
    
    user_id = payload.get("sub")  # JWT 표준에서 subject는 user_id
    if not user_id:
        raise unauthorized()
    
    return int(user_id)


async def get_current_user_id_optional(
    authorization: Optional[str] = Header(None)
) -> Optional[int]:
    """JWT 토큰에서 user_id 추출 (선택적, 로그인 안 해도 됨)"""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None
    
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    return int(user_id)
