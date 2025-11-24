from dataclasses import dataclass, field
from typing import Dict, Set

@dataclass
class User:
    id: int
    email: str
    password: str
    nickname: str
    profile_image_url: str

@dataclass
class Post:
    id: int
    user_id: int
    title: str
    content: str
    image_url: str | None
    board_type: str = "couple"  # couple, planner, private
    tags: list[str] = field(default_factory=list)
    summary: str | None = None
    sentiment_score: float | None = None
    sentiment_label: str | None = None
    like_count: int = 0
    view_count: int = 0

@dataclass
class Comment:
    id: int
    post_id: int
    user_id: int
    content: str

@dataclass
class CalendarEvent:
    """일정 구조화 엔진 - 표준화된 일정 데이터 모델"""
    id: int
    user_id: int
    title: str
    description: str | None = None
    start_date: str = ""  # ISO 8601 format: YYYY-MM-DD
    end_date: str | None = None
    start_time: str | None = None  # HH:MM format
    end_time: str | None = None
    location: str | None = None
    category: str = "general"  # general, payment, meeting, fitting, etc.
    priority: str = "medium"  # high, medium, low
    assignee: str = "both"  # groom, bride, both
    progress: int = 0  # 0-100
    reminder_days: list[int] = field(default_factory=list)  # D-Day 기준 알림일 (예: [7, 3, 1])
    is_completed: bool = False
    wedding_d_day: str | None = None  # 예식일 (D-Day 계산용)
    d_day_offset: int | None = None  # 예식일로부터 며칠 전인지
    metadata: dict = field(default_factory=dict)  # 추가 메타데이터

@dataclass
class Todo:
    """할일 리스트"""
    id: int
    event_id: int | None = None  # 연결된 일정 ID
    user_id: int = 0
    title: str = ""
    description: str | None = None
    priority: str = "medium"  # high, medium, low
    assignee: str = "both"  # groom, bride, both
    progress: int = 0  # 0-100
    due_date: str | None = None  # ISO 8601 format
    is_completed: bool = False
    created_at: str = ""  # ISO 8601 format

USERS: Dict[int, User] = {}
USERS_BY_EMAIL: Dict[str, int] = {}
USERS_BY_NICK: Dict[str, int] = {}

POSTS: Dict[int, Post] = {}
COMMENTS: Dict[int, Comment] = {}
LIKES: Dict[int, Set[int]] = {}  # post_id -> set(user_id)

@dataclass
class BudgetItem:
    """예산 항목 - 구조화된 JSON 스키마"""
    id: int
    user_id: int
    item_name: str  # 항목명
    category: str  # hall, dress, studio, snap, honeymoon, etc.
    estimated_budget: float  # 예상 예산
    actual_expense: float = 0.0  # 실제 지출
    unit: str | None = None  # 단위 (인원, 시간 등)
    quantity: float = 1.0  # 수량
    notes: str | None = None  # 비고
    payment_schedule: list[Dict] = field(default_factory=list)  # 계약금/중도금/잔금 일정
    payer: str = "both"  # groom, bride, both
    created_at: str = ""  # ISO 8601 format
    updated_at: str = ""  # ISO 8601 format
    metadata: dict = field(default_factory=dict)  # 추가 메타데이터 (OCR 원본, 구조화 정보 등)

CALENDAR_EVENTS: Dict[int, CalendarEvent] = {}
TODOS: Dict[int, Todo] = {}
USER_WEDDING_DATES: Dict[int, str] = {}  # user_id -> wedding_date (YYYY-MM-DD)
BUDGET_ITEMS: Dict[int, BudgetItem] = {}  # 예산 항목
USER_TOTAL_BUDGETS: Dict[int, float] = {}  # user_id -> 총 예산

COUNTERS = {"user": 1, "post": 1, "comment": 1, "event": 1, "todo": 1, "budget": 1}
