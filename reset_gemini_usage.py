#!/usr/bin/env python3
"""
Gemini 이미지 생성 일일 사용량 초기화 스크립트

사용법:
    # 모든 사용자의 오늘 사용량 초기화
    python reset_gemini_usage.py
    
    # 특정 사용자의 사용량 초기화 (이메일로)
    python reset_gemini_usage.py --email user@example.com
    
    # 특정 사용자의 사용량 초기화 (user_id로)
    python reset_gemini_usage.py --user-id 1
    
    # 모든 날짜의 사용량 기록 삭제
    python reset_gemini_usage.py --all
    
    # 현재 사용량 조회만
    python reset_gemini_usage.py --check
"""
import sys
import os
import argparse
from datetime import date

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.db.gemini_usage import GeminiImageUsage
from app.models.db import User


def get_usage_info(db, user_id=None, email=None):
    """사용량 정보 조회"""
    today = date.today()
    
    query = db.query(
        GeminiImageUsage,
        User.email,
        User.nickname
    ).join(User, GeminiImageUsage.user_id == User.id)
    
    if user_id:
        query = query.filter(GeminiImageUsage.user_id == user_id)
    elif email:
        query = query.filter(User.email == email)
    
    query = query.filter(GeminiImageUsage.usage_date == today)
    
    return query.all()


def reset_usage(db, user_id=None, email=None, all_dates=False):
    """사용량 초기화"""
    today = date.today()
    
    # 사용자 찾기
    user = None
    if email:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ 사용자를 찾을 수 없습니다: {email}")
            return False
        user_id = user.id
    
    # 쿼리 구성
    query = db.query(GeminiImageUsage)
    
    if user_id:
        query = query.filter(GeminiImageUsage.user_id == user_id)
    
    if not all_dates:
        query = query.filter(GeminiImageUsage.usage_date == today)
    
    # 삭제 전 정보 출력
    count = query.count()
    
    if count == 0:
        print("ℹ️  초기화할 사용량 기록이 없습니다.")
        return True
    
    # 삭제 실행
    query.delete(synchronize_session=False)
    db.commit()
    
    if user_id and user:
        print(f"✅ {user.email} ({user.nickname})의 사용량이 초기화되었습니다.")
    elif user_id:
        print(f"✅ user_id={user_id}의 사용량이 초기화되었습니다.")
    else:
        print(f"✅ 총 {count}개의 사용량 기록이 초기화되었습니다.")
    
    return True


def show_usage(db):
    """현재 사용량 조회"""
    today = date.today()
    
    usages = db.query(
        GeminiImageUsage,
        User.email,
        User.nickname,
        User.role
    ).join(User, GeminiImageUsage.user_id == User.id).filter(
        GeminiImageUsage.usage_date == today
    ).order_by(GeminiImageUsage.usage_count.desc()).all()
    
    if not usages:
        print(f"📊 오늘({today}) 사용 기록이 없습니다.")
        return
    
    print(f"\n📊 오늘({today}) Gemini 이미지 생성 사용량")
    print("=" * 70)
    print(f"{'이메일':<30} {'닉네임':<15} {'역할':<15} {'사용 횟수':>8}")
    print("-" * 70)
    
    for usage, email, nickname, role in usages:
        role_str = role.value if hasattr(role, 'value') else str(role)
        limit_status = "⚠️ 제한" if usage.usage_count >= 5 and role_str == "USER" else ""
        print(f"{email:<30} {nickname:<15} {role_str:<15} {usage.usage_count:>5}/5 {limit_status}")
    
    print("=" * 70)
    print(f"총 {len(usages)}명의 사용자가 오늘 이미지를 생성했습니다.")
    print("\n💡 관리자(SYSTEM_ADMIN, WEB_ADMIN, VENDOR_ADMIN)는 제한이 없습니다.")


def main():
    parser = argparse.ArgumentParser(description='Gemini 이미지 생성 일일 사용량 초기화')
    parser.add_argument('--email', '-e', help='특정 사용자 이메일')
    parser.add_argument('--user-id', '-u', type=int, help='특정 사용자 ID')
    parser.add_argument('--all', '-a', action='store_true', help='모든 날짜의 기록 삭제')
    parser.add_argument('--check', '-c', action='store_true', help='사용량 조회만 (초기화 안 함)')
    
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        if args.check:
            show_usage(db)
        else:
            # 초기화 전 현재 상태 표시
            print("\n📋 초기화 전 사용량:")
            show_usage(db)
            
            print("\n🔄 사용량 초기화 중...")
            reset_usage(
                db,
                user_id=args.user_id,
                email=args.email,
                all_dates=args.all
            )
            
            print("\n📋 초기화 후 사용량:")
            show_usage(db)
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        return 1
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


