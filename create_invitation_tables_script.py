"""
청첩장 테이블 생성 스크립트 (SQLAlchemy 사용)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models.db.invitation import InvitationTemplate, InvitationDesign, InvitationOrder

def create_tables():
    """테이블 생성"""
    try:
        Base.metadata.create_all(bind=engine, tables=[
            InvitationTemplate.__table__,
            InvitationDesign.__table__,
            InvitationOrder.__table__
        ])
        print("✅ 청첩장 테이블 생성 완료")
        return True
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_tables()

