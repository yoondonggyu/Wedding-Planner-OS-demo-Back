# KakaoTechBootcamp-Backend

FastAPI를 이용한 커뮤니티 백엔드 프로젝트

## 프로젝트 구조

### 2-1 단계: Route만 사용
- `main_routes_only.py`: Route만 이용하여 모든 로직 구현
- 모든 비즈니스 로직이 Route 함수 내에 직접 구현
- 메모리 기반 데이터 저장소 사용 (딕셔너리)

### 2-2, 2-3 단계: Route-Controller-Model 구조
- `app/routers/`: Route 레이어 (요청/응답 처리)
- `app/controllers/`: Controller 레이어 (비즈니스 로직)
- `app/models/`: Model 레이어 (데이터 저장소)

### 4번 과제: Route-Controller-Model 패턴 완전 구현
- **Route 레이어** (`app/routers/`): HTTP 요청/응답만 처리
  - 요청 검증 및 응답 포맷팅
  - Controller 호출
  
- **Controller 레이어** (`app/controllers/`): 비즈니스 로직 처리
  - 데이터 검증 및 처리
  - Model과의 상호작용
  - 예외 처리
  
- **Model 레이어** (`app/models/memory.py`): 데이터 저장소
  - **4-1 조건 충족**: DB 사용하지 않음, JSON으로만 반환
  - 메모리 기반 딕셔너리로 데이터 저장
  - Python 객체 → FastAPI가 자동으로 JSON 변환

## 실행 방법

```bash
# 가상환경 활성화
conda activate env_fastapi

# 2-1 단계 실행 (Route만 사용)
uvicorn main_routes_only:app --reload

# 2-2, 2-3, 4번 단계 실행 (Route/Controller/Model 구분)
uvicorn app.main:app --reload
```

## 과제별 구현 내용

### 2-1: Route만 이용한 백엔드
- **파일**: `main_routes_only.py`
- **특징**: 모든 로직이 Route 함수 내에 직접 구현
- **데이터 저장**: Route 파일 내에서 딕셔너리로 관리

### 2-2: Route/Controller 구분
- **파일**: `app/routers/`, `app/controllers/`
- **특징**: Route는 요청/응답만, Controller는 비즈니스 로직 처리

### 2-3: 커뮤니티 백엔드 완성
- **파일**: `app/` 디렉토리 전체
- **특징**: API 명세에 맞게 최종 구현, 예외 처리 보완

### 4번: Route-Controller-Model 패턴
- **파일**: `app/` 디렉토리 전체
- **구조**:
  ```
  Route (routers/) → Controller (controllers/) → Model (models/)
  ```
- **4-1 조건**: Model은 JSON으로만 반환 (DB 사용 안 함)
  - `app/models/memory.py`: 메모리 기반 딕셔너리 저장소
  - Python 객체를 FastAPI가 자동으로 JSON으로 변환

#### 4번 과제 상세 설명

**Route-Controller-Model 패턴**은 3계층 아키텍처로 구현되었습니다:

1. **Route 레이어** (`app/routers/`)
   - HTTP 요청/응답 처리
   - 요청 파라미터 검증
   - Controller 호출
   - 응답 포맷팅

2. **Controller 레이어** (`app/controllers/`)
   - 비즈니스 로직 처리
   - 데이터 검증 및 변환
   - Model과의 상호작용
   - 예외 처리

3. **Model 레이어** (`app/models/memory.py`)
   - 데이터 저장소 (메모리 기반)
   - **4-1 조건 충족**: DB 사용하지 않음
   - 딕셔너리로 데이터 저장
   - Python 객체 반환 (FastAPI가 자동으로 JSON 변환)

#### 데이터 흐름 예시

```
클라이언트 요청
    ↓
Route (post_routes.py)
    ↓
Controller (post_controller.py)
    ↓
Model (memory.py) - JSON 데이터 반환
    ↓
Controller (데이터 처리)
    ↓
Route (응답 포맷팅)
    ↓
클라이언트 응답 (JSON)
```

## 데이터베이스 설정

### MySQL 데이터베이스 생성
```sql
CREATE DATABASE WEDDING_PLANNER_OS_DB;
```

### 테이블 생성
```bash
python create_tables.py
```

### 데이터베이스 관리자 페이지
- **URL**: `http://localhost:8001/secret_admin`
- SQLAdmin을 사용한 웹 기반 관리 인터페이스
- 사용자, 게시글, 댓글, 태그 등을 관리할 수 있습니다

## 인증 시스템

### JWT 토큰 기반 인증
- 로그인 시 JWT 토큰이 발급됩니다
- 토큰 유효기간: 7일
- 모든 인증이 필요한 API 요청에 `Authorization: Bearer <token>` 헤더를 포함해야 합니다

### 로그인 응답 예시
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

## API 문서

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## 주요 기능

- 사용자 인증 (로그인, 회원가입)
- 사용자 관리 (프로필 수정, 비밀번호 변경, 회원 탈퇴)
- 게시글 CRUD
- 댓글 CRUD
- 좋아요 기능
- 파일 업로드

