from pydantic import BaseModel


class MonthlyStat(BaseModel):
    year: int
    month: int
    total: float


class CategoryStat(BaseModel):
    category: str
    total: float
    count: int


class DailyStat(BaseModel):
    date: str   # "YYYY-MM-DD"
    total: float


class StatsSummary(BaseModel):
    monthly: list[MonthlyStat]
    by_category: list[CategoryStat]
    daily: list[DailyStat]
    grand_total: float
    receipt_count: int
