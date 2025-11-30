# Wedding OS - Backend

웨딩 플래너를 위한 종합 관리 시스템의 백엔드 서버입니다.

## 📋 프로젝트 개요

Wedding OS는 예비부부를 위한 웨딩 준비 통합 관리 플랫폼입니다. 게시판, 캘린더, 예산 관리, 챗봇, 음성 비서, 업체 매칭 등 다양한 기능을 제공합니다.

## 🛠 기술 스택

- **Framework**: FastAPI 0.121.3
- **Database**: MySQL (PyMySQL)
- **ORM**: SQLAlchemy 2.0.23
- **Authentication**: JWT (python-jose)
- **Admin Panel**: SQLAdmin 0.18.0
- **AI/ML**: 
  - Ollama (LLM)
  - LangChain (Vector DB, RAG)
  - Chroma (Vector Database)
- **Python**: 3.10+

## 📁 프로젝트 구조

```
2.Wedding_OS_back/
├── app/
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   ├── routers/                # API 라우터 (엔드포인트 정의)
│   │   ├── auth_routes.py      # 인증 (로그인, 회원가입)
│   │   ├── user_routes.py      # 사용자 관리
│   │   ├── post_routes.py      # 게시판
│   │   ├── comment_routes.py   # 댓글
│   │   ├── calendar_routes.py  # 캘린더 & 할일
│   │   ├── budget_routes.py    # 예산 관리
│   │   ├── chat_routes.py      # 챗봇
│   │   ├── voice_routes.py     # 음성 비서
│   │   ├── vendor_routes.py    # 업체 매칭
│   │   ├── vector_routes.py    # Vector DB 관리
│   │   ├── admin_dashboard_routes.py  # 관리자 대시보드
│   │   ├── admin_docs_routes.py       # API 문서 뷰어
│   │   └── sql_terminal_routes.py     # SQL 터미널
│   ├── controllers/            # 비즈니스 로직
│   ├── models/                 # 데이터 모델
│   │   ├── db/                 # SQLAlchemy ORM 모델
│   │   └── memory.py           # 메모리 기반 모델 (레거시)
│   ├── services/               # 서비스 레이어
│   │   ├── model_client.py     # AI 모델 서버 클라이언트
│   │   ├── vector_db.py       # Vector DB 서비스
│   │   ├── user_memory_service.py  # 사용자 메모리 레이어
│   │   └── ...
│   ├── core/                   # 핵심 설정
│   │   ├── database.py        # 데이터베이스 연결
│   │   ├── security.py        # JWT 인증
│   │   ├── admin.py           # 관리자 페이지 설정
│   │   └── exceptions.py      # 예외 처리
│   └── schemas.py              # Pydantic 스키마
├── requirements.txt            # Python 패키지 의존성
├── create_tables.py           # 데이터베이스 테이블 생성
└── RENDER_ENV_SETUP.md        # Render 배포 환경 변수 가이드
```

## 🚀 시작하기

### 1. 환경 설정

```bash
# Python 3.10+ 가상환경 생성 (Conda 사용)
conda create -n env_python310 python=3.10
conda activate env_python310

# 의존성 설치
pip install -r requirements.txt
```

### 2. 데이터베이스 설정

```sql
-- MySQL 데이터베이스 생성
CREATE DATABASE WEDDING_PLANNER_OS_DB;
```

```bash
# 테이블 생성
python create_tables.py
```

### 3. 환경 변수 설정

`.env` 파일 생성 (또는 환경 변수로 설정):

```env
# 필수
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/WEDDING_PLANNER_OS_DB
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters-long

# 선택사항
MODEL_API_URL=http://localhost:8102
MODEL_API_PORT=8102
```

⚠️ **보안 주의**: `.env` 파일은 절대 Git에 커밋하지 마세요!

### 4. 서버 실행

```bash
# 개발 모드 (자동 리로드)
uvicorn app.main:app --host 0.0.0.0 --port 8101 --reload

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8101
```

서버가 실행되면:
- **API 문서**: http://localhost:8101/docs
- **관리자 대시보드**: http://localhost:8101/secret_admin/dashboard
- **관리자 페이지**: http://localhost:8101/secret_admin/

## 🔐 인증 시스템

### JWT 토큰 기반 인증

모든 API 요청은 JWT 토큰을 사용합니다:

