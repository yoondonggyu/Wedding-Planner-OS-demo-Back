"""
LLM 모델 설정 및 라벨링
"""
from typing import Dict, List, Optional

# 사용 가능한 모델 목록 및 라벨
AVAILABLE_MODELS: List[Dict[str, str]] = [
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "label": "일반 상담",
        "description": "빠르고 정확한 일반적인 상담에 적합",
        "category": "general",
        "provider": "google"
    },
    {
        "id": "gemma3:4b",
        "name": "Gemma 3 4B",
        "label": "일반 상담",
        "description": "균형잡힌 성능의 일반 상담 모델",
        "category": "general",
        "provider": "ollama"
    },
    {
        "id": "qwen3:0.6b",
        "name": "Qwen 3 0.6B",
        "label": "일정 상담",
        "description": "빠른 응답이 필요한 일정 관리 상담",
        "category": "schedule",
        "provider": "ollama"
    },
    {
        "id": "gemma3:latest",
        "name": "Gemma 3 (Latest)",
        "label": "일반 상담",
        "description": "최신 버전의 Gemma 모델",
        "category": "general",
        "provider": "ollama"
    }
]

# 카테고리별 기본 모델
DEFAULT_MODELS: Dict[str, str] = {
    "general": "gemini-2.5-flash",
    "emotional": "gemma3:4b",  # DeepSeek 제거로 Gemma 3 4B로 대체
    "schedule": "qwen3:0.6b"
}


def get_model_by_id(model_id: str) -> Optional[Dict[str, str]]:
    """모델 ID로 모델 정보 조회"""
    for model in AVAILABLE_MODELS:
        if model["id"] == model_id:
            return model
    return None


def get_models_by_category(category: str) -> List[Dict[str, str]]:
    """카테고리별 모델 목록 조회"""
    return [model for model in AVAILABLE_MODELS if model["category"] == category]


def get_all_models() -> List[Dict[str, str]]:
    """모든 모델 목록 반환"""
    return AVAILABLE_MODELS


def get_default_model_for_category(category: str) -> str:
    """카테고리별 기본 모델 반환"""
    return DEFAULT_MODELS.get(category, "gemini-2.5-flash")

