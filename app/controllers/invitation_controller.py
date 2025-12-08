"""
청첩장 디자인 서비스 컨트롤러
"""
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.db import (
    InvitationTemplate, InvitationDesign, InvitationOrder,
    InvitationTemplateStyle, InvitationDesignStatus
)
from app.core.couple_helpers import get_user_couple_id
from app.core.exceptions import not_found, bad_request
from app.core.error_codes import ErrorCode
from app.schemas import (
    InvitationDesignCreateReq, InvitationDesignUpdateReq,
    InvitationTextRecommendReq, InvitationQRCodeGenerateReq,
    InvitationPDFGenerateReq, InvitationOrderCreateReq, InvitationOrderUpdateReq
)
from app.services.invitation_service import (
    generate_qr_code, generate_qr_code_image, recommend_invitation_text,
    generate_invitation_pdf
)
import os
import uuid
from datetime import datetime


def get_templates(style: str = None, db: Session = None) -> Dict:
    """템플릿 목록 조회"""
    query = db.query(InvitationTemplate).filter(InvitationTemplate.is_active == True)
    
    if style:
        try:
            template_style = InvitationTemplateStyle(style)
            query = query.filter(InvitationTemplate.style == template_style)
        except ValueError:
            pass
    
    templates = query.order_by(InvitationTemplate.created_at.desc()).all()
    
    return {
        "message": "templates_retrieved",
        "data": {
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "style": t.style.value,
                    "preview_image_url": t.preview_image_url,
                    "template_data": t.template_data
                }
                for t in templates
            ]
        }
    }


def get_template(template_id: int, db: Session = None) -> Dict:
    """템플릿 상세 조회"""
    template = db.query(InvitationTemplate).filter(
        InvitationTemplate.id == template_id,
        InvitationTemplate.is_active == True
    ).first()
    
    if not template:
        raise not_found("template_not_found", ErrorCode.TEMPLATE_NOT_FOUND)
    
    return {
        "message": "template_retrieved",
        "data": {
            "id": template.id,
            "name": template.name,
            "style": template.style.value,
            "preview_image_url": template.preview_image_url,
            "template_data": template.template_data
        }
    }


def create_design(user_id: int | None, request: InvitationDesignCreateReq, db: Session) -> Dict:
    """디자인 생성 (인증 선택적)"""
    # user_id가 없으면 임시 사용자 ID 사용 (0 또는 기본값)
    # 실제로는 임시 사용자를 생성하거나 기본값을 사용해야 함
    if user_id is None:
        # 임시 사용자: user_id를 0으로 설정 (실제 사용자가 아닌 경우)
        # 또는 기본 사용자를 찾아서 사용
        from app.models.db import User
        # 기본 사용자 찾기 (예: id=1 또는 첫 번째 사용자)
        default_user = db.query(User).first()
        if default_user:
            user_id = default_user.id
        else:
            # 사용자가 없으면 에러 발생
            raise bad_request("user_not_found", ErrorCode.USER_NOT_FOUND)
    
    couple_id = get_user_couple_id(user_id, db)
    
    # 템플릿 검증
    template_id = request.template_id
    if template_id:
        template = db.query(InvitationTemplate).filter(
            InvitationTemplate.id == template_id,
            InvitationTemplate.is_active == True
        ).first()
        if not template:
            raise not_found("template_not_found", ErrorCode.TEMPLATE_NOT_FOUND)
    
    # QR 코드 생성
    qr_code_url = None
    qr_code_data = None
    if request.qr_code_data:
        qr_code_data = request.qr_code_data
        try:
            qr_code_url = generate_qr_code(qr_code_data)
        except Exception as e:
            print(f"⚠️ QR 코드 생성 실패: {e}")
            # QR 코드 생성 실패해도 디자인 생성은 계속 진행
            qr_code_url = None
    
    # 지도 정보 처리 (카카오 Maps API)
    # 주의: get_map_location은 async 함수이지만, create_design은 동기 함수입니다.
    # 지도 정보는 선택적이므로 실패해도 디자인 생성은 계속 진행합니다.
    map_lat = None
    map_lng = None
    map_image_url = None  # 카카오는 동적 지도 사용, 프론트엔드에서 처리
    # 지도 정보는 프론트엔드에서 처리하거나, 별도 API로 처리하도록 변경
    # 현재는 동기 함수에서 async 함수를 호출할 수 없으므로 스킵
    if request.map_address:
        print(f"ℹ️ 지도 정보는 프론트엔드에서 처리됩니다: {request.map_address}")
    
    design = InvitationDesign(
        user_id=user_id,
        couple_id=couple_id,
        template_id=template_id,
        design_data=request.design_data,
        qr_code_url=qr_code_url,
        qr_code_data=qr_code_data,
        status=InvitationDesignStatus.DRAFT,
        # 기본 정보 저장
        groom_father_name=request.groom_father_name,
        groom_mother_name=request.groom_mother_name,
        bride_father_name=request.bride_father_name,
        bride_mother_name=request.bride_mother_name,
        map_lat=map_lat,
        map_lng=map_lng,
        map_image_url=map_image_url
    )
    
    db.add(design)
    db.commit()
    db.refresh(design)
    
    return {
        "message": "design_created",
        "data": {
            "id": design.id,
            "template_id": design.template_id,
            "design_data": design.design_data,
            "qr_code_url": design.qr_code_url,
            "status": design.status.value,
            "map_image_url": design.map_image_url
        }
    }


