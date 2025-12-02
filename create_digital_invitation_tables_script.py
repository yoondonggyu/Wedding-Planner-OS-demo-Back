"""
디지털 초대장 + 축의금 결제 시스템 테이블 생성 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models.db.digital_invitation import DigitalInvitation, Payment, RSVP, GuestMessage

def create_digital_invitation_tables():
    """디지털 초대장 관련 테이블 생성"""
    try:
        Base.metadata.create_all(bind=engine, tables=[
            DigitalInvitation.__table__,
            Payment.__table__,
            RSVP.__table__,
            GuestMessage.__table__
        ])
        print("✅ 디지털 초대장 + 축의금 결제 시스템 테이블 생성 완료!")
        print("   - digital_invitations")
        print("   - payments")
        print("   - rsvps")
        print("   - guest_messages")
        return True
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_digital_invitation_tables()

