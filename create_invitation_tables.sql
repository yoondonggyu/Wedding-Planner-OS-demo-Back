-- 청첩장 디자인 서비스 테이블 생성

-- 템플릿 테이블
CREATE TABLE IF NOT EXISTS invitation_templates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    style ENUM('CLASSIC', 'MODERN', 'VINTAGE', 'MINIMAL', 'LUXURY', 'NATURE', 'ROMANTIC') NOT NULL,
    preview_image_url TEXT,
    template_data JSON NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_style (style),
    INDEX idx_is_active (is_active)
);

-- 디자인 테이블
CREATE TABLE IF NOT EXISTS invitation_designs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    couple_id BIGINT NULL,
    template_id BIGINT NULL,
    design_data JSON NOT NULL,
    status ENUM('DRAFT', 'COMPLETED', 'ORDERED') DEFAULT 'DRAFT' NOT NULL,
    qr_code_url TEXT,
    qr_code_data JSON,
    pdf_url TEXT,
    preview_image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (couple_id) REFERENCES couples(id) ON DELETE SET NULL,
    FOREIGN KEY (template_id) REFERENCES invitation_templates(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_couple_id (couple_id),
    INDEX idx_template_id (template_id),
    INDEX idx_status (status)
);

-- 주문 테이블
CREATE TABLE IF NOT EXISTS invitation_orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    design_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    paper_type VARCHAR(50),
    paper_size VARCHAR(50),
    total_price DECIMAL(15, 2),
    order_status VARCHAR(50) DEFAULT 'PENDING' NOT NULL,
    vendor_id BIGINT NULL,
    shipping_address TEXT,
    shipping_phone VARCHAR(50),
    shipping_name VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (design_id) REFERENCES invitation_designs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL,
    INDEX idx_design_id (design_id),
    INDEX idx_user_id (user_id),
    INDEX idx_order_status (order_status)
);

