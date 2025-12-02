"""
관리자 승인 관리 페이지
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.user_roles import UserRole
from app.models.db.user import User, AdminApprovalStatus

router = APIRouter()


def require_system_admin(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """시스템 관리자만 접근 가능"""
    from fastapi import HTTPException
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=403, detail="시스템 관리자 권한이 필요합니다.")
    return user


@router.get("/dashboard/admin-approval", response_class=HTMLResponse)
async def admin_approval_page(request: Request):
    """관리자 승인 관리 페이지"""
    base_url = str(request.base_url).rstrip('/')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>관리자 승인 관리 - Wedding OS</title>
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
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            }}
            
            .back-link {{
                display: inline-block;
                margin-bottom: 20px;
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
            }}
            
            .back-link:hover {{
                text-decoration: underline;
            }}
            
            .header {{
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                color: #333;
                margin-bottom: 10px;
            }}
            
            .header p {{
                color: #666;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            
            th, td {{
                padding: 12px;
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
            }}
            
            .btn-approve:hover {{
                background: #059669;
            }}
            
            .btn-reject {{
                padding: 8px 16px;
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9em;
            }}
            
            .btn-reject:hover {{
                background: #dc2626;
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
                <h1>✅ 관리자 승인 관리</h1>
                <p>관리자 역할로 변경된 사용자들의 승인 여부를 관리합니다.</p>
            </div>
            
            <div id="messageArea"></div>
            
            <div id="pendingAdminsTableContainer">
                <div class="loading">로딩 중...</div>
            </div>
        </div>
        
        <script>
            const baseUrl = '{base_url}';
            const urlParams = new URLSearchParams(window.location.search);
            const tokenFromQuery = urlParams.get('token');
            if (tokenFromQuery) {{
                localStorage.setItem('wedding_access_token', tokenFromQuery);
                localStorage.setItem('access_token', tokenFromQuery);
                const newUrl = window.location.pathname;
                window.history.replaceState({{}}, '', newUrl);
            }}
            
            let pendingAdmins = [];
            
            async function loadPendingAdmins() {{
                try {{
                    const response = await fetch(`${{baseUrl}}/secret_admin/api/admin/admins/pending`, {{
                        headers: {{
                            'Authorization': `Bearer ${{localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || ''}}`
                        }}
                    }});
                    
                    if (!response.ok) {{
                        throw new Error('승인 대기 중인 관리자 목록을 불러올 수 없습니다.');
                    }}
                    
                    const data = await response.json();
                    pendingAdmins = data.data.users || [];
                    renderPendingAdmins();
                }} catch (error) {{
                    document.getElementById('pendingAdminsTableContainer').innerHTML = 
                        `<div class="error">${{error.message}}</div>`;
                }}
            }}
            
            function renderPendingAdmins() {{
                const container = document.getElementById('pendingAdminsTableContainer');
                
                if (pendingAdmins.length === 0) {{
                    container.innerHTML = '<div class="loading">승인 대기 중인 관리자가 없습니다.</div>';
                    return;
                }}
                
                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>이메일</th>
                                <th>닉네임</th>
                                <th>역할</th>
                                <th>가입일</th>
                                <th>작업</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                pendingAdmins.forEach(admin => {{
                    html += `
                        <tr data-user-id="${{admin.id}}">
                            <td>${{admin.id}}</td>
                            <td>${{admin.email}}</td>
                            <td>${{admin.nickname}}</td>
                            <td>${{admin.role}}</td>
                            <td>${{new Date(admin.created_at).toLocaleDateString('ko-KR')}}</td>
                            <td>
                                <button class="btn-approve" onclick="approveAdmin(${{admin.id}})">승인</button>
                                <button class="btn-reject" onclick="rejectAdmin(${{admin.id}})">거부</button>
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
            
            async function approveAdmin(userId) {{
                try {{
                    const response = await fetch(`${{baseUrl}}/secret_admin/api/admin/admins/${{userId}}/approve`, {{
                        method: 'PUT',
                        headers: {{
                            'Authorization': `Bearer ${{localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || ''}}`
                        }}
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        showMessage('관리자가 승인되었습니다.', 'success');
                        await loadPendingAdmins();
                    }} else {{
                        showMessage(data.data?.error || data.message || '승인에 실패했습니다.', 'error');
                    }}
                }} catch (error) {{
                    showMessage('승인 중 오류가 발생했습니다.', 'error');
                }}
            }}
            
            async function rejectAdmin(userId) {{
                try {{
                    const response = await fetch(`${{baseUrl}}/secret_admin/api/admin/admins/${{userId}}/reject`, {{
                        method: 'PUT',
                        headers: {{
                            'Authorization': `Bearer ${{localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || ''}}`
                        }}
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        showMessage('관리자가 거부되었습니다.', 'success');
                        await loadPendingAdmins();
                    }} else {{
                        showMessage(data.data?.error || data.message || '거부에 실패했습니다.', 'error');
                    }}
                }} catch (error) {{
                    showMessage('거부 중 오류가 발생했습니다.', 'error');
                }}
            }}
            
            function showMessage(message, type) {{
                const messageArea = document.getElementById('messageArea');
                messageArea.innerHTML = `<div class="${{type}}">${{message}}</div>`;
                setTimeout(() => {{
                    messageArea.innerHTML = '';
                }}, 3000);
            }}
            
            loadPendingAdmins();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/api/admin/admins/pending")
async def get_pending_admins(
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """승인 대기 중인 관리자 목록 조회"""
    pending_users = db.query(User).filter(
        User.admin_approval_status == AdminApprovalStatus.PENDING
    ).order_by(User.created_at.desc()).all()
    
    return {
        "message": "pending_admins_retrieved",
        "data": {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                }
                for user in pending_users
            ]
        }
    }


@router.put("/api/admin/admins/{user_id}/approve")
async def approve_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """관리자 승인"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return JSONResponse(
            status_code=404,
            content={"message": "error", "data": {"error": "사용자를 찾을 수 없습니다."}}
        )
    
    if user.admin_approval_status != AdminApprovalStatus.PENDING:
        return JSONResponse(
            status_code=400,
            content={"message": "error", "data": {"error": "승인 대기 중인 사용자가 아닙니다."}}
        )
    
    user.admin_approval_status = AdminApprovalStatus.APPROVED
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "admin_approved",
        "data": {
            "id": user.id,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        }
    }


@router.put("/api/admin/admins/{user_id}/reject")
async def reject_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """관리자 거부"""
    from app.core.user_roles import UserRole
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return JSONResponse(
            status_code=404,
            content={"message": "error", "data": {"error": "사용자를 찾을 수 없습니다."}}
        )
    
    if user.admin_approval_status != AdminApprovalStatus.PENDING:
        return JSONResponse(
            status_code=400,
            content={"message": "error", "data": {"error": "승인 대기 중인 사용자가 아닙니다."}}
        )
    
    # 거부 시 일반 사용자로 변경
    user.role = UserRole.USER
    user.admin_approval_status = AdminApprovalStatus.REJECTED
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "admin_rejected",
        "data": {
            "id": user.id,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        }
    }

