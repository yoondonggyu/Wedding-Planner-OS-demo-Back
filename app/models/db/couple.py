"""
커플 연결 모델
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class CoupleStatus(str, enum.Enum):
    PENDING = "PENDING"  # 연결 대기 중
    CONNECTED = "CONNECTED"  # 연결 완료

class Couple(Base):
    """커플 연결 정보"""
    __tablename__ = "couples"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    couple_key = Column(String(32), unique=True, nullable=False)  # 커플 고유 키
    user1_id = Column(BigInteger, nullable=False)  # 첫 번째 사용자 (키 발급자)
    user2_id = Column(BigInteger, nullable=True)  # 두 번째 사용자 (키 입력자)
    user1_entered_key = Column(String(32), nullable=True)  # user1이 입력한 상대방의 키
    user2_entered_key = Column(String(32), nullable=True)  # user2가 입력한 상대방의 키
    status = Column(SQLEnum(CoupleStatus), default=CoupleStatus.PENDING, nullable=False)
    connected_at = Column(DateTime, nullable=True)  # 연결 완료 시간
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __str__(self):
        return f"Couple {self.id} ({self.couple_key})"

