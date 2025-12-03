from fastapi import APIRouter, Query
from app.schemas import VoiceProcessReq
from app.controllers import voice_controller

router = APIRouter(tags=["voice"])

@router.post("/voice/process")
async def process_voice(request: VoiceProcessReq):
    """음성 처리 (STT + 자동 정리 파이프라인)"""
    return await voice_controller.process_voice(request)

@router.post("/voice/response")
async def generate_voice_response(
    query: str = Query(...),
    user_id: int = Query(...)
):
    """음성 질문에 대한 답변 생성"""
    return await voice_controller.generate_response(query, user_id)








