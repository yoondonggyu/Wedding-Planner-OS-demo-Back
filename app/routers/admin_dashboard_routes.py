"""
관리자 대시보드 - 모든 관리자 도구에 접근할 수 있는 통합 페이지
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import socket
import subprocess
from typing import Dict

router = APIRouter()


def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """포트가 열려있는지 확인"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def check_service_status() -> Dict[str, bool]:
    """서비스 상태 확인"""
    return {
        "backend": check_port("localhost", 8101),
        "frontend": check_port("localhost", 5173) or check_port("localhost", 5174),
        "database": check_port("localhost", 3306),
    }


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """관리자 대시보드 메인 페이지"""
    
    # 현재 호스트와 포트 자동 감지
    base_url = str(request.base_url).rstrip('/')
    host = request.url.hostname
    port = request.url.port or 8101
    
    # 로고 URL 생성 (정적 파일로 서빙)
    logo_url = f"{base_url}/static/favicon.png"
    
    # 서비스 상태 확인
    service_status = check_service_status()
    backend_status = "🟢 실행 중" if service_status["backend"] else "🔴 중지"
    frontend_status = "🟢 실행 중" if service_status["frontend"] else "🔴 중지"
    db_status = "🟢 실행 중" if service_status["database"] else "🔴 중지"
    
    # 전체 상태
    all_running = all(service_status.values())
    system_status_text = "시스템 정상 작동 중" if all_running else "일부 서비스 중지"
    system_status_class = "status-ok" if all_running else "status-warning"
    
    # API 레퍼런스와 ERD는 상대 경로로 접근 (프론트엔드 디렉토리 기준)
    # 실제 파일 경로는 프론트엔드 서버에서 서빙되어야 함
    # 여기서는 상대 경로로 설정하고, 필요시 절대 경로로 변경 가능
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wedding OS - 관리자 대시보드</title>
        <link rel="icon" type="image/png" href="{logo_url}">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            .header {{
                text-align: center;
                color: white;
                margin-bottom: 40px;
                padding: 30px 0;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .header p {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .card {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                cursor: pointer;
                text-decoration: none;
                color: inherit;
                display: block;
            }}
            
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
            }}
            
            .card-icon {{
                font-size: 3em;
                margin-bottom: 15px;
                text-align: center;
            }}
            
            .card-title {{
                font-size: 1.5em;
                font-weight: 600;
                margin-bottom: 10px;
                color: #333;
                text-align: center;
            }}
            
            .card-description {{
                color: #666;
                text-align: center;
                line-height: 1.6;
                font-size: 0.95em;
            }}
            
            .card-url {{
                margin-top: 15px;
                padding: 8px 12px;
                background: #f5f5f5;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 0.85em;
                color: #666;
                word-break: break-all;
                text-align: center;
            }}
            
            .info-section {{
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-top: 20px;
            }}
            
            .info-section h2 {{
                color: #333;
                margin-bottom: 15px;
                font-size: 1.3em;
            }}
            
            .info-section p {{
                color: #666;
                line-height: 1.8;
                margin-bottom: 10px;
            }}
            
            .info-section code {{
                background: #f5f5f5;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                color: #e83e8c;
            }}
            
            .status-indicator {{
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #28a745;
                margin-right: 8px;
                animation: pulse 2s infinite;
            }}
            
            .status-ok .status-indicator {{
                background: #28a745;
            }}
            
            .status-warning .status-indicator {{
                background: #f59e0b;
            }}
            
            .service-status {{
                display: flex;
                gap: 20px;
                margin-top: 12px;
                flex-wrap: wrap;
                justify-content: center;
            }}
            
            .service-status-item {{
                padding: 8px 16px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                font-size: 14px;
            }}
            
            @keyframes pulse {{
                0% {{
                    opacity: 1;
                }}
                50% {{
                    opacity: 0.5;
                }}
                100% {{
                    opacity: 1;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{logo_url}" alt="Wedding OS Logo" style="width: 80px; height: 80px; margin-bottom: 16px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);" />
                <h1>🎯 Wedding OS 관리자 대시보드</h1>
                <p class="{system_status_class}"><span class="status-indicator"></span>{system_status_text}</p>
                <div class="service-status">
                    <div class="service-status-item">백엔드: {backend_status}</div>
                    <div class="service-status-item">프론트엔드: {frontend_status}</div>
                    <div class="service-status-item">데이터베이스: {db_status}</div>
                </div>
            </div>
            
            <div class="dashboard-grid">
                <a href="{base_url}/secret_admin/" class="card" target="_blank">
                    <div class="card-icon">📊</div>
                    <div class="card-title">데이터베이스 관리</div>
                    <div class="card-description">
                        SQLAdmin을 통한 데이터베이스 테이블 관리<br>
                        사용자, 게시글, 댓글, 일정 등 모든 데이터 조회 및 수정
                    </div>
                    <div class="card-url">{base_url}/secret_admin/</div>
                </a>
                
                <a href="{base_url}/secret_admin/sql-terminal" class="card" target="_blank">
                    <div class="card-icon">💻</div>
                    <div class="card-title">SQL 터미널</div>
                    <div class="card-description">
                        직접 SQL 쿼리를 실행하여 데이터베이스 관리<br>
                        SELECT, INSERT, UPDATE, DELETE 쿼리 실행 가능
                    </div>
                    <div class="card-url">{base_url}/secret_admin/sql-terminal</div>
                </a>
                
                <a href="{base_url}/docs" class="card" target="_blank">
                    <div class="card-icon">📚</div>
                    <div class="card-title">API 문서 (Swagger)</div>
                    <div class="card-description">
                        FastAPI 자동 생성 API 문서<br>
                        모든 엔드포인트의 상세 정보 및 테스트 가능
                    </div>
                    <div class="card-url">{base_url}/docs</div>
                </a>
                
                <a href="{base_url}/secret_admin/api-reference" class="card" target="_blank">
                    <div class="card-icon">📖</div>
                    <div class="card-title">API 레퍼런스</div>
                    <div class="card-description">
                        상세한 API 명세서<br>
                        요청/응답 형식, 에러 코드 등 전체 API 문서
                    </div>
                    <div class="card-url">{base_url}/secret_admin/api-reference</div>
                </a>
                
                <a href="{base_url}/secret_admin/erd" class="card" target="_blank">
                    <div class="card-icon">🗄️</div>
                    <div class="card-title">데이터베이스 ERD</div>
                    <div class="card-description">
                        데이터베이스 구조 시각화<br>
                        테이블 관계 및 스키마 다이어그램
                    </div>
                    <div class="card-url">{base_url}/secret_admin/erd</div>
                </a>
                
                <a href="{base_url}/secret_admin/dashboard/userauthsetting" class="card" target="_blank">
                    <div class="card-icon">👥</div>
                    <div class="card-title">사용자 권한 설정</div>
                    <div class="card-description">
                        사용자 역할 및 권한 관리<br>
                        시스템 관리자, 웹 관리자, 업체 관리자 등 역할 설정
                    </div>
                    <div class="card-url">{base_url}/secret_admin/dashboard/userauthsetting</div>
                </a>
                
                <a href="{base_url}/secret_admin/dashboard/vendor-management" class="card" target="_blank">
                    <div class="card-icon">🏢</div>
                    <div class="card-title">벤더 관리</div>
                    <div class="card-description">
                        벤더 업체 목록 관리<br>
                        카테고리별 벤더 추가, 수정, 삭제
                    </div>
                    <div class="card-url">{base_url}/secret_admin/dashboard/vendor-management</div>
                </a>
                
                <a href="{base_url}/secret_admin/dashboard/vendor-approval" class="card" target="_blank">
                    <div class="card-icon">✅</div>
                    <div class="card-title">제휴 업체 승인 관리</div>
                    <div class="card-description">
                        제휴 업체 가입 신청 승인/거부<br>
                        승인 대기 중인 제휴 업체 목록 관리
                    </div>
                    <div class="card-url">{base_url}/secret_admin/dashboard/vendor-approval</div>
                </a>
                
                <a href="{base_url}/secret_admin/dashboard/admin-approval" class="card" target="_blank">
                    <div class="card-icon">👨‍💼</div>
                    <div class="card-title">관리자 승인 관리</div>
                    <div class="card-description">
                        관리자 역할 승인 및 거부<br>
                        승인 대기 중인 관리자 목록 관리
                    </div>
                    <div class="card-url">{base_url}/secret_admin/dashboard/admin-approval</div>
                </a>
            </div>
            
            <div class="info-section">
                <h2>ℹ️ 시스템 정보</h2>
                <p><strong>서버 주소:</strong> <code>{host}:{port}</code></p>
                <p><strong>기본 URL:</strong> <code>{base_url}</code></p>
                <p><strong>API 엔드포인트:</strong> <code>{base_url}/api</code></p>
                <p><strong>관리자 페이지:</strong> <code>{base_url}/secret_admin</code></p>
                <p style="margin-top: 15px; color: #888; font-size: 0.9em;">
                    💡 <strong>팁:</strong> IP나 포트가 변경되어도 이 페이지는 자동으로 현재 주소를 감지합니다.
                </p>
            </div>
        </div>
        
        <script>
            // 쿼리 파라미터에서 토큰 가져와서 localStorage에 저장
            const urlParams = new URLSearchParams(window.location.search);
            const tokenFromQuery = urlParams.get('token');
            if (tokenFromQuery) {{
                localStorage.setItem('wedding_access_token', tokenFromQuery);
                localStorage.setItem('access_token', tokenFromQuery);
                // URL에서 토큰 제거 (보안)
                const newUrl = window.location.pathname;
                window.history.replaceState({{}}, '', newUrl);
            }}
            
            // 모든 관리자 페이지 링크에 토큰 추가
            document.addEventListener('DOMContentLoaded', function() {{
                const token = localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || '';
                if (token) {{
                    const links = document.querySelectorAll('.dashboard-grid a[href*="/secret_admin/"]');
                    links.forEach(link => {{
                        const href = link.getAttribute('href');
                        if (href && !href.includes('token=')) {{
                            const separator = href.includes('?') ? '&' : '?';
                            link.setAttribute('href', `${{href}}${{separator}}token=${{encodeURIComponent(token)}}`);
                        }}
                    }});
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

