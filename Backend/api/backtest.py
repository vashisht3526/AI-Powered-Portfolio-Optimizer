from __future__ import annotations

from fastapi import APIRouter, HTTPException

from config import settings
from models.schemas import BacktestRequest, BacktestSummaryResponse, EquityCurveResponse
from services import backtest_service, data_service, nifty50_pipeline
from utils.helpers import format_date, parse_date, to_percent


router = APIRouter()

_last_result: dict | None = None


def _run_and_cache(request: BacktestRequest) -> dict:
    global _last_result

    tickers = request.tickers or settings.default_tickers
    start_date = parse_date(request.start_date)
    end_date = parse_date(request.end_date)

    try:
        prices = data_service.get_prices_frame(tickers, start=start_date, end=end_date)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    result = backtest_service.run_backtest(
        prices,
        lookback_days=request.lookback_days,
        max_weight=request.max_weight,
        rebalance_frequency=request.rebalance_frequency,
        risk_free_rate=settings.risk_free_rate,
    )
    _last_result = result
    return result


def _get_or_run_default() -> dict:
    global _last_result
    if _last_result is None:
        request = BacktestRequest(
            tickers=settings.default_tickers,
            lookback_days=settings.backtest_lookback_days,
            max_weight=settings.max_weight,
        )
        _last_result = _run_and_cache(request)
    return _last_result


@router.post("/run")
def run_backtest(request: BacktestRequest):
    result = _run_and_cache(request)

    equity_curve = result.get("equity_curve")
    summary = result.get("summary", {})

    equity_points = []
    if equity_curve is not None and not equity_curve.empty:
        for date, value in equity_curve.items():
            equity_points.append({"date": format_date(date), "value": float(value)})

    return {
        "equityCurve": equity_points,
        "summary": {
            "cagr": to_percent(summary.get("cagr", 0.0)),
            "sharpeRatio": summary.get("sharpe", 0.0),
            "maxDrawdown": to_percent(summary.get("max_drawdown", 0.0)),
            "winRate": to_percent(summary.get("win_rate", 0.0)),
            "totalReturn": to_percent(summary.get("total_return", 0.0)),
        },
    }


@router.get("/equity-curve", response_model=EquityCurveResponse)
def get_equity_curve():
    cached_curve = nifty50_pipeline.load_backtest_equity_curve()
    if cached_curve is not None and not cached_curve.empty:
        equity_points = []
        for date, value in cached_curve.items():
            equity_points.append({"date": format_date(date), "value": float(value)})
        return EquityCurveResponse(equityCurve=equity_points)

    result = _get_or_run_default()
    equity_curve = result.get("equity_curve")

    equity_points = []
    if equity_curve is not None and not equity_curve.empty:
        for date, value in equity_curve.items():
            equity_points.append({"date": format_date(date), "value": float(value)})

    return EquityCurveResponse(equityCurve=equity_points)


@router.get("/summary", response_model=BacktestSummaryResponse)
def get_backtest_summary():
    cached_summary = nifty50_pipeline.load_backtest_summary()
    if cached_summary:
        return BacktestSummaryResponse(
            cagr=to_percent(cached_summary.get("cagr", 0.0)),
            sharpeRatio=cached_summary.get("sharpe", 0.0),
            maxDrawdown=to_percent(cached_summary.get("max_drawdown", 0.0)),
            winRate=to_percent(cached_summary.get("win_rate", 0.0)),
            totalReturn=to_percent(cached_summary.get("total_return", 0.0)),
        )

    result = _get_or_run_default()
    summary = result.get("summary", {})

    return BacktestSummaryResponse(
        cagr=to_percent(summary.get("cagr", 0.0)),
        sharpeRatio=summary.get("sharpe", 0.0),
        maxDrawdown=to_percent(summary.get("max_drawdown", 0.0)),
        winRate=to_percent(summary.get("win_rate", 0.0)),
        totalReturn=to_percent(summary.get("total_return", 0.0)),
    )
