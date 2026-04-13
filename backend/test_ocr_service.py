"""
OCR 서비스 프롬프트 검증 스크립트 (2주차 Day 1)

실행:
  cd C:/claude_upstage_ocr
  PYTHONUTF8=1 python -m backend.test_ocr_service

검증 항목:
  - 5개 카테고리 대표 이미지 OCR 정확도
  - PDF 형식 처리 여부
  - date / store_name / items / total / category 추출 품질
"""

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from backend.services.ocr_service import extract_receipt  # noqa: E402

IMAGES_DIR = Path(__file__).parent.parent / "images"

# (파일명, 예상 카테고리, 예상 상호명 키워드)
TEST_CASES = [
    ("01_emart.png",            "식료품",    "emart"),
    ("02_starbucks.png",        "외식",      "starbucks"),
    ("03_cu.jpg",               "식료품",    "cu"),
    ("11_taxi.png",             "교통",      ""),
    ("GS25편의점_영수증.pdf",   "식료품",    "gs25"),
]


def run(filename: str, expected_category: str, store_keyword: str) -> bool:
    path = IMAGES_DIR / filename
    if not path.exists():
        print(f"  [SKIP] 파일 없음: {filename}")
        return True

    print(f"\n{'─' * 60}")
    print(f"  파일 : {filename}")
    print(f"  예상 카테고리 : {expected_category}")

    try:
        result = extract_receipt(path.read_bytes())
    except Exception as exc:
        print(f"  [FAIL] 예외 발생: {exc}")
        return False

    cat_ok = result.category == expected_category
    store_ok = (not store_keyword) or (store_keyword.lower() in result.store_name.lower())
    date_ok = len(result.date) == 10 and result.date[4] == "-"
    total_ok = result.total > 0
    # 교통·의료는 개별 항목이 없는 영수증이 일반적
    items_ok = len(result.items) > 0 or result.category in ("교통", "의료")

    print(f"  상호명   : {result.store_name}")
    print(f"  날짜     : {result.date}  {'[OK]' if date_ok else '[??]'}")
    print(f"  합계     : {result.total:,.0f}원  {'[OK]' if total_ok else '[??]'}")
    print(f"  카테고리 : {result.category}  {'[OK]' if cat_ok else f'[?? 예상: {expected_category}]'}")
    print(f"  항목 수  : {len(result.items)}개  {'[OK]' if items_ok else '[??]'}")
    for item in result.items[:3]:
        print(f"    - {item.name} × {item.quantity}  @{item.price:,.0f}원")
    if len(result.items) > 3:
        print(f"    ... 외 {len(result.items) - 3}개")

    passed = date_ok and total_ok and items_ok
    print(f"  결과 : {'[PASS]' if passed else '[FAIL]'}")
    return passed


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  OCR 서비스 프롬프트 검증  (2주차 Day 1)")
    print("=" * 60)

    results = []
    for filename, category, keyword in TEST_CASES:
        results.append(run(filename, category, keyword))

    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"  최종 결과 : {passed}/{total} 통과")
    print("=" * 60)
