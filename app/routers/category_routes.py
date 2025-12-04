"""
카테고리 관련 API 라우터
"""
from fastapi import APIRouter
from app.core.categories import CATEGORY_GROUPS, ALL_CATEGORIES, CATEGORY_DISPLAY_NAMES, get_category_display_name

router = APIRouter(tags=["categories"])


@router.get("/categories")
async def get_categories():
    """카테고리 목록 조회 API"""
    # 그룹별 카테고리 반환
    categories_by_group = {}
    for group_name, categories in CATEGORY_GROUPS.items():
        categories_by_group[group_name] = [
            {
                "code": cat,
                "display_name": get_category_display_name(cat)
            }
            for cat in categories
        ]
    
    # 전체 카테고리 목록 (플랫 리스트)
    all_categories_flat = [
        {
            "code": cat,
            "display_name": get_category_display_name(cat)
        }
        for cat in ALL_CATEGORIES
    ]
    
    return {
        "message": "get_categories_success",
        "data": {
            "by_group": categories_by_group,
            "all": all_categories_flat
        }
    }


