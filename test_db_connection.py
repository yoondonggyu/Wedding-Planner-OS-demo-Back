"""데이터베이스 연결 테스트"""
from app.core.database import engine, SessionLocal
from app.models.db import User, Post, Comment
from sqlalchemy import text

print("=" * 50)
print("데이터베이스 연결 테스트")
print("=" * 50)

# 1. 엔진 연결 테스트
try:
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        print(f"\n✅ 데이터베이스 연결 성공!")
        print(f"📋 생성된 테이블 목록:")
        for table in tables:
            print(f"   - {table}")
except Exception as e:
    print(f"❌ 데이터베이스 연결 실패: {e}")
    exit(1)

# 2. ORM 연결 테스트
try:
    db = SessionLocal()
    user_count = db.query(User).count()
    post_count = db.query(Post).count()
    comment_count = db.query(Comment).count()
    
    print(f"\n✅ ORM 연결 성공!")
    print(f"📊 데이터 현황:")
    print(f"   - 사용자: {user_count}명")
    print(f"   - 게시글: {post_count}개")
    print(f"   - 댓글: {comment_count}개")
    db.close()
except Exception as e:
    print(f"❌ ORM 연결 실패: {e}")
    exit(1)

print("\n" + "=" * 50)
print("✅ 모든 테스트 통과!")
print("=" * 50)




