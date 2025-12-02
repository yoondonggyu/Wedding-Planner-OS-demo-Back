"""
청첩장 디자인 서비스 - QR 코드 생성, PDF 생성, AI 문구 추천
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
    AI 기반 청첩장 문구 추천
    
    Args:
        groom_name: 신랑 이름
        bride_name: 신부 이름
        wedding_date: 예식일 (YYYY-MM-DD)
        wedding_time: 예식 시간 (HH:MM)
        wedding_location: 예식 장소
        style: 스타일 (CLASSIC, MODERN, VINTAGE 등)
        additional_info: 추가 정보
    
    Returns:
        추천 문구 딕셔너리
    """
    style_map = {
        "CLASSIC": "전통적이고 우아한",
        "MODERN": "현대적이고 세련된",
        "VINTAGE": "빈티지하고 로맨틱한",
        "MINIMAL": "미니멀하고 깔끔한",
        "LUXURY": "고급스럽고 화려한",
        "NATURE": "자연스럽고 따뜻한",
        "ROMANTIC": "로맨틱하고 감성적인"
    }
    
    style_desc = style_map.get(style, "따뜻하고 정중한") if style else "따뜻하고 정중한"
    
    prompt = f"""다음 정보를 바탕으로 {style_desc} 톤의 청첩장 문구를 작성해주세요.

신랑: {groom_name}
신부: {bride_name}
예식일: {wedding_date}"""
    
    if wedding_time:
        prompt += f"\n예식 시간: {wedding_time}"
    if wedding_location:
        prompt += f"\n예식 장소: {wedding_location}"
    if additional_info:
        prompt += f"\n추가 정보: {additional_info}"
    
    prompt += """

다음 형식의 JSON으로 응답해주세요:
{
  "main_text": "주요 문구 (예: 두 사람이 하나가 되어...)",
  "groom_parents": "신랑 부모님 성함",
  "bride_parents": "신부 부모님 성함",
  "wedding_info": "예식 정보 (날짜, 시간, 장소)",
  "reception_info": "식장 정보 (있으면)",
  "closing_text": "마무리 문구 (예: 바쁘시겠지만 참석해 주시면 감사하겠습니다)"
}

JSON만 응답해주세요."""
    
    try:
        response = await chat_with_model(prompt, model="gemma3:4b")
        
        # JSON 추출
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            recommended_text = json.loads(json_match.group())
            return recommended_text
    except Exception as e:
        print(f"⚠️ AI 문구 추천 실패: {e}")
    
    # 기본 문구 반환
    return {
        "main_text": f"{groom_name} · {bride_name} 두 사람이 하나가 되어\n새로운 인생을 시작합니다.",
        "groom_parents": "신랑 부모님",
        "bride_parents": "신부 부모님",
        "wedding_info": f"{wedding_date} {wedding_time or ''}",
        "reception_info": wedding_location or "",
        "closing_text": "바쁘시겠지만 참석해 주시면 감사하겠습니다."
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

