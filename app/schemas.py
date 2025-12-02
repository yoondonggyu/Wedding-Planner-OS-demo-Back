from pydantic import BaseModel, HttpUrl, Field
import enum
from typing import Any

# Enums
class Gender(str, enum.Enum):
    BRIDE = "BRIDE"
    GROOM = "GROOM"

# Auth
class LoginReq(BaseModel):
    email: str
    password: str

class LoginRes(BaseModel):
    message: str = "login_success"
    data: dict

class SignupReq(BaseModel):
    email: str
    password: str
    password_check: str
    nickname: str
    profile_image_url: HttpUrl | None = None
    gender: Gender | None = None  # 신부/신랑
    is_partner_vendor: bool = False  # 제휴 업체로 가입 신청
    invite_code: str | None = None  # 초대 링크의 커플 키 (자동 매칭용)

class CoupleConnectReq(BaseModel):
    partner_couple_key: str

# Users
class NicknamePatchReq(BaseModel):
    nickname: str
    profile_image_url: str | None = None

class PasswordUpdateReq(BaseModel):
    old_password: str
    password: str
    password_check: str

# Posts
class PostCreateReq(BaseModel):
    title: str = Field(..., max_length=2000)
    content: str
    image_url: HttpUrl | None = None
    board_type: str = "couple"

class PostUpdateReq(BaseModel):
    title: str | None = None
    content: str | None = None
    image_url: HttpUrl | None = None

# Comments
class CommentCreateReq(BaseModel):
    content: str

class CommentUpdateReq(BaseModel):
    content: str

# Chat
class ChatRequest(BaseModel):
    message: str
    user_id: int | None = None
    include_context: bool = True  # 개인 데이터 포함 여부

# Calendar
class CalendarEventCreateReq(BaseModel):
    title: str
    description: str | None = None
    start_date: str  # YYYY-MM-DD
    end_date: str | None = None
    start_time: str | None = None  # HH:MM
    end_time: str | None = None
    location: str | None = None
    category: str = "general"
    priority: str = "medium"  # high, medium, low
    assignee: str = "both"  # groom, bride, both
    reminder_days: list[int] = []
    wedding_d_day: str | None = None  # YYYY-MM-DD
    d_day_offset: int | None = None

class CalendarEventUpdateReq(BaseModel):
    title: str | None = None
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    location: str | None = None
    category: str | None = None
    priority: str | None = None
    assignee: str | None = None
    progress: int | None = None  # 0-100
    is_completed: bool | None = None
    reminder_days: list[int] | None = None

