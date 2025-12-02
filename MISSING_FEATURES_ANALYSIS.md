# "상" 우선순위 누락 기능 분석 보고서

## 📊 현재 구현 상태 vs 명세서 비교

### ✅ 구현 완료된 "상" 우선순위 기능

#### 1. 게시판
- ✅ **LLM Summarization (리뷰 요약)**: `app/services/model_client.py`의 `summarize_text()` 함수
- ✅ **NLP 카테고리 분류(자동 태깅)**: `app/services/model_client.py`의 `auto_tag_text()` 함수

#### 2. 챗봇
- ✅ **LLM Model (대화/요약/추천)**: `app/services/model_client.py`의 `chat_with_model()` 함수
- ✅ **RAG (기본 구조)**: `app/services/chat_service.py`의 `build_rag_prompt()` 함수 (단, Vector DB 검색 없이 단순 컨텍스트만 사용)

#### 3. 캘린더
- ✅ **LLM 기반 개인화 일정 추천**: `app/services/calendar_service.py`의 `generate_personalized_timeline()` 함수
- ✅ **일정 구조화 엔진 (기본)**: 일정 데이터 구조화는 있으나 표준화된 JSON Schema는 미완성

#### 4. 음성 비서
- ✅ **STT(Speech-to-Text)**: `app/services/stt_service.py`의 `transcribe_audio()` 함수 (Whisper 기반)
- ✅ **LLM(웨딩 전용 프롬프트 + Memory 연동)**: `app/services/voice_service.py`의 `analyze_intent_and_organize()` 함수

#### 5. 예산서
- ✅ **OCR (PaddleOCR / Tesseract)**: `app/services/ocr_service.py`의 `extract_text_from_image()` 함수
- ✅ **LLM 기반 테이블 구조화 모델**: `app/services/budget_service.py`의 `structure_text_with_llm()` 함수
- ✅ **Pandas → Excel / CSV Export**: `app/routers/budget_routes.py`의 `export_to_excel()` 함수

#### 6. 업체 매칭 & 추천
- ✅ **추천 엔진 (규칙 기반)**: `app/controllers/vendor_controller.py`의 매칭 점수 계산 로직
- ✅ **Vendor / WeddingProfile / FavoriteVendor 데이터 모델링**: `app/models/db/vendor.py`
- ✅ **REST API 설계 (FastAPI)**: `app/routers/vendor_routes.py`

---

## ❌ 누락된 "상" 우선순위 기능

### 1. 게시판 - Embedding Model + Vector DB ⚠️ **핵심 누락**

**현재 상태:**
- Vector DB 관련 코드가 전혀 없음
- Embedding 모델 사용 없음
- 게시판 검색이 단순 텍스트 매칭만 가능

**필요한 구현:**
- Embedding 모델 통합 (예: `nomic-embed-text`, `sentence-transformers`)
- Vector DB 설정 (예: Chroma, FAISS, Qdrant)
- 게시판 게시글 자동 벡터화 및 저장
- 벡터 검색 API (`/api/posts/search?query=...`)
- RAG 검색을 위한 게시판 데이터 벡터화

**영향:**
- 챗봇 RAG 성능 저하 (게시판 데이터 검색 불가)
- "비슷한 커플 후기 추천" 기능 불가능
- 웨딩 지식 데이터베이스 구축 불가

---

### 2. 챗봇 - User Memory Layer (Vector DB 기반) ⚠️ **핵심 누락**

**현재 상태:**
- `app/services/chat_service.py`의 `get_user_context()`는 단순 메모리 기반
- 사용자 선호도/패턴을 지속적으로 저장하는 구조 없음
- Vector DB 기반 사용자 프로필 없음

**필요한 구현:**
- 사용자별 Vector DB 컬렉션 생성
- 사용자 대화/선호도/패턴을 Embedding으로 저장
- 사용자 메모리 검색 기능 (`get_user_memory()`)
- 예산 스타일, 좋아하는 컨셉, 일정 패턴, 갈등 포인트 저장

**영향:**
- 개인화된 추천 불가능
- 장기적인 사용자 맞춤형 서비스 불가
- 챗봇이 사용자 성향을 기억하지 못함

---

### 3. 챗봇 - LangGraph 기반 자동 정리 파이프라인 ⚠️ **핵심 누락**

**현재 상태:**
- `app/services/chat_service.py`는 단순 LLM 호출만 수행
- 자동 정리 파이프라인 없음
- 챗봇 대화 → 정리 → 일정/예산 DB 자동 반영 기능 없음

**필요한 구현:**
- LangGraph 파이프라인 설계 및 구현
- 챗봇 대화 분석 → 의도 파악 → 자동 정리 → DB 반영 워크플로우
- 예: "다음 주 토요일에 스튜디오 투어 일정 잡아줘" → 자동으로 캘린더에 추가

