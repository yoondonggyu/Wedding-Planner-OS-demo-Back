"""
couples 테이블에 user1_entered_key, user2_entered_key 컬럼 추가 스크립트
"""
import pymysql

# 데이터베이스 연결 정보
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root1234',
    'database': 'wedding_os',
    'charset': 'utf8mb4'
}

def add_columns():
    """couples 테이블에 컬럼 추가"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 컬럼이 이미 존재하는지 확인
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'wedding_os' 
            AND TABLE_NAME = 'couples' 
            AND COLUMN_NAME IN ('user1_entered_key', 'user2_entered_key')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # user1_entered_key 컬럼 추가
        if 'user1_entered_key' not in existing_columns:
            cursor.execute("""
                ALTER TABLE couples 
                ADD COLUMN user1_entered_key VARCHAR(32) NULL AFTER user2_id
            """)
            print("✓ user1_entered_key 컬럼 추가 완료")
        else:
            print("✓ user1_entered_key 컬럼이 이미 존재합니다")
        
        # user2_entered_key 컬럼 추가
        if 'user2_entered_key' not in existing_columns:
            cursor.execute("""
                ALTER TABLE couples 
                ADD COLUMN user2_entered_key VARCHAR(32) NULL AFTER user1_entered_key
            """)
            print("✓ user2_entered_key 컬럼 추가 완료")
        else:
            print("✓ user2_entered_key 컬럼이 이미 존재합니다")
        
        connection.commit()
        print("\n✅ 모든 컬럼 추가 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n💡 수동으로 SQL을 실행해주세요:")
        print("   mysql -u root -p wedding_os < add_couple_entered_keys.sql")
    finally:
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == "__main__":
    add_columns()

