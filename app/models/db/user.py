from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.user_roles import UserRole
import enum

class Gender(str, enum.Enum):
    BRIDE = "BRIDE"  # 신부
    GROOM = "GROOM"  # 신랑

class VendorApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"  # 승인 대기
    APPROVED = "APPROVED"  # 승인됨
    REJECTED = "REJECTED"  # 거부됨

class AdminApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"  # 승인 대기
    APPROVED = "APPROVED"  # 승인됨
    REJECTED = "REJECTED"  # 거부됨

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=False)
    profile_image_url = Column(Text, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    gender = Column(SQLEnum(Gender), nullable=True)  # 신부/신랑 구분
    couple_key = Column(String(32), unique=True, nullable=True)  # 자신의 커플 키
    partner_couple_key = Column(String(32), nullable=True)  # 상대방의 커플 키
    couple_id = Column(BigInteger, ForeignKey("couples.id", ondelete="SET NULL"), nullable=True)  # 연결된 커플 ID
    vendor_approval_status = Column(SQLEnum(VendorApprovalStatus), nullable=True)  # 제휴 업체 승인 상태
    admin_approval_status = Column(SQLEnum(AdminApprovalStatus), nullable=True)  # 관리자 승인 상태
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    couple = relationship("Couple", foreign_keys=[couple_id], backref="users")

    def __str__(self):
        return f"{self.nickname} ({self.email})"






