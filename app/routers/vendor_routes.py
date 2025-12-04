from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.schemas import (
    WeddingProfileCreateReq, WeddingProfileUpdateReq,
    VendorRecommendReq, FavoriteVendorCreateReq
)
from app.controllers import vendor_controller
from app.core.database import get_db
from app.core.security import get_current_user_id

router = APIRouter(tags=["vendor"])

# 결혼식 프로필
@router.post("/wedding-profiles")
async def create_wedding_profile(
    request: WeddingProfileCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """결혼식 프로필 생성"""
    return vendor_controller.create_wedding_profile(user_id, request, db)

@router.get("/wedding-profiles")
async def get_wedding_profiles(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """결혼식 프로필 목록 조회"""
    return vendor_controller.get_wedding_profiles(user_id, db)

@router.get("/wedding-profiles/{profile_id}")
async def get_wedding_profile(
    profile_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """결혼식 프로필 단건 조회"""
    return vendor_controller.get_wedding_profile(profile_id, user_id, db)

@router.put("/wedding-profiles/{profile_id}")
async def update_wedding_profile(
    profile_id: int,
    request: WeddingProfileUpdateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """결혼식 프로필 수정"""
    return vendor_controller.update_wedding_profile(profile_id, user_id, request, db)

@router.delete("/wedding-profiles/{profile_id}")
async def delete_wedding_profile(
    profile_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """결혼식 프로필 삭제"""
    return vendor_controller.delete_wedding_profile(profile_id, user_id, db)

# 업체 추천
@router.get("/vendors/recommend")
async def recommend_vendors(
    wedding_profile_id: int = Query(...),
    vendor_type: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    location_city: str | None = Query(None),
    has_rain_plan: bool | None = Query(None),
    sort: str = Query("score_desc"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """업체 추천 (프로필 기반)"""
    request = VendorRecommendReq(
        wedding_profile_id=wedding_profile_id,
        vendor_type=vendor_type,
        min_price=min_price,
        max_price=max_price,
        location_city=location_city,
        has_rain_plan=has_rain_plan,
        sort=sort
    )
    return vendor_controller.recommend_vendors(user_id, request, db)

@router.get("/vendors")
async def get_vendors(
    vendor_type: str | None = Query(None, description="제휴 업체 타입 필터"),
    category: str | None = Query(None, description="카테고리 필터 (vendor_type보다 우선)"),
    db: Session = Depends(get_db)
):
    """제휴 업체 목록 조회 (카테고리별 또는 vendor_type별)"""
    return vendor_controller.get_vendors(vendor_type, category, db)

@router.get("/vendors/my-vendor")
async def get_my_vendor(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """제휴 업체 계정의 자신의 제휴 업체 정보 조회"""
    return vendor_controller.get_my_vendor(user_id, db)

@router.get("/vendors/{vendor_id}")
async def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    """업체 상세 조회"""
    return vendor_controller.get_vendor(vendor_id, db)

# 찜 기능
@router.post("/favorites")
async def create_favorite(
    request: FavoriteVendorCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """찜하기"""
    return vendor_controller.create_favorite(user_id, request, db)

@router.get("/favorites")
async def get_favorites(
    wedding_profile_id: int | None = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """찜 목록 조회"""
    return vendor_controller.get_favorites(user_id, wedding_profile_id, db)

@router.delete("/favorites/{favorite_id}")
async def delete_favorite(
    favorite_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """찜 삭제"""
    return vendor_controller.delete_favorite(favorite_id, user_id, db)



