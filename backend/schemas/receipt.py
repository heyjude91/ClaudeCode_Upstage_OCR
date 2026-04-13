from datetime import date as Date, datetime
from pydantic import BaseModel, Field
from backend.schemas.receipt_item import ReceiptItemCreate, ReceiptItemRead, ReceiptItemUpdate


class ReceiptBase(BaseModel):
    store_name: str = Field(..., max_length=255)
    date: Date
    total_amount: float = Field(..., ge=0)
    category: str | None = Field(None, max_length=100)


class ReceiptCreate(ReceiptBase):
    items: list[ReceiptItemCreate] = []


class ReceiptUpdate(BaseModel):
    store_name: str | None = Field(None, max_length=255)
    date: Date | None = None
    total_amount: float | None = Field(None, ge=0)
    category: str | None = Field(None, max_length=100)
    items: list[ReceiptItemUpdate] | None = None


class ReceiptRead(ReceiptBase):
    id: int
    image_path: str | None
    created_at: datetime
    items: list[ReceiptItemRead] = []

    model_config = {"from_attributes": True}


class PageMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class ReceiptListResponse(BaseModel):
    data: list[ReceiptRead]
    meta: PageMeta
