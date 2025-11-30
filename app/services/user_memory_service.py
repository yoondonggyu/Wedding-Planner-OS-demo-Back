"""
User Memory Layer 서비스 - Vector DB 기반 사용자 패턴 저장 및 검색
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.services.vector_db import (
    add_documents_to_collection,
    search_similar_documents,
    get_collection_count,
    VECTOR_DB_AVAILABLE
)

# 사용자별 메모리 컬렉션 이름 패턴
USER_MEMORY_COLLECTION_PATTERN = "user_memory_{user_id}"


def get_user_memory_collection_name(user_id: int) -> str:
    """사용자 메모리 컬렉션 이름 반환"""
    return USER_MEMORY_COLLECTION_PATTERN.format(user_id=user_id)


def save_user_preference(
    user_id: int,
    preference_type: str,
    content: str,
    metadata: Dict = None
) -> bool:
    """
    사용자 선호도/패턴 저장
    
    Args:
        user_id: 사용자 ID
        preference_type: 선호도 타입 (예: "budget_style", "schedule_preference", "wedding_concept", "conflict_point")
        content: 선호도 내용
        metadata: 추가 메타데이터
    
    Returns:
        성공 여부
    """
    if not VECTOR_DB_AVAILABLE:
        return False
    
    try:
        collection_name = get_user_memory_collection_name(user_id)
        
        # 메타데이터 구성
        full_metadata = {
            "user_id": user_id,
            "preference_type": preference_type,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        # 문서 ID 생성
        doc_id = f"pref_{user_id}_{preference_type}_{int(datetime.now().timestamp())}"
        
        return add_documents_to_collection(
            collection_name=collection_name,
            documents=[content],
            metadatas=[full_metadata],
            ids=[doc_id]
        )
    except Exception as e:
        print(f"⚠️ 사용자 선호도 저장 실패 (user_id={user_id}): {e}")
        return False


def save_user_conversation_memory(
    user_id: int,
    conversation_text: str,
    intent: str = None,
    extracted_info: Dict = None
) -> bool:
    """
    사용자 대화 내용을 메모리에 저장 (챗봇/음성 비서 대화)
    
    Args:
        user_id: 사용자 ID
        conversation_text: 대화 내용
        intent: 의도 (예: "budget_query", "schedule_planning")
        extracted_info: 추출된 정보 (예: {"budget_amount": 30000000, "wedding_date": "2025-11-11"})
    
    Returns:
        성공 여부
    """
    if not VECTOR_DB_AVAILABLE:
        return False
    
    try:
        collection_name = get_user_memory_collection_name(user_id)
        
        # 메타데이터 구성
        metadata = {
            "user_id": user_id,
            "memory_type": "conversation",
            "intent": intent or "general",
            "timestamp": datetime.now().isoformat(),
            **(extracted_info or {})
        }
        
        # 문서 ID 생성
        doc_id = f"conv_{user_id}_{int(datetime.now().timestamp())}"
        
        return add_documents_to_collection(
            collection_name=collection_name,
            documents=[conversation_text],
            metadatas=[metadata],
            ids=[doc_id]
        )
    except Exception as e:
        print(f"⚠️ 사용자 대화 메모리 저장 실패 (user_id={user_id}): {e}")
        return False


def search_user_memory(
    user_id: int,
    query: str,
    k: int = 5,
    preference_type: Optional[str] = None
) -> List[Dict]:
    """
    사용자 메모리 검색
    
    Args:
        user_id: 사용자 ID
        query: 검색 쿼리
        k: 반환할 결과 개수
        preference_type: 선호도 타입 필터
    
    Returns:
        검색 결과 리스트
    """
    if not VECTOR_DB_AVAILABLE:
        return []
    
    try:
        collection_name = get_user_memory_collection_name(user_id)
        
        # 필터 구성
        filter_dict = {"user_id": user_id}
        if preference_type:
            filter_dict["preference_type"] = preference_type
        
        return search_similar_documents(
            collection_name=collection_name,
            query=query,
            k=k,
            filter=filter_dict
        )
    except Exception as e:
        print(f"⚠️ 사용자 메모리 검색 실패 (user_id={user_id}): {e}")
        return []


def get_user_profile_summary(user_id: int) -> Dict:
    """
    사용자 프로필 요약 (예산 스타일, 선호 컨셉, 일정 패턴 등)
    
    Args:
        user_id: 사용자 ID
    
    Returns:
        프로필 요약 정보
    """
    if not VECTOR_DB_AVAILABLE:
        return {}
    
    try:
        # 각 선호도 타입별로 최근 메모리 검색
        profile = {
            "budget_style": [],
            "schedule_preference": [],
            "wedding_concept": [],
            "conflict_points": [],
            "recent_conversations": []
        }
        
        for pref_type in ["budget_style", "schedule_preference", "wedding_concept", "conflict_points"]:
            results = search_user_memory(
                user_id=user_id,
                query=f"{pref_type} preference",
                k=3,
                preference_type=pref_type
            )
            profile[pref_type] = [r["content"] for r in results]
        
        # 최근 대화 검색
        conv_results = search_user_memory(
            user_id=user_id,
            query="recent conversation",
            k=5
        )
        profile["recent_conversations"] = [r["content"][:200] for r in conv_results]
        
        return profile
    except Exception as e:
        print(f"⚠️ 사용자 프로필 요약 생성 실패 (user_id={user_id}): {e}")
        return {}


def get_user_memory_stats(user_id: int) -> Dict:
    """
    사용자 메모리 통계 반환
    
    Args:
        user_id: 사용자 ID
    
    Returns:
        통계 정보
    """
    if not VECTOR_DB_AVAILABLE:
        return {"available": False, "count": 0}
    
    try:
        collection_name = get_user_memory_collection_name(user_id)
        count = get_collection_count(collection_name)
        return {
            "available": True,
            "count": count,
            "collection_name": collection_name
        }
    except Exception as e:
        print(f"⚠️ 사용자 메모리 통계 조회 실패 (user_id={user_id}): {e}")
        return {"available": False, "count": 0}