def update_design(design_id: int, user_id: int | None, request: InvitationDesignUpdateReq, db: Session) -> Dict:
    """디자인 수정 (인증 선택적)"""
    # user_id가 있으면 해당 사용자의 디자인만 조회, 없으면 design_id로만 조회
    if user_id:
        design = db.query(InvitationDesign).filter(
            InvitationDesign.id == design_id,
            InvitationDesign.user_id == user_id
        ).first()
    else:
        design = db.query(InvitationDesign).filter(
            InvitationDesign.id == design_id
        ).first()
    
    if not design:
        raise not_found("design_not_found", ErrorCode.DESIGN_NOT_FOUND)
    
    if request.design_data:
        design.design_data = request.design_data
    
    if request.qr_code_data:
        design.qr_code_data = request.qr_code_data
        try:
            design.qr_code_url = generate_qr_code(request.qr_code_data)
        except Exception as e:
            print(f"⚠️ QR 코드 생성 실패: {e}")
            # QR 코드 생성 실패해도 디자인 수정은 계속 진행
            design.qr_code_url = None
    
    if request.status:
        try:
            design.status = InvitationDesignStatus(request.status)
        except ValueError:
            raise bad_request("invalid_status", ErrorCode.INVALID_STATUS)
    
    # 기본 정보 업데이트
    if request.groom_father_name is not None:
        design.groom_father_name = request.groom_father_name
    if request.groom_mother_name is not None:
        design.groom_mother_name = request.groom_mother_name
    if request.bride_father_name is not None:
        design.bride_father_name = request.bride_father_name
    if request.bride_mother_name is not None:
        design.bride_mother_name = request.bride_mother_name
    
    # 지도 정보는 프론트엔드에서 처리 (비동기 이슈로 백엔드에서 직접 처리하지 않음)
    if request.map_address:
        print(f"ℹ️ 지도 정보는 프론트엔드에서 처리됩니다: {request.map_address}")
    
    db.commit()
    db.refresh(design)
    
    return {
        "message": "design_updated",
        "data": {
            "id": design.id,
            "design_data": design.design_data,
            "qr_code_url": design.qr_code_url,
            "status": design.status.value,
            "map_image_url": design.map_image_url
        }
    }