**영향:**
- 챗봇이 단순 대화만 가능, 실제 작업 수행 불가
- 사용자가 수동으로 일정/예산을 입력해야 함

---

### 4. 캘린더 - User Memory + Vector DB 기반 일정 컨텍스트 ⚠️ **중요 누락**

**현재 상태:**
- `app/services/calendar_service.py`는 기본 타임라인만 생성
- 사용자 일정 패턴 학습 없음
- Vector DB 기반 일정 컨텍스트 없음

**필요한 구현:**
- 사용자 일정 패턴을 Vector DB에 저장
- "보통 주말 일정 선호" 같은 규칙 자동 습득
- 일정 생성 시 사용자 패턴 반영

**영향:**
- 개인화된 일정 추천 품질 저하
- 사용자 선호도를 반영한 일정 생성 불가

---

### 5. 음성 비서 - 자동 정리 파이프라인(LangGraph 기반) ⚠️ **중요 누락**

**현재 상태:**
- `app/services/voice_service.py`의 `execute_organize_pipeline()`은 단순 LLM 호출만 수행
- LangGraph 기반 파이프라인 없음
- 음성 → 텍스트 → 요약 → 구조화 → DB 반영의 자동화 흐름이 불완전

**필요한 구현:**
- LangGraph 기반 자동 정리 파이프라인
- 음성 입력 → STT → 의도 분석 → 구조화 → DB 자동 반영 워크플로우
- 일정/예산/할일/게시판 자동 생성

**영향:**
- 음성 비서가 단순 STT만 수행, 실제 정리 기능 미흡
- "핸즈프리 플래너" 역할 불가능

---

### 6. 예산서 - OpenAI Structured Output + Pydantic Schema ⚠️ **중요 누락**

**현재 상태:**
- `app/services/budget_service.py`의 `structure_text_with_llm()`은 단순 JSON 파싱만 수행
- Structured Output 사용 없음
- Pydantic Schema 기반 검증 없음

**필요한 구현:**
- OpenAI Structured Output 또는 Ollama의 구조화된 출력 사용
- Pydantic Schema로 예산 데이터 검증
- 일정/챗봇과 연결할 수 있는 표준화된 포맷 생성

**영향:**
- OCR 결과 구조화 품질 저하
- 예산 데이터의 일관성 보장 어려움
- OS 전체에서 일관된 데이터 처리 불가

---

## 📋 누락 기능 우선순위 정리

### 🔴 **최우선 (OS 전체 기능에 필수)**

1. **게시판 - Embedding Model + Vector DB**
   - 챗봇 RAG, 게시판 검색, 지식 그래프 구축의 기반
   - **없으면 OS 전체가 AI 기반으로 작동할 수 없음**

2. **챗봇 - User Memory Layer (Vector DB 기반)**
   - 개인화된 서비스의 핵심
   - **결혼까지의 긴 여정을 커버하는 핵심 구조**

3. **챗봇 - LangGraph 기반 자동 정리 파이프라인**
   - 챗봇이 실제 작업을 수행하는 핵심
   - **챗봇이 하는 모든 "정리 업무"의 중심**

### 🟡 **중요 (서비스 품질 향상)**

4. **음성 비서 - 자동 정리 파이프라인(LangGraph 기반)**
   - "핸즈프리 플래너"의 핵심

5. **캘린더 - User Memory + Vector DB 기반 일정 컨텍스트**
   - 개인화된 일정 추천 품질 향상

6. **예산서 - OpenAI Structured Output + Pydantic Schema**
   - 데이터 일관성 및 품질 보장

---

## 📝 구현 권장 순서

1. **1단계: Vector DB 인프라 구축**
   - Chroma 또는 FAISS 설정
   - Embedding 모델 통합
   - 게시판 데이터 벡터화

2. **2단계: User Memory Layer 구현**
   - 사용자별 Vector DB 컬렉션
   - 사용자 패턴 저장 및 검색

3. **3단계: LangGraph 파이프라인 구현**
   - 챗봇 자동 정리 파이프라인
   - 음성 비서 자동 정리 파이프라인

4. **4단계: 데이터 구조화 개선**
   - Structured Output 통합
   - Pydantic Schema 강화

---

## 🔍 추가 확인 사항

### 현재 구현이 있으나 개선이 필요한 부분

1. **챗봇 RAG**: Vector DB 검색 없이 단순 컨텍스트만 사용 중
2. **일정 구조화 엔진**: 기본 구조는 있으나 표준화된 JSON Schema 미완성
3. **캘린더 LLM 개인화**: 기본 구현은 있으나 사용자 패턴 학습 없음

---

## 📌 결론

**총 6개의 "상" 우선순위 기능이 누락되어 있으며, 이 중 3개는 OS 전체 기능에 필수적입니다.**

특히 **Vector DB 기반 인프라**가 없어서 게시판 검색, 챗봇 RAG, 사용자 메모리 등 핵심 기능이 제대로 작동하지 않습니다.



