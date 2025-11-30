"""
캘린더 서비스 - LLM 기반 개인화 일정 추천 + D-Day 기반 타임라인 생성
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.models.memory import (
    CALENDAR_EVENTS, TODOS, USER_WEDDING_DATES, COUNTERS,
    CalendarEvent, Todo
)
from app.services.model_client import chat_with_model, get_model_api_base_url
import httpx
import json


def calculate_d_day(wedding_date: str, current_date: str | None = None) -> int:
    """D-Day 계산 (예식일까지 남은 일수)"""
    if current_date is None:
        current_date = datetime.now().strftime("%Y-%m-%d")
    
    wedding = datetime.strptime(wedding_date, "%Y-%m-%d")
    current = datetime.strptime(current_date, "%Y-%m-%d")
    delta = (wedding - current).days
    return delta


def get_default_timeline_templates() -> List[Dict]:
    """기본 웨딩 타임라인 템플릿 (D-Day 기반)"""
    return [
        # 12개월 전
        {"title": "예산 계획 수립", "d_day_offset": 365, "category": "planning", "priority": "high"},
        {"title": "웨딩홀 예약 시작", "d_day_offset": 330, "category": "booking", "priority": "high"},
        
        # 6개월 전
        {"title": "웨딩홀 계약", "d_day_offset": 180, "category": "payment", "priority": "high"},
        {"title": "스튜디오 예약", "d_day_offset": 150, "category": "booking", "priority": "high"},
        {"title": "드레스샵 예약", "d_day_offset": 120, "category": "booking", "priority": "medium"},
        
        # 3개월 전
        {"title": "청첩장 제작 주문", "d_day_offset": 90, "category": "preparation", "priority": "high"},
        {"title": "스드메 피팅 1차", "d_day_offset": 60, "category": "fitting", "priority": "medium"},
        {"title": "웨딩홀 중도금 납부", "d_day_offset": 45, "category": "payment", "priority": "high"},
        
        # 1개월 전
        {"title": "청첩장 발송", "d_day_offset": 30, "category": "preparation", "priority": "high"},
        {"title": "스드메 피팅 2차", "d_day_offset": 21, "category": "fitting", "priority": "medium"},
        {"title": "웨딩홀 잔금 납부", "d_day_offset": 14, "category": "payment", "priority": "high"},
        {"title": "최종 리허설", "d_day_offset": 7, "category": "meeting", "priority": "high"},
        {"title": "예식 당일", "d_day_offset": 0, "category": "wedding", "priority": "high"},
    ]


async def generate_personalized_timeline(
    wedding_date: str,
    user_id: int,
    user_preferences: Dict | None = None
) -> List[Dict]:
    """LLM 기반 개인화 일정 추천"""
    # 기본 타임라인 가져오기
    base_timeline = get_default_timeline_templates()
    
    # 사용자 선호도가 있으면 LLM으로 개인화
    if user_preferences:
        try:
            prompt = f"""웨딩 준비 일정을 개인화해주세요.

[기본 타임라인]
{json.dumps(base_timeline, ensure_ascii=False, indent=2)}

[사용자 선호도]
{json.dumps(user_preferences, ensure_ascii=False, indent=2)}

[예식일]
{wedding_date}

위 정보를 바탕으로 사용자에게 맞는 개인화된 웨딩 준비 일정을 생성해주세요.
각 일정은 다음 형식으로 제공해주세요:
- title: 일정 제목
- d_day_offset: 예식일로부터 며칠 전인지
- category: 일정 카테고리
- priority: 우선순위 (high/medium/low)
- description: 상세 설명 (선택)

