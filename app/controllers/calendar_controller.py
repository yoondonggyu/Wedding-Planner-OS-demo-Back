"""
캘린더 컨트롤러
"""
from typing import Dict, List
from app.models.memory import (
    CALENDAR_EVENTS, TODOS, COUNTERS, CalendarEvent, Todo
)
from app.schemas import (
    CalendarEventCreateReq, CalendarEventUpdateReq,
    TodoCreateReq, TodoUpdateReq, WeddingDateSetReq, TimelineGenerateReq
)
from app.services import calendar_service
from datetime import datetime


def set_wedding_date(user_id: int, wedding_date: str) -> Dict:
    """예식일 설정"""
    calendar_service.USER_WEDDING_DATES[user_id] = wedding_date
    return {
        "message": "wedding_date_set",
        "data": {"wedding_date": wedding_date}
    }


async def generate_timeline(
    user_id: int,
    request: TimelineGenerateReq
) -> Dict:
    """타임라인 자동 생성"""
    events = await calendar_service.create_timeline_from_wedding_date(
        user_id,
        request.wedding_date,
        request.user_preferences
    )
    
    return {
        "message": "timeline_generated",
        "data": {
            "wedding_date": request.wedding_date,
            "events_count": len(events),
            "events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "start_date": e.start_date,
                    "category": e.category,
                    "priority": e.priority,
                    "d_day_offset": e.d_day_offset
                }
                for e in events
            ]
        }
    }


def create_event(user_id: int, request: CalendarEventCreateReq) -> Dict:
    """일정 생성"""
    event_id = COUNTERS["event"]
    COUNTERS["event"] += 1
    
    event = CalendarEvent(
        id=event_id,
        user_id=user_id,
        title=request.title,
        description=request.description,
        start_date=request.start_date,
        end_date=request.end_date,
        start_time=request.start_time,
        end_time=request.end_time,
        location=request.location,
        category=request.category,
        priority=request.priority,
        assignee=request.assignee,
        reminder_days=request.reminder_days,
        wedding_d_day=request.wedding_d_day,
        d_day_offset=request.d_day_offset
    )
    
    CALENDAR_EVENTS[event_id] = event
    
    return {
        "message": "event_created",
        "data": {
            "id": event.id,
            "title": event.title,
            "start_date": event.start_date
        }
    }


def update_event(event_id: int, user_id: int, request: CalendarEventUpdateReq) -> Dict:
    """일정 수정"""
    event = CALENDAR_EVENTS.get(event_id)
    if not event or event.user_id != user_id:
        return {"message": "error", "data": {"error": "일정을 찾을 수 없습니다."}}
    
    if request.title is not None:
        event.title = request.title
    if request.description is not None:
        event.description = request.description
    if request.start_date is not None:
        event.start_date = request.start_date
    if request.end_date is not None:
        event.end_date = request.end_date
    if request.start_time is not None:
        event.start_time = request.start_time
    if request.end_time is not None:
        event.end_time = request.end_time
    if request.location is not None:
        event.location = request.location
    if request.category is not None:
        event.category = request.category
    if request.priority is not None:
        event.priority = request.priority
    if request.assignee is not None:
        event.assignee = request.assignee
    if request.progress is not None:
        event.progress = request.progress
    if request.is_completed is not None:
        event.is_completed = request.is_completed
    if request.reminder_days is not None:
        event.reminder_days = request.reminder_days
    
    return {
        "message": "event_updated",
        "data": {
            "id": event.id,
            "title": event.title
        }
    }


def delete_event(event_id: int, user_id: int) -> Dict:
    """일정 삭제"""
    event = CALENDAR_EVENTS.get(event_id)
    if not event or event.user_id != user_id:
        return {"message": "error", "data": {"error": "일정을 찾을 수 없습니다."}}
    
    del CALENDAR_EVENTS[event_id]
    return {"message": "event_deleted", "data": {"id": event_id}}


def get_events(user_id: int, start_date: str | None = None, end_date: str | None = None) -> Dict:
    """일정 조회"""
    events = calendar_service.get_user_events(user_id, start_date, end_date)
    
    return {
        "message": "events_retrieved",
        "data": {
            "events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "description": e.description,
                    "start_date": e.start_date,
                    "end_date": e.end_date,
                    "start_time": e.start_time,
                    "end_time": e.end_time,
                    "location": e.location,
                    "category": e.category,
                    "priority": e.priority,
                    "assignee": e.assignee,
                    "progress": e.progress,
                    "is_completed": e.is_completed,
                    "d_day_offset": e.d_day_offset,
                    "reminder_days": e.reminder_days
                }
                for e in events
            ]
        }
    }


def get_upcoming_events(user_id: int, days: int = 7) -> Dict:
    """다가오는 일정 조회"""
    events = calendar_service.get_upcoming_events(user_id, days)
    
    return {
        "message": "upcoming_events_retrieved",
        "data": {
            "events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "start_date": e.start_date,
                    "start_time": e.start_time,
                    "category": e.category,
                    "priority": e.priority
                }
                for e in events
            ]
        }
    }


def get_week_summary(user_id: int) -> Dict:
    """이번 주 요약 (챗봇 연동용)"""
    summary = calendar_service.get_week_summary(user_id)
    return {
        "message": "week_summary_retrieved",
        "data": summary
    }


def create_todo(user_id: int, request: TodoCreateReq) -> Dict:
    """할일 생성"""
    todo_id = COUNTERS["todo"]
    COUNTERS["todo"] += 1
    
    todo = Todo(
        id=todo_id,
        user_id=user_id,
        event_id=request.event_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        assignee=request.assignee,
        due_date=request.due_date,
        created_at=datetime.now().strftime("%Y-%m-%d")
    )
    
    TODOS[todo_id] = todo
    
    return {
        "message": "todo_created",
        "data": {
            "id": todo.id,
            "title": todo.title
        }
    }


def update_todo(todo_id: int, user_id: int, request: TodoUpdateReq) -> Dict:
    """할일 수정"""
    todo = TODOS.get(todo_id)
    if not todo or todo.user_id != user_id:
        return {"message": "error", "data": {"error": "할일을 찾을 수 없습니다."}}
    
    if request.title is not None:
        todo.title = request.title
    if request.description is not None:
        todo.description = request.description
    if request.priority is not None:
        todo.priority = request.priority
    if request.assignee is not None:
        todo.assignee = request.assignee
    if request.progress is not None:
        todo.progress = request.progress
    if request.due_date is not None:
        todo.due_date = request.due_date
    if request.is_completed is not None:
        todo.is_completed = request.is_completed
    
    return {
        "message": "todo_updated",
        "data": {
            "id": todo.id,
            "title": todo.title
        }
    }


def delete_todo(todo_id: int, user_id: int) -> Dict:
    """할일 삭제"""
    todo = TODOS.get(todo_id)
    if not todo or todo.user_id != user_id:
        return {"message": "error", "data": {"error": "할일을 찾을 수 없습니다."}}
    
    del TODOS[todo_id]
    return {"message": "todo_deleted", "data": {"id": todo_id}}


def get_todos(user_id: int, completed: bool | None = None) -> Dict:
    """할일 조회"""
    todos = calendar_service.get_user_todos(user_id, completed)
    
    return {
        "message": "todos_retrieved",
        "data": {
            "todos": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority,
                    "assignee": t.assignee,
                    "progress": t.progress,
                    "due_date": t.due_date,
                    "is_completed": t.is_completed,
                    "event_id": t.event_id
                }
                for t in todos
            ]
        }
    }


