"""
디지털 초대장 및 축의금 결제 시스템 모델
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, Enum as SQLEnum, ForeignKey, Boolean, JSON, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class InvitationTheme(str, enum.Enum):
    """초대장 테마"""
    CLASSIC = "CLASSIC"
    MODERN = "MODERN"
    ROMANTIC = "ROMANTIC"
    ELEGANT = "ELEGANT"
    MINIMAL = "MINIMAL"
    NATURE = "NATURE"


class RSVPStatus(str, enum.Enum):
    """RSVP 상태"""
    PENDING = "PENDING"  # 미응답
    ATTENDING = "ATTENDING"  # 참석
    NOT_ATTENDING = "NOT_ATTENDING"  # 불참
    MAYBE = "MAYBE"  # 미정


class PaymentStatus(str, enum.Enum):
    """결제 상태"""
    PENDING = "PENDING"  # 대기
    COMPLETED = "COMPLETED"  # 완료
    FAILED = "FAILED"  # 실패
    CANCELLED = "CANCELLED"  # 취소


class PaymentMethod(str, enum.Enum):
    """결제 방법"""
    BANK_TRANSFER = "BANK_TRANSFER"  # 계좌이체
    KAKAO_PAY = "KAKAO_PAY"  # 카카오페이
    TOSS = "TOSS"  # 토스
    CREDIT_CARD = "CREDIT_CARD"  # 신용카드


class DigitalInvitation(Base):
    """디지털 초대장"""
    __tablename__ = "digital_invitations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    couple_id = Column(BigInteger, ForeignKey("couples.id", ondelete="SET NULL"), nullable=True)
    invitation_design_id = Column(BigInteger, ForeignKey("invitation_designs.id", ondelete="SET NULL"), nullable=True)  # 연결된 청첩장 디자인
    
    # 초대장 정보
    theme = Column(SQLEnum(InvitationTheme), nullable=False)
    invitation_url = Column(String(255), unique=True, nullable=False)  # 고유 URL (예: /invitation/abc123)
    
    # 예식 정보
    groom_name = Column(String(100), nullable=False)
    bride_name = Column(String(100), nullable=False)
    wedding_date = Column(DateTime, nullable=False)
    wedding_time = Column(String(50), nullable=True)  # HH:MM
    wedding_location = Column(String(255), nullable=False)
    wedding_location_detail = Column(Text, nullable=True)  # 상세 주소
    map_url = Column(Text, nullable=True)  # 지도 링크
    parking_info = Column(Text, nullable=True)  # 주차 안내
    
    # 초대장 설정
    invitation_data = Column(JSON, nullable=False)  # 초대장 데이터 (테마별 설정)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 통계
    view_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="digital_invitations")
    payments = relationship("Payment", backref="invitation", cascade="all, delete-orphan")
    rsvps = relationship("RSVP", backref="invitation", cascade="all, delete-orphan")
    guest_messages = relationship("GuestMessage", backref="invitation", cascade="all, delete-orphan")


class Payment(Base):
    """축의금 결제"""
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    invitation_id = Column(BigInteger, ForeignKey("digital_invitations.id", ondelete="CASCADE"), nullable=False)
    
    # 결제자 정보
    payer_name = Column(String(100), nullable=False)
    payer_phone = Column(String(50), nullable=True)
    payer_message = Column(Text, nullable=True)  # 축하 메시지
    
    # 결제 정보
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # 결제 상세
    transaction_id = Column(String(255), nullable=True)  # 결제 거래 ID
    payment_data = Column(JSON, nullable=True)  # 결제 상세 데이터
    
    # 감사 메시지
    thank_you_message_sent = Column(Boolean, default=False, nullable=False)
    thank_you_sent_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class RSVP(Base):
    """RSVP (참석 여부)"""
    __tablename__ = "rsvps"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    invitation_id = Column(BigInteger, ForeignKey("digital_invitations.id", ondelete="CASCADE"), nullable=False)
    
    # 참석자 정보
    guest_name = Column(String(100), nullable=False)
    guest_phone = Column(String(50), nullable=True)
    guest_email = Column(String(255), nullable=True)
    
    # RSVP 정보
    status = Column(SQLEnum(RSVPStatus), default=RSVPStatus.PENDING, nullable=False)
    plus_one = Column(Boolean, default=False, nullable=False)  # 동반자 여부
    plus_one_name = Column(String(100), nullable=True)  # 동반자 이름
    dietary_restrictions = Column(Text, nullable=True)  # 식이 제한 (알레르기 등)
    special_requests = Column(Text, nullable=True)  # 특별 요청사항
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class GuestMessage(Base):
    """하객 메시지 및 사진"""
    __tablename__ = "guest_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    invitation_id = Column(BigInteger, ForeignKey("digital_invitations.id", ondelete="CASCADE"), nullable=False)
    
    # 작성자 정보
    guest_name = Column(String(100), nullable=False)
    guest_phone = Column(String(50), nullable=True)
    
    # 메시지
    message = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)  # 업로드된 사진 URL
    
    # 승인 상태 (필요시)
    is_approved = Column(Boolean, default=True, nullable=False)  # 기본적으로 승인됨
    
    created_at = Column(DateTime, default=func.now(), nullable=False)

