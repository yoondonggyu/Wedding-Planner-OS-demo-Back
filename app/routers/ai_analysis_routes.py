"""
AI 분석 API 라우터
단일 텍스트에 대한 감성 분석, 요약, 태그 생성
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.security import get_current_user_id_optional
from app.services.model_client import analyze_sentiment, summarize_text, auto_tag_text
from typing import Optional

router = APIRouter(tags=["AI Analysis"])


class AnalyzeTextRequest(BaseModel):
    text: str


class AnalyzeTextResponse(BaseModel):
    sentiment: Optional[dict] = None
    summary: Optional[str] = None
    tags: Optional[list] = None


@router.post("/model/analyze", response_model=AnalyzeTextResponse)
async def analyze_text_endpoint(
    request: AnalyzeTextRequest,
    user_id: Optional[int] = Depends(get_current_user_id_optional)
):
    """
    단일 텍스트에 대한 AI 분석 (감성 분석, 요약, 태그)
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="텍스트를 입력해주세요.")
    
    try:
        # 병렬로 모든 분석 수행
        sentiment_result = None
        summary_result = None
        tags_result = None
        
        # 감성 분석
        try:
            sentiment_res = await analyze_sentiment(request.text)
            if sentiment_res:
                sentiment_result = {
                    "label": sentiment_res.get("label", "neutral"),
                    "confidence": sentiment_res.get("confidence", 0.5)
                }
        except Exception as e:
            print(f"⚠️ 감성 분석 실패: {e}")
        
        # 요약
        try:
            summary_res = await summarize_text(request.text)
            if summary_res:
                summary_result = summary_res.get("summary")
        except Exception as e:
            print(f"⚠️ 요약 실패: {e}")
        
        # 태그 생성
        try:
            tags_list = await auto_tag_text(request.text)
            if tags_list:
                tags_result = tags_list
        except Exception as e:
            print(f"⚠️ 태그 생성 실패: {e}")
        
        return AnalyzeTextResponse(
            sentiment=sentiment_result,
            summary=summary_result,
            tags=tags_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석 실패: {str(e)}")


@router.post("/model/sentiment")
async def analyze_sentiment_endpoint(
    request: AnalyzeTextRequest,
    user_id: Optional[int] = Depends(get_current_user_id_optional)
):
    """감성 분석만 수행"""
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="텍스트를 입력해주세요.")
    
    try:
        result = await analyze_sentiment(request.text)
        if not result:
            raise HTTPException(status_code=500, detail="감성 분석에 실패했습니다.")
        return {"message": "sentiment_analysis_success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"감성 분석 실패: {str(e)}")


@router.post("/model/summarize")
async def summarize_text_endpoint(
    request: AnalyzeTextRequest,
    user_id: Optional[int] = Depends(get_current_user_id_optional)
):
    """요약만 수행"""
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="텍스트를 입력해주세요.")
    
    try:
        result = await summarize_text(request.text)
        if not result:
            raise HTTPException(status_code=500, detail="요약에 실패했습니다.")
        return {"message": "summarize_success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 실패: {str(e)}")


@router.post("/model/auto-tag")
async def auto_tag_endpoint(
    request: AnalyzeTextRequest,
    user_id: Optional[int] = Depends(get_current_user_id_optional)
):
    """태그 생성만 수행"""
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="텍스트를 입력해주세요.")
    
    try:
        result = await auto_tag_text(request.text)
        if result is None:
            result = []
        return {"message": "auto_tag_success", "data": {"tags": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"태그 생성 실패: {str(e)}")


