"""
VendorType을 카테고리 코드로 매핑하는 유틸리티
"""
from app.models.db.vendor import VendorType

# VendorType -> 카테고리 코드 매핑
VENDOR_TYPE_TO_CATEGORY = {
    # 사진/영상
    VendorType.IPHONE_SNAP: "아이폰_스냅",
    VendorType.STUDIO_PREWEDDING: "웨딩_스튜디오",
    VendorType.WEDDING_PHOTO: "웨딩_사진",
    VendorType.VIDEO: "웨딩_영상",
    
    # 웨딩홀/장소
    VendorType.WEDDING_HALL: "웨딩홀",
    VendorType.VENUE_INDOOR: "실내_식장",
    VendorType.VENUE_OUTDOOR: "야외_식장",
    VendorType.VENUE_COMPLEX: "복합_식장",
    
    # 플래너/기획
    VendorType.PLANNER: "웨딩_플래너",
    VendorType.COORDINATOR: "웨딩_코디네이터",
    
    # 패션/뷰티
    VendorType.DRESS_SHOP: "드레스샵",
    VendorType.SUIT_SHOP: "턱시도샵",
    VendorType.MAKEUP_HAIR: "메이크업_헤어",
    VendorType.BEAUTY_SALON: "뷰티_살롱",
    VendorType.HANBOK: "한복",
    
    # 음식/케이터링
    VendorType.CATERING: "케이터링",
    VendorType.BUFFET: "뷔페_식당",
    VendorType.CAKE: "케이크_디저트",
    VendorType.BAR: "바_음료",
    
    # 꽃/장식
    VendorType.FLORIST: "꽃_플로리스트",
    VendorType.DECORATION: "장식_데코",
    VendorType.BOUQUET: "부케_꽃다발",
    
    # 예물/주얼리
    VendorType.JEWELRY: "예물_주얼리",
    VendorType.RING: "예물_반지",
    
    # 교통/운송
    VendorType.WEDDING_CAR: "웨딩카",
    VendorType.LIMOUSINE: "리무진",
    VendorType.TRANSPORTATION: "교통_운송",
    
    # 기타
    VendorType.MC: "사회자",
    VendorType.SINGER: "축가",
    VendorType.BAND: "밴드_연주자",
    VendorType.MUSIC: "축가_연주",
    VendorType.INVITATION: "청첩장_인쇄",
    VendorType.GIFT: "웨딩선물_답례품",
    VendorType.HOTEL: "호텔_숙박",
    VendorType.WEDDING_FAIR: "웨딩박람회",
    VendorType.HONEYMOON: "신혼여행",
}

# 카테고리 코드 -> VendorType 역매핑 (여러 VendorType이 같은 카테고리를 가질 수 있음)
CATEGORY_TO_VENDOR_TYPES: dict[str, list[VendorType]] = {}
for vendor_type, category in VENDOR_TYPE_TO_CATEGORY.items():
    if category not in CATEGORY_TO_VENDOR_TYPES:
        CATEGORY_TO_VENDOR_TYPES[category] = []
    CATEGORY_TO_VENDOR_TYPES[category].append(vendor_type)

def get_category_from_vendor_type(vendor_type: str | VendorType) -> str | None:
    """VendorType을 카테고리 코드로 변환"""
    if isinstance(vendor_type, str):
        try:
            vendor_type = VendorType(vendor_type)
        except ValueError:
            return None
    
    return VENDOR_TYPE_TO_CATEGORY.get(vendor_type)

def get_vendor_types_from_category(category: str) -> list[VendorType]:
    """카테고리 코드를 VendorType 리스트로 변환"""
    return CATEGORY_TO_VENDOR_TYPES.get(category, [])
