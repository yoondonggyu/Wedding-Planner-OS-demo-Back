"""
제휴 업체 승인 관리 페이지
"""
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.user_roles import UserRole
from app.models.db.user import User, VendorApprovalStatus
from app.core.exceptions import bad_request, not_found
from app.core.error_codes import ErrorCode

router = APIRouter()


def require_system_admin(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """시스템 관리자만 접근 가능"""
    from fastapi import HTTPException
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=403, detail="시스템 관리자 권한이 필요합니다.")
    return user


@router.get("/dashboard/vendor-approval", response_class=HTMLResponse)
async def vendor_approval_page(request: Request):
    """제휴 업체 승인 관리 페이지"""
    base_url = str(request.base_url).rstrip('/')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>제휴 업체 승인 관리 - Wedding OS</title>
        <link rel="icon" type="image/png" href="{base_url}/static/favicon.png">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            
            .header {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            
            .header h1 {{
                font-size: 2em;
                margin-bottom: 10px;
                color: #333;
            }}
            
            .back-link {{
                display: inline-block;
                margin-bottom: 20px;
                color: white;
                text-decoration: none;
                padding: 10px 20px;
                background: rgba(255,255,255,0.2);
                border-radius: 8px;
                transition: all 0.3s;
            }}
            
            .back-link:hover {{
                background: rgba(255,255,255,0.3);
            }}
            
            .user-table-container {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            
            .table-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }}
            
            .table-header h2 {{
                color: #333;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            th, td {{
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }}
            
            th {{
                background: #f9f9f9;
                font-weight: 600;
                color: #333;
            }}
            
            tr:hover {{
                background: #f9f9f9;
            }}
            
            .btn-approve {{
                padding: 8px 16px;
                background: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9em;
                margin-right: 8px;
                transition: all 0.3s;
            }}
            
            .btn-approve:hover {{
                background: #059669;
                transform: translateY(-2px);
            }}
            
            .btn-reject {{
                padding: 8px 16px;
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9em;
                transition: all 0.3s;
            }}
            
            .btn-reject:hover {{
                background: #dc2626;
                transform: translateY(-2px);
            }}
            
            .status-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            
            .status-badge.pending {{
                background: #fef3c7;
                color: #92400e;
            }}
            
            .loading {{
                text-align: center;
                padding: 40px;
                color: #666;
            }}
            
            .error {{
                background: #fee2e2;
                color: #991b1b;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            
            .success {{
                background: #d1fae5;
                color: #065f46;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="{base_url}/secret_admin/dashboard" class="back-link">← 대시보드로 돌아가기</a>
            
            <div class="header">
                <h1>✅ 제휴 업체 승인 관리</h1>
                <p>제휴 업체 가입 신청을 승인하거나 거부합니다.</p>
            </div>
            
            <div class="user-table-container">
                <div class="table-header">
                    <h2>승인 대기 중인 제휴 업체</h2>
                </div>
                
                <div id="messageArea"></div>
                
                <div id="userTableContainer">
                    <div class="loading">로딩 중...</div>
                </div>
            </div>
        </div>
        
        <script>
            const baseUrl = '{base_url}';
            // 쿼리 파라미터에서 토큰 가져와서 localStorage에 저장
            const urlParams = new URLSearchParams(window.location.search);
            const tokenFromQuery = urlParams.get('token');
            if (tokenFromQuery) {{
                localStorage.setItem('wedding_access_token', tokenFromQuery);
                localStorage.setItem('access_token', tokenFromQuery);
                // URL에서 토큰 제거 (보안)
                const newUrl = window.location.pathname;
                window.history.replaceState({{}}, '', newUrl);
            }}
            
            let users = [];
            
            // 페이지 로드 시 승인 대기 목록 가져오기
            async function loadPendingVendors() {{
                try {{
                    const response = await fetch(`${{baseUrl}}/secret_admin/api/admin/vendors/pending`, {{
                        headers: {{
                            'Authorization': `Bearer ${{localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || ''}}`
                        }}
                    }});
                    
                    if (!response.ok) {{
                        throw new Error('승인 대기 목록을 불러올 수 없습니다.');
                    }}
                    
                    const data = await response.json();
                    users = data.data.users || [];
                    renderUsers();
                }} catch (error) {{
                    document.getElementById('userTableContainer').innerHTML = 
                        `<div class="error">${{error.message}}</div>`;
                }}
            }}
            
            // 사용자 목록 렌더링
            function renderUsers() {{
                const container = document.getElementById('userTableContainer');
                
                if (users.length === 0) {{
                    container.innerHTML = '<div class="loading">승인 대기 중인 제휴 업체가 없습니다.</div>';
                    return;
                }}
                
                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>이메일</th>
                                <th>닉네임</th>
                                <th>가입일</th>
                                <th>작업</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                users.forEach(user => {{
                    html += `
                        <tr data-user-id="${{user.id}}">
                            <td>${{user.id}}</td>
                            <td>${{user.email}}</td>
                            <td>${{user.nickname}}</td>
                            <td>${{new Date(user.created_at).toLocaleDateString('ko-KR')}}</td>
                            <td>
                                <button class="btn-approve" onclick="approveVendor(${{user.id}})">승인</button>
                                <button class="btn-reject" onclick="rejectVendor(${{user.id}})">거부</button>
                            </td>
                        </tr>
                    `;
                }});
                
                html += `
                        </tbody>
                    </table>
                `;
                
                container.innerHTML = html;
            }}
            
            // 제휴 업체 승인
            async function approveVendor(userId) {{
                if (!confirm('이 사용자를 제휴 업체로 승인하시겠습니까?')) {{
                    return;
                }}
                
                try {{
                    const response = await fetch(`${{baseUrl}}/secret_admin/api/admin/vendors/${{userId}}/approve`, {{
                        method: 'PUT',
                        headers: {{
                            'Authorization': `Bearer ${{localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || ''}}`
                        }}
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        showMessage('제휴 업체가 승인되었습니다.', 'success');
                        await loadPendingVendors();
                    }} else {{
                        showMessage(data.data?.error || '승인에 실패했습니다.', 'error');
                    }}
                }} catch (error) {{
                    showMessage('승인 중 오류가 발생했습니다.', 'error');
                }}
            }}
            
            // 제휴 업체 거부
            async function rejectVendor(userId) {{
                if (!confirm('이 사용자의 제휴 업체 가입을 거부하시겠습니까?')) {{
                    return;
                }}
                
                try {{
                    const response = await fetch(`${{baseUrl}}/secret_admin/api/admin/vendors/${{userId}}/reject`, {{
                        method: 'PUT',
                        headers: {{
                            'Authorization': `Bearer ${{localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || ''}}`
                        }}
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        showMessage('제휴 업체 가입이 거부되었습니다.', 'success');
                        await loadPendingVendors();
                    }} else {{
                        showMessage(data.data?.error || '거부에 실패했습니다.', 'error');
                    }}
                }} catch (error) {{
                    showMessage('거부 중 오류가 발생했습니다.', 'error');
                }}
            }}
            
            // 메시지 표시
            function showMessage(message, type) {{
                const messageArea = document.getElementById('messageArea');
                messageArea.innerHTML = `<div class="${{type}}">${{message}}</div>`;
                setTimeout(() => {{
                    messageArea.innerHTML = '';
                }}, 3000);
            }}
            
            // 페이지 로드
            loadPendingVendors();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/api/admin/vendors/pending")
async def get_pending_vendors(
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """승인 대기 중인 제휴 업체 목록 조회"""
    pending_users = db.query(User).filter(
        User.vendor_approval_status == VendorApprovalStatus.PENDING
    ).order_by(User.created_at.desc()).all()
    
    return {
        "message": "pending_vendors_retrieved",
        "data": {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                }
                for user in pending_users
            ]
        }
    }


@router.put("/api/admin/vendors/{user_id}/approve")
async def approve_vendor(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """제휴 업체 승인"""
    from app.core.user_roles import UserRole
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return JSONResponse(
            status_code=404,
            content={"message": "error", "data": {"error": "사용자를 찾을 수 없습니다."}}
        )
    
    if user.vendor_approval_status != VendorApprovalStatus.PENDING:
        return JSONResponse(
            status_code=400,
            content={"message": "error", "data": {"error": "승인 대기 중인 사용자가 아닙니다."}}
        )
    
    user.role = UserRole.PARTNER_VENDOR
    user.vendor_approval_status = VendorApprovalStatus.APPROVED
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "vendor_approved",
        "data": {
            "id": user.id,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        }
    }


@router.put("/api/admin/vendors/{user_id}/reject")
async def reject_vendor(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """제휴 업체 거부"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return JSONResponse(
            status_code=404,
            content={"message": "error", "data": {"error": "사용자를 찾을 수 없습니다."}}
        )
    
    if user.vendor_approval_status != VendorApprovalStatus.PENDING:
        return JSONResponse(
            status_code=400,
            content={"message": "error", "data": {"error": "승인 대기 중인 사용자가 아닙니다."}}
        )
    
    user.vendor_approval_status = VendorApprovalStatus.REJECTED
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "vendor_rejected",
        "data": {
            "id": user.id,
            "email": user.email,
        }
    }

