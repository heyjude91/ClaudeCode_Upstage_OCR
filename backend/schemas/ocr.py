from pydantic import BaseModel, Field


class OCRItem(BaseModel):
    """OCR이 추출한 개별 구매 항목"""
    name: str = Field(..., description="상품명")
    quantity: int = Field(1, ge=1, description="수량")
    price: float = Field(..., ge=0, description="단가")


class OCRResult(BaseModel):
    """Upstage Vision LLM이 반환하는 영수증 OCR 결과 JSON 스펙 (PRD FR-01-4)"""
    date: str = Field(..., description="구매 날짜 (YYYY-MM-DD)")
    store_name: str = Field(..., description="상호명")
    items: list[OCRItem] = Field(default_factory=list, description="구매 항목 목록")
    total: float = Field(..., ge=0, description="합계 금액")
    category: str = Field("기타", description="지출 카테고리")
