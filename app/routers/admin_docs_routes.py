"""
관리자 문서 페이지 - API 레퍼런스 및 ERD 뷰어
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

router = APIRouter()

# 프로젝트 루트 디렉토리 (백엔드 디렉토리 기준으로 상위 디렉토리)
# 현재 파일: app/routers/admin_docs_routes.py
# 목표: 1.Wedding_OS_Project/1.Wedding_OS_front/api_reference.html
#      1.Wedding_OS_Project/1.Wedding_OS_front/api_reference_details.html
#      1.Wedding_OS_Project/database_erd_viewer.html
BACKEND_DIR = Path(__file__).parent.parent.parent  # app/ 까지
PROJECT_DIR = BACKEND_DIR.parent  # 1.Wedding_OS_Project/ 까지
API_REF_PATH = PROJECT_DIR / "1.Wedding_OS_front" / "api_reference.html"
API_REF_DETAILS_PATH = PROJECT_DIR / "1.Wedding_OS_front" / "api_reference_details.html"
ERD_PATH = PROJECT_DIR / "database_erd_viewer.html"


def _inject_favicon(html_content: str, base_url: str) -> str:
    """HTML에 favicon 추가"""
    favicon_tag = f'<link rel="icon" type="image/png" href="{base_url}/static/favicon.png">'
    # </head> 태그 앞에 favicon 추가
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', f'    {favicon_tag}\n</head>')
    elif '<head>' in html_content and '</head>' not in html_content:
        # head 태그가 열려있지만 닫히지 않은 경우
        html_content = html_content.replace('<head>', f'<head>\n    {favicon_tag}')
    return html_content


@router.get("/api-reference", response_class=HTMLResponse)
async def api_reference(request: Request):
    """API 레퍼런스 문서 (상세 설명 페이지로 리다이렉트)"""
    # api_reference_details.html로 리다이렉트
    base_url = str(request.base_url).rstrip('/')
    if API_REF_DETAILS_PATH.exists():
        with open(API_REF_DETAILS_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            content = _inject_favicon(content, base_url)
            return HTMLResponse(content=content)
    else:
        return HTMLResponse(
            content=f"<h1>파일을 찾을 수 없습니다</h1><p>경로: {API_REF_DETAILS_PATH}</p>",
            status_code=404
        )


@router.get("/api-reference/details", response_class=HTMLResponse)
async def api_reference_details(request: Request):
    """API 레퍼런스 상세 설명 문서"""
    base_url = str(request.base_url).rstrip('/')
    if API_REF_DETAILS_PATH.exists():
        with open(API_REF_DETAILS_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            content = _inject_favicon(content, base_url)
            return HTMLResponse(content=content)
    else:
        return HTMLResponse(
            content=f"<h1>파일을 찾을 수 없습니다</h1><p>경로: {API_REF_DETAILS_PATH}</p>",
            status_code=404
        )


@router.get("/erd", response_class=HTMLResponse)
async def erd_viewer(request: Request):
    """데이터베이스 ERD 뷰어"""
    base_url = str(request.base_url).rstrip('/')
    if ERD_PATH.exists():
        with open(ERD_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            content = _inject_favicon(content, base_url)
            return HTMLResponse(content=content)
    else:
        return HTMLResponse(
            content=f"<h1>파일을 찾을 수 없습니다</h1><p>경로: {ERD_PATH}</p>",
            status_code=404
        )

