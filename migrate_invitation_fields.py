"""
청첩장 디자인 테이블 마이그레이션 스크립트
새로운 필드들을 추가합니다.
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from sqlalchemy import create_engine, text

def run_migration():
    """마이그레이션 실행"""
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    
    print("🔄 청첩장 디자인 테이블 마이그레이션 시작...")
    
    migration_sql = """
    -- 부모님 성함 컬럼 추가
    ALTER TABLE invitation_designs 
    ADD COLUMN IF NOT EXISTS groom_father_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS groom_mother_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS bride_father_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS bride_mother_name VARCHAR(100);

    -- 지도 정보 컬럼 추가
    ALTER TABLE invitation_designs
    ADD COLUMN IF NOT EXISTS map_lat NUMERIC(10, 8),
    ADD COLUMN IF NOT EXISTS map_lng NUMERIC(11, 8),
    ADD COLUMN IF NOT EXISTS map_image_url TEXT;

    -- 선택된 톤 및 문구 컬럼 추가
    ALTER TABLE invitation_designs
    ADD COLUMN IF NOT EXISTS selected_tone VARCHAR(50),
    ADD COLUMN IF NOT EXISTS selected_text TEXT;

    -- 생성된 이미지 컬럼 추가
    ALTER TABLE invitation_designs
    ADD COLUMN IF NOT EXISTS generated_image_url TEXT,
    ADD COLUMN IF NOT EXISTS generated_image_model VARCHAR(50);
    """
    
    try:
        with engine.connect() as conn:
            # 각 ALTER TABLE 문을 개별 실행
            statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                if statement:
                    conn.execute(text(statement))
                    conn.commit()
            
            # 결과 확인
            result = conn.execute(text("SELECT COUNT(*) FROM invitation_designs"))
            count = result.scalar()
            
            print(f"✅ 마이그레이션 완료!")
            print(f"   총 {count}개의 청첩장 디자인이 있습니다.")
            print(f"   새로운 컬럼들이 추가되었습니다:")
            print(f"   - 부모님 성함 (groom_father_name, groom_mother_name, bride_father_name, bride_mother_name)")
            print(f"   - 지도 정보 (map_lat, map_lng, map_image_url)")
            print(f"   - 톤/문구 (selected_tone, selected_text)")
            print(f"   - 생성 이미지 (generated_image_url, generated_image_model)")
            
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        raise

if __name__ == "__main__":
    run_migration()
