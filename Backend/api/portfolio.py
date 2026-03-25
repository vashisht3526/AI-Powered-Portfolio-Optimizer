from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
import numpy as np

from config import settings
from models.schemas import (
    Holding,
    OptimizeRequest,
    OptimizeResponse,
    PortfolioHoldingsResponse,
    PortfolioMetricsResponse,
)
from services import data_service, metrics_service, optimization_service, backtest_service, nifty50_pipeline
from utils.helpers import parse_tickers, parse_date, to_percent, format_date


router = APIRouter()


def _map_to_ns_ticker(ticker: str) -> str:
    if ticker.upper().endswith(".NS"):
        return ticker.upper()
    candidate = f"{ticker.upper()}.NS"
    if candidate in settings.default_tickers:
        return candidate
    return ticker.upper()


def _build_holdings(tickers: list[str], weights: np.ndarray) -> list[Holding]:
    holdings = []
    for ticker, weight in zip(tickers, weights):
        profile = data_service.get_ticker_profile(ticker)
        holdings.append(
            Holding(
                ticker=ticker,
                name=profile.get("name", ticker),
                weight=float(weight) * 100.0,
            )
        )
    return holdings


@router.get("/metrics", response_model=PortfolioMetricsResponse)
def get_portfolio_metrics(
    tickers: str | None = Query(None, description="Comma-separated tickers"),
    lookback_days: int = Query(settings.lookback_days, ge=30, le=1000),
    max_weight: float = Query(settings.max_weight, ge=0.01, le=1.0),
    risk_free_rate: float = Query(settings.risk_free_rate, ge=0.0, le=1.0),
    mode: str = Query("system", pattern="^(system|user)$"),
    rebalance_date: str | None = Query(None, description="YYYY-MM-DD"),
):
    tickers_list = parse_tickers(tickers, settings.default_tickers)
    if mode == "system":
        cached = nifty50_pipeline.load_precomputed_metrics()
        cached_weights = nifty50_pipeline.load_precomputed_weights()
        if cached and not cached_weights.empty and "Weight" in cached_weights.columns:
            cached_tickers = {str(t).upper().replace(".NS", "") for t in cached_weights.index}
            requested = {t.upper().replace(".NS", "") for t in tickers_list}
            if not tickers or requested == cached_tickers:
                response = PortfolioMetricsResponse(
                    metrics={
                        "expectedReturn": to_percent(cached.get("expected_return", 0.0)),
                        "volatility": to_percent(cached.get("volatility", 0.0)),
                        "sharpeRatio": cached.get("sharpe", 0.0),
                        "maxDrawdown": to_percent(cached.get("max_drawdown", 0.0)),
                    }
                )
                return response
    end_date = parse_date(rebalance_date)

    try:
        prices = data_service.get_prices_frame(tickers_list, end=end_date)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    returns = metrics_service.compute_daily_returns(prices).tail(lookback_days)
    data_service.persist_returns(f"portfolio_{'_'.join(tickers_list)}", returns)
    if returns.empty:
        raise HTTPException(status_code=400, detail="Not enough return history")

    if mode == "system":
        optimization = optimization_service.optimize_portfolio(
            returns,
            max_weight=max_weight,
            risk_free_rate=risk_free_rate,
            lookback_days=lookback_days,
        )
        weights = optimization.get("weights", np.array([]))
        if len(weights) == 0:
            weights = np.array([1.0 / len(returns.columns)] * len(returns.columns))
    else:
        weights = np.array([1.0 / len(returns.columns)] * len(returns.columns))

    metrics = metrics_service.compute_portfolio_metrics(returns, weights, risk_free_rate)

    response = PortfolioMetricsResponse(
        metrics={
            "expectedReturn": to_percent(metrics["expected_return"]),
            "volatility": to_percent(metrics["volatility"]),
            "sharpeRatio": metrics["sharpe"],
            "maxDrawdown": to_percent(metrics["max_drawdown"]),
        }
    )
    return response


