"""
챗봇 서비스 - RAG + 개인 데이터 통합 + Vector DB 검색
"""
import json
from typing import AsyncGenerator, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.db import User, Post, Comment
from app.services.model_client import chat_with_model, analyze_sentiment, get_model_api_base_url
from app.services import post_vector_service, user_memory_service, chat_memory_vector_service
import httpx


async def get_user_context(user_id: int, db: Session = None) -> Dict:
    """
    사용자의 개인 데이터 수집 (캘린더/예산/게시판)
    
    Args:
        user_id: 사용자 ID
        db: DB 세션 (선택적, 없으면 메모리 기반으로 동작)
    """
    context = {
        "user_info": None,
        "recent_posts": [],
        "recent_comments": [],
        "summary": ""
    }
    
    # DB 세션이 있으면 DB에서 조회, 없으면 메모리에서 조회
    if db:
        # DB에서 사용자 정보 조회
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            context["user_info"] = {
                "nickname": user.nickname,
                "email": user.email
            }
        
        # 최근 게시글 (최대 10개)
        user_posts = db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).limit(10).all()
        context["recent_posts"] = [
            {
                "id": p.id,
                "title": p.title,
                "content": p.content[:200] + "..." if len(p.content) > 200 else p.content,
                "board_type": p.board_type,
                "tags": [tag.name for tag in p.tags] if p.tags else [],
                "summary": p.summary
            }
            for p in user_posts
        ]
        
        # 최근 댓글 (최대 10개)
        user_comments = db.query(Comment).filter(Comment.user_id == user_id).order_by(Comment.created_at.desc()).limit(10).all()
        context["recent_comments"] = [
            {
                "id": c.id,
                "post_id": c.post_id,
                "content": c.content[:100] + "..." if len(c.content) > 100 else c.content
            }
            for c in user_comments
        ]
    else:
        # 메모리 기반 (기존 방식, 하위 호환성)
        from app.models.memory import POSTS, USERS, COMMENTS
        
        user = USERS.get(user_id)
        if user:
            context["user_info"] = {
                "nickname": user.nickname,
                "email": user.email
            }
        
        user_posts = [p for p in POSTS.values() if p.user_id == user_id]
        user_posts.sort(key=lambda x: x.id, reverse=True)
        context["recent_posts"] = [
            {
                "id": p.id,
                "title": p.title,
                "content": p.content[:200] + "..." if len(p.content) > 200 else p.content,
                "board_type": p.board_type,
                "tags": p.tags if hasattr(p, 'tags') else [],
                "summary": p.summary if hasattr(p, 'summary') else None
            }
            for p in user_posts[:10]
        ]
        
        user_comments = [c for c in COMMENTS.values() if c.user_id == user_id]
        user_comments.sort(key=lambda x: x.id, reverse=True)
        context["recent_comments"] = [
            {
                "id": c.id,
                "post_id": c.post_id,
                "content": c.content[:100] + "..." if len(c.content) > 100 else c.content
            }
            for c in user_comments[:10]
        ]
    
    # 요약 생성
    if context["recent_posts"]:
        post_summaries = [p.get("summary") or p.get("content", "")[:100] for p in context["recent_posts"][:5]]
        context["summary"] = "\n".join(post_summaries)
    
    return context


