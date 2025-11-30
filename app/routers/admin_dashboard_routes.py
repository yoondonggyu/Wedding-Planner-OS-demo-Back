"""
관리자 대시보드 - 모든 관리자 도구에 접근할 수 있는 통합 페이지
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """관리자 대시보드 메인 페이지"""
    
    # 현재 호스트와 포트 자동 감지
    base_url = str(request.base_url).rstrip('/')
    host = request.url.hostname
    port = request.url.port or 8101
    
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
                <h1>🎯 Wedding OS 관리자 대시보드</h1>
                <p><span class="status-indicator"></span>시스템 정상 작동 중</p>
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
            // 현재 호스트와 포트 정보 표시용
            const currentHost = window.location.hostname;
            const currentPort = window.location.port || '8101';
            const protocol = window.location.protocol;
            
            console.log('현재 호스트:', currentHost);
            console.log('현재 포트:', currentPort);
            console.log('현재 프로토콜:', protocol);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

