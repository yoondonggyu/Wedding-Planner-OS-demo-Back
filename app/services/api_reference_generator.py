"""
API 명세서 자동 생성 서비스
FastAPI의 OpenAPI 스키마를 활용하여 api_reference.html을 자동으로 생성/업데이트
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import re
from app.core.error_codes import ErrorCode, ERROR_MESSAGES
from app.main import app


class APIReferenceGenerator:
    """API 명세서 자동 생성기"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.api_ref_path = self.base_dir.parent / "1.Wedding_OS_front" / "api_reference.html"
        
    def get_next_error_code(self, status_code: int) -> int:
        """에러 코드 자동 넘버링 (4001~4009 이후 40010, 40011, ... 형식)"""
        # 현재 error_codes.py에서 해당 상태 코드의 모든 에러 코드 수집
        codes = []
        for error_code in ErrorCode:
            code_str = str(error_code.value)
            if code_str.startswith(str(status_code)):
                codes.append(error_code.value)
        
        if not codes:
            # 첫 번째 에러 코드
            return int(f"{status_code}1")
        
        # 최대값 찾기
        max_code = max(codes)
        max_code_str = str(max_code)
        
        # 상태 코드 이후의 숫자 추출
        remaining = max_code_str[len(str(status_code)):]
        
        if remaining.isdigit():
            num = int(remaining)
            # 다음 번호 생성 (4009 이후 40010, 40011...)
            next_num = num + 1
            return int(f"{status_code}{next_num}")
        
        return int(f"{status_code}1")
    
    def get_openapi_schema(self) -> Dict:
        """FastAPI 앱에서 OpenAPI 스키마 가져오기"""
        return app.openapi()
    
    def scan_controllers_for_errors(self) -> Dict[str, List[Dict]]:
        """컨트롤러 파일을 스캔하여 각 API별 발생 가능한 에러 추출"""
        api_errors = {}
        controllers_dir = self.base_dir / "app" / "controllers"
        
        controller_files = [
            "auth_controller.py",
            "user_controller.py",
            "post_controller.py",
            "comment_controller.py",
            "calendar_controller.py",
            "vendor_controller.py",
            "budget_controller.py",
        ]
        
        for controller_file in controller_files:
            controller_path = controllers_dir / controller_file
            if not controller_path.exists():
                continue
            
            with open(controller_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 함수별로 에러 추출
                for func_match in re.finditer(r'def\s+(\w+)_controller', content):
                    func_name = func_match.group(1)
                    func_start = func_match.end()
                    
                    # 다음 함수까지의 범위 찾기
                    next_func = re.search(r'\ndef\s+\w+_controller', content[func_start:])
                    func_end = func_start + (next_func.start() if next_func else len(content))
                    func_content = content[func_start:func_end]
                    
                    errors = []
                    # raise 문에서 에러 코드와 상태 코드 추출
                    for raise_match in re.finditer(r'raise\s+(\w+)\s*\([^,]+,\s*ErrorCode\.(\w+)', func_content):
                        exception_type = raise_match.group(1)  # bad_request, not_found 등
                        error_code_name = raise_match.group(2)
                        
                        # exception_type에서 상태 코드 추출
                        status_code = self._get_status_from_exception(exception_type)
                        error_code = getattr(ErrorCode, error_code_name, None)
                        
                        if error_code:
                            errors.append({
                                'status': status_code,
                                'error_code': error_code.value,
                                'message': ERROR_MESSAGES.get(error_code, error_code_name.lower()),
                                'error_name': error_code_name.lower()
                            })
                    
                    if errors:
                        api_errors[func_name] = errors
        
        return api_errors
    
    def _get_status_from_exception(self, exception_type: str) -> int:
        """예외 타입에서 HTTP 상태 코드 추출"""
        status_map = {
            'bad_request': 400,
            'unauthorized': 401,
            'forbidden': 403,
            'not_found': 404,
            'conflict': 409,
            'unprocessable': 422,
            'payload_too_large': 413,
        }
        return status_map.get(exception_type, 500)
    
    def generate_api_reference_from_openapi(self) -> str:
        """OpenAPI 스키마를 기반으로 API 명세서 HTML 생성"""
        schema = self.get_openapi_schema()
        controller_errors = self.scan_controllers_for_errors()
        
        # 기존 HTML 읽기 (템플릿으로 사용)
        if self.api_ref_path.exists():
            with open(self.api_ref_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
        else:
            html_template = self._get_default_template()
        
        # API 테이블 행 생성
        api_table_rows = []
        api_details = []
        
        # OpenAPI paths에서 API 추출
        paths = schema.get('paths', {})
        api_id_counter = {}
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                    continue
                
                # 태그 추출
                tags = details.get('tags', ['default'])
                tag = tags[0] if tags else 'default'
                
                # API ID 생성
                if tag not in api_id_counter:
                    api_id_counter[tag] = 1
                else:
                    api_id_counter[tag] += 1
                
                api_id = f"{self._get_tag_number(tag)}.{api_id_counter[tag]}"
                summary = details.get('summary', details.get('operationId', path))
                
                # 인증 필요 여부 확인
                security = details.get('security', [])
                auth_required = len(security) > 0
                auth_badge = '<span class="auth-badge auth-required">필수</span>' if auth_required else '<span class="auth-badge auth-optional">선택</span>'
                
                method_badge = self._get_method_badge(method.upper())
                
                api_table_rows.append(f"""
        <tr>
          <td><strong>{api_id} {summary}</strong></td>
          <td>{method_badge}</td>
          <td><code>{path}</code></td>
          <td><code>Request</code></td>
          <td><code>Response</code></td>
          <td>{auth_badge}</td>
        </tr>""")
                
                # API 상세 생성
                api_detail = self._generate_api_detail_from_openapi(
                    api_id, path, method.upper(), details, controller_errors
                )
                api_details.append(api_detail)
        
        # HTML에 삽입
        # 기존 테이블 행 찾아서 교체
        table_pattern = r'<tbody>.*?</tbody>'
        if api_table_rows:
            new_table_body = '<tbody>' + '\n'.join(api_table_rows) + '\n      </tbody>'
            html_template = re.sub(table_pattern, new_table_body, html_template, flags=re.DOTALL)
        
        # 기존 API 상세 섹션 찾아서 교체
        details_pattern = r'<div class="api-detail">.*?</div>\s*</div>'
        if api_details:
            # 마지막 </div> 태그 전에 삽입
            new_details = '\n'.join(api_details)
            # 기존 상세 섹션을 모두 제거하고 새로 추가
            html_template = re.sub(r'<div class="api-detail">.*?</div>\s*</div>', '', html_template, flags=re.DOTALL)
            # </body> 태그 전에 삽입
            html_template = html_template.replace('</body>', new_details + '\n</body>')
        
        return html_template
    
    def _get_tag_number(self, tag: str) -> int:
        """태그를 번호로 매핑"""
        tag_map = {
            'auth': 1,
            'users': 2,
            'posts': 3,
            'comments': 4,
            'chat': 5,
            'calendar': 6,
            'budget': 7,
            'voice': 8,
            'vendor': 9,
            'vector': 10,
        }
        return tag_map.get(tag.lower(), 99)
    
    def _get_method_badge(self, method: str) -> str:
        """HTTP 메서드 배지 생성"""
        method_classes = {
            'POST': 'method-post',
            'GET': 'method-get',
            'PUT': 'method-put',
            'PATCH': 'method-patch',
            'DELETE': 'method-delete',
        }
        class_name = method_classes.get(method, 'method-get')
        return f'<span class="method-badge {class_name}">{method}</span>'
    
    def _generate_api_detail_from_openapi(
        self, api_id: str, path: str, method: str, details: Dict, controller_errors: Dict
    ) -> str:
        """OpenAPI 스키마를 기반으로 API 상세 섹션 생성"""
        summary = details.get('summary', details.get('operationId', path))
        description = details.get('description', '')
        
        # 에러 응답 생성
        error_responses = []
        
        # operationId에서 컨트롤러 함수명 추출
        operation_id = details.get('operationId', '')
        func_name = operation_id.replace('_', '_').split('_')[0] if '_' in operation_id else operation_id
        
        # 컨트롤러에서 발견된 에러 추가
        if func_name in controller_errors:
            for error in controller_errors[func_name]:
                error_responses.append(self._generate_error_row(
                    error['status'],
                    error['message'],
                    error['error_code'],
                    self._get_error_description(error['error_name'])
                ))
        
        # 기본 에러 (모든 API에 공통)
        if not any(e['status'] == 500 for e in error_responses):
            error_responses.append(self._generate_error_row(500, 'internal_server_error', 5001, '서버 오류'))
        
        error_rows = '\n'.join(error_responses)
        
        # 요청/응답 스키마 추출
        request_body = details.get('requestBody', {})
        responses = details.get('responses', {})
        
        return f"""
    <div class="api-detail">
      <h3>{api_id} {summary}</h3>
      <div class="api-id">API ID: {api_id}</div>
      <div class="description">{description or summary}</div>
      
      <h4 style="margin-top: 24px; margin-bottom: 12px; color: var(--accent-2);">Body / Parameter / Header / Query</h4>
      <h5 style="margin-top: 24px; color: var(--text);">응답 코드별 예시</h5>
      <table class="status-code-table">
        <thead>
          <tr>
            <th>Response Status Code</th>
            <th>Body</th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
{error_rows}
        </tbody>
      </table>
    </div>"""
    
    def _generate_error_row(self, status: int, message: str, error_code: int, description: str) -> str:
        """에러 응답 행 생성"""
        return f"""          <tr>
            <td><span class="status-{status}">{status}</span></td>
            <td><div class="code-block" style="margin: 0; padding: 8px; font-size: 12px;">{{
  &quot;message&quot;: &quot;{message}&quot;,
  &quot;error_code&quot;: {error_code},
  &quot;data&quot;: null
}}</div></td>
            <td>{description}</td>
          </tr>"""
    
    def _get_error_description(self, error_name: str) -> str:
        """에러 이름에서 설명 생성"""
        descriptions = {
            'invalid_credentials': '아이디 또는 비밀번호를 확인해주세요',
            'unauthorized': '인증 필요',
            'unauthorized_user': '인증 필요',
            'forbidden': '권한 없음',
            'post_not_found': '게시글을 찾을 수 없습니다',
            'comment_not_found': '댓글을 찾을 수 없습니다',
            'event_not_found': '일정을 찾을 수 없습니다',
            'todo_not_found': '할일을 찾을 수 없습니다',
            'duplicate_email': '이미 사용 중인 이메일입니다',
            'duplicate_nickname': '이미 사용 중인 닉네임입니다',
            'validation_error': '유효성 검사 실패',
            'missing_required_field': '필수 필드가 누락되었습니다',
            'missing_fields': '필수 필드가 누락되었습니다',
            'invalid_date_format': '올바른 날짜 형식을 입력해주세요 (YYYY-MM-DD)',
            'invalid_time_format': '올바른 시간 형식을 입력해주세요 (HH:MM)',
            'password_mismatch': '비밀번호가 일치하지 않습니다',
            'file_too_large': '파일 크기가 너무 큽니다 (최대 5MB)',
            'internal_server_error': '서버 오류',
        }
        return descriptions.get(error_name, error_name.replace('_', ' ').title())
    
    def _get_default_template(self) -> str:
        """기본 HTML 템플릿"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Wedding OS API Reference</title>
</head>
<body>
  <div class="container">
    <header>
      <h1>Wedding OS API Reference</h1>
      <button id="refreshBtn" onclick="refreshAPIReference()">🔄 새로고침</button>
    </header>
  </div>
</body>
</html>"""
    
    def update_api_reference(self) -> bool:
        """API 명세서 업데이트"""
        try:
            html = self.generate_api_reference_from_openapi()
            with open(self.api_ref_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True
        except Exception as e:
            print(f"API 명세서 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
