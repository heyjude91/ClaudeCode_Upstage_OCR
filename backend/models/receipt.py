from datetime import datetime, date
from sqlalchemy import String, Date, DateTime, Float, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    items: Mapped[list["ReceiptItem"]] = relationship(
        "ReceiptItem",
        back_populates="receipt",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
