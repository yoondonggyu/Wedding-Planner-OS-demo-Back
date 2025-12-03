from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger, Boolean, JSON, Enum, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class MessageSenderType(str, enum.Enum):
    USER = "user"  # 사용자 (커플/플래너)
    VENDOR = "vendor"  # 벤더


class DocumentType(str, enum.Enum):
    QUOTE = "quote"  # 견적서
    CONTRACT = "contract"  # 계약서
    INVOICE = "invoice"  # 청구서
    RECEIPT = "receipt"  # 영수증


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"  # 초안
    PENDING = "pending"  # 검토 중
    SIGNED = "signed"  # 서명 완료
    REJECTED = "rejected"  # 거부됨


class PaymentType(str, enum.Enum):
    DEPOSIT = "deposit"  # 계약금
    INTERIM = "interim"  # 중도금
    BALANCE = "balance"  # 잔금
    ADDITIONAL = "additional"  # 추가 결제


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"  # 대기 중
    PAID = "paid"  # 결제 완료
    OVERDUE = "overdue"  # 연체
    CANCELLED = "cancelled"  # 취소됨


class ThreadType(str, enum.Enum):
    ONE_ON_ONE = "one_on_one"  # 1대1 채팅
    GROUP = "group"  # 단체톡방 (업체 + 신랑 + 신부)


class VendorThread(Base):
    """벤더별 메시지 쓰레드"""
    __tablename__ = "vendor_threads"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # 쓰레드 생성자
    couple_id = Column(BigInteger, ForeignKey("couples.id", ondelete="SET NULL"), nullable=True)  # 커플 공유
    is_shared_with_partner = Column(Boolean, default=False, nullable=False)  # 파트너와 공유 여부 (1대1 채팅용)
    vendor_id = Column(BigInteger, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    thread_type = Column(String(20), default='one_on_one', nullable=False)  # 1대1 또는 단체톡 (one_on_one, group)
    participant_user_ids = Column(JSON, nullable=True)  # 단체톡 참여자 user_id 리스트 [user1_id, user2_id]
    title = Column(String(255), nullable=False)  # "카메라맨 A와의 대화" 등
    is_active = Column(Boolean, default=True, nullable=False)  # 활성 상태
    last_message_at = Column(DateTime, nullable=True)  # 마지막 메시지 시간
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="vendor_threads")
    vendor = relationship("Vendor", backref="threads")
    messages = relationship("VendorMessage", backref="thread", cascade="all, delete-orphan", order_by="VendorMessage.created_at")
    contract = relationship("VendorContract", backref="thread", uselist=False, cascade="all, delete-orphan")


class VendorMessage(Base):
    """벤더 메시지"""
    __tablename__ = "vendor_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    thread_id = Column(BigInteger, ForeignKey("vendor_threads.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(Enum(MessageSenderType), nullable=False)  # user or vendor
    sender_id = Column(BigInteger, nullable=False)  # user_id 또는 vendor_id
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    is_visible_to_partner = Column(Boolean, default=True, nullable=False)  # 1대1 채팅에서 파트너에게 공개 여부
    attachments = Column(JSON, nullable=True)  # 파일 첨부 URL 리스트
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    # thread relationship은 VendorThread에서 정의됨


class VendorContract(Base):
    """벤더 계약 정보"""
    __tablename__ = "vendor_contracts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    thread_id = Column(BigInteger, ForeignKey("vendor_threads.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vendor_id = Column(BigInteger, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    contract_date = Column(Date, nullable=True)  # 계약일
    total_amount = Column(Numeric(15, 2), nullable=True)  # 총 계약 금액
    deposit_amount = Column(Numeric(15, 2), nullable=True)  # 계약금
    interim_amount = Column(Numeric(15, 2), nullable=True)  # 중도금
    balance_amount = Column(Numeric(15, 2), nullable=True)  # 잔금
    service_date = Column(Date, nullable=True)  # 서비스 제공일 (예식일 등)
    notes = Column(Text, nullable=True)  # 계약 메모
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="vendor_contracts")
    vendor = relationship("Vendor", backref="contracts")
    documents = relationship("VendorDocument", backref="contract", cascade="all, delete-orphan", order_by="VendorDocument.version")
    payment_schedules = relationship("VendorPaymentSchedule", backref="contract", cascade="all, delete-orphan", order_by="VendorPaymentSchedule.due_date")


class VendorDocument(Base):
    """견적서/계약서 문서"""
    __tablename__ = "vendor_documents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contract_id = Column(BigInteger, ForeignKey("vendor_contracts.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)  # quote, contract, invoice, receipt
    version = Column(Integer, default=1, nullable=False)  # 버전 번호
    file_url = Column(String(500), nullable=False)  # 문서 파일 URL
    file_name = Column(String(255), nullable=False)  # 원본 파일명
    file_size = Column(BigInteger, nullable=True)  # 파일 크기 (bytes)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False)
    signed_at = Column(DateTime, nullable=True)  # 서명 완료 시간
    signed_by = Column(String(255), nullable=True)  # 서명자 이름
    document_metadata = Column(JSON, nullable=True)  # 추가 메타데이터 (OCR 결과, 구조화 정보 등) - metadata는 SQLAlchemy 예약어
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    # contract relationship은 VendorContract에서 정의됨


class VendorPaymentSchedule(Base):
    """결제 일정"""
    __tablename__ = "vendor_payment_schedules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contract_id = Column(BigInteger, ForeignKey("vendor_contracts.id", ondelete="CASCADE"), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)  # deposit, interim, balance, additional
    amount = Column(Numeric(15, 2), nullable=False)  # 결제 금액
    due_date = Column(Date, nullable=False)  # 납부 기한
    paid_date = Column(Date, nullable=True)  # 실제 결제일
    payment_method = Column(String(50), nullable=True)  # 결제 방법 (카드, 계좌이체 등)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    reminder_sent = Column(Boolean, default=False, nullable=False)  # 알림 발송 여부
    notes = Column(Text, nullable=True)  # 결제 메모
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    # contract relationship은 VendorContract에서 정의됨

