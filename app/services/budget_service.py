"""
예산서 서비스 - LLM 기반 테이블 구조화 + Excel 처리
"""
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from app.models.memory import BUDGET_ITEMS, BudgetItem, COUNTERS
from app.services.ocr_service import extract_text_from_image, extract_text_from_image_paddle
from app.services.model_client import chat_with_model
import pandas as pd
import io


async def structure_text_with_llm(extracted_text: str) -> List[Dict]:
    """
    LLM 기반 테이블 구조화 - OCR로 추출된 텍스트를 항목/가격/단위로 분리
    """
    prompt = f"""다음은 웨딩 견적서나 영수증에서 OCR로 추출한 텍스트입니다.
이 텍스트에서 예산 항목을 구조화해주세요.

[추출된 텍스트]
{extracted_text}

다음 형식의 JSON 배열로 응답해주세요:
[
  {{
    "item_name": "항목명",
    "category": "카테고리 (hall/dress/studio/snap/honeymoon/etc)",
    "estimated_budget": 예상 금액 (숫자만),
    "quantity": 수량 (있으면),
    "unit": "단위 (인원/시간 등, 있으면)",
    "notes": "비고 (있으면)"
  }}
]

카테고리 분류 가이드:
- hall: 웨딩홀 관련 (대관료, 식대, 보증인원 등)
- dress: 드레스 관련 (드레스, 턱시도, 액세서리)
- studio: 스튜디오 관련 (촬영, 앨범)
- snap: 스냅 관련 (스냅, 영상)
- honeymoon: 혼수/신혼여행
- etc: 기타

JSON 배열만 응답해주세요."""

    try:
        response = await chat_with_model(prompt, model="gemma3:4b")
        
        if response:
            # JSON 부분만 추출
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                structured = json.loads(json_match.group())
                if isinstance(structured, list):
                    return structured
    except Exception as e:
        print(f"⚠️ LLM 구조화 실패: {e}")
    
    return []


async def process_image_receipt(image_data: bytes) -> List[Dict]:
    """
    이미지 영수증/견적서 처리: OCR → LLM 구조화
    """
    # OCR로 텍스트 추출
    text = await extract_text_from_image(image_data)
    
    if not text:
        return []
    
    # LLM으로 구조화
    structured_items = await structure_text_with_llm(text)
    
    return structured_items


def get_category_summary(user_id: int) -> Dict:
    """카테고리별 합계 계산"""
    items = [item for item in BUDGET_ITEMS.values() if item.user_id == user_id]
    
    category_totals = {}
    total_estimated = 0.0
    total_actual = 0.0
    
    for item in items:
        category = item.category
        if category not in category_totals:
            category_totals[category] = {
                "estimated": 0.0,
                "actual": 0.0,
                "count": 0
            }
        
        category_totals[category]["estimated"] += item.estimated_budget
        category_totals[category]["actual"] += item.actual_expense
        category_totals[category]["count"] += 1
        total_estimated += item.estimated_budget
        total_actual += item.actual_expense
    
    return {
        "category_totals": category_totals,
        "total_estimated": total_estimated,
        "total_actual": total_actual,
        "remaining": total_estimated - total_actual
    }


def export_to_excel(user_id: int) -> bytes:
    """예산 데이터를 Excel 파일로 Export"""
    items = [item for item in BUDGET_ITEMS.values() if item.user_id == user_id]
    
    if not items:
        # 빈 데이터프레임 생성
        df = pd.DataFrame(columns=[
            "항목명", "카테고리", "예상 예산", "실제 지출", "수량", "단위", "담당자", "비고"
        ])
    else:
        data = []
        for item in items:
            data.append({
                "항목명": item.item_name,
                "카테고리": item.category,
                "예상 예산": item.estimated_budget,
                "실제 지출": item.actual_expense,
                "수량": item.quantity,
                "단위": item.unit or "",
                "담당자": item.payer,
                "비고": item.notes or ""
            })
        
        df = pd.DataFrame(data)
    
    # Excel 파일 생성
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='예산서')
        
        # 카테고리별 합계 시트 추가
        summary = get_category_summary(user_id)
        summary_data = []
        for category, totals in summary["category_totals"].items():
            summary_data.append({
                "카테고리": category,
                "예상 예산": totals["estimated"],
                "실제 지출": totals["actual"],
                "항목 수": totals["count"]
            })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, index=False, sheet_name='카테고리별 합계')
    
    output.seek(0)
    return output.read()


def export_to_csv(user_id: int) -> str:
    """예산 데이터를 CSV로 Export"""
    items = [item for item in BUDGET_ITEMS.values() if item.user_id == user_id]
    
    if not items:
        return "항목명,카테고리,예상 예산,실제 지출,수량,단위,담당자,비고\n"
    
    data = []
    for item in items:
        data.append({
            "항목명": item.item_name,
            "카테고리": item.category,
            "예상 예산": item.estimated_budget,
            "실제 지출": item.actual_expense,
            "수량": item.quantity,
            "단위": item.unit or "",
            "담당자": item.payer,
            "비고": item.notes or ""
        })
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False, encoding='utf-8-sig')


def import_from_excel(user_id: int, file_data: bytes) -> List[BudgetItem]:
    """Excel 파일에서 예산 데이터 Import"""
    try:
        df = pd.read_excel(io.BytesIO(file_data))
        
        items = []
        for _, row in df.iterrows():
            item_id = COUNTERS["budget"]
            COUNTERS["budget"] += 1
            
            item = BudgetItem(
                id=item_id,
                user_id=user_id,
                item_name=str(row.get("항목명", "")),
                category=str(row.get("카테고리", "etc")),
                estimated_budget=float(row.get("예상 예산", 0)),
                actual_expense=float(row.get("실제 지출", 0)),
                quantity=float(row.get("수량", 1)),
                unit=str(row.get("단위", "")) if pd.notna(row.get("단위")) else None,
                payer=str(row.get("담당자", "both")),
                notes=str(row.get("비고", "")) if pd.notna(row.get("비고")) else None,
                created_at=datetime.now().strftime("%Y-%m-%d"),
                updated_at=datetime.now().strftime("%Y-%m-%d")
            )
            
            BUDGET_ITEMS[item_id] = item
            items.append(item)
        
        return items
    except Exception as e:
        print(f"⚠️ Excel Import 실패: {e}")
        return []


def import_from_csv(user_id: int, csv_data: str) -> List[BudgetItem]:
    """CSV 파일에서 예산 데이터 Import"""
    try:
        df = pd.read_csv(io.StringIO(csv_data))
        
        items = []
        for _, row in df.iterrows():
            item_id = COUNTERS["budget"]
            COUNTERS["budget"] += 1
            
            item = BudgetItem(
                id=item_id,
                user_id=user_id,
                item_name=str(row.get("항목명", "")),
                category=str(row.get("카테고리", "etc")),
                estimated_budget=float(row.get("예상 예산", 0)),
                actual_expense=float(row.get("실제 지출", 0)),
                quantity=float(row.get("수량", 1)),
                unit=str(row.get("단위", "")) if pd.notna(row.get("단위")) else None,
                payer=str(row.get("담당자", "both")),
                notes=str(row.get("비고", "")) if pd.notna(row.get("비고")) else None,
                created_at=datetime.now().strftime("%Y-%m-%d"),
                updated_at=datetime.now().strftime("%Y-%m-%d")
            )
            
            BUDGET_ITEMS[item_id] = item
            items.append(item)
        
        return items
    except Exception as e:
        print(f"⚠️ CSV Import 실패: {e}")
        return []







