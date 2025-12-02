from sqlalchemy.orm import Session
from app.schemas import LoginReq, SignupReq
from app.core.validators import validate_email, validate_password_pair, validate_nickname
from app.core.exceptions import bad_request, conflict
from app.core.error_codes import ErrorCode
from app.core.security import create_access_token
from app.models.db import User, Couple, Gender, VendorApprovalStatus, CoupleStatus
from app.core.user_roles import UserRole
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import string
import uuid


def login_controller(req: LoginReq, db: Session):
    """로그인 컨트롤러 - JWT 토큰 발급"""
    validate_email(req.email)
    
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise bad_request("invalid_credentials", ErrorCode.INVALID_CREDENTIALS)
    
    # 비밀번호 검증: 해시된 비밀번호 또는 평문 비밀번호 모두 지원 (하위 호환성)
    password_valid = False
    if user.password.startswith('$') or user.password.startswith('scrypt:'):  # 해시된 비밀번호 (werkzeug 형식)
        password_valid = check_password_hash(user.password, req.password)
    else:  # 평문 비밀번호 (기존 계정)
        password_valid = user.password == req.password
    
    if not password_valid:
        raise bad_request("invalid_credentials", ErrorCode.INVALID_CREDENTIALS)
    
    # JWT 토큰 생성 (sub는 문자열이어야 함)
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "nickname": user.nickname,
        "profile_image_url": user.profile_image_url,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
    }


def generate_couple_key() -> str:
    """커플 키 생성 (8자리 영문+숫자)"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))

def signup_controller(req: SignupReq, db: Session):
    """회원가입 컨트롤러"""
    validate_email(req.email)
    validate_password_pair(req.password, req.password_check)
    validate_nickname(req.nickname)
    
    # 프로필 이미지 URL이 없으면 기본 이미지 사용
    profile_image_url = req.profile_image_url or "https://via.placeholder.com/150"

    if db.query(User).filter(User.email == req.email).first():
        raise conflict("duplicate_email", ErrorCode.DUPLICATE_EMAIL)
    if db.query(User).filter(User.nickname == req.nickname).first():
        raise conflict("duplicate_nickname", ErrorCode.DUPLICATE_NICKNAME)

    # 역할 설정
    user_role = UserRole.USER
    vendor_approval_status = None  # 일반 사용자는 승인 상태 없음
    
    if req.is_partner_vendor:
        # 제휴 업체 가입: 일반 사용자로 가입하고 승인 대기 상태로 설정
        user_role = UserRole.USER  # 일단 일반 사용자로 가입
        vendor_approval_status = VendorApprovalStatus.PENDING  # 승인 대기
    
    # 성별 설정
    gender = None
    if req.gender:
        try:
            gender = Gender(req.gender)
        except ValueError:
            raise bad_request("invalid_gender", ErrorCode.INVALID_GENDER)
    
    # 비밀번호 해싱
    hashed_password = generate_password_hash(req.password)
    
    # 초대 링크로 가입하는 경우 (invite_code가 있는 경우)
    auto_connected = False
    partner_nickname = None
    partner_couple = None
    partner_user = None
    
    if req.invite_code:
        # 초대 링크의 커플 키로 커플 정보 찾기
        partner_couple = db.query(Couple).filter(Couple.couple_key == req.invite_code).first()
        
        if partner_couple:
            # 상대방 사용자 찾기
            partner_user = db.query(User).filter(User.id == partner_couple.user1_id).first()
            
            if partner_user:
                # 성별이 설정되어 있고, 상대방과 다른 성별인지 확인
                if gender and partner_user.gender and partner_user.gender != gender:
                    # 이미 연결되어 있지 않은지 확인
                    if not partner_couple.user2_id:
                        partner_nickname = partner_user.nickname
    
    # 커플 키 생성 (성별이 선택된 경우에만)
    couple_key = None
    if gender:
        # 고유한 커플 키 생성 (8자리)
        while True:
            couple_key = str(uuid.uuid4()).replace('-', '')[:8]
            if not db.query(User).filter(User.couple_key == couple_key).first():
                break

    user = User(
        email=req.email,
        password=hashed_password,  # 해시된 비밀번호 저장
        nickname=req.nickname,
        profile_image_url=str(profile_image_url),
        role=user_role,
        gender=gender,
        couple_key=couple_key,
        vendor_approval_status=vendor_approval_status
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 초대 링크로 가입한 경우 자동 커플 연결 완료
    if req.invite_code and partner_couple and partner_user and gender and partner_user.gender and partner_user.gender != gender:
        if not partner_couple.user2_id:  # 아직 연결되지 않은 경우
            partner_couple.user2_id = user.id
            partner_couple.status = CoupleStatus.CONNECTED
            from datetime import datetime
            partner_couple.connected_at = datetime.now()
            user.couple_id = partner_couple.id
            user.partner_couple_key = req.invite_code
            partner_user.couple_id = partner_couple.id
            partner_user.partner_couple_key = couple_key
            auto_connected = True
            db.commit()
            db.refresh(user)
            db.refresh(partner_couple)
            db.refresh(partner_user)
    
    # 초대 링크로 가입하지 않은 경우, 성별이 있으면 Couple 생성
    # (초대 링크로 가입한 경우에도 Couple이 생성되지 않았을 수 있으므로 확인)
    if gender and couple_key:
        existing_couple = db.query(Couple).filter(Couple.user1_id == user.id).first()
        if not existing_couple:
            couple = Couple(
                couple_key=couple_key,
                user1_id=user.id,
                status=CoupleStatus.PENDING
            )
            db.add(couple)
            db.commit()
            db.refresh(couple)
    
    return {
        "user_id": user.id,
        "couple_key": couple_key,
        "is_partner_vendor_pending": vendor_approval_status == VendorApprovalStatus.PENDING,
        "auto_connected": auto_connected,
        "partner_nickname": partner_nickname if auto_connected else None
    }
