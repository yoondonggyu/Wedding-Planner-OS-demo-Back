from fastapi import status
from app.core.error_codes import ErrorCode, ERROR_MESSAGES


class APIError(Exception):
    def __init__(self, message: str, status_code: int, error_code: int = None, data=None):
        """
        API 에러 예외 클래스
        
        Args:
            message: 에러 메시지
            status_code: HTTP 상태 코드 (400, 401, 404 등)
            error_code: 커스텀 에러 코드 (4001, 4002 등) - 선택사항
            data: 추가 데이터
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.data = data


def bad_request(msg: str, error_code: ErrorCode = None, data=None):
    """400 Bad Request"""
    return APIError(msg, status.HTTP_400_BAD_REQUEST, error_code.value if error_code else None, data)

def unauthorized(msg="unauthorized_user", error_code: ErrorCode = ErrorCode.UNAUTHORIZED):
    """401 Unauthorized"""
    return APIError(msg, status.HTTP_401_UNAUTHORIZED, error_code.value)

def forbidden(msg="forbidden", error_code: ErrorCode = ErrorCode.FORBIDDEN):
    """403 Forbidden"""
    return APIError(msg, status.HTTP_403_FORBIDDEN, error_code.value)

def not_found(msg: str, error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND):
    """404 Not Found"""
    return APIError(msg, status.HTTP_404_NOT_FOUND, error_code.value)

def conflict(msg: str, error_code: ErrorCode = ErrorCode.DUPLICATE_RESOURCE):
    """409 Conflict"""
    return APIError(msg, status.HTTP_409_CONFLICT, error_code.value)

def unprocessable(msg: str, error_code: ErrorCode = ErrorCode.VALIDATION_ERROR, data=None):
    """422 Unprocessable Entity"""
    return APIError(msg, status.HTTP_422_UNPROCESSABLE_ENTITY, error_code.value, data)

def payload_too_large(msg: str, error_code: ErrorCode = ErrorCode.FILE_TOO_LARGE, data=None):
    """413 Payload Too Large"""
    return APIError(msg, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, error_code.value, data)
