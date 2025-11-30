"""
기존 todos 테이블의 데이터를 calendar_events 테이블로 마이그레이션하는 스크립트
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# DB 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate_todos_to_events():
    """todos 테이블의 데이터를 calendar_events로 마이그레이션"""
    db = SessionLocal()
    try:
        # 1. todos 테이블에 데이터가 있는지 확인
        result = db.execute(text("SELECT COUNT(*) as count FROM todos"))
        todo_count = result.fetchone()[0]
        print(f"마이그레이션할 todos 레코드 수: {todo_count}")
        
        if todo_count == 0:
            print("마이그레이션할 데이터가 없습니다.")
            return
        
        # 2. todos 데이터를 calendar_events로 복사
        # due_date -> start_date, category='todo'로 설정
        migration_sql = """
        INSERT INTO calendar_events (
            user_id, title, description, start_date, 
            category, priority, assignee, is_completed, 
            created_at, updated_at
        )
        SELECT 
            user_id,
            title,
            description,
            due_date as start_date,  -- due_date를 start_date로 매핑
            'todo' as category,      -- 할일 구분
            priority,
            assignee,
            is_completed,
            created_at,
            updated_at
        FROM todos
        WHERE NOT EXISTS (
            -- 중복 방지: 이미 마이그레이션된 데이터는 제외
            SELECT 1 FROM calendar_events ce 
            WHERE ce.user_id = todos.user_id 
            AND ce.title = todos.title 
            AND ce.start_date = todos.due_date
            AND ce.category = 'todo'
        )
        """
        
        result = db.execute(text(migration_sql))
        db.commit()
        migrated_count = result.rowcount
        print(f"마이그레이션 완료: {migrated_count}개 레코드가 calendar_events로 이동되었습니다.")
        
        # 3. 마이그레이션 확인
        result = db.execute(text("SELECT COUNT(*) as count FROM calendar_events WHERE category = 'todo'"))
        todo_events_count = result.fetchone()[0]
        print(f"calendar_events 테이블의 todo 카테고리 레코드 수: {todo_events_count}")
        
    except Exception as e:
        db.rollback()
        print(f"마이그레이션 실패: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("todos -> calendar_events 마이그레이션 시작...")
    migrate_todos_to_events()
    print("마이그레이션 완료!")

