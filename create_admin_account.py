#!/usr/bin/env python3
"""
관리자 계정 생성 스크립트
admin@admin.com / admin/// - SYSTEM_ADMIN 권한
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.db import User
from app.core.user_roles import UserRole
from werkzeug.security import generate_password_hash


def create_admin():
    db = SessionLocal()
    
    try:
        email = "admin@admin.com"
        password = "admin///"
        nickname = "관리자"
        
        # 기존 계정 확인
        existing = db.query(User).filter(User.email == email).first()
        
        if existing:
            print(f"ℹ️  기존 계정이 있습니다: {email}")
            print(f"   현재 역할: {existing.role}")
            
            # 역할이 SYSTEM_ADMIN이 아니면 업데이트
            if existing.role != UserRole.SYSTEM_ADMIN:
                existing.role = UserRole.SYSTEM_ADMIN
                db.commit()
                print(f"✅ 역할이 SYSTEM_ADMIN으로 업데이트되었습니다.")
            else:
                print(f"✅ 이미 SYSTEM_ADMIN 권한을 가지고 있습니다.")
            
            return existing
        
        # 새 계정 생성
        hashed_password = generate_password_hash(password)
        
        admin_user = User(
            email=email,
            password=hashed_password,
            nickname=nickname,
            role=UserRole.SYSTEM_ADMIN
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ 관리자 계정이 생성되었습니다!")
        print(f"   이메일: {email}")
        print(f"   비밀번호: {password}")
        print(f"   닉네임: {nickname}")
        print(f"   역할: SYSTEM_ADMIN (모든 권한)")
        print(f"   User ID: {admin_user.id}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()

