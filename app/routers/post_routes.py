from fastapi import APIRouter, UploadFile, File, Depends, Path, Query, Form, status
from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import get_current_user_id, get_current_user_id_optional
from app.core.database import get_db
from app.controllers import post_controller
from app.schemas import PostCreateReq, PostUpdateReq

router = APIRouter(tags=["posts"])


@router.get("/posts")
async def get_posts(
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100), 
    board_type: str = Query("couple"), 
    user_id: Optional[int] = Depends(get_current_user_id_optional),
    db: Session = Depends(get_db)
):
    """게시글 목록 조회 API (로그인 선택)"""
    data = post_controller.get_posts_controller(page, limit, user_id, board_type, db)
    return {"message": "get_posts_success", "data": data}


@router.get("/posts/{post_id}")
async def get_post(
    post_id: int, 
    user_id: Optional[int] = Depends(get_current_user_id_optional),
    db: Session = Depends(get_db)
):
    """게시글 상세 조회 API (로그인 선택)"""
    data = post_controller.get_post_controller(post_id, user_id, db)
    return {"message": "get_post_success", "data": data}


@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(req: PostCreateReq, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """게시글 작성 API"""
    data = await post_controller.create_post_controller(req, user_id, db)
    return {"message": "create_post_success", "data": data}


@router.patch("/posts/{post_id}")
async def update_post(post_id: int = Path(...), req: PostUpdateReq = None, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """게시글 수정 API"""
    data = post_controller.update_post_controller(post_id, req, user_id, db)
    return {"message": "update_post_success", "data": data}


@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """게시글 삭제 API"""
    data = post_controller.delete_post_controller(post_id, user_id, db)
    return {"message": "delete_post_success", "data": data}


@router.post("/posts/{post_id}/like")
async def toggle_like(post_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """좋아요 토글 API"""
    data = post_controller.toggle_like_controller(post_id, user_id, db)
    return {"message": "like_toggled", "data": data}


@router.patch("/posts/{post_id}/view")
async def inc_view(post_id: int, db: Session = Depends(get_db)):
    """조회수 증가 API"""
    data = post_controller.increment_view_controller(post_id, db)
    return {"message": "view_incremented", "data": data}


@router.post("/posts/upload")
async def upload_post_image(file: UploadFile = File(...)):
    """게시글 이미지 업로드 API (이미지 분류 포함)"""
    file_data = await file.read()
    filename = file.filename or "unknown"
    data = await post_controller.upload_post_image_controller(file.content_type or "", file_data, filename)
    return {"message": "upload_success", "data": data}


@router.post("/posts/upload-document")
async def upload_document_with_ocr(
    file: UploadFile = File(...),
    title: str = Form(..., description="문서 제목"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """문서 업로드 + OCR 처리 API (문서 보관함용)"""
    file_data = await file.read()
    filename = file.filename or "unknown"
    # title이 없으면 파일명 사용
    document_title = title or filename.rsplit('.', 1)[0] if '.' in filename else filename
    data = await post_controller.upload_document_with_ocr_controller(
        file.content_type or "", file_data, filename, document_title, user_id, db
    )
    return {"message": "document_uploaded", "data": data}
