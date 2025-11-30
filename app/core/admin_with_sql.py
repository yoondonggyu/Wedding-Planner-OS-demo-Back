"""
각 ModelView 페이지에 SQL 쿼리 입력 기능을 추가하는 헬퍼
JavaScript를 사용하여 각 페이지에 SQL 입력 필드를 동적으로 추가
"""
from sqladmin import ModelView
from fastapi import Request
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from app.core.database import engine
import time
import json


class SQLQueryMixin:
    """각 ModelView 페이지에 SQL 입력 기능을 추가하는 Mixin"""
    
    async def list(self, request: Request):
        """리스트 페이지에 SQL 입력 기능 추가"""
        # 기본 리스트 기능 실행 - super()를 통해 부모 클래스의 list 메서드 호출
        # MRO를 따라 올바른 부모 클래스를 찾아 호출
        response = await super(SQLQueryMixin, self).list(request)
        
        # SQL 쿼리 실행 (POST 요청인 경우)
        sql_error = None
        sql_results = None
        sql_execution_time = None
        sql_query = ""
        
        if request.method == "POST":
            form = await request.form()
            sql_query = form.get("sql_query", "").strip()
            
            if sql_query:
                try:
                    query_upper = sql_query.upper().strip()
                    
                    # 매우 위험한 쿼리만 차단
                    very_dangerous_keywords = [
                        "DROP TABLE", "DROP DATABASE", "TRUNCATE", 
                        "ALTER TABLE", "CREATE TABLE", "CREATE DATABASE",
                        "GRANT", "REVOKE", "EXEC", "EXECUTE", "CALL"
                    ]
                    
                    query_upper_for_check = query_upper.replace('\n', ' ').replace('\r', ' ')
                    if any(kw in query_upper_for_check for kw in very_dangerous_keywords):
                        sql_error = "보안상 DROP, TRUNCATE, ALTER TABLE 등의 쿼리는 실행할 수 없습니다."
                    else:
                        start_time = time.time()
                        with engine.begin() as conn:
                            result = conn.execute(text(sql_query))
                            
                            if result.returns_rows:
                                columns = list(result.keys())
                                rows = []
                                for row in result:
                                    row_dict = {}
                                    for key, value in row._mapping.items():
                                        if value is None:
                                            row_dict[key] = None
                                        elif isinstance(value, (int, float, str, bool)):
                                            row_dict[key] = value
                                        else:
                                            row_dict[key] = str(value)
                                    rows.append(row_dict)
                                
                                sql_results = {
                                    "columns": columns,
                                    "rows": rows,
                                    "row_count": len(rows)
                                }
                            else:
                                affected_rows = result.rowcount if hasattr(result, 'rowcount') else 0
                                sql_results = {
                                    "message": f"쿼리가 실행되었습니다. {affected_rows}개 행이 영향을 받았습니다.",
                                    "row_count": affected_rows
                                }
                        
                        sql_execution_time = round((time.time() - start_time) * 1000, 2)
                        
                except Exception as e:
                    sql_error = str(e)
        
        # HTML 응답에 SQL 입력 필드 추가
        if isinstance(response, HTMLResponse):
            html_content = response.body.decode('utf-8')
            
            # SQL 입력 섹션 HTML
            table_name = self.model.__tablename__ if hasattr(self, 'model') else 'table'
            sql_section = f"""
            <div id="sql-terminal-section" style="margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
                <h3 style="margin-top: 0; color: #333;">🔧 SQL 쿼리 실행 (현재 테이블: <code>{table_name}</code>)</h3>
                <div style="background: #fff3cd; border: 1px solid #ffc107; color: #856404; padding: 12px; border-radius: 4px; margin-bottom: 12px;">
                    <strong>⚠️ 주의:</strong> 관리자 전용 SQL 터미널입니다. SELECT, INSERT, UPDATE, DELETE 쿼리를 실행할 수 있습니다.
                </div>
                {f'<div style="background: #f8d7da; border: 1px solid #dc3545; color: #721c24; padding: 12px; border-radius: 4px; margin-bottom: 12px;"><strong>❌ 오류:</strong> {sql_error}</div>' if sql_error else ''}
                {f'<div style="background: #d4edda; border: 1px solid #28a745; color: #155724; padding: 12px; border-radius: 4px; margin-bottom: 12px;"><strong>✅ 성공:</strong> {sql_execution_time}ms 소요, {sql_results.get("row_count", 0) if sql_results else 0}개 행 반환</div>' if sql_results and not sql_error else ''}
                <form method="POST" style="margin-bottom: 12px;">
                    <textarea name="sql_query" placeholder="SQL 쿼리를 입력하세요...&#10;&#10;예: SELECT * FROM {table_name} LIMIT 10;&#10;예: UPDATE {table_name} SET ... WHERE ...;&#10;예: DELETE FROM {table_name} WHERE ...;" style="width: 100%; min-height: 150px; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 14px; resize: vertical; box-sizing: border-box;">{sql_query}</textarea>
                    <div style="display: flex; gap: 12px; margin-top: 12px;">
                        <button type="submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 500;">실행</button>
                        <button type="button" onclick="document.querySelector('textarea[name=\\'sql_query\\']').value=''" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 500;">초기화</button>
                    </div>
                </form>
                {self._render_sql_results(sql_results) if sql_results else ''}
            </div>
            """
            
            # </body> 태그 앞에 SQL 섹션 추가
            if '</body>' in html_content:
                html_content = html_content.replace('</body>', sql_section + '</body>')
            else:
                # </body> 태그가 없으면 끝에 추가
                html_content += sql_section
        
        return HTMLResponse(content=html_content) if isinstance(response, HTMLResponse) else response
    
    def _render_sql_results(self, results: dict) -> str:
        """SQL 쿼리 결과를 HTML 테이블로 렌더링"""
        if not results:
            return ""
        
        if "message" in results:
            return f'<div style="margin-top: 12px;"><div style="background: #d4edda; border: 1px solid #28a745; color: #155724; padding: 12px; border-radius: 4px;">{results["message"]}</div></div>'
        
        if "columns" not in results or "rows" not in results:
            return ""
        
        columns = results["columns"]
        rows = results["rows"]
        
        if not rows:
            return '<div style="margin-top: 12px;"><div style="background: #d4edda; border: 1px solid #28a745; color: #155724; padding: 12px; border-radius: 4px;">쿼리 실행 완료. 반환된 행이 없습니다.</div></div>'
        
        # 테이블 HTML 생성
        table_html = f'<div style="margin-top: 12px;"><div style="padding: 12px; background: #f8f9fa; border-radius: 4px; margin-bottom: 12px;"><strong>{len(rows)}개 행 반환</strong></div>'
        table_html += '<div style="overflow-x: auto; border: 1px solid #ddd; border-radius: 4px; max-height: 500px; overflow-y: auto;"><table style="width: 100%; border-collapse: collapse; background: white;"><thead><tr>'
        
        for col in columns:
            table_html += f'<th style="background: #007bff; color: white; padding: 12px; text-align: left; font-weight: 600; position: sticky; top: 0;">{col}</th>'
        table_html += '</tr></thead><tbody>'
        
        for row in rows:
            table_html += '<tr>'
            for col in columns:
                value = row.get(col, '')
                if value is None:
                    value = '<em style="color: #999;">NULL</em>'
                elif isinstance(value, str) and len(value) > 100:
                    value = value[:100] + '...'
                # HTML 이스케이프
                if isinstance(value, str):
                    value = value.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                table_html += f'<td style="padding: 10px 12px; border-bottom: 1px solid #eee;">{value}</td>'
            table_html += '</tr>'
        
        table_html += '</tbody></table></div></div>'
        
        return table_html

