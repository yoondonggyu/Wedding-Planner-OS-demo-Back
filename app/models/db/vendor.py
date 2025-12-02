from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger, Boolean, JSON, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class GuestCountCategory(str, enum.Enum):
    SMALL = "SMALL"  # 50명 미만
    MEDIUM = "MEDIUM"  # 50~150명
    LARGE = "LARGE"  # 150명 이상


class VendorType(str, enum.Enum):
    IPHONE_SNAP = "IPHONE_SNAP"  # 아이폰 스냅 촬영자
    MC = "MC"  # 사회자
    SINGER = "SINGER"  # 축가(싱어/밴드/연주자)
    STUDIO_PREWEDDING = "STUDIO_PREWEDDING"  # 사전 웨딩 사진 스튜디오
    VENUE_OUTDOOR = "VENUE_OUTDOOR"  # 야외 결혼식 장소


class WeddingProfile(Base):
    __tablename__ = "wedding_profiles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    couple_id = Column(BigInteger, ForeignKey("couples.id", ondelete="SET NULL"), nullable=True)  # 커플 공유
    wedding_date = Column(DateTime, nullable=False)
    guest_count_category = Column(Enum(GuestCountCategory), nullable=False)
    total_budget = Column(Numeric(15, 2), nullable=False)  # KRW
    location_city = Column(String(50), nullable=False)
    location_district = Column(String(50), nullable=False)
    style_indoor = Column(Boolean, default=True, nullable=False)
    style_outdoor = Column(Boolean, default=False, nullable=False)
    outdoor_rain_plan_required = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="wedding_profiles")
    favorites = relationship("FavoriteVendor", backref="wedding_profile", cascade="all, delete-orphan")


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    vendor_type = Column(Enum(VendorType), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    base_location_city = Column(String(50), nullable=False)
    base_location_district = Column(String(50), nullable=False)
    service_area = Column(JSON, nullable=True)  # ["서울시", "경기도"] 형태
    min_price = Column(Numeric(15, 2), nullable=True)
    max_price = Column(Numeric(15, 2), nullable=True)
    rating_avg = Column(Numeric(3, 2), default=0.0, nullable=False)  # 0.00 ~ 5.00
    review_count = Column(Integer, default=0, nullable=False)
    portfolio_images = Column(JSON, nullable=True)  # URL 리스트
    portfolio_videos = Column(JSON, nullable=True)  # URL 리스트
    contact_link = Column(String(500), nullable=True)  # 카톡/인스타/홈페이지 URL
    contact_phone = Column(String(20), nullable=True)
    tags = Column(JSON, nullable=True)  # ["자연스러운", "감성", "풀데이"] 형태
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # 벤더 계정 연결
    
    # 타입별 상세 정보 (JSON으로 저장)
    # IPHONE_SNAP
    iphone_snap_detail = Column(JSON, nullable=True)  # coverage_range, deliverables, device_model, stabilizer_used
    
    # MC
    mc_detail = Column(JSON, nullable=True)  # mc_style_tags, experience_years, language_support
    
    # SINGER
    singer_detail = Column(JSON, nullable=True)  # genre_tags, member_count, sample_tracks
    
    # STUDIO_PREWEDDING
    studio_detail = Column(JSON, nullable=True)  # indoor_available, outdoor_available, package_list
    
    # VENUE_OUTDOOR
    venue_detail = Column(JSON, nullable=True)  # max_guest_count, has_indoor_backup, has_tent_option, rain_refund_policy, noise_restriction, parking_info
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    favorites = relationship("FavoriteVendor", backref="vendor", cascade="all, delete-orphan")
    user = relationship("User", backref="vendor_account")


class FavoriteVendor(Base):
    __tablename__ = "favorite_vendors"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    wedding_profile_id = Column(BigInteger, ForeignKey("wedding_profiles.id", ondelete="CASCADE"), nullable=False)
    vendor_id = Column(BigInteger, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="favorite_vendors")



