"""
채팅 메모리 컨트롤러
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.db import ChatMemory, User, Couple
from app.schemas import ChatMemoryCreateReq, ChatMemoryUpdateReq
from app.services.chat_memory_vector_service import (
    vectorize_chat_memory,
    delete_chat_memory_vector
)


def create_chat_memory(
    user_id: int,
    request: ChatMemoryCreateReq,
    db: Session
) -> Dict:
    """채팅 메모리 생성"""
    # 사용자 정보 조회
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    
    # 커플 ID 가져오기
    couple_id = user.couple_id if user.couple_id else None
    
    # 메모리 생성
    memory = ChatMemory(
        user_id=user_id,
        couple_id=couple_id,
        content=request.content,
        title=request.title,
        tags=request.tags if request.tags else [],
        original_message=request.original_message,
        ai_response=request.ai_response,
        context_summary=request.context_summary,
        is_shared_with_partner=1 if request.is_shared_with_partner else 0
    )
    
    db.add(memory)
    db.commit()
    db.refresh(memory)
    
    # ChromaDB에 벡터로 저장
    vector_id = vectorize_chat_memory(memory)
    if vector_id:
        memory.vector_db_id = vector_id
        memory.vector_db_collection = "chat_memories"
        db.commit()
        db.refresh(memory)
    
    return {
        "id": memory.id,
        "content": memory.content,
        "title": memory.title,
        "tags": memory.tags,
        "vector_db_id": memory.vector_db_id,
        "created_at": memory.created_at.isoformat() if memory.created_at else None
    }


def get_chat_memories(
    user_id: int,
    db: Session,
    include_shared: bool = True
) -> List[Dict]:
    """채팅 메모리 목록 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    
    # 사용자 본인의 메모리 + 파트너와 공유된 메모리
    if include_shared and user.couple_id:
        memories = db.query(ChatMemory).filter(
            or_(
                ChatMemory.user_id == user_id,
                and_(
                    ChatMemory.couple_id == user.couple_id,
                    ChatMemory.is_shared_with_partner == 1
                )
            )
        ).order_by(ChatMemory.created_at.desc()).all()
    else:
        memories = db.query(ChatMemory).filter(
            ChatMemory.user_id == user_id
        ).order_by(ChatMemory.created_at.desc()).all()
    
    return [
        {
            "id": m.id,
            "content": m.content,
            "title": m.title,
            "tags": m.tags or [],
            "original_message": m.original_message,
            "ai_response": m.ai_response,
            "context_summary": m.context_summary,
            "is_shared_with_partner": bool(m.is_shared_with_partner),
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None
        }
        for m in memories
    ]


def get_chat_memory(
    memory_id: int,
    user_id: int,
    db: Session
) -> Optional[Dict]:
    """특정 채팅 메모리 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # 본인 메모리 또는 파트너와 공유된 메모리만 조회 가능
    memory = db.query(ChatMemory).filter(
        ChatMemory.id == memory_id
    ).first()
    
    if not memory:
        return None
    
    # 권한 확인
    if memory.user_id != user_id:
        if not (memory.couple_id == user.couple_id and memory.is_shared_with_partner == 1):
            return None
    
    return {
        "id": memory.id,
        "content": memory.content,
        "title": memory.title,
        "tags": memory.tags or [],
        "original_message": memory.original_message,
        "ai_response": memory.ai_response,
        "context_summary": memory.context_summary,
        "is_shared_with_partner": bool(memory.is_shared_with_partner),
        "created_at": memory.created_at.isoformat() if memory.created_at else None,
        "updated_at": memory.updated_at.isoformat() if memory.updated_at else None
    }


def update_chat_memory(
    memory_id: int,
    user_id: int,
    request: ChatMemoryUpdateReq,
    db: Session
) -> Optional[Dict]:
    """채팅 메모리 수정"""
    memory = db.query(ChatMemory).filter(
        ChatMemory.id == memory_id,
        ChatMemory.user_id == user_id  # 본인 메모리만 수정 가능
    ).first()
    
    if not memory:
        return None
    
    if request.title is not None:
        memory.title = request.title
    if request.tags is not None:
        memory.tags = request.tags
    if request.is_shared_with_partner is not None:
        memory.is_shared_with_partner = 1 if request.is_shared_with_partner else 0
    
    db.commit()
    db.refresh(memory)
    
    return {
        "id": memory.id,
        "content": memory.content,
        "title": memory.title,
        "tags": memory.tags or [],
        "is_shared_with_partner": bool(memory.is_shared_with_partner),
        "updated_at": memory.updated_at.isoformat() if memory.updated_at else None
    }


def delete_chat_memory(
    memory_id: int,
    user_id: int,
    db: Session
) -> bool:
    """채팅 메모리 삭제"""
    memory = db.query(ChatMemory).filter(
        ChatMemory.id == memory_id,
        ChatMemory.user_id == user_id  # 본인 메모리만 삭제 가능
    ).first()
    
    if not memory:
        return False
    
    # ChromaDB에서 벡터 삭제
    if memory.vector_db_id:
        delete_chat_memory_vector(memory.vector_db_id)
    
    db.delete(memory)
    db.commit()
    return True

