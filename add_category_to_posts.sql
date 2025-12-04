-- 게시글에 카테고리 필드 추가 마이그레이션
-- 실행 방법: mysql -u username -p database_name < add_category_to_posts.sql

-- category 컬럼 추가 (NULL 허용, 기존 데이터는 NULL로 유지)
ALTER TABLE posts 
ADD COLUMN category VARCHAR(50) NULL 
AFTER board_type;

-- 인덱스 추가 (카테고리 필터링 성능 향상)
CREATE INDEX idx_posts_category ON posts(category);
CREATE INDEX idx_posts_board_type_category ON posts(board_type, category);

-- 기존 데이터 마이그레이션 (board_type을 기반으로 기본 카테고리 설정)
-- 예비부부 게시판 -> 웨딩홀 (기본값)
UPDATE posts 
SET category = '웨딩홀' 
WHERE board_type = 'couple' AND category IS NULL;

-- 플래너 리뷰 -> 웨딩_플래너
UPDATE posts 
SET category = '웨딩_플래너' 
WHERE board_type = 'planner' AND category IS NULL;

-- 웨딩홀 리뷰 -> 웨딩홀
UPDATE posts 
SET category = '웨딩홀' 
WHERE board_type = 'venue_review' AND category IS NULL;


