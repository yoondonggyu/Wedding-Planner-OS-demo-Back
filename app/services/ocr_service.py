"""
OCR 서비스 - PaddleOCR + 문서 파서
"""
from __future__ import annotations

import asyncio
import io
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd

# 선택적 import
try:
    from PIL import Image
except ImportError:  # pragma: no cover - 배포 환경에서 pillow는 requirements에 포함됨
    Image = None  # type: ignore

try:
    import pytesseract

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ pytesseract가 설치되지 않아 Tesseract OCR을 사용할 수 없습니다.")

try:
    from paddleocr import PaddleOCR

    PADDLE_IMPORT_ERROR = None
except Exception as import_error:  # pragma: no cover - paddle 설치 실패 시 로깅
    PaddleOCR = None  # type: ignore
    PADDLE_IMPORT_ERROR = import_error
    print(f"⚠️ PaddleOCR을 불러오지 못했습니다: {import_error}")

try:
    from pdfminer.high_level import extract_text as pdf_extract_text

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    pdf_extract_text = None
    print("ℹ️ pdfminer.six가 설치되어 있지 않아 PDF 텍스트 추출 기능이 제한됩니다.")

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    print("⚠️ openpyxl이 설치되지 않아 Excel 파일 읽기 기능이 제한됩니다.")

try:
    import xlrd
    XLRD_AVAILABLE = True
except ImportError:
    XLRD_AVAILABLE = False
    print("ℹ️ xlrd가 설치되지 않아 .xls 파일 읽기 기능이 제한됩니다.")

_paddle_instance: Optional["PaddleOCR"] = None
_paddle_init_error: Optional[Exception] = None

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".heic", ".tif", ".tiff", ".webp"}
EXCEL_EXTENSIONS = {".xls", ".xlsx"}
CSV_EXTENSIONS = {".csv"}
TEXT_EXTENSIONS = {".txt", ".md", ".rtf"}
PDF_EXTENSIONS = {".pdf"}


def _get_paddle_ocr() -> Optional["PaddleOCR"]:
    """PaddleOCR 인스턴스를 지연 초기화"""
    global _paddle_instance, _paddle_init_error

    if _paddle_instance is not None:
        return _paddle_instance
    if _paddle_init_error is not None:
        return None
    if PaddleOCR is None or PADDLE_IMPORT_ERROR is not None:
        _paddle_init_error = PADDLE_IMPORT_ERROR or RuntimeError("PaddleOCR 미설치")
        return None

    try:
        _paddle_instance = PaddleOCR(use_angle_cls=True, lang="korean")
        print("✅ PaddleOCR(korean) 초기화 완료")
    except Exception as exc:  # pragma: no cover - 초기화 실패 시 로깅
        _paddle_init_error = exc
        print(f"⚠️ PaddleOCR 초기화 실패: {exc}")
        return None

    return _paddle_instance


def _is_extension(target_exts: set[str], filename: str) -> bool:
    suffix = Path(filename or "").suffix.lower()
    return suffix in target_exts


def _is_image_file(filename: str, content_type: Optional[str]) -> bool:
    if content_type and content_type.lower().startswith("image/"):
        return True
    return _is_extension(IMAGE_EXTENSIONS, filename)


async def extract_text_from_image(image_data: bytes) -> Optional[str]:
    """
    이미지에서 텍스트 추출 (PaddleOCR 우선, 실패 시 Tesseract)
    """
    text = await extract_text_from_image_paddle(image_data)
    if text:
        return text

    if TESSERACT_AVAILABLE:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _extract_text_tesseract, image_data)

    return None


