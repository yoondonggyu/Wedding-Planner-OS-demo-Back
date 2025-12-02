"""
디지털 초대장 및 축의금 결제 시스템 컨트롤러
"""
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.db import (
    DigitalInvitation, Payment, RSVP, GuestMessage,
    InvitationTheme, RSVPStatus, PaymentStatus, PaymentMethod,
    InvitationDesign
)
from app.core.couple_helpers import get_user_couple_id
from app.core.exceptions import not_found, bad_request
from app.core.error_codes import ErrorCode
from app.schemas import (
    DigitalInvitationCreateReq, DigitalInvitationUpdateReq,
    PaymentCreateReq, RSVPCreateReq, RSVPUpdateReq, GuestMessageCreateReq
)
import secrets
import string
from datetime import datetime


def generate_invitation_url() -> str:
    """고유한 초대장 URL 생성 (8자리 영문+숫자)"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))


def create_digital_invitation(user_id: int, request: DigitalInvitationCreateReq, db: Session) -> Dict:
    """디지털 초대장 생성"""
    couple_id = get_user_couple_id(user_id, db)
    
    # 청첩장 디자인 연결 확인
    invitation_design_id = request.invitation_design_id
    if invitation_design_id:
        design = db.query(InvitationDesign).filter(
            InvitationDesign.id == invitation_design_id,
            InvitationDesign.user_id == user_id
        ).first()
        if not design:
            raise not_found("design_not_found", ErrorCode.DESIGN_NOT_FOUND)
    
    # 고유 URL 생성
    invitation_url = generate_invitation_url()
    while db.query(DigitalInvitation).filter(DigitalInvitation.invitation_url == invitation_url).first():
        invitation_url = generate_invitation_url()
    
    # 날짜 변환
    wedding_date = datetime.strptime(request.wedding_date, "%Y-%m-%d")
    
    # 테마 검증
    try:
        theme = InvitationTheme(request.theme)
    except ValueError:
        raise bad_request("invalid_theme", ErrorCode.INVALID_REQUEST)
    
    invitation = DigitalInvitation(
        user_id=user_id,
        couple_id=couple_id,
        invitation_design_id=invitation_design_id,
        theme=theme,
        invitation_url=invitation_url,
        groom_name=request.groom_name,
        bride_name=request.bride_name,
        wedding_date=wedding_date,
        wedding_time=request.wedding_time,
        wedding_location=request.wedding_location,
        wedding_location_detail=request.wedding_location_detail,
        map_url=request.map_url,
        parking_info=request.parking_info,
        invitation_data=request.invitation_data or {}
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # 초대장 URL 생성
    base_url = "http://localhost:5173"  # 실제로는 환경 변수에서 가져오기
    full_url = f"{base_url}/invitation/{invitation_url}"
    
    return {
        "message": "digital_invitation_created",
        "data": {
            "id": invitation.id,
            "invitation_url": invitation_url,
            "full_url": full_url,
            "theme": invitation.theme.value
        }
    }


def get_digital_invitation(invitation_url: str, db: Session) -> Dict:
    """디지털 초대장 조회 (공개 접근)"""
    invitation = db.query(DigitalInvitation).filter(
        DigitalInvitation.invitation_url == invitation_url,
        DigitalInvitation.is_active == True
    ).first()
    
    if not invitation:
        raise not_found("invitation_not_found", ErrorCode.RESOURCE_NOT_FOUND)
    
    # 조회수 증가
    invitation.view_count += 1
    db.commit()
    
    return {
        "message": "invitation_retrieved",
        "data": {
            "id": invitation.id,
            "invitation_url": invitation.invitation_url,
            "theme": invitation.theme.value,
            "groom_name": invitation.groom_name,
            "bride_name": invitation.bride_name,
            "wedding_date": invitation.wedding_date.isoformat() if invitation.wedding_date else None,
            "wedding_time": invitation.wedding_time,
            "wedding_location": invitation.wedding_location,
            "wedding_location_detail": invitation.wedding_location_detail,
            "map_url": invitation.map_url,
            "parking_info": invitation.parking_info,
            "invitation_data": invitation.invitation_data,
            "view_count": invitation.view_count
        }
    }


def get_my_digital_invitations(user_id: int, db: Session) -> Dict:
    """내 디지털 초대장 목록 조회"""
    couple_id = get_user_couple_id(user_id, db)
    
    if couple_id:
        invitations = db.query(DigitalInvitation).filter(
            DigitalInvitation.couple_id == couple_id
        ).order_by(DigitalInvitation.created_at.desc()).all()
    else:
        invitations = db.query(DigitalInvitation).filter(
            DigitalInvitation.user_id == user_id
        ).order_by(DigitalInvitation.created_at.desc()).all()
    
    base_url = "http://localhost:5173"
    
    return {
        "message": "invitations_retrieved",
        "data": {
            "invitations": [
                {
                    "id": inv.id,
                    "invitation_url": inv.invitation_url,
                    "full_url": f"{base_url}/invitation/{inv.invitation_url}",
                    "theme": inv.theme.value,
                    "groom_name": inv.groom_name,
                    "bride_name": inv.bride_name,
                    "wedding_date": inv.wedding_date.isoformat() if inv.wedding_date else None,
                    "view_count": inv.view_count,
                    "is_active": inv.is_active,
                    "created_at": inv.created_at.isoformat() if inv.created_at else None
                }
                for inv in invitations
            ]
        }
    }


def update_digital_invitation(invitation_id: int, user_id: int, request: DigitalInvitationUpdateReq, db: Session) -> Dict:
    """디지털 초대장 수정"""
    invitation = db.query(DigitalInvitation).filter(
        DigitalInvitation.id == invitation_id,
        DigitalInvitation.user_id == user_id
    ).first()
    
    if not invitation:
        raise not_found("invitation_not_found", ErrorCode.RESOURCE_NOT_FOUND)
    
    if request.theme:
        try:
            invitation.theme = InvitationTheme(request.theme)
        except ValueError:
            raise bad_request("invalid_theme", ErrorCode.INVALID_REQUEST)
    
    if request.groom_name:
        invitation.groom_name = request.groom_name
    if request.bride_name:
        invitation.bride_name = request.bride_name
    if request.wedding_date:
        invitation.wedding_date = datetime.strptime(request.wedding_date, "%Y-%m-%d")
    if request.wedding_time is not None:
        invitation.wedding_time = request.wedding_time
    if request.wedding_location:
        invitation.wedding_location = request.wedding_location
    if request.wedding_location_detail is not None:
        invitation.wedding_location_detail = request.wedding_location_detail
    if request.map_url is not None:
        invitation.map_url = request.map_url
    if request.parking_info is not None:
        invitation.parking_info = request.parking_info
    if request.invitation_data:
        invitation.invitation_data = request.invitation_data
    if request.is_active is not None:
        invitation.is_active = request.is_active
    
    db.commit()
    db.refresh(invitation)
    
    return {
        "message": "invitation_updated",
        "data": {
            "id": invitation.id,
            "invitation_url": invitation.invitation_url,
            "theme": invitation.theme.value
        }
    }


def create_payment(invitation_id: int, request: PaymentCreateReq, db: Session) -> Dict:
    """축의금 결제 생성"""
    invitation = db.query(DigitalInvitation).filter(
        DigitalInvitation.id == invitation_id,
        DigitalInvitation.is_active == True
    ).first()
    
    if not invitation:
        raise not_found("invitation_not_found", ErrorCode.RESOURCE_NOT_FOUND)
    
    try:
        payment_method = PaymentMethod(request.payment_method)
    except ValueError:
        raise bad_request("invalid_payment_method", ErrorCode.INVALID_REQUEST)
    
    payment = Payment(
        invitation_id=invitation_id,
        payer_name=request.payer_name,
        payer_phone=request.payer_phone,
        payer_message=request.payer_message,
        amount=request.amount,
        payment_method=payment_method,
        payment_status=PaymentStatus.PENDING
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # 실제 결제는 여기서 결제 게이트웨이 API 호출
    # 데모용으로는 PENDING 상태로 저장
    
    return {
        "message": "payment_created",
        "data": {
            "id": payment.id,
            "amount": float(payment.amount),
            "payment_method": payment.payment_method.value,
            "payment_status": payment.payment_status.value
        }
    }


def create_rsvp(invitation_id: int, request: RSVPCreateReq, db: Session) -> Dict:
    """RSVP 생성/수정"""
    invitation = db.query(DigitalInvitation).filter(
        DigitalInvitation.id == invitation_id,
        DigitalInvitation.is_active == True
    ).first()
    
    if not invitation:
        raise not_found("invitation_not_found", ErrorCode.RESOURCE_NOT_FOUND)
    
    # 기존 RSVP 확인 (이름과 전화번호로)
    existing_rsvp = None
    if request.guest_phone:
        existing_rsvp = db.query(RSVP).filter(
            RSVP.invitation_id == invitation_id,
            RSVP.guest_phone == request.guest_phone
        ).first()
    elif request.guest_name:
        existing_rsvp = db.query(RSVP).filter(
            RSVP.invitation_id == invitation_id,
            RSVP.guest_name == request.guest_name
        ).first()
    
    try:
        status = RSVPStatus(request.status)
    except ValueError:
        raise bad_request("invalid_rsvp_status", ErrorCode.INVALID_REQUEST)
    
    if existing_rsvp:
        # 기존 RSVP 업데이트
        existing_rsvp.status = status
        existing_rsvp.plus_one = request.plus_one
        existing_rsvp.plus_one_name = request.plus_one_name
        existing_rsvp.dietary_restrictions = request.dietary_restrictions
        existing_rsvp.special_requests = request.special_requests
        db.commit()
        db.refresh(existing_rsvp)
        
        return {
            "message": "rsvp_updated",
            "data": {
                "id": existing_rsvp.id,
                "status": existing_rsvp.status.value,
                "plus_one": existing_rsvp.plus_one
            }
        }
    else:
        # 새 RSVP 생성
        rsvp = RSVP(
            invitation_id=invitation_id,
            guest_name=request.guest_name,
            guest_phone=request.guest_phone,
            guest_email=request.guest_email,
            status=status,
            plus_one=request.plus_one,
            plus_one_name=request.plus_one_name,
            dietary_restrictions=request.dietary_restrictions,
            special_requests=request.special_requests
        )
        
        db.add(rsvp)
        db.commit()
        db.refresh(rsvp)
        
        return {
            "message": "rsvp_created",
            "data": {
                "id": rsvp.id,
                "status": rsvp.status.value,
                "plus_one": rsvp.plus_one
            }
        }


def create_guest_message(invitation_id: int, request: GuestMessageCreateReq, db: Session) -> Dict:
    """하객 메시지 생성"""
    invitation = db.query(DigitalInvitation).filter(
        DigitalInvitation.id == invitation_id,
        DigitalInvitation.is_active == True
    ).first()
    
    if not invitation:
        raise not_found("invitation_not_found", ErrorCode.RESOURCE_NOT_FOUND)
    
    message = GuestMessage(
        invitation_id=invitation_id,
        guest_name=request.guest_name,
        guest_phone=request.guest_phone,
        message=request.message,
        image_url=request.image_url
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return {
        "message": "guest_message_created",
        "data": {
            "id": message.id,
            "guest_name": message.guest_name,
            "message": message.message,
            "image_url": message.image_url,
            "created_at": message.created_at.isoformat() if message.created_at else None
        }
    }


def get_invitation_statistics(invitation_id: int, user_id: int, db: Session) -> Dict:
    """초대장 통계 조회"""
    invitation = db.query(DigitalInvitation).filter(
        DigitalInvitation.id == invitation_id,
        DigitalInvitation.user_id == user_id
    ).first()
    
    if not invitation:
        raise not_found("invitation_not_found", ErrorCode.RESOURCE_NOT_FOUND)
    
    # 통계 계산
    total_payments = db.query(func.count(Payment.id)).filter(
        Payment.invitation_id == invitation_id
    ).scalar()
    
    completed_payments = db.query(func.count(Payment.id)).filter(
        Payment.invitation_id == invitation_id,
        Payment.payment_status == PaymentStatus.COMPLETED
    ).scalar()
    
    total_amount = db.query(func.sum(Payment.amount)).filter(
        Payment.invitation_id == invitation_id,
        Payment.payment_status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    total_rsvps = db.query(func.count(RSVP.id)).filter(
        RSVP.invitation_id == invitation_id
    ).scalar()
    
    attending_count = db.query(func.count(RSVP.id)).filter(
        RSVP.invitation_id == invitation_id,
        RSVP.status == RSVPStatus.ATTENDING
    ).scalar()
    
    plus_one_count = db.query(func.count(RSVP.id)).filter(
        RSVP.invitation_id == invitation_id,
        RSVP.plus_one == True
    ).scalar()
    
    total_guests = attending_count + plus_one_count
    
    pending_rsvps = db.query(func.count(RSVP.id)).filter(
        RSVP.invitation_id == invitation_id,
        RSVP.status == RSVPStatus.PENDING
    ).scalar()
    
    guest_messages_count = db.query(func.count(GuestMessage.id)).filter(
        GuestMessage.invitation_id == invitation_id
    ).scalar()
    
    return {
        "message": "statistics_retrieved",
        "data": {
            "view_count": invitation.view_count,
            "total_payments": total_payments,
            "completed_payments": completed_payments,
            "total_amount": float(total_amount),
            "total_rsvps": total_rsvps,
            "attending_count": attending_count,
            "not_attending_count": db.query(func.count(RSVP.id)).filter(
                RSVP.invitation_id == invitation_id,
                RSVP.status == RSVPStatus.NOT_ATTENDING
            ).scalar(),
            "maybe_count": db.query(func.count(RSVP.id)).filter(
                RSVP.invitation_id == invitation_id,
                RSVP.status == RSVPStatus.MAYBE
            ).scalar(),
            "pending_rsvps": pending_rsvps,
            "total_guests": total_guests,
            "guest_messages_count": guest_messages_count
        }
    }


def get_invitation_rsvps(invitation_id: int, user_id: int, db: Session) -> Dict:
    """RSVP 목록 조회 (초대장 소유자만)"""
    invitation = db.query(DigitalInvitation).filter(
        DigitalInvitation.id == invitation_id,
        DigitalInvitation.user_id == user_id
    ).first()
    
    if not invitation:
        raise not_found("invitation_not_found", ErrorCode.RESOURCE_NOT_FOUND)
    
    rsvps = db.query(RSVP).filter(
        RSVP.invitation_id == invitation_id
    ).order_by(RSVP.created_at.desc()).all()
    
    return {
        "message": "rsvps_retrieved",
        "data": {
            "rsvps": [
                {
                    "id": r.id,
                    "guest_name": r.guest_name,
                    "guest_phone": r.guest_phone,
                    "guest_email": r.guest_email,
                    "status": r.status.value,
                    "plus_one": r.plus_one,
                    "plus_one_name": r.plus_one_name,
                    "dietary_restrictions": r.dietary_restrictions,
                    "special_requests": r.special_requests,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                }
                for r in rsvps
            ]
        }
    }


def get_invitation_payments(invitation_id: int, user_id: int, db: Session) -> Dict:
    """결제 목록 조회 (초대장 소유자만)"""
    invitation = db.query(DigitalInvitation).filter(
        DigitalInvitation.id == invitation_id,
        DigitalInvitation.user_id == user_id
    ).first()
    
    if not invitation:
        raise not_found("invitation_not_found", ErrorCode.RESOURCE_NOT_FOUND)
    
    payments = db.query(Payment).filter(
        Payment.invitation_id == invitation_id
    ).order_by(Payment.created_at.desc()).all()
    
    return {
        "message": "payments_retrieved",
        "data": {
            "payments": [
                {
                    "id": p.id,
                    "payer_name": p.payer_name,
                    "payer_phone": p.payer_phone,
                    "payer_message": p.payer_message,
                    "amount": float(p.amount),
                    "payment_method": p.payment_method.value,
                    "payment_status": p.payment_status.value,
                    "thank_you_message_sent": p.thank_you_message_sent,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in payments
            ]
        }
    }


def get_invitation_guest_messages(invitation_id: int, db: Session) -> Dict:
    """하객 메시지 목록 조회 (공개)"""
    invitation = db.query(DigitalInvitation).filter(
        DigitalInvitation.id == invitation_id,
        DigitalInvitation.is_active == True
    ).first()
    
    if not invitation:
        raise not_found("invitation_not_found", ErrorCode.RESOURCE_NOT_FOUND)
    
    messages = db.query(GuestMessage).filter(
        GuestMessage.invitation_id == invitation_id,
        GuestMessage.is_approved == True
    ).order_by(GuestMessage.created_at.desc()).all()
    
    return {
        "message": "guest_messages_retrieved",
        "data": {
            "messages": [
                {
                    "id": m.id,
                    "guest_name": m.guest_name,
                    "message": m.message,
                    "image_url": m.image_url,
                    "created_at": m.created_at.isoformat() if m.created_at else None
                }
                for m in messages
            ]
        }
    }

