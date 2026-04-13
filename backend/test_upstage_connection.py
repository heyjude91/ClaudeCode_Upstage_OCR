"""
Upstage API 연결 테스트 스크립트 (1주차 Day 4)

실행 방법:
  cd C:/claude_upstage_ocr
  source .venv/Scripts/activate
  python -m backend.test_upstage_connection

확인 항목:
  1. .env UPSTAGE_API_KEY 로딩
  2. Document Digitization API (OCR) — 영수증 이미지 → 원시 텍스트
  3. Information Extraction API — 영수증 이미지 → 구조화 JSON
"""

import json
import sys
from pathlib import Path

# ── 환경변수 로딩 ─────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from backend.config import settings  # noqa: E402  (env 로딩 후 import)

SAMPLE_IMAGE = Path(__file__).parent.parent / "images" / "02_starbucks.png"
API_BASE = "https://api.upstage.ai/v1"
PASS = "[PASS]"
FAIL = "[FAIL]"


# ── 유틸 ─────────────────────────────────────────────────────────────────────
def section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print("─" * 60)


# ── TEST 1: API Key 로딩 확인 ─────────────────────────────────────────────────
def test_api_key_loaded() -> bool:
    section("TEST 1 / API Key 로딩")
    key = settings.upstage_api_key
    masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
    if key and key.startswith("up_"):
        print(f"  API Key : {masked}")
        print(f"  결과    : {PASS}")
        return True
    print(f"  API Key : {masked!r}  ← 'up_' 로 시작해야 합니다")
    print(f"  결과    : {FAIL}")
    return False


# ── TEST 2: Document Digitization (OCR) ──────────────────────────────────────
def test_document_digitization() -> bool:
    import requests  # stdlib-compatible; already in venv

    section("TEST 2 / Document Digitization API (OCR)")
    if not SAMPLE_IMAGE.exists():
        print(f"  샘플 이미지 없음: {SAMPLE_IMAGE}")
        print(f"  결과 : {FAIL}")
        return False

    url = f"{API_BASE}/document-digitization"
    headers = {"Authorization": f"Bearer {settings.upstage_api_key}"}

    with SAMPLE_IMAGE.open("rb") as f:
        resp = requests.post(
            url,
            headers=headers,
            files={"document": f},
            data={"model": "ocr"},
            timeout=30,
        )

    print(f"  HTTP {resp.status_code}")

    if resp.status_code != 200:
        print(f"  오류 : {resp.text[:300]}")
        print(f"  결과 : {FAIL}")
        return False

    data = resp.json()
    output = data.get("output", [])
    preview = " ".join(b.get("text", "") for b in output[:5])
    print(f"  추출 블록 수 : {len(output)}")
    print(f"  텍스트 미리보기 : {preview[:120]}")
    print(f"  결과 : {PASS}")
    return True


# ── TEST 3: Information Extraction (구조화 JSON) ──────────────────────────────
def test_information_extraction() -> bool:
    import base64
    from openai import OpenAI

    section("TEST 3 / Information Extraction API (구조화 JSON)")
    if not SAMPLE_IMAGE.exists():
        print(f"  샘플 이미지 없음: {SAMPLE_IMAGE}")
        print(f"  결과 : {FAIL}")
        return False

    b64 = base64.b64encode(SAMPLE_IMAGE.read_bytes()).decode()

    client = OpenAI(
        api_key=settings.upstage_api_key,
        base_url=f"{API_BASE}/information-extraction",
    )

    resp = client.chat.completions.create(
        model="information-extract",
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
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "receipt_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "구매 날짜 (YYYY-MM-DD)",
                        },
                        "store_name": {
                            "type": "string",
                            "description": "상호명",
                        },
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "상품명"},
                                    "quantity": {"type": "number", "description": "수량"},
                                    "price": {"type": "number", "description": "단가"},
                                },
                                "required": ["name", "quantity", "price"],
                            },
                        },
                        "total": {
                            "type": "number",
                            "description": "합계 금액",
                        },
                        "category": {
                            "type": "string",
                            "description": "지출 카테고리 (식료품/외식/쇼핑/교통/의료/문화/기타 중 하나)",
                        },
                    },
                    "required": ["date", "store_name", "items", "total", "category"],
                },
            },
        },
        timeout=30,
    )

    raw = resp.choices[0].message.content
    parsed = json.loads(raw)
    print(f"  상호명  : {parsed.get('store_name')}")
    print(f"  날짜    : {parsed.get('date')}")
    print(f"  합계    : {parsed.get('total')}")
    print(f"  카테고리: {parsed.get('category')}")
    print(f"  항목 수 : {len(parsed.get('items', []))}")
    for item in parsed.get("items", [])[:3]:
        print(f"    - {item.get('name')} × {item.get('quantity')}  @{item.get('price')}")
    print(f"  결과 : {PASS}")
    return True


# ── 메인 ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Upstage API 연결 테스트  (1주차 Day 4)")
    print("=" * 60)

    results = [
        test_api_key_loaded(),
        test_document_digitization(),
        test_information_extraction(),
    ]

    passed = sum(results)
    total = len(results)
    section(f"최종 결과 : {passed}/{total} 통과")

    if passed < total:
        sys.exit(1)
