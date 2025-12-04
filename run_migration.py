"""
카테고리 컬럼 추가 마이그레이션 실행 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text

def run_migration():
    """category 컬럼 추가 마이그레이션 실행"""
    try:
        with engine.connect() as conn:
            # 트랜잭션 시작
            trans = conn.begin()
            
            try:
                # category 컬럼이 이미 있는지 확인
                check_query = text("""
                    SELECT COUNT(*) as cnt 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'posts' 
                    AND COLUMN_NAME = 'category'
                """)
                result = conn.execute(check_query)
                has_column = result.fetchone()[0] > 0
                
                if has_column:
                    print("✅ category 컬럼이 이미 존재합니다.")
                else:
                    print("📝 category 컬럼 추가 중...")
                    # category 컬럼 추가
                    conn.execute(text("""
                        ALTER TABLE posts 
                        ADD COLUMN category VARCHAR(50) NULL 
                        AFTER board_type
                    """))
                    print("✅ category 컬럼 추가 완료!")
                
                # 인덱스 확인 및 추가
                index_check = text("""
                    SELECT COUNT(*) as cnt 
                    FROM information_schema.STATISTICS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'posts' 
                    AND INDEX_NAME = 'idx_posts_category'
                """)
                result = conn.execute(index_check)
                has_index = result.fetchone()[0] > 0
                
                if not has_index:
                    print("📝 인덱스 추가 중...")
                    conn.execute(text("CREATE INDEX idx_posts_category ON posts(category)"))
                    conn.execute(text("CREATE INDEX idx_posts_board_type_category ON posts(board_type, category)"))
                    print("✅ 인덱스 추가 완료!")
                else:
                    print("✅ 인덱스가 이미 존재합니다.")
                
                # 트랜잭션 커밋
                trans.commit()
                print("\n✅ 마이그레이션 완료!")
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    run_migration()


