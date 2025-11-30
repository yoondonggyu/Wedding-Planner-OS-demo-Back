from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.schemas import ChatRequest
from app.controllers import chat_controller
from app.core.database import get_db
from app.core.security import get_current_user_id
from typing import Optional

router = APIRouter(tags=["chat"])

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """챗봇 대화 API - RAG + 개인 데이터 통합 + Vector DB 검색"""
    return StreamingResponse(
        chat_controller.chat_stream(
            message=request.message,
            user_id=user_id,
            include_context=request.include_context,
            db=db
        ),
        media_type="application/x-ndjson"
    )

@router.post("/chat/simple")
async def chat_simple(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """챗봇 대화 API (비스트리밍) - RAG + 개인 데이터 통합 + Vector DB 검색"""
    response = await chat_controller.chat_simple(
        message=request.message,
        user_id=user_id,
        include_context=request.include_context,
        db=db
    )
    return response





