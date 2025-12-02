-- 벤더 메시지 & 결제 리마인더 관련 테이블 생성

-- 벤더 메시지 쓰레드 테이블
CREATE TABLE IF NOT EXISTS vendor_threads (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    vendor_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    last_message_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_vendor_id (vendor_id),
    INDEX idx_user_vendor (user_id, vendor_id),
    INDEX idx_last_message_at (last_message_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 벤더 메시지 테이블
CREATE TABLE IF NOT EXISTS vendor_messages (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    thread_id BIGINT NOT NULL,
    sender_type ENUM('user', 'vendor') NOT NULL,
    sender_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    attachments JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (thread_id) REFERENCES vendor_threads(id) ON DELETE CASCADE,
    INDEX idx_thread_id (thread_id),
    INDEX idx_thread_created (thread_id, created_at),
    INDEX idx_is_read (is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 벤더 계약 정보 테이블
CREATE TABLE IF NOT EXISTS vendor_contracts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    thread_id BIGINT NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    vendor_id BIGINT NOT NULL,
    contract_date DATE,
    total_amount DECIMAL(15, 2),
    deposit_amount DECIMAL(15, 2),
    interim_amount DECIMAL(15, 2),
    balance_amount DECIMAL(15, 2),
    service_date DATE,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (thread_id) REFERENCES vendor_threads(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_vendor_id (vendor_id),
    INDEX idx_thread_id (thread_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 벤더 문서 테이블 (견적서/계약서)
CREATE TABLE IF NOT EXISTS vendor_documents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    contract_id BIGINT NOT NULL,
    document_type ENUM('quote', 'contract', 'invoice', 'receipt') NOT NULL,
    version INT DEFAULT 1 NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    status ENUM('draft', 'pending', 'signed', 'rejected') DEFAULT 'draft' NOT NULL,
    signed_at DATETIME,
    signed_by VARCHAR(255),
    document_metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES vendor_contracts(id) ON DELETE CASCADE,
    INDEX idx_contract_id (contract_id),
    INDEX idx_document_type (document_type),
    INDEX idx_status (status),
    INDEX idx_contract_type_version (contract_id, document_type, version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 결제 일정 테이블
CREATE TABLE IF NOT EXISTS vendor_payment_schedules (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    contract_id BIGINT NOT NULL,
    payment_type ENUM('deposit', 'interim', 'balance', 'additional') NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    due_date DATE NOT NULL,
    paid_date DATE,
    payment_method VARCHAR(50),
    status ENUM('pending', 'paid', 'overdue', 'cancelled') DEFAULT 'pending' NOT NULL,
    reminder_sent BOOLEAN DEFAULT FALSE NOT NULL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES vendor_contracts(id) ON DELETE CASCADE,
    INDEX idx_contract_id (contract_id),
    INDEX idx_due_date (due_date),
    INDEX idx_status (status),
    INDEX idx_contract_due_date (contract_id, due_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