```bash
# 로그인
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# 응답
{
  "message": "login_success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_id": 1,
    "nickname": "사용자"
  }
}

# 인증이 필요한 API 호출
Authorization: Bearer <access_token>
```

## 📊 주요 기능

### 1. 사용자 관리
- 회원가입 / 로그인
- 프로필 수정
- 프로필 이미지 업로드

### 2. 게시판
- 게시글 CRUD
- 댓글 시스템
- 좋아요 기능
- 이미지 업로드
- AI 기반 게시글 요약 및 감성 분석
- Vector DB 기반 유사 게시글 검색

### 3. 캘린더 & 할일
- 일정 관리 (이벤트, 할일 통합)
- 예식일 설정
- 자동 타임라인 생성
- 우선순위 및 담당자 설정

### 4. 예산 관리
- 예산 항목 관리
- OCR 기반 영수증 처리
- LLM 기반 예산 구조화
- Excel 형식 지원

### 5. 챗봇
- LLM 기반 대화
- Vector DB 기반 사용자 메모리
- LangGraph 기반 자동 정리 파이프라인 (구조 준비)

### 6. 음성 비서
- STT (Speech-to-Text)
- 음성 명령 처리
- LangGraph 기반 자동 정리 (구조 준비)

### 7. 업체 매칭 & 추천
- 웨딩 프로필 기반 매칭
- 규칙 기반 추천 엔진
- 즐겨찾기 기능
- 업체 타입별 상세 정보

### 8. 관리자 기능
- SQLAdmin 기반 데이터베이스 관리
- SQL 터미널 (직접 쿼리 실행)
- 통합 관리자 대시보드
- API 문서 및 ERD 뷰어

## 🗄 데이터베이스

### 주요 테이블

- `users`: 사용자 정보
- `posts`: 게시글
- `comments`: 댓글
- `calendar_events`: 일정 및 할일 (통합)
- `wedding_dates`: 예식일
- `wedding_profiles`: 웨딩 프로필
- `vendors`: 업체 정보
- `favorite_vendors`: 즐겨찾기 업체
- `budget_items`: 예산 항목
- `chat_history`: 챗봇 대화 기록

전체 ERD는 `database_erd_viewer.html`에서 확인할 수 있습니다.

## 🔧 관리자 페이지

### 접근 방법

1. **통합 대시보드**: http://localhost:8101/secret_admin/dashboard
   - 모든 관리 도구에 접근할 수 있는 중앙 페이지

2. **데이터베이스 관리**: http://localhost:8101/secret_admin/
   - SQLAdmin을 통한 테이블 관리

3. **SQL 터미널**: http://localhost:8101/secret_admin/sql-terminal
   - 직접 SQL 쿼리 실행

4. **API 문서**: http://localhost:8101/docs
   - Swagger UI

## 📚 API 문서

- **Swagger UI**: http://localhost:8101/docs
- **ReDoc**: http://localhost:8101/redoc
- **상세 API 레퍼런스**: `api_reference.html` (프론트엔드 디렉토리)

## 🚢 배포 (Render)

Render에 배포할 때는 다음 환경 변수를 설정하세요:

```env
DATABASE_URL=mysql+pymysql://user:pass@host:port/db
JWT_SECRET_KEY=your-secret-key-here
MODEL_API_URL=http://your-model-server.onrender.com  # 선택사항
```

자세한 내용은 `RENDER_ENV_SETUP.md`를 참조하세요.

## 📝 개발 가이드

### 아키텍처 패턴

```
Route (routers/) → Controller (controllers/) → Service (services/) → Model (models/db/)
```

- **Route**: HTTP 요청/응답 처리, 요청 검증
- **Controller**: 비즈니스 로직 처리
- **Service**: 외부 서비스 연동 (AI, Vector DB 등)
- **Model**: 데이터베이스 ORM 모델

### 코드 스타일

- Python 3.10+ 타입 힌팅 사용
- Pydantic 스키마로 요청/응답 검증
- SQLAlchemy ORM 사용
- 예외 처리는 `app/core/exceptions.py`에서 통합 관리

## 🔒 보안

- JWT 토큰 기반 인증
- 환경 변수로 민감 정보 관리
- SQL Injection 방지 (SQLAlchemy ORM 사용)
- CORS 설정으로 프론트엔드 도메인만 허용

## 📄 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다.
