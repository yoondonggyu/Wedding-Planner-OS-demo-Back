"""
관리자 문서 페이지 - API 레퍼런스 및 ERD 뷰어
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import os

router = APIRouter()

# 프로젝트 루트 디렉토리 (백엔드 디렉토리 기준으로 상위 디렉토리)
# 현재 파일: app/routers/admin_docs_routes.py
# 목표: 1.Wedding_OS_Project/1.Wedding_OS_front/api_reference.html
#      1.Wedding_OS_Project/database_erd_viewer.html
BACKEND_DIR = Path(__file__).parent.parent.parent  # app/ 까지
PROJECT_DIR = BACKEND_DIR.parent  # 1.Wedding_OS_Project/ 까지
API_REF_PATH = PROJECT_DIR / "1.Wedding_OS_front" / "api_reference.html"
ERD_PATH = PROJECT_DIR / "database_erd_viewer.html"


@router.get("/api-reference", response_class=HTMLResponse)
async def api_reference():
    """API 레퍼런스 문서"""
    if API_REF_PATH.exists():
        with open(API_REF_PATH, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(
            content=f"<h1>파일을 찾을 수 없습니다</h1><p>경로: {API_REF_PATH}</p>",
            status_code=404
        )


@router.get("/erd", response_class=HTMLResponse)
async def erd_viewer():
    """데이터베이스 ERD 뷰어"""
    if ERD_PATH.exists():
        with open(ERD_PATH, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(
            content=f"<h1>파일을 찾을 수 없습니다</h1><p>경로: {ERD_PATH}</p>",
            status_code=404
        )

