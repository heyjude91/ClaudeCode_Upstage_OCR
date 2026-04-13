from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import StatsSummary

router = APIRouter()


@router.get(
    "/summary",
    response_model=StatsSummary,
    summary="지출 통계 조회",
)
def get_stats_summary(
    date_from: str | None = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    date_to: str | None = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """기간별 월별·카테고리별·일별 지출 통계 데이터를 반환합니다."""
    # TODO (M2): stats_service 구현 후 연결
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="M2에서 구현 예정")
