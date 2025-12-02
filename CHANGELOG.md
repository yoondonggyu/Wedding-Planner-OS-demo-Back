# 변경 이력 (Changelog)

## [2025-01-XX] 데이터베이스 연동 및 JWT 인증 구현

### 주요 변경사항

#### 1. MySQL 데이터베이스 연동
- **메모리 기반 저장소 → MySQL 데이터베이스 전환**
- SQLAlchemy ORM을 사용한 데이터베이스 모델 구현
- 다음 테이블 생성:
  - `users`: 사용자 정보
  - `posts`: 게시글
  - `comments`: 댓글
  - `post_likes`: 게시글 좋아요
  - `tags`: 태그
  - `post_tags`: 게시글-태그 연결 (Many-to-Many)

#### 2. JWT 토큰 기반 인증 시스템
- **기존**: 헤더 기반 인증 (`x_user_id`)
- **변경**: JWT 토큰 기반 인증 (`Authorization: Bearer <token>`)
- 로그인 시 JWT 토큰 발급 (유효기간: 7일)
- 프론트엔드에서 토큰을 localStorage에 저장하여 세션 유지
- 페이지 새로고침 후에도 로그인 상태 유지

#### 3. 데이터베이스 관리자 페이지
- SQLAdmin을 사용한 웹 기반 관리자 페이지 추가
- 접속 URL: `http://localhost:8001/secret_admin`
- 관리 가능한 항목:
  - 사용자 관리
  - 게시글 관리
  - 댓글 관리
  - 좋아요 관리
  - 태그 관리

### 기술 스택 추가
- `sqlalchemy==2.0.23`: ORM
- `pymysql==1.1.0`: MySQL 드라이버
- `sqladmin==0.18.0`: 관리자 페이지
- `pyjwt==2.8.0`: JWT 토큰 생성/검증
- `python-jose[cryptography]==3.3.0`: JWT 토큰 처리

### 파일 구조 변경

#### 새로 생성된 파일
- `app/core/database.py`: 데이터베이스 연결 설정
- `app/models/db/`: SQLAlchemy 모델
  - `user.py`: User 모델
  - `post.py`: Post, PostLike, Tag 모델
  - `comment.py`: Comment 모델
- `create_tables.py`: 데이터베이스 테이블 생성 스크립트
- `test_db_connection.py`: 데이터베이스 연결 테스트 스크립트

#### 수정된 파일
- `app/core/security.py`: JWT 토큰 생성/검증 로직 추가
- `app/controllers/auth_controller.py`: JWT 토큰 발급
- `app/controllers/user_controller.py`: DB 모델 사용
- `app/controllers/post_controller.py`: DB 모델 사용
- `app/controllers/comment_controller.py`: DB 모델 사용
- `app/routers/*.py`: DB 의존성 추가 및 JWT 인증 적용
- `app/core/admin.py`: SQLAdmin 설정
- `app/main.py`: Admin 페이지 등록

### 데이터베이스 설정

#### 데이터베이스 생성
```sql
CREATE DATABASE WEDDING_PLANNER_OS_DB;
```

#### 테이블 생성
```bash
cd 2.Wedding_OS_back
python create_tables.py
```

#### 연결 정보
- 호스트: `localhost:3306`
- 데이터베이스: `WEDDING_PLANNER_OS_DB`
- 설정 파일: `app/core/database.py`

### API 변경사항

#### 인증 방식 변경
- **기존**: `x_user_id` 헤더로 사용자 식별
- **변경**: `Authorization: Bearer <JWT_TOKEN>` 헤더 사용

#### 로그인 응답 형식 변경
```json
{
  "message": "login_success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_id": 1,
    "nickname": "사용자",
    "profile_image_url": "..."
  }
}
```

### 프론트엔드 변경사항
- `apiFetch()` 헬퍼 함수 추가: 모든 API 요청에 JWT 토큰 자동 포함
- 로그인 시 `access_token`을 localStorage에 저장
- 페이지 새로고침 시 토큰으로 자동 인증

### 마이그레이션 가이드

#### 기존 메모리 데이터
- 메모리 기반 데이터는 서버 재시작 시 초기화됨
- 데이터베이스로 전환 후 기존 데이터는 마이그레이션 필요

#### 환경 변수 설정 (권장)
프로덕션 환경에서는 다음을 환경 변수로 설정:
- `DATABASE_URL`: 데이터베이스 연결 문자열
- `JWT_SECRET_KEY`: JWT 토큰 서명 키

### 보안 개선사항
- 비밀번호는 평문 저장 (향후 해싱 필요)
- JWT 토큰 서명 키는 환경 변수로 관리 권장
- CORS 설정 확인 필요

### 향후 개선 계획
- [ ] 비밀번호 해싱 (bcrypt)
- [ ] 리프레시 토큰 구현
- [ ] 토큰 만료 시 자동 갱신
- [ ] 환경 변수 기반 설정 관리
- [ ] 데이터베이스 마이그레이션 도구 (Alembic)






