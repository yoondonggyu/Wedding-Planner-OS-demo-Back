-- 청첩장 디자인 테이블에 새 컬럼 추가
-- 생성일: 2025-12-07

-- 부모님 성함 컬럼 추가
ALTER TABLE invitation_designs 
ADD COLUMN IF NOT EXISTS groom_father_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS groom_mother_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS bride_father_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS bride_mother_name VARCHAR(100);

-- 지도 정보 컬럼 추가
ALTER TABLE invitation_designs
ADD COLUMN IF NOT EXISTS map_lat NUMERIC(10, 8),
ADD COLUMN IF NOT EXISTS map_lng NUMERIC(11, 8),
ADD COLUMN IF NOT EXISTS map_image_url TEXT;

-- 선택된 톤 및 문구 컬럼 추가
ALTER TABLE invitation_designs
ADD COLUMN IF NOT EXISTS selected_tone VARCHAR(50),
ADD COLUMN IF NOT EXISTS selected_text TEXT;

-- 생성된 이미지 컬럼 추가
ALTER TABLE invitation_designs
ADD COLUMN IF NOT EXISTS generated_image_url TEXT,
ADD COLUMN IF NOT EXISTS generated_image_model VARCHAR(50);

-- 마이그레이션 완료 확인
SELECT 
    'Migration completed: Added new columns to invitation_designs table' AS status,
    COUNT(*) AS total_designs
FROM invitation_designs;
