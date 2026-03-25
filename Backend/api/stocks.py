from __future__ import annotations

from datetime import timedelta
from fastapi import APIRouter, HTTPException, Query
import numpy as np
import pandas as pd

from config import settings
from models.schemas import PriceHistoryResponse, StockMetricsResponse, StockSearchResult
from services import data_service, metrics_service
from utils.helpers import parse_date, parse_tickers, format_date, to_percent


router = APIRouter()


@router.get("/search", response_model=list[StockSearchResult])
def search_stocks(q: str = Query("", min_length=1), limit: int = Query(10, ge=1, le=50)):
    results = data_service.search_tickers(q, limit=limit)
    return results


@router.get("/{ticker}/metrics", response_model=StockMetricsResponse)
def get_stock_metrics(
    ticker: str,
    lookback_days: int = Query(252, ge=30, le=2000),
    portfolio_tickers: str | None = Query(None, description="Comma-separated tickers"),
):
    ticker = ticker.upper()
    try:
        price_df = data_service.get_price_history(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    price_series = price_df["Adj Close"] if "Adj Close" in price_df.columns else price_df["Close"]

    benchmark_prices = None
    try:
        benchmark_df = data_service.get_price_history(settings.market_benchmark)
        benchmark_prices = (
            benchmark_df["Adj Close"] if "Adj Close" in benchmark_df.columns else benchmark_df["Close"]
        )
    except Exception:
        benchmark_prices = None

    portfolio_returns = None
    if portfolio_tickers:
        tickers_list = parse_tickers(portfolio_tickers, settings.default_tickers)
    else:
        tickers_list = settings.default_tickers

    try:
        portfolio_prices = data_service.get_prices_frame(tickers_list)
        portfolio_returns_df = metrics_service.compute_daily_returns(portfolio_prices).tail(lookback_days)
        if not portfolio_returns_df.empty:
            weights = np.array([1.0 / len(portfolio_returns_df.columns)] * len(portfolio_returns_df.columns))
            portfolio_returns = metrics_service.compute_portfolio_returns(portfolio_returns_df, weights)
    except Exception:
        portfolio_returns = None

    metrics = metrics_service.compute_stock_metrics(
        price_series.tail(lookback_days),
        benchmark_prices=benchmark_prices.tail(lookback_days) if benchmark_prices is not None else None,
        portfolio_returns=portfolio_returns,
    )

    current_price = float(price_series.iloc[-1])
    prev_price = float(price_series.iloc[-2]) if len(price_series) >= 2 else current_price
    change = current_price - prev_price
    change_percent = (change / prev_price * 100.0) if prev_price else 0.0

    profile = data_service.get_ticker_profile(ticker)

    return StockMetricsResponse(
        ticker=ticker,
        name=profile.get("name", ticker),
        sector=profile.get("sector"),
        currentPrice=current_price,
        change=change,
        changePercent=change_percent,
        annualizedReturn=to_percent(metrics["annualized_return"]),
        volatility=to_percent(metrics["volatility"]),
        maxDrawdown=to_percent(metrics["max_drawdown"]),
        beta=metrics["beta"],
        correlationWithPortfolio=metrics["correlation"],
    )


@router.get("/{ticker}/price-history", response_model=PriceHistoryResponse)
def get_price_history(
    ticker: str,
    range: str = Query("1y", pattern="^(1y|3y|5y)$"),
    start: str | None = Query(None),
    end: str | None = Query(None),
):
    ticker = ticker.upper()
    if start:
        start_date = parse_date(start)
    else:
        years = int(range.replace("y", ""))
        start_date = pd.Timestamp.utcnow().normalize() - pd.DateOffset(years=years)

    end_date = parse_date(end)

    try:
        price_df = data_service.get_price_history(ticker, start=start_date, end=end_date)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    history = []
    for date, row in price_df.iterrows():
        price_value = row.get("Adj Close")
        if price_value is None or pd.isna(price_value):
            price_value = row.get("Close")
        if price_value is None or pd.isna(price_value):
            price_value = row.iloc[0]

        history.append(
            {
                "date": format_date(pd.to_datetime(date)),
                "price": float(price_value),
                "open": float(row.get("Open", 0.0)) if "Open" in row else None,
                "high": float(row.get("High", 0.0)) if "High" in row else None,
                "low": float(row.get("Low", 0.0)) if "Low" in row else None,
                "close": float(row.get("Close", 0.0)) if "Close" in row else None,
                "adjClose": float(row.get("Adj Close", 0.0)) if "Adj Close" in row else None,
                "volume": float(row.get("Volume", 0.0)) if "Volume" in row else None,
            }
        )

    return PriceHistoryResponse(ticker=ticker, history=history)
