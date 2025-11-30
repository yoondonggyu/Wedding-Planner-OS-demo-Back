-- Wedding Profiles 테이블
CREATE TABLE IF NOT EXISTS wedding_profiles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    wedding_date DATETIME NOT NULL,
    guest_count_category ENUM('SMALL', 'MEDIUM', 'LARGE') NOT NULL,
    total_budget DECIMAL(15, 2) NOT NULL,
    location_city VARCHAR(50) NOT NULL,
    location_district VARCHAR(50) NOT NULL,
    style_indoor BOOLEAN DEFAULT TRUE NOT NULL,
    style_outdoor BOOLEAN DEFAULT FALSE NOT NULL,
    outdoor_rain_plan_required BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Vendors 테이블
CREATE TABLE IF NOT EXISTS vendors (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    vendor_type ENUM('IPHONE_SNAP', 'MC', 'SINGER', 'STUDIO_PREWEDDING', 'VENUE_OUTDOOR') NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_location_city VARCHAR(50) NOT NULL,
    base_location_district VARCHAR(50) NOT NULL,
    service_area JSON,
    min_price DECIMAL(15, 2),
    max_price DECIMAL(15, 2),
    rating_avg DECIMAL(3, 2) DEFAULT 0.00 NOT NULL,
    review_count INTEGER DEFAULT 0 NOT NULL,
    portfolio_images JSON,
    portfolio_videos JSON,
    contact_link VARCHAR(500),
    contact_phone VARCHAR(20),
    tags JSON,
    iphone_snap_detail JSON,
    mc_detail JSON,
    singer_detail JSON,
    studio_detail JSON,
    venue_detail JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL
);

-- Favorite Vendors 테이블
CREATE TABLE IF NOT EXISTS favorite_vendors (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    wedding_profile_id BIGINT NOT NULL,
    vendor_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (wedding_profile_id) REFERENCES wedding_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE,
    UNIQUE KEY unique_favorite (user_id, wedding_profile_id, vendor_id)
);

