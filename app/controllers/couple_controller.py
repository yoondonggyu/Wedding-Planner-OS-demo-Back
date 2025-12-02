"""
커플 연결 컨트롤러
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Dict
from app.models.db import User, Couple, Gender, CoupleStatus
from app.schemas import CoupleConnectReq
from app.core.exceptions import bad_request, not_found, conflict
from app.core.error_codes import ErrorCode


def get_my_couple_key(user_id: int, db: Session) -> Dict:
    """자신의 커플 키 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise not_found("user_not_found", ErrorCode.USER_NOT_FOUND)
    
    if not user.couple_key:
        return {
            "message": "couple_key_not_generated",
            "data": {
                "error": "커플 키가 생성되지 않았습니다. 회원가입 시 성별을 선택해주세요."
            }
        }
    
    return {
        "message": "couple_key_retrieved",
        "data": {
            "couple_key": user.couple_key,
            "gender": user.gender.value if user.gender else None,
            "is_connected": user.couple_id is not None and db.query(Couple).filter(
                and_(
                    Couple.id == user.couple_id,
                    Couple.status == CoupleStatus.CONNECTED
                )
            ).first() is not None
        }
    }


def connect_couple(user_id: int, request: CoupleConnectReq, db: Session) -> Dict:
    """커플 연결 (상대방의 키 입력) - 양방향 확인 필요"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise not_found("user_not_found", ErrorCode.USER_NOT_FOUND)
    
    if not user.gender:
        raise bad_request("gender_not_set", ErrorCode.INVALID_GENDER, {"error": "성별이 설정되지 않았습니다."})
    
    if not user.couple_key:
        raise bad_request("couple_key_not_generated", ErrorCode.INVALID_COUPLE_KEY, {"error": "커플 키가 생성되지 않았습니다."})
    
    # 이미 연결되어 있는지 확인
    if user.couple_id:
        couple = db.query(Couple).filter(Couple.id == user.couple_id).first()
        if couple and couple.status == CoupleStatus.CONNECTED:
            raise conflict("couple_already_connected", ErrorCode.COUPLE_ALREADY_CONNECTED)
    
    # 상대방의 커플 키로 상대방 사용자 찾기
    partner_user = db.query(User).filter(User.couple_key == request.partner_couple_key).first()
    
    if not partner_user:
        raise bad_request("invalid_couple_key", ErrorCode.INVALID_COUPLE_KEY, {"error": "유효하지 않은 커플 키입니다."})
    
    # 자신의 키와 상대방의 키가 같은지 확인
    if partner_user.couple_key == user.couple_key:
        raise bad_request("cannot_connect_self", ErrorCode.INVALID_COUPLE_KEY, {"error": "자신의 키는 입력할 수 없습니다."})
    
    # 성별이 다른지 확인
    if partner_user.gender == user.gender:
        raise bad_request("same_gender", ErrorCode.INVALID_GENDER, {"error": "같은 성별끼리는 연결할 수 없습니다."})
    
    # 상대방의 Couple 찾기 (상대방이 user1인 Couple)
    partner_couple = db.query(Couple).filter(Couple.user1_id == partner_user.id).first()
    
    if not partner_couple:
        raise bad_request("invalid_couple_key", ErrorCode.INVALID_COUPLE_KEY, {"error": "상대방의 커플 정보를 찾을 수 없습니다."})
    
    # 사용자의 Couple 찾기 (사용자가 user1인 Couple)
    my_couple = db.query(Couple).filter(Couple.user1_id == user.id).first()
    
    # Couple이 없으면 생성 (회원가입 시 생성되지 않았을 수 있음)
    if not my_couple:
        my_couple = Couple(
            couple_key=user.couple_key,
            user1_id=user.id,
            status=CoupleStatus.PENDING
        )
        db.add(my_couple)
        db.commit()
        db.refresh(my_couple)
    
    # 양방향 확인 로직
    # 컬럼 존재 여부 확인
    has_entered_key_columns = hasattr(my_couple, 'user2_entered_key') and hasattr(partner_couple, 'user2_entered_key')
    
    if has_entered_key_columns:
        # 컬럼이 있는 경우: 양방향 확인 로직 사용
        # 사용자가 상대방의 키를 입력 → 내 Couple에 user2_entered_key 저장
        partner_key_upper = request.partner_couple_key.upper()
        my_couple.user2_entered_key = partner_key_upper
        
        # 양방향 확인: 
        # 1. 내가 상대방의 키를 입력했는지 (my_couple.user2_entered_key == partner_user.couple_key) ✓
        # 2. 상대방이 내 키를 입력했는지 (partner_couple.user2_entered_key == user.couple_key) ✓
        # 둘 다 True이면 연결 완료
        
        # 상대방이 이미 내 키를 입력했는지 확인 (상대방의 Couple에 user2_entered_key가 내 키인지)
        # 대소문자 구분 없이 비교
        my_key_upper = user.couple_key.upper() if user.couple_key else None
        partner_key_upper_check = partner_user.couple_key.upper() if partner_user.couple_key else None
        my_entered_upper = my_couple.user2_entered_key.upper() if my_couple.user2_entered_key else None
        partner_entered_upper = partner_couple.user2_entered_key.upper() if partner_couple.user2_entered_key else None
        
        # 양방향 확인: 내가 상대방 키를 입력했고, 상대방이 내 키를 입력했는지 확인
        if partner_entered_upper == my_key_upper and my_entered_upper == partner_key_upper_check:
            # 양방향 확인 완료 - 연결
            if not partner_couple.user2_id:
                partner_couple.user2_id = user.id
            partner_couple.status = CoupleStatus.CONNECTED
            partner_couple.connected_at = datetime.now()
            user.couple_id = partner_couple.id
            user.partner_couple_key = request.partner_couple_key
            partner_user.couple_id = partner_couple.id
            partner_user.partner_couple_key = user.couple_key
            
            # 매칭 완료 후 키 값 정리 (불필요한 데이터 제거)
            partner_couple.user1_entered_key = None
            partner_couple.user2_entered_key = None
            my_couple.user1_entered_key = None
            my_couple.user2_entered_key = None
            
            db.commit()
            db.refresh(partner_couple)
            return {
                "message": "couple_connected",
                "data": {
                    "couple_id": partner_couple.id,
                    "partner_id": partner_user.id,
                    "partner_nickname": partner_user.nickname,
                    "connected_at": partner_couple.connected_at.isoformat() if partner_couple.connected_at else None
                }
            }
        else:
            # 상대방이 아직 입력하지 않음 - 대기 상태
            db.commit()
            return {
                "message": "couple_pending",
                "data": {
                    "message": "상대방이 아직 코드를 입력하지 않았습니다. 상대방도 코드를 입력하면 연결됩니다.",
                    "waiting_for_partner": True
                }
            }
    else:
        # 컬럼이 없는 경우: 기존 방식으로 연결 (하위 호환성)
        # 한 명만 입력해도 연결 (기존 동작 유지)
        if not partner_couple.user2_id:
            partner_couple.user2_id = user.id
        partner_couple.status = CoupleStatus.CONNECTED
        partner_couple.connected_at = datetime.now()
        user.couple_id = partner_couple.id
        user.partner_couple_key = request.partner_couple_key
        partner_user.couple_id = partner_couple.id
        partner_user.partner_couple_key = user.couple_key
        
        # 매칭 완료 후 키 값 정리 (컬럼이 있으면)
        if hasattr(partner_couple, 'user1_entered_key'):
            partner_couple.user1_entered_key = None
        if hasattr(partner_couple, 'user2_entered_key'):
            partner_couple.user2_entered_key = None
        if hasattr(my_couple, 'user1_entered_key'):
            my_couple.user1_entered_key = None
        if hasattr(my_couple, 'user2_entered_key'):
            my_couple.user2_entered_key = None
        
        db.commit()
        db.refresh(partner_couple)
        return {
            "message": "couple_connected",
            "data": {
                "couple_id": partner_couple.id,
                "partner_id": partner_user.id,
                "partner_nickname": partner_user.nickname,
                "connected_at": partner_couple.connected_at.isoformat() if partner_couple.connected_at else None
            }
        }


def get_couple_info(user_id: int, db: Session) -> Dict:
    """커플 정보 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise not_found("user_not_found", ErrorCode.USER_NOT_FOUND)
    
    if not user.couple_id:
        return {
            "message": "couple_not_connected",
            "data": {
                "is_connected": False,
                "couple_key": user.couple_key
            }
        }
    
    couple = db.query(Couple).filter(Couple.id == user.couple_id).first()
    
    if not couple:
        return {
            "message": "couple_not_connected",
            "data": {
                "is_connected": False,
                "couple_key": user.couple_key
            }
        }
    
    # 상대방 찾기
    partner_id = couple.user2_id if couple.user1_id == user.id else couple.user1_id
    partner = db.query(User).filter(User.id == partner_id).first() if partner_id else None
    
    return {
        "message": "couple_info_retrieved",
        "data": {
            "is_connected": couple.status == CoupleStatus.CONNECTED,
            "couple_id": couple.id,
            "couple_key": user.couple_key,
            "partner": {
                "id": partner.id if partner else None,
                "nickname": partner.nickname if partner else None,
                "email": partner.email if partner else None,
                "gender": partner.gender.value if partner and partner.gender else None
            } if partner else None,
            "connected_at": couple.connected_at.isoformat() if couple.connected_at else None
        }
    }

