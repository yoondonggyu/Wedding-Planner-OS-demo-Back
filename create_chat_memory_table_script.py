"""
채팅 메모리 테이블 생성 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import engine, Base
from app.models.db.chat_memory import ChatMemory

def create_chat_memory_table():
    """chat_memories 테이블 생성"""
    try:
        # 테이블 생성
        ChatMemory.__table__.create(engine, checkfirst=True)
        print("✅ chat_memories 테이블 생성 완료")
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        raise

if __name__ == "__main__":
    create_chat_memory_table()


