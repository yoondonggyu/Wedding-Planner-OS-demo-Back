from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import Response, StreamingResponse
from app.schemas import BudgetItemCreateReq, BudgetItemUpdateReq, TotalBudgetSetReq
from app.controllers import budget_controller
from app.services import budget_service
import io

router = APIRouter(tags=["budget"])

# 예산 항목 관리
@router.post("/budget/items")
async def create_budget_item(request: BudgetItemCreateReq, user_id: int = Query(...)):
    """예산 항목 생성"""
    return budget_controller.create_budget_item(user_id, request)

@router.get("/budget/items")
async def get_budget_items(user_id: int = Query(...)):
    """예산 항목 조회"""
    return budget_controller.get_budget_items(user_id)

@router.put("/budget/items/{item_id}")
async def update_budget_item(
    item_id: int,
    request: BudgetItemUpdateReq,
    user_id: int = Query(...)
):
    """예산 항목 수정"""
    return budget_controller.update_budget_item(item_id, user_id, request)

@router.delete("/budget/items/{item_id}")
async def delete_budget_item(item_id: int, user_id: int = Query(...)):
    """예산 항목 삭제"""
    return budget_controller.delete_budget_item(item_id, user_id)

# 예산 요약
@router.get("/budget/summary")
async def get_budget_summary(user_id: int = Query(...)):
    """예산 요약 (카테고리별 합계)"""
    return budget_controller.get_budget_summary(user_id)

# 총 예산 설정
@router.post("/budget/total")
async def set_total_budget(request: TotalBudgetSetReq, user_id: int = Query(...)):
    """총 예산 설정"""
    return budget_controller.set_total_budget(user_id, request)

# Excel/CSV Export
@router.get("/budget/export/excel")
async def export_to_excel(user_id: int = Query(...)):
    """예산 데이터를 Excel 파일로 Export"""
    excel_data = budget_service.export_to_excel(user_id)
    return StreamingResponse(
        io.BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=budget.xlsx"}
    )

@router.get("/budget/export/csv")
async def export_to_csv(user_id: int = Query(...)):
    """예산 데이터를 CSV로 Export"""
    csv_data = budget_service.export_to_csv(user_id)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=budget.csv"}
    )

# Excel/CSV Import
@router.post("/budget/import/excel")
async def import_from_excel(
    file: UploadFile = File(...),
    user_id: int = Query(...)
):
    """Excel 파일에서 예산 데이터 Import"""
    file_data = await file.read()
    items = budget_service.import_from_excel(user_id, file_data)
    
    return {
        "message": "budget_imported",
        "data": {
            "items_imported": len(items),
            "items": [
                {
                    "id": item.id,
                    "item_name": item.item_name,
                    "category": item.category
                }
                for item in items
            ]
        }
    }

@router.post("/budget/import/csv")
async def import_from_csv(
    file: UploadFile = File(...),
    user_id: int = Query(...)
):
    """CSV 파일에서 예산 데이터 Import"""
    csv_data = (await file.read()).decode('utf-8-sig')
    items = budget_service.import_from_csv(user_id, csv_data)
    
    return {
        "message": "budget_imported",
        "data": {
            "items_imported": len(items),
            "items": [
                {
                    "id": item.id,
                    "item_name": item.item_name,
                    "category": item.category
                }
                for item in items
            ]
        }
    }

# OCR 처리
@router.post("/budget/process-receipt")
async def process_receipt_image(
    file: UploadFile = File(...),
    user_id: int = Query(...)
):
    """영수증/견적서 이미지 처리 (OCR + LLM 구조화)"""
    image_data = await file.read()
    return await budget_controller.process_receipt_image(user_id, image_data)



