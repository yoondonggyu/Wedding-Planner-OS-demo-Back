"""
캘린더 컨트롤러 - DB 기반
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from app.models.db import CalendarEvent, WeddingDate, User
from app.schemas import (
    CalendarEventCreateReq, CalendarEventUpdateReq,
    TodoCreateReq, TodoUpdateReq, WeddingDateSetReq, TimelineGenerateReq
)
from app.core.exceptions import not_found, forbidden, bad_request
from app.core.error_codes import ErrorCode
from app.services import calendar_service
from app.core.couple_helpers import get_user_couple_id, get_couple_filter_with_user


def set_wedding_date(user_id: int, wedding_date: str, db: Session) -> Dict:
    """예식일 설정"""
    try:
        # String을 Date로 변환
        from datetime import datetime as dt
        wedding_date_obj_db = dt.strptime(wedding_date, "%Y-%m-%d").date()
        
        # 기존 예식일이 있으면 업데이트, 없으면 생성
        wedding_date_obj = db.query(WeddingDate).filter(WeddingDate.user_id == user_id).first()
        
        if wedding_date_obj:
            # 기존 예식일 업데이트
            wedding_date_obj.wedding_date = wedding_date_obj_db
            wedding_date_obj.updated_at = datetime.now()
            print(f"예식일 업데이트: user_id={user_id}, wedding_date={wedding_date}")
        else:
            # 새 예식일 생성
            wedding_date_obj = WeddingDate(
                user_id=user_id,
                wedding_date=wedding_date_obj_db
            )
            db.add(wedding_date_obj)
            print(f"예식일 생성: user_id={user_id}, wedding_date={wedding_date}")
        
        db.commit()
        db.refresh(wedding_date_obj)
        
        # Date를 String으로 변환하여 반환
        wedding_date_str = wedding_date_obj.wedding_date.strftime("%Y-%m-%d") if wedding_date_obj.wedding_date else None
        
        return {
            "message": "wedding_date_set",
            "data": {"wedding_date": wedding_date_str}
        }
    except Exception as e:
        db.rollback()
        print(f"예식일 설정 실패: user_id={user_id}, error={str(e)}")
        import traceback
        traceback.print_exc()
        raise


def get_wedding_date(user_id: int, db: Session) -> Dict:
    """예식일 조회"""
    try:
        wedding_date_obj = db.query(WeddingDate).filter(WeddingDate.user_id == user_id).first()
        
        # Date를 String으로 변환
        if wedding_date_obj and wedding_date_obj.wedding_date:
            wedding_date_str = wedding_date_obj.wedding_date.strftime("%Y-%m-%d")
        else:
            wedding_date_str = None
        
        print(f"예식일 조회: user_id={user_id}, wedding_date={wedding_date_str}")
        
        return {
            "message": "wedding_date_retrieved",
            "data": {"wedding_date": wedding_date_str}
        }
    except Exception as e:
        print(f"예식일 조회 실패: user_id={user_id}, error={str(e)}")
        import traceback
        traceback.print_exc()
        raise


async def generate_timeline(
    user_id: int,
    request: TimelineGenerateReq,
    db: Session
) -> Dict:
    """타임라인 자동 생성"""
    from datetime import datetime as dt
    
    # 기존 자동 생성된 일정 삭제는 하지 않음 (DB에 is_auto_generated 컬럼이 없음)
    
    # 타임라인 생성 (서비스에서 딕셔너리 리스트 반환)
    events_dict = await calendar_service.create_timeline_from_wedding_date(
        user_id,
        request.wedding_date,
        request.user_preferences
    )
    
    # DB에 저장
    created_events = []
    for e in events_dict:
        # String을 Date/Time으로 변환
        start_date = dt.strptime(e["start_date"], "%Y-%m-%d").date() if e.get("start_date") else None
        end_date = dt.strptime(e.get("end_date"), "%Y-%m-%d").date() if e.get("end_date") else None
        start_time = dt.strptime(e.get("start_time"), "%H:%M").time() if e.get("start_time") else None
        end_time = dt.strptime(e.get("end_time"), "%H:%M").time() if e.get("end_time") else None
        
        # 커플 ID 가져오기
        couple_id = get_user_couple_id(e["user_id"], db)
        
        event = CalendarEvent(
            user_id=e["user_id"],
            couple_id=couple_id,  # 커플 공유
            title=e["title"],
            description=e.get("description"),
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            location=e.get("location"),
            category=e["category"],
            priority=e.get("priority", "medium"),
            assignee=e.get("assignee", "both"),
            # reminder_days, wedding_d_day, d_day_offset, is_auto_generated, metadata는 DB에 없거나 사용 안 함
        )
        db.add(event)
        created_events.append(event)
    
    db.commit()
    
    # 생성된 이벤트 ID 반환
    for i, event in enumerate(created_events):
        db.refresh(event)
        created_events[i] = event
    
    return {
        "message": "timeline_generated",
        "data": {
            "wedding_date": request.wedding_date,
            "events_count": len(created_events),
            "events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "start_date": e.start_date.strftime("%Y-%m-%d") if e.start_date else None,
                    "category": e.category,
                    "priority": e.priority.value if hasattr(e.priority, 'value') else str(e.priority),
                }
                for e in created_events
            ]
        }
    }


def create_event(user_id: int, request: CalendarEventCreateReq, db: Session) -> Dict:
    """일정 생성"""
    from datetime import datetime as dt
    from app.models.db.calendar import PriorityEnum, AssigneeEnum
    
    # String을 Date/Time으로 변환
    start_date = dt.strptime(request.start_date, "%Y-%m-%d").date() if request.start_date else None
    end_date = dt.strptime(request.end_date, "%Y-%m-%d").date() if request.end_date else None
    start_time = dt.strptime(request.start_time, "%H:%M").time() if request.start_time else None
    end_time = dt.strptime(request.end_time, "%H:%M").time() if request.end_time else None
    
    # ENUM 변환
    priority = None
    if request.priority:
        if isinstance(request.priority, str):
            priority = PriorityEnum(request.priority)
        else:
            priority = request.priority
    
    assignee = None
    if request.assignee:
        if isinstance(request.assignee, str):
            assignee = AssigneeEnum(request.assignee)
        else:
            assignee = request.assignee
    
    # 커플 ID 가져오기
    couple_id = get_user_couple_id(user_id, db)
    
    event = CalendarEvent(
        user_id=user_id,
        couple_id=couple_id,  # 커플 공유
        title=request.title,
        description=request.description,
        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time,
        location=request.location,
        category=request.category,
        priority=priority,
        assignee=assignee,
        # reminder_days, wedding_d_day, d_day_offset, is_auto_generated는 DB에 없으므로 제거
    )
    
    try:
        db.add(event)
        db.commit()
        db.refresh(event)
    except Exception as e:
        db.rollback()
        print(f"일정 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    return {
        "message": "event_created",
        "data": {
            "id": event.id,
            "title": event.title,
            "start_date": event.start_date.strftime("%Y-%m-%d") if event.start_date else None
        }
    }


def update_event(event_id: int, user_id: int, request: CalendarEventUpdateReq, db: Session) -> Dict:
    """일정 수정"""
    from datetime import datetime as dt
    
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise not_found("event_not_found", ErrorCode.EVENT_NOT_FOUND)
    
    if event.user_id != user_id:
        raise forbidden("forbidden", ErrorCode.FORBIDDEN)
    
    if request.title is not None:
        event.title = request.title
    if request.description is not None:
        event.description = request.description
    if request.start_date is not None:
        event.start_date = dt.strptime(request.start_date, "%Y-%m-%d").date()
    if request.end_date is not None:
        event.end_date = dt.strptime(request.end_date, "%Y-%m-%d").date()
    if request.start_time is not None:
        event.start_time = dt.strptime(request.start_time, "%H:%M").time()
    if request.end_time is not None:
        event.end_time = dt.strptime(request.end_time, "%H:%M").time()
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
    # reminder_days는 DB에 없으므로 제거
    
    db.commit()
    db.refresh(event)
    
    return {
        "message": "event_updated",
        "data": {
            "id": event.id,
            "title": event.title
        }
    }


def delete_event(event_id: int, user_id: int, db: Session) -> Dict:
    """일정 삭제"""
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise not_found("event_not_found", ErrorCode.EVENT_NOT_FOUND)
    
    if event.user_id != user_id:
        raise forbidden("forbidden", ErrorCode.FORBIDDEN)
    
    db.delete(event)
    db.commit()
    
    return {"message": "event_deleted", "data": {"id": event_id}}


def get_events(user_id: int, start_date: str | None = None, end_date: str | None = None, db: Session = None) -> Dict:
    """일정 조회 (커플 데이터 공유)"""
    from datetime import datetime as dt
    
    # 커플 필터 생성
    couple_filter = get_couple_filter_with_user(user_id, db, CalendarEvent)
    query = db.query(CalendarEvent).filter(couple_filter)
    
    if start_date:
        start_date_obj = dt.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(CalendarEvent.start_date >= start_date_obj)
    if end_date:
        end_date_obj = dt.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(CalendarEvent.start_date <= end_date_obj)
    
    events = query.order_by(CalendarEvent.start_date, CalendarEvent.start_time).all()
    
    return {
        "message": "events_retrieved",
        "data": {
            "events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "description": e.description,
                    "start_date": e.start_date.strftime("%Y-%m-%d") if e.start_date else None,
                    "end_date": e.end_date.strftime("%Y-%m-%d") if e.end_date else None,
                    "start_time": e.start_time.strftime("%H:%M") if e.start_time else None,
                    "end_time": e.end_time.strftime("%H:%M") if e.end_time else None,
                    "location": e.location,
                    "category": e.category,
                    "priority": e.priority.value if hasattr(e.priority, 'value') else (str(e.priority) if e.priority else None),
                    "assignee": e.assignee.value if hasattr(e.assignee, 'value') else (str(e.assignee) if e.assignee else None),
                    "progress": e.progress,
                    "is_completed": e.is_completed,
                    # d_day_offset, reminder_days, is_auto_generated는 DB에 없으므로 제거
                }
                for e in events
            ]
        }
    }


def get_upcoming_events(user_id: int, days: int = 7, db: Session = None) -> Dict:
    """다가오는 일정 조회 (커플 데이터 공유)"""
    today = datetime.now().date()
    end_date = today + timedelta(days=days)
    
    # 커플 필터 생성
    couple_filter = get_couple_filter_with_user(user_id, db, CalendarEvent)
    
    events = db.query(CalendarEvent).filter(
        couple_filter,
        CalendarEvent.start_date >= today,
        CalendarEvent.start_date <= end_date
    ).order_by(CalendarEvent.start_date, CalendarEvent.start_time).all()
    
    return {
        "message": "upcoming_events_retrieved",
        "data": {
            "events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "start_date": e.start_date.strftime("%Y-%m-%d") if e.start_date else None,
                    "start_time": e.start_time.strftime("%H:%M") if e.start_time else None,
                    "category": e.category,
                    "priority": e.priority.value if hasattr(e.priority, 'value') else (str(e.priority) if e.priority else None)
                }
                for e in events
            ]
        }
    }


def get_week_summary(user_id: int, db: Session) -> Dict:
    """이번 주 요약 (챗봇 연동용)"""
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    
    # 일정 조회 (category != 'todo')
    events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == user_id,
        CalendarEvent.start_date >= today,
        CalendarEvent.start_date <= week_end,
        CalendarEvent.category != 'todo'  # 할일 제외
    ).all()
    
    # 할일 조회 (category == 'todo')
    todos = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == user_id,
        CalendarEvent.category == 'todo',
        CalendarEvent.is_completed == False
    ).all()
    
    return {
        "message": "week_summary_retrieved",
        "data": {
            "events_count": len(events),
            "todos_count": len(todos),
            "events": [{"title": e.title, "date": e.start_date.strftime("%Y-%m-%d") if e.start_date else None} for e in events],
            "todos": [{"title": t.title, "due_date": t.start_date.strftime("%Y-%m-%d") if t.start_date else None} for t in todos]
        }
    }


def create_todo(user_id: int, request: TodoCreateReq, db: Session) -> Dict:
    """일정/할일 생성 (calendar_events 테이블 사용, 통합 API)"""
    from datetime import datetime as dt
    from app.models.db.calendar import PriorityEnum, AssigneeEnum
    
    # start_date 우선, 없으면 due_date 사용
    date_str = request.start_date or request.due_date
    start_date = dt.strptime(date_str, "%Y-%m-%d").date() if date_str else None
    
    end_date = dt.strptime(request.end_date, "%Y-%m-%d").date() if request.end_date else None
    start_time = dt.strptime(request.start_time, "%H:%M").time() if request.start_time else None
    end_time = dt.strptime(request.end_time, "%H:%M").time() if request.end_time else None
    
    # ENUM 변환
    priority = None
    if request.priority:
        if isinstance(request.priority, str):
            priority = PriorityEnum(request.priority)
        else:
            priority = request.priority
    
    assignee = None
    if request.assignee:
        if isinstance(request.assignee, str):
            assignee = AssigneeEnum(request.assignee)
        else:
            assignee = request.assignee
    
    # calendar_events 테이블에 저장 (category로 일정/할일 구분)
    event = CalendarEvent(
        user_id=user_id,
        title=request.title,
        description=request.description,
        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time,
        location=request.location,
        category=request.category or 'todo',  # 기본값은 'todo'
        priority=priority,
        assignee=assignee,
        is_completed=request.is_completed or False
    )
    
    try:
        db.add(event)
        db.commit()
        db.refresh(event)
    except Exception as e:
        db.rollback()
        print(f"일정/할일 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    return {
        "message": "todo_created",
        "data": {
            "id": event.id,
            "title": event.title,
            "start_date": event.start_date.strftime("%Y-%m-%d") if event.start_date else None,
            "category": event.category
        }
    }


def update_todo(todo_id: int, user_id: int, request: TodoUpdateReq, db: Session) -> Dict:
    """일정/할일 수정 (calendar_events 테이블 사용, 통합 API)"""
    from datetime import datetime as dt
    from app.models.db.calendar import PriorityEnum, AssigneeEnum
    
    event = db.query(CalendarEvent).filter(CalendarEvent.id == todo_id).first()
    if not event:
        raise not_found("todo_not_found", ErrorCode.EVENT_NOT_FOUND)
    
    if event.user_id != user_id:
        raise forbidden("forbidden", ErrorCode.FORBIDDEN)
    
    if request.title is not None:
        event.title = request.title
    if request.description is not None:
        event.description = request.description
    if request.priority is not None:
        if isinstance(request.priority, str):
            event.priority = PriorityEnum(request.priority)
        else:
            event.priority = request.priority
    if request.assignee is not None:
        if isinstance(request.assignee, str):
            event.assignee = AssigneeEnum(request.assignee)
        else:
            event.assignee = request.assignee
    if request.due_date is not None:
        event.start_date = dt.strptime(request.due_date, "%Y-%m-%d").date() if request.due_date else None
    if request.start_date is not None:
        event.start_date = dt.strptime(request.start_date, "%Y-%m-%d").date() if request.start_date else None
    if request.end_date is not None:
        event.end_date = dt.strptime(request.end_date, "%Y-%m-%d").date() if request.end_date else None
    if request.start_time is not None:
        event.start_time = dt.strptime(request.start_time, "%H:%M").time() if request.start_time else None
    if request.end_time is not None:
        event.end_time = dt.strptime(request.end_time, "%H:%M").time() if request.end_time else None
    if request.location is not None:
        event.location = request.location
    if request.category is not None:
        event.category = request.category
    if request.is_completed is not None:
        event.is_completed = request.is_completed
    if request.progress is not None:
        event.progress = request.progress
    
    db.commit()
    db.refresh(event)
    
    return {
        "message": "todo_updated",
        "data": {
            "id": event.id,
            "title": event.title
        }
    }


def delete_todo(todo_id: int, user_id: int, db: Session) -> Dict:
    """일정/할일 삭제 (calendar_events 테이블 사용, 통합 API)"""
    event = db.query(CalendarEvent).filter(CalendarEvent.id == todo_id).first()
    if not event:
        raise not_found("todo_not_found", ErrorCode.TODO_NOT_FOUND)
    
    if event.user_id != user_id:
        raise forbidden("forbidden", ErrorCode.FORBIDDEN)
    
    db.delete(event)
    db.commit()
    
    return {"message": "todo_deleted", "data": {"id": todo_id}}


def get_todos(user_id: int, completed: bool | None = None, start_date: str | None = None, end_date: str | None = None, category: str | None = None, db: Session = None) -> Dict:
    """일정/할일 조회 (calendar_events 테이블 사용, 통합 API)"""
    from datetime import datetime as dt
    
    # 모든 일정 조회 (category 필터는 선택적)
    query = db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id)
    
    # category 필터 (지정된 경우만)
    if category:
        query = query.filter(CalendarEvent.category == category)
    
    if completed is not None:
        query = query.filter(CalendarEvent.is_completed == completed)
    
    if start_date:
        start_date_obj = dt.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(CalendarEvent.start_date >= start_date_obj)
    if end_date:
        end_date_obj = dt.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(CalendarEvent.start_date <= end_date_obj)
    
    events = query.order_by(CalendarEvent.start_date, CalendarEvent.start_time).all()
    
    return {
        "message": "todos_retrieved",
        "data": {
            "events": [  # 응답 필드명을 events로 통일 (프론트엔드 호환성)
                {
                    "id": e.id,
                    "title": e.title,
                    "description": e.description,
                    "start_date": e.start_date.strftime("%Y-%m-%d") if e.start_date else None,
                    "start_time": e.start_time.strftime("%H:%M") if e.start_time else None,
                    "end_date": e.end_date.strftime("%Y-%m-%d") if e.end_date else None,
                    "end_time": e.end_time.strftime("%H:%M") if e.end_time else None,
                    "category": e.category,
                    "priority": e.priority.value if hasattr(e.priority, 'value') else (str(e.priority) if e.priority else None),
                    "assignee": e.assignee.value if hasattr(e.assignee, 'value') else (str(e.assignee) if e.assignee else None),
                    "is_completed": e.is_completed,
                    "location": e.location,
                    "progress": e.progress
                }
                for e in events
            ]
        }
    }
