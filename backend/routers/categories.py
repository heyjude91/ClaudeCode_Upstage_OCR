from fastapi import APIRouter

router = APIRouter()

CATEGORIES = ["식료품", "외식", "쇼핑", "교통", "의료", "문화/여가", "기타"]


@router.get("", response_model=list[str], summary="카테고리 목록")
def list_categories():
    """사용 가능한 지출 카테고리 목록을 반환합니다."""
    return CATEGORIES
