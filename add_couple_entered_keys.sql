-- couples 테이블에 user1_entered_key, user2_entered_key 컬럼 추가
ALTER TABLE couples 
ADD COLUMN user1_entered_key VARCHAR(32) NULL AFTER user2_id,
ADD COLUMN user2_entered_key VARCHAR(32) NULL AFTER user1_entered_key;

