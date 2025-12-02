"""
커플 연결 라우터
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import CoupleConnectReq
from app.controllers import couple_controller
from app.core.database import get_db
from app.core.security import get_current_user_id

router = APIRouter(tags=["couple"])


@router.get("/couple/my-key")
async def get_my_couple_key(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """자신의 커플 키 조회"""
    return couple_controller.get_my_couple_key(user_id, db)


@router.post("/couple/connect")
async def connect_couple(
    request: CoupleConnectReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """커플 연결 (상대방의 키 입력)"""
    return couple_controller.connect_couple(user_id, request, db)


@router.get("/couple/info")
async def get_couple_info(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """커플 정보 조회"""
    return couple_controller.get_couple_info(user_id, db)

