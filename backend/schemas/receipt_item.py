from pydantic import BaseModel, Field


class ReceiptItemBase(BaseModel):
    item_name: str = Field(..., max_length=255)
    quantity: int = Field(1, ge=1)
    unit_price: float = Field(..., ge=0)
    total_price: float = Field(..., ge=0)


class ReceiptItemCreate(ReceiptItemBase):
    pass


class ReceiptItemUpdate(BaseModel):
    item_name: str | None = Field(None, max_length=255)
    quantity: int | None = Field(None, ge=1)
    unit_price: float | None = Field(None, ge=0)
    total_price: float | None = Field(None, ge=0)


class ReceiptItemRead(ReceiptItemBase):
    id: int
    receipt_id: int

    model_config = {"from_attributes": True}
