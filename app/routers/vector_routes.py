"""
Vector DB 관련 API 라우터
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services import post_vector_service, user_memory_service
from app.models.db import Post

router = APIRouter(tags=["vector"])


@router.get("/vector/posts/search")
async def search_posts_vector(
    query: str = Query(..., description="검색 쿼리"),
    k: int = Query(5, ge=1, le=20, description="반환할 결과 개수"),
    board_type: str = Query(None, description="게시판 타입 필터"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    게시글 벡터 검색 (Vector DB 기반)
    """
    try:
        results = post_vector_service.search_posts(
            query=query,
            k=k,
            board_type=board_type,
            user_id=None  # 전체 게시글 검색 (필요시 user_id로 필터링 가능)
        )
        
        # DB에서 실제 Post 객체 조회
        post_ids = [r["metadata"].get("post_id") for r in results if r["metadata"].get("post_id")]
        posts = db.query(Post).filter(Post.id.in_(post_ids)).all() if post_ids else []
        
        # 결과 매핑
        post_dict = {p.id: p for p in posts}
        formatted_results = []
        for result in results:
            post_id = result["metadata"].get("post_id")
            if post_id and post_id in post_dict:
                post = post_dict[post_id]
                formatted_results.append({
                    "post_id": post.id,
                    "title": post.title,
                    "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                    "board_type": post.board_type,
                    "similarity_score": result.get("score", 0),
                    "created_at": post.created_at.isoformat() if post.created_at else None
                })
        
        return {
            "message": "posts_searched",
            "data": {
                "query": query,
                "results": formatted_results,
                "total": len(formatted_results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")


@router.get("/vector/posts/stats")
async def get_posts_vector_stats():
    """
    게시판 Vector DB 통계
    """
    stats = post_vector_service.get_posts_collection_stats()
    return {
        "message": "vector_stats_retrieved",
        "data": stats
    }


@router.post("/vector/posts/batch-vectorize")
async def batch_vectorize_posts(
    limit: int = Query(100, ge=1, le=1000, description="처리할 최대 게시글 수"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    기존 게시글들을 일괄 벡터화 (관리자용)
    """
    try:
        count = post_vector_service.batch_vectorize_posts(db, limit)
        return {
            "message": "posts_vectorized",
            "data": {
                "vectorized_count": count,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"일괄 벡터화 실패: {str(e)}")


@router.get("/vector/user/memory")
async def get_user_memory(
    query: str = Query(..., description="검색 쿼리"),
    k: int = Query(5, ge=1, le=20, description="반환할 결과 개수"),
    preference_type: str = Query(None, description="선호도 타입 필터"),
    user_id: int = Depends(get_current_user_id)
):
    """
    사용자 메모리 검색
    """
    try:
        results = user_memory_service.search_user_memory(
            user_id=user_id,
            query=query,
            k=k,
            preference_type=preference_type
        )
        
        return {
            "message": "user_memory_retrieved",
            "data": {
                "query": query,
                "results": results,
                "total": len(results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메모리 검색 실패: {str(e)}")


@router.get("/vector/user/profile")
async def get_user_profile(
    user_id: int = Depends(get_current_user_id)
):
    """
    사용자 프로필 요약 (예산 스타일, 선호 컨셉, 일정 패턴 등)
    """
    try:
        profile = user_memory_service.get_user_profile_summary(user_id)
        stats = user_memory_service.get_user_memory_stats(user_id)
        
        return {
            "message": "user_profile_retrieved",
            "data": {
                "profile": profile,
                "stats": stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 조회 실패: {str(e)}")


@router.get("/vector/user/stats")
async def get_user_memory_stats(
    user_id: int = Depends(get_current_user_id)
):
    """
    사용자 메모리 통계
    """
    stats = user_memory_service.get_user_memory_stats(user_id)
    return {
        "message": "user_memory_stats_retrieved",
        "data": stats
    }

