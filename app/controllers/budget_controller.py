"""
예산서 컨트롤러
"""
from typing import Dict, List
from datetime import datetime
from app.models.memory import BUDGET_ITEMS, BudgetItem, COUNTERS, USER_TOTAL_BUDGETS
from app.schemas import BudgetItemCreateReq, BudgetItemUpdateReq, TotalBudgetSetReq
from app.services import budget_service, ocr_service


def create_budget_item(user_id: int, request: BudgetItemCreateReq) -> Dict:
    """예산 항목 생성"""
    item_id = COUNTERS["budget"]
    COUNTERS["budget"] += 1
    
    now = datetime.now().strftime("%Y-%m-%d")
    
    item = BudgetItem(
        id=item_id,
        user_id=user_id,
        item_name=request.item_name,
        category=request.category,
        estimated_budget=request.estimated_budget,
        actual_expense=request.actual_expense,
        unit=request.unit,
        quantity=request.quantity,
        notes=request.notes,
        payer=request.payer,
        payment_schedule=request.payment_schedule,
        created_at=now,
        updated_at=now
    )
    
    BUDGET_ITEMS[item_id] = item
    
    return {
        "message": "budget_item_created",
        "data": {
            "id": item.id,
            "item_name": item.item_name
        }
    }


def update_budget_item(item_id: int, user_id: int, request: BudgetItemUpdateReq) -> Dict:
    """예산 항목 수정"""
    item = BUDGET_ITEMS.get(item_id)
    if not item or item.user_id != user_id:
        return {"message": "error", "data": {"error": "예산 항목을 찾을 수 없습니다."}}
    
    if request.item_name is not None:
        item.item_name = request.item_name
    if request.category is not None:
        item.category = request.category
    if request.estimated_budget is not None:
        item.estimated_budget = request.estimated_budget
    if request.actual_expense is not None:
        item.actual_expense = request.actual_expense
    if request.unit is not None:
        item.unit = request.unit
    if request.quantity is not None:
        item.quantity = request.quantity
    if request.notes is not None:
        item.notes = request.notes
    if request.payer is not None:
        item.payer = request.payer
    if request.payment_schedule is not None:
        item.payment_schedule = request.payment_schedule
    
    item.updated_at = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "message": "budget_item_updated",
        "data": {
            "id": item.id,
            "item_name": item.item_name
        }
    }


def delete_budget_item(item_id: int, user_id: int) -> Dict:
    """예산 항목 삭제"""
    item = BUDGET_ITEMS.get(item_id)
    if not item or item.user_id != user_id:
        return {"message": "error", "data": {"error": "예산 항목을 찾을 수 없습니다."}}
    
    del BUDGET_ITEMS[item_id]
    return {"message": "budget_item_deleted", "data": {"id": item_id}}


def get_budget_items(user_id: int) -> Dict:
    """예산 항목 조회"""
    items = [item for item in BUDGET_ITEMS.values() if item.user_id == user_id]
    
    return {
        "message": "budget_items_retrieved",
        "data": {
            "items": [
                {
                    "id": item.id,
                    "item_name": item.item_name,
                    "category": item.category,
                    "estimated_budget": item.estimated_budget,
                    "actual_expense": item.actual_expense,
                    "unit": item.unit,
                    "quantity": item.quantity,
                    "notes": item.notes,
                    "payer": item.payer,
                    "payment_schedule": item.payment_schedule,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at
                }
                for item in items
            ]
        }
    }


def get_budget_summary(user_id: int) -> Dict:
    """예산 요약 (카테고리별 합계)"""
    summary = budget_service.get_category_summary(user_id)
    total_budget = USER_TOTAL_BUDGETS.get(user_id, 0.0)
    
    return {
        "message": "budget_summary_retrieved",
        "data": {
            **summary,
            "total_budget": total_budget,
            "budget_usage_percent": (summary["total_actual"] / total_budget * 100) if total_budget > 0 else 0
        }
    }


def set_total_budget(user_id: int, request: TotalBudgetSetReq) -> Dict:
    """총 예산 설정"""
    USER_TOTAL_BUDGETS[user_id] = request.total_budget
    return {
        "message": "total_budget_set",
        "data": {"total_budget": request.total_budget}
    }


async def process_receipt_image(user_id: int, image_data: bytes) -> Dict:
    """영수증/견적서 이미지 처리 (OCR + LLM 구조화)"""
    structured_items = await budget_service.process_image_receipt(image_data)
    
    created_items = []
    for item_data in structured_items:
        item_id = COUNTERS["budget"]
        COUNTERS["budget"] += 1
        
        now = datetime.now().strftime("%Y-%m-%d")
        
        item = BudgetItem(
            id=item_id,
            user_id=user_id,
            item_name=item_data.get("item_name", "항목"),
            category=item_data.get("category", "etc"),
            estimated_budget=float(item_data.get("estimated_budget", 0)),
            actual_expense=float(item_data.get("estimated_budget", 0)),  # OCR에서 추출한 금액은 실제 지출로 간주
            quantity=float(item_data.get("quantity", 1)),
            unit=item_data.get("unit"),
            notes=item_data.get("notes"),
            created_at=now,
            updated_at=now,
            metadata={"source": "ocr", "original_text": ""}  # 원본 텍스트는 메타데이터에 저장 가능
        )
        
        BUDGET_ITEMS[item_id] = item
        created_items.append(item)
    
    return {
        "message": "receipt_processed",
        "data": {
            "items_created": len(created_items),
            "items": [
                {
                    "id": item.id,
                    "item_name": item.item_name,
                    "category": item.category,
                    "estimated_budget": item.estimated_budget
                }
                for item in created_items
            ]
        }
    }



