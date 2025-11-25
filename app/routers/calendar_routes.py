from fastapi import APIRouter, HTTPException, Query
from app.schemas import (
    CalendarEventCreateReq, CalendarEventUpdateReq,
    TodoCreateReq, TodoUpdateReq, WeddingDateSetReq, TimelineGenerateReq
)
from app.controllers import calendar_controller

router = APIRouter(tags=["calendar"])

# 예식일 설정
@router.post("/calendar/wedding-date")
async def set_wedding_date(request: WeddingDateSetReq, user_id: int = Query(...)):
    """예식일 설정"""
    return calendar_controller.set_wedding_date(user_id, request.wedding_date)

# 타임라인 생성
@router.post("/calendar/timeline/generate")
async def generate_timeline(request: TimelineGenerateReq, user_id: int = Query(...)):
    """D-Day 기반 타임라인 자동 생성"""
    return await calendar_controller.generate_timeline(user_id, request)

# 일정 관리
@router.post("/calendar/events")
async def create_event(request: CalendarEventCreateReq, user_id: int = Query(...)):
    """일정 생성"""
    return calendar_controller.create_event(user_id, request)

@router.get("/calendar/events")
async def get_events(
    user_id: int = Query(...),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None)
):
    """일정 조회"""
    return calendar_controller.get_events(user_id, start_date, end_date)

@router.get("/calendar/events/upcoming")
async def get_upcoming_events(
    user_id: int = Query(...),
    days: int = Query(7, ge=1, le=30)
):
    """다가오는 일정 조회"""
    return calendar_controller.get_upcoming_events(user_id, days)

@router.put("/calendar/events/{event_id}")
async def update_event(
    event_id: int,
    request: CalendarEventUpdateReq,
    user_id: int = Query(...)
):
    """일정 수정"""
    return calendar_controller.update_event(event_id, user_id, request)

@router.delete("/calendar/events/{event_id}")
async def delete_event(event_id: int, user_id: int = Query(...)):
    """일정 삭제"""
    return calendar_controller.delete_event(event_id, user_id)

# 할일 관리
@router.post("/calendar/todos")
async def create_todo(request: TodoCreateReq, user_id: int = Query(...)):
    """할일 생성"""
    return calendar_controller.create_todo(user_id, request)

@router.get("/calendar/todos")
async def get_todos(
    user_id: int = Query(...),
    completed: bool | None = Query(None)
):
    """할일 조회"""
    return calendar_controller.get_todos(user_id, completed)

@router.put("/calendar/todos/{todo_id}")
async def update_todo(
    todo_id: int,
    request: TodoUpdateReq,
    user_id: int = Query(...)
):
    """할일 수정"""
    return calendar_controller.update_todo(todo_id, user_id, request)

@router.delete("/calendar/todos/{todo_id}")
async def delete_todo(todo_id: int, user_id: int = Query(...)):
    """할일 삭제"""
    return calendar_controller.delete_todo(todo_id, user_id)

# 챗봇 연동
@router.get("/calendar/week-summary")
async def get_week_summary(user_id: int = Query(...)):
    """이번 주 요약 (챗봇 연동용)"""
    return calendar_controller.get_week_summary(user_id)



