"""
채팅 메모리 Vector DB 서비스 - ChromaDB에 벡터로 저장
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.db import ChatMemory
from app.services.vector_db import (
    add_documents_to_collection,
    search_similar_documents,
    delete_documents_from_collection,
    get_collection_count,
    VECTOR_DB_AVAILABLE
)

# 채팅 메모리 컬렉션 이름
CHAT_MEMORY_COLLECTION = "chat_memories"


def vectorize_chat_memory(memory: ChatMemory) -> Optional[str]:
    """
    채팅 메모리를 벡터화하여 ChromaDB에 저장
    
    Args:
        memory: ChatMemory 모델 인스턴스
    
    Returns:
        ChromaDB에 저장된 벡터 ID (실패 시 None)
    """
    if not VECTOR_DB_AVAILABLE:
        print("⚠️ Vector DB를 사용할 수 없습니다.")
        return None
    
    try:
        # 저장할 텍스트 구성 (제목 + 내용 + 태그)
        text_parts = []
        if memory.title:
            text_parts.append(f"제목: {memory.title}")
        text_parts.append(memory.content)
        if memory.tags and len(memory.tags) > 0:
            text_parts.append(f"태그: {', '.join(memory.tags)}")
        if memory.context_summary:
            text_parts.append(f"컨텍스트: {memory.context_summary}")
        
        document_text = "\n".join(text_parts)
        
        # 메타데이터 구성
        metadata = {
            "memory_id": memory.id,
            "user_id": memory.user_id,
            "couple_id": memory.couple_id if memory.couple_id else None,
            "title": memory.title or "",
            "tags": ",".join(memory.tags) if memory.tags else "",
            "is_shared_with_partner": bool(memory.is_shared_with_partner),
            "created_at": memory.created_at.isoformat() if memory.created_at else None
        }
        
        # Vector DB에 추가
        vector_id = f"memory_{memory.id}"
        success = add_documents_to_collection(
            collection_name=CHAT_MEMORY_COLLECTION,
            documents=[document_text],
            metadatas=[metadata],
            ids=[vector_id]
        )
        
        if success:
            print(f"✅ 채팅 메모리 벡터화 완료 (memory_id={memory.id}, vector_id={vector_id})")
            return vector_id
        else:
            print(f"⚠️ 채팅 메모리 벡터화 실패 (memory_id={memory.id})")
            return None
            
    except Exception as e:
        print(f"⚠️ 채팅 메모리 벡터화 오류 (memory_id={memory.id}): {e}")
        return None


def search_chat_memories(
    query: str,
    user_id: int,
    k: int = 5,
    include_shared: bool = True,
    couple_id: Optional[int] = None
) -> List[Dict]:
    """
    채팅 메모리 벡터 검색
    
    Args:
        query: 검색 쿼리
        user_id: 사용자 ID
        k: 반환할 결과 개수
        include_shared: 파트너와 공유된 메모리 포함 여부
        couple_id: 커플 ID (파트너 메모리 검색용)
    
    Returns:
        검색 결과 리스트 [{"content": str, "metadata": dict, "score": float}, ...]
    """
    if not VECTOR_DB_AVAILABLE:
        return []
    
    try:
        # 필터 구성
        filter_dict = {}
        if include_shared and couple_id:
            # 본인 메모리 또는 파트너와 공유된 메모리
            # ChromaDB 필터는 단순하므로, 검색 후 필터링
            pass
        else:
            filter_dict["user_id"] = user_id
        
        # 벡터 검색 수행
        results = search_similar_documents(
            collection_name=CHAT_MEMORY_COLLECTION,
            query=query,
            k=k * 2,  # 필터링을 위해 더 많이 가져옴
            filter=filter_dict if filter_dict else None
        )
        
        # 권한 필터링 (본인 메모리 또는 공유된 메모리만)
        filtered_results = []
        for result in results:
            metadata = result.get("metadata", {})
            result_user_id = metadata.get("user_id")
            is_shared = metadata.get("is_shared_with_partner", False)
            result_couple_id = metadata.get("couple_id")
            
            # 본인 메모리이거나, 공유된 메모리인 경우만 포함
            if result_user_id == user_id:
                filtered_results.append(result)
            elif include_shared and is_shared and result_couple_id == couple_id:
                filtered_results.append(result)
        
        return filtered_results[:k]
        
    except Exception as e:
        print(f"⚠️ 채팅 메모리 검색 오류: {e}")
        return []


def delete_chat_memory_vector(vector_id: str) -> bool:
    """
    채팅 메모리 벡터 삭제
    
    Args:
        vector_id: ChromaDB 벡터 ID
    
    Returns:
        성공 여부
    """
    if not VECTOR_DB_AVAILABLE:
        return False
    
    try:
        return delete_documents_from_collection(
            collection_name=CHAT_MEMORY_COLLECTION,
            ids=[vector_id]
        )
    except Exception as e:
        print(f"⚠️ 채팅 메모리 벡터 삭제 오류: {e}")
        return False


def get_chat_memory_collection_stats() -> Dict:
    """
    채팅 메모리 Vector DB 통계 반환
    
    Returns:
        통계 정보
    """
    if not VECTOR_DB_AVAILABLE:
        return {"available": False, "count": 0}
    
    count = get_collection_count(CHAT_MEMORY_COLLECTION)
    return {
        "available": True,
        "count": count,
        "collection_name": CHAT_MEMORY_COLLECTION
    }


