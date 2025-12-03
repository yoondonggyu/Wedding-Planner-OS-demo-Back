from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# .env 파일 로드 (python-dotenv 사용 가능 시)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv가 없어도 환경 변수는 사용 가능

# MySQL 데이터베이스 연결 설정
# ⚠️ 보안: 반드시 환경 변수 또는 .env 파일로 설정하세요!
# .env 파일 또는 환경 변수 DATABASE_URL이 없으면 에러 발생
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "DATABASE_URL 환경 변수가 설정되지 않았습니다. "
        ".env 파일을 생성하거나 환경 변수를 설정해주세요.\n"
        "예: DATABASE_URL=mysql+pymysql://root:password@localhost:3306/WEDDING_PLANNER_OS_DB"
    )

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