def get_designs(user_id: int, db: Session) -> Dict:
    """디자인 목록 조회"""
    couple_id = get_user_couple_id(user_id, db)
    
    if couple_id:
        # 커플이 연결된 경우 파트너 디자인도 포함
        designs = db.query(InvitationDesign).filter(
            InvitationDesign.couple_id == couple_id
        ).order_by(InvitationDesign.created_at.desc()).all()
    else:
        designs = db.query(InvitationDesign).filter(
            InvitationDesign.user_id == user_id
        ).order_by(InvitationDesign.created_at.desc()).all()
    
    return {
        "message": "designs_retrieved",
        "data": {
            "designs": [
                {
                    "id": d.id,
                    "template_id": d.template_id,
                    "design_data": d.design_data,
                    "qr_code_url": d.qr_code_url,
                    "preview_image_url": d.preview_image_url,
                    "status": d.status.value,
                    "created_at": d.created_at.isoformat() if d.created_at else None
                }
                for d in designs
            ]
        }
    }


def get_design(design_id: int, user_id: int, db: Session) -> Dict:
    """디자인 상세 조회"""
    couple_id = get_user_couple_id(user_id, db)
    
    design = db.query(InvitationDesign).filter(InvitationDesign.id == design_id).first()
    
    if not design:
        raise not_found("design_not_found", ErrorCode.DESIGN_NOT_FOUND)
    
    # 권한 확인 (본인 또는 파트너)
    if design.user_id != user_id:
        if not couple_id or design.couple_id != couple_id:
            raise bad_request("unauthorized", ErrorCode.FORBIDDEN)
    
    return {
        "message": "design_retrieved",
        "data": {
            "id": design.id,
            "template_id": design.template_id,
            "design_data": design.design_data,
            "qr_code_url": design.qr_code_url,
            "qr_code_data": design.qr_code_data,
            "preview_image_url": design.preview_image_url,
            "pdf_url": design.pdf_url,
            "status": design.status.value,
            "created_at": design.created_at.isoformat() if design.created_at else None
        }
    }


async def recommend_text(request: InvitationTextRecommendReq) -> Dict:
    """AI 문구 추천"""
    recommended = await recommend_invitation_text(
        groom_name=request.groom_name,
        bride_name=request.bride_name,
        wedding_date=request.wedding_date,
        wedding_time=request.wedding_time,
        wedding_location=request.wedding_location,
        style=request.style,
        additional_info=request.additional_info
    )
    
    return {
        "message": "text_recommended",
        "data": recommended
    }


def generate_qr_code_endpoint(request: InvitationQRCodeGenerateReq) -> Dict:
    """QR 코드 생성"""
    qr_code_data = {
        "digital_invitation_url": request.digital_invitation_url,
        "payment_url": request.payment_url,
        "rsvp_url": request.rsvp_url
    }
    
    qr_code_url = generate_qr_code(qr_code_data)
    
    return {
        "message": "qr_code_generated",
        "data": {
            "qr_code_url": qr_code_url,
            "qr_code_data": qr_code_data
        }
    }


def generate_pdf(design_id: int, user_id: int, request: InvitationPDFGenerateReq, db: Session) -> bytes:
    """PDF 생성"""
    design = db.query(InvitationDesign).filter(
        InvitationDesign.id == design_id,
        InvitationDesign.user_id == user_id
    ).first()
    
    if not design:
        raise not_found("design_not_found", ErrorCode.DESIGN_NOT_FOUND)
    
    # QR 코드 이미지 바이트 생성
    qr_code_image_bytes = None
    if design.qr_code_data:
        qr_code_image_bytes = generate_qr_code_image(design.qr_code_data)
    
    # PDF 생성
    pdf_bytes = generate_invitation_pdf(
        design_data=design.design_data,
        qr_code_image_bytes=qr_code_image_bytes,
        paper_size=request.paper_size,
        dpi=request.dpi
    )
    
    # PDF URL 저장 (실제 구현에서는 파일 시스템 또는 S3에 저장)
    pdf_filename = f"invitation_{design_id}_{uuid.uuid4().hex[:8]}.pdf"
    pdf_url = f"https://cdn.example.com/invitations/{pdf_filename}"
    
    design.pdf_url = pdf_url
    db.commit()
    
    return pdf_bytes


