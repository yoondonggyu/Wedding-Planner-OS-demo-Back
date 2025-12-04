from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from app.schemas import (
    CalendarEventCreateReq, CalendarEventUpdateReq,
    TodoCreateReq, TodoUpdateReq, WeddingDateSetReq, TimelineGenerateReq
)
from app.controllers import calendar_controller
from app.core.database import get_db
from app.core.security import get_current_user_id

router = APIRouter(tags=["calendar"])

# 예식일 설정
@router.post("/calendar/wedding-date")
async def set_wedding_date(request: WeddingDateSetReq, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """예식일 설정 (JWT 토큰에서 user_id 추출)"""
    return calendar_controller.set_wedding_date(user_id, request.wedding_date, db)

@router.get("/calendar/wedding-date")
async def get_wedding_date(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """예식일 조회 (JWT 토큰에서 user_id 추출)"""
    return calendar_controller.get_wedding_date(user_id, db)

# 타임라인 생성
@router.post("/calendar/timeline/generate")
async def generate_timeline(request: TimelineGenerateReq, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """D-Day 기반 타임라인 자동 생성 (JWT 토큰에서 user_id 추출)"""
    return await calendar_controller.generate_timeline(user_id, request, db)

# 일정/할일 통합 관리 (todos API 사용)
@router.post("/calendar/todos")
async def create_todo(request: TodoCreateReq, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """일정/할일 생성 (통합 API, JWT 토큰에서 user_id 추출)"""
    return calendar_controller.create_todo(user_id, request, db)

@router.get("/calendar/todos")
async def get_todos(
    user_id: int = Depends(get_current_user_id),
    completed: bool | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    category: str | None = Query(None),  # 'todo'로 필터링하면 할일만, None이면 모든 일정
    db: Session = Depends(get_db)
):
    """일정/할일 조회 (통합 API, JWT 토큰에서 user_id 추출)"""
    return calendar_controller.get_todos(user_id, completed, start_date, end_date, category, db)

@router.put("/calendar/todos/{todo_id}")
async def update_todo(
    todo_id: int,
    request: TodoUpdateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """일정/할일 수정 (통합 API, JWT 토큰에서 user_id 추출)"""
    return calendar_controller.update_todo(todo_id, user_id, request, db)

@router.delete("/calendar/todos/{todo_id}")
async def delete_todo(todo_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """일정/할일 삭제 (통합 API, JWT 토큰에서 user_id 추출)"""
    return calendar_controller.delete_todo(todo_id, user_id, db)

# 챗봇 연동
@router.get("/calendar/week-summary")
async def get_week_summary(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """이번 주 요약 (챗봇 연동용, JWT 토큰에서 user_id 추출)"""
    return calendar_controller.get_week_summary(user_id, db)

@router.get("/calendar/completed-reservations")
async def get_completed_reservations(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """완료된 예약 중 하루 이상 지난 것 조회 (리뷰 작성용)"""
    return calendar_controller.get_completed_reservations_for_review(user_id, db)





