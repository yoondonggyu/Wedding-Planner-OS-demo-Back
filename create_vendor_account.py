"""
벤더 계정 생성 스크립트
아이폰 스냅 테스트 1 업체의 사장 계정 생성 및 연결
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.db.user import User
from app.models.db.vendor import Vendor
from app.core.user_roles import UserRole
from werkzeug.security import generate_password_hash

def create_vendor_account():
    """벤더 계정 생성 및 벤더와 연결"""
    db: Session = SessionLocal()
    
    try:
        # 1. 벤더 계정 생성 (snaptest1)
        email = "snaptest1@demo.com"
        password = "snaptest1"
        nickname = "아이폰 스냅 테스트 1"
        
        # 기존 계정 확인
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"✓ 계정이 이미 존재합니다: {email}")
            user = existing_user
        else:
            # 새 계정 생성
            user = User(
                email=email,
                password=generate_password_hash(password),
                nickname=nickname,
                role=UserRole.PARTNER_VENDOR
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✓ 벤더 계정 생성 완료: {email} (ID: {user.id})")
        
        # 2. "아이폰 스냅 테스트 1" 벤더 찾기
        vendor = db.query(Vendor).filter(Vendor.name == "아이폰 스냅 테스트 1").first()
        
        if not vendor:
            print("✗ '아이폰 스냅 테스트 1' 벤더를 찾을 수 없습니다.")
            print("  벤더 관리 페이지에서 먼저 벤더를 생성해주세요.")
            return
        
        # 3. 벤더에 user_id 연결
        if vendor.user_id and vendor.user_id != user.id:
            print(f"⚠ 벤더가 이미 다른 계정({vendor.user_id})과 연결되어 있습니다.")
            response = input("연결을 변경하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                print("취소되었습니다.")
                return
        
        vendor.user_id = user.id
        db.commit()
        
        print(f"✓ 벤더 연결 완료:")
        print(f"  - 벤더 ID: {vendor.id}")
        print(f"  - 벤더 이름: {vendor.name}")
        print(f"  - 계정 이메일: {user.email}")
        print(f"  - 계정 비밀번호: {password}")
        print(f"  - 역할: {user.role.value}")
        
    except Exception as e:
        db.rollback()
        print(f"✗ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_vendor_account()

