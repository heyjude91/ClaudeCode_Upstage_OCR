"""
routers/receipts.py — 영수증 API 엔드포인트
"""
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.schemas import ReceiptListResponse, ReceiptRead, ReceiptUpdate
from backend.services import ocr_service, receipt_service

router = APIRouter()


# ── POST /upload ───────────────────────────────────────────────────────────────
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
    """
    영수증 이미지(JPG·PNG) 또는 PDF를 업로드합니다.

    - MIME 타입 검증: image/jpeg · image/png · application/pdf 만 허용
    - 크기 제한: 최대 10 MB
    - Upstage Information Extraction으로 날짜·상호명·항목·합계·카테고리 추출
    - 추출 결과를 DB에 저장하고 ReceiptRead 반환
    """
    # 1. MIME 타입 검증
    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"지원하지 않는 파일 형식: {file.content_type!r}. "
                "JPG · PNG · PDF 만 허용됩니다."
            ),
        )

    # 2. 파일 읽기 + 크기 검증
    file_bytes = await file.read()
    if len(file_bytes) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"파일 크기 초과: {settings.max_file_size_mb} MB 이하만 허용됩니다.",
        )

    # 3. 업로드 파일 저장 (고유 파일명)
    ext = _safe_ext(file.filename, file.content_type)
    saved_name = f"{uuid.uuid4().hex}{ext}"
    saved_path = settings.upload_path / saved_name
    saved_path.write_bytes(file_bytes)
    image_path = f"/uploads/{saved_name}"

    # 4. OCR 분석
    try:
        ocr_result = ocr_service.extract_receipt(file_bytes)
    except RuntimeError as exc:
        saved_path.unlink(missing_ok=True)  # 업로드 파일 정리
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    # 5. DB 저장
    receipt = receipt_service.create_receipt_from_ocr(db, ocr_result, image_path)
    return receipt


# ── GET / (목록) ───────────────────────────────────────────────────────────────
@router.get(
    "",
    response_model=ReceiptListResponse,
    summary="영수증 목록 조회",
)
def list_receipts(
    date_from: str | None = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    date_to: str | None = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    category: str | None = Query(None, description="카테고리 필터"),
    store_name: str | None = Query(None, description="상호명 부분 일치 검색"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """날짜·카테고리·상호명 필터와 페이지네이션을 지원하는 영수증 목록 조회"""
    # TODO (Day 3): receipt_service 구현 후 연결
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Day 3에서 구현 예정")


# ── GET /{id} (상세) ───────────────────────────────────────────────────────────
@router.get(
    "/{receipt_id}",
    response_model=ReceiptRead,
    summary="영수증 상세 조회",
)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """특정 영수증의 상세 정보와 항목 목록을 반환합니다."""
    # TODO (Day 3): receipt_service 구현 후 연결
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Day 3에서 구현 예정")


# ── PUT /{id} (수정) ───────────────────────────────────────────────────────────
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
    # TODO (Day 4): receipt_service 구현 후 연결
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Day 4에서 구현 예정")


# ── DELETE /{id} (삭제) ────────────────────────────────────────────────────────
@router.delete(
    "/{receipt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="영수증 삭제",
)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """영수증과 관련 항목(receipt_items)을 CASCADE 삭제합니다."""
    # TODO (Day 4): receipt_service 구현 후 연결
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Day 4에서 구현 예정")


# ── 내부 유틸 ─────────────────────────────────────────────────────────────────
def _safe_ext(filename: str | None, content_type: str) -> str:
    """원본 파일명에서 확장자를 추출. 없으면 content_type 기반으로 결정."""
    if filename:
        ext = Path(filename).suffix.lower()
        if ext in {".jpg", ".jpeg", ".png", ".pdf"}:
            return ext
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "application/pdf": ".pdf",
    }
    return mapping.get(content_type, ".bin")
