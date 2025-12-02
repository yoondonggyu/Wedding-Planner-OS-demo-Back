# Wedding OS API Specification

## 목차
1. [인증 (Authentication)](#인증-authentication)
2. [사용자 (User)](#사용자-user)
3. [게시판 (Posts)](#게시판-posts)
4. [댓글 (Comments)](#댓글-comments)
5. [챗봇 (Chat)](#챗봇-chat)
6. [캘린더 (Calendar)](#캘린더-calendar)
7. [예산서 (Budget)](#예산서-budget)
8. [음성 비서 (Voice)](#음성-비서-voice)
9. [업체 추천 (Vendor)](#업체-추천-vendor)
10. [Vector DB](#vector-db)
11. [스키마 (Schemas)](#스키마-schemas)

---

## 인증 (Authentication)

### 로그인
- **Method**: `POST`
- **Endpoint**: `/api/auth/login`
- **Request Body**: `LoginReq` (스키마 참조)
- **Success Response (200)**:
```json
{
  "message": "login_success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_id": 1,
    "nickname": "사용자",
    "profile_image_url": "https://..."
  }
}
```

### 회원가입
- **Method**: `POST`
- **Endpoint**: `/api/auth/signup`
- **Request Body**: `SignupReq` (스키마 참조)
- **Success Response (201)**:
```json
{
  "message": "register_success",
  "data": {
    "user_id": 1
  }
}
```

---

## 사용자 (User)

### 프로필 조회
- **Method**: `GET`
- **Endpoint**: `/api/users/profile`
- **Headers**: `Authorization: Bearer <token>`
- **Success Response (200)**:
```json
{
  "message": "get_profile_success",
  "data": {
    "user_id": 1,
    "email": "user@example.com",
    "nickname": "사용자",
    "profile_image_url": "https://..."
  }
}
```

### 프로필 수정
- **Method**: `PATCH`
- **Endpoint**: `/api/users/profile`
- **Request Body**: `NicknamePatchReq` (스키마 참조)

### 비밀번호 변경
- **Method**: `PATCH`
- **Endpoint**: `/api/users/password`
- **Request Body**: `PasswordUpdateReq` (스키마 참조)

---

## 게시판 (Posts)

### 게시글 목록 조회
- **Method**: `GET`
- **Endpoint**: `/api/posts?page=1&limit=10&board_type=couple`
- **Query Parameters**:
  - `page`: 페이지 번호 (기본값: 1)
  - `limit`: 페이지당 항목 수 (기본값: 10)
  - `board_type`: 게시판 타입 (`couple`, `planner`, `preparation`)

### 게시글 작성
- **Method**: `POST`
- **Endpoint**: `/api/posts`
- **Request Body**: `PostCreateReq` (스키마 참조)
- **Success Response (201)**:
```json
{
  "message": "create_post_success",
  "data": {
    "post_id": 1
  }
}
```

### 게시글 수정
- **Method**: `PATCH`
- **Endpoint**: `/api/posts/{post_id}`
- **Request Body**: `PostUpdateReq` (스키마 참조)

### 게시글 삭제
- **Method**: `DELETE`
- **Endpoint**: `/api/posts/{post_id}`

### 게시글 좋아요
- **Method**: `POST`
- **Endpoint**: `/api/posts/{post_id}/like`

---

## 댓글 (Comments)

### 댓글 작성
- **Method**: `POST`
- **Endpoint**: `/api/posts/{post_id}/comments`
- **Request Body**: `CommentCreateReq` (스키마 참조)

### 댓글 수정
- **Method**: `PATCH`
- **Endpoint**: `/api/posts/{post_id}/comments/{comment_id}`
- **Request Body**: `CommentUpdateReq` (스키마 참조)

### 댓글 삭제
- **Method**: `DELETE`
- **Endpoint**: `/api/posts/{post_id}/comments/{comment_id}`

---

## 챗봇 (Chat)

### 챗봇 대화 (스트리밍)
- **Method**: `POST`
- **Endpoint**: `/api/chat`
- **Request Body**: `ChatRequest` (스키마 참조)
- **Response**: Server-Sent Events (스트리밍)

### 챗봇 대화 (비스트리밍)
- **Method**: `POST`
- **Endpoint**: `/api/chat/simple`
- **Request Body**: `ChatRequest` (스키마 참조)

---

## 캘린더 (Calendar)

### 일정 조회
- **Method**: `GET`
- **Endpoint**: `/api/calendar/events?start_date=2025-01-01&end_date=2025-12-31`

### 일정 생성
- **Method**: `POST`
- **Endpoint**: `/api/calendar/events`
- **Request Body**: `CalendarEventCreateReq` (스키마 참조)

### 일정 수정
- **Method**: `PATCH`
- **Endpoint**: `/api/calendar/events/{event_id}`
- **Request Body**: `CalendarEventUpdateReq` (스키마 참조)

### 일정 삭제
- **Method**: `DELETE`
- **Endpoint**: `/api/calendar/events/{event_id}`

### 예식일 설정
- **Method**: `POST`
- **Endpoint**: `/api/calendar/wedding-date`
- **Request Body**: `WeddingDateSetReq` (스키마 참조)

### 타임라인 자동 생성
- **Method**: `POST`
- **Endpoint**: `/api/calendar/timeline/generate`
- **Request Body**: `TimelineGenerateReq` (스키마 참조)

### 할일 생성
- **Method**: `POST`
- **Endpoint**: `/api/calendar/todos`
- **Request Body**: `TodoCreateReq` (스키마 참조)

### 할일 수정
- **Method**: `PATCH`
- **Endpoint**: `/api/calendar/todos/{todo_id}`
- **Request Body**: `TodoUpdateReq` (스키마 참조)

---

## 예산서 (Budget)

### 예산 항목 생성
- **Method**: `POST`
- **Endpoint**: `/api/budget/items`
- **Request Body**: `BudgetItemCreateReq` (스키마 참조)

### 예산 항목 수정
- **Method**: `PUT`
- **Endpoint**: `/api/budget/items/{item_id}`
- **Request Body**: `BudgetItemUpdateReq` (스키마 참조)

### 예산 항목 삭제
- **Method**: `DELETE`
- **Endpoint**: `/api/budget/items/{item_id}`

### 총 예산 설정
- **Method**: `POST`
- **Endpoint**: `/api/budget/total`
- **Request Body**: `TotalBudgetSetReq` (스키마 참조)

### 영수증 OCR 처리
- **Method**: `POST`
- **Endpoint**: `/api/budget/process-receipt`
- **Request**: Multipart Form-data (이미지 파일)

---

## 음성 비서 (Voice)

### 음성 처리
- **Method**: `POST`
- **Endpoint**: `/api/voice/process`
- **Request Body**: `VoiceProcessReq` (스키마 참조)

### 음성 답변 생성
- **Method**: `POST`
- **Endpoint**: `/api/voice/response?query=...&user_id=1`

---

## 업체 추천 (Vendor)

### 결혼식 프로필 생성
- **Method**: `POST`
- **Endpoint**: `/api/vendors/profiles`
- **Request Body**: `WeddingProfileCreateReq` (스키마 참조)

### 결혼식 프로필 수정
- **Method**: `PATCH`
- **Endpoint**: `/api/vendors/profiles/{profile_id}`
- **Request Body**: `WeddingProfileUpdateReq` (스키마 참조)

### 업체 추천
- **Method**: `POST`
- **Endpoint**: `/api/vendors/recommend`
- **Request Body**: `VendorRecommendReq` (스키마 참조)

### 찜하기
- **Method**: `POST`
- **Endpoint**: `/api/vendors/favorites`
- **Request Body**: `FavoriteVendorCreateReq` (스키마 참조)

---

## Vector DB

### 게시글 벡터 검색
- **Method**: `GET`
- **Endpoint**: `/api/vector/posts/search?query={검색어}&k={개수}&board_type={타입}`
- **Headers**: `Authorization: Bearer <token>`

### 게시판 Vector DB 통계
- **Method**: `GET`
- **Endpoint**: `/api/vector/posts/stats`
- **Headers**: `Authorization: Bearer <token>`

### 기존 게시글 일괄 벡터화
- **Method**: `POST`
- **Endpoint**: `/api/vector/posts/batch-vectorize?limit={개수}`
- **Headers**: `Authorization: Bearer <token>`

### 사용자 메모리 검색
- **Method**: `GET`
- **Endpoint**: `/api/vector/user/memory?query={검색어}&k={개수}&preference_type={타입}`
- **Headers**: `Authorization: Bearer <token>`

### 사용자 프로필 요약
- **Method**: `GET`
- **Endpoint**: `/api/vector/user/profile`
- **Headers**: `Authorization: Bearer <token>`

---

## 스키마 (Schemas)

이 섹션에서는 API에서 사용하는 모든 Request/Response 스키마를 정의합니다.

### 인증 (Auth)

#### LoginReq
로그인 요청 스키마
```json
{
  "email": "string",
  "password": "string"
}
```
- `email` (string, required): 사용자 이메일
- `password` (string, required): 사용자 비밀번호

#### LoginRes
로그인 응답 스키마
```json
{
  "message": "login_success",
  "data": {
    "access_token": "string",
    "token_type": "bearer",
    "user_id": 1,
    "nickname": "string",
    "profile_image_url": "string"
  }
}
```

#### SignupReq
회원가입 요청 스키마
```json
{
  "email": "string",
  "password": "string",
  "password_check": "string",
  "nickname": "string",
  "profile_image_url": "string (HttpUrl)"
}
```
- `email` (string, required): 사용자 이메일
- `password` (string, required): 비밀번호 (8-20자, 대소문자+특수문자 포함)
- `password_check` (string, required): 비밀번호 확인
- `nickname` (string, required): 닉네임 (최대 10자, 공백 없음)
- `profile_image_url` (HttpUrl, required): 프로필 이미지 URL

---

### 사용자 (User)

#### NicknamePatchReq
프로필 수정 요청 스키마
```json
{
  "nickname": "string",
  "profile_image_url": "string | null"
}
```
- `nickname` (string, required): 수정할 닉네임
- `profile_image_url` (string, optional): 프로필 이미지 URL

#### PasswordUpdateReq
비밀번호 변경 요청 스키마
```json
{
  "old_password": "string",
  "password": "string",
  "password_check": "string"
}
```
- `old_password` (string, required): 기존 비밀번호
- `password` (string, required): 새 비밀번호
- `password_check` (string, required): 새 비밀번호 확인

---

### 게시판 (Posts)

#### PostCreateReq
게시글 작성 요청 스키마
```json
{
  "title": "string (max 2000자)",
  "content": "string",
  "image_url": "string (HttpUrl) | null",
  "board_type": "string (기본값: 'couple')"
}
```
- `title` (string, required, max_length: 2000): 게시글 제목
- `content` (string, required): 게시글 내용
- `image_url` (HttpUrl, optional): 이미지 URL
- `board_type` (string, optional, default: "couple"): 게시판 타입 (`couple`, `planner`, `preparation`)

#### PostUpdateReq
게시글 수정 요청 스키마
```json
{
  "title": "string | null",
  "content": "string | null",
  "image_url": "string (HttpUrl) | null"
}
```
- 모든 필드는 선택적 (optional)

---

### 댓글 (Comments)

#### CommentCreateReq
댓글 작성 요청 스키마
```json
{
  "content": "string"
}
```
- `content` (string, required): 댓글 내용

#### CommentUpdateReq
댓글 수정 요청 스키마
```json
{
  "content": "string"
}
```
- `content` (string, required): 수정할 댓글 내용

---

### 챗봇 (Chat)

#### ChatRequest
챗봇 대화 요청 스키마
```json
{
  "message": "string",
  "user_id": "integer | null",
  "include_context": "boolean (기본값: true)"
}
```
- `message` (string, required): 사용자 메시지
- `user_id` (integer, optional): 사용자 ID (JWT 토큰에서 자동 추출 가능)
- `include_context` (boolean, optional, default: true): 개인 데이터 포함 여부

---

### 캘린더 (Calendar)

#### CalendarEventCreateReq
일정 생성 요청 스키마
```json
{
  "title": "string",
  "description": "string | null",
  "start_date": "string (YYYY-MM-DD)",
  "end_date": "string (YYYY-MM-DD) | null",
  "start_time": "string (HH:MM) | null",
  "end_time": "string (HH:MM) | null",
  "location": "string | null",
  "category": "string (기본값: 'general')",
  "priority": "string (기본값: 'medium')",
  "assignee": "string (기본값: 'both')",
  "reminder_days": "array[integer] (기본값: [])",
  "wedding_d_day": "string (YYYY-MM-DD) | null",
  "d_day_offset": "integer | null"
}
```
- `title` (string, required): 일정 제목
- `description` (string, optional): 일정 설명
- `start_date` (string, required, format: YYYY-MM-DD): 시작 날짜
- `end_date` (string, optional, format: YYYY-MM-DD): 종료 날짜
- `start_time` (string, optional, format: HH:MM): 시작 시간
- `end_time` (string, optional, format: HH:MM): 종료 시간
- `location` (string, optional): 장소
- `category` (string, optional, default: "general"): 카테고리
- `priority` (string, optional, default: "medium"): 우선순위 (`high`, `medium`, `low`)
- `assignee` (string, optional, default: "both"): 담당자 (`groom`, `bride`, `both`)
- `reminder_days` (array[integer], optional): 리마인더 일수 리스트
- `wedding_d_day` (string, optional): 예식일
- `d_day_offset` (integer, optional): 예식일로부터의 오프셋 (일수)

#### CalendarEventUpdateReq
일정 수정 요청 스키마
```json
{
  "title": "string | null",
  "description": "string | null",
  "start_date": "string (YYYY-MM-DD) | null",
  "end_date": "string (YYYY-MM-DD) | null",
  "start_time": "string (HH:MM) | null",
  "end_time": "string (HH:MM) | null",
  "location": "string | null",
  "category": "string | null",
  "priority": "string | null",
  "assignee": "string | null",
  "progress": "integer (0-100) | null",
  "is_completed": "boolean | null",
  "reminder_days": "array[integer] | null"
}
```
- 모든 필드는 선택적 (optional)
- `progress` (integer, optional): 진행률 (0-100)
- `is_completed` (boolean, optional): 완료 여부

#### TodoCreateReq
할일 생성 요청 스키마
```json
{
  "title": "string",
  "description": "string | null",
  "priority": "string (기본값: 'medium')",
  "assignee": "string (기본값: 'both')",
  "due_date": "string (YYYY-MM-DD) | null",
  "event_id": "integer | null"
}
```
- `title` (string, required): 할일 제목
- `description` (string, optional): 할일 설명
- `priority` (string, optional, default: "medium"): 우선순위 (`high`, `medium`, `low`)
- `assignee` (string, optional, default: "both"): 담당자 (`groom`, `bride`, `both`)
- `due_date` (string, optional, format: YYYY-MM-DD): 마감일
- `event_id` (integer, optional): 연결된 일정 ID

#### TodoUpdateReq
할일 수정 요청 스키마
```json
{
  "title": "string | null",
  "description": "string | null",
  "priority": "string | null",
  "assignee": "string | null",
  "progress": "integer (0-100) | null",
  "due_date": "string (YYYY-MM-DD) | null",
  "is_completed": "boolean | null"
}
```
- 모든 필드는 선택적 (optional)
- `progress` (integer, optional): 진행률 (0-100)
- `is_completed` (boolean, optional): 완료 여부

#### WeddingDateSetReq
예식일 설정 요청 스키마
```json
{
  "wedding_date": "string (YYYY-MM-DD)"
}
```
- `wedding_date` (string, required, format: YYYY-MM-DD): 예식일

#### TimelineGenerateReq
타임라인 자동 생성 요청 스키마
```json
{
  "wedding_date": "string (YYYY-MM-DD)",
  "user_preferences": "object | null"
}
```
- `wedding_date` (string, required, format: YYYY-MM-DD): 예식일
- `user_preferences` (object, optional): LLM 개인화를 위한 사용자 선호도

---

### 예산서 (Budget)

#### BudgetItemCreateReq
예산 항목 생성 요청 스키마
```json
{
  "item_name": "string",
  "category": "string (기본값: 'etc')",
  "estimated_budget": "number (float)",
  "actual_expense": "number (float, 기본값: 0.0)",
  "unit": "string | null",
  "quantity": "number (float, 기본값: 1.0)",
  "notes": "string | null",
  "payer": "string (기본값: 'both')",
  "payment_schedule": "array[object] (기본값: [])"
}
```
- `item_name` (string, required): 항목명
- `category` (string, optional, default: "etc"): 카테고리 (`hall`, `dress`, `studio`, `snap`, `honeymoon`, `etc`)
- `estimated_budget` (float, required): 예상 예산
- `actual_expense` (float, optional, default: 0.0): 실제 지출
- `unit` (string, optional): 단위 (인원, 시간 등)
- `quantity` (float, optional, default: 1.0): 수량
- `notes` (string, optional): 비고
- `payer` (string, optional, default: "both"): 담당자 (`groom`, `bride`, `both`)
- `payment_schedule` (array[object], optional): 계약금/중도금/잔금 일정

#### BudgetItemUpdateReq
예산 항목 수정 요청 스키마
```json
{
  "item_name": "string | null",
  "category": "string | null",
  "estimated_budget": "number (float) | null",
  "actual_expense": "number (float) | null",
  "unit": "string | null",
  "quantity": "number (float) | null",
  "notes": "string | null",
  "payer": "string | null",
  "payment_schedule": "array[object] | null"
}
```
- 모든 필드는 선택적 (optional)

#### TotalBudgetSetReq
총 예산 설정 요청 스키마
```json
{
  "total_budget": "number (float)"
}
```
- `total_budget` (float, required): 총 예산 (원)

#### BudgetUploadReq
예산 파일 업로드 요청 스키마
```json
{
  "file_type": "string (기본값: 'excel')"
}
```
- `file_type` (string, optional, default: "excel"): 파일 타입 (`excel`, `csv`, `image` (OCR))

---

### 음성 비서 (Voice)

#### VoiceProcessReq
음성 처리 요청 스키마
```json
{
  "audio_data": "string (base64) | null",
  "text": "string | null",
  "user_id": "integer",
  "auto_organize": "boolean (기본값: true)"
}
```
- `audio_data` (string, optional): base64 인코딩된 오디오 데이터
- `text` (string, optional): 직접 텍스트 입력 (STT 우회)
- `user_id` (integer, required): 사용자 ID
- `auto_organize` (boolean, optional, default: true): 자동 정리 파이프라인 실행 여부

**참고**: `audio_data`와 `text` 중 하나는 반드시 제공되어야 합니다.

---

### 업체 추천 (Vendor)

#### WeddingProfileCreateReq
결혼식 프로필 생성 요청 스키마
```json
{
  "wedding_date": "string (YYYY-MM-DD)",
  "guest_count_category": "string",
  "total_budget": "number (float)",
  "location_city": "string",
  "location_district": "string",
  "style_indoor": "boolean (기본값: true)",
  "style_outdoor": "boolean (기본값: false)",
  "outdoor_rain_plan_required": "boolean (기본값: false)"
}
```
- `wedding_date` (string, required, format: YYYY-MM-DD): 예식일
- `guest_count_category` (string, required): 하객 수 카테고리 (`SMALL`, `MEDIUM`, `LARGE`)
- `total_budget` (float, required): 전체 예산 (원)
- `location_city` (string, required): 시/도
- `location_district` (string, required): 구/군
- `style_indoor` (boolean, optional, default: true): 실내 결혼식 여부
- `style_outdoor` (boolean, optional, default: false): 야외 결혼식 여부
- `outdoor_rain_plan_required` (boolean, optional, default: false): 야외 결혼식 시 우천 대안 필수 여부

#### WeddingProfileUpdateReq
결혼식 프로필 수정 요청 스키마
```json
{
  "wedding_date": "string (YYYY-MM-DD) | null",
  "guest_count_category": "string | null",
  "total_budget": "number (float) | null",
  "location_city": "string | null",
  "location_district": "string | null",
  "style_indoor": "boolean | null",
  "style_outdoor": "boolean | null",
  "outdoor_rain_plan_required": "boolean | null"
}
```
- 모든 필드는 선택적 (optional)

#### VendorRecommendReq
업체 추천 요청 스키마
```json
{
  "wedding_profile_id": "integer",
  "vendor_type": "string | null",
  "min_price": "number (float) | null",
  "max_price": "number (float) | null",
  "location_city": "string | null",
  "has_rain_plan": "boolean | null",
  "sort": "string (기본값: 'score_desc')"
}
```
- `wedding_profile_id` (integer, required): 결혼식 프로필 ID
- `vendor_type` (string, optional): 업체 타입 (`IPHONE_SNAP`, `MC`, `SINGER`, `STUDIO_PREWEDDING`, `VENUE_OUTDOOR`)
- `min_price` (float, optional): 최소 가격 필터
- `max_price` (float, optional): 최대 가격 필터
- `location_city` (string, optional): 지역 필터
- `has_rain_plan` (boolean, optional): 우천 대안 필수 여부 (VENUE_OUTDOOR 한정)
- `sort` (string, optional, default: "score_desc"): 정렬 방식 (`score_desc`, `price_asc`, `price_desc`, `review_desc`)

#### FavoriteVendorCreateReq
찜하기 요청 스키마
```json
{
  "wedding_profile_id": "integer",
  "vendor_id": "integer"
}
```
- `wedding_profile_id` (integer, required): 결혼식 프로필 ID
- `vendor_id` (integer, required): 업체 ID

---

## 공통 응답 형식

모든 API 응답은 다음 형식을 따릅니다:

```json
{
  "message": "string",
  "data": "object | null"
}
```

- `message`: 응답 메시지 코드 (예: `"login_success"`, `"create_post_success"`)
- `data`: 응답 데이터 (성공 시 데이터 객체, 실패 시 `null`)

---

## 공통 에러 코드

| Status Code | Message | Description |
|:---|:---|:---|
| 400 | `bad_request` | 잘못된 요청 |
| 401 | `unauthorized` | 인증 필요 |
| 403 | `forbidden` | 권한 없음 |
| 404 | `not_found` | 리소스 없음 |
| 409 | `conflict` | 충돌 (중복 등) |
| 413 | `payload_too_large` | 페이로드 너무 큼 |
| 422 | `invalid_request` | 유효성 검사 실패 |
| 500 | `internal_server_error` | 서버 내부 오류 |

---

## 인증

모든 인증이 필요한 API는 JWT 토큰을 사용합니다.

### 토큰 사용 방법
```
Authorization: Bearer <access_token>
```

### 토큰 발급
- 로그인 성공 시 `access_token`이 발급됩니다.
- 토큰 유효기간: 7일

---

## API 문서

- **Swagger UI**: `http://localhost:8101/docs`
- **ReDoc**: `http://localhost:8101/redoc`

Swagger UI에서 모든 스키마를 시각적으로 확인할 수 있습니다.