class TodoCreateReq(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    assignee: str = "both"
    due_date: str | None = None  # 할일의 경우 due_date, 일정의 경우 start_date로 사용
    start_date: str | None = None  # 일정용 (due_date와 동일하게 처리)
    start_time: str | None = None  # HH:MM
    end_date: str | None = None
    end_time: str | None = None
    location: str | None = None
    category: str = "todo"  # 'todo'면 할일, 그 외는 일정
    is_completed: bool = False
    event_id: int | None = None  # 기존 이벤트와의 연결 (사용 안 함)

class TodoUpdateReq(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    assignee: str | None = None
    progress: int | None = None
    due_date: str | None = None  # 할일의 경우 due_date, 일정의 경우 start_date로 사용
    start_date: str | None = None  # 일정용 (due_date와 동일하게 처리)
    start_time: str | None = None  # HH:MM
    end_date: str | None = None
    end_time: str | None = None
    location: str | None = None
    category: str | None = None
    is_completed: bool | None = None

class WeddingDateSetReq(BaseModel):
    wedding_date: str  # YYYY-MM-DD

class TimelineGenerateReq(BaseModel):
    wedding_date: str  # YYYY-MM-DD
    user_preferences: dict | None = None  # LLM 개인화를 위한 사용자 선호도

# Budget
class BudgetItemCreateReq(BaseModel):
    item_name: str
    category: str = "etc"  # hall, dress, studio, snap, honeymoon, etc.
    estimated_budget: float
    actual_expense: float = 0.0
    unit: str | None = None
    quantity: float = 1.0
    notes: str | None = None
    payer: str = "both"  # groom, bride, both
    payment_schedule: list[dict] = []

class BudgetItemUpdateReq(BaseModel):
    item_name: str | None = None
    category: str | None = None
    estimated_budget: float | None = None
    actual_expense: float | None = None
    unit: str | None = None
    quantity: float | None = None
    notes: str | None = None
    payer: str | None = None
    payment_schedule: list[dict] | None = None

class TotalBudgetSetReq(BaseModel):
    total_budget: float

class BudgetUploadReq(BaseModel):
    file_type: str = "excel"  # excel, csv, image (OCR)

# Voice Assistant
class VoiceProcessReq(BaseModel):
    audio_data: str | None = None  # base64 encoded audio
    text: str | None = None  # 직접 텍스트 입력 (STT 우회)
    user_id: int
    auto_organize: bool = True  # 자동 정리 파이프라인 실행 여부

# Vendor (업체 추천 시스템)
class WeddingProfileCreateReq(BaseModel):
    wedding_date: str  # YYYY-MM-DD
    guest_count_category: str  # SMALL, MEDIUM, LARGE
    total_budget: float  # KRW
    location_city: str
    location_district: str
    style_indoor: bool = True
    style_outdoor: bool = False
    outdoor_rain_plan_required: bool = False

class WeddingProfileUpdateReq(BaseModel):
    wedding_date: str | None = None
    guest_count_category: str | None = None
    total_budget: float | None = None
    location_city: str | None = None
    location_district: str | None = None
    style_indoor: bool | None = None
    style_outdoor: bool | None = None
    outdoor_rain_plan_required: bool | None = None

class VendorRecommendReq(BaseModel):
    wedding_profile_id: int
    vendor_type: str | None = None  # IPHONE_SNAP, MC, SINGER, STUDIO_PREWEDDING, VENUE_OUTDOOR
    min_price: float | None = None
    max_price: float | None = None
    location_city: str | None = None
    has_rain_plan: bool | None = None  # VENUE_OUTDOOR 한정
    sort: str = "score_desc"  # score_desc, price_asc, price_desc, review_desc

class FavoriteVendorCreateReq(BaseModel):
    wedding_profile_id: int
    vendor_id: int

# Vendor Message & Payment Reminder
class VendorThreadCreateReq(BaseModel):
    vendor_id: int
    title: str | None = None  # None이면 벤더 이름으로 자동 생성
    is_shared_with_partner: bool = False  # 파트너와 공유 여부

class VendorThreadUpdateReq(BaseModel):
    title: str | None = None
    is_active: bool | None = None

class VendorMessageCreateReq(BaseModel):
    thread_id: int
    content: str
    attachments: list[str] | None = None  # 파일 URL 리스트

class VendorContractCreateReq(BaseModel):
    thread_id: int
    contract_date: str | None = None  # YYYY-MM-DD
    total_amount: float | None = None
    deposit_amount: float | None = None
    interim_amount: float | None = None
    balance_amount: float | None = None
    service_date: str | None = None  # YYYY-MM-DD
    notes: str | None = None

class VendorContractUpdateReq(BaseModel):
    contract_date: str | None = None
    total_amount: float | None = None
    deposit_amount: float | None = None
    interim_amount: float | None = None
    balance_amount: float | None = None
    service_date: str | None = None
    notes: str | None = None
    is_active: bool | None = None

class VendorDocumentCreateReq(BaseModel):
    contract_id: int
    document_type: str  # quote, contract, invoice, receipt
    file_url: str
    file_name: str
    file_size: int | None = None
    metadata: dict | None = None

class VendorDocumentUpdateReq(BaseModel):
    status: str | None = None  # draft, pending, signed, rejected
    signed_at: str | None = None  # YYYY-MM-DD HH:MM:SS
    signed_by: str | None = None
    metadata: dict | None = None

class VendorPaymentScheduleCreateReq(BaseModel):
    contract_id: int
    payment_type: str  # deposit, interim, balance, additional
    amount: float
    due_date: str  # YYYY-MM-DD
    notes: str | None = None

class VendorPaymentScheduleUpdateReq(BaseModel):
    amount: float | None = None
    due_date: str | None = None
    paid_date: str | None = None  # YYYY-MM-DD
    payment_method: str | None = None
    status: str | None = None  # pending, paid, overdue, cancelled
    notes: str | None = None

class VendorCompareReq(BaseModel):
    vendor_ids: list[int]  # 비교할 벤더 ID 리스트 (최대 5개)

# Invitation (청첩장 디자인 서비스)
class InvitationDesignCreateReq(BaseModel):
    template_id: int | None = None
    design_data: dict  # 디자인 설정 (문구, 이미지, 레이아웃 등)
    qr_code_data: dict | None = None  # QR 코드 데이터 (디지털 초대장, 축의금, RSVP 링크)

class InvitationDesignUpdateReq(BaseModel):
    design_data: dict | None = None
    qr_code_data: dict | None = None
    status: str | None = None  # DRAFT, COMPLETED

class InvitationTextRecommendReq(BaseModel):
    groom_name: str
    bride_name: str
    wedding_date: str  # YYYY-MM-DD
    wedding_time: str | None = None  # HH:MM
    wedding_location: str | None = None
    style: str | None = None  # CLASSIC, MODERN, VINTAGE 등
    additional_info: str | None = None  # 추가 정보

class InvitationQRCodeGenerateReq(BaseModel):
    digital_invitation_url: str | None = None  # 디지털 초대장 URL
    payment_url: str | None = None  # 축의금 결제 URL
    rsvp_url: str | None = None  # RSVP URL

class InvitationPDFGenerateReq(BaseModel):
    design_id: int
    paper_size: str = "A5"  # A5, A6 등
    dpi: int = 300  # 인쇄 해상도

class InvitationOrderCreateReq(BaseModel):
    design_id: int
    quantity: int
    paper_type: str | None = None  # 일반, 고급, 에코 등
    paper_size: str = "A5"
    shipping_address: str
    shipping_phone: str
    shipping_name: str

class InvitationOrderUpdateReq(BaseModel):
    order_status: str | None = None  # PENDING, CONFIRMED, PRINTING, SHIPPED, DELIVERED
    vendor_id: int | None = None
    shipping_address: str | None = None
    shipping_phone: str | None = None
    shipping_name: str | None = None

# Digital Invitation (디지털 초대장 + 축의금 결제)
class DigitalInvitationCreateReq(BaseModel):
    invitation_design_id: int | None = None  # 연결된 청첩장 디자인 ID
    theme: str  # CLASSIC, MODERN, ROMANTIC 등
    groom_name: str
    bride_name: str
    wedding_date: str  # YYYY-MM-DD
    wedding_time: str | None = None  # HH:MM
    wedding_location: str
    wedding_location_detail: str | None = None
    map_url: str | None = None
    parking_info: str | None = None
    invitation_data: dict | None = None  # 테마별 추가 설정

class DigitalInvitationUpdateReq(BaseModel):
    theme: str | None = None
    groom_name: str | None = None
    bride_name: str | None = None
    wedding_date: str | None = None
    wedding_time: str | None = None
    wedding_location: str | None = None
    wedding_location_detail: str | None = None
    map_url: str | None = None
    parking_info: str | None = None
    invitation_data: dict | None = None
    is_active: bool | None = None

class PaymentCreateReq(BaseModel):
    invitation_id: int
    payer_name: str
    payer_phone: str | None = None
    payer_message: str | None = None
    amount: float
    payment_method: str  # BANK_TRANSFER, KAKAO_PAY, TOSS, CREDIT_CARD

class RSVPCreateReq(BaseModel):
    invitation_id: int
    guest_name: str
    guest_phone: str | None = None
    guest_email: str | None = None
    status: str  # ATTENDING, NOT_ATTENDING, MAYBE
    plus_one: bool = False
    plus_one_name: str | None = None
    dietary_restrictions: str | None = None
    special_requests: str | None = None

class RSVPUpdateReq(BaseModel):
    status: str | None = None
    plus_one: bool | None = None
    plus_one_name: str | None = None
    dietary_restrictions: str | None = None
    special_requests: str | None = None

class GuestMessageCreateReq(BaseModel):
    invitation_id: int
    guest_name: str
    guest_phone: str | None = None
    message: str | None = None
    image_url: str | None = None

# Base Response
class BaseResponse(BaseModel):
    message: str
    data: Any | None = None
    error_code: int | None = None
