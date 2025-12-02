-- 데모 계정 생성 스크립트
-- 시스템 관리자와 웹 관리자 계정을 생성합니다.

-- 기존 계정이 있으면 삭제 (선택사항)
DELETE FROM users WHERE email IN ('systemadmin@demo.com', 'webadmin@demo.com');

-- 시스템 관리자 계정 생성
INSERT INTO users (email, password, nickname, role, created_at, updated_at)
VALUES (
    'systemadmin@demo.com',
    'systemadmin',
    '시스템 관리자',
    'SYSTEM_ADMIN',
    NOW(),
    NOW()
);

-- 웹 관리자 계정 생성
INSERT INTO users (email, password, nickname, role, created_at, updated_at)
VALUES (
    'webadmin@demo.com',
    'webadmin',
    '웹 관리자',
    'WEB_ADMIN',
    NOW(),
    NOW()
);

-- 생성된 계정 확인
SELECT id, email, nickname, role, created_at 
FROM users 
WHERE email IN ('systemadmin@demo.com', 'webadmin@demo.com');