def build_rag_prompt(
    user_message: str,
    context: Dict,
    include_context: bool = True,
    user_id: Optional[int] = None,
    db: Session = None
) -> str:
    """
    RAG 기반 프롬프트 생성 (Vector DB 검색 포함)
    
    Args:
        user_message: 사용자 메시지
        context: 기본 컨텍스트
        include_context: 컨텍스트 포함 여부
        user_id: 사용자 ID (Vector DB 검색용)
    """
    system_prompt = """당신은 AI Wedding Planner OS의 전문 웨딩 플래너 챗봇입니다.
사용자의 개인 데이터(게시판, 예산, 일정)를 분석하여 맞춤형 조언을 제공합니다.

**CRITICAL: You MUST respond ONLY in Korean (한글). All responses must be in Korean language. 
절대 규칙: 모든 답변은 반드시 한글로만 작성해야 합니다. 영어나 다른 언어를 절대 사용하지 마세요.**

주요 기능:
1. 개인 DB 기반 상담: 사용자의 게시판/예산/일정 데이터를 읽고 분석
2. 감정 분석 & 갈등 코칭: 스트레스 지수 분석 및 심리 코칭
3. 웨딩홀 탐색·추천: 조건 기반 추천 및 비교
4. 게시판/일정/예산 통합 관리: 리뷰 요약, 일정 기반 플랜 업데이트

항상 친절하고 전문적인 톤으로 한글로 답변하세요."""

    context_parts = []
    
    if include_context:
        # 1. 사용자 정보
        if context.get("user_info"):
            user_info = context["user_info"]
            context_parts.append(f"""[사용자 정보]
- 닉네임: {user_info.get('nickname', '알 수 없음')}""")
        
        # 2. Vector DB 기반 게시판 검색 (질문과 관련된 게시글)
        try:
            relevant_posts = post_vector_service.search_posts(
                query=user_message,
                k=3,
                user_id=user_id
            )
            if relevant_posts:
                context_parts.append(f"""[관련 게시글] (Vector DB 검색 결과)
""")
                for i, post_result in enumerate(relevant_posts, 1):
                    metadata = post_result.get("metadata", {})
                    content = post_result.get("content", "")[:200]
                    context_parts.append(f"""{i}. [{metadata.get('board_type', 'couple')}] {metadata.get('title', '제목 없음')}
   내용: {content}...
   유사도: {post_result.get('score', 0):.3f}""")
        except Exception as e:
            print(f"⚠️ Vector DB 게시판 검색 실패: {e}")
        
        # 3. 사용자 메모리 검색 (사용자 선호도/패턴)
        if user_id:
            try:
                user_memories = user_memory_service.search_user_memory(
                    user_id=user_id,
                    query=user_message,
                    k=3
                )
                if user_memories:
                    context_parts.append(f"""[사용자 선호도/패턴] (User Memory)
""")
                    for i, memory in enumerate(user_memories, 1):
                        pref_type = memory.get("metadata", {}).get("preference_type", "general")
                        content = memory.get("content", "")[:150]
                        context_parts.append(f"""{i}. [{pref_type}] {content}...""")
            except Exception as e:
                print(f"⚠️ 사용자 메모리 검색 실패: {e}")
        
        # 4. 채팅 메모리 검색 (사용자가 저장한 대화 내용)
        if user_id and db:
            try:
                user = db.query(User).filter(User.id == user_id).first()
                couple_id = user.couple_id if user else None
                
                chat_memories = chat_memory_vector_service.search_chat_memories(
                    query=user_message,
                    user_id=user_id,
                    k=3,
                    include_shared=True,
                    couple_id=couple_id
                )
                if chat_memories:
                    context_parts.append(f"""[저장된 대화 메모리] (Chat Memory)
""")
                    for i, memory in enumerate(chat_memories, 1):
                        metadata = memory.get("metadata", {})
                        title = metadata.get("title", "제목 없음")
                        content = memory.get("content", "")[:150]
                        context_parts.append(f"""{i}. [{title}] {content}...""")
            except Exception as e:
                print(f"⚠️ 채팅 메모리 검색 실패: {e}")
        
        # 4. 최근 게시글 (기존 방식 유지)
        if context.get("recent_posts"):
            context_parts.append(f"""[최근 게시글] (총 {len(context.get('recent_posts', []))}개)
""")
            for i, post in enumerate(context.get("recent_posts", [])[:5], 1):
                context_parts.append(f"""{i}. [{post.get('board_type', 'couple')}] {post.get('title', '제목 없음')}
   내용: {post.get('content', '')[:150]}...""")
                if post.get("tags"):
                    context_parts[-1] += f"\n   태그: {', '.join(post.get('tags', []))}"
        
        # 5. 최근 댓글
        if context.get("recent_comments"):
            context_parts.append(f"""[최근 댓글] (총 {len(context.get('recent_comments', []))}개)
""")
            for i, comment in enumerate(context.get("recent_comments", [])[:3], 1):
                context_parts.append(f"""{i}. {comment.get('content', '')[:100]}...""")
    
    # 프롬프트 조합
    if context_parts:
        context_text = "\n\n".join(context_parts)
        full_prompt = f"""{system_prompt}

{context_text}

[사용자 질문]
{user_message}

**CRITICAL: You MUST respond ONLY in Korean (한글). Do NOT use English or any other language.
중요: 위 질문에 대한 답변을 반드시 한글로만 작성해주세요. 영어나 다른 언어를 절대 사용하지 마세요.**

위의 사용자 정보, 관련 게시글, 사용자 선호도를 참고하여 개인 맞춤형 답변을 한글로 제공해주세요."""
    else:
        full_prompt = f"""{system_prompt}

[사용자 질문]
{user_message}

**중요: 위 질문에 대한 답변을 반드시 한글로만 작성해주세요. 영어나 다른 언어를 사용하지 마세요.**

친절하고 전문적으로 한글로 답변해주세요."""

    return full_prompt


