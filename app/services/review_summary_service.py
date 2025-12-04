"""
리뷰 요약 서비스 - 게시판 및 업체 리뷰 요약
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.db import Post, Vendor
from app.services.model_client import summarize_reviews


async def summarize_board_reviews(
    board_type: str,
    limit: int = 50,
    vendor_type: Optional[str] = None,
    db: Session = None
) -> Optional[Dict[str, Any]]:
    """
    게시판의 리뷰 게시글들을 요약
    
    Args:
        board_type: 게시판 타입 (예: "venue_review")
        limit: 요약할 최대 리뷰 개수
        db: 데이터베이스 세션
    
    Returns:
        리뷰 요약 결과
    """
    if not db:
        return None
    
    from sqlalchemy.orm import joinedload
    from app.models.db.vendor import VendorType
    
    # 해당 게시판 타입의 리뷰 게시글 조회
    query = db.query(Post).options(joinedload(Post.vendor)).filter(
        Post.board_type == board_type
    )
    
    # vendor_type 필터 적용
    if vendor_type:
        try:
            vendor_type_enum = VendorType(vendor_type)
            query = query.join(Vendor).filter(
                Vendor.vendor_type == vendor_type_enum
            )
        except ValueError:
            # 잘못된 vendor_type인 경우 필터링하지 않음
            pass
    
    posts = query.order_by(Post.created_at.desc()).limit(limit).all()
    
    if not posts:
        return {
            "summary": "리뷰가 없습니다.",
            "sentiment_analysis": {
                "positive_count": 0,
                "negative_count": 0,
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "overall_sentiment": "neutral"
            },
            "review_count": 0
        }
    
    # 게시글 내용을 리뷰 리스트로 변환
    reviews = [post.content for post in posts if post.content]
    
    # 모델 API 호출 - vendor_type이 있으면 그것을 사용, 없으면 board_type 사용
    result = await summarize_reviews(
        reviews=reviews,
        vendor_name=None,
        vendor_type=vendor_type if vendor_type else board_type
    )
    
    if result:
        result["review_count"] = len(reviews)
    
    return result


async def summarize_vendor_reviews(
    vendor_id: int,
    db: Session = None
) -> Optional[Dict[str, Any]]:
    """
    특정 업체의 리뷰 게시글들을 요약
    
    Args:
        vendor_id: 업체 ID
        db: 데이터베이스 세션
    
    Returns:
        리뷰 요약 결과
    """
    if not db:
        return None
    
    # 업체 정보 조회
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return None
    
    # 해당 업체와 관련된 리뷰 게시글 조회
    # 업체명이나 타입으로 검색 (게시글 제목/내용에 업체명이 포함된 경우)
    # 또는 별도의 vendor_reviews 테이블이 있다면 그것을 사용
    # 현재는 board_type이 "venue_review"인 게시글들을 가져옴
    posts = db.query(Post).filter(
        Post.board_type == "venue_review"
    ).order_by(Post.created_at.desc()).limit(50).all()
    
    # 업체명이 포함된 게시글만 필터링 (간단한 구현)
    vendor_name = vendor.name
    relevant_posts = [
        post for post in posts 
        if vendor_name in post.title or vendor_name in post.content
    ]
    
    if not relevant_posts:
        return {
            "summary": f"{vendor_name}에 대한 리뷰가 없습니다.",
            "sentiment_analysis": {
                "positive_count": 0,
                "negative_count": 0,
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "overall_sentiment": "neutral"
            },
            "review_count": 0
        }
    
    # 게시글 내용을 리뷰 리스트로 변환
    reviews = [post.content for post in relevant_posts if post.content]
    
    # 모델 API 호출
    result = await summarize_reviews(
        reviews=reviews,
        vendor_name=vendor.name,
        vendor_type=vendor.vendor_type.value if hasattr(vendor.vendor_type, 'value') else str(vendor.vendor_type)
    )
    
    if result:
        result["review_count"] = len(reviews)
    
    return result

