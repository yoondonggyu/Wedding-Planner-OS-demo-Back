"""응답 포맷팅 유틸리티"""
from fastapi.responses import JSONResponse


def create_json_response(status_code: int, message: str, data=None, error_code: int = None) -> JSONResponse:
    """
    일관된 JSON 응답 형식 생성
    
    Args:
        status_code: HTTP 상태 코드
        message: 응답 메시지
        data: 응답 데이터 (선택)
        error_code: 커스텀 에러 코드 (선택)
    
    Returns:
        JSONResponse: 표준화된 JSON 응답
    """
    content = {"message": message}
    
    # 에러 응답인 경우 error_code 추가
    if error_code is not None:
        content["error_code"] = error_code
    
    # data가 있으면 추가
    if data is not None:
        content["data"] = data
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )



