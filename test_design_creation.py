"""
디자인 생성 기능 테스트 스크립트
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# .env 파일 로드
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print('❌ DATABASE_URL이 설정되지 않았습니다.')
    sys.exit(1)

engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)

def test_design_creation():
    """디자인 생성 테스트"""
    print('🧪 디자인 생성 기능 테스트 시작...\n')
    
    db = SessionLocal()
    try:
        # 1. 컬럼 존재 확인
        print('1️⃣ 컬럼 존재 여부 확인:')
        result = db.execute(text('SHOW COLUMNS FROM invitation_designs'))
        columns = [col[0] for col in result.fetchall()]
        required = [
            'groom_father_name', 'groom_mother_name', 
            'bride_father_name', 'bride_mother_name',
            'map_lat', 'map_lng', 'map_image_url',
            'selected_tone', 'selected_text',
            'generated_image_url', 'generated_image_model'
        ]
        
        all_exist = True
        for col in required:
            exists = col in columns
            status = '✅' if exists else '❌'
            print(f'   {status} {col}')
            if not exists:
                all_exist = False
        
        if not all_exist:
            print('\n❌ 일부 컬럼이 누락되었습니다.')
            return False
        
        print('   ✅ 모든 필요한 컬럼이 존재합니다.\n')
        
        # 2. 테스트 데이터로 INSERT 테스트
        print('2️⃣ INSERT 테스트:')
        test_data = {
            'user_id': 13,  # 기존 사용자
            'couple_id': None,
            'template_id': None,
            'design_data': '{"groom_name": "테스트", "bride_name": "테스트"}',
            'status': 'DRAFT',
            'groom_father_name': '테스트아버지',
            'groom_mother_name': '테스트어머니',
            'bride_father_name': '테스트아버지2',
            'bride_mother_name': '테스트어머니2',
            'map_lat': None,
            'map_lng': None,
            'map_image_url': None,
            'selected_tone': None,
            'selected_text': None,
            'generated_image_url': None,
            'generated_image_model': None,
            'qr_code_url': None,
            'qr_code_data': None,
            'pdf_url': None,
            'preview_image_url': None
        }
        
        try:
            # INSERT 문 생성
            insert_sql = text("""
                INSERT INTO invitation_designs 
                (user_id, couple_id, template_id, design_data, status, 
                 groom_father_name, groom_mother_name, bride_father_name, bride_mother_name,
                 map_lat, map_lng, map_image_url, selected_tone, selected_text,
                 generated_image_url, generated_image_model, qr_code_url, qr_code_data,
                 pdf_url, preview_image_url, created_at, updated_at)
                VALUES 
                (:user_id, :couple_id, :template_id, :design_data, :status,
                 :groom_father_name, :groom_mother_name, :bride_father_name, :bride_mother_name,
                 :map_lat, :map_lng, :map_image_url, :selected_tone, :selected_text,
                 :generated_image_url, :generated_image_model, :qr_code_url, :qr_code_data,
                 :pdf_url, :preview_image_url, NOW(), NOW())
            """)
            
            result = db.execute(insert_sql, test_data)
            db.commit()
            design_id = result.lastrowid
            
            print(f'   ✅ 디자인 생성 성공! (ID: {design_id})')
            
            # 생성된 데이터 확인
            select_sql = text("""
                SELECT id, groom_father_name, groom_mother_name, 
                       bride_father_name, bride_mother_name
                FROM invitation_designs 
                WHERE id = :design_id
            """)
            result = db.execute(select_sql, {'design_id': design_id})
            row = result.fetchone()
            
            if row:
                print(f'   📋 생성된 데이터 확인:')
                print(f'      - ID: {row[0]}')
                print(f'      - 신랑 부모: {row[1]} / {row[2]}')
                print(f'      - 신부 부모: {row[3]} / {row[4]}')
            
            # 테스트 데이터 삭제
            delete_sql = text("DELETE FROM invitation_designs WHERE id = :design_id")
            db.execute(delete_sql, {'design_id': design_id})
            db.commit()
            print(f'   🗑️ 테스트 데이터 삭제 완료\n')
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f'   ❌ INSERT 실패: {e}')
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f'❌ 테스트 실패: {e}')
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    success = test_design_creation()
    if success:
        print('✅ 모든 테스트 통과!')
        sys.exit(0)
    else:
        print('❌ 테스트 실패')
        sys.exit(1)

