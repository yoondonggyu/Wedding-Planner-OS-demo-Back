"""
챗봇 서비스 - RAG + 개인 데이터 통합
"""
import json
from typing import AsyncGenerator, Dict, List, Optional
from app.models.memory import POSTS, USERS, COMMENTS
from app.services.model_client import chat_with_model, analyze_sentiment, get_model_api_base_url
import httpx


async def get_user_context(user_id: int) -> Dict:
    """사용자의 개인 데이터 수집 (캘린더/예산/게시판)"""
    context = {
        "user_info": None,
        "recent_posts": [],
        "recent_comments": [],
        "summary": ""
    }
    
    # 사용자 정보
    user = USERS.get(user_id)
    if user:
        context["user_info"] = {
            "nickname": user.nickname,
            "email": user.email
        }
    
    # 최근 게시글 (최대 10개)
    user_posts = [p for p in POSTS.values() if p.user_id == user_id]
    user_posts.sort(key=lambda x: x.id, reverse=True)
    context["recent_posts"] = [
        {
            "id": p.id,
            "title": p.title,
            "content": p.content[:200] + "..." if len(p.content) > 200 else p.content,
            "board_type": p.board_type,
            "tags": p.tags,
            "summary": p.summary
        }
        for p in user_posts[:10]
    ]
    
    # 최근 댓글 (최대 10개)
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


def build_rag_prompt(user_message: str, context: Dict, include_context: bool = True) -> str:
    """RAG 기반 프롬프트 생성"""
    system_prompt = """당신은 AI Wedding Planner OS의 전문 웨딩 플래너 챗봇입니다.
사용자의 개인 데이터(게시판, 예산, 일정)를 분석하여 맞춤형 조언을 제공합니다.

주요 기능:
1. 개인 DB 기반 상담: 사용자의 게시판/예산/일정 데이터를 읽고 분석
2. 감정 분석 & 갈등 코칭: 스트레스 지수 분석 및 심리 코칭
3. 웨딩홀 탐색·추천: 조건 기반 추천 및 비교
4. 게시판/일정/예산 통합 관리: 리뷰 요약, 일정 기반 플랜 업데이트

항상 친절하고 전문적인 톤으로 답변하세요."""

    if include_context and context.get("user_info"):
        user_info = context["user_info"]
        context_text = f"""
[사용자 정보]
- 닉네임: {user_info.get('nickname', '알 수 없음')}

[최근 게시글] (총 {len(context.get('recent_posts', []))}개)
"""
        for i, post in enumerate(context.get("recent_posts", [])[:5], 1):
            context_text += f"{i}. [{post.get('board_type', 'couple')}] {post.get('title', '제목 없음')}\n"
            if post.get("content"):
                context_text += f"   내용: {post.get('content', '')[:150]}...\n"
            if post.get("tags"):
                context_text += f"   태그: {', '.join(post.get('tags', []))}\n"
        
        if context.get("recent_comments"):
            context_text += f"\n[최근 댓글] (총 {len(context.get('recent_comments', []))}개)\n"
            for i, comment in enumerate(context.get("recent_comments", [])[:3], 1):
                context_text += f"{i}. {comment.get('content', '')[:100]}...\n"
        
        full_prompt = f"""{system_prompt}

{context_text}

[사용자 질문]
{user_message}

위의 사용자 정보와 최근 활동을 참고하여 개인 맞춤형 답변을 제공해주세요."""
    else:
        full_prompt = f"""{system_prompt}

[사용자 질문]
{user_message}

친절하고 전문적으로 답변해주세요."""

    return full_prompt


async def chat_stream(
    message: str,
    user_id: int,
    include_context: bool = True
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
            context = await get_user_context(user_id)
        
        # RAG 프롬프트 생성
        prompt = build_rag_prompt(message, context, include_context)
        
        # 모델 API 호출 (스트리밍)
        base_url = get_model_api_base_url()
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/chat",
                json={"message": prompt, "model": "gemma3:4b"},
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
    include_context: bool = True
) -> Dict:
    """챗봇 단순 응답 (비스트리밍)"""
    try:
        # 개인 데이터 수집
        context = {}
        if include_context:
            context = await get_user_context(user_id)
        
        # RAG 프롬프트 생성
        prompt = build_rag_prompt(message, context, include_context)
        
        # 모델 API 호출
        response_text = await chat_with_model(prompt, model="gemma3:4b")
        
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


