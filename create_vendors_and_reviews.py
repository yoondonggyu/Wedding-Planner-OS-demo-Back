"""
카테고리별 제휴 업체 생성 및 다양한 리뷰 게시글 생성 스크립트
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.db.vendor import Vendor, VendorType
from app.models.db.post import Post
from app.models.db.user import User
from decimal import Decimal
from datetime import datetime, timedelta
import random

# 카테고리별 업체 정보
VENDOR_DATA = [
    # 사진/영상
    {"type": VendorType.IPHONE_SNAP, "name": "아이폰 스냅 전문 스튜디오", "city": "서울시", "district": "강남구", "description": "자연스러운 아이폰 스냅 촬영 전문"},
    {"type": VendorType.STUDIO_PREWEDDING, "name": "로맨틱 프리웨딩 스튜디오", "city": "서울시", "district": "홍대", "description": "감성적인 프리웨딩 사진 촬영"},
    {"type": VendorType.WEDDING_PHOTO, "name": "웨딩 포토그래퍼", "city": "서울시", "district": "강남구", "description": "전문 웨딩 사진 촬영"},
    {"type": VendorType.VIDEO, "name": "웨딩 영상 제작소", "city": "서울시", "district": "송파구", "description": "감동적인 웨딩 영상 제작"},
    
    # 웨딩홀/장소
    {"type": VendorType.WEDDING_HALL, "name": "그랜드 웨딩홀", "city": "서울시", "district": "강남구", "description": "럭셔리 웨딩홀"},
    {"type": VendorType.VENUE_INDOOR, "name": "인도어 웨딩 센터", "city": "서울시", "district": "강서구", "description": "아늑한 실내 결혼식장"},
    {"type": VendorType.VENUE_OUTDOOR, "name": "가든 웨딩", "city": "경기도", "district": "고양시", "description": "자연 속 야외 결혼식장"},
    {"type": VendorType.VENUE_COMPLEX, "name": "컴플렉스 웨딩 센터", "city": "서울시", "district": "송파구", "description": "실내/야외 복합 결혼식장"},
    
    # 플래너/기획
    {"type": VendorType.PLANNER, "name": "드림 웨딩 플래너", "city": "서울시", "district": "강남구", "description": "전문 웨딩 플래닝 서비스"},
    {"type": VendorType.COORDINATOR, "name": "퍼펙트 코디네이터", "city": "서울시", "district": "서초구", "description": "완벽한 웨딩 코디네이션"},
    
    # 패션/뷰티
    {"type": VendorType.DRESS_SHOP, "name": "엘레강트 드레스샵", "city": "서울시", "district": "강남구", "description": "고급 웨딩드레스"},
    {"type": VendorType.SUIT_SHOP, "name": "클래식 턱시도샵", "city": "서울시", "district": "강남구", "description": "정장 전문 샵"},
    {"type": VendorType.MAKEUP_HAIR, "name": "뷰티 메이크업 살롱", "city": "서울시", "district": "강남구", "description": "전문 메이크업 및 헤어"},
    {"type": VendorType.BEAUTY_SALON, "name": "글로리 뷰티 살롱", "city": "서울시", "district": "서초구", "description": "프리미엄 뷰티 서비스"},
    
    
    # 꽃/장식
    {"type": VendorType.FLORIST, "name": "로맨틱 플로리스트", "city": "서울시", "district": "강남구", "description": "아름다운 웨딩 꽃 장식"},
    {"type": VendorType.DECORATION, "name": "아트 데코레이션", "city": "서울시", "district": "강남구", "description": "창의적인 웨딩 장식"},
    
    # 예물/주얼리
    {"type": VendorType.JEWELRY, "name": "다이아몬드 주얼리", "city": "서울시", "district": "강남구", "description": "고급 예물 및 주얼리"},
    
    # 교통/운송
    {"type": VendorType.WEDDING_CAR, "name": "럭셔리 웨딩카", "city": "서울시", "district": "강남구", "description": "고급 웨딩카 렌탈"},
    {"type": VendorType.LIMOUSINE, "name": "프리미엄 리무진", "city": "서울시", "district": "강남구", "description": "럭셔리 리무진 서비스"},
    {"type": VendorType.TRANSPORTATION, "name": "웨딩 교통 서비스", "city": "서울시", "district": "강남구", "description": "전문 웨딩 교통 서비스"},
    
    # 기타
    {"type": VendorType.MC, "name": "프로 사회자", "city": "서울시", "district": "강남구", "description": "전문 웨딩 사회자"},
    {"type": VendorType.SINGER, "name": "웨딩 싱어", "city": "서울시", "district": "강남구", "description": "감동적인 축가 서비스"},
    {"type": VendorType.BAND, "name": "웨딩 밴드", "city": "서울시", "district": "강남구", "description": "프로 웨딩 밴드"},
    {"type": VendorType.INVITATION, "name": "아트 인쇄소", "city": "서울시", "district": "강남구", "description": "예쁜 청첩장 인쇄"},
    {"type": VendorType.GIFT, "name": "기프트 스튜디오", "city": "서울시", "district": "강남구", "description": "특별한 웨딩 선물"},
    {"type": VendorType.HOTEL, "name": "웨딩 호텔", "city": "서울시", "district": "강남구", "description": "럭셔리 웨딩 호텔"},
    {"type": VendorType.WEDDING_FAIR, "name": "웨딩 박람회 센터", "city": "서울시", "district": "강남구", "description": "웨딩 박람회 주최"},
]

# 다양한 리뷰 텍스트 (감정별)
REVIEWS = {
    "positive": [
        "너무 좋았다! 완벽한 서비스였어요.",
        "정말 만족스러웠습니다. 추천합니다!",
        "이쁘고 깔끔하게 잘 챙겨주셨어요.",
        "처음 해본 경험이었는데 너무 좋았어요.",
        "완벽했습니다! 다시 이용하고 싶어요.",
        "서비스가 정말 훌륭했어요. 감사합니다!",
        "예상보다 훨씬 좋았습니다.",
        "친절하고 전문적인 서비스였어요.",
    ],
    "negative": [
        "별로다. 기대했던 것과 달랐어요.",
        "나쁘다. 서비스가 아쉬웠습니다.",
        "안이쁘다. 디자인이 마음에 안 들었어요.",
        "더럽다. 청결도가 아쉬웠어요.",
        "서비스가 별로였어요. 추천하지 않습니다.",
        "기대했던 것보다 못했어요.",
        "불만족스러웠습니다.",
    ],
    "neutral": [
        "그저그렇다. 특별한 건 없었어요.",
        "보통이에요. 나쁘지도 좋지도 않아요.",
        "평범했어요. 기대만큼은 아니었어요.",
        "무난했어요. 특별한 인상은 없었습니다.",
    ],
    "mixed": [
        "좋은 점도 있지만 아쉬운 점도 있어요.",
        "일부는 만족했지만 일부는 아쉬웠어요.",
        "처음 해본 경험이라 신기했지만 완벽하지는 않았어요.",
    ]
}

def create_vendors_and_reviews():
    """카테고리별 업체 생성 및 다양한 리뷰 게시글 생성"""
    db: Session = SessionLocal()
    
    try:
        # 테스트 사용자 찾기 (신랑테스트1)
        test_user = db.query(User).filter(User.nickname == "신랑테스트1").first()
        if not test_user:
            print("✗ 테스트 사용자를 찾을 수 없습니다.")
            return
        
        print(f"✓ 테스트 사용자 확인: {test_user.nickname} (ID: {test_user.id})")
        
        created_vendors = []
        
        # 1. 카테고리별 업체 생성
        for vendor_info in VENDOR_DATA:
            # 기존 업체 확인
            existing_vendor = db.query(Vendor).filter(
                Vendor.name == vendor_info["name"]
            ).first()
            
            if existing_vendor:
                print(f"✓ 업체 이미 존재: {vendor_info['name']}")
                created_vendors.append(existing_vendor)
            else:
                vendor = Vendor(
                    vendor_type=vendor_info["type"],
                    name=vendor_info["name"],
                    description=vendor_info["description"],
                    base_location_city=vendor_info["city"],
                    base_location_district=vendor_info["district"],
                    service_area=[vendor_info["city"]],
                    min_price=Decimal("100000"),
                    max_price=Decimal("5000000"),
                    rating_avg=Decimal("0.00"),
                    review_count=0,
                )
                db.add(vendor)
                db.commit()
                db.refresh(vendor)
                print(f"✓ 업체 생성: {vendor_info['name']} (ID: {vendor.id})")
                created_vendors.append(vendor)
        
        # 2. 각 업체별로 다양한 리뷰 게시글 생성
        board_types = ["planner", "couple"]  # venue_review는 ENUM에 없을 수 있음
        
        for vendor in created_vendors:
            # 각 업체당 3-5개의 리뷰 생성
            num_reviews = random.randint(3, 5)
            
            for i in range(num_reviews):
                # 감정 선택 (긍정, 부정, 중립, 혼합)
                sentiment_type = random.choice(["positive", "negative", "neutral", "mixed"])
                review_text = random.choice(REVIEWS[sentiment_type])
                
                # 게시판 타입 선택
                board_type = random.choice(board_types)
                
                # 제목 생성
                title = f"{vendor.name} 리뷰 {i+1}"
                
                # 게시글 생성
                post = Post(
                    user_id=test_user.id,
                    vendor_id=vendor.id,
                    title=title,
                    content=review_text,
                    board_type=board_type,
                    view_count=random.randint(0, 100),
                    created_at=datetime.now() - timedelta(days=random.randint(0, 30))
                )
                db.add(post)
            
            db.commit()
            print(f"✓ {vendor.name} 리뷰 {num_reviews}개 생성 완료")
        
        print(f"\n✓ 총 {len(created_vendors)}개 업체 생성 완료")
        print(f"✓ 총 리뷰 게시글 생성 완료")
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        print(f"✗ 오류 발생: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_vendors_and_reviews()

