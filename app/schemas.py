from pydantic import BaseModel, HttpUrl, Field

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
    profile_image_url: HttpUrl

# Users
class NicknamePatchReq(BaseModel):
    nickname: str

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
    due_date: str | None = None
    event_id: int | None = None

class TodoUpdateReq(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    assignee: str | None = None
    progress: int | None = None
    due_date: str | None = None
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
