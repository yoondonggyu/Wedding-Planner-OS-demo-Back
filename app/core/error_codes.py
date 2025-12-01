"""
에러 코드 정의
HTTP 상태 코드 기반 에러 코드 체계
각 HTTP 상태 코드 + 순번(1, 2, 3...) 형식
4001~4009 이후는 40010, 40011... 형식으로 계속 이어감
4221~4229 이후는 42210, 42211... 형식으로 계속 이어감
"""
from enum import IntEnum


class ErrorCode(IntEnum):
    """커스텀 에러 코드 정의 - HTTP 상태 코드 기반"""
    
    # 400 Bad Request (4001, 4002, ..., 4009, 40010, 40011, ...)
    INVALID_CREDENTIALS = 4001
    INVALID_REQUEST = 4002
    FILE_REQUIRED = 4003
    INVALID_FILE_TYPE = 4004
    INVALID_GUEST_COUNT_CATEGORY = 4005
    INVALID_VENDOR_TYPE = 4006
    
    # 401 Unauthorized (4011, 4012, ..., 4019, 40110, 40111, ...)
    UNAUTHORIZED = 4011
    TOKEN_EXPIRED = 4012
    TOKEN_INVALID = 4013
    
    # 403 Forbidden (4031, 4032, ..., 4039, 40310, 40311, ...)
    FORBIDDEN = 4031
    INSUFFICIENT_PERMISSIONS = 4032
    
    # 404 Not Found (4041, 4042, ..., 4049, 40410, 40411, ...)
    RESOURCE_NOT_FOUND = 4041
    POST_NOT_FOUND = 4042
    COMMENT_NOT_FOUND = 4043
    USER_NOT_FOUND = 4044
    EVENT_NOT_FOUND = 4045
    TODO_NOT_FOUND = 4046
    BUDGET_ITEM_NOT_FOUND = 4047
    VENDOR_NOT_FOUND = 4048
    WEDDING_PROFILE_NOT_FOUND = 4049
    FAVORITE_NOT_FOUND = 40410
    
    # 409 Conflict (4090, 4091, ..., 4099, 40910, 40911, ...)
    DUPLICATE_EMAIL = 4090
    DUPLICATE_NICKNAME = 4091
    DUPLICATE_USER_ID = 4092
    DUPLICATE_RESOURCE = 4093
    POST_ALREADY_LIKED = 4094
    FAVORITE_ALREADY_EXISTS = 4095
    
    # 422 Unprocessable Entity (4221, 4222, ..., 4229, 42210, 42211, ...)
    EMAIL_REQUIRED = 4221
    INVALID_EMAIL_FORMAT = 4222
    INVALID_EMAIL_CHARACTER = 4223
    PASSWORD_REQUIRED = 4224
    INVALID_PASSWORD_FORMAT = 4225
    PASSWORD_CHECK_REQUIRED = 4226
    NICKNAME_REQUIRED = 4227
    NICKNAME_CONTAINS_SPACE = 4228
    NICKNAME_TOO_LONG = 4229
    PROFILE_IMAGE_URL_REQUIRED = 42210
    VALIDATION_ERROR = 42211
    MISSING_REQUIRED_FIELD = 42212
    MISSING_FIELDS = 42213
    INVALID_DATE_FORMAT = 42214
    INVALID_TIME_FORMAT = 42215
    PASSWORD_MISMATCH = 42216
    
    # 413 Payload Too Large (4131, 4132, ..., 4139, 41310, 41311, ...)
    FILE_TOO_LARGE = 4131
    
    # 500 Internal Server Error (5001, 5002, ..., 5009, 50010, 50011, ...)
    INTERNAL_SERVER_ERROR = 5001
    DATABASE_ERROR = 5002
    EXTERNAL_SERVICE_ERROR = 5003
    MODEL_API_ERROR = 5004


