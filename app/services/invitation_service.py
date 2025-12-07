"""
청첩장 디자인 서비스 - QR 코드 생성, PDF 생성, AI 문구 추천, 카카오 Maps API 연동
"""
import qrcode
from io import BytesIO
import base64
from typing import Dict, Optional
from reportlab.lib.pagesizes import A5, A6
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import os
import httpx
from app.services.model_client import chat_with_model


def generate_qr_code(data: Dict) -> str:
    """
    QR 코드 생성 및 base64 인코딩된 이미지 반환
    
    Args:
        data: QR 코드에 포함할 데이터 (디지털 초대장, 축의금, RSVP 링크)
    
    Returns:
        base64 인코딩된 QR 코드 이미지 문자열
    """
    # QR 코드 데이터 구성
    qr_data_parts = []
    if data.get("digital_invitation_url"):
        qr_data_parts.append(f"초대장: {data['digital_invitation_url']}")
    if data.get("payment_url"):
        qr_data_parts.append(f"축의금: {data['payment_url']}")
    if data.get("rsvp_url"):
        qr_data_parts.append(f"RSVP: {data['rsvp_url']}")
    
    if not qr_data_parts:
        return None
    
    qr_text = "\n".join(qr_data_parts)
    
    # QR 코드 생성
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_text)
    qr.make(fit=True)
    
    # 이미지 생성
    img = qr.make_image(fill_color="black", back_color="white")
    
    # base64 인코딩
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def generate_qr_code_image(data: Dict) -> bytes:
    """
    QR 코드 이미지 바이트 반환 (파일 저장용)
    
    Args:
        data: QR 코드에 포함할 데이터
    
    Returns:
        PNG 이미지 바이트
    """
    qr_data_parts = []
    if data.get("digital_invitation_url"):
        qr_data_parts.append(f"초대장: {data['digital_invitation_url']}")
    if data.get("payment_url"):
        qr_data_parts.append(f"축의금: {data['payment_url']}")
    if data.get("rsvp_url"):
        qr_data_parts.append(f"RSVP: {data['rsvp_url']}")
    
    if not qr_data_parts:
        return None
    
    qr_text = "\n".join(qr_data_parts)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()


