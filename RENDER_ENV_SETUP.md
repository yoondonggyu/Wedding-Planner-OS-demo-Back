# Render 환경 변수 설정 가이드

## ⚠️ 필수 환경 변수 (반드시 설정 필요!)

### 1. 데이터베이스 연결
```
DATABASE_URL=mysql+pymysql://username:password@host:port/database_name
```
- **설명**: MySQL 데이터베이스 연결 문자열
- **예시**: `mysql+pymysql://root:password@dbserver.render.com:3306/wedding_db`
- **Render 설정**: Render의 MySQL 서비스 연결 정보 사용
- **중요**: 비밀번호가 포함되어 있으므로 절대 GitHub에 커밋하지 마세요!

### 2. JWT 보안 키 (보안 필수!)
```
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters-long
```
- **설명**: JWT 토큰 서명에 사용되는 비밀 키
- **중요**: 반드시 강력한 랜덤 문자열로 설정 (최소 32자 이상 권장)
- **생성 방법**: 
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```
- **보안**: 이 키가 유출되면 모든 JWT 토큰이 위조 가능합니다!

## 선택적 환경 변수

### 3. 모델 서버 설정 (AI 기능 사용 시)
```
MODEL_API_URL=http://your-model-server.onrender.com
MODEL_API_PORT=10000
```
- **설명**: AI 모델 서버 URL 및 포트
- **기본값**: `http://localhost:8102` (없으면 기본값 사용)
- **필요 시**: 별도의 모델 서버가 Render에 배포된 경우 설정

## Render 설정 방법

1. Render 대시보드에서 서비스 선택
2. **Environment** 탭으로 이동
3. **Add Environment Variable** 클릭
4. 위의 환경 변수들을 하나씩 추가

## 환경 변수 설정 예시

```
DATABASE_URL=mysql+pymysql://user:pass@dbserver.render.com:3306/wedding_db
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters-long-random-string-generated-by-secrets-module
MODEL_API_URL=http://your-model-server.onrender.com
MODEL_API_PORT=10000
```

## 보안 주의사항

⚠️ **절대 GitHub에 커밋하지 마세요!**
- `.env` 파일은 `.gitignore`에 포함되어 있습니다
- 환경 변수는 Render 대시보드에서만 관리하세요
- API 키나 비밀번호가 코드에 하드코딩되지 않도록 주의하세요
- `JWT_SECRET_KEY`는 프로덕션 환경에서 반드시 환경 변수로 설정하세요!

## 현재 코드 상태

✅ **환경 변수 지원 완료:**
- `DATABASE_URL`: 데이터베이스 연결 문자열
- `JWT_SECRET_KEY`: JWT 토큰 서명 키
- `MODEL_API_URL`: 모델 서버 URL
- `MODEL_API_PORT`: 모델 서버 포트

코드는 환경 변수가 없으면 개발 환경 기본값을 사용하지만, **프로덕션에서는 반드시 환경 변수로 설정해야 합니다!**