# 에러 코드와 메시지 매핑
ERROR_MESSAGES = {
    # 400 Bad Request
    ErrorCode.INVALID_CREDENTIALS: "invalid_credentials",
    ErrorCode.INVALID_REQUEST: "invalid_request",
    ErrorCode.FILE_REQUIRED: "file_required",
    ErrorCode.INVALID_FILE_TYPE: "invalid_file_type",
    ErrorCode.INVALID_GUEST_COUNT_CATEGORY: "invalid_guest_count_category",
    ErrorCode.INVALID_VENDOR_TYPE: "invalid_vendor_type",
    
    # 401 Unauthorized
    ErrorCode.UNAUTHORIZED: "unauthorized_user",
    ErrorCode.TOKEN_EXPIRED: "token_expired",
    ErrorCode.TOKEN_INVALID: "token_invalid",
    
    # 403 Forbidden
    ErrorCode.FORBIDDEN: "forbidden",
    ErrorCode.INSUFFICIENT_PERMISSIONS: "insufficient_permissions",
    
    # 404 Not Found
    ErrorCode.RESOURCE_NOT_FOUND: "resource_not_found",
    ErrorCode.POST_NOT_FOUND: "post_not_found",
    ErrorCode.COMMENT_NOT_FOUND: "comment_not_found",
    ErrorCode.USER_NOT_FOUND: "user_not_found",
    ErrorCode.EVENT_NOT_FOUND: "event_not_found",
    ErrorCode.TODO_NOT_FOUND: "todo_not_found",
    ErrorCode.BUDGET_ITEM_NOT_FOUND: "budget_item_not_found",
    ErrorCode.VENDOR_NOT_FOUND: "vendor_not_found",
    ErrorCode.WEDDING_PROFILE_NOT_FOUND: "wedding_profile_not_found",
    ErrorCode.FAVORITE_NOT_FOUND: "favorite_not_found",
    
    # 409 Conflict
    ErrorCode.DUPLICATE_EMAIL: "duplicate_email",
    ErrorCode.DUPLICATE_NICKNAME: "duplicate_nickname",
    ErrorCode.DUPLICATE_USER_ID: "duplicate_user_id",
    ErrorCode.DUPLICATE_RESOURCE: "duplicate_resource",
    ErrorCode.POST_ALREADY_LIKED: "post_already_liked",
    ErrorCode.FAVORITE_ALREADY_EXISTS: "favorite_already_exists",
    
    # 422 Unprocessable Entity
    ErrorCode.EMAIL_REQUIRED: "email_required",
    ErrorCode.INVALID_EMAIL_FORMAT: "invalid_email_format",
    ErrorCode.INVALID_EMAIL_CHARACTER: "invalid_email_character",
    ErrorCode.PASSWORD_REQUIRED: "password_required",
    ErrorCode.INVALID_PASSWORD_FORMAT: "invalid_password_format",
    ErrorCode.PASSWORD_CHECK_REQUIRED: "password_check_required",
    ErrorCode.NICKNAME_REQUIRED: "nickname_required",
    ErrorCode.NICKNAME_CONTAINS_SPACE: "nickname_contains_space",
    ErrorCode.NICKNAME_TOO_LONG: "nickname_too_long",
    ErrorCode.PROFILE_IMAGE_URL_REQUIRED: "profile_image_url_required",
    ErrorCode.VALIDATION_ERROR: "validation_error",
    ErrorCode.MISSING_REQUIRED_FIELD: "missing_required_field",
    ErrorCode.MISSING_FIELDS: "missing_fields",
    ErrorCode.INVALID_DATE_FORMAT: "invalid_date_format",
    ErrorCode.INVALID_TIME_FORMAT: "invalid_time_format",
    ErrorCode.PASSWORD_MISMATCH: "password_mismatch",
    
    # 413 Payload Too Large
    ErrorCode.FILE_TOO_LARGE: "file_too_large",
    
    # 500 Internal Server Error
    ErrorCode.INTERNAL_SERVER_ERROR: "internal_server_error",
    ErrorCode.DATABASE_ERROR: "database_error",
    ErrorCode.EXTERNAL_SERVICE_ERROR: "external_service_error",
    ErrorCode.MODEL_API_ERROR: "model_api_error",
}
