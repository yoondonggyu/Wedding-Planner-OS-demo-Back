"""
챗봇 컨트롤러
"""
from typing import AsyncGenerator, Dict
from app.services import chat_service
from sqlalchemy.orm import Session


async def chat_stream(
    message: str,
    user_id: int,
    include_context: bool = True,
    db: Session = None,
    model: str | None = None
) -> AsyncGenerator[str, None]:
    """챗봇 스트리밍 응답"""
    async for chunk in chat_service.chat_stream(message, user_id, include_context, db, model):
        yield chunk


async def chat_simple(
    message: str,
    user_id: int,
    include_context: bool = True,
    db: Session = None
) -> Dict:
    """챗봇 단순 응답"""
    return await chat_service.chat_simple(message, user_id, include_context, db)





