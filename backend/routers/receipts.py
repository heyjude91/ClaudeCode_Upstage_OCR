from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import ReceiptCreate, ReceiptListResponse, ReceiptRead, ReceiptUpdate

router = APIRouter()


@router.post(
    "/upload",
    response_model=ReceiptRead,
    status_code=status.HTTP_201_CREATED,
    summary="영수증 업로드 및 OCR 분석",
)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """영수증 이미지(JPG/PNG) 또는 PDF를 업로드하면 Upstage OCR이 항목을 추출하고 DB에 저장합니다."""
    # TODO (M2): ocr_service, receipt_service 구현 후 연결
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="M2에서 구현 예정")


@router.get(
    "",
    response_model=ReceiptListResponse,
    summary="영수증 목록 조회",
)
def list_receipts(
    date_from: str | None = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    date_to: str | None = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    category: str | None = Query(None),
    store_name: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """날짜·카테고리·상호명 필터와 페이지네이션을 지원하는 영수증 목록 조회"""
    # TODO (M2): receipt_service 구현 후 연결
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="M2에서 구현 예정")


@router.get(
    "/{receipt_id}",
    response_model=ReceiptRead,
    summary="영수증 상세 조회",
)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """특정 영수증의 상세 정보와 항목 목록을 반환합니다."""
    # TODO (M2): receipt_service 구현 후 연결
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="M2에서 구현 예정")


@router.put(
    "/{receipt_id}",
    response_model=ReceiptRead,
    summary="영수증 수정",
)
def update_receipt(
    receipt_id: int,
    body: ReceiptUpdate,
    db: Session = Depends(get_db),
):
    """AI 추출 결과를 수동으로 수정합니다. 항목 목록도 함께 수정 가능합니다."""
    # TODO (M2): receipt_service 구현 후 연결
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="M2에서 구현 예정")


@router.delete(
    "/{receipt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="영수증 삭제",
)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """영수증과 관련 항목(receipt_items)을 CASCADE 삭제합니다."""
    # TODO (M2): receipt_service 구현 후 연결
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="M2에서 구현 예정")
