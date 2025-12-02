"""
음성 비서 컨트롤러
"""
from typing import Dict
import base64
from app.schemas import VoiceProcessReq
from app.services import voice_service, stt_service


async def process_voice(
    request: VoiceProcessReq
) -> Dict:
    """음성 처리 (STT + 자동 정리)"""
    # 1. STT: 음성 → 텍스트
    text = None
    
    if request.text:
        # 직접 텍스트 입력
        text = request.text
    elif request.audio_data:
        # 오디오 데이터 디코딩 및 STT
        try:
            audio_bytes = base64.b64decode(request.audio_data)
            text = await stt_service.transcribe_audio(audio_bytes)
        except Exception as e:
            return {
                "message": "error",
                "data": {"error": f"STT 실패: {str(e)}"}
            }
    
    if not text:
        return {
            "message": "error",
            "data": {"error": "텍스트를 추출할 수 없습니다."}
        }
    
    # 2. 자동 정리 파이프라인 실행
    if request.auto_organize:
        organized = await voice_service.analyze_intent_and_organize(
            text, request.user_id
        )
        
        return {
            "message": "voice_processed",
            "data": {
                "transcribed_text": text,
                "intent": organized.get("intent"),
                "summary": organized.get("summary"),
                "organized_items": organized.get("organized_items", [])
            }
        }
    else:
        return {
            "message": "voice_transcribed",
            "data": {
                "transcribed_text": text
            }
        }


async def generate_response(
    query: str,
    user_id: int
) -> Dict:
    """음성 질문에 대한 답변 생성"""
    response_text = await voice_service.generate_voice_response(query, user_id)
    
    return {
        "message": "voice_response_generated",
        "data": {
            "response": response_text
        }
    }







