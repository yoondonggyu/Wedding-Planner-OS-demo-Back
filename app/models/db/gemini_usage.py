"""
Gemini 모델 사용 횟수 제한 모델
"""
from sqlalchemy import Column, Integer, Date, DateTime, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class GeminiImageUsage(Base):
    """Gemini 이미지 생성 사용 횟수 (하루 5회 제한)"""
    __tablename__ = "gemini_image_usage"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    usage_date = Column(Date, nullable=False)  # 사용 날짜 (YYYY-MM-DD)
    usage_count = Column(Integer, default=0, nullable=False)  # 당일 사용 횟수
    last_used_at = Column(DateTime, nullable=True)  # 마지막 사용 시간
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="gemini_image_usage")

    def __str__(self):
        return f"GeminiImageUsage(user_id={self.user_id}, date={self.usage_date}, count={self.usage_count})"

