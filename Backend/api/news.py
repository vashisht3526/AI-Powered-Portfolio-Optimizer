from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from models.schemas import NewsResponse
from services import news_service


router = APIRouter()


@router.get("/market", response_model=NewsResponse)
def get_market_news(limit: int = Query(20, ge=1, le=50)):
    try:
        news = news_service.get_market_news(limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return NewsResponse(news=news)


@router.get("/stock/{ticker}", response_model=NewsResponse)
def get_stock_news(ticker: str, limit: int = Query(20, ge=1, le=50)):
    try:
        news = news_service.get_stock_news(ticker, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return NewsResponse(news=news)
