"""
Vector DB 서비스 - Chroma 기반 벡터 저장 및 검색
"""
import os
from typing import List, Dict, Optional, Any
from pathlib import Path

# 선택적 import
try:
    from langchain_chroma import Chroma
    from langchain_ollama import OllamaEmbeddings
    from langchain_core.documents import Document
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False
    print("⚠️ langchain-chroma 또는 langchain-ollama가 설치되지 않았습니다. Vector DB 기능을 사용할 수 없습니다.")

# Vector DB 저장 경로
VECTOR_DB_DIR = Path("./vector_db")
VECTOR_DB_DIR.mkdir(exist_ok=True)

# 전역 변수
_embeddings = None
_vector_stores = {}  # collection_name -> Chroma instance


def get_embeddings():
    """Embedding 모델 인스턴스 반환 (싱글톤)"""
    global _embeddings
    
    if not VECTOR_DB_AVAILABLE:
        return None
    
    if _embeddings is None:
        try:
            # Ollama의 nomic-embed-text 모델 사용
            _embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
            print("✅ Embedding 모델 로드 완료: nomic-embed-text")
        except Exception as e:
            print(f"⚠️ Embedding 모델 로드 실패: {e}")
            return None
    
    return _embeddings


def get_vector_store(collection_name: str, persist_directory: str = None) -> Optional[Any]:
    """
    Vector Store 인스턴스 반환 (싱글톤)
    
    Args:
        collection_name: 컬렉션 이름 (예: "posts", "user_memory_{user_id}")
        persist_directory: 저장 디렉토리 (None이면 기본 경로 사용)
    """
    if not VECTOR_DB_AVAILABLE:
        return None
    
    if collection_name in _vector_stores:
        return _vector_stores[collection_name]
    
    embeddings = get_embeddings()
    if not embeddings:
        return None
    
    try:
        if persist_directory is None:
            persist_directory = str(VECTOR_DB_DIR / collection_name)
        
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        
        _vector_stores[collection_name] = vector_store
        print(f"✅ Vector Store 생성 완료: {collection_name}")
        return vector_store
    except Exception as e:
        print(f"⚠️ Vector Store 생성 실패: {e}")
        return None


def add_documents_to_collection(
    collection_name: str,
    documents: List[str],
    metadatas: List[Dict] = None,
    ids: List[str] = None
) -> bool:
    """
    문서를 Vector DB에 추가
    
    Args:
        collection_name: 컬렉션 이름
        documents: 문서 리스트 (텍스트)
        metadatas: 메타데이터 리스트 (각 문서의 추가 정보)
        ids: 문서 ID 리스트 (None이면 자동 생성)
    
    Returns:
        성공 여부
    """
    vector_store = get_vector_store(collection_name)
    if not vector_store:
        return False
    
    try:
        # Document 객체로 변환
        doc_objects = []
        for i, doc_text in enumerate(documents):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            doc_id = ids[i] if ids and i < len(ids) else None
            
            from langchain_core.documents import Document
            doc = Document(
                page_content=doc_text,
                metadata=metadata
            )
            doc_objects.append(doc)
        
        # Vector DB에 추가
        if ids:
            vector_store.add_documents(documents=doc_objects, ids=ids)
        else:
            vector_store.add_documents(documents=doc_objects)
        
        print(f"✅ {len(documents)}개 문서를 {collection_name}에 추가 완료")
        return True
    except Exception as e:
        print(f"⚠️ 문서 추가 실패: {e}")
        return False


def search_similar_documents(
    collection_name: str,
    query: str,
    k: int = 5,
    filter: Dict = None
) -> List[Dict]:
    """
    유사한 문서 검색
    
    Args:
        collection_name: 컬렉션 이름
        query: 검색 쿼리
        k: 반환할 문서 개수
        filter: 메타데이터 필터 (예: {"user_id": 1})
    
    Returns:
        검색 결과 리스트 [{"content": str, "metadata": dict, "score": float}, ...]
    """
    vector_store = get_vector_store(collection_name)
    if not vector_store:
        return []
    
    try:
        # 유사도 검색
        if filter:
            results = vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
        else:
            results = vector_store.similarity_search_with_score(
                query=query,
                k=k
            )
        
        # 결과 포맷팅
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
        
        return formatted_results
    except Exception as e:
        print(f"⚠️ 문서 검색 실패: {e}")
        return []


def delete_documents_from_collection(
    collection_name: str,
    ids: List[str]
) -> bool:
    """
    문서 삭제
    
    Args:
        collection_name: 컬렉션 이름
        ids: 삭제할 문서 ID 리스트
    
    Returns:
        성공 여부
    """
    vector_store = get_vector_store(collection_name)
    if not vector_store:
        return False
    
    try:
        vector_store.delete(ids=ids)
        print(f"✅ {len(ids)}개 문서를 {collection_name}에서 삭제 완료")
        return True
    except Exception as e:
        print(f"⚠️ 문서 삭제 실패: {e}")
        return False


def get_collection_count(collection_name: str) -> int:
    """
    컬렉션의 문서 개수 반환
    
    Args:
        collection_name: 컬렉션 이름
    
    Returns:
        문서 개수
    """
    vector_store = get_vector_store(collection_name)
    if not vector_store:
        return 0
    
    try:
        # Chroma의 _collection을 통해 개수 확인
        collection = vector_store._collection
        return collection.count()
    except Exception as e:
        print(f"⚠️ 문서 개수 조회 실패: {e}")
        return 0

