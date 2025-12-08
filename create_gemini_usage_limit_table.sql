-- Gemini 모델 사용 횟수 제한 테이블 생성
-- 하루 5회 제한을 위한 테이블

CREATE TABLE IF NOT EXISTS gemini_image_usage (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    usage_date DATE NOT NULL,  -- 사용 날짜 (YYYY-MM-DD)
    usage_count INT DEFAULT 0 NOT NULL,  -- 당일 사용 횟수
    last_used_at DATETIME NULL,  -- 마지막 사용 시간
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_user_date (user_id, usage_date),
    INDEX idx_user_id (user_id),
    INDEX idx_usage_date (usage_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

