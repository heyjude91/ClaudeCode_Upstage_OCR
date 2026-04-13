from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import Base, engine
from backend.models import Receipt, ReceiptItem  # noqa: F401 — Base에 등록
from backend.routers import receipts, stats, categories

# 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI 영수증 지출 관리 시스템",
    description="Upstage Vision LLM 기반 영수증 OCR 및 지출 관리 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드 이미지 정적 서빙
app.mount("/uploads", StaticFiles(directory=str(settings.upload_path)), name="uploads")

# 라우터 등록
app.include_router(receipts.router, prefix="/api/receipts", tags=["receipts"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "version": "1.0.0"}
