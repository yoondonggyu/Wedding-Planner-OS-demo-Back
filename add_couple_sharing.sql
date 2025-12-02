-- 커플 데이터 공유를 위한 컬럼 추가

-- 1. 자동 공유 (couple_id 추가)
-- 게시판
ALTER TABLE posts 
ADD COLUMN couple_id BIGINT NULL AFTER user_id,
ADD INDEX idx_couple_id (couple_id),
ADD FOREIGN KEY (couple_id) REFERENCES couples(id) ON DELETE SET NULL;

-- 캘린더
ALTER TABLE calendar_events 
ADD COLUMN couple_id BIGINT NULL AFTER user_id,
ADD INDEX idx_couple_id (couple_id),
ADD FOREIGN KEY (couple_id) REFERENCES couples(id) ON DELETE SET NULL;

-- 예산서
ALTER TABLE budget_items 
ADD COLUMN couple_id BIGINT NULL AFTER user_id,
ADD INDEX idx_couple_id (couple_id),
ADD FOREIGN KEY (couple_id) REFERENCES couples(id) ON DELETE SET NULL;

-- 업체 추천 (WeddingProfile)
ALTER TABLE wedding_profiles 
ADD COLUMN couple_id BIGINT NULL AFTER user_id,
ADD INDEX idx_couple_id (couple_id),
ADD FOREIGN KEY (couple_id) REFERENCES couples(id) ON DELETE SET NULL;

-- 2. 선택적 공유 (couple_id + is_shared_with_partner 추가)
-- 제휴 업체 메시지
ALTER TABLE vendor_threads 
ADD COLUMN couple_id BIGINT NULL AFTER user_id,
ADD COLUMN is_shared_with_partner BOOLEAN DEFAULT FALSE AFTER couple_id,
ADD INDEX idx_couple_id (couple_id),
ADD FOREIGN KEY (couple_id) REFERENCES couples(id) ON DELETE SET NULL;

-- AI 플래너 (ChatHistory)
ALTER TABLE chat_history 
ADD COLUMN couple_id BIGINT NULL AFTER user_id,
ADD COLUMN is_shared_with_partner BOOLEAN DEFAULT FALSE AFTER couple_id,
ADD INDEX idx_couple_id (couple_id),
ADD FOREIGN KEY (couple_id) REFERENCES couples(id) ON DELETE SET NULL;

