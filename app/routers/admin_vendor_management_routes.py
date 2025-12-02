"""
벤더 관리 페이지 (시스템 관리자용)
"""
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.user_roles import UserRole, can_manage_vendors
from app.models.db.user import User
from app.models.db.vendor import Vendor, VendorType
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter()


class VendorCreateReq(BaseModel):
    vendor_type: str
    name: str
    description: Optional[str] = None
    base_location_city: str
    base_location_district: str
    service_area: Optional[List[str]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    contact_link: Optional[str] = None
    contact_phone: Optional[str] = None
    tags: Optional[List[str]] = None
    portfolio_images: Optional[List[str]] = None
    portfolio_videos: Optional[List[str]] = None
    # 타입별 상세 정보
    iphone_snap_detail: Optional[dict] = None
    mc_detail: Optional[dict] = None
    singer_detail: Optional[dict] = None
    studio_detail: Optional[dict] = None
    venue_detail: Optional[dict] = None


class VendorUpdateReq(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_location_city: Optional[str] = None
    base_location_district: Optional[str] = None
    service_area: Optional[List[str]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    contact_link: Optional[str] = None
    contact_phone: Optional[str] = None
    tags: Optional[List[str]] = None
    portfolio_images: Optional[List[str]] = None
    portfolio_videos: Optional[List[str]] = None
    iphone_snap_detail: Optional[dict] = None
    mc_detail: Optional[dict] = None
    singer_detail: Optional[dict] = None
    studio_detail: Optional[dict] = None
    venue_detail: Optional[dict] = None


def require_system_admin(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """시스템 관리자만 접근 가능"""
    from fastapi import HTTPException
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=403, detail="시스템 관리자 권한이 필요합니다.")
    return user


@router.get("/dashboard/vendor-management", response_class=HTMLResponse)
async def vendor_management_page(request: Request):
    """제휴 업체 관리 페이지"""
    base_url = str(request.base_url).rstrip('/')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>제휴 업체 관리 - Wedding OS</title>
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
                max-width: 1600px;
                margin: 0 auto;
            }}
            
            .header {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .header h1 {{
                font-size: 2em;
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
            
            .btn-primary {{
                padding: 12px 24px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                transition: all 0.3s;
            }}
            
            .btn-primary:hover {{
                background: #5568d3;
                transform: translateY(-2px);
            }}
            
            .filters {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }}
            
            .filter-group {{
                display: flex;
                flex-direction: column;
                gap: 5px;
            }}
            
            .filter-group label {{
                font-size: 0.9em;
                color: #666;
                font-weight: 600;
            }}
            
            .filter-group select,
            .filter-group input {{
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 0.9em;
            }}
            
            .vendor-table-container {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
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
            
            .btn-edit, .btn-delete {{
                padding: 6px 12px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.85em;
                margin-right: 5px;
            }}
            
            .btn-edit {{
                background: #3b82f6;
                color: white;
            }}
            
            .btn-delete {{
                background: #ef4444;
                color: white;
            }}
            
            .btn-edit:hover {{
                background: #2563eb;
            }}
            
            .btn-delete:hover {{
                background: #dc2626;
            }}
            
            .modal {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 1000;
            }}
            
            .modal-content {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 600px;
                width: 90%;
                max-height: 90vh;
                overflow-y: auto;
            }}
            
            .modal-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }}
            
            .modal-header h2 {{
                color: #333;
            }}
            
            .close-btn {{
                background: none;
                border: none;
                font-size: 1.5em;
                cursor: pointer;
                color: #666;
            }}
            
            .form-group {{
                margin-bottom: 15px;
            }}
            
            .form-group label {{
                display: block;
                margin-bottom: 5px;
                color: #333;
                font-weight: 600;
            }}
            
            .form-group input,
            .form-group select,
            .form-group textarea {{
                width: 100%;
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 0.9em;
            }}
            
            .form-group textarea {{
                min-height: 100px;
                resize: vertical;
            }}
            
            .form-actions {{
                display: flex;
                gap: 10px;
                justify-content: flex-end;
                margin-top: 20px;
            }}
            
            .btn-cancel {{
                padding: 10px 20px;
                background: #e0e0e0;
                color: #333;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }}
            
            .btn-save {{
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }}
            
            .vendor-type-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            
            .vendor-type-badge.IPHONE_SNAP {{ background: #dbeafe; color: #1e40af; }}
            .vendor-type-badge.MC {{ background: #fef3c7; color: #92400e; }}
            .vendor-type-badge.SINGER {{ background: #fce7f3; color: #9f1239; }}
            .vendor-type-badge.STUDIO_PREWEDDING {{ background: #d1fae5; color: #065f46; }}
            .vendor-type-badge.VENUE_OUTDOOR {{ background: #e0e7ff; color: #3730a3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="{base_url}/secret_admin/dashboard" class="back-link">← 대시보드로 돌아가기</a>
            
            <div class="header">
                <h1>🏢 제휴 업체 관리</h1>
                <button class="btn-primary" onclick="openCreateModal()">+ 새 제휴 업체 추가</button>
            </div>
            
            <div class="filters">
                <div class="filter-group">
                    <label>카테고리</label>
                    <select id="filterType">
                        <option value="">전체</option>
                        <option value="IPHONE_SNAP">아이폰 스냅</option>
                        <option value="MC">사회자</option>
                        <option value="SINGER">축가</option>
                        <option value="STUDIO_PREWEDDING">사전 웨딩 스튜디오</option>
                        <option value="VENUE_OUTDOOR">야외 결혼식 장소</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>지역</label>
                    <input type="text" id="filterLocation" placeholder="도시 또는 구">
                </div>
                <div class="filter-group">
                    <label>검색</label>
                    <input type="text" id="filterSearch" placeholder="제휴 업체명 검색">
                </div>
            </div>
            
            <div class="vendor-table-container">
                <div id="vendorTableContainer">
                    <div style="text-align: center; padding: 40px; color: #666;">로딩 중...</div>
                </div>
            </div>
        </div>
        
        <!-- 벤더 생성/수정 모달 -->
        <div id="vendorModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="modalTitle">새 제휴 업체 추가</h2>
                    <button class="close-btn" onclick="closeModal()">&times;</button>
                </div>
                <form id="vendorForm">
                    <input type="hidden" id="vendorId">
                    <div class="form-group">
                        <label>제휴 업체 타입 *</label>
                        <select id="vendorType" required>
                            <option value="">선택하세요</option>
                            <option value="IPHONE_SNAP">아이폰 스냅</option>
                            <option value="MC">사회자</option>
                            <option value="SINGER">축가</option>
                            <option value="STUDIO_PREWEDDING">사전 웨딩 스튜디오</option>
                            <option value="VENUE_OUTDOOR">야외 결혼식 장소</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>제휴 업체명 *</label>
                        <input type="text" id="vendorName" required>
                    </div>
                    <div class="form-group">
                        <label>설명</label>
                        <textarea id="vendorDescription"></textarea>
                    </div>
                    <div class="form-group">
                        <label>도시 *</label>
                        <input type="text" id="vendorCity" required>
                    </div>
                    <div class="form-group">
                        <label>구 *</label>
                        <input type="text" id="vendorDistrict" required>
                    </div>
                    <div class="form-group">
                        <label>최소 가격 (원)</label>
                        <input type="number" id="vendorMinPrice">
                    </div>
                    <div class="form-group">
                        <label>최대 가격 (원)</label>
                        <input type="number" id="vendorMaxPrice">
                    </div>
                    <div class="form-group">
                        <label>연락처</label>
                        <input type="text" id="vendorPhone">
                    </div>
                    <div class="form-group">
                        <label>연락 링크 (카톡/인스타/홈페이지)</label>
                        <input type="url" id="vendorLink">
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn-cancel" onclick="closeModal()">취소</button>
                        <button type="submit" class="btn-save">저장</button>
                    </div>
                </form>
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
            
            let vendors = [];
            let editingVendorId = null;
            
            // 페이지 로드 시 벤더 목록 가져오기
            async function loadVendors() {{
                try {{
                    const typeFilter = document.getElementById('filterType').value;
                    const locationFilter = document.getElementById('filterLocation').value;
                    const searchFilter = document.getElementById('filterSearch').value;
                    
                    let url = `${{baseUrl}}/secret_admin/api/admin/vendors?`;
                    if (typeFilter) url += `vendor_type=${{typeFilter}}&`;
                    if (locationFilter) url += `location=${{locationFilter}}&`;
                    if (searchFilter) url += `search=${{searchFilter}}&`;
                    
                    // 프론트엔드와 관리자 페이지 모두의 토큰 키 확인
                    const token = localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || '';
                    const response = await fetch(url, {{
                        headers: {{
                            'Authorization': `Bearer ${{token}}`
                        }}
                    }});
                    
                    if (!response.ok) {{
                        let errorMsg = '제휴 업체 목록을 불러올 수 없습니다.';
                        try {{
                            const errorData = await response.json();
                            if (response.status === 401 || response.status === 403) {{
                                errorMsg = '시스템 관리자 권한이 필요합니다.\\n현재 로그인한 사용자의 권한을 확인해주세요.';
                            }} else if (errorData?.detail) {{
                                errorMsg = errorData.detail;
                            }} else if (errorData?.message) {{
                                errorMsg = errorData.message;
                            }}
                        }} catch (e) {{
                            if (response.status === 404) {{
                                errorMsg = 'API 엔드포인트를 찾을 수 없습니다. (404)';
                            }} else if (response.status === 401 || response.status === 403) {{
                                errorMsg = '시스템 관리자 권한이 필요합니다.';
                            }}
                        }}
                        throw new Error(errorMsg);
                    }}
                    
                    const data = await response.json();
                    vendors = data.data?.vendors || data.vendors || [];
                    renderVendors();
                }} catch (error) {{
                    console.error('제휴 업체 목록 로드 실패:', error);
                    document.getElementById('vendorTableContainer').innerHTML = 
                        `<div style="color: #ef4444; padding: 20px; white-space: pre-line;">${{error.message}}</div>`;
                }}
            }}
            
            // 제휴 업체 목록 렌더링
            function renderVendors() {{
                const container = document.getElementById('vendorTableContainer');
                
                if (vendors.length === 0) {{
                    container.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;">제휴 업체가 없습니다.</div>';
                    return;
                }}
                
                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>타입</th>
                                <th>제휴 업체명</th>
                                <th>지역</th>
                                <th>가격 범위</th>
                                <th>평점</th>
                                <th>리뷰 수</th>
                                <th>작업</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                vendors.forEach(vendor => {{
                    const typeClass = vendor.vendor_type.toLowerCase();
                    html += `
                        <tr>
                            <td>${{vendor.id}}</td>
                            <td><span class="vendor-type-badge ${{vendor.vendor_type}}">${{getTypeLabel(vendor.vendor_type)}}</span></td>
                            <td>${{vendor.name}}</td>
                            <td>${{vendor.base_location_city}} ${{vendor.base_location_district}}</td>
                            <td>${{vendor.min_price ? vendor.min_price.toLocaleString() + '원' : '-'}} ~ ${{vendor.max_price ? vendor.max_price.toLocaleString() + '원' : '-'}}</td>
                            <td>${{vendor.rating_avg || 0}}</td>
                            <td>${{vendor.review_count || 0}}</td>
                            <td>
                                <button class="btn-edit" onclick="editVendor(${{vendor.id}})">수정</button>
                                <button class="btn-delete" onclick="deleteVendor(${{vendor.id}})">삭제</button>
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
            
            function getTypeLabel(type) {{
                const labels = {{
                    'IPHONE_SNAP': '아이폰 스냅',
                    'MC': '사회자',
                    'SINGER': '축가',
                    'STUDIO_PREWEDDING': '사전 웨딩 스튜디오',
                    'VENUE_OUTDOOR': '야외 결혼식 장소'
                }};
                return labels[type] || type;
            }}
            
            // 필터 변경 시 목록 새로고침
            document.getElementById('filterType').addEventListener('change', loadVendors);
            document.getElementById('filterLocation').addEventListener('input', loadVendors);
            document.getElementById('filterSearch').addEventListener('input', loadVendors);
            
            // 모달 열기/닫기
            function openCreateModal() {{
                editingVendorId = null;
                document.getElementById('modalTitle').textContent = '새 제휴 업체 추가';
                document.getElementById('vendorForm').reset();
                document.getElementById('vendorId').value = '';
                document.getElementById('vendorModal').style.display = 'block';
            }}
            
            function closeModal() {{
                document.getElementById('vendorModal').style.display = 'none';
                editingVendorId = null;
            }}
            
            // 제휴 업체 수정
            async function editVendor(id) {{
                const vendor = vendors.find(v => v.id === id);
                if (!vendor) return;
                
                editingVendorId = id;
                document.getElementById('modalTitle').textContent = '제휴 업체 수정';
                document.getElementById('vendorId').value = vendor.id;
                document.getElementById('vendorType').value = vendor.vendor_type;
                document.getElementById('vendorName').value = vendor.name;
                document.getElementById('vendorDescription').value = vendor.description || '';
                document.getElementById('vendorCity').value = vendor.base_location_city;
                document.getElementById('vendorDistrict').value = vendor.base_location_district;
                document.getElementById('vendorMinPrice').value = vendor.min_price || '';
                document.getElementById('vendorMaxPrice').value = vendor.max_price || '';
                document.getElementById('vendorPhone').value = vendor.contact_phone || '';
                document.getElementById('vendorLink').value = vendor.contact_link || '';
                document.getElementById('vendorModal').style.display = 'block';
            }}
            
            // 제휴 업체 삭제
            async function deleteVendor(id) {{
                if (!confirm('정말 삭제하시겠습니까?')) return;
                
                try {{
                    const response = await fetch(`${{baseUrl}}/secret_admin/api/admin/vendors/${{id}}`, {{
                        method: 'DELETE',
                        headers: {{
                            'Authorization': `Bearer ${{localStorage.getItem('access_token') || ''}}`
                        }}
                    }});
                    
                    if (response.ok) {{
                        alert('제휴 업체가 삭제되었습니다.');
                        loadVendors();
                    }} else {{
                        const data = await response.json();
                        const errorMsg = data?.data?.error || data?.error || data?.message || '삭제에 실패했습니다.';
                        console.error('제휴 업체 삭제 실패:', data);
                        alert(`삭제에 실패했습니다: ${{errorMsg}}`);
                    }}
                }} catch (error) {{
                    console.error('제휴 업체 삭제 중 오류:', error);
                    alert(`삭제 중 오류가 발생했습니다: ${{error.message || error}}`);
                }}
            }}
            
            // 폼 제출
            document.getElementById('vendorForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                
                const formData = {{
                    vendor_type: document.getElementById('vendorType').value,
                    name: document.getElementById('vendorName').value,
                    description: document.getElementById('vendorDescription').value,
                    base_location_city: document.getElementById('vendorCity').value,
                    base_location_district: document.getElementById('vendorDistrict').value,
                    min_price: document.getElementById('vendorMinPrice').value ? parseFloat(document.getElementById('vendorMinPrice').value) : null,
                    max_price: document.getElementById('vendorMaxPrice').value ? parseFloat(document.getElementById('vendorMaxPrice').value) : null,
                    contact_phone: document.getElementById('vendorPhone').value,
                    contact_link: document.getElementById('vendorLink').value,
                }};
                
                try {{
                    const url = editingVendorId 
                        ? `${{baseUrl}}/secret_admin/api/admin/vendors/${{editingVendorId}}`
                        : `${{baseUrl}}/secret_admin/api/admin/vendors`;
                    const method = editingVendorId ? 'PUT' : 'POST';
                    
                    const response = await fetch(url, {{
                        method: method,
                        headers: {{
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${{localStorage.getItem('wedding_access_token') || localStorage.getItem('access_token') || ''}}`
                        }},
                        body: JSON.stringify(formData)
                    }});
                    
                    let data;
                    try {{
                        data = await response.json();
                    }} catch (e) {{
                        // JSON 파싱 실패 시 (예: 권한 에러 등)
                        if (response.status === 403) {{
                            alert('시스템 관리자 권한이 필요합니다.\\n현재 로그인한 사용자의 권한을 확인해주세요.');
                            return;
                        }}
                        if (response.status === 401) {{
                            alert('로그인이 필요합니다.\\n다시 로그인해주세요.');
                            return;
                        }}
                        alert(`저장에 실패했습니다. (상태 코드: ${{response.status}})`);
                        return;
                    }}
                    
                    if (response.ok) {{
                        alert(editingVendorId ? '제휴 업체가 수정되었습니다.' : '제휴 업체가 생성되었습니다.');
                        closeModal();
                        loadVendors();
                    }} else {{
                        let errorMsg = '저장에 실패했습니다.';
                        if (response.status === 403) {{
                            errorMsg = '시스템 관리자 권한이 필요합니다.';
                        }} else if (response.status === 401) {{
                            errorMsg = '로그인이 필요합니다.';
                        }} else if (data?.data?.error) {{
                            errorMsg = data.data.error;
                        }} else if (data?.error) {{
                            errorMsg = data.error;
                        }} else if (data?.detail) {{
                            errorMsg = data.detail;
                        }} else if (data?.message) {{
                            errorMsg = data.message;
                        }}
                        console.error('제휴 업체 저장 실패:', {{
                            status: response.status,
                            statusText: response.statusText,
                            data: data
                        }});
                        alert(errorMsg);
                    }}
                }} catch (error) {{
                    console.error('제휴 업체 저장 중 오류:', error);
                    alert(`저장 중 오류가 발생했습니다: ${{error.message || error}}`);
                }}
            }});
            
            // 모달 외부 클릭 시 닫기
            window.onclick = function(event) {{
                const modal = document.getElementById('vendorModal');
                if (event.target == modal) {{
                    closeModal();
                }}
            }}
            
            // 페이지 로드
            loadVendors();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/api/admin/vendors")
async def get_vendors(
    vendor_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """제휴 업체 목록 조회 (시스템 관리자만)"""
    query = db.query(Vendor)
    
    if vendor_type:
        query = query.filter(Vendor.vendor_type == VendorType(vendor_type))
    
    if location:
        query = query.filter(
            or_(
                Vendor.base_location_city.ilike(f"%{location}%"),
                Vendor.base_location_district.ilike(f"%{location}%")
            )
        )
    
    if search:
        query = query.filter(Vendor.name.ilike(f"%{search}%"))
    
    vendors = query.order_by(Vendor.created_at.desc()).all()
    
    return {
        "message": "vendors_retrieved",
        "data": {
            "vendors": [
                {
                    "id": vendor.id,
                    "vendor_type": vendor.vendor_type.value if hasattr(vendor.vendor_type, 'value') else str(vendor.vendor_type),
                    "name": vendor.name,
                    "description": vendor.description,
                    "base_location_city": vendor.base_location_city,
                    "base_location_district": vendor.base_location_district,
                    "min_price": float(vendor.min_price) if vendor.min_price else None,
                    "max_price": float(vendor.max_price) if vendor.max_price else None,
                    "rating_avg": float(vendor.rating_avg) if vendor.rating_avg else 0.0,
                    "review_count": vendor.review_count,
                    "contact_phone": vendor.contact_phone,
                    "contact_link": vendor.contact_link,
                }
                for vendor in vendors
            ]
        }
    }


@router.post("/api/admin/vendors")
async def create_vendor(
    request: VendorCreateReq,
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """제휴 업체 생성 (시스템 관리자만)"""
    try:
        vendor_type_enum = VendorType(request.vendor_type)
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"message": "error", "data": {"error": f"잘못된 제휴 업체 타입입니다: {request.vendor_type}"}}
        )
    
    vendor = Vendor(
        vendor_type=vendor_type_enum,
        name=request.name,
        description=request.description,
        base_location_city=request.base_location_city,
        base_location_district=request.base_location_district,
        service_area=request.service_area,
        min_price=Decimal(str(request.min_price)) if request.min_price else None,
        max_price=Decimal(str(request.max_price)) if request.max_price else None,
        contact_link=request.contact_link,
        contact_phone=request.contact_phone,
        tags=request.tags,
        portfolio_images=request.portfolio_images,
        portfolio_videos=request.portfolio_videos,
        iphone_snap_detail=request.iphone_snap_detail,
        mc_detail=request.mc_detail,
        singer_detail=request.singer_detail,
        studio_detail=request.studio_detail,
        venue_detail=request.venue_detail,
    )
    
    try:
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        
        return {
            "message": "vendor_created",
            "data": {
                "id": vendor.id,
                "name": vendor.name,
            }
        }
    except ValueError as e:
        # VendorType enum 변환 실패 등
        db.rollback()
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={"message": "error", "data": {"error": f"잘못된 입력값입니다: {str(e)}"}}
        )
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={"message": "error", "data": {"error": f"제휴 업체 생성에 실패했습니다: {str(e)}"}}
        )


@router.put("/api/admin/vendors/{vendor_id}")
async def update_vendor(
    vendor_id: int,
    request: VendorUpdateReq,
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """제휴 업체 수정 (시스템 관리자만)"""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    
    if not vendor:
        return JSONResponse(
            status_code=404,
            content={"message": "error", "data": {"error": "제휴 업체를 찾을 수 없습니다."}}
        )
    
    try:
        if request.name is not None:
            vendor.name = request.name
        if request.description is not None:
            vendor.description = request.description
        if request.base_location_city is not None:
            vendor.base_location_city = request.base_location_city
        if request.base_location_district is not None:
            vendor.base_location_district = request.base_location_district
        if request.service_area is not None:
            vendor.service_area = request.service_area
        if request.min_price is not None:
            vendor.min_price = Decimal(str(request.min_price))
        if request.max_price is not None:
            vendor.max_price = Decimal(str(request.max_price))
        if request.contact_link is not None:
            vendor.contact_link = request.contact_link
        if request.contact_phone is not None:
            vendor.contact_phone = request.contact_phone
        if request.tags is not None:
            vendor.tags = request.tags
        if request.portfolio_images is not None:
            vendor.portfolio_images = request.portfolio_images
        if request.portfolio_videos is not None:
            vendor.portfolio_videos = request.portfolio_videos
        
        db.commit()
        db.refresh(vendor)
        
        return {
            "message": "vendor_updated",
            "data": {
                "id": vendor.id,
                "name": vendor.name,
            }
        }
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=400,
            content={"message": "error", "data": {"error": str(e)}}
        )


@router.delete("/api/admin/vendors/{vendor_id}")
async def delete_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_system_admin)
):
    """제휴 업체 삭제 (시스템 관리자만)"""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    
    if not vendor:
        return JSONResponse(
            status_code=404,
            content={"message": "error", "data": {"error": "제휴 업체를 찾을 수 없습니다."}}
        )
    
    try:
        db.delete(vendor)
        db.commit()
        
        return {
            "message": "vendor_deleted",
            "data": {"id": vendor_id}
        }
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=400,
            content={"message": "error", "data": {"error": str(e)}}
        )