@router.get("/holdings", response_model=PortfolioHoldingsResponse)
def get_portfolio_holdings(
    tickers: str | None = Query(None, description="Comma-separated tickers"),
    lookback_days: int = Query(settings.lookback_days, ge=30, le=1000),
    max_weight: float = Query(settings.max_weight, ge=0.01, le=1.0),
    risk_free_rate: float = Query(settings.risk_free_rate, ge=0.0, le=1.0),
    mode: str = Query("system", pattern="^(system|user)$"),
):
    if mode == "system":
        weights_df = nifty50_pipeline.load_precomputed_weights()
        if not weights_df.empty and "Weight" in weights_df.columns:
            weights_df = weights_df[weights_df["Weight"] > 0].sort_values(
                by="Weight",
                ascending=False,
            )
            holdings: list[Holding] = []
            for ticker, row in weights_df.iterrows():
                mapped = _map_to_ns_ticker(str(ticker))
                profile = data_service.get_ticker_profile(mapped)
                holdings.append(
                    Holding(
                        ticker=mapped,
                        name=profile.get("name", mapped),
                        weight=float(row["Weight"]) * 100.0,
                    )
                )
            return PortfolioHoldingsResponse(holdings=holdings)

    tickers_list = parse_tickers(tickers, settings.default_tickers)

    try:
        prices = data_service.get_prices_frame(tickers_list)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    returns = metrics_service.compute_daily_returns(prices).tail(lookback_days)
    data_service.persist_returns(f"portfolio_{'_'.join(tickers_list)}", returns)
    if returns.empty:
        raise HTTPException(status_code=400, detail="Not enough return history")

    if mode == "system":
        optimization = optimization_service.optimize_portfolio(
            returns,
            max_weight=max_weight,
            risk_free_rate=risk_free_rate,
            lookback_days=lookback_days,
        )
        weights = optimization.get("weights", np.array([]))
        tickers_used = optimization.get("tickers", list(returns.columns))
        if len(weights) == 0:
            weights = np.array([1.0 / len(tickers_used)] * len(tickers_used))
    else:
        tickers_used = list(returns.columns)
        weights = np.array([1.0 / len(tickers_used)] * len(tickers_used))

    holdings = _build_holdings(tickers_used, weights)
    return PortfolioHoldingsResponse(holdings=holdings)


@router.post("/optimize", response_model=OptimizeResponse)
def optimize_portfolio(request: OptimizeRequest):
    tickers = [ticker.upper() for ticker in request.tickers]

    try:
        prices = data_service.get_prices_frame(tickers)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    returns = metrics_service.compute_daily_returns(prices).tail(request.lookback_days)
    data_service.persist_returns(f"portfolio_{'_'.join(tickers)}", returns)
    if returns.empty:
        raise HTTPException(status_code=400, detail="Not enough return history")

    optimization = optimization_service.optimize_portfolio(
        returns,
        max_weight=request.max_weight,
        risk_free_rate=request.risk_free_rate,
        lookback_days=request.lookback_days,
    )

    weights = optimization.get("weights", np.array([]))
    if len(weights) == 0:
        weights = np.array([1.0 / len(returns.columns)] * len(returns.columns))
        tickers_used = list(returns.columns)
    else:
        tickers_used = optimization.get("tickers", list(returns.columns))

    metrics = metrics_service.compute_portfolio_metrics(returns, weights, request.risk_free_rate)
    holdings = _build_holdings(tickers_used, weights)

    return OptimizeResponse(
        holdings=holdings,
        metrics={
            "expectedReturn": to_percent(metrics["expected_return"]),
            "volatility": to_percent(metrics["volatility"]),
            "sharpeRatio": metrics["sharpe"],
            "maxDrawdown": to_percent(metrics["max_drawdown"]),
        },
    )


@router.get("/equity-curve")
def get_portfolio_equity_curve(
    tickers: str | None = Query(None, description="Comma-separated tickers"),
    lookback_days: int = Query(settings.backtest_lookback_days, ge=252, le=4000),
    max_weight: float = Query(settings.max_weight, ge=0.01, le=1.0),
):
    tickers_list = parse_tickers(tickers, settings.default_tickers)
    try:
        prices = data_service.get_prices_frame(tickers_list)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    result = backtest_service.run_backtest(
        prices,
        lookback_days=lookback_days,
        max_weight=max_weight,
        rebalance_frequency="M",
        risk_free_rate=settings.risk_free_rate,
    )
    equity_curve = result.get("equity_curve")
    points = []
    if equity_curve is not None and not equity_curve.empty:
        for date, value in equity_curve.items():
            points.append({"date": format_date(date), "value": float(value)})
    return {"equityCurve": points}
