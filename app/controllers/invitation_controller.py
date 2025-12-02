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


def create_design(user_id: int, request: InvitationDesignCreateReq, db: Session) -> Dict:
    """디자인 생성"""
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
    
    design = InvitationDesign(
        user_id=user_id,
        couple_id=couple_id,
        template_id=template_id,
        design_data=request.design_data,
        qr_code_url=qr_code_url,
        qr_code_data=qr_code_data,
        status=InvitationDesignStatus.DRAFT
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
            "status": design.status.value
        }
    }


def update_design(design_id: int, user_id: int, request: InvitationDesignUpdateReq, db: Session) -> Dict:
    """디자인 수정"""
    design = db.query(InvitationDesign).filter(
        InvitationDesign.id == design_id,
        InvitationDesign.user_id == user_id
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
    
    db.commit()
    db.refresh(design)
    
    return {
        "message": "design_updated",
        "data": {
            "id": design.id,
            "design_data": design.design_data,
            "qr_code_url": design.qr_code_url,
            "status": design.status.value
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

