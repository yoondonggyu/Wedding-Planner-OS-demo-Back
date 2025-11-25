"""
음성 비서 서비스 - LLM 기반 의도 분석 및 자동 정리 파이프라인
"""
import json
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.models.memory import (
    CALENDAR_EVENTS, TODOS, BUDGET_ITEMS, POSTS, COUNTERS,
    CalendarEvent, Todo, BudgetItem, Post
)
from app.services.stt_service import transcribe_audio
from app.services.model_client import chat_with_model
from app.services import calendar_service, budget_service


async def analyze_intent_and_organize(
    text: str,
    user_id: int
) -> Dict:
    """
    LLM 기반 의도 분석 및 자동 정리 파이프라인
    음성 → 텍스트 → 요약 → 구조화 → DB 반영
    """
    # 1. 의도 분석 및 구조화
    intent_prompt = f"""다음은 사용자가 음성으로 말한 내용입니다. 이를 분석하여 자동으로 정리해주세요.

[사용자 음성 내용]
{text}

다음 중 어떤 작업이 필요한지 분석하고, 필요한 정보를 추출해주세요:
1. 캘린더 일정 생성 (날짜, 시간, 제목, 카테고리)
2. 예산 항목 추가/수정 (항목명, 금액, 카테고리)
3. 할일(Todo) 생성 (제목, 우선순위, 마감일)
4. 게시판 게시글 생성 (제목, 내용, 카테고리)
5. 단순 질문/답변 (정보 조회)

다음 JSON 형식으로 응답해주세요:
{{
  "intent": "calendar|budget|todo|post|query",
  "action": "create|update|query",
  "entities": {{
    "title": "제목",
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "amount": 숫자,
    "category": "카테고리",
    "content": "내용",
    "priority": "high|medium|low"
  }},
  "summary": "요약된 내용"
}}

JSON만 응답해주세요."""

    try:
        response = await chat_with_model(intent_prompt, model="gemma3:4b")
        
        if response:
            # JSON 추출
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                intent_data = json.loads(json_match.group())
                
                # 2. 자동 정리 파이프라인 실행
                organized_items = await execute_organize_pipeline(intent_data, user_id, text)
                
                return {
                    "intent": intent_data.get("intent", "query"),
                    "action": intent_data.get("action", "query"),
                    "summary": intent_data.get("summary", text),
                    "organized_items": organized_items
                }
    except Exception as e:
        print(f"⚠️ 의도 분석 실패: {e}")
    
    return {
        "intent": "query",
        "action": "query",
        "summary": text,
        "organized_items": []
    }


async def execute_organize_pipeline(
    intent_data: Dict,
    user_id: int,
    original_text: str
) -> List[Dict]:
    """
    자동 정리 파이프라인 실행
    의도에 따라 캘린더/예산/할일/게시판에 자동 반영
    """
    organized = []
    entities = intent_data.get("entities", {})
    intent = intent_data.get("intent", "query")
    action = intent_data.get("action", "query")
    
    if action == "query":
        # 질문인 경우 처리하지 않음
        return organized
    
    # 캘린더 일정 생성
    if intent == "calendar" and entities.get("date"):
        try:
            event_id = COUNTERS["event"]
            COUNTERS["event"] += 1
            
            event = CalendarEvent(
                id=event_id,
                user_id=user_id,
                title=entities.get("title", "일정"),
                description=entities.get("content", original_text),
                start_date=entities.get("date"),
                start_time=entities.get("time"),
                category=entities.get("category", "general"),
                priority=entities.get("priority", "medium"),
                created_at=datetime.now().strftime("%Y-%m-%d")
            )
            
            CALENDAR_EVENTS[event_id] = event
            organized.append({
                "type": "calendar_event",
                "id": event_id,
                "title": event.title,
                "date": event.start_date
            })
        except Exception as e:
            print(f"⚠️ 캘린더 일정 생성 실패: {e}")
    
    # 예산 항목 생성
    if intent == "budget" and entities.get("amount"):
        try:
            item_id = COUNTERS["budget"]
            COUNTERS["budget"] += 1
            
            item = BudgetItem(
                id=item_id,
                user_id=user_id,
                item_name=entities.get("title", "항목"),
                category=entities.get("category", "etc"),
                estimated_budget=float(entities.get("amount", 0)),
                notes=entities.get("content", original_text),
                created_at=datetime.now().strftime("%Y-%m-%d"),
                updated_at=datetime.now().strftime("%Y-%m-%d")
            )
            
            BUDGET_ITEMS[item_id] = item
            organized.append({
                "type": "budget_item",
                "id": item_id,
                "title": item.item_name,
                "amount": item.estimated_budget
            })
        except Exception as e:
            print(f"⚠️ 예산 항목 생성 실패: {e}")
    
    # 할일 생성
    if intent == "todo":
        try:
            todo_id = COUNTERS["todo"]
            COUNTERS["todo"] += 1
            
            todo = Todo(
                id=todo_id,
                user_id=user_id,
                title=entities.get("title", "할일"),
                description=entities.get("content", original_text),
                priority=entities.get("priority", "medium"),
                due_date=entities.get("date"),
                created_at=datetime.now().strftime("%Y-%m-%d")
            )
            
            TODOS[todo_id] = todo
            organized.append({
                "type": "todo",
                "id": todo_id,
                "title": todo.title
            })
        except Exception as e:
            print(f"⚠️ 할일 생성 실패: {e}")
    
    # 게시판 게시글 생성
    if intent == "post":
        try:
            post_id = COUNTERS["post"]
            COUNTERS["post"] += 1
            
            post = Post(
                id=post_id,
                user_id=user_id,
                title=entities.get("title", "음성 메모"),
                content=entities.get("content", original_text),
                board_type="couple"  # 음성 메모는 커플 게시판에 저장
            )
            
            POSTS[post_id] = post
            organized.append({
                "type": "post",
                "id": post_id,
                "title": post.title
            })
        except Exception as e:
            print(f"⚠️ 게시글 생성 실패: {e}")
    
    return organized


async def generate_voice_response(
    query: str,
    user_id: int
) -> str:
    """
    LLM 기반 음성 답변 생성 (상황 맞춤 답변)
    """
    # 사용자 데이터 조회
    calendar_summary = calendar_service.get_week_summary(user_id)
    budget_summary = budget_service.get_category_summary(user_id)
    
    prompt = f"""사용자가 음성으로 질문했습니다. 개인 데이터를 참고하여 답변해주세요.

[사용자 질문]
{query}

[사용자 데이터]
- 이번 주 일정: {len(calendar_summary.get('events', []))}개
- 예산 상황: 예상 {budget_summary.get('total_estimated', 0):,.0f}원, 실제 {budget_summary.get('total_actual', 0):,.0f}원

친절하고 간결하게 답변해주세요. 한 문장으로 답변하는 것이 좋습니다."""

    try:
        response = await chat_with_model(prompt, model="gemma3:4b")
        return response.strip() if response else "죄송합니다. 답변을 생성할 수 없습니다."
    except Exception as e:
        print(f"⚠️ 음성 답변 생성 실패: {e}")
        return "죄송합니다. 답변을 생성할 수 없습니다."