def create_order(user_id: int, request: InvitationOrderCreateReq, db: Session) -> Dict:
    """주문 생성"""
    design = db.query(InvitationDesign).filter(
        InvitationDesign.id == request.design_id,
        InvitationDesign.user_id == user_id
    ).first()
    
    if not design:
        raise not_found("design_not_found", ErrorCode.DESIGN_NOT_FOUND)
    
    if design.status != InvitationDesignStatus.COMPLETED:
        raise bad_request("design_not_completed", ErrorCode.DESIGN_NOT_COMPLETED)
    
    order = InvitationOrder(
        design_id=request.design_id,
        user_id=user_id,
        quantity=request.quantity,
        paper_type=request.paper_type,
        paper_size=request.paper_size,
        shipping_address=request.shipping_address,
        shipping_phone=request.shipping_phone,
        shipping_name=request.shipping_name,
        order_status="PENDING"
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # 디자인 상태 업데이트
    design.status = InvitationDesignStatus.ORDERED
    db.commit()
    
    return {
        "message": "order_created",
        "data": {
            "id": order.id,
            "design_id": order.design_id,
            "quantity": order.quantity,
            "order_status": order.order_status,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }
    }


def get_orders(user_id: int, db: Session) -> Dict:
    """주문 목록 조회"""
    orders = db.query(InvitationOrder).filter(
        InvitationOrder.user_id == user_id
    ).order_by(InvitationOrder.created_at.desc()).all()
    
    return {
        "message": "orders_retrieved",
        "data": {
            "orders": [
                {
                    "id": o.id,
                    "design_id": o.design_id,
                    "quantity": o.quantity,
                    "paper_type": o.paper_type,
                    "paper_size": o.paper_size,
                    "order_status": o.order_status,
                    "created_at": o.created_at.isoformat() if o.created_at else None
                }
                for o in orders
            ]
        }
    }


async def generate_tones(request) -> Dict:
    """5가지 톤의 청첩장 문구 생성 (Gemini 2.5 Flash 사용)"""
    import httpx
    from app.services.model_client import get_model_api_base_url
    
    # 모델 서버의 톤 제안 API 호출
    base_url = get_model_api_base_url()
    url = f"{base_url}/invitation/tone-recommend"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json={
                    "groom_name": request.groom_name,
                    "bride_name": request.bride_name,
                    "groom_father_name": request.groom_father_name,
                    "groom_mother_name": request.groom_mother_name,
                    "bride_father_name": request.bride_father_name,
                    "bride_mother_name": request.bride_mother_name,
                    "wedding_date": request.wedding_date,
                    "wedding_time": request.wedding_time,
                    "wedding_location": request.wedding_location,
                    "additional_message": request.additional_message
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
    except Exception as e:
        print(f"⚠️ 톤 제안 API 호출 실패: {e}")
        # 기본 톤 반환
        return generate_default_tones(request)


def generate_default_tones(request) -> Dict:
    """기본 5가지 톤 생성"""
    base_info = f"{request.wedding_date}\n{request.wedding_time or ''}\n{request.wedding_location or ''}"
    
    return {
        "message": "tones_recommended",
        "data": {
            "tones": [
                {
                    "tone": "affectionate",
                    "description": "다정한",
                    "main_text": f"{request.groom_name}과 {request.bride_name}이\n서로를 향한 마음을 담아\n평생의 동반자가 되려 합니다.",
                    "parents_greeting": "두 사람의 시작을 축복해주세요.",
                    "wedding_info": base_info,
                    "closing": "소중한 분들을 모시고 싶어\n이렇게 초대합니다."
                },
                {
                    "tone": "cheerful",
                    "description": "밝고 명랑한",
                    "main_text": f"{request.groom_name} ♥ {request.bride_name}\n우리 결혼해요!",
                    "parents_greeting": "함께 축하해주세요!",
                    "wedding_info": base_info,
                    "closing": "행복한 출발을 함께해요!"
                },
                {
                    "tone": "polite",
                    "description": "예의 있는",
                    "main_text": f"{request.groom_name} · {request.bride_name}\n두 사람이 혼인하오니\n귀한 걸음 하시어\n자리를 빛내주시면 감사하겠습니다.",
                    "parents_greeting": "두 집안의 경사를 함께하시길 청합니다.",
                    "wedding_info": base_info,
                    "closing": "부디 참석하시어 축복해주시기 바랍니다."
                },
                {
                    "tone": "formal",
                    "description": "격식 있는",
                    "main_text": f"{request.groom_name} · {request.bride_name}\n두 사람의 결혼을 알리오니\n부디 참석하시어\n축복해 주시기 바랍니다.",
                    "parents_greeting": "삼가 청첩드립니다.",
                    "wedding_info": base_info,
                    "closing": "귀한 시간 내어 주시면\n더없는 영광이겠습니다."
                },
                {
                    "tone": "emotional",
                    "description": "감성적인",
                    "main_text": f"서로를 향한 마음이 모여\n하나의 사랑이 되었습니다.\n{request.groom_name}과 {request.bride_name}의 시작을\n함께 지켜봐 주세요.",
                    "parents_greeting": "두 사람이 만들어갈 아름다운 이야기에\n소중한 한 페이지가 되어주세요.",
                    "wedding_info": base_info,
                    "closing": "여러분의 축복이\n두 사람에게 큰 힘이 되겠습니다."
                }
            ]
        }
    }


async def generate_image(request, user_id: int | None, db: Session) -> Dict:
    """청첩장 이미지 생성 (인증 선택적)"""
    import httpx
    from datetime import date, datetime
    from app.services.model_client import get_model_api_base_url
    from app.models.db.gemini_usage import GeminiImageUsage
    from app.models.db import User
    
    # user_id가 없으면 기본 사용자 사용
    if user_id is None:
        default_user = db.query(User).first()
        if default_user:
            user_id = default_user.id
        else:
            raise bad_request("user_not_found", ErrorCode.USER_NOT_FOUND)
    
    # 디자인 확인 (user_id 조건 완화 - 디자인 ID만으로 조회)
    design = db.query(InvitationDesign).filter(
        InvitationDesign.id == request.design_id
    ).first()
    
    if not design:
        raise not_found("design_not_found", ErrorCode.DESIGN_NOT_FOUND)
    
    # 모델 선택: request.model이 있으면 사용, 없으면 model_type 기반으로 결정 (하위 호환성)
    if request.model:
        # 프론트엔드에서 선택한 모델 사용
        model = request.model
    elif request.model_type == "free":
        # 무료 모델: FLUX (이미지+텍스트 지원) 또는 SDXL (텍스트만)
        model = "flux" if request.base_image_url else "sdxl"
    else:
        # 유료 모델: Gemini Imagen (하루 5회 제한)
        model = "gemini"
    
    # Gemini 모델 (gemini)은 일일 사용 횟수 확인
    if model == "gemini":
        # 일일 사용 횟수 확인
        today = date.today()
        usage = db.query(GeminiImageUsage).filter(
            GeminiImageUsage.user_id == user_id,
            GeminiImageUsage.usage_date == today
        ).first()
        
        if usage:
            if usage.usage_count >= 5:
                raise bad_request("daily_limit_exceeded", ErrorCode.DAILY_LIMIT_EXCEEDED)
        else:
            # 오늘 첫 사용이면 레코드 생성
            usage = GeminiImageUsage(
                user_id=user_id,
                usage_date=today,
                usage_count=0
            )
            db.add(usage)
            db.flush()
    else:
        usage = None  # 무료 모델은 사용 횟수 추적 안 함
    
    # 모델 서버의 이미지 생성 API 호출
    base_url = get_model_api_base_url()
    url = f"{base_url}/image/generate"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                json={
                    "prompt": request.prompt,
                    "model": model,
                    "base_image_b64": request.base_image_url
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            # 디자인에 이미지 정보 저장
            if "data" in result and "image_b64" in result["data"]:
                design.generated_image_url = result["data"]["image_b64"]
                design.generated_image_model = model
                design.selected_tone = request.selected_tone
                design.selected_text = request.selected_text
                
                # Gemini 모델 사용 시 횟수 증가
                if model == "gemini" and usage:
                    usage.usage_count += 1
                    usage.last_used_at = datetime.now()
                
                db.commit()
            
            return result
            
    except Exception as e:
        print(f"⚠️ 이미지 생성 API 호출 실패: {e}")
        raise bad_request("image_generation_failed", ErrorCode.EXTERNAL_SERVICE_ERROR)


async def modify_image(request, user_id: int | None, db: Session) -> Dict:
    """청첩장 이미지 수정 (인증 선택적)"""
    import httpx
    from datetime import date, datetime
    from app.services.model_client import get_model_api_base_url
    from app.models.db.gemini_usage import GeminiImageUsage
    from app.models.db import User
    
    # user_id가 없으면 기본 사용자 사용
    if user_id is None:
        default_user = db.query(User).first()
        if default_user:
            user_id = default_user.id
        else:
            raise bad_request("user_not_found", ErrorCode.USER_NOT_FOUND)
    
    # 디자인 확인 (user_id 조건 완화 - 디자인 ID만으로 조회)
    design = db.query(InvitationDesign).filter(
        InvitationDesign.id == request.design_id
    ).first()
    
    if not design:
        raise not_found("design_not_found", ErrorCode.DESIGN_NOT_FOUND)
    
    # 모델 선택: request.model이 있으면 사용, 없으면 model_type 기반으로 결정 (하위 호환성)
    if request.model:
        # 프론트엔드에서 선택한 모델 사용
        model = request.model
    elif request.model_type == "free":
        # 무료 모델: FLUX (이미지 수정 지원)
        model = "flux"
    else:
        # 유료 모델: Gemini Imagen (하루 5회 제한)
        model = "gemini"
    
    # Gemini 모델 (gemini)은 일일 사용 횟수 확인
    if model == "gemini":
        # 일일 사용 횟수 확인
        today = date.today()
        usage = db.query(GeminiImageUsage).filter(
            GeminiImageUsage.user_id == user_id,
            GeminiImageUsage.usage_date == today
        ).first()
        
        if usage:
            if usage.usage_count >= 5:
                raise bad_request("daily_limit_exceeded", ErrorCode.DAILY_LIMIT_EXCEEDED)
        else:
            # 오늘 첫 사용이면 레코드 생성
            usage = GeminiImageUsage(
                user_id=user_id,
                usage_date=today,
                usage_count=0
            )
            db.add(usage)
            db.flush()
    else:
        usage = None  # 무료 모델은 사용 횟수 추적 안 함
    
    # 모델 서버의 이미지 수정 API 호출
    base_url = get_model_api_base_url()
    url = f"{base_url}/image/modify"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                json={
                    "base_image_b64": request.base_image_url,
                    "modification_prompt": request.modification_prompt,
                    "model": model
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            # 디자인에 수정된 이미지 정보 저장
            if "data" in result and "image_b64" in result["data"]:
                design.generated_image_url = result["data"]["image_b64"]
                design.generated_image_model = model
                
                # Gemini 모델 사용 시 횟수 증가
                if model == "gemini" and usage:
                    usage.usage_count += 1
                    usage.last_used_at = datetime.now()
                
                db.commit()
            
            return result
            
    except Exception as e:
        print(f"⚠️ 이미지 수정 API 호출 실패: {e}")
        raise bad_request("image_modification_failed", ErrorCode.EXTERNAL_SERVICE_ERROR)

