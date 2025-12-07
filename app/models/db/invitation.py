"""
청첩장 디자인 서비스 모델
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, Enum as SQLEnum, ForeignKey, Boolean, JSON, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class InvitationTemplateStyle(str, enum.Enum):
    """템플릿 스타일"""
    CLASSIC = "CLASSIC"  # 클래식
    MODERN = "MODERN"  # 모던
    VINTAGE = "VINTAGE"  # 빈티지
    MINIMAL = "MINIMAL"  # 미니멀
    LUXURY = "LUXURY"  # 럭셔리
    NATURE = "NATURE"  # 자연스러운
    ROMANTIC = "ROMANTIC"  # 로맨틱


class InvitationDesignStatus(str, enum.Enum):
    """디자인 상태"""
    DRAFT = "DRAFT"  # 초안
    COMPLETED = "COMPLETED"  # 완료
    ORDERED = "ORDERED"  # 주문됨


class InvitationTemplate(Base):
    """청첩장 템플릿"""
    __tablename__ = "invitation_templates"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # 템플릿 이름
    style = Column(SQLEnum(InvitationTemplateStyle), nullable=False)  # 스타일
    preview_image_url = Column(Text, nullable=True)  # 미리보기 이미지 URL
    template_data = Column(JSON, nullable=False)  # 템플릿 데이터 (레이아웃, 색상, 폰트 등)
    is_active = Column(Boolean, default=True, nullable=False)  # 활성화 여부
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    designs = relationship("InvitationDesign", backref="template")


class InvitationDesign(Base):
    """청첩장 디자인 (사용자가 만든 디자인)"""
    __tablename__ = "invitation_designs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    couple_id = Column(BigInteger, ForeignKey("couples.id", ondelete="SET NULL"), nullable=True)  # 커플 공유
    template_id = Column(BigInteger, ForeignKey("invitation_templates.id", ondelete="SET NULL"), nullable=True)
    
    # 디자인 데이터
    design_data = Column(JSON, nullable=False)  # 디자인 설정 (문구, 이미지, 레이아웃 등)
    status = Column(SQLEnum(InvitationDesignStatus), default=InvitationDesignStatus.DRAFT, nullable=False)
    
    # 부모님 성함
    groom_father_name = Column(String(100), nullable=True)
    groom_mother_name = Column(String(100), nullable=True)
    bride_father_name = Column(String(100), nullable=True)
    bride_mother_name = Column(String(100), nullable=True)
    
    # 지도 정보
    map_lat = Column(Numeric(10, 8), nullable=True)  # 위도
    map_lng = Column(Numeric(11, 8), nullable=True)  # 경도
    map_image_url = Column(Text, nullable=True)  # 약도 이미지 URL
    
    # 선택된 톤 및 문구
    selected_tone = Column(String(50), nullable=True)  # affectionate, cheerful, polite, formal, emotional
    selected_text = Column(Text, nullable=True)  # 선택된 문구
    
    # 생성된 이미지
    generated_image_url = Column(Text, nullable=True)  # AI 생성 이미지 URL
    generated_image_model = Column(String(50), nullable=True)  # 사용한 모델 (flux, sdxl, gemini)
    
    # QR 코드 관련
    qr_code_url = Column(Text, nullable=True)  # QR 코드 이미지 URL
    qr_code_data = Column(JSON, nullable=True)  # QR 코드 데이터 (디지털 초대장, 축의금, RSVP 링크)
    
    # 파일 관련
    pdf_url = Column(Text, nullable=True)  # 생성된 PDF URL
    preview_image_url = Column(Text, nullable=True)  # 미리보기 이미지 URL
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="invitation_designs")
    orders = relationship("InvitationOrder", backref="design")


class InvitationOrder(Base):
    """청첩장 주문 정보"""
    __tablename__ = "invitation_orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    design_id = Column(BigInteger, ForeignKey("invitation_designs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 주문 정보
    quantity = Column(Integer, nullable=False)  # 주문 수량
    paper_type = Column(String(50), nullable=True)  # 종이 타입 (일반, 고급, 에코 등)
    paper_size = Column(String(50), nullable=True)  # 종이 크기 (A5, A6 등)
    total_price = Column(Numeric(15, 2), nullable=True)  # 총 가격
    
    # 주문 상태
    order_status = Column(String(50), default="PENDING", nullable=False)  # PENDING, CONFIRMED, PRINTING, SHIPPED, DELIVERED
    vendor_id = Column(BigInteger, ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True)  # 인쇄 업체
    
    # 배송 정보
    shipping_address = Column(Text, nullable=True)
    shipping_phone = Column(String(50), nullable=True)
    shipping_name = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="invitation_orders")
    vendor = relationship("Vendor", backref="invitation_orders")

