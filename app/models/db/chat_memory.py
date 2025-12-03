"""
채팅 메모리 모델 - 사용자가 LLM 대화에서 기억하고 싶은 내용을 저장
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChatMemory(Base):
    __tablename__ = "chat_memories"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    couple_id = Column(BigInteger, ForeignKey("couples.id", ondelete="SET NULL"), nullable=True)  # 커플 공유 가능
    
    # 저장할 내용
    content = Column(Text, nullable=False)  # 저장할 메시지 내용
    title = Column(String(255), nullable=True)  # 사용자가 지정한 제목 (선택적)
    tags = Column(JSON, nullable=True)  # 태그 리스트 ["웨딩홀", "예산"] 형태
    
    # 컨텍스트 정보
    original_message = Column(Text, nullable=True)  # 원본 사용자 메시지
    ai_response = Column(Text, nullable=True)  # AI 응답 전체
    context_summary = Column(Text, nullable=True)  # 컨텍스트 요약
    
    # Vector DB 연동
    vector_db_id = Column(String(255), nullable=True)  # ChromaDB에 저장된 벡터 ID
    vector_db_collection = Column(String(100), nullable=True)  # ChromaDB 컬렉션 이름
    
    # 메타데이터
    is_shared_with_partner = Column(Integer, default=0, nullable=False)  # 파트너와 공유 여부 (0: 비공개, 1: 공유)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="chat_memories")

    def __str__(self):
        return f"ChatMemory {self.id}: {self.title or self.content[:50]}"

