"""
모든 역할별 계정 생성 스크립트
- SYSTEM_ADMIN: systemadmin@demo.com (이미 존재)
- WEB_ADMIN: webadmin@demo.com (이미 존재)
- VENDOR_ADMIN: vendoradmin@demo.com (생성)
- PARTNER_VENDOR: snaptest1@demo.com (이미 존재)
- USER: test@test.com, estar987@naver.com, pstar987@naver.com (이미 존재)
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.db.user import User
from app.core.user_roles import UserRole

def create_all_role_accounts():
    """모든 역할별 계정 확인 및 생성"""
    db: Session = SessionLocal()
    
    try:
        accounts_to_create = [
            {
                'email': 'vendoradmin@demo.com',
                'password': 'vendoradmin',
                'nickname': '업체 관리자',
                'role': UserRole.VENDOR_ADMIN
            }
        ]
        
        existing_roles = {}
        for user in db.query(User).all():
            role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            if role not in existing_roles:
                existing_roles[role] = []
            existing_roles[role].append(user.email)
        
        print("현재 계정 상태:")
        for role, emails in existing_roles.items():
            print(f"  {role}: {', '.join(emails)}")
        
        print("\n필요한 역할:")
        required_roles = ['SYSTEM_ADMIN', 'WEB_ADMIN', 'VENDOR_ADMIN', 'PARTNER_VENDOR', 'USER']
        for role in required_roles:
            if role in existing_roles:
                print(f"  ✓ {role}: 존재함")
            else:
                print(f"  ✗ {role}: 없음")
        
        # VENDOR_ADMIN 계정 생성
        for account in accounts_to_create:
            existing_user = db.query(User).filter(User.email == account['email']).first()
            if existing_user:
                print(f"\n✓ 계정이 이미 존재합니다: {account['email']}")
                # 역할 확인 및 업데이트
                if existing_user.role != account['role']:
                    existing_user.role = account['role']
                    db.commit()
                    print(f"  역할이 {account['role'].value}로 업데이트되었습니다.")
            else:
                user = User(
                    email=account['email'],
                    password=account['password'],  # 평문 비밀번호
                    nickname=account['nickname'],
                    role=account['role']
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"\n✓ 계정 생성 완료:")
                print(f"  - 이메일: {account['email']}")
                print(f"  - 비밀번호: {account['password']}")
                print(f"  - 역할: {account['role'].value}")
        
        print("\n최종 계정 목록:")
        for user in db.query(User).order_by(User.role, User.email).all():
            role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            print(f"  - {user.email}: {role}")
        
    except Exception as e:
        db.rollback()
        print(f"✗ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_all_role_accounts()

