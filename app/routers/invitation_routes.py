"""
청첩장 디자인 서비스 라우터
"""
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.schemas import (
    InvitationDesignCreateReq, InvitationDesignUpdateReq,
    InvitationTextRecommendReq, InvitationQRCodeGenerateReq,
    InvitationPDFGenerateReq, InvitationOrderCreateReq, InvitationOrderUpdateReq
)
from app.controllers import invitation_controller
from app.core.database import get_db
from app.core.security import get_current_user_id

router = APIRouter(tags=["invitation"])


# 템플릿
@router.get("/invitation-templates")
async def get_templates(
    style: str = Query(None, description="템플릿 스타일 필터 (CLASSIC, MODERN, VINTAGE 등)"),
    db: Session = Depends(get_db)
):
    """템플릿 목록 조회"""
    return invitation_controller.get_templates(style=style, db=db)


@router.get("/invitation-templates/{template_id}")
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """템플릿 상세 조회"""
    return invitation_controller.get_template(template_id, db=db)


# 디자인
@router.post("/invitation-designs")
async def create_design(
    request: InvitationDesignCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """디자인 생성"""
    return invitation_controller.create_design(user_id, request, db)


@router.get("/invitation-designs")
async def get_designs(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """디자인 목록 조회"""
    return invitation_controller.get_designs(user_id, db)


@router.get("/invitation-designs/{design_id}")
async def get_design(
    design_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """디자인 상세 조회"""
    return invitation_controller.get_design(design_id, user_id, db)


@router.put("/invitation-designs/{design_id}")
async def update_design(
    design_id: int,
    request: InvitationDesignUpdateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """디자인 수정"""
    return invitation_controller.update_design(design_id, user_id, request, db)


# AI 문구 추천
@router.post("/invitation-text-recommend")
async def recommend_text(
    request: InvitationTextRecommendReq
):
    """AI 문구 추천"""
    return await invitation_controller.recommend_text(request)


# QR 코드 생성
@router.post("/invitation-qr-code")
async def generate_qr_code(
    request: InvitationQRCodeGenerateReq
):
    """QR 코드 생성"""
    return invitation_controller.generate_qr_code_endpoint(request)


# PDF 생성
@router.post("/invitation-pdf")
async def generate_pdf(
    request: InvitationPDFGenerateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """PDF 생성 및 다운로드"""
    pdf_bytes = invitation_controller.generate_pdf(
        request.design_id, user_id, request, db
    )
    
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invitation_{request.design_id}.pdf"
        }
    )


# 주문
@router.post("/invitation-orders")
async def create_order(
    request: InvitationOrderCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """주문 생성"""
    return invitation_controller.create_order(user_id, request, db)


@router.get("/invitation-orders")
async def get_orders(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """주문 목록 조회"""
    return invitation_controller.get_orders(user_id, db)

