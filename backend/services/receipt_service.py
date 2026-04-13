"""
receipt_service.py — 영수증 CRUD 비즈니스 로직
"""
import json
from datetime import date as Date, datetime
from math import ceil

from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.models.receipt import Receipt
from backend.models.receipt_item import ReceiptItem
from backend.schemas.ocr import OCRResult
from backend.schemas.receipt import PageMeta, ReceiptListResponse


# ── 저장 ──────────────────────────────────────────────────────────────────────
def create_receipt_from_ocr(
    db: Session,
    ocr: OCRResult,
    image_path: str | None = None,
) -> Receipt:
    """OCR 결과를 receipts + receipt_items 테이블에 저장하고 Receipt 반환."""
    parsed_date = _parse_date(ocr.date)

    receipt = Receipt(
        store_name=ocr.store_name,
        date=parsed_date,
        total_amount=ocr.total,
        category=ocr.category,
        image_path=image_path,
        raw_json=json.dumps(ocr.model_dump(), ensure_ascii=False),
    )
    db.add(receipt)
    db.flush()  # receipt.id 확보

    for item in ocr.items:
        db.add(
            ReceiptItem(
                receipt_id=receipt.id,
                item_name=item.name,
                quantity=item.quantity,
                unit_price=item.price,
                total_price=round(item.price * item.quantity, 2),
            )
        )

    db.commit()
    db.refresh(receipt)
    return receipt


# ── 목록 조회 ─────────────────────────────────────────────────────────────────
def list_receipts(
    db: Session,
    date_from: str | None,
    date_to: str | None,
    category: str | None,
    store_name: str | None,
    page: int,
    limit: int,
) -> ReceiptListResponse:
    """필터·페이지네이션 적용 영수증 목록 반환."""
    q = db.query(Receipt)

    if date_from:
        q = q.filter(Receipt.date >= _parse_date(date_from))
    if date_to:
        q = q.filter(Receipt.date <= _parse_date(date_to))
    if category:
        q = q.filter(Receipt.category == category)
    if store_name:
        q = q.filter(Receipt.store_name.ilike(f"%{store_name}%"))

    total = q.count()
    items = (
        q.order_by(desc(Receipt.created_at))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return ReceiptListResponse(
        data=items,
        meta=PageMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=max(1, ceil(total / limit)),
        ),
    )


# ── 상세 조회 ─────────────────────────────────────────────────────────────────
def get_receipt(db: Session, receipt_id: int) -> Receipt:
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise ValueError(f"영수증을 찾을 수 없습니다: id={receipt_id}")
    return receipt


# ── 내부 유틸 ─────────────────────────────────────────────────────────────────
def _parse_date(raw: str) -> Date:
    """YYYY-MM-DD 외에 자주 등장하는 형식도 허용. 파싱 실패 시 오늘 날짜."""
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%y-%m-%d", "%y/%m/%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return Date.today()
