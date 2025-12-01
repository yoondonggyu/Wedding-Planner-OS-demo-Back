import re
from app.core.exceptions import bad_request, unprocessable
from app.core.error_codes import ErrorCode

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
NICKNAME_SPACE = re.compile(r"\s")

def validate_email(email: str):
    if not email:
        raise unprocessable("email_required", ErrorCode.EMAIL_REQUIRED)
    if not EMAIL_RE.match(email):
        raise unprocessable("invalid_email_format", ErrorCode.INVALID_EMAIL_FORMAT)
    if not re.fullmatch(r"[A-Za-z0-9@._+-]+", email):
        raise unprocessable("invalid_email_character", ErrorCode.INVALID_EMAIL_CHARACTER, {"allowed": "영문, @, ."})
    return True

def validate_password(pw: str, field="password"):
    if not pw:
        raise unprocessable(f"{field}_required", ErrorCode.PASSWORD_REQUIRED)
    if len(pw) < 8 or len(pw) > 20 or \
       not re.search(r"[A-Z]", pw) or \
       not re.search(r"[a-z]", pw) or \
       not re.search(r"[0-9\W_]", pw):
        raise unprocessable("invalid_password_format", ErrorCode.INVALID_PASSWORD_FORMAT)
    return True

def validate_password_pair(pw: str, pw_check: str, raise_validation_failed=False):
    """비밀번호 쌍 검증. raise_validation_failed=True일 경우 password_validation_failed 형식으로 반환"""
    if not pw:
        if raise_validation_failed:
            raise unprocessable("password_validation_failed", ErrorCode.MISSING_REQUIRED_FIELD, {"reason": "password_blank"})
        raise unprocessable("password_required", ErrorCode.PASSWORD_REQUIRED)
    if not pw_check:
        if raise_validation_failed:
            raise unprocessable("password_validation_failed", ErrorCode.MISSING_REQUIRED_FIELD, {"reason": "password_check_blank"})
        raise unprocessable("password_check_required", ErrorCode.PASSWORD_CHECK_REQUIRED)
    
    # 비밀번호 형식 검증
    if len(pw) < 8 or len(pw) > 20:
        if raise_validation_failed:
            raise unprocessable("password_validation_failed", ErrorCode.VALIDATION_ERROR, {"reason": "password_too_short"})
        raise unprocessable("invalid_password_format", ErrorCode.INVALID_PASSWORD_FORMAT)
    if not re.search(r"[A-Z]", pw) or not re.search(r"[a-z]", pw) or not re.search(r"[0-9\W_]", pw):
        if raise_validation_failed:
            raise unprocessable("password_validation_failed", ErrorCode.VALIDATION_ERROR, {"reason": "password_invalid_format"})
        raise unprocessable("invalid_password_format", ErrorCode.INVALID_PASSWORD_FORMAT)
    
    if pw != pw_check:
        if raise_validation_failed:
            raise unprocessable("password_validation_failed", ErrorCode.VALIDATION_ERROR, {"reason": "password_mismatch"})
        raise unprocessable("password_mismatch", ErrorCode.PASSWORD_MISMATCH)
    return True

def validate_nickname(nickname: str, raise_validation_failed=False):
    """닉네임 검증. raise_validation_failed=True일 경우 validation_failed 형식으로 반환"""
    if not nickname:
        if raise_validation_failed:
            raise unprocessable("validation_failed", ErrorCode.MISSING_REQUIRED_FIELD, {"field": "nickname", "reason": "nickname_blank"})
        raise unprocessable("nickname_required", ErrorCode.NICKNAME_REQUIRED)
    if NICKNAME_SPACE.search(nickname):
        if raise_validation_failed:
            raise unprocessable("validation_failed", ErrorCode.VALIDATION_ERROR, {"field": "nickname", "reason": "nickname_has_space"})
        raise unprocessable("nickname_contains_space", ErrorCode.NICKNAME_CONTAINS_SPACE)
    if len(nickname) > 10:
        if raise_validation_failed:
            raise unprocessable("validation_failed", ErrorCode.VALIDATION_ERROR, {"field": "nickname", "reason": "nickname_too_long"})
        raise unprocessable("nickname_too_long", ErrorCode.NICKNAME_TOO_LONG, {"max_length": 10})
    return True

def validate_title(title: str):
    if len(title) > 26:
        raise unprocessable("title_too_long", {"max_length": 26})

