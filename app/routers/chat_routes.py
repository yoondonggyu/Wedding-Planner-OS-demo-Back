from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas import ChatRequest
from app.controllers import chat_controller
from typing import Optional

router = APIRouter(tags=["chat"])

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """챗봇 대화 API - RAG + 개인 데이터 통합"""
    if not request.user_id:
        raise HTTPException(status_code=401, detail="user_id is required")
    
    return StreamingResponse(
        chat_controller.chat_stream(
            message=request.message,
            user_id=request.user_id,
            include_context=request.include_context
        ),
        media_type="application/x-ndjson"
    )

@router.post("/chat/simple")
async def chat_simple(request: ChatRequest):
    """챗봇 대화 API (비스트리밍)"""
    if not request.user_id:
        raise HTTPException(status_code=401, detail="user_id is required")
    
    response = await chat_controller.chat_simple(
        message=request.message,
        user_id=request.user_id,
        include_context=request.include_context
    )
    return response


