"""
SQL 터미널 - FastAPI 라우터로 구현된 관리자 페이지용 SQL 쿼리 실행 인터페이스
"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from app.core.database import engine
import time

router = APIRouter()


def _render_results(results: dict) -> str:
    """쿼리 결과를 HTML 테이블로 렌더링"""
    if not results:
        return ""
    
    if "message" in results:
        return f'<div class="results"><div class="success">{results["message"]}</div></div>'
    
    if "columns" not in results or "rows" not in results:
        return ""
    
    columns = results["columns"]
    rows = results["rows"]
    
    if not rows:
        return '<div class="results"><div class="success">쿼리 실행 완료. 반환된 행이 없습니다.</div></div>'
    
    # 테이블 HTML 생성
    table_html = '<div class="results">'
    table_html += f'<div class="results-header"><strong>{len(rows)}개 행 반환</strong></div>'
    table_html += '<div class="results-table"><table><thead><tr>'
    
    for col in columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr></thead><tbody>'
    
    for row in rows:
        table_html += '<tr>'
        for col in columns:
            value = row.get(col, '')
            # None 값 처리
            if value is None:
                value = '<em style="color: #999;">NULL</em>'
            # 긴 텍스트는 잘라서 표시
            elif isinstance(value, str) and len(value) > 100:
                value = value[:100] + '...'
            # HTML 이스케이프
            if isinstance(value, str):
                value = value.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            table_html += f'<td>{value}</td>'
        table_html += '</tr>'
    
    table_html += '</tbody></table></div></div>'
    
    return table_html


async def _execute_query(query: str) -> dict:
    """SQL 쿼리 실행"""
    if not query or not query.strip():
        return {"error": "쿼리가 비어있습니다."}
    
    try:
        query_upper = query.upper().strip()
        
        # 매우 위험한 쿼리만 차단 (DROP, TRUNCATE, ALTER TABLE 등)
        very_dangerous_keywords = [
            "DROP TABLE", "DROP DATABASE", "TRUNCATE", 
            "ALTER TABLE", "CREATE TABLE", "CREATE DATABASE",
            "GRANT", "REVOKE", "EXEC", "EXECUTE", "CALL"
        ]
        
        # 매우 위험한 쿼리 체크
        query_upper_for_check = query_upper.replace('\n', ' ').replace('\r', ' ')
        if any(kw in query_upper_for_check for kw in very_dangerous_keywords):
            return {"error": "보안상 DROP, TRUNCATE, ALTER TABLE, CREATE TABLE 등의 쿼리는 실행할 수 없습니다."}
        
        # 모든 쿼리 실행 허용 (SELECT, INSERT, UPDATE, DELETE 등)
        start_time = time.time()
        
        with engine.begin() as conn:  # begin()을 사용하여 자동 커밋
            result = conn.execute(text(query))
            
            if result.returns_rows:
                columns = list(result.keys())
                rows = []
                for row in result:
                    # 각 값을 JSON 직렬화 가능한 형태로 변환
                    row_dict = {}
                    for key, value in row._mapping.items():
                        if value is None:
                            row_dict[key] = None
                        elif isinstance(value, (int, float, str, bool)):
                            row_dict[key] = value
                        else:
                            # datetime 등은 문자열로 변환
                            row_dict[key] = str(value)
                    rows.append(row_dict)
                
                results = {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows)
                }
            else:
                # INSERT, UPDATE, DELETE 등
                affected_rows = result.rowcount if hasattr(result, 'rowcount') else 0
                results = {
                    "message": f"쿼리가 실행되었습니다. {affected_rows}개 행이 영향을 받았습니다.",
                    "row_count": affected_rows
                }
        
        execution_time = round((time.time() - start_time) * 1000, 2)  # ms
        
        return {
            "results": results,
            "execution_time": execution_time
        }
        
    except Exception as e:
        return {"error": str(e)}


@router.get("/sql-terminal", response_class=HTMLResponse)
@router.post("/sql-terminal", response_class=HTMLResponse)
async def sql_terminal(request: Request, query: str = Form(None)):
    """SQL 쿼리 실행 터미널"""
    error = None
    results = None
    execution_time = None
    query_value = ""
    
    # 로고 URL 생성 (정적 파일로 서빙)
    base_url = str(request.base_url).rstrip('/')
    logo_url = f"{base_url}/static/favicon.png"
    
    # POST 요청 처리
    if request.method == "POST" and query:
        query_value = query.strip()
        result = await _execute_query(query_value)
        if "error" in result:
            error = result["error"]
        else:
            results = result.get("results")
            execution_time = result.get("execution_time")
    
    # HTML 템플릿
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SQL 터미널 - Wedding OS Admin</title>
        <link rel="icon" type="image/png" href="{logo_url}">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 24px;
            }}
            h1 {{
                margin: 0 0 24px 0;
                color: #333;
                border-bottom: 2px solid #007bff;
                padding-bottom: 12px;
            }}
            .nav-link {{
                display: inline-block;
                margin-bottom: 20px;
                padding: 8px 16px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-size: 14px;
            }}
            .nav-link:hover {{
                background: #0056b3;
            }}
            .warning {{
                background: #fff3cd;
                border: 1px solid #ffc107;
                color: #856404;
                padding: 12px;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
            .error {{
                background: #f8d7da;
                border: 1px solid #dc3545;
                color: #721c24;
                padding: 12px;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
            .success {{
                background: #d4edda;
                border: 1px solid #28a745;
                color: #155724;
                padding: 12px;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
            form {{
                margin-bottom: 24px;
            }}
            textarea {{
                width: 100%;
                min-height: 200px;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                resize: vertical;
                box-sizing: border-box;
            }}
            textarea:focus {{
                outline: none;
                border-color: #007bff;
                box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
            }}
            .button-group {{
                display: flex;
                gap: 12px;
                margin-top: 12px;
            }}
            button {{
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
            }}
            .btn-primary {{
                background: #007bff;
                color: white;
            }}
            .btn-primary:hover {{
                background: #0056b3;
            }}
            .btn-secondary {{
                background: #6c757d;
                color: white;
            }}
            .btn-secondary:hover {{
                background: #545b62;
            }}
            .results {{
                margin-top: 24px;
            }}
            .results-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
                padding: 12px;
                background: #f8f9fa;
                border-radius: 4px;
            }}
            .results-table {{
                overflow-x: auto;
                border: 1px solid #ddd;
                border-radius: 4px;
                max-height: 500px;
                overflow-y: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}
            th {{
                background: #007bff;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                position: sticky;
                top: 0;
            }}
            td {{
                padding: 10px 12px;
                border-bottom: 1px solid #eee;
            }}
            tr:hover {{
                background: #f8f9fa;
            }}
            .query-examples {{
                margin-top: 24px;
                padding: 16px;
                background: #f8f9fa;
                border-radius: 4px;
            }}
            .query-examples h3 {{
                margin: 0 0 12px 0;
                color: #333;
            }}
            .example-query {{
                background: white;
                padding: 8px 12px;
                margin: 8px 0;
                border-left: 3px solid #007bff;
                cursor: pointer;
                border-radius: 2px;
            }}
            .example-query:hover {{
                background: #e7f3ff;
            }}
            .example-query code {{
                font-family: 'Courier New', monospace;
                color: #007bff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/secret_admin/" class="nav-link">← Admin 페이지로 돌아가기</a>
            <h1>🔧 SQL 터미널</h1>
            
            <div class="warning">
                <strong>⚠️ 주의:</strong> 관리자 전용 SQL 터미널입니다. 
                SELECT, INSERT, UPDATE, DELETE 쿼리를 실행할 수 있습니다. 
                DROP, TRUNCATE, ALTER TABLE 등의 매우 위험한 쿼리는 차단됩니다.
            </div>
            
            {f'<div class="error"><strong>❌ 오류:</strong> {error}</div>' if error else ''}
            {f'<div class="success"><strong>✅ 성공:</strong> {execution_time}ms 소요, {results.get("row_count", 0) if results else 0}개 행 반환</div>' if results and not error else ''}
            
            <form method="POST">
                <textarea name="query" placeholder="SQL 쿼리를 입력하세요...&#10;&#10;예: SELECT * FROM users LIMIT 10;">{query_value}</textarea>
                <div class="button-group">
                    <button type="submit" class="btn-primary">실행</button>
                    <button type="button" class="btn-secondary" onclick="document.querySelector('textarea[name=\\'query\\']').value=''">초기화</button>
                </div>
            </form>
            
            {_render_results(results) if results else ''}
            
            <div class="query-examples">
                <h3>📝 예제 쿼리 (클릭하여 사용)</h3>
                
                <h4 style="margin-top: 16px; margin-bottom: 8px; color: #555;">🔍 기본 조회</h4>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM users LIMIT 10;'">
                    <code>SELECT * FROM users LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM posts LIMIT 10;'">
                    <code>SELECT * FROM posts LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM comments LIMIT 10;'">
                    <code>SELECT * FROM comments LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM calendar_events LIMIT 20;'">
                    <code>SELECT * FROM calendar_events LIMIT 20;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM wedding_dates;'">
                    <code>SELECT * FROM wedding_dates;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM wedding_profiles LIMIT 10;'">
                    <code>SELECT * FROM wedding_profiles LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM vendors LIMIT 10;'">
                    <code>SELECT * FROM vendors LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM favorite_vendors LIMIT 10;'">
                    <code>SELECT * FROM favorite_vendors LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM budget_items LIMIT 20;'">
                    <code>SELECT * FROM budget_items LIMIT 20;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM chat_history LIMIT 20;'">
                    <code>SELECT * FROM chat_history LIMIT 20;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM user_total_budgets;'">
                    <code>SELECT * FROM user_total_budgets;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM post_likes LIMIT 20;'">
                    <code>SELECT * FROM post_likes LIMIT 20;</code>
                </div>
                
                <h4 style="margin-top: 20px; margin-bottom: 8px; color: #555;">🔗 JOIN 쿼리</h4>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT p.id, p.title, u.nickname, p.view_count, p.created_at FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.created_at DESC LIMIT 10;'">
                    <code>SELECT p.id, p.title, u.nickname, p.view_count, p.created_at FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.created_at DESC LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT c.id, c.content, u.nickname, p.title FROM comments c JOIN users u ON c.user_id = u.id JOIN posts p ON c.post_id = p.id ORDER BY c.created_at DESC LIMIT 20;'">
                    <code>SELECT c.id, c.content, u.nickname, p.title FROM comments c JOIN users u ON c.user_id = u.id JOIN posts p ON c.post_id = p.id ORDER BY c.created_at DESC LIMIT 20;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT ce.id, ce.title, ce.start_date, u.nickname FROM calendar_events ce JOIN users u ON ce.user_id = u.id WHERE ce.category = \\'event\\' ORDER BY ce.start_date LIMIT 20;'">
                    <code>SELECT ce.id, ce.title, ce.start_date, u.nickname FROM calendar_events ce JOIN users u ON ce.user_id = u.id WHERE ce.category = 'event' ORDER BY ce.start_date LIMIT 20;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT fv.id, u.nickname, v.name, v.vendor_type FROM favorite_vendors fv JOIN users u ON fv.user_id = u.id JOIN vendors v ON fv.vendor_id = v.id LIMIT 20;'">
                    <code>SELECT fv.id, u.nickname, v.name, v.vendor_type FROM favorite_vendors fv JOIN users u ON fv.user_id = u.id JOIN vendors v ON fv.vendor_id = v.id LIMIT 20;</code>
                </div>
                
                <h4 style="margin-top: 20px; margin-bottom: 8px; color: #555;">📊 통계 쿼리</h4>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT COUNT(*) as total_users FROM users;'">
                    <code>SELECT COUNT(*) as total_users FROM users;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT COUNT(*) as total_posts, SUM(view_count) as total_views, AVG(view_count) as avg_views FROM posts;'">
                    <code>SELECT COUNT(*) as total_posts, SUM(view_count) as total_views, AVG(view_count) as avg_views FROM posts;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT board_type, COUNT(*) as count FROM posts GROUP BY board_type;'">
                    <code>SELECT board_type, COUNT(*) as count FROM posts GROUP BY board_type;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT u.id, u.nickname, COUNT(p.id) as post_count FROM users u LEFT JOIN posts p ON u.id = p.user_id GROUP BY u.id, u.nickname ORDER BY post_count DESC LIMIT 10;'">
                    <code>SELECT u.id, u.nickname, COUNT(p.id) as post_count FROM users u LEFT JOIN posts p ON u.id = p.user_id GROUP BY u.id, u.nickname ORDER BY post_count DESC LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT category, COUNT(*) as count FROM calendar_events GROUP BY category;'">
                    <code>SELECT category, COUNT(*) as count FROM calendar_events GROUP BY category;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT user_id, SUM(estimated_budget) as total_estimated, SUM(actual_expense) as total_actual FROM budget_items GROUP BY user_id;'">
                    <code>SELECT user_id, SUM(estimated_budget) as total_estimated, SUM(actual_expense) as total_actual FROM budget_items GROUP BY user_id;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT vendor_type, COUNT(*) as count, AVG(rating_avg) as avg_rating FROM vendors GROUP BY vendor_type;'">
                    <code>SELECT vendor_type, COUNT(*) as count, AVG(rating_avg) as avg_rating FROM vendors GROUP BY vendor_type;</code>
                </div>
                
                <h4 style="margin-top: 20px; margin-bottom: 8px; color: #555;">🔎 검색 및 필터링</h4>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM posts WHERE title LIKE \\'%결혼%\\' LIMIT 10;'">
                    <code>SELECT * FROM posts WHERE title LIKE '%결혼%' LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM calendar_events WHERE category = \\'todo\\' AND is_completed = 0 LIMIT 20;'">
                    <code>SELECT * FROM calendar_events WHERE category = 'todo' AND is_completed = 0 LIMIT 20;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM posts WHERE view_count > 100 ORDER BY view_count DESC LIMIT 10;'">
                    <code>SELECT * FROM posts WHERE view_count > 100 ORDER BY view_count DESC LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM calendar_events WHERE start_date >= CURDATE() ORDER BY start_date LIMIT 20;'">
                    <code>SELECT * FROM calendar_events WHERE start_date >= CURDATE() ORDER BY start_date LIMIT 20;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM vendors WHERE base_location_city = \\'서울시\\' LIMIT 20;'">
                    <code>SELECT * FROM vendors WHERE base_location_city = '서울시' LIMIT 20;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM budget_items WHERE category = \\'웨딩홀\\' ORDER BY estimated_budget DESC LIMIT 20;'">
                    <code>SELECT * FROM budget_items WHERE category = '웨딩홀' ORDER BY estimated_budget DESC LIMIT 20;</code>
                </div>
                
                <h4 style="margin-top: 20px; margin-bottom: 8px; color: #555;">📅 날짜/시간 관련</h4>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM posts WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) ORDER BY created_at DESC LIMIT 20;'">
                    <code>SELECT * FROM posts WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) ORDER BY created_at DESC LIMIT 20;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM calendar_events WHERE start_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY) ORDER BY start_date;'">
                    <code>SELECT * FROM calendar_events WHERE start_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY) ORDER BY start_date;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT DATE(created_at) as date, COUNT(*) as count FROM posts GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 30;'">
                    <code>SELECT DATE(created_at) as date, COUNT(*) as count FROM posts GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 30;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM wedding_profiles WHERE wedding_date >= CURDATE() ORDER BY wedding_date LIMIT 20;'">
                    <code>SELECT * FROM wedding_profiles WHERE wedding_date >= CURDATE() ORDER BY wedding_date LIMIT 20;</code>
                </div>
                
                <h4 style="margin-top: 20px; margin-bottom: 8px; color: #555;">👤 사용자별 조회</h4>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM posts WHERE user_id = 1 ORDER BY created_at DESC LIMIT 20;'">
                    <code>SELECT * FROM posts WHERE user_id = 1 ORDER BY created_at DESC LIMIT 20;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM calendar_events WHERE user_id = 1 ORDER BY start_date;'">
                    <code>SELECT * FROM calendar_events WHERE user_id = 1 ORDER BY start_date;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM budget_items WHERE user_id = 1 ORDER BY created_at DESC;'">
                    <code>SELECT * FROM budget_items WHERE user_id = 1 ORDER BY created_at DESC;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT * FROM chat_history WHERE user_id = 1 ORDER BY created_at DESC LIMIT 50;'">
                    <code>SELECT * FROM chat_history WHERE user_id = 1 ORDER BY created_at DESC LIMIT 50;</code>
                </div>
                
                <h4 style="margin-top: 20px; margin-bottom: 8px; color: #555;">🔥 인기/랭킹</h4>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT p.id, p.title, u.nickname, p.view_count, COUNT(pl.id) as like_count FROM posts p JOIN users u ON p.user_id = u.id LEFT JOIN post_likes pl ON p.id = pl.post_id GROUP BY p.id ORDER BY like_count DESC, view_count DESC LIMIT 10;'">
                    <code>SELECT p.id, p.title, u.nickname, p.view_count, COUNT(pl.id) as like_count FROM posts p JOIN users u ON p.user_id = u.id LEFT JOIN post_likes pl ON p.id = pl.post_id GROUP BY p.id ORDER BY like_count DESC, view_count DESC LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT p.id, p.title, COUNT(c.id) as comment_count FROM posts p LEFT JOIN comments c ON p.id = c.post_id GROUP BY p.id ORDER BY comment_count DESC LIMIT 10;'">
                    <code>SELECT p.id, p.title, COUNT(c.id) as comment_count FROM posts p LEFT JOIN comments c ON p.id = c.post_id GROUP BY p.id ORDER BY comment_count DESC LIMIT 10;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SELECT v.id, v.name, v.vendor_type, v.rating_avg, COUNT(fv.id) as favorite_count FROM vendors v LEFT JOIN favorite_vendors fv ON v.id = fv.vendor_id GROUP BY v.id ORDER BY favorite_count DESC, rating_avg DESC LIMIT 10;'">
                    <code>SELECT v.id, v.name, v.vendor_type, v.rating_avg, COUNT(fv.id) as favorite_count FROM vendors v LEFT JOIN favorite_vendors fv ON v.id = fv.vendor_id GROUP BY v.id ORDER BY favorite_count DESC, rating_avg DESC LIMIT 10;</code>
                </div>
                
                <h4 style="margin-top: 20px; margin-bottom: 8px; color: #555;">✏️ 수정/삭제</h4>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='UPDATE posts SET view_count = 0 WHERE id = 1;'">
                    <code>UPDATE posts SET view_count = 0 WHERE id = 1;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='UPDATE calendar_events SET is_completed = 1 WHERE id = 1;'">
                    <code>UPDATE calendar_events SET is_completed = 1 WHERE id = 1;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='DELETE FROM comments WHERE id = 1;'">
                    <code>DELETE FROM comments WHERE id = 1;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='DELETE FROM post_likes WHERE post_id = 1 AND user_id = 1;'">
                    <code>DELETE FROM post_likes WHERE post_id = 1 AND user_id = 1;</code>
                </div>
                
                <h4 style="margin-top: 20px; margin-bottom: 8px; color: #555;">➕ 삽입</h4>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='INSERT INTO tags (name) VALUES (\\'새 태그\\');'">
                    <code>INSERT INTO tags (name) VALUES ('새 태그');</code>
                </div>
                
                <h4 style="margin-top: 20px; margin-bottom: 8px; color: #555;">🔧 테이블 정보</h4>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='SHOW TABLES;'">
                    <code>SHOW TABLES;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='DESCRIBE users;'">
                    <code>DESCRIBE users;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='DESCRIBE posts;'">
                    <code>DESCRIBE posts;</code>
                </div>
                <div class="example-query" onclick="document.querySelector('textarea[name=\\'query\\']').value='DESCRIBE calendar_events;'">
                    <code>DESCRIBE calendar_events;</code>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

