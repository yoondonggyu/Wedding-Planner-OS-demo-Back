from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, BigInteger, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class BudgetCategory(str, enum.Enum):
    HALL = "hall"
    DRESS = "dress"
    STUDIO = "studio"
    SNAP = "snap"
    HONEYMOON = "honeymoon"
    ETC = "etc"


class PayerEnum(str, enum.Enum):
    GROOM = "groom"
    BRIDE = "bride"
    BOTH = "both"


class BudgetItem(Base):
    __tablename__ = "budget_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    couple_id = Column(BigInteger, ForeignKey("couples.id", ondelete="SET NULL"), nullable=True)  # 커플 공유
    item_name = Column(String(255), nullable=False)
    category = Column(Enum(BudgetCategory), nullable=False)
    estimated_budget = Column(Numeric(15, 2), nullable=False)
    actual_expense = Column(Numeric(15, 2), default=0.0, nullable=False)
    quantity = Column(Numeric(10, 2), default=1.0, nullable=False)
    unit = Column(String(50), nullable=True)
    payer = Column(Enum(PayerEnum), default="both", nullable=False)
    notes = Column(Text, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)  # metadata는 SQLAlchemy 예약어이므로 컬럼명으로 매핑
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="budget_items")


class UserTotalBudget(Base):
    __tablename__ = "user_total_budgets"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_budget = Column(Numeric(15, 2), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="user_total_budget", uselist=False)

