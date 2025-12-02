"""
커플 공유 헬퍼 함수
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.db import User, Couple, CoupleStatus


def get_user_couple_id(user_id: int, db: Session) -> int | None:
    """사용자의 couple_id 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # 커플이 연결되어 있는지 확인
    if user.couple_id:
        couple = db.query(Couple).filter(
            Couple.id == user.couple_id,
            Couple.status == CoupleStatus.CONNECTED
        ).first()
        if couple:
            return couple.id
    
    return None


def get_couple_user_ids(couple_id: int, db: Session) -> list[int]:
    """커플의 두 사용자 ID 리스트 반환"""
    couple = db.query(Couple).filter(Couple.id == couple_id).first()
    if not couple or couple.status != CoupleStatus.CONNECTED:
        return []
    
    user_ids = [couple.user1_id]
    if couple.user2_id:
        user_ids.append(couple.user2_id)
    
    return user_ids


def get_couple_filter(user_id: int, db: Session, model_class):
    """커플 데이터 조회를 위한 필터 생성 (자신 + 파트너 데이터)"""
    couple_id = get_user_couple_id(user_id, db)
    
    if couple_id:
        # 커플이 연결되어 있으면 couple_id로 필터링
        return model_class.couple_id == couple_id
    else:
        # 커플이 연결되어 있지 않으면 자신의 데이터만
        return model_class.user_id == user_id


def get_couple_filter_with_user(user_id: int, db: Session, model_class):
    """커플 데이터 조회를 위한 필터 생성 (user_id 또는 couple_id)"""
    couple_id = get_user_couple_id(user_id, db)
    
    if couple_id:
        # 커플이 연결되어 있으면 couple_id로 필터링 (파트너 데이터 포함)
        return model_class.couple_id == couple_id
    else:
        # 커플이 연결되어 있지 않으면 자신의 데이터만
        return model_class.user_id == user_id