async def recommend_invitation_text(
    groom_name: str,
    bride_name: str,
    wedding_date: str,
    wedding_time: Optional[str] = None,
    wedding_location: Optional[str] = None,
    style: Optional[str] = None,
    additional_info: Optional[str] = None
) -> Dict:
    """
    AI 기반 청첩장 문구 추천 (모델 서버의 Gemini 2.5 Flash 사용)
    
    Args:
        groom_name: 신랑 이름
        bride_name: 신부 이름
        wedding_date: 예식일 (YYYY-MM-DD)
        wedding_time: 예식 시간 (HH:MM)
        wedding_location: 예식 장소
        style: 스타일 (CLASSIC, MODERN, VINTAGE 등)
        additional_info: 추가 정보
    
    Returns:
        {"options": [option1, option2, ...]} 형식의 딕셔너리 (5개 옵션)
    """
    from app.services.model_client import get_model_api_base_url
    import httpx
    
    base_url = get_model_api_base_url()
    url = f"{base_url}/invitation/text-recommend"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json={
                    "groom_name": groom_name,
                    "bride_name": bride_name,
                    "wedding_date": wedding_date,
                    "wedding_time": wedding_time,
                    "wedding_location": wedding_location,
                    "style": style,
                    "additional_info": additional_info
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            # 모델 서버 응답 형식: {"message": "text_recommended", "data": {"options": [...]}}
            if "data" in result and "options" in result["data"]:
                return result["data"]
            else:
                # 하위 호환성: 직접 options가 있는 경우
                if "options" in result:
                    return {"options": result["options"]}
                else:
                    raise ValueError("올바른 응답 형식이 아닙니다")
                    
    except httpx.TimeoutException:
        print("⚠️ 문구 추천 API 호출 타임아웃 (60초 초과)")
    except httpx.HTTPStatusError as e:
        print(f"⚠️ 문구 추천 API HTTP 에러: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"⚠️ AI 문구 추천 실패: {e}")
    
    # 기본 문구 옵션 반환 (5개)
    return {
        "options": [
            {
                "main_text": f"{groom_name} · {bride_name} 두 사람이 하나가 되어\n새로운 인생을 시작합니다.",
                "groom_father": "",
                "groom_mother": "",
                "bride_father": "",
                "bride_mother": "",
                "wedding_info": f"{wedding_date}\n{wedding_time or ''}\n{wedding_location or ''}",
                "reception_info": wedding_location or "",
                "closing_text": "바쁘시겠지만 참석해 주시면 감사하겠습니다."
            },
            {
                "main_text": f"{groom_name}님과 {bride_name}님이\n사랑으로 하나가 되어\n새로운 가정을 이룹니다.",
                "groom_father": "",
                "groom_mother": "",
                "bride_father": "",
                "bride_mother": "",
                "wedding_info": f"{wedding_date}\n{wedding_time or ''}\n{wedding_location or ''}",
                "reception_info": wedding_location or "",
                "closing_text": "소중한 분들을 모시고 싶어\n이렇게 초대의 말씀을 드립니다."
            },
            {
                "main_text": f"{groom_name} · {bride_name}\n두 사람이 만나\n하나의 가정을 이루려 합니다.",
                "groom_father": "",
                "groom_mother": "",
                "bride_father": "",
                "bride_mother": "",
                "wedding_info": f"{wedding_date}\n{wedding_time or ''}\n{wedding_location or ''}",
                "reception_info": wedding_location or "",
                "closing_text": "바쁘시겠지만 참석해 주시면 감사하겠습니다."
            },
            {
                "main_text": f"{groom_name}과 {bride_name}이\n인연을 맺어\n새로운 출발을 합니다.",
                "groom_father": "",
                "groom_mother": "",
                "bride_father": "",
                "bride_mother": "",
                "wedding_info": f"{wedding_date}\n{wedding_time or ''}\n{wedding_location or ''}",
                "reception_info": wedding_location or "",
                "closing_text": "귀한 시간 내어 주시면\n더욱 기쁘겠습니다."
            },
            {
                "main_text": f"{groom_name} · {bride_name}\n두 분이 만나\n행복한 가정을 꾸리려 합니다.",
                "groom_father": "",
                "groom_mother": "",
                "bride_father": "",
                "bride_mother": "",
                "wedding_info": f"{wedding_date}\n{wedding_time or ''}\n{wedding_location or ''}",
                "reception_info": wedding_location or "",
                "closing_text": "바쁘시겠지만 참석해 주시면\n진심으로 감사하겠습니다."
            }
        ]
    }


def generate_invitation_pdf(
    design_data: Dict,
    qr_code_image_bytes: Optional[bytes] = None,
    paper_size: str = "A5",
    dpi: int = 300
) -> bytes:
    """
    청첩장 PDF 생성
    
    Args:
        design_data: 디자인 데이터 (문구, 레이아웃, 색상 등)
        qr_code_image_bytes: QR 코드 이미지 바이트
        paper_size: 종이 크기 (A5, A6)
        dpi: 해상도
    
    Returns:
        PDF 바이트
    """
    # 종이 크기 설정
    if paper_size == "A6":
        page_size = A6
        width, height = A6
    else:  # A5 기본
        page_size = A5
        width, height = A5
    
    # PDF 생성
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=page_size)
    
    # 배경색 (디자인 데이터에서 가져오기)
    bg_color = design_data.get("background_color", "#FFFFFF")
    if bg_color.startswith("#"):
        r = int(bg_color[1:3], 16) / 255.0
        g = int(bg_color[3:5], 16) / 255.0
        b = int(bg_color[5:7], 16) / 255.0
        c.setFillColorRGB(r, g, b)
        c.rect(0, 0, width, height, fill=1)
    
    # 텍스트 색상
    text_color = design_data.get("text_color", "#000000")
    if text_color.startswith("#"):
        r = int(text_color[1:3], 16) / 255.0
        g = int(text_color[3:5], 16) / 255.0
        b = int(text_color[5:7], 16) / 255.0
        c.setFillColorRGB(r, g, b)
    
    # 폰트 설정
    font_name = design_data.get("font_name", "Helvetica")
    font_size = design_data.get("font_size", 12)
    c.setFont(font_name, font_size)
    
    # 메인 문구
    main_text = design_data.get("main_text", "")
    if main_text:
        # 여러 줄 처리
        lines = main_text.split("\n")
        y_position = height - 100
        for line in lines:
            c.drawString(50, y_position, line)
            y_position -= 20
    
    # 신랑/신부 이름
    groom_name = design_data.get("groom_name", "")
    bride_name = design_data.get("bride_name", "")
    if groom_name and bride_name:
        c.drawString(50, y_position - 20, f"{groom_name} · {bride_name}")
    
    # 예식 정보
    wedding_info = design_data.get("wedding_info", "")
    if wedding_info:
        c.drawString(50, y_position - 60, wedding_info)
    
    # QR 코드 삽입
    if qr_code_image_bytes:
        try:
            qr_img = Image.open(BytesIO(qr_code_image_bytes))
            qr_width = 50 * mm
            qr_height = 50 * mm
            c.drawImage(ImageReader(qr_img), width - 80, 20, width=qr_width, height=qr_height)
        except Exception as e:
            print(f"⚠️ QR 코드 삽입 실패: {e}")
    
    # 이미지 삽입 (커플 사진 등)
    image_url = design_data.get("image_url")
    if image_url:
        # 실제 구현에서는 이미지 다운로드 필요
        pass
    
    c.save()
    buffer.seek(0)
    return buffer.read()


async def get_map_location(address: str) -> Dict:
    """
    카카오 Maps REST API를 사용하여 주소를 위도/경도로 변환
    
    Args:
        address: 주소 문자열
    
    Returns:
        {"lat": float, "lng": float, "formatted_address": str}
    """
    api_key = os.getenv("KAKAO_REST_API_KEY")
    if not api_key:
        print("⚠️ KAKAO_REST_API_KEY가 설정되지 않았습니다.")
        # 기본값 반환 (서울 시청)
        return {
            "lat": 37.5665,
            "lng": 126.9780,
            "formatted_address": address
        }
    
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }
    params = {
        "query": address
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("documents") and len(data["documents"]) > 0:
                doc = data["documents"][0]
                return {
                    "lat": float(doc["y"]),
                    "lng": float(doc["x"]),
                    "formatted_address": doc.get("address_name") or doc.get("road_address", {}).get("address_name") or address
                }
            else:
                # 주소 검색 실패 시 키워드 검색 시도
                keyword_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
                response = await client.get(keyword_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get("documents") and len(data["documents"]) > 0:
                    doc = data["documents"][0]
                    return {
                        "lat": float(doc["y"]),
                        "lng": float(doc["x"]),
                        "formatted_address": doc.get("address_name") or doc.get("place_name") or address
                    }
                
                print(f"⚠️ 카카오 Geocoding 실패: 검색 결과 없음")
                return {
                    "lat": 37.5665,
                    "lng": 126.9780,
                    "formatted_address": address
                }
    except Exception as e:
        print(f"⚠️ 카카오 Maps API 호출 실패: {e}")
        return {
            "lat": 37.5665,
            "lng": 126.9780,
            "formatted_address": address
        }


def generate_kakao_map_urls(lat: float, lng: float, place_name: str = "") -> Dict:
    """
    카카오맵 링크 URL 생성 (지도 보기, 길찾기)
    
    Args:
        lat: 위도
        lng: 경도
        place_name: 장소명
    
    Returns:
        {"map_url": str, "direction_url": str}
    """
    import urllib.parse
    
    encoded_name = urllib.parse.quote(place_name) if place_name else ""
    
    return {
        "map_url": f"https://map.kakao.com/link/map/{encoded_name},{lat},{lng}",
        "direction_url": f"https://map.kakao.com/link/to/{encoded_name},{lat},{lng}"
    }

