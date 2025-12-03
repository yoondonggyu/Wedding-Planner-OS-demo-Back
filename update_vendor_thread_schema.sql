-- VendorThread 테이블에 thread_type과 participant_user_ids 컬럼 추가
ALTER TABLE vendor_threads 
ADD COLUMN thread_type ENUM('one_on_one', 'group') DEFAULT 'one_on_one' NOT NULL AFTER vendor_id,
ADD COLUMN participant_user_ids JSON NULL AFTER thread_type;

-- VendorMessage 테이블에 is_visible_to_partner 컬럼 추가
ALTER TABLE vendor_messages 
ADD COLUMN is_visible_to_partner BOOLEAN DEFAULT TRUE NOT NULL AFTER is_read;
