"""
모델 관련 라우터 - 사용 가능한 모델 목록 조회
"""
from fastapi import APIRouter
from app.services.model_config import get_all_models, get_models_by_category

router = APIRouter(tags=["Model"])


@router.get("/models")
async def get_models():
    """사용 가능한 모든 모델 목록 조회"""
    models = get_all_models()
    return {
        "message": "models_retrieved",
        "data": models
    }


@router.get("/models/category/{category}")
async def get_models_by_category_endpoint(category: str):
    """카테고리별 모델 목록 조회"""
    models = get_models_by_category(category)
    return {
        "message": "models_retrieved",
        "data": models
    }

