"""
STT 서비스 - Whisper 기반 음성 인식
"""
import base64
import io
from typing import Optional
from app.services.model_client import get_model_api_base_url
import httpx

# 선택적 import
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ whisper가 설치되지 않았습니다. STT 기능을 사용할 수 없습니다.")


async def transcribe_audio_whisper(audio_data: bytes) -> Optional[str]:
    """
    Whisper를 사용한 음성 인식 (로컬)
    """
    if not WHISPER_AVAILABLE:
        return None
    
    try:
        # Whisper 모델 로드 (base 모델 사용)
        model = whisper.load_model("base")
        
        # 오디오 파일로 변환
        audio_file = io.BytesIO(audio_data)
        
        # 음성 인식
        result = model.transcribe(audio_file, language="ko")
        
        return result.get("text", "").strip()
    except Exception as e:
        print(f"⚠️ Whisper STT 실패: {e}")
        return None


async def transcribe_audio_api(audio_data: bytes) -> Optional[str]:
    """
    외부 STT API를 사용한 음성 인식 (모델 서버 또는 외부 API)
    """
    base_url = get_model_api_base_url()
    try:
        # 오디오를 base64로 인코딩
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/stt",
                json={"audio": audio_base64},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")
    except Exception as e:
        print(f"⚠️ STT API 호출 실패: {e}")
        # Fallback to Whisper
        return await transcribe_audio_whisper(audio_data)


async def transcribe_audio(audio_data: bytes) -> Optional[str]:
    """
    음성 인식 (우선순위: API > Whisper)
    """
    # API 시도
    result = await transcribe_audio_api(audio_data)
    if result:
        return result
    
    # Whisper 시도
    if WHISPER_AVAILABLE:
        result = await transcribe_audio_whisper(audio_data)
        if result:
            return result
    
    return None








