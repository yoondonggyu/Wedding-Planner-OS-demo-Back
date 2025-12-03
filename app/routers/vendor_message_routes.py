from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.schemas import (
    VendorThreadCreateReq, VendorThreadUpdateReq, VendorThreadInviteReq,
    VendorMessageCreateReq,
    VendorContractCreateReq, VendorContractUpdateReq,
    VendorDocumentCreateReq, VendorDocumentUpdateReq,
    VendorPaymentScheduleCreateReq, VendorPaymentScheduleUpdateReq,
    VendorCompareReq
)
from app.controllers import vendor_message_controller
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.db.user import User
from app.core.user_roles import UserRole

router = APIRouter(tags=["vendor_message"])

def get_user_role(user_id: int, db: Session) -> UserRole:
    """사용자 역할 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return UserRole.USER
    return UserRole(user.role) if user.role else UserRole.USER

# 제휴 업체 메시지 쓰레드
@router.post("/vendor-threads")
async def create_thread(
    request: VendorThreadCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """제휴 업체 메시지 쓰레드 생성"""
    return vendor_message_controller.create_thread(user_id, request, db)

@router.get("/vendor-threads")
async def get_threads(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """제휴 업체 메시지 쓰레드 목록 조회 (사용자 또는 제휴 업체)"""
    user_role = get_user_role(user_id, db)
    is_vendor = user_role == UserRole.PARTNER_VENDOR
    return vendor_message_controller.get_threads(user_id, db, is_vendor=is_vendor)

@router.get("/vendor-threads/{thread_id}")
async def get_thread(
    thread_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """제휴 업체 메시지 쓰레드 상세 조회 (사용자 또는 제휴 업체)"""
    user_role = get_user_role(user_id, db)
    is_vendor = user_role == UserRole.PARTNER_VENDOR
    return vendor_message_controller.get_thread(thread_id, user_id, db, is_vendor=is_vendor)

@router.put("/vendor-threads/{thread_id}")
async def update_thread(
    thread_id: int,
    request: VendorThreadUpdateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """제휴 업체 메시지 쓰레드 수정"""
    return vendor_message_controller.update_thread(thread_id, user_id, request, db)

@router.delete("/vendor-threads/{thread_id}")
async def delete_thread(
    thread_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """제휴 업체 메시지 쓰레드 삭제"""
    return vendor_message_controller.delete_thread(thread_id, user_id, db)

@router.post("/vendor-threads/{thread_id}/invite")
async def invite_participant(
    thread_id: int,
    request: VendorThreadInviteReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """쓰레드에 참여자 초대 (1대1 → 단체톡방 전환 또는 단체톡방에 참여자 추가)"""
    return vendor_message_controller.invite_participant(thread_id, user_id, request, db)

# 메시지
@router.post("/vendor-messages")
async def send_message(
    request: VendorMessageCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """메시지 전송 (사용자 또는 제휴 업체)"""
    user_role = get_user_role(user_id, db)
    is_vendor = user_role == UserRole.PARTNER_VENDOR
    return vendor_message_controller.send_message(user_id, request, db, is_vendor=is_vendor)

# 계약
@router.post("/vendor-contracts")
async def create_contract(
    request: VendorContractCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """계약 정보 생성"""
    return vendor_message_controller.create_contract(user_id, request, db)

@router.put("/vendor-contracts/{contract_id}")
async def update_contract(
    contract_id: int,
    request: VendorContractUpdateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """계약 정보 수정"""
    return vendor_message_controller.update_contract(contract_id, user_id, request, db)

# 문서
@router.post("/vendor-documents")
async def create_document(
    request: VendorDocumentCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """문서 업로드 (견적서/계약서)"""
    return vendor_message_controller.create_document(user_id, request, db)

@router.put("/vendor-documents/{document_id}")
async def update_document(
    document_id: int,
    request: VendorDocumentUpdateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """문서 상태 수정 (서명 등)"""
    return vendor_message_controller.update_document(document_id, user_id, request, db)

# 결제 일정
@router.post("/vendor-payment-schedules")
async def create_payment_schedule(
    request: VendorPaymentScheduleCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """결제 일정 생성"""
    return vendor_message_controller.create_payment_schedule(user_id, request, db)

@router.put("/vendor-payment-schedules/{schedule_id}")
async def update_payment_schedule(
    schedule_id: int,
    request: VendorPaymentScheduleUpdateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """결제 일정 수정"""
    return vendor_message_controller.update_payment_schedule(schedule_id, user_id, request, db)

@router.get("/vendor-payment-reminders")
async def get_payment_reminders(
    days: int = Query(7, description="N일 이내 결제 예정 조회"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """결제 리마인더 조회"""
    return vendor_message_controller.get_payment_reminders(user_id, days, db)

# 제휴 업체 비교
@router.post("/vendors/compare")
async def compare_vendors(
    request: VendorCompareReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """제휴 업체 비교"""
    return vendor_message_controller.compare_vendors(user_id, request, db)