JSON 배열 형식으로 응답해주세요."""

            response = await chat_with_model(prompt, model="gemma3:4b")
            
            if response:
                # LLM 응답에서 JSON 추출 시도
                try:
                    # JSON 부분만 추출
                    import re
                    json_match = re.search(r'\[.*\]', response, re.DOTALL)
                    if json_match:
                        personalized = json.loads(json_match.group())
                        if isinstance(personalized, list):
                            return personalized
                except:
                    pass
        except Exception as e:
            print(f"⚠️ LLM 개인화 실패: {e}")
            pass
    
    return base_timeline


async def create_timeline_from_wedding_date(
    user_id: int,
    wedding_date: str,
    user_preferences: Dict | None = None
) -> List[Dict]:
    """예식일 기반 타임라인 자동 생성 - 딕셔너리 리스트 반환 (DB 저장은 controller에서 처리)"""
    # 개인화된 타임라인 생성
    timeline_items = await generate_personalized_timeline(
        wedding_date, user_id, user_preferences
    )
    
    # 일정 딕셔너리 생성
    events = []
    wedding_dt = datetime.strptime(wedding_date, "%Y-%m-%d")
    
    for item in timeline_items:
        d_day_offset = item.get("d_day_offset", 0)
        event_date = wedding_dt - timedelta(days=d_day_offset)
        
        event_dict = {
            "user_id": user_id,
            "title": item.get("title", "일정"),
            "description": item.get("description"),
            "start_date": event_date.strftime("%Y-%m-%d"),
            "end_date": None,
            "start_time": None,
            "end_time": None,
            "location": None,
            "category": item.get("category", "general"),
            "priority": item.get("priority", "medium"),
            "assignee": item.get("assignee", "both"),
            "wedding_d_day": wedding_date,
            "d_day_offset": d_day_offset,
            "reminder_days": item.get("reminder_days", [7, 3, 1] if d_day_offset > 0 else []),
            "is_auto_generated": True,  # 타임라인 자동 생성된 일정
            "metadata": None  # event_metadata로 변환됨
        }
        
        events.append(event_dict)
    
    return events


def get_user_events(user_id: int, start_date: str | None = None, end_date: str | None = None) -> List[CalendarEvent]:
    """사용자 일정 조회"""
    events = [e for e in CALENDAR_EVENTS.values() if e.user_id == user_id]
    
    if start_date:
        events = [e for e in events if e.start_date >= start_date]
    if end_date:
        events = [e for e in events if e.start_date <= end_date]
    
    # 날짜순 정렬
    events.sort(key=lambda x: x.start_date)
    return events


def get_user_todos(user_id: int, completed: bool | None = None) -> List[Todo]:
    """사용자 할일 조회"""
    todos = [t for t in TODOS.values() if t.user_id == user_id]
    
    if completed is not None:
        todos = [t for t in todos if t.is_completed == completed]
    
    # 우선순위 및 날짜순 정렬
    priority_order = {"high": 0, "medium": 1, "low": 2}
    todos.sort(key=lambda x: (
        priority_order.get(x.priority, 1),
        x.due_date or "9999-12-31"
    ))
    
    return todos


def get_upcoming_events(user_id: int, days: int = 7) -> List[CalendarEvent]:
    """다가오는 일정 조회"""
    today = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    events = get_user_events(user_id, start_date=today, end_date=end_date)
    return [e for e in events if not e.is_completed]


def get_week_summary(user_id: int) -> Dict:
    """이번 주 요약 생성 (챗봇 연동용)"""
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    events = get_user_events(
        user_id,
        start_date=week_start.strftime("%Y-%m-%d"),
        end_date=week_end.strftime("%Y-%m-%d")
    )
    
    todos = get_user_todos(user_id, completed=False)
    
    high_priority = [e for e in events if e.priority == "high" and not e.is_completed]
    payments = [e for e in events if e.category == "payment" and not e.is_completed]
    
    return {
        "week_start": week_start.strftime("%Y-%m-%d"),
        "week_end": week_end.strftime("%Y-%m-%d"),
        "total_events": len(events),
        "high_priority_events": len(high_priority),
        "payment_events": len(payments),
        "pending_todos": len(todos),
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "date": e.start_date,
                "priority": e.priority,
                "category": e.category
            }
            for e in events[:10]
        ],
        "todos": [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "due_date": t.due_date
            }
            for t in todos[:10]
        ]
    }

