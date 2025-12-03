-- 채팅 메모리 테이블 생성
CREATE TABLE IF NOT EXISTS chat_memories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    couple_id BIGINT NULL,
    content TEXT NOT NULL,
    title VARCHAR(255) NULL,
    tags JSON NULL,
    original_message TEXT NULL,
    ai_response TEXT NULL,
    context_summary TEXT NULL,
    vector_db_id VARCHAR(255) NULL,
    vector_db_collection VARCHAR(100) NULL,
    is_shared_with_partner INT DEFAULT 0 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (couple_id) REFERENCES couples(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_couple_id (couple_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

