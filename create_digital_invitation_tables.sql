-- 디지털 초대장 + 축의금 결제 시스템 테이블 생성

-- 디지털 초대장 테이블
CREATE TABLE IF NOT EXISTS digital_invitations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    couple_id BIGINT NULL,
    invitation_design_id BIGINT NULL,  -- 연결된 청첩장 디자인 ID
    
    -- 초대장 정보
    theme ENUM('CLASSIC', 'MODERN', 'ROMANTIC', 'ELEGANT', 'MINIMAL', 'NATURE') NOT NULL,
    invitation_url VARCHAR(255) NOT NULL UNIQUE,  -- 고유 URL (예: abc123xyz)
    
    -- 예식 정보
    groom_name VARCHAR(100) NOT NULL,
    bride_name VARCHAR(100) NOT NULL,
    wedding_date DATETIME NOT NULL,
    wedding_time VARCHAR(50) NULL,  -- HH:MM 형식
    wedding_location VARCHAR(255) NOT NULL,  -- 예식 장소
    wedding_location_detail TEXT NULL,  -- 상세 주소
    map_url TEXT NULL,  -- 지도 링크
    parking_info TEXT NULL,  -- 주차 안내
    
    -- 초대장 설정 (JSON으로 테마별 추가 설정 저장)
    invitation_data JSON NOT NULL,  -- 테마별 추가 설정, title, greeting_message, main_image_url, gallery_image_urls, contact_info, bank_info 등
    
    -- 기능 설정
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- 통계
    view_count INT DEFAULT 0 NOT NULL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (couple_id) REFERENCES couples(id) ON DELETE SET NULL,
    FOREIGN KEY (invitation_design_id) REFERENCES invitation_designs(id) ON DELETE SET NULL,
    
    INDEX idx_user_id (user_id),
    INDEX idx_couple_id (couple_id),
    INDEX idx_invitation_design_id (invitation_design_id),
    INDEX idx_invitation_url (invitation_url),
    INDEX idx_is_active (is_active),
    INDEX idx_wedding_date (wedding_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 축의금 결제 테이블
CREATE TABLE IF NOT EXISTS payments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    invitation_id BIGINT NOT NULL,
    
    -- 결제자 정보
    payer_name VARCHAR(100) NOT NULL,
    payer_phone VARCHAR(50) NULL,
    payer_message TEXT NULL,  -- 축하 메시지
    
    -- 결제 정보
    amount DECIMAL(15, 2) NOT NULL,
    payment_method ENUM('BANK_TRANSFER', 'KAKAO_PAY', 'TOSS', 'CREDIT_CARD') NOT NULL,
    payment_status ENUM('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED') DEFAULT 'PENDING' NOT NULL,
    
    -- 결제 상세
    transaction_id VARCHAR(255) NULL,  -- 결제 거래 ID
    payment_data JSON NULL,  -- 결제 상세 데이터
    
    -- 감사 메시지
    thank_you_message_sent BOOLEAN DEFAULT FALSE NOT NULL,
    thank_you_sent_at DATETIME NULL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (invitation_id) REFERENCES digital_invitations(id) ON DELETE CASCADE,
    
    INDEX idx_invitation_id (invitation_id),
    INDEX idx_payment_status (payment_status),
    INDEX idx_payment_method (payment_method),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- RSVP (참석 여부) 테이블
CREATE TABLE IF NOT EXISTS rsvps (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    invitation_id BIGINT NOT NULL,
    
    -- 참석자 정보
    guest_name VARCHAR(100) NOT NULL,
    guest_phone VARCHAR(50) NULL,
    guest_email VARCHAR(255) NULL,
    
    -- RSVP 정보
    status ENUM('PENDING', 'ATTENDING', 'NOT_ATTENDING', 'MAYBE') DEFAULT 'PENDING' NOT NULL,
    plus_one BOOLEAN DEFAULT FALSE NOT NULL,  -- 동반자 여부
    plus_one_name VARCHAR(100) NULL,  -- 동반자 이름
    dietary_restrictions TEXT NULL,  -- 식이 제한 (알레르기 등)
    special_requests TEXT NULL,  -- 특별 요청사항
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (invitation_id) REFERENCES digital_invitations(id) ON DELETE CASCADE,
    
    INDEX idx_invitation_id (invitation_id),
    INDEX idx_status (status),
    INDEX idx_guest_phone (guest_phone),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 하객 메시지 및 사진 테이블
CREATE TABLE IF NOT EXISTS guest_messages (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    invitation_id BIGINT NOT NULL,
    
    -- 작성자 정보
    guest_name VARCHAR(100) NOT NULL,
    guest_phone VARCHAR(50) NULL,
    
    -- 메시지
    message TEXT NULL,
    image_url TEXT NULL,  -- 업로드된 사진 URL
    
    -- 승인 상태 (필요시)
    is_approved BOOLEAN DEFAULT TRUE NOT NULL,  -- 기본적으로 승인됨
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (invitation_id) REFERENCES digital_invitations(id) ON DELETE CASCADE,
    
    INDEX idx_invitation_id (invitation_id),
    INDEX idx_is_approved (is_approved),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

