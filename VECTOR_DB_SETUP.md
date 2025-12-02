# Vector DB 설정 가이드

## 📦 필요한 패키지 설치

```bash
# conda 환경 활성화
conda activate env_python310

# Vector DB 관련 패키지 설치
pip install langchain-chroma==0.1.2
pip install langchain-ollama==0.1.0
pip install langchain-core==0.3.0
pip install langchain-text-splitters==0.3.0
```

또는 `requirements.txt`에 이미 추가되어 있으므로:

```bash
pip install -r requirements.txt
```

## 🔧 Ollama Embedding 모델 다운로드

Vector DB가 작동하려면 Ollama에 `nomic-embed-text` 모델이 설치되어 있어야 합니다.

```bash
# Ollama 모델 다운로드
ollama pull nomic-embed-text
```

## 📁 Vector DB 저장 경로

Vector DB 데이터는 `./vector_db/` 디렉토리에 저장됩니다:

```
vector_db/
├── posts/          # 게시판 벡터 데이터
├── user_memory_1/  # 사용자 1의 메모리
├── user_memory_2/  # 사용자 2의 메모리
└── ...
```

## 🚀 사용 방법

### 1. 게시글 작성 시 자동 벡터화

게시글을 작성하면 자동으로 Vector DB에 저장됩니다.

### 2. 기존 게시글 일괄 벡터화

```bash
# API 호출
POST /api/vector/posts/batch-vectorize?limit=100
```

### 3. 게시글 벡터 검색

```bash
# API 호출
GET /api/vector/posts/search?query=웨딩홀&k=5
```

### 4. 사용자 메모리 검색

```bash
# API 호출
GET /api/vector/user/memory?query=예산&k=5
```

## 🔍 API 엔드포인트

### 게시판 벡터 검색
- `GET /api/vector/posts/search?query={검색어}&k={개수}&board_type={타입}`

### 게시판 Vector DB 통계
- `GET /api/vector/posts/stats`

### 기존 게시글 일괄 벡터화
- `POST /api/vector/posts/batch-vectorize?limit={개수}`

### 사용자 메모리 검색
- `GET /api/vector/user/memory?query={검색어}&k={개수}&preference_type={타입}`

### 사용자 프로필 요약
- `GET /api/vector/user/profile`

### 사용자 메모리 통계
- `GET /api/vector/user/stats`

## ⚠️ 주의사항

1. **Ollama 서버 실행 필요**: Vector DB는 Ollama의 `nomic-embed-text` 모델을 사용합니다.
2. **초기 벡터화**: 기존 게시글은 일괄 벡터화 API를 호출해야 검색 가능합니다.
3. **디스크 공간**: Vector DB 데이터는 로컬 디스크에 저장되므로 충분한 공간이 필요합니다.

## 🔄 LangGraph 파이프라인

LangGraph 파이프라인은 `app/services/langgraph_service.py`에 구조가 준비되어 있습니다.
나중에 LangGraph를 학습한 후 실제 구현을 추가하면 됩니다.

현재 구조:
- `OrganizePipeline` 클래스: 파이프라인 관리
- `PipelineNode` 클래스: 개별 노드
- `prepare_langgraph_state()`: LangGraph State 준비 함수
- `extract_langgraph_result()`: LangGraph 결과 추출 함수