async def extract_text_from_image_paddle(image_data: bytes) -> Optional[str]:
    """PaddleOCR을 사용한 텍스트 추출"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _extract_text_paddle_sync, image_data)


def _extract_text_paddle_sync(image_data: bytes) -> Optional[str]:
    ocr = _get_paddle_ocr()
    if not ocr:
        return None
    if not Image:
        print("⚠️ Pillow가 없어 이미지를 로드할 수 없습니다.")
        return None

    try:
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        np_image = np.array(image)
        # PaddleOCR은 이미지 리스트를 기대하므로 단일 이미지도 리스트로 전달
        result = ocr.ocr(np_image, cls=True)
        lines: list[str] = []
        for page in result:
            for line in page:
                text = line[1][0].strip()
                if text:
                    lines.append(text)
        return "\n".join(lines).strip() if lines else None
    except Exception as exc:
        print(f"⚠️ PaddleOCR 추출 실패: {exc}")
        return None


def _extract_text_tesseract(image_data: bytes) -> Optional[str]:
    if not TESSERACT_AVAILABLE or not Image:
        return None

    try:
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image, lang="kor+eng")  # type: ignore[arg-type]
        return text.strip() if text else None
    except Exception as exc:
        print(f"⚠️ Tesseract OCR 실패: {exc}")
        return None


async def extract_text_from_document(
    file_data: bytes,
    filename: str,
    content_type: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    파일 종류에 맞춰 텍스트 추출
    Returns:
        (text, error_message)
    """
    filename = filename or "document"
    lowered_type = (content_type or "").lower()

    if _is_image_file(filename, lowered_type):
        text = await extract_text_from_image(file_data)
        return text, None if text else "이미지에서 텍스트를 추출하지 못했습니다."

    if _is_extension(EXCEL_EXTENSIONS, filename) or "spreadsheet" in lowered_type:
        try:
            text = await asyncio.to_thread(_extract_text_from_excel, file_data)
            return text, None if text else "엑셀에서 텍스트를 추출하지 못했습니다."
        except Exception as exc:
            print(f"⚠️ 엑셀 파싱 실패: {exc}")
            return None, "엑셀 파일을 읽는 중 오류가 발생했습니다."

    if _is_extension(CSV_EXTENSIONS, filename) or "csv" in lowered_type:
        try:
            text = await asyncio.to_thread(_extract_text_from_csv, file_data)
            return text, None if text else "CSV에서 텍스트를 추출하지 못했습니다."
        except Exception as exc:
            print(f"⚠️ CSV 파싱 실패: {exc}")
            return None, "CSV 파일을 읽는 중 오류가 발생했습니다."

    if _is_extension(TEXT_EXTENSIONS, filename) or lowered_type.startswith("text/"):
        try:
            decoded = file_data.decode("utf-8")
        except UnicodeDecodeError:
            decoded = file_data.decode("cp949", errors="ignore")
        decoded = decoded.strip()
        return (decoded or None), None if decoded else "텍스트 파일이 비어있습니다."

    if _is_extension(PDF_EXTENSIONS, filename) or "pdf" in lowered_type:
        if not PDF_AVAILABLE:
            return None, "PDF 추출 기능이 설정되지 않았습니다."
        try:
            text = await asyncio.to_thread(_extract_text_from_pdf, file_data)
            return text, None if text else "PDF에서 텍스트를 추출하지 못했습니다."
        except Exception as exc:
            print(f"⚠️ PDF 파싱 실패: {exc}")
            return None, "PDF 파일을 읽는 중 오류가 발생했습니다."

    # 나머지는 이미지로 간주
    text = await extract_text_from_image(file_data)
    return text, None if text else "문서에서 텍스트를 추출하지 못했습니다."


def _extract_text_from_excel(file_data: bytes) -> Optional[str]:
    if not OPENPYXL_AVAILABLE:
        raise ImportError("openpyxl이 설치되지 않았습니다. 'pip install openpyxl'로 설치해주세요.")
    
    try:
        # openpyxl을 명시적으로 엔진으로 지정
        sheets = pd.read_excel(
            io.BytesIO(file_data), 
            sheet_name=None, 
            header=None,
            engine='openpyxl'
        )
        lines: list[str] = []
        for sheet_name, df in sheets.items():
            sheet_text = _dataframe_to_text(df)
            if not sheet_text:
                continue
            if len(sheets) > 1:
                lines.append(f"[Sheet: {sheet_name}]")
            lines.append(sheet_text)
        text = "\n".join(lines).strip()
        return text or None
    except Exception as exc:
        # pandas의 에러를 더 명확하게 전달
        error_msg = str(exc)
        if "openpyxl" in error_msg.lower():
            raise ImportError("openpyxl이 설치되지 않았습니다. 'pip install openpyxl'로 설치해주세요.") from exc
        raise


def _extract_text_from_csv(file_data: bytes) -> Optional[str]:
    df = pd.read_csv(io.BytesIO(file_data), header=None)
    return _dataframe_to_text(df)


def _dataframe_to_text(df: pd.DataFrame) -> Optional[str]:
    lines: list[str] = []
    for _, row in df.iterrows():
        values = []
        for value in row.tolist():
            if pd.isna(value):
                continue
            cleaned = str(value).strip()
            if cleaned:
                values.append(cleaned)
        if values:
            lines.append(" | ".join(values))
    text = "\n".join(lines).strip()
    return text or None


def _extract_text_from_pdf(file_data: bytes) -> Optional[str]:
    if not PDF_AVAILABLE or pdf_extract_text is None:
        return None
    with io.BytesIO(file_data) as buffer:
        text = pdf_extract_text(buffer)
    return text.strip() if text else None
