"""
ocr_service.py — Upstage Information Extraction 기반 영수증 OCR 파이프라인

사용 API:
  POST https://api.upstage.ai/v1/information-extraction
  model: information-extract
  response_format: receipt JSON Schema

흐름:
  파일 바이트 → base64 인코딩 → Information Extraction API
  → JSON 파싱 → OCRResult 반환
  ※ 실패 시 1회 재시도 (2초 대기), 30초 타임아웃
"""
import base64
import json
import time

from openai import OpenAI

from backend.config import settings
from backend.schemas.ocr import OCRItem, OCRResult

# ── 상수 ──────────────────────────────────────────────────────────────────────
_API_BASE = "https://api.upstage.ai/v1/information-extraction"
_MODEL = "information-extract"
_TIMEOUT = 30       # 초
_MAX_RETRIES = 1    # 재시도 횟수 (최초 1회 + 재시도 1회 = 총 2회)

# ── JSON Schema (PRD FR-01-4 기준) ────────────────────────────────────────────
_RECEIPT_SCHEMA: dict = {
    "type": "json_schema",
    "json_schema": {
        "name": "receipt_schema",
        "schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": (
                        "영수증의 구매 날짜. YYYY-MM-DD 형식으로 반환. "
                        "날짜를 읽을 수 없으면 오늘 날짜를 사용."
                    ),
                },
                "store_name": {
                    "type": "string",
                    "description": "상호명 또는 가게 이름. 영수증 상단에 표기된 이름을 그대로 반환.",
                },
                "items": {
                    "type": "array",
                    "description": "구매 항목 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "상품명",
                            },
                            "quantity": {
                                "type": "number",
                                "description": "수량. 명시되지 않은 경우 1.",
                            },
                            "price": {
                                "type": "number",
                                "description": "단가 (원 단위 숫자, 쉼표·기호 제외)",
                            },
                        },
                        "required": ["name", "quantity", "price"],
                    },
                },
                "total": {
                    "type": "number",
                    "description": "합계 금액 (원 단위 숫자, 쉼표·기호 제외)",
                },
                "category": {
                    "type": "string",
                    "description": (
                        "지출 카테고리. 반드시 아래 7개 중 하나만 반환:\n"
                        "식료품 - 마트·편의점 식품류\n"
                        "외식 - 음식점·카페·패스트푸드\n"
                        "쇼핑 - 의류·잡화·가구·전자\n"
                        "교통 - 택시·버스·주유\n"
                        "의료 - 병원·약국\n"
                        "문화/여가 - 영화·공연·스포츠\n"
                        "기타 - 위 항목 해당 없음"
                    ),
                },
            },
            "required": ["date", "store_name", "items", "total", "category"],
        },
    },
}


# ── 공개 API ──────────────────────────────────────────────────────────────────
def extract_receipt(file_bytes: bytes) -> OCRResult:
    """
    영수증 이미지/PDF 바이트 → OCRResult

    Args:
        file_bytes: JPG·PNG·PDF 파일 바이트

    Returns:
        OCRResult: 구조화된 영수증 데이터

    Raises:
        RuntimeError: 최대 재시도 초과 시
    """
    last_exc: Exception | None = None

    for attempt in range(_MAX_RETRIES + 1):
        try:
            return _call_information_extraction(file_bytes)
        except Exception as exc:
            last_exc = exc
            if attempt < _MAX_RETRIES:
                time.sleep(2)

    raise RuntimeError(
        f"OCR 분석 실패 (총 {_MAX_RETRIES + 1}회 시도): {last_exc}"
    ) from last_exc


# ── 내부 함수 ─────────────────────────────────────────────────────────────────
def _build_client() -> OpenAI:
    return OpenAI(
        api_key=settings.upstage_api_key,
        base_url=_API_BASE,
    )


def _encode_bytes(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode()


def _call_information_extraction(file_bytes: bytes) -> OCRResult:
    client = _build_client()
    b64 = _encode_bytes(file_bytes)

    response = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:application/octet-stream;base64,{b64}"
                        },
                    }
                ],
            }
        ],
        response_format=_RECEIPT_SCHEMA,
        timeout=_TIMEOUT,
    )

    raw: str = response.choices[0].message.content
    data: dict = json.loads(raw)

    items = [
        OCRItem(
            name=item["name"],
            quantity=max(1, int(item.get("quantity") or 1)),
            price=float(item.get("price") or 0),
        )
        for item in data.get("items", [])
    ]

    return OCRResult(
        date=data["date"],
        store_name=data["store_name"],
        items=items,
        total=float(data.get("total") or 0),
        category=data.get("category", "기타"),
    )
