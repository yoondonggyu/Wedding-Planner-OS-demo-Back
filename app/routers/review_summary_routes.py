"""
리뷰 요약 API 라우터
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id_optional
from app.services.review_summary_service import summarize_board_reviews, summarize_vendor_reviews
from typing import Optional

router = APIRouter(tags=["Review Summary"])


@router.post("/posts/reviews/summarize")
async def summarize_board_reviews_endpoint(
    board_type: str = Query(..., description="게시판 타입 (예: venue_review)"),
    limit: int = Query(50, ge=1, le=100, description="요약할 최대 리뷰 개수"),
    vendor_type: Optional[str] = Query(None, description="업체 타입 필터 (선택적)"),
    user_id: Optional[int] = Depends(get_current_user_id_optional),
    db: Session = Depends(get_db)
):
    """
    게시판의 리뷰 게시글들을 감성 분석하고 요약
    
    Returns:
        {
            "summary": "요약 텍스트",
            "sentiment_analysis": {...},
            "review_count": int
        }
    """
    try:
        result = await summarize_board_reviews(
            board_type=board_type,
            limit=limit,
            vendor_type=vendor_type,
            db=db
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="리뷰 요약 중 오류가 발생했습니다.")
        
        return {"message": "review_summary_success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리뷰 요약 실패: {str(e)}")


@router.post("/vendors/{vendor_id}/reviews/summarize")
async def summarize_vendor_reviews_endpoint(
    vendor_id: int,
    user_id: Optional[int] = Depends(get_current_user_id_optional),
    db: Session = Depends(get_db)
):
    """
    특정 업체의 리뷰 게시글들을 감성 분석하고 요약
    
    Returns:
        {
            "summary": "요약 텍스트",
            "sentiment_analysis": {...},
            "review_count": int
        }
    """
    try:
        result = await summarize_vendor_reviews(
            vendor_id=vendor_id,
            db=db
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="업체를 찾을 수 없거나 리뷰가 없습니다.")
        
        return {"message": "vendor_review_summary_success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리뷰 요약 실패: {str(e)}")

