from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger, Boolean, JSON, Date, Time, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PriorityEnum(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class AssigneeEnum(str, enum.Enum):
    groom = "groom"
    bride = "bride"
    both = "both"


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    couple_id = Column(BigInteger, ForeignKey("couples.id", ondelete="SET NULL"), nullable=True)  # 커플 공유
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)  # DB는 DATE 타입
    end_date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=True)  # DB는 TIME 타입
    end_time = Column(Time, nullable=True)
    location = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True)
    priority = Column(Enum(PriorityEnum), nullable=True)
    assignee = Column(Enum(AssigneeEnum), nullable=True)
    progress = Column(Integer, nullable=True)  # DB에 있음
    is_completed = Column(Boolean, nullable=True)
    # metadata는 SQLAlchemy 예약어이므로 사용 불가 - DB에 있지만 모델에서는 제외
    # 필요시 별도 쿼리로 접근해야 함
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="calendar_events")

# Todo 모델 제거됨 - calendar_events 테이블의 category='todo'로 통합됨
# 기존 todos 테이블 데이터는 migrate_todos_to_events.py 스크립트로 마이그레이션 필요


class WeddingDate(Base):
    __tablename__ = "wedding_dates"

    # DB에는 id가 없고 user_id가 primary key인 것 같지만, 모델에서는 id를 추가
    # 실제로는 user_id가 unique이므로 이를 primary key로 사용
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    wedding_date = Column(Date, nullable=False)  # DB는 DATE 타입
    dday_offset = Column(Integer, nullable=True)  # DB에 있는 컬럼
    updated_at = Column(DateTime, nullable=True)
    # created_at은 DB에 없음

    # Relationships
    user = relationship("User", backref="wedding_date", uselist=False)

