-- VendorType ENUM 확장을 위한 SQL 스크립트
-- 기존 ENUM을 삭제하고 새로운 ENUM으로 교체

-- 1. vendors 테이블의 vendor_type 컬럼을 VARCHAR로 변경 (임시)
ALTER TABLE vendors MODIFY COLUMN vendor_type VARCHAR(50);

-- 2. 새로운 ENUM 타입 생성
ALTER TABLE vendors MODIFY COLUMN vendor_type ENUM(
    -- 사진/영상
    'IPHONE_SNAP',
    'STUDIO_PREWEDDING',
    'WEDDING_PHOTO',
    'VIDEO',
    -- 웨딩홀/장소
    'WEDDING_HALL',
    'VENUE_INDOOR',
    'VENUE_OUTDOOR',
    'VENUE_COMPLEX',
    -- 플래너/기획
    'PLANNER',
    'COORDINATOR',
    -- 패션/뷰티
    'DRESS_SHOP',
    'SUIT_SHOP',
    'MAKEUP_HAIR',
    'BEAUTY_SALON',
    -- 음식/케이터링
    'CATERERING',
    'BUFFET',
    'CAKE',
    'BAR',
    -- 꽃/장식
    'FLORIST',
    'DECORATION',
    -- 예물/주얼리
    'JEWELRY',
    -- 교통/운송
    'WEDDING_CAR',
    'LIMOUSINE',
    'TRANSPORTATION',
    -- 기타
    'MC',
    'SINGER',
    'BAND',
    'INVITATION',
    'GIFT',
    'HOTEL',
    'WEDDING_FAIR'
) NOT NULL;



