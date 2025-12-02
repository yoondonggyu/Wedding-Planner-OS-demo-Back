-- User 테이블에 role 컬럼 추가
ALTER TABLE users 
ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'USER' 
AFTER profile_image_url;

-- 기존 사용자들은 모두 USER 역할로 설정
UPDATE users SET role = 'USER' WHERE role IS NULL OR role = '';

-- 시스템 관리자 계정 설정 (필요시 이메일 변경)
-- UPDATE users SET role = 'SYSTEM_ADMIN' WHERE email = 'admin@example.com';

