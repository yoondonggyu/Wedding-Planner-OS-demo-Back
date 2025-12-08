"""
데이터베이스 컬럼 확인 및 수정 스크립트
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine, text

# .env 파일 로드
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print('❌ DATABASE_URL이 설정되지 않았습니다.')
    sys.exit(1)

print(f'📊 데이터베이스 연결 중...')
engine = create_engine(database_url)

try:
    with engine.connect() as conn:
        # invitation_designs 테이블의 컬럼 목록 확인
        result = conn.execute(text('SHOW COLUMNS FROM invitation_designs'))
        columns = result.fetchall()
        
        print('\n📋 invitation_designs 테이블의 현재 컬럼 목록:')
        column_names = [col[0] for col in columns]
        for col in columns:
            print(f'  - {col[0]} ({col[1]})')
        
        # 필요한 컬럼 확인
        required_columns = {
            'groom_father_name': 'VARCHAR(100)',
            'groom_mother_name': 'VARCHAR(100)',
            'bride_father_name': 'VARCHAR(100)',
            'bride_mother_name': 'VARCHAR(100)',
            'map_lat': 'NUMERIC(10, 8)',
            'map_lng': 'NUMERIC(11, 8)',
            'map_image_url': 'TEXT',
            'selected_tone': 'VARCHAR(50)',
            'selected_text': 'TEXT',
            'generated_image_url': 'TEXT',
            'generated_image_model': 'VARCHAR(50)'
        }
        
        print('\n🔍 필요한 컬럼 확인:')
        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name in column_names:
                print(f'  ✅ {col_name} - 존재함')
            else:
                print(f'  ❌ {col_name} - 없음 (추가 필요: {col_type})')
                missing_columns.append((col_name, col_type))
        
        if missing_columns:
            print(f'\n⚠️ 누락된 컬럼: {len(missing_columns)}개')
            print('🔄 컬럼 추가 중...')
            
            # 부모님 성함 컬럼 추가
            parent_cols = [col for col in missing_columns if 'father_name' in col[0] or 'mother_name' in col[0]]
            if parent_cols:
                try:
                    alter_sql = 'ALTER TABLE invitation_designs ADD COLUMN '
                    alter_sql += ', ADD COLUMN '.join([f'{col[0]} {col[1]}' for col in parent_cols])
                    print(f'  실행: {alter_sql[:100]}...')
                    conn.execute(text(alter_sql))
                    conn.commit()
                    print('  ✅ 부모님 성함 컬럼 추가 완료')
                except Exception as e:
                    print(f'  ❌ 부모님 성함 컬럼 추가 실패: {e}')
            
            # 지도 정보 컬럼 추가
            map_cols = [col for col in missing_columns if 'map' in col[0]]
            if map_cols:
                try:
                    alter_sql = 'ALTER TABLE invitation_designs ADD COLUMN '
                    alter_sql += ', ADD COLUMN '.join([f'{col[0]} {col[1]}' for col in map_cols])
                    print(f'  실행: {alter_sql[:100]}...')
                    conn.execute(text(alter_sql))
                    conn.commit()
                    print('  ✅ 지도 정보 컬럼 추가 완료')
                except Exception as e:
                    print(f'  ❌ 지도 정보 컬럼 추가 실패: {e}')
            
            # 톤/문구 컬럼 추가
            tone_cols = [col for col in missing_columns if 'tone' in col[0] or 'text' in col[0]]
            if tone_cols:
                try:
                    alter_sql = 'ALTER TABLE invitation_designs ADD COLUMN '
                    alter_sql += ', ADD COLUMN '.join([f'{col[0]} {col[1]}' for col in tone_cols])
                    print(f'  실행: {alter_sql[:100]}...')
                    conn.execute(text(alter_sql))
                    conn.commit()
                    print('  ✅ 톤/문구 컬럼 추가 완료')
                except Exception as e:
                    print(f'  ❌ 톤/문구 컬럼 추가 실패: {e}')
            
            # 이미지 생성 컬럼 추가 (map_image_url 제외)
            image_cols = [col for col in missing_columns if ('image' in col[0] or 'model' in col[0]) and 'map_image' not in col[0]]
            if image_cols:
                try:
                    alter_sql = 'ALTER TABLE invitation_designs ADD COLUMN '
                    alter_sql += ', ADD COLUMN '.join([f'{col[0]} {col[1]}' for col in image_cols])
                    print(f'  실행: {alter_sql[:100]}...')
                    conn.execute(text(alter_sql))
                    conn.commit()
                    print('  ✅ 이미지 생성 컬럼 추가 완료')
                except Exception as e:
                    print(f'  ❌ 이미지 생성 컬럼 추가 실패: {e}')
            
            print('\n✅ 모든 컬럼 추가 완료!')
        else:
            print('\n✅ 모든 필요한 컬럼이 존재합니다.')
            
except Exception as e:
    print(f'❌ 오류 발생: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

