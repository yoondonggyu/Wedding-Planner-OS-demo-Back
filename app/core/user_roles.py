"""
사용자 권한 시스템
"""
from enum import Enum
from typing import List


class UserRole(str, Enum):
    """사용자 역할"""
    # 개발자 - 시스템 관리자: 모든 권한
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    
    # 웹 페이지 관리자, 업체 관리자: 시스템 접근 외의 제공된 웹페이지에서 페이지 관리 가능
    WEB_ADMIN = "WEB_ADMIN"
    VENDOR_ADMIN = "VENDOR_ADMIN"
    
    # 제휴 업체: 업체들의 홍보성, 설명 등 작성 가능, 예약 받기 등 가능
    PARTNER_VENDOR = "PARTNER_VENDOR"
    
    # 사용자: 실제 결혼하는 사람들
    USER = "USER"


class Permission:
    """권한 정의"""
    # 시스템 관리
    MANAGE_SYSTEM = "manage_system"
    MANAGE_USERS = "manage_users"
    MANAGE_VENDORS = "manage_vendors"
    
    # 웹 페이지 관리
    MANAGE_PAGES = "manage_pages"
    MANAGE_CONTENT = "manage_content"
    
    # 업체 관리
    MANAGE_OWN_VENDOR = "manage_own_vendor"
    CREATE_VENDOR_PROFILE = "create_vendor_profile"
    RECEIVE_BOOKINGS = "receive_bookings"
    
    # 일반 사용자
    USE_SERVICES = "use_services"
    CREATE_POSTS = "create_posts"
    VIEW_VENDORS = "view_vendors"


# 역할별 권한 매핑
ROLE_PERMISSIONS = {
    UserRole.SYSTEM_ADMIN: [
        Permission.MANAGE_SYSTEM,
        Permission.MANAGE_USERS,
        Permission.MANAGE_VENDORS,
        Permission.MANAGE_PAGES,
        Permission.MANAGE_CONTENT,
        Permission.USE_SERVICES,
        Permission.CREATE_POSTS,
        Permission.VIEW_VENDORS,
    ],
    UserRole.WEB_ADMIN: [
        Permission.MANAGE_PAGES,
        Permission.MANAGE_CONTENT,
        Permission.VIEW_VENDORS,
    ],
    UserRole.VENDOR_ADMIN: [
        Permission.MANAGE_OWN_VENDOR,
        Permission.CREATE_VENDOR_PROFILE,
        Permission.RECEIVE_BOOKINGS,
        Permission.VIEW_VENDORS,
    ],
    UserRole.PARTNER_VENDOR: [
        Permission.MANAGE_OWN_VENDOR,
        Permission.CREATE_VENDOR_PROFILE,
        Permission.RECEIVE_BOOKINGS,
        Permission.VIEW_VENDORS,
    ],
    UserRole.USER: [
        Permission.USE_SERVICES,
        Permission.CREATE_POSTS,
        Permission.VIEW_VENDORS,
    ],
}


def has_permission(user_role: UserRole, permission: str) -> bool:
    """사용자 역할이 특정 권한을 가지고 있는지 확인"""
    if user_role not in ROLE_PERMISSIONS:
        return False
    return permission in ROLE_PERMISSIONS[user_role]


def can_access_admin(user_role: UserRole, admin_approval_status=None) -> bool:
    """관리자 페이지 접근 가능 여부 (승인 상태 확인 포함)"""
    from app.models.db.user import AdminApprovalStatus
    
    # 시스템 관리자는 항상 접근 가능
    if user_role == UserRole.SYSTEM_ADMIN:
        return True
    
    # 관리자 역할이지만 승인되지 않은 경우 접근 불가
    if user_role in [UserRole.WEB_ADMIN, UserRole.VENDOR_ADMIN]:
        if admin_approval_status is None:
            return False
        # 승인 상태가 APPROVED인 경우만 접근 가능
        if hasattr(admin_approval_status, 'value'):
            return admin_approval_status.value == AdminApprovalStatus.APPROVED.value
        return str(admin_approval_status) == AdminApprovalStatus.APPROVED.value
    
    return False


def can_manage_vendors(user_role: UserRole) -> bool:
    """벤더 관리 권한 여부"""
    return user_role in [
        UserRole.SYSTEM_ADMIN,
        UserRole.VENDOR_ADMIN,
        UserRole.PARTNER_VENDOR,
    ]


def can_manage_users(user_role: UserRole) -> bool:
    """사용자 관리 권한 여부"""
    return user_role == UserRole.SYSTEM_ADMIN

