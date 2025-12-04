# ChromaDB 설정 및 연동 가이드

## ✅ 현재 상태

- **ChromaDB 버전**: 1.3.5 (설치 완료)
- **저장 방식**: 로컬 파일 기반 (`./vector_db/` 디렉토리)
- **Embedding 모델**: Ollama `nomic-embed-text:latest`

## 📁 저장 구조

```
vector_db/
├── posts/              # 게시판 벡터 데이터
├── chat_memories/      # 채팅 메모리 벡터 데이터
├── user_memory_1/      # 사용자 1의 메모리
└── ...
```

## 🔐 보안 설정

**참고**: ChromaDB는 기본적으로 로컬 파일 기반이며 비밀번호가 없습니다. 
향후 ChromaDB Server 모드로 전환 시 인증 설정이 가능합니다.

### 현재 구조 (로컬 파일 기반)
- 데이터는 `./vector_db/` 디렉토리에 저장
- 파일 시스템 권한으로 보안 관리
- MySQL과 별도로 운영

### 향후 확장 계획
- ChromaDB Server 모드 전환 시 비밀번호 설정 가능
- 현재는 MySQL 비밀번호와 동일한 정책 적용 예정 (`1q2w#E$R`)

## 🔄 데이터 저장 흐름

### 채팅 메모리 저장 시:

1. **ChromaDB에 벡터 저장**
   - 텍스트 → Embedding → 벡터로 변환
   - 컬렉션: `chat_memories`
   - 벡터 ID: `memory_{memory_id}`

2. **MySQL에 메타데이터 저장**
   - `chat_memories` 테이블에 저장
   - `vector_db_id`: ChromaDB 벡터 ID
   - `vector_db_collection`: 컬렉션 이름
   - 실제 텍스트는 ChromaDB에만 저장

## 🔍 RAG 통합

채팅 메모리는 RAG 프롬프트에 자동으로 포함됩니다:

1. 사용자 질문과 유사한 저장된 메모리 검색
2. 검색 결과를 프롬프트에 포함
3. LLM이 저장된 정보를 참고하여 답변

## 📊 향후 확장 계획

### 1. 문서 보관함 연동
- OCR 결과를 ChromaDB에 벡터로 저장
- 문서 검색 및 RAG 활용

### 2. 이미지 처리
- 이미지 임베딩 모델 추가
- 멀티모달 검색 지원

### 3. S3 연동
- 대용량 파일은 S3에 저장
- ChromaDB에는 메타데이터만 저장

### 4. MongoDB 연동
- 비구조화된 데이터 저장
- ChromaDB와 연계하여 하이브리드 검색

## 🚀 사용 방법

### 채팅 메모리 저장
```python
# 자동으로 ChromaDB에 벡터 저장됨
POST /api/chat-memories
{
    "content": "저장할 내용",
    "title": "제목",
    "tags": ["태그1", "태그2"]
}
```

### 채팅 메모리 검색 (RAG)
- 채팅 시 자동으로 유사한 메모리 검색
- 검색 결과가 프롬프트에 포함됨

### 수동 검색
```python
from app.services.chat_memory_vector_service import search_chat_memories

results = search_chat_memories(
    query="검색어",
    user_id=1,
    k=5
)
```

## ⚠️ 주의사항

1. **Ollama 서버 필요**: Embedding 모델을 사용하므로 Ollama 서버가 실행 중이어야 합니다.
2. **디스크 공간**: 벡터 데이터는 디스크 공간을 사용합니다.
3. **성능**: 대량의 데이터 저장 시 검색 성능에 영향을 줄 수 있습니다.

## 🔧 문제 해결

### Embedding 모델 로드 실패
```bash
# Ollama 모델 다운로드
ollama pull nomic-embed-text
```

### Vector DB 사용 불가
```bash
# 패키지 설치 확인
conda run -n env_python310 pip list | grep chroma
conda run -n env_python310 pip list | grep langchain
```


