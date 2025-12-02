"""
사용자 권한 관리 페이지
"""
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.user_roles import UserRole, can_manage_users
from app.models.db.user import User, AdminApprovalStatus, VendorApprovalStatus
from pydantic import BaseModel

router = APIRouter()


class UserRoleUpdateReq(BaseModel):
    user_id: int
    role: str




def require_system_admin(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """시스템 관리자만 접근 가능"""
    from fastapi import HTTPException
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=403, detail="시스템 관리자 권한이 필요합니다.")
    return user


@router.get("/dashboard/userauthsetting", response_class=HTMLResponse)
async def user_auth_setting_page(request: Request):
    """사용자 권한 설정 페이지"""
    base_url = str(request.base_url).rstrip('/')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>사용자 권한 설정 - Wedding OS</title>
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
            
            .header p {{
                color: #666;
                font-size: 1.1em;
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
            
            .role-info {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            
            .role-info h2 {{
                margin-bottom: 20px;
                color: #333;
            }}
            
            .role-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }}
            
            .role-card {{
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                background: #f9f9f9;
            }}
            
            .role-card.system-admin {{
                border-color: #ef4444;
                background: #fee2e2;
            }}
            
            .role-card.web-admin {{
                border-color: #3b82f6;
                background: #dbeafe;
            }}
            
            .role-card.vendor-admin {{
                border-color: #10b981;
                background: #d1fae5;
            }}
            
            .role-card.partner-vendor {{
                border-color: #f59e0b;
                background: #fef3c7;
            }}
            
            .role-card.user {{
                border-color: #9ca3af;
                background: #f3f4f6;
            }}
            
            .role-card h3 {{
                margin-bottom: 10px;
                color: #333;
            }}
            
            .role-card p {{
                color: #666;
                font-size: 0.9em;
                line-height: 1.6;
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
            
            .search-box {{
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1em;
                width: 300px;
            }}
            
            .category-select {{
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1em;
                background: white;
                cursor: pointer;
                min-width: 180px;
            }}
            
            .category-select:focus {{
                outline: none;
                border-color: #667eea;
            }}
            
            .category-tabs {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-bottom: 20px;
            }}
            
            .category-tab {{
                padding: 10px 20px;
                background: #f3f4f6;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 0.9em;
                color: #374151;
                font-weight: 500;
            }}
            
            .category-tab:hover {{
                background: #e5e7eb;
                border-color: #667eea;
                transform: translateY(-2px);
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
            }}
            
            .category-tab.active {{
                background: #667eea;
                border-color: #667eea;
                color: white;
                font-weight: 600;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}
            
            .search-box:focus {{
                outline: none;
                border-color: #667eea;
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
            
            .role-select {{
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 0.9em;
                cursor: pointer;
                min-width: 150px;
            }}
            
            .role-select:focus {{
                outline: none;
                border-color: #667eea;
            }}
            
            .btn-save {{
                padding: 8px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9em;
                transition: all 0.3s;
            }}
            
            .btn-save:hover {{
                background: #5568d3;
                transform: translateY(-2px);
            }}
            
            .btn-save:disabled {{
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }}
            
            .status-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            
            .status-badge.system-admin {{
                background: #fee2e2;
                color: #991b1b;
            }}
            
            .status-badge.web-admin {{
                background: #dbeafe;
                color: #1e40af;
            }}
            
            .status-badge.vendor-admin {{
                background: #d1fae5;
                color: #065f46;
            }}
            
            .status-badge.partner-vendor {{
                background: #fef3c7;
                color: #92400e;
            }}
            
            .status-badge.user {{
                background: #f3f4f6;
                color: #374151;
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
                <h1>👥 사용자 권한 설정</h1>
                <p>사용자의 역할과 권한을 관리합니다.</p>
            </div>
            
            <div class="role-info">
                <h2>📋 역할 설명 (클릭하여 필터링)</h2>
                <div class="role-grid">
                    <div class="role-card system-admin" onclick="filterByRole('SYSTEM_ADMIN')" style="cursor: pointer;">
                        <h3>🔴 시스템 관리자 (SYSTEM_ADMIN)</h3>
                        <p>개발자 - 시스템 관리자: 모든 권한을 가집니다. 시스템 전체를 관리할 수 있습니다.</p>
                    </div>
                    <div class="role-card web-admin" onclick="filterByRole('WEB_ADMIN')" style="cursor: pointer;">
                        <h3>🔵 웹 페이지 관리자 (WEB_ADMIN)</h3>
                        <p>시스템 접근 외의 제공된 웹페이지에서 페이지 관리가 가능합니다.</p>
                    </div>
                    <div class="role-card vendor-admin" onclick="filterByRole('VENDOR_ADMIN')" style="cursor: pointer;">
                        <h3>🟢 업체 관리자 (VENDOR_ADMIN)</h3>
                        <p>시스템 접근 외의 제공된 웹페이지에서 페이지 관리가 가능합니다.</p>
                    </div>
                    <div class="role-card partner-vendor" onclick="filterByRole('PARTNER_VENDOR')" style="cursor: pointer;">
                        <h3>🟡 제휴 업체 (PARTNER_VENDOR)</h3>
                        <p>업체들의 홍보성, 설명 등 작성 가능, 예약 받기 등이 가능합니다.</p>
                    </div>
                    <div class="role-card user" onclick="filterByRole('USER')" style="cursor: pointer;">
                        <h3>⚪ 사용자 (USER)</h3>
                        <p>실제 결혼하는 사람들. 기본 서비스를 이용할 수 있습니다.</p>
                    </div>
                    <div class="role-card" onclick="filterByRole(null)" style="cursor: pointer; border-color: #667eea; background: #e0e7ff;">
                        <h3>🔵 전체 보기</h3>
                        <p>모든 사용자를 표시합니다.</p>
                    </div>
                </div>
            </div>
            
            <div class="user-table-container">
                <div class="table-header">
                    <h2>사용자 목록</h2>
                    <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                        <a href="#" id="vendorApprovalLink" class="btn-save" style="text-decoration: none; display: inline-block; padding: 8px 16px;">
                            제휴 업체 승인 관리
                        </a>
                        <a href="#" id="adminApprovalLink" class="btn-save" style="text-decoration: none; display: inline-block; padding: 8px 16px; background: #8b5cf6;">
                            관리자 승인 관리
                        </a>
                        <select id="categoryFilter" class="category-select" onchange="filterByCategory()">
                            <option value="all">전체 사용자</option>
                            <option value="role">역할별</option>
                            <option value="approval">승인 상태별</option>
                            <option value="couple">커플 연결 상태별</option>
                            <option value="recent">최근 가입자 (7일 이내)</option>
                        </select>
                        <input type="text" class="search-box" id="searchInput" placeholder="이메일 또는 닉네임 검색..." oninput="applyFilters()">
                    </div>
                </div>
                
                <div id="categoryTabs" style="display: none; margin: 20px 0; padding: 15px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px;">
                    <!-- 카테고리별 탭이 여기에 동적으로 생성됩니다 -->
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
            let originalUsers = [];
            let currentRoleFilter = null;
            let currentCategory = 'all';
            let currentCategoryFilter = null;
            
            // 페이지 로드 시 사용자 목록 가져오기
            async function loadUsers() {{
                try {{
                    const response = await fetch(`${{baseUrl}}/secret_admin/api/admin/users`, {{
                        headers: {{
                            'Authorization': `Bearer ${{localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || ''}}`
                        }}
                    }});
                    
                    if (!response.ok) {{
                        throw new Error('사용자 목록을 불러올 수 없습니다.');
                    }}
                    
                    const data = await response.json();
                    users = data.data.users || [];
                    originalUsers = [...users];
                    applyFilters();
                }} catch (error) {{
                    document.getElementById('userTableContainer').innerHTML = 
                        `<div class="error">${{error.message}}</div>`;
                }}
            }}
            
            // 역할별 필터링
            function filterByRole(role) {{
                console.log('필터링:', role);
                currentRoleFilter = role;
                applyFilters();
                
                // 선택된 역할 카드 강조
                document.querySelectorAll('.role-card').forEach(card => {{
                    card.style.opacity = '1';
                    card.style.transform = 'scale(1)';
                    card.style.borderWidth = '2px';
                }});
                
                if (role) {{
                    const roleClass = role.toLowerCase().replace('_', '-');
                    const selectedCard = document.querySelector(`.role-card.${{roleClass}}`);
                    if (selectedCard) {{
                        selectedCard.style.opacity = '0.9';
                        selectedCard.style.transform = 'scale(0.98)';
                        selectedCard.style.borderWidth = '3px';
                    }}
                }} else {{
                    // 전체 보기 선택
                    const allCard = document.querySelector('.role-card:last-child');
                    if (allCard) {{
                        allCard.style.opacity = '0.9';
                        allCard.style.transform = 'scale(0.98)';
                        allCard.style.borderWidth = '3px';
                    }}
                }}
            }}
            
            // 카테고리별 필터링
            function filterByCategory() {{
                const categorySelect = document.getElementById('categoryFilter');
                currentCategory = categorySelect.value;
                currentCategoryFilter = null;
                currentRoleFilter = null;
                
                const categoryTabsDiv = document.getElementById('categoryTabs');
                
                // 역할 카드 초기화
                document.querySelectorAll('.role-card').forEach(card => {{
                    card.style.opacity = '1';
                    card.style.transform = 'scale(1)';
                    card.style.borderWidth = '2px';
                }});
                
                if (currentCategory === 'all') {{
                    categoryTabsDiv.style.display = 'none';
                    categoryTabsDiv.innerHTML = '';
                }} else                 if (currentCategory === 'role') {{
                    categoryTabsDiv.style.display = 'block';
                    categoryTabsDiv.innerHTML = `
                        <div class="category-tabs">
                            <div class="category-tab" data-filter="SYSTEM_ADMIN" onclick="selectCategoryFilter('SYSTEM_ADMIN', this)">시스템 관리자</div>
                            <div class="category-tab" data-filter="WEB_ADMIN" onclick="selectCategoryFilter('WEB_ADMIN', this)">웹 관리자</div>
                            <div class="category-tab" data-filter="VENDOR_ADMIN" onclick="selectCategoryFilter('VENDOR_ADMIN', this)">업체 관리자</div>
                            <div class="category-tab" data-filter="PARTNER_VENDOR" onclick="selectCategoryFilter('PARTNER_VENDOR', this)">제휴 업체</div>
                            <div class="category-tab" data-filter="USER" onclick="selectCategoryFilter('USER', this)">일반 사용자</div>
                            <div class="category-tab active" data-filter="all" onclick="selectCategoryFilter(null, this)">전체</div>
                        </div>
                    `;
                }} else if (currentCategory === 'approval') {{
                    categoryTabsDiv.style.display = 'block';
                    categoryTabsDiv.innerHTML = `
                        <div class="category-tabs">
                            <div class="category-tab" data-filter="vendor_pending" onclick="selectCategoryFilter('vendor_pending', this)">제휴 업체 승인 대기</div>
                            <div class="category-tab" data-filter="vendor_approved" onclick="selectCategoryFilter('vendor_approved', this)">제휴 업체 승인됨</div>
                            <div class="category-tab" data-filter="admin_pending" onclick="selectCategoryFilter('admin_pending', this)">관리자 승인 대기</div>
                            <div class="category-tab" data-filter="admin_approved" onclick="selectCategoryFilter('admin_approved', this)">관리자 승인됨</div>
                            <div class="category-tab active" data-filter="all" onclick="selectCategoryFilter(null, this)">전체</div>
                        </div>
                    `;
                }} else if (currentCategory === 'couple') {{
                    categoryTabsDiv.style.display = 'block';
                    categoryTabsDiv.innerHTML = `
                        <div class="category-tabs">
                            <div class="category-tab" data-filter="connected" onclick="selectCategoryFilter('connected', this)">커플 연결됨</div>
                            <div class="category-tab" data-filter="not_connected" onclick="selectCategoryFilter('not_connected', this)">커플 미연결</div>
                            <div class="category-tab active" data-filter="all" onclick="selectCategoryFilter(null, this)">전체</div>
                        </div>
                    `;
                }} else if (currentCategory === 'recent') {{
                    categoryTabsDiv.style.display = 'none';
                    categoryTabsDiv.innerHTML = '';
                }}
                
                applyFilters();
            }}
            
            // 카테고리 필터 선택
            function selectCategoryFilter(filter, element) {{
                currentCategoryFilter = filter;
                
                // 탭 활성화 상태 업데이트
                document.querySelectorAll('.category-tab').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                if (element) {{
                    element.classList.add('active');
                }}
                
                applyFilters();
            }}
            
            // 필터 적용
            function applyFilters() {{
                let filtered = [...originalUsers];
                
                // 카테고리별 필터
                if (currentCategory === 'role' && currentCategoryFilter) {{
                    filtered = filtered.filter(user => user.role === currentCategoryFilter);
                }} else if (currentCategory === 'approval') {{
                    if (currentCategoryFilter === 'vendor_pending') {{
                        filtered = filtered.filter(user => user.vendor_approval_status === 'PENDING');
                    }} else if (currentCategoryFilter === 'vendor_approved') {{
                        filtered = filtered.filter(user => user.vendor_approval_status === 'APPROVED');
                    }} else if (currentCategoryFilter === 'admin_pending') {{
                        filtered = filtered.filter(user => user.admin_approval_status === 'PENDING');
                    }} else if (currentCategoryFilter === 'admin_approved') {{
                        filtered = filtered.filter(user => user.admin_approval_status === 'APPROVED');
                    }}
                }} else if (currentCategory === 'couple') {{
                    if (currentCategoryFilter === 'connected') {{
                        filtered = filtered.filter(user => user.couple_id !== null);
                    }} else if (currentCategoryFilter === 'not_connected') {{
                        filtered = filtered.filter(user => user.couple_id === null);
                    }}
                }} else if (currentCategory === 'recent') {{
                    const sevenDaysAgo = new Date();
                    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
                    filtered = filtered.filter(user => {{
                        if (!user.created_at) return false;
                        const createdDate = new Date(user.created_at);
                        return createdDate >= sevenDaysAgo;
                    }});
                }}
                
                // 역할 필터 (역할 카드 클릭 시)
                if (currentRoleFilter !== null && currentRoleFilter !== undefined && currentRoleFilter !== '') {{
                    filtered = filtered.filter(user => user.role === currentRoleFilter);
                }}
                
                // 검색 필터
                const searchInput = document.getElementById('searchInput');
                if (searchInput) {{
                    const searchTerm = searchInput.value.toLowerCase();
                    if (searchTerm) {{
                        filtered = filtered.filter(user => 
                            user.email.toLowerCase().includes(searchTerm) ||
                            user.nickname.toLowerCase().includes(searchTerm)
                        );
                    }}
                }}
                
                console.log(`필터링 결과: ${{filtered.length}}명`);
                users = filtered;
                renderUsers();
            }}
            
            // 사용자 목록 렌더링
            function renderUsers() {{
                const container = document.getElementById('userTableContainer');
                
                if (users.length === 0) {{
                    container.innerHTML = '<div class="loading">사용자가 없습니다.</div>';
                    return;
                }}
                
                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>이메일</th>
                                <th>닉네임</th>
                                <th>현재 역할</th>
                                <th>역할 변경</th>
                                <th>생성일</th>
                                <th>작업</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                users.forEach(user => {{
                    const roleClass = user.role.toLowerCase().replace('_', '-');
                    html += `
                        <tr data-user-id="${{user.id}}">
                            <td>${{user.id}}</td>
                            <td>${{user.email}}</td>
                            <td>${{user.nickname}}</td>
                            <td><span class="status-badge ${{roleClass}}">${{user.role}}</span></td>
                            <td>
                                <select class="role-select" data-user-id="${{user.id}}" value="${{user.role}}">
                                    <option value="SYSTEM_ADMIN" ${{user.role === 'SYSTEM_ADMIN' ? 'selected' : ''}}>시스템 관리자</option>
                                    <option value="WEB_ADMIN" ${{user.role === 'WEB_ADMIN' ? 'selected' : ''}}>웹 페이지 관리자</option>
                                    <option value="VENDOR_ADMIN" ${{user.role === 'VENDOR_ADMIN' ? 'selected' : ''}}>업체 관리자</option>
                                    <option value="PARTNER_VENDOR" ${{user.role === 'PARTNER_VENDOR' ? 'selected' : ''}}>제휴 업체</option>
                                    <option value="USER" ${{user.role === 'USER' ? 'selected' : ''}}>사용자</option>
                                </select>
                            </td>
                            <td>${{new Date(user.created_at).toLocaleDateString('ko-KR')}}</td>
                            <td>
                                <button class="btn-save" onclick="updateUserRole(${{user.id}})">저장</button>
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
            
            // 역할 업데이트
            async function updateUserRole(userId) {{
                const select = document.querySelector(`select[data-user-id="${{userId}}"]`);
                const newRole = select.value;
                
                try {{
                    const response = await fetch(`${{baseUrl}}/secret_admin/api/admin/users/role`, {{
                        method: 'PUT',
                        headers: {{
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${{localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || ''}}`
                        }},
                        body: JSON.stringify({{
                            user_id: userId,
                            role: newRole
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        showMessage('역할이 성공적으로 변경되었습니다.', 'success');
                        await loadUsers();
                    }} else {{
                        showMessage(data.error || '역할 변경에 실패했습니다.', 'error');
                    }}
                }} catch (error) {{
                    showMessage('역할 변경 중 오류가 발생했습니다.', 'error');
                }}
            }}
            
            // 검색 기능
            document.getElementById('searchInput').addEventListener('input', (e) => {{
                applyFilters();
            }});
            
            // 메시지 표시
            function showMessage(message, type) {{
                const messageArea = document.getElementById('messageArea');
                messageArea.innerHTML = `<div class="${{type}}">${{message}}</div>`;
                setTimeout(() => {{
                    messageArea.innerHTML = '';
                }}, 3000);
            }}
            
            // 제휴 업체 승인 관리 링크 설정
            document.addEventListener('DOMContentLoaded', function() {{
                const token = localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || '';
                const vendorApprovalLink = document.getElementById('vendorApprovalLink');
                if (vendorApprovalLink && token) {{
                    vendorApprovalLink.href = `${{baseUrl}}/secret_admin/dashboard/vendor-approval?token=${{encodeURIComponent(token)}}`;
                }} else if (vendorApprovalLink) {{
                    vendorApprovalLink.href = `${{baseUrl}}/secret_admin/dashboard/vendor-approval`;
                }}
                
                const adminApprovalLink = document.getElementById('adminApprovalLink');
                if (adminApprovalLink && token) {{
                    adminApprovalLink.href = `${{baseUrl}}/secret_admin/dashboard/admin-approval?token=${{encodeURIComponent(token)}}`;
                }} else if (adminApprovalLink) {{
                    adminApprovalLink.href = `${{baseUrl}}/secret_admin/dashboard/admin-approval`;
                }}
            }});
            
            // 페이지 로드
            loadUsers();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/api/admin/users")
async def get_users(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """사용자 목록 조회 (시스템 관리자만)"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.nickname.ilike(f"%{search}%")
            )
        )
    
    users = query.order_by(User.created_at.desc()).all()
    
    return {
        "message": "users_retrieved",
        "data": {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                    "profile_image_url": user.profile_image_url,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "vendor_approval_status": user.vendor_approval_status.value if user.vendor_approval_status and hasattr(user.vendor_approval_status, 'value') else (str(user.vendor_approval_status) if user.vendor_approval_status else None),
                    "admin_approval_status": user.admin_approval_status.value if user.admin_approval_status and hasattr(user.admin_approval_status, 'value') else (str(user.admin_approval_status) if user.admin_approval_status else None),
                    "couple_id": user.couple_id,
                    "gender": user.gender.value if user.gender and hasattr(user.gender, 'value') else (str(user.gender) if user.gender else None),
                }
                for user in users
            ]
        }
    }


@router.put("/api/admin/users/role")
async def update_user_role(
    request: UserRoleUpdateReq,
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """사용자 역할 변경 (시스템 관리자만)"""
    from app.models.db.user import VendorApprovalStatus
    
    user = db.query(User).filter(User.id == request.user_id).first()
    
    if not user:
        return JSONResponse(
            status_code=404,
            content={"message": "error", "data": {"error": "사용자를 찾을 수 없습니다."}}
        )
    
    try:
        new_role = UserRole(request.role)
        old_role = user.role
        user.role = new_role
        
        # 관리자 역할로 변경 시 승인 대기 상태로 설정
        if new_role in [UserRole.SYSTEM_ADMIN, UserRole.WEB_ADMIN, UserRole.VENDOR_ADMIN]:
            # 관리자 역할로 변경하는 경우 승인 대기 상태로 설정
            if old_role not in [UserRole.SYSTEM_ADMIN, UserRole.WEB_ADMIN, UserRole.VENDOR_ADMIN]:
                # 기존에 관리자가 아니었던 경우에만 승인 대기로 설정
                user.admin_approval_status = AdminApprovalStatus.PENDING
        elif new_role == UserRole.PARTNER_VENDOR:
            # 제휴 업체로 변경 시 승인 상태 업데이트
            user.vendor_approval_status = VendorApprovalStatus.APPROVED
            # 관리자 승인 상태 초기화
            if user.admin_approval_status:
                user.admin_approval_status = None
        else:
            # 일반 사용자로 변경 시 모든 승인 상태 초기화
            if user.vendor_approval_status:
                user.vendor_approval_status = None
            if user.admin_approval_status:
                user.admin_approval_status = None
        
        db.commit()
        db.refresh(user)
        
        return {
            "message": "user_role_updated",
            "data": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            }
        }
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"message": "error", "data": {"error": "유효하지 않은 역할입니다."}}
        )



