"""
디지털 초대장 및 축의금 결제 시스템 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.controllers import digital_invitation_controller
from app.schemas import (
    DigitalInvitationCreateReq, DigitalInvitationUpdateReq,
    PaymentCreateReq, RSVPCreateReq, RSVPUpdateReq, GuestMessageCreateReq
)

router = APIRouter(prefix="/digital-invitations", tags=["Digital Invitation"])


@router.post("")
async def create_digital_invitation(
    request: DigitalInvitationCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """디지털 초대장 생성"""
    return digital_invitation_controller.create_digital_invitation(user_id, request, db)


@router.get("/my")
async def get_my_digital_invitations(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """내 디지털 초대장 목록 조회"""
    return digital_invitation_controller.get_my_digital_invitations(user_id, db)


@router.get("/{invitation_url}")
async def get_digital_invitation(
    invitation_url: str,
    db: Session = Depends(get_db)
):
    """디지털 초대장 조회 (공개 접근)"""
    return digital_invitation_controller.get_digital_invitation(invitation_url, db)


@router.put("/{invitation_id}")
async def update_digital_invitation(
    invitation_id: int,
    request: DigitalInvitationUpdateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """디지털 초대장 수정"""
    return digital_invitation_controller.update_digital_invitation(invitation_id, user_id, request, db)


@router.get("/{invitation_id}/statistics")
async def get_invitation_statistics(
    invitation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """초대장 통계 조회"""
    return digital_invitation_controller.get_invitation_statistics(invitation_id, user_id, db)


@router.post("/{invitation_id}/payments")
async def create_payment(
    invitation_id: int,
    request: PaymentCreateReq,
    db: Session = Depends(get_db)
):
    """축의금 결제 생성 (공개 접근)"""
    return digital_invitation_controller.create_payment(invitation_id, request, db)


@router.get("/{invitation_id}/payments")
async def get_invitation_payments(
    invitation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """결제 목록 조회 (초대장 소유자만)"""
    return digital_invitation_controller.get_invitation_payments(invitation_id, user_id, db)


@router.post("/{invitation_id}/rsvps")
async def create_rsvp(
    invitation_id: int,
    request: RSVPCreateReq,
    db: Session = Depends(get_db)
):
    """RSVP 생성/수정 (공개 접근)"""
    return digital_invitation_controller.create_rsvp(invitation_id, request, db)


@router.get("/{invitation_id}/rsvps")
async def get_invitation_rsvps(
    invitation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """RSVP 목록 조회 (초대장 소유자만)"""
    return digital_invitation_controller.get_invitation_rsvps(invitation_id, user_id, db)


@router.post("/{invitation_id}/guest-messages")
async def create_guest_message(
    invitation_id: int,
    request: GuestMessageCreateReq,
    db: Session = Depends(get_db)
):
    """하객 메시지 생성 (공개 접근)"""
    return digital_invitation_controller.create_guest_message(invitation_id, request, db)


@router.get("/{invitation_id}/guest-messages")
async def get_invitation_guest_messages(
    invitation_id: int,
    db: Session = Depends(get_db)
):
    """하객 메시지 목록 조회 (공개)"""
    return digital_invitation_controller.get_invitation_guest_messages(invitation_id, db)

