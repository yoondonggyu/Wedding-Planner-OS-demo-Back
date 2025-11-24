"""
OCR 서비스 - 견적서/영수증 이미지에서 텍스트 추출
"""
import base64
from typing import Dict, Optional
import io
from app.services.model_client import get_model_api_base_url
import httpx

# 선택적 import
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ pytesseract 또는 PIL이 설치되지 않았습니다. OCR 기능을 사용할 수 없습니다.")


async def extract_text_from_image(image_data: bytes) -> Optional[str]:
    """
    이미지에서 텍스트 추출 (Tesseract OCR)
    """
    if not OCR_AVAILABLE:
        print("⚠️ OCR 기능을 사용할 수 없습니다. pytesseract를 설치해주세요.")
        return None
    
    try:
        # 이미지 로드
        image = Image.open(io.BytesIO(image_data))
        
        # OCR 수행
        text = pytesseract.image_to_string(image, lang='kor+eng')
        
        return text.strip() if text else None
    except Exception as e:
        print(f"⚠️ OCR 실패: {e}")
        return None


async def extract_text_from_image_paddle(image_data: bytes) -> Optional[str]:
    """
    PaddleOCR을 사용한 텍스트 추출 (더 정확하지만 설치 필요)
    모델 서버에 PaddleOCR이 있다면 API로 호출
    """
    base_url = get_model_api_base_url()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 이미지를 base64로 인코딩
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = await client.post(
                f"{base_url}/ocr",
                json={"image": image_base64},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")
    except Exception as e:
        print(f"⚠️ PaddleOCR API 호출 실패: {e}")
        # Fallback to Tesseract
        return await extract_text_from_image(image_data)

