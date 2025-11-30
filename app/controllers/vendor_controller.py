"""
업체 추천 시스템 컨트롤러
"""
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.db import WeddingProfile, Vendor, FavoriteVendor, GuestCountCategory, VendorType
from app.schemas import (
    WeddingProfileCreateReq, WeddingProfileUpdateReq,
    VendorRecommendReq, FavoriteVendorCreateReq
)
from app.core.exceptions import not_found, unauthorized, bad_request


def create_wedding_profile(user_id: int, request: WeddingProfileCreateReq, db: Session) -> Dict:
    """결혼식 프로필 생성"""
    try:
        # 날짜 변환
        wedding_date = datetime.strptime(request.wedding_date, "%Y-%m-%d")
        
        # GuestCountCategory 검증
        try:
            guest_category = GuestCountCategory(request.guest_count_category)
        except ValueError:
            raise bad_request("invalid_guest_count_category")
        
        profile = WeddingProfile(
            user_id=user_id,
            wedding_date=wedding_date,
            guest_count_category=guest_category,
            total_budget=request.total_budget,
            location_city=request.location_city,
            location_district=request.location_district,
            style_indoor=request.style_indoor,
            style_outdoor=request.style_outdoor,
            outdoor_rain_plan_required=request.outdoor_rain_plan_required
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        return {
            "message": "wedding_profile_created",
            "data": {
                "id": profile.id,
                "wedding_date": profile.wedding_date.strftime("%Y-%m-%d"),
                "guest_count_category": profile.guest_count_category.value,
                "total_budget": float(profile.total_budget),
                "location_city": profile.location_city,
                "location_district": profile.location_district
            }
        }
    except Exception as e:
        db.rollback()
        print(f"프로필 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        raise


def get_wedding_profiles(user_id: int, db: Session) -> Dict:
    """결혼식 프로필 목록 조회"""
    profiles = db.query(WeddingProfile).filter(WeddingProfile.user_id == user_id).order_by(WeddingProfile.created_at.desc()).all()
    
    return {
        "message": "wedding_profiles_retrieved",
        "data": {
            "profiles": [
                {
                    "id": p.id,
                    "wedding_date": p.wedding_date.strftime("%Y-%m-%d"),
                    "guest_count_category": p.guest_count_category.value,
                    "total_budget": float(p.total_budget),
                    "location_city": p.location_city,
                    "location_district": p.location_district,
                    "style_indoor": p.style_indoor,
                    "style_outdoor": p.style_outdoor,
                    "outdoor_rain_plan_required": p.outdoor_rain_plan_required,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in profiles
            ]
        }
    }


def get_wedding_profile(profile_id: int, user_id: int, db: Session) -> Dict:
    """결혼식 프로필 단건 조회"""
    profile = db.query(WeddingProfile).filter(
        WeddingProfile.id == profile_id,
        WeddingProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise not_found("wedding_profile_not_found")
    
    return {
        "message": "wedding_profile_retrieved",
        "data": {
            "id": profile.id,
            "wedding_date": profile.wedding_date.strftime("%Y-%m-%d"),
            "guest_count_category": profile.guest_count_category.value,
            "total_budget": float(profile.total_budget),
            "location_city": profile.location_city,
            "location_district": profile.location_district,
            "style_indoor": profile.style_indoor,
            "style_outdoor": profile.style_outdoor,
            "outdoor_rain_plan_required": profile.outdoor_rain_plan_required,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
        }
    }


def update_wedding_profile(profile_id: int, user_id: int, request: WeddingProfileUpdateReq, db: Session) -> Dict:
    """결혼식 프로필 수정"""
    profile = db.query(WeddingProfile).filter(
        WeddingProfile.id == profile_id,
        WeddingProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise not_found("wedding_profile_not_found")
    
    if request.wedding_date:
        profile.wedding_date = datetime.strptime(request.wedding_date, "%Y-%m-%d")
    if request.guest_count_category:
        try:
            profile.guest_count_category = GuestCountCategory(request.guest_count_category)
        except ValueError:
            raise bad_request("invalid_guest_count_category")
    if request.total_budget is not None:
        profile.total_budget = request.total_budget
    if request.location_city:
        profile.location_city = request.location_city
    if request.location_district:
        profile.location_district = request.location_district
    if request.style_indoor is not None:
        profile.style_indoor = request.style_indoor
    if request.style_outdoor is not None:
        profile.style_outdoor = request.style_outdoor
    if request.outdoor_rain_plan_required is not None:
        profile.outdoor_rain_plan_required = request.outdoor_rain_plan_required
    
    db.commit()
    db.refresh(profile)
    
    return {
        "message": "wedding_profile_updated",
        "data": {
            "id": profile.id,
            "wedding_date": profile.wedding_date.strftime("%Y-%m-%d")
        }
    }


def delete_wedding_profile(profile_id: int, user_id: int, db: Session) -> Dict:
    """결혼식 프로필 삭제"""
    profile = db.query(WeddingProfile).filter(
        WeddingProfile.id == profile_id,
        WeddingProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise not_found("wedding_profile_not_found")
    
    db.delete(profile)
    db.commit()
    
    return {"message": "wedding_profile_deleted", "data": {"id": profile_id}}


def calculate_match_score(vendor: Vendor, profile: WeddingProfile) -> float:
    """업체와 프로필의 매칭 점수 계산 (0~100)"""
    score = 0.0
    
    # 1. guest_count_match (0~30점)
    # 간단 버전: 프로필의 guest_count_category와 업체의 max_guest_count 비교
    if vendor.vendor_type == VendorType.VENUE_OUTDOOR and vendor.venue_detail:
        max_guest = vendor.venue_detail.get("max_guest_count")
        if max_guest:
            if profile.guest_count_category == GuestCountCategory.SMALL and max_guest >= 50:
                score += 30
            elif profile.guest_count_category == GuestCountCategory.MEDIUM and 50 <= max_guest <= 150:
                score += 30
            elif profile.guest_count_category == GuestCountCategory.LARGE and max_guest >= 150:
                score += 30
    else:
        # 다른 타입은 기본 점수 부여
        score += 20
    
    # 2. budget_match (0~30점)
    if vendor.min_price and vendor.max_price:
        budget_range = float(vendor.max_price - vendor.min_price)
        budget_center = float(vendor.min_price + budget_range / 2)
        profile_budget = float(profile.total_budget)
        
        # 예산의 30% 범위 내면 만점
        if budget_center <= profile_budget * 1.3:
            if budget_center >= profile_budget * 0.7:
                score += 30  # 예산 범위 내
            else:
                score += 20  # 예산보다 낮음 (가능)
        else:
            score += 10  # 예산 초과 (감점)
    else:
        score += 15  # 가격 정보 없음
    
    # 3. region_match (0~20점)
    if vendor.service_area:
        if profile.location_city in vendor.service_area:
            score += 20
        elif profile.location_district in vendor.service_area:
            score += 15
        else:
            # 인접 지역 체크 (간단 버전)
            score += 5
    else:
        score += 10  # 서비스 지역 정보 없음
    
    # 4. style_match (0~20점)
    if profile.style_outdoor:
        if vendor.vendor_type == VendorType.VENUE_OUTDOOR:
            score += 15
            # 우천 플랜 체크
            if profile.outdoor_rain_plan_required:
                venue_detail = vendor.venue_detail or {}
                if venue_detail.get("has_indoor_backup") or venue_detail.get("has_tent_option"):
                    score += 5
                else:
                    score -= 10  # 우천 플랜 없으면 크게 감점
        elif vendor.vendor_type == VendorType.STUDIO_PREWEDDING:
            studio_detail = vendor.studio_detail or {}
            if studio_detail.get("outdoor_available"):
                score += 10
    
    if profile.style_indoor:
        if vendor.vendor_type == VendorType.VENUE_OUTDOOR:
            venue_detail = vendor.venue_detail or {}
            if venue_detail.get("has_indoor_backup"):
                score += 10
        elif vendor.vendor_type == VendorType.STUDIO_PREWEDDING:
            studio_detail = vendor.studio_detail or {}
            if studio_detail.get("indoor_available"):
                score += 10
    
    return min(100.0, max(0.0, score))


def recommend_vendors(user_id: int, request: VendorRecommendReq, db: Session) -> Dict:
    """업체 추천"""
    # 프로필 조회
    profile = db.query(WeddingProfile).filter(
        WeddingProfile.id == request.wedding_profile_id,
        WeddingProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise not_found("wedding_profile_not_found")
    
    # 업체 쿼리
    query = db.query(Vendor)
    
    # vendor_type 필터
    if request.vendor_type:
        try:
            vendor_type = VendorType(request.vendor_type)
            query = query.filter(Vendor.vendor_type == vendor_type)
        except ValueError:
            raise bad_request("invalid_vendor_type")
    
    # 가격 필터
    if request.min_price:
        query = query.filter(Vendor.max_price >= request.min_price)
    if request.max_price:
        query = query.filter(Vendor.min_price <= request.max_price)
    
    # 지역 필터
    if request.location_city:
        query = query.filter(
            (Vendor.base_location_city == request.location_city) |
            (Vendor.service_area.contains([request.location_city]))
        )
    
    # 우천 플랜 필터 (VENUE_OUTDOOR만)
    if request.has_rain_plan is not None and request.vendor_type == "VENUE_OUTDOOR":
        # JSON 필드에서 검색 (간단 버전)
        pass  # TODO: JSON 필드 검색 구현
    
    vendors = query.all()
    
    # 매칭 점수 계산
    vendor_scores = []
    for vendor in vendors:
        score = calculate_match_score(vendor, profile)
        vendor_scores.append({
            "vendor": {
                "id": vendor.id,
                "vendor_type": vendor.vendor_type.value,
                "name": vendor.name,
                "description": vendor.description,
                "base_location_city": vendor.base_location_city,
                "base_location_district": vendor.base_location_district,
                "service_area": vendor.service_area,
                "min_price": float(vendor.min_price) if vendor.min_price else None,
                "max_price": float(vendor.max_price) if vendor.max_price else None,
                "rating_avg": float(vendor.rating_avg) if vendor.rating_avg else 0.0,
                "review_count": vendor.review_count,
                "portfolio_images": vendor.portfolio_images,
                "portfolio_videos": vendor.portfolio_videos,
                "contact_link": vendor.contact_link,
                "contact_phone": vendor.contact_phone,
                "tags": vendor.tags,
                # 타입별 상세 정보
                "iphone_snap_detail": vendor.iphone_snap_detail,
                "mc_detail": vendor.mc_detail,
                "singer_detail": vendor.singer_detail,
                "studio_detail": vendor.studio_detail,
                "venue_detail": vendor.venue_detail
            },
            "match_score": round(score, 2)
        })
    
    # 정렬
    if request.sort == "price_asc":
        vendor_scores.sort(key=lambda x: x["vendor"]["min_price"] or float('inf'))
    elif request.sort == "price_desc":
        vendor_scores.sort(key=lambda x: x["vendor"]["max_price"] or 0.0, reverse=True)
    elif request.sort == "review_desc":
        vendor_scores.sort(key=lambda x: x["vendor"]["review_count"], reverse=True)
    else:  # score_desc (기본)
        vendor_scores.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "message": "vendors_recommended",
        "data": {
            "wedding_profile_id": profile.id,
            "vendors": vendor_scores
        }
    }


def get_vendor(vendor_id: int, db: Session) -> Dict:
    """업체 상세 조회"""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    
    if not vendor:
        raise not_found("vendor_not_found")
    
    return {
        "message": "vendor_retrieved",
        "data": {
            "id": vendor.id,
            "vendor_type": vendor.vendor_type.value,
            "name": vendor.name,
            "description": vendor.description,
            "base_location_city": vendor.base_location_city,
            "base_location_district": vendor.base_location_district,
            "service_area": vendor.service_area,
            "min_price": float(vendor.min_price) if vendor.min_price else None,
            "max_price": float(vendor.max_price) if vendor.max_price else None,
            "rating_avg": float(vendor.rating_avg) if vendor.rating_avg else 0.0,
            "review_count": vendor.review_count,
            "portfolio_images": vendor.portfolio_images,
            "portfolio_videos": vendor.portfolio_videos,
            "contact_link": vendor.contact_link,
            "contact_phone": vendor.contact_phone,
            "tags": vendor.tags,
            "iphone_snap_detail": vendor.iphone_snap_detail,
            "mc_detail": vendor.mc_detail,
            "singer_detail": vendor.singer_detail,
            "studio_detail": vendor.studio_detail,
            "venue_detail": vendor.venue_detail,
            "created_at": vendor.created_at.isoformat() if vendor.created_at else None
        }
    }


def create_favorite(user_id: int, request: FavoriteVendorCreateReq, db: Session) -> Dict:
    """찜하기"""
    # 프로필 소유권 확인
    profile = db.query(WeddingProfile).filter(
        WeddingProfile.id == request.wedding_profile_id,
        WeddingProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise not_found("wedding_profile_not_found")
    
    # 업체 존재 확인
    vendor = db.query(Vendor).filter(Vendor.id == request.vendor_id).first()
    if not vendor:
        raise not_found("vendor_not_found")
    
    # 중복 체크
    existing = db.query(FavoriteVendor).filter(
        FavoriteVendor.user_id == user_id,
        FavoriteVendor.wedding_profile_id == request.wedding_profile_id,
        FavoriteVendor.vendor_id == request.vendor_id
    ).first()
    
    if existing:
        raise bad_request("favorite_already_exists")
    
    favorite = FavoriteVendor(
        user_id=user_id,
        wedding_profile_id=request.wedding_profile_id,
        vendor_id=request.vendor_id
    )
    
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return {
        "message": "favorite_created",
        "data": {
            "id": favorite.id,
            "vendor_id": favorite.vendor_id
        }
    }


def get_favorites(user_id: int, wedding_profile_id: int | None, db: Session) -> Dict:
    """찜 목록 조회"""
    query = db.query(FavoriteVendor).filter(FavoriteVendor.user_id == user_id)
    
    if wedding_profile_id:
        query = query.filter(FavoriteVendor.wedding_profile_id == wedding_profile_id)
    
    favorites = query.order_by(FavoriteVendor.created_at.desc()).all()
    
    return {
        "message": "favorites_retrieved",
        "data": {
            "favorites": [
                {
                    "id": f.id,
                    "wedding_profile_id": f.wedding_profile_id,
                    "vendor_id": f.vendor_id,
                    "created_at": f.created_at.isoformat() if f.created_at else None,
                    "vendor": {
                        "id": f.vendor.id,
                        "name": f.vendor.name,
                        "vendor_type": f.vendor.vendor_type.value,
                        "min_price": float(f.vendor.min_price) if f.vendor.min_price else None,
                        "max_price": float(f.vendor.max_price) if f.vendor.max_price else None,
                        "rating_avg": float(f.vendor.rating_avg) if f.vendor.rating_avg else 0.0
                    }
                }
                for f in favorites
            ]
        }
    }


def delete_favorite(favorite_id: int, user_id: int, db: Session) -> Dict:
    """찜 삭제"""
    favorite = db.query(FavoriteVendor).filter(
        FavoriteVendor.id == favorite_id,
        FavoriteVendor.user_id == user_id
    ).first()
    
    if not favorite:
        raise not_found("favorite_not_found")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "favorite_deleted", "data": {"id": favorite_id}}

