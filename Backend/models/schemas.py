from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Holding(BaseModel):
    ticker: str
    name: str
    weight: float


class PortfolioMetrics(BaseModel):
    expectedReturn: float
    volatility: float
    sharpeRatio: float
    maxDrawdown: float


class PortfolioHoldingsResponse(BaseModel):
    holdings: List[Holding]


class PortfolioMetricsResponse(BaseModel):
    metrics: PortfolioMetrics


class OptimizeRequest(BaseModel):
    tickers: List[str] = Field(..., min_length=1)
    lookback_days: int = 180
    max_weight: float = 0.2
    risk_free_rate: float = 0.06


class OptimizeResponse(BaseModel):
    holdings: List[Holding]
    metrics: PortfolioMetrics


class BacktestRequest(BaseModel):
    tickers: Optional[List[str]] = None
    lookback_days: int = 252
    max_weight: float = 0.2
    rebalance_frequency: Literal["M", "Q"] = "M"
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class EquityPoint(BaseModel):
    date: str
    value: float


class EquityCurveResponse(BaseModel):
    equityCurve: List[EquityPoint]


class BacktestSummaryResponse(BaseModel):
    cagr: float
    sharpeRatio: float
    maxDrawdown: float
    winRate: float
    totalReturn: float


class StockSearchResult(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None


class StockMetricsResponse(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    currentPrice: float
    change: float
    changePercent: float
    annualizedReturn: float
    volatility: float
    maxDrawdown: float
    beta: float
    correlationWithPortfolio: float


class PriceHistoryPoint(BaseModel):
    date: str
    price: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    adjClose: Optional[float] = None
    volume: Optional[float] = None


class PriceHistoryResponse(BaseModel):
    ticker: str
    history: List[PriceHistoryPoint]


class NewsArticle(BaseModel):
    headline: str
    summary: str
    source: str
    date: str
    related_stocks: List[str] = []
    sentiment: Optional[Literal["positive", "neutral", "negative"]] = None
    category: Optional[str] = None


class NewsResponse(BaseModel):
    news: List[NewsArticle]


class AIChatRequest(BaseModel):
    question: Optional[str] = None
    message: Optional[str] = None
    portfolio: Optional[dict] = None
    news: Optional[list] = None
    tickers: Optional[List[str]] = None


class AIChatResponse(BaseModel):
    answer: str
    context: Optional[str] = None
