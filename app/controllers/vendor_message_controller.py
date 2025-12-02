from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, date, timedelta
from typing import Dict, List
from decimal import Decimal

from app.models.db.vendor_message import (
    VendorThread, VendorMessage, VendorContract, VendorDocument, VendorPaymentSchedule,
    MessageSenderType, DocumentType, DocumentStatus, PaymentType, PaymentStatus
)
from app.models.db.vendor import Vendor
from app.models.db.calendar import CalendarEvent
from app.schemas import (
    VendorThreadCreateReq, VendorThreadUpdateReq,
    VendorMessageCreateReq,
    VendorContractCreateReq, VendorContractUpdateReq,
    VendorDocumentCreateReq, VendorDocumentUpdateReq,
    VendorPaymentScheduleCreateReq, VendorPaymentScheduleUpdateReq,
    VendorCompareReq
)
from app.core.couple_helpers import get_user_couple_id, get_couple_user_ids


def create_thread(user_id: int, request: VendorThreadCreateReq, db: Session) -> Dict:
    """제휴 업체 메시지 쓰레드 생성"""
    # 제휴 업체 존재 확인
    vendor = db.query(Vendor).filter(Vendor.id == request.vendor_id).first()
    if not vendor:
        return {"message": "error", "data": {"error": "제휴 업체를 찾을 수 없습니다."}}
    
    # 이미 쓰레드가 있는지 확인
    existing_thread = db.query(VendorThread).filter(
        and_(
            VendorThread.user_id == user_id,
            VendorThread.vendor_id == request.vendor_id,
            VendorThread.is_active == True
        )
    ).first()
    
    if existing_thread:
        return {
            "message": "thread_already_exists",
            "data": {
                "id": existing_thread.id,
                "title": existing_thread.title,
                "vendor_id": existing_thread.vendor_id
            }
        }
    
    # 제목이 없으면 제휴 업체 이름으로 자동 생성
    title = request.title or f"{vendor.name}와의 대화"
    
    # 커플 ID 가져오기
    couple_id = get_user_couple_id(user_id, db)
    
    thread = VendorThread(
        user_id=user_id,
        couple_id=couple_id,  # 커플 공유
        is_shared_with_partner=getattr(request, 'is_shared_with_partner', False),  # 선택적 공유
        vendor_id=request.vendor_id,
        title=title,
        is_active=True
    )
    
    try:
        db.add(thread)
        db.commit()
        db.refresh(thread)
        
        return {
            "message": "thread_created",
            "data": {
                "id": thread.id,
                "title": thread.title,
                "vendor_id": thread.vendor_id,
                "vendor_name": vendor.name,
                "created_at": thread.created_at.isoformat() if thread.created_at else None
            }
        }
    except Exception as e:
        db.rollback()
        print(f"쓰레드 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return {"message": "error", "data": {"error": "쓰레드 생성에 실패했습니다."}}


def get_threads(user_id: int, db: Session, is_vendor: bool = False) -> Dict:
    """사용자 또는 제휴 업체의 쓰레드 목록 조회"""
    from app.models.db.user import User
    
    if is_vendor:
        # 제휴 업체 계정인 경우: 자신의 vendor_id와 연결된 쓰레드 조회
        vendor = db.query(Vendor).filter(Vendor.user_id == user_id).first()
        if not vendor:
            return {"message": "threads_retrieved", "data": {"threads": []}}
        
        threads = db.query(VendorThread).filter(
            VendorThread.vendor_id == vendor.id
        ).order_by(desc(VendorThread.last_message_at), desc(VendorThread.created_at)).all()
    else:
        # 일반 사용자 계정인 경우: 자신의 user_id와 연결된 쓰레드 조회 (커플 공유 포함)
        # 커플이 연결되어 있고 is_shared_with_partner가 True인 쓰레드도 포함
        couple_id = get_user_couple_id(user_id, db)
        
        if couple_id:
            # 커플이 연결되어 있으면 couple_id로 필터링 (공유된 쓰레드 포함)
            threads = db.query(VendorThread).filter(
                or_(
                    VendorThread.user_id == user_id,  # 자신의 쓰레드
                    and_(
                        VendorThread.couple_id == couple_id,
                        VendorThread.is_shared_with_partner == True  # 공유된 쓰레드
                    )
                )
            ).order_by(desc(VendorThread.last_message_at), desc(VendorThread.created_at)).all()
        else:
            # 커플이 연결되어 있지 않으면 자신의 쓰레드만
            threads = db.query(VendorThread).filter(
                VendorThread.user_id == user_id
            ).order_by(desc(VendorThread.last_message_at), desc(VendorThread.created_at)).all()
    
    result = []
    for thread in threads:
        vendor = db.query(Vendor).filter(Vendor.id == thread.vendor_id).first()
        # 읽지 않은 메시지 수 계산
        if is_vendor:
            # 제휴 업체 계정: 사용자가 보낸 메시지 중 읽지 않은 것
            unread_count = db.query(VendorMessage).filter(
                and_(
                    VendorMessage.thread_id == thread.id,
                    VendorMessage.sender_type == MessageSenderType.USER,
                    VendorMessage.is_read == False
                )
            ).count()
        else:
            # 일반 사용자 계정: 제휴 업체가 보낸 메시지 중 읽지 않은 것
            unread_count = db.query(VendorMessage).filter(
                and_(
                    VendorMessage.thread_id == thread.id,
                    VendorMessage.sender_type == MessageSenderType.VENDOR,
                    VendorMessage.is_read == False
                )
            ).count()
        
        last_message = db.query(VendorMessage).filter(
            VendorMessage.thread_id == thread.id
        ).order_by(desc(VendorMessage.created_at)).first()
        
        result.append({
            "id": thread.id,
            "title": thread.title,
            "vendor_id": thread.vendor_id,
            "vendor_name": vendor.name if vendor else None,
            "vendor_type": vendor.vendor_type.value if vendor else None,
            "is_active": thread.is_active,
            "unread_count": unread_count,
            "last_message": {
                "content": last_message.content[:50] + "..." if last_message and len(last_message.content) > 50 else (last_message.content if last_message else None),
                "created_at": last_message.created_at.isoformat() if last_message else None
            } if last_message else None,
            "last_message_at": thread.last_message_at.isoformat() if thread.last_message_at else None,
            "created_at": thread.created_at.isoformat() if thread.created_at else None
        })
    
    return {
        "message": "threads_retrieved",
        "data": {"threads": result}
    }


def get_thread(thread_id: int, user_id: int, db: Session, is_vendor: bool = False) -> Dict:
    """제휴 업체 쓰레드 상세 조회 (메시지 포함) - 사용자 또는 제휴 업체"""
    from app.models.db.user import User
    
    # 쓰레드 조회
    thread = db.query(VendorThread).filter(
        VendorThread.id == thread_id
    ).first()
    
    if not thread:
        return {"message": "error", "data": {"error": "쓰레드를 찾을 수 없습니다."}}
    
    # 권한 확인
    if is_vendor:
        # 제휴 업체 계정인 경우: 자신의 vendor_id와 쓰레드의 vendor_id가 일치해야 함
        vendor = db.query(Vendor).filter(Vendor.user_id == user_id).first()
        if not vendor or vendor.id != thread.vendor_id:
            return {"message": "error", "data": {"error": "이 쓰레드에 접근할 권한이 없습니다."}}
    else:
        # 일반 사용자 계정인 경우: 쓰레드의 user_id와 일치해야 함
        if thread.user_id != user_id:
            return {"message": "error", "data": {"error": "이 쓰레드에 접근할 권한이 없습니다."}}
    
    vendor = db.query(Vendor).filter(Vendor.id == thread.vendor_id).first()
    
    # 메시지 목록 조회
    messages = db.query(VendorMessage).filter(
        VendorMessage.thread_id == thread_id
    ).order_by(VendorMessage.created_at).all()
    
    # 읽지 않은 메시지를 읽음으로 표시
    if is_vendor:
        # 제휴 업체 계정: 사용자가 보낸 메시지를 읽음으로 표시
        db.query(VendorMessage).filter(
            and_(
                VendorMessage.thread_id == thread_id,
                VendorMessage.sender_type == MessageSenderType.USER,
                VendorMessage.is_read == False
            )
        ).update({"is_read": True})
    else:
        # 일반 사용자 계정: 제휴 업체가 보낸 메시지를 읽음으로 표시
        db.query(VendorMessage).filter(
            and_(
                VendorMessage.thread_id == thread_id,
                VendorMessage.sender_type == MessageSenderType.VENDOR,
                VendorMessage.is_read == False
            )
        ).update({"is_read": True})
    db.commit()
    
    # 계약 정보 조회
    contract = db.query(VendorContract).filter(
        VendorContract.thread_id == thread_id
    ).first()
    
    contract_data = None
    if contract:
        # 결제 일정 조회
        payment_schedules = db.query(VendorPaymentSchedule).filter(
            VendorPaymentSchedule.contract_id == contract.id
        ).order_by(VendorPaymentSchedule.due_date).all()
        
        # 문서 조회
        documents = db.query(VendorDocument).filter(
            VendorDocument.contract_id == contract.id
        ).order_by(desc(VendorDocument.version)).all()
        
        contract_data = {
            "id": contract.id,
            "contract_date": contract.contract_date.isoformat() if contract.contract_date else None,
            "total_amount": float(contract.total_amount) if contract.total_amount else None,
            "deposit_amount": float(contract.deposit_amount) if contract.deposit_amount else None,
            "interim_amount": float(contract.interim_amount) if contract.interim_amount else None,
            "balance_amount": float(contract.balance_amount) if contract.balance_amount else None,
            "service_date": contract.service_date.isoformat() if contract.service_date else None,
            "notes": contract.notes,
            "is_active": contract.is_active,
            "payment_schedules": [
                {
                    "id": ps.id,
                    "payment_type": ps.payment_type.value,
                    "amount": float(ps.amount),
                    "due_date": ps.due_date.isoformat() if ps.due_date else None,
                    "paid_date": ps.paid_date.isoformat() if ps.paid_date else None,
                    "payment_method": ps.payment_method,
                    "status": ps.status.value,
                    "reminder_sent": ps.reminder_sent,
                    "notes": ps.notes
                }
                for ps in payment_schedules
            ],
            "documents": [
                {
                    "id": doc.id,
                    "document_type": doc.document_type.value,
                    "version": doc.version,
                    "file_url": doc.file_url,
                    "file_name": doc.file_name,
                    "file_size": doc.file_size,
                    "status": doc.status.value,
                    "signed_at": doc.signed_at.isoformat() if doc.signed_at else None,
                    "signed_by": doc.signed_by,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None
                }
                for doc in documents
            ]
        }
    
    return {
        "message": "thread_retrieved",
        "data": {
            "id": thread.id,
            "title": thread.title,
            "vendor_id": thread.vendor_id,
            "vendor": {
                "id": vendor.id if vendor else None,
                "name": vendor.name if vendor else None,
                "vendor_type": vendor.vendor_type.value if vendor else None,
                "contact_phone": vendor.contact_phone if vendor else None,
                "contact_link": vendor.contact_link if vendor else None
            },
            "is_active": thread.is_active,
            "messages": [
                {
                    "id": msg.id,
                    "sender_type": msg.sender_type.value,
                    "sender_id": msg.sender_id,
                    "content": msg.content,
                    "attachments": msg.attachments or [],
                    "is_read": msg.is_read,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ],
            "contract": contract_data,
            "created_at": thread.created_at.isoformat() if thread.created_at else None
        }
    }


def update_thread(thread_id: int, user_id: int, request: VendorThreadUpdateReq, db: Session) -> Dict:
    """제휴 업체 쓰레드 수정"""
    thread = db.query(VendorThread).filter(
        and_(
            VendorThread.id == thread_id,
            VendorThread.user_id == user_id
        )
    ).first()
    
    if not thread:
        return {"message": "error", "data": {"error": "쓰레드를 찾을 수 없습니다."}}
    
    if request.title is not None:
        thread.title = request.title
    if request.is_active is not None:
        thread.is_active = request.is_active
    
    try:
        db.commit()
        db.refresh(thread)
        
        return {
            "message": "thread_updated",
            "data": {
                "id": thread.id,
                "title": thread.title,
                "is_active": thread.is_active
            }
        }
    except Exception as e:
        db.rollback()
        print(f"쓰레드 수정 실패: {e}")
        return {"message": "error", "data": {"error": "쓰레드 수정에 실패했습니다."}}


def send_message(user_id: int, request: VendorMessageCreateReq, db: Session, is_vendor: bool = False) -> Dict:
    """메시지 전송 (사용자 또는 제휴 업체)"""
    from app.models.db.user import User
    
    # 쓰레드 조회
    thread = db.query(VendorThread).filter(
        VendorThread.id == request.thread_id
    ).first()
    
    if not thread:
        return {"message": "error", "data": {"error": "쓰레드를 찾을 수 없습니다."}}
    
    # 권한 확인
    if is_vendor:
        # 제휴 업체 계정인 경우: 자신의 vendor_id와 쓰레드의 vendor_id가 일치해야 함
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"message": "error", "data": {"error": "사용자를 찾을 수 없습니다."}}
        
        vendor = db.query(Vendor).filter(Vendor.user_id == user_id).first()
        if not vendor or vendor.id != thread.vendor_id:
            return {"message": "error", "data": {"error": "이 쓰레드에 메시지를 보낼 권한이 없습니다."}}
        
        sender_type = MessageSenderType.VENDOR
        sender_id = vendor.id
    else:
        # 일반 사용자 계정인 경우: 쓰레드의 user_id와 일치해야 함
        if thread.user_id != user_id:
            return {"message": "error", "data": {"error": "이 쓰레드에 메시지를 보낼 권한이 없습니다."}}
        
        sender_type = MessageSenderType.USER
        sender_id = user_id
    
    message = VendorMessage(
        thread_id=request.thread_id,
        sender_type=sender_type,
        sender_id=sender_id,
        content=request.content,
        attachments=request.attachments or [],
        is_read=True  # 본인이 보낸 메시지는 자동으로 읽음
    )
    
    try:
        db.add(message)
        # 쓰레드의 last_message_at 업데이트
        thread.last_message_at = datetime.now()
        db.commit()
        db.refresh(message)
        
        return {
            "message": "message_sent",
            "data": {
                "id": message.id,
                "thread_id": message.thread_id,
                "sender_type": sender_type.value,
                "content": message.content,
                "created_at": message.created_at.isoformat() if message.created_at else None
            }
        }
    except Exception as e:
        db.rollback()
        print(f"메시지 전송 실패: {e}")
        import traceback
        traceback.print_exc()
        return {"message": "error", "data": {"error": "메시지 전송에 실패했습니다."}}


def create_contract(user_id: int, request: VendorContractCreateReq, db: Session) -> Dict:
    """계약 정보 생성"""
    thread = db.query(VendorThread).filter(
        and_(
            VendorThread.id == request.thread_id,
            VendorThread.user_id == user_id
        )
    ).first()
    
    if not thread:
        return {"message": "error", "data": {"error": "쓰레드를 찾을 수 없습니다."}}
    
    # 이미 계약이 있는지 확인
    existing_contract = db.query(VendorContract).filter(
        VendorContract.thread_id == request.thread_id
    ).first()
    
    if existing_contract:
        return {"message": "error", "data": {"error": "이미 계약 정보가 존재합니다."}}
    
    contract_date = None
    if request.contract_date:
        contract_date = datetime.strptime(request.contract_date, "%Y-%m-%d").date()
    
    service_date = None
    if request.service_date:
        service_date = datetime.strptime(request.service_date, "%Y-%m-%d").date()
    
    contract = VendorContract(
        thread_id=request.thread_id,
        user_id=user_id,
        vendor_id=thread.vendor_id,
        contract_date=contract_date,
        total_amount=Decimal(str(request.total_amount)) if request.total_amount else None,
        deposit_amount=Decimal(str(request.deposit_amount)) if request.deposit_amount else None,
        interim_amount=Decimal(str(request.interim_amount)) if request.interim_amount else None,
        balance_amount=Decimal(str(request.balance_amount)) if request.balance_amount else None,
        service_date=service_date,
        notes=request.notes,
        is_active=True
    )
    
    try:
        db.add(contract)
        db.commit()
        db.refresh(contract)
        
        return {
            "message": "contract_created",
            "data": {
                "id": contract.id,
                "thread_id": contract.thread_id,
                "contract_date": contract.contract_date.isoformat() if contract.contract_date else None,
                "total_amount": float(contract.total_amount) if contract.total_amount else None
            }
        }
    except Exception as e:
        db.rollback()
        print(f"계약 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return {"message": "error", "data": {"error": "계약 생성에 실패했습니다."}}


def update_contract(contract_id: int, user_id: int, request: VendorContractUpdateReq, db: Session) -> Dict:
    """계약 정보 수정"""
    contract = db.query(VendorContract).filter(
        and_(
            VendorContract.id == contract_id,
            VendorContract.user_id == user_id
        )
    ).first()
    
    if not contract:
        return {"message": "error", "data": {"error": "계약을 찾을 수 없습니다."}}
    
    if request.contract_date is not None:
        contract.contract_date = datetime.strptime(request.contract_date, "%Y-%m-%d").date()
    if request.total_amount is not None:
        contract.total_amount = Decimal(str(request.total_amount))
    if request.deposit_amount is not None:
        contract.deposit_amount = Decimal(str(request.deposit_amount))
    if request.interim_amount is not None:
        contract.interim_amount = Decimal(str(request.interim_amount))
    if request.balance_amount is not None:
        contract.balance_amount = Decimal(str(request.balance_amount))
    if request.service_date is not None:
        contract.service_date = datetime.strptime(request.service_date, "%Y-%m-%d").date()
    if request.notes is not None:
        contract.notes = request.notes
    if request.is_active is not None:
        contract.is_active = request.is_active
    
    try:
        db.commit()
        db.refresh(contract)
        
        return {
            "message": "contract_updated",
            "data": {
                "id": contract.id,
                "total_amount": float(contract.total_amount) if contract.total_amount else None
            }
        }
    except Exception as e:
        db.rollback()
        print(f"계약 수정 실패: {e}")
        return {"message": "error", "data": {"error": "계약 수정에 실패했습니다."}}


def create_document(user_id: int, request: VendorDocumentCreateReq, db: Session) -> Dict:
    """문서 업로드"""
    contract = db.query(VendorContract).filter(
        and_(
            VendorContract.id == request.contract_id,
            VendorContract.user_id == user_id
        )
    ).first()
    
    if not contract:
        return {"message": "error", "data": {"error": "계약을 찾을 수 없습니다."}}
    
    # 같은 타입의 최신 버전 찾기
    latest_doc = db.query(VendorDocument).filter(
        and_(
            VendorDocument.contract_id == request.contract_id,
            VendorDocument.document_type == DocumentType(request.document_type)
        )
    ).order_by(desc(VendorDocument.version)).first()
    
    new_version = (latest_doc.version + 1) if latest_doc else 1
    
    document = VendorDocument(
        contract_id=request.contract_id,
        document_type=DocumentType(request.document_type),
        version=new_version,
        file_url=request.file_url,
        file_name=request.file_name,
        file_size=request.file_size if request.file_size else None,
        status=DocumentStatus.DRAFT,
        document_metadata=request.metadata if request.metadata else {}
    )
    
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return {
            "message": "document_created",
            "data": {
                "id": document.id,
                "document_type": document.document_type.value,
                "version": document.version,
                "file_url": document.file_url,
                "status": document.status.value
            }
        }
    except Exception as e:
        db.rollback()
        print(f"문서 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return {"message": "error", "data": {"error": "문서 생성에 실패했습니다."}}


def update_document(document_id: int, user_id: int, request: VendorDocumentUpdateReq, db: Session) -> Dict:
    """문서 상태 수정 (서명 등)"""
    document = db.query(VendorDocument).join(VendorContract).filter(
        and_(
            VendorDocument.id == document_id,
            VendorContract.user_id == user_id
        )
    ).first()
    
    if not document:
        return {"message": "error", "data": {"error": "문서를 찾을 수 없습니다."}}
    
    if request.status is not None:
        document.status = DocumentStatus(request.status)
    if request.signed_at is not None:
        document.signed_at = datetime.strptime(request.signed_at, "%Y-%m-%d %H:%M:%S")
    if request.signed_by is not None:
        document.signed_by = request.signed_by
    if request.metadata is not None:
        document.document_metadata = request.metadata
    
    try:
        db.commit()
        db.refresh(document)
        
        return {
            "message": "document_updated",
            "data": {
                "id": document.id,
                "status": document.status.value,
                "signed_at": document.signed_at.isoformat() if document.signed_at else None
            }
        }
    except Exception as e:
        db.rollback()
        print(f"문서 수정 실패: {e}")
        return {"message": "error", "data": {"error": "문서 수정에 실패했습니다."}}


def create_payment_schedule(user_id: int, request: VendorPaymentScheduleCreateReq, db: Session) -> Dict:
    """결제 일정 생성"""
    contract = db.query(VendorContract).filter(
        and_(
            VendorContract.id == request.contract_id,
            VendorContract.user_id == user_id
        )
    ).first()
    
    if not contract:
        return {"message": "error", "data": {"error": "계약을 찾을 수 없습니다."}}
    
    due_date = datetime.strptime(request.due_date, "%Y-%m-%d").date()
    
    payment_schedule = VendorPaymentSchedule(
        contract_id=request.contract_id,
        payment_type=PaymentType(request.payment_type),
        amount=Decimal(str(request.amount)),
        due_date=due_date,
        status=PaymentStatus.PENDING,
        reminder_sent=False,
        notes=request.notes
    )
    
    try:
        db.add(payment_schedule)
        db.commit()
        db.refresh(payment_schedule)
        
        # 결제 일정을 캘린더에 자동 등록
        _create_calendar_event_for_payment(user_id, contract, payment_schedule, db)
        
        return {
            "message": "payment_schedule_created",
            "data": {
                "id": payment_schedule.id,
                "payment_type": payment_schedule.payment_type.value,
                "amount": float(payment_schedule.amount),
                "due_date": payment_schedule.due_date.isoformat()
            }
        }
    except Exception as e:
        db.rollback()
        print(f"결제 일정 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return {"message": "error", "data": {"error": "결제 일정 생성에 실패했습니다."}}


def _create_calendar_event_for_payment(user_id: int, contract: VendorContract, payment_schedule: VendorPaymentSchedule, db: Session):
    """결제 일정을 캘린더에 자동 등록"""
    try:
        vendor = db.query(Vendor).filter(Vendor.id == contract.vendor_id).first()
        vendor_name = vendor.name if vendor else "제휴 업체"
        
        payment_type_names = {
            PaymentType.DEPOSIT: "계약금",
            PaymentType.INTERIM: "중도금",
            PaymentType.BALANCE: "잔금",
            PaymentType.ADDITIONAL: "추가 결제"
        }
        
        title = f"{vendor_name} {payment_type_names.get(payment_schedule.payment_type, '결제')} 납부"
        amount_str = f"{int(payment_schedule.amount):,}원"
        
        event = CalendarEvent(
            user_id=user_id,
            title=title,
            description=f"{payment_type_names.get(payment_schedule.payment_type, '결제')} 납부일\n금액: {amount_str}",
            start_date=payment_schedule.due_date,
            category="payment",
            priority="high",
            assignee="both"
        )
        
        db.add(event)
        db.commit()
    except Exception as e:
        print(f"캘린더 이벤트 생성 실패: {e}")
        # 캘린더 이벤트 생성 실패해도 결제 일정은 저장되도록 함


def update_payment_schedule(schedule_id: int, user_id: int, request: VendorPaymentScheduleUpdateReq, db: Session) -> Dict:
    """결제 일정 수정"""
    payment_schedule = db.query(VendorPaymentSchedule).join(VendorContract).filter(
        and_(
            VendorPaymentSchedule.id == schedule_id,
            VendorContract.user_id == user_id
        )
    ).first()
    
    if not payment_schedule:
        return {"message": "error", "data": {"error": "결제 일정을 찾을 수 없습니다."}}
    
    if request.amount is not None:
        payment_schedule.amount = Decimal(str(request.amount))
    if request.due_date is not None:
        payment_schedule.due_date = datetime.strptime(request.due_date, "%Y-%m-%d").date()
    if request.paid_date is not None:
        payment_schedule.paid_date = datetime.strptime(request.paid_date, "%Y-%m-%d").date()
        # 결제 완료 시 상태 자동 변경
        if payment_schedule.status == PaymentStatus.PENDING:
            payment_schedule.status = PaymentStatus.PAID
    if request.payment_method is not None:
        payment_schedule.payment_method = request.payment_method
    if request.status is not None:
        payment_schedule.status = PaymentStatus(request.status)
    if request.notes is not None:
        payment_schedule.notes = request.notes
    
    try:
        db.commit()
        db.refresh(payment_schedule)
        
        return {
            "message": "payment_schedule_updated",
            "data": {
                "id": payment_schedule.id,
                "status": payment_schedule.status.value,
                "paid_date": payment_schedule.paid_date.isoformat() if payment_schedule.paid_date else None
            }
        }
    except Exception as e:
        db.rollback()
        print(f"결제 일정 수정 실패: {e}")
        return {"message": "error", "data": {"error": "결제 일정 수정에 실패했습니다."}}


def get_payment_reminders(user_id: int, days: int = 7, db: Session = None) -> Dict:
    """결제 리마인더 조회 (N일 이내 결제 예정)"""
    today = date.today()
    reminder_date = today + timedelta(days=days)
    
    payment_schedules = db.query(VendorPaymentSchedule).join(VendorContract).filter(
        and_(
            VendorContract.user_id == user_id,
            VendorPaymentSchedule.status == PaymentStatus.PENDING,
            VendorPaymentSchedule.due_date >= today,
            VendorPaymentSchedule.due_date <= reminder_date
        )
    ).order_by(VendorPaymentSchedule.due_date).all()
    
    result = []
    for ps in payment_schedules:
        contract = ps.contract
        vendor = db.query(Vendor).filter(Vendor.id == contract.vendor_id).first()
        
        result.append({
            "id": ps.id,
            "contract_id": ps.contract_id,
            "vendor_name": vendor.name if vendor else None,
            "payment_type": ps.payment_type.value,
            "amount": float(ps.amount),
            "due_date": ps.due_date.isoformat() if ps.due_date else None,
            "days_until_due": (ps.due_date - today).days if ps.due_date else None,
            "reminder_sent": ps.reminder_sent,
            "notes": ps.notes
        })
    
    return {
        "message": "payment_reminders_retrieved",
        "data": {
            "reminders": result,
            "count": len(result)
        }
    }


def compare_vendors(user_id: int, request: VendorCompareReq, db: Session) -> Dict:
    """제휴 업체 비교"""
    if len(request.vendor_ids) > 5:
        return {"message": "error", "data": {"error": "최대 5개까지 비교할 수 있습니다."}}
    
    vendors = db.query(Vendor).filter(Vendor.id.in_(request.vendor_ids)).all()
    
    if len(vendors) != len(request.vendor_ids):
        return {"message": "error", "data": {"error": "일부 제휴 업체를 찾을 수 없습니다."}}
    
    result = []
    for vendor in vendors:
        # 각 제휴 업체의 계약 정보 조회
        contracts = db.query(VendorContract).filter(
            and_(
                VendorContract.vendor_id == vendor.id,
                VendorContract.user_id == user_id,
                VendorContract.is_active == True
            )
        ).all()
        
        # 결제 일정 조회
        payment_schedules = []
        for contract in contracts:
            schedules = db.query(VendorPaymentSchedule).filter(
                VendorPaymentSchedule.contract_id == contract.id
            ).all()
            payment_schedules.extend(schedules)
        
        result.append({
            "id": vendor.id,
            "name": vendor.name,
            "vendor_type": vendor.vendor_type.value,
            "description": vendor.description,
            "min_price": float(vendor.min_price) if vendor.min_price else None,
            "max_price": float(vendor.max_price) if vendor.max_price else None,
            "rating_avg": float(vendor.rating_avg) if vendor.rating_avg else None,
            "review_count": vendor.review_count,
            "tags": vendor.tags or [],
            "contact_phone": vendor.contact_phone,
            "contact_link": vendor.contact_link,
            "contracts": [
                {
                    "id": c.id,
                    "total_amount": float(c.total_amount) if c.total_amount else None,
                    "contract_date": c.contract_date.isoformat() if c.contract_date else None
                }
                for c in contracts
            ],
            "total_contract_amount": sum([float(c.total_amount) for c in contracts if c.total_amount]),
            "payment_schedules_count": len(payment_schedules),
            "pending_payments": sum([float(ps.amount) for ps in payment_schedules if ps.status == PaymentStatus.PENDING])
        })
    
    return {
        "message": "vendors_compared",
        "data": {
            "vendors": result,
            "count": len(result)
        }
    }

