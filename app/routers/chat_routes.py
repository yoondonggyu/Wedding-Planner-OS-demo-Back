from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.schemas import ChatRequest
from app.controllers import chat_controller
from app.core.database import get_db, SessionLocal
from app.core.security import get_current_user_id, verify_token
from typing import Optional
import json

router = APIRouter(tags=["chat"])

@router.websocket("/chat/ws")
async def chat_websocket(
    websocket: WebSocket,
    token: str = Query(...)
):
    """챗봇 WebSocket API - RAG + 개인 데이터 통합 + Vector DB 검색"""
    # JWT 토큰 검증
    try:
        payload = verify_token(token)
        if not payload:
            await websocket.close(code=1008, reason="Invalid token")
            return
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
        user_id = int(user_id)
    except Exception as e:
        await websocket.close(code=1008, reason="Token verification failed")
        return
    
    # WebSocket 연결 수락
    await websocket.accept()
    
    # DB 세션 생성
    db = SessionLocal()
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                message = message_data.get("message", "")
                include_context = message_data.get("include_context", True)
                model = message_data.get("model", None)
                
                if not message:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "content": "메시지가 비어있습니다."
                    }))
                    continue
                
                # 감정 분석 (선택적)
                sentiment_result = None
                if any(keyword in message.lower() for keyword in ['스트레스', '힘들', '갈등', '문제', '걱정']):
                    from app.services.model_client import analyze_sentiment
                    sentiment_result = await analyze_sentiment(message, explain=True)
                    if sentiment_result:
                        await websocket.send_text(json.dumps({
                            "type": "sentiment",
                            "data": sentiment_result
                        }))
                
                # 채팅 스트림 처리
                async for chunk in chat_controller.chat_stream(
                    message=message,
                    user_id=user_id,
                    include_context=include_context,
                    db=db,
                    model=model
                ):
                    # NDJSON 형식의 chunk를 파싱하여 WebSocket으로 전송
                    if chunk.strip():
                        try:
                            # chunk는 이미 JSON 문자열이므로 그대로 전송
                            await websocket.send_text(chunk.strip())
                        except Exception as e:
                            # 전송 실패 시 에러 메시지
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "content": "응답 처리 중 오류가 발생했습니다."
                            }))
                
                # 스트리밍 완료 신호 전송
                await websocket.send_text(json.dumps({
                    "type": "end"
                }))
                            
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": "잘못된 메시지 형식입니다."
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": f"오류가 발생했습니다: {str(e)}"
                }))
                
    except WebSocketDisconnect:
        # 클라이언트가 연결을 끊은 경우
        pass
    except Exception as e:
        # 기타 오류 발생 시
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": f"연결 오류: {str(e)}"
            }))
        except:
            pass
        await websocket.close()
    finally:
        # DB 세션 종료
        db.close()

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """챗봇 대화 API - RAG + 개인 데이터 통합 + Vector DB 검색 (HTTP Streaming)"""
    return StreamingResponse(
        chat_controller.chat_stream(
            message=request.message,
            user_id=user_id,
            include_context=request.include_context,
            db=db,
            model=request.model
        ),
        media_type="application/x-ndjson"
    )

@router.post("/chat/simple")
async def chat_simple(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """챗봇 대화 API (비스트리밍) - RAG + 개인 데이터 통합 + Vector DB 검색"""
    response = await chat_controller.chat_simple(
        message=request.message,
        user_id=user_id,
        include_context=request.include_context,
        db=db
    )
    return response





