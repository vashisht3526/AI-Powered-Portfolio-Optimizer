from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api import portfolio, backtest, stocks, news, ai, data
from services import data_service
from services import nifty50_pipeline

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(data.router, prefix="/api/data", tags=["data"])


@app.on_event("startup")
def update_local_data() -> None:
    # Update local CSV with any missing dates (if enabled + yfinance available).
    if settings.data_update_enabled:
        nifty50_pipeline.refresh_nifty50_data_and_metrics()


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": settings.app_name}
