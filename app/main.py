from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_routes, user_routes, post_routes, comment_routes, chat_routes, calendar_routes, budget_routes, voice_routes
from app.core.exceptions import APIError
from app.core.formatter import create_json_response

app = FastAPI(title="Wedding OS API")

# CORS 설정 - 프론트엔드(8000번 포트)에서 API 호출을 위해 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # 프론트엔드 포트 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 루트 경로 - API 정보
@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Wedding OS API",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_prefix": "/api"
    }

# 라우터 등록
app.include_router(auth_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(post_routes.router, prefix="/api")
app.include_router(comment_routes.router, prefix="/api")
app.include_router(chat_routes.router, prefix="/api")
app.include_router(calendar_routes.router, prefix="/api")
app.include_router(budget_routes.router, prefix="/api")
app.include_router(voice_routes.router, prefix="/api")

# 전역 예외 처리
@app.exception_handler(APIError)
async def handle_api_error(_: Request, exc: APIError):
    """커스텀 API 에러 처리"""
    return create_json_response(exc.status_code, exc.message, exc.data)

@app.exception_handler(RequestValidationError)
async def handle_validation_error(_: Request, exc: RequestValidationError):
    """Pydantic 검증 에러 처리"""
    errors = exc.errors()
    if errors:
        # 첫 번째 에러 메시지 사용
        error = errors[0]
        field = ".".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "invalid_request")
        
        # 필드별 에러 메시지 매핑
        error_messages = {
            "email": "invalid_email_format",
            "password": "invalid_password_format",
            "nickname": "invalid_request",
            "title": "invalid_request",
            "content": "invalid_request",
        }
        
        # 필드명에서 에러 타입 추출
        for key, error_msg in error_messages.items():
            if key in field.lower():
                return create_json_response(422, error_msg, None)
        
        return create_json_response(422, "invalid_request", None)
    
    return create_json_response(422, "invalid_request", None)

@app.exception_handler(Exception)
async def handle_unexpected(_: Request, exc: Exception):
    """예상치 못한 서버 내부 오류 처리"""
    return create_json_response(500, "internal_server_error", None)
