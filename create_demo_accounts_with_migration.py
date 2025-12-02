"""
데모 계정 생성 스크립트 (마이그레이션 포함)
시스템 관리자와 웹 관리자 계정을 생성합니다.
"""
import sys
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.db.user import User
from app.core.user_roles import UserRole

def add_role_column_if_not_exists(db: Session):
    """role 컬럼이 없으면 추가"""
    try:
        # role 컬럼 존재 여부 확인
        result = db.execute(text("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'role'
        """))
        count = result.fetchone()[0]
        
        if count == 0:
            print("📝 role 컬럼 추가 중...")
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'USER' 
                AFTER profile_image_url
            """))
            db.execute(text("""
                UPDATE users SET role = 'USER' WHERE role IS NULL OR role = ''
            """))
            db.commit()
            print("✅ role 컬럼 추가 완료!")
        else:
            print("✅ role 컬럼이 이미 존재합니다.")
    except Exception as e:
        db.rollback()
        print(f"⚠️ role 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        # 오류가 나도 계속 진행

def create_demo_accounts():
    """데모 계정 생성"""
    db: Session = SessionLocal()
    
    try:
        # role 컬럼 추가
        add_role_column_if_not_exists(db)
        
        # 기존 계정 확인 및 삭제
        existing_system = db.query(User).filter(User.email == 'systemadmin@demo.com').first()
        existing_web = db.query(User).filter(User.email == 'webadmin@demo.com').first()
        
        if existing_system:
            print(f"🗑️ 기존 시스템 관리자 계정 삭제: {existing_system.email}")
            db.delete(existing_system)
        
        if existing_web:
            print(f"🗑️ 기존 웹 관리자 계정 삭제: {existing_web.email}")
            db.delete(existing_web)
        
        db.commit()
        
        # 시스템 관리자 계정 생성
        system_admin = User(
            email='systemadmin@demo.com',
            password='systemadmin',
            nickname='시스템 관리자',
            role=UserRole.SYSTEM_ADMIN
        )
        db.add(system_admin)
        
        # 웹 관리자 계정 생성
        web_admin = User(
            email='webadmin@demo.com',
            password='webadmin',
            nickname='웹 관리자',
            role=UserRole.WEB_ADMIN
        )
        db.add(web_admin)
        
        db.commit()
        db.refresh(system_admin)
        db.refresh(web_admin)
        
        print("\n✅ 데모 계정 생성 완료!")
        print("\n📋 생성된 계정:")
        print(f"  1. 시스템 관리자")
        print(f"     이메일: {system_admin.email}")
        print(f"     비밀번호: systemadmin")
        print(f"     역할: {system_admin.role.value}")
        print(f"\n  2. 웹 관리자")
        print(f"     이메일: {web_admin.email}")
        print(f"     비밀번호: webadmin")
        print(f"     역할: {web_admin.role.value}")
        print("\n💡 이제 벤더 관리 페이지에서 시스템 관리자 계정으로 로그인하여 벤더를 추가할 수 있습니다.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_accounts()

