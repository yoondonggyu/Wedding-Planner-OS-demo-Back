"""
채팅 메모리 라우터
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import ChatMemoryCreateReq, ChatMemoryUpdateReq
from app.controllers import chat_memory_controller
from app.core.database import get_db
from app.core.security import get_current_user_id

router = APIRouter(tags=["Chat Memory"])


@router.post("/chat-memories")
async def create_chat_memory(
    request: ChatMemoryCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """채팅 메모리 생성"""
    try:
        result = chat_memory_controller.create_chat_memory(user_id, request, db)
        return {
            "message": "chat_memory_created",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat-memories")
async def get_chat_memories(
    include_shared: bool = True,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """채팅 메모리 목록 조회"""
    memories = chat_memory_controller.get_chat_memories(user_id, db, include_shared)
    return {
        "message": "chat_memories_retrieved",
        "data": memories
    }


@router.get("/chat-memories/{memory_id}")
async def get_chat_memory(
    memory_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """특정 채팅 메모리 조회"""
    memory = chat_memory_controller.get_chat_memory(memory_id, user_id, db)
    if not memory:
        raise HTTPException(status_code=404, detail="Chat memory not found")
    return {
        "message": "chat_memory_retrieved",
        "data": memory
    }


@router.patch("/chat-memories/{memory_id}")
async def update_chat_memory(
    memory_id: int,
    request: ChatMemoryUpdateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """채팅 메모리 수정"""
    result = chat_memory_controller.update_chat_memory(memory_id, user_id, request, db)
    if not result:
        raise HTTPException(status_code=404, detail="Chat memory not found")
    return {
        "message": "chat_memory_updated",
        "data": result
    }


@router.delete("/chat-memories/{memory_id}")
async def delete_chat_memory(
    memory_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """채팅 메모리 삭제"""
    success = chat_memory_controller.delete_chat_memory(memory_id, user_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Chat memory not found")
    return {
        "message": "chat_memory_deleted",
        "data": {"id": memory_id}
    }