async def chat_stream(
    message: str,
    user_id: int,
    include_context: bool = True,
    db: Session = None,
    model: str | None = None
) -> AsyncGenerator[str, None]:
    """챗봇 스트리밍 응답 생성"""
    try:
        # 감정 분석 (선택적)
        sentiment_result = None
        if any(keyword in message.lower() for keyword in ['스트레스', '힘들', '갈등', '문제', '걱정']):
            sentiment_result = await analyze_sentiment(message, explain=True)
            if sentiment_result:
                yield json.dumps({
                    "type": "sentiment",
                    "data": sentiment_result
                }) + "\n"
        
        # 개인 데이터 수집
        context = {}
        if include_context:
            context = await get_user_context(user_id, db)
        
        # RAG 프롬프트 생성 (Vector DB 검색 포함)
        prompt = build_rag_prompt(message, context, include_context, user_id, db)
        
        # 모델 API 호출 (스트리밍)
        # 선택된 모델 또는 환경 변수에서 모델 선택 (기본값: gemini-2.5-flash)
        import os
        from app.services.model_config import get_model_by_id, get_default_model_for_category
        
        # 모델 선택: 요청에서 전달된 모델 > 환경 변수 > 기본값
        if model:
            selected_model = model
        else:
            chat_model = os.getenv("CHAT_MODEL", "gemini-2.5-flash")
            selected_model = chat_model
        
        base_url = get_model_api_base_url()
        
        # Gemini 모델인 경우 Gemini 엔드포인트 사용
        if selected_model.startswith("gemini"):
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{base_url}/gemini/chat",
                    json={"message": prompt, "model": selected_model},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            # 모델 응답을 그대로 전달
                            yield json.dumps(data) + "\n"
                        except json.JSONDecodeError:
                            pass
        else:
            # Ollama 모델인 경우 기존 엔드포인트 사용
            # DeepSeek R1은 응답이 매우 느릴 수 있으므로 타임아웃을 늘림
            timeout = 600.0 if selected_model.startswith("deepseek-r1") else 120.0
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{base_url}/chat",
                    json={"message": prompt, "model": selected_model},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            # 모델 응답을 그대로 전달
                            yield json.dumps(data) + "\n"
                        except json.JSONDecodeError:
                            pass
        
    except Exception as e:
        error_msg = f"챗봇 응답 생성 중 오류가 발생했습니다: {str(e)}"
        yield json.dumps({
            "type": "error",
            "content": error_msg
        }) + "\n"


async def chat_simple(
    message: str,
    user_id: int,
    include_context: bool = True,
    db: Session = None
) -> Dict:
    """챗봇 단순 응답 (비스트리밍)"""
    try:
        # 개인 데이터 수집
        context = {}
        if include_context:
            context = await get_user_context(user_id, db)
        
        # RAG 프롬프트 생성 (Vector DB 검색 포함)
        prompt = build_rag_prompt(message, context, include_context, user_id, db)
        
        # 모델 API 호출
        # 환경 변수에서 모델 선택 (기본값: gemma3:4b, Gemini 사용 시: gemini-2.5-flash)
        import os
        chat_model = os.getenv("CHAT_MODEL", "gemma3:4b")
        response_text = await chat_with_model(prompt, model=chat_model)
        
        if not response_text:
            return {
                "message": "error",
                "data": {"error": "응답 생성에 실패했습니다."}
            }
        
        return {
            "message": "chat_success",
            "data": {
                "response": response_text,
                "context_used": include_context
            }
        }
    except Exception as e:
        return {
            "message": "error",
            "data": {"error": str(e)}
        }





