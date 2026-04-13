"""
지출 내역 필터링 기능 Playwright 테스트 스크립트
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:5177/receipts"
OUT = Path(__file__).parent

async def wait_table(page):
    """테이블 또는 빈 상태 메시지가 나타날 때까지 대기"""
    await page.wait_for_selector("table, .text-gray-400", timeout=8000)
    await asyncio.sleep(0.5)

async def test1_store_name(page):
    """테스트1: 가게명 필터링"""
    print("\n[TEST 1] 가게명 필터링 시작")
    await page.goto(BASE_URL, wait_until="networkidle")
    await wait_table(page)

    # 초기 전체 목록 스크린샷
    await page.screenshot(path=str(OUT/"test1/01_전체목록.png"), full_page=True)
    print("  01_전체목록.png 저장")

    # 가게명 입력: "스타벅스" 키워드
    store_input = page.locator('input[name="store_name"]')
    await store_input.fill("STARBUCKS")
    await asyncio.sleep(1.2)
    await page.screenshot(path=str(OUT/"test1/02_가게명_STARBUCKS.png"), full_page=True)
    print("  02_가게명_STARBUCKS.png 저장")

    # 가게명 변경: "이마트"
    await store_input.fill("이마트")
    await asyncio.sleep(1.2)
    await page.screenshot(path=str(OUT/"test1/03_가게명_이마트.png"), full_page=True)
    print("  03_가게명_이마트.png 저장")

    # 초기화
    await page.locator("button", has_text="필터 초기화").click()
    await asyncio.sleep(0.8)
    print("[TEST 1] 완료")

async def test2_category(page):
    """테스트2: 카테고리 필터링"""
    print("\n[TEST 2] 카테고리 필터링 시작")
    await page.goto(BASE_URL, wait_until="networkidle")
    await wait_table(page)

    category_select = page.locator('select[name="category"]')

    for cat in ["식료품", "외식", "교통", "문화/여가"]:
        await category_select.select_option(cat)
        await asyncio.sleep(1.2)
        safe = cat.replace("/", "_")
        path = OUT / f"test2/카테고리_{safe}.png"
        await page.screenshot(path=str(path), full_page=True)
        print(f"  카테고리_{safe}.png 저장")

    # 초기화
    await page.locator("button", has_text="필터 초기화").click()
    await asyncio.sleep(0.8)
    print("[TEST 2] 완료")

async def test3_date_range(page):
    """테스트3: 날짜 범위 필터링"""
    print("\n[TEST 3] 날짜 범위 필터링 시작")
    await page.goto(BASE_URL, wait_until="networkidle")
    await wait_table(page)

    # 케이스 A: 2022년 데이터 (스타벅스·택시)
    await page.locator('input[name="date_from"]').fill("2022-01-01")
    await page.locator('input[name="date_to"]').fill("2022-12-31")
    await asyncio.sleep(1.2)
    await page.screenshot(path=str(OUT/"test3/01_2022년_필터.png"), full_page=True)
    print("  01_2022년_필터.png 저장")

    # 케이스 B: 2026년 데이터 (GS25·CU·CGV)
    await page.locator('input[name="date_from"]').fill("2026-01-01")
    await page.locator('input[name="date_to"]').fill("2026-12-31")
    await asyncio.sleep(1.2)
    await page.screenshot(path=str(OUT/"test3/02_2026년_필터.png"), full_page=True)
    print("  02_2026년_필터.png 저장")

    # 케이스 C: 날짜 없는 범위 (결과 0건)
    await page.locator('input[name="date_from"]').fill("2020-01-01")
    await page.locator('input[name="date_to"]').fill("2020-12-31")
    await asyncio.sleep(1.2)
    await page.screenshot(path=str(OUT/"test3/03_2020년_결과없음.png"), full_page=True)
    print("  03_2020년_결과없음.png 저장")

    # 초기화
    await page.locator("button", has_text="필터 초기화").click()
    await asyncio.sleep(0.8)
    print("[TEST 3] 완료")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        await test1_store_name(page)
        await test2_category(page)
        await test3_date_range(page)

        await browser.close()
    print("\n모든 테스트 완료")

if __name__ == "__main__":
    asyncio.run(main())
