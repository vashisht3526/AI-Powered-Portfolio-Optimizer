from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

from config import settings
from core.optimizer import optimize_portfolio
from services import data_service


PRICES_FILE = settings.data_dir / "nifty50_close_prices_10y.csv"
RETURNS_FILE = settings.data_dir / "nifty50_daily_returns.csv"

EXPECTED_RETURNS_FILE = settings.metrics_dir / "expected_monthly_returns.csv"
COV_MATRIX_FILE = settings.metrics_dir / "covariance_matrix.csv"
WEIGHTS_FILE = settings.metrics_dir / "optimized_portfolio_weights.csv"
WEIGHTS_METRICS_FILE = settings.metrics_dir / "optimized_portfolio_metrics.json"
BACKTEST_EQUITY_FILE = settings.metrics_dir / "backtest_equity_curve.csv"
BACKTEST_SUMMARY_FILE = settings.metrics_dir / "backtest_summary.json"
PORTFOLIO_METRICS_FILE = settings.metrics_dir / "portfolio_metrics.json"


def _read_frame(path: Path, *, parse_dates: bool = True) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, index_col=0, parse_dates=parse_dates)
    if parse_dates:
        df.index = pd.to_datetime(df.index)
    return df.sort_index()


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _target_date() -> pd.Timestamp:
    return (pd.Timestamp.utcnow().normalize() - pd.Timedelta(days=1)).tz_localize(None)


def _as_of_date(frame: pd.DataFrame | pd.Series) -> Optional[str]:
    if frame is None or frame.empty:
        return None
    if not isinstance(frame.index, pd.DatetimeIndex):
        return None
    return frame.index.max().date().isoformat()


def compute_expected_monthly_returns(
    returns: pd.DataFrame,
    lookback_days: int = 60,
    trading_days: int = 21,
) -> pd.Series:
    if returns.empty:
        return pd.Series(dtype=float)
    rolling_mean = returns.rolling(window=lookback_days).mean()
    if rolling_mean.empty:
        return pd.Series(dtype=float)
    expected = rolling_mean.iloc[-1] * trading_days
    return expected.dropna()


def compute_covariance_matrix(
    returns: pd.DataFrame,
    lookback_days: int = 60,
) -> pd.DataFrame:
    if returns.empty:
        return pd.DataFrame()
    recent_returns = returns.tail(lookback_days)
    recent_returns = recent_returns.dropna(axis=1, how="any")
    if recent_returns.empty:
        return pd.DataFrame()
    return recent_returns.cov()


def compute_optimized_weights(
    expected_returns: pd.Series,
    covariance_matrix: pd.DataFrame,
    max_weight: float = 1.0,
) -> tuple[pd.DataFrame, Dict[str, float]]:
    if expected_returns.empty or covariance_matrix.empty:
        return pd.DataFrame(), {"expected_return": 0.0, "volatility": 0.0, "sharpe": 0.0}

    weights, exp_ret, vol, sharpe = optimize_portfolio(
        expected_returns,
        covariance_matrix,
        max_weight=max_weight,
    )

    if weights.empty:
        return pd.DataFrame(), {"expected_return": 0.0, "volatility": 0.0, "sharpe": 0.0}

    weights_df = weights.to_frame(name="Weight")
    return weights_df, {
        "expected_return": float(exp_ret),
        "volatility": float(vol),
        "sharpe": float(sharpe),
    }


def run_backtest(
    prices: pd.DataFrame,
    lookback_days: int = 80,
    trading_days: int = 21,
    max_weight: float = 0.30,
) -> tuple[pd.Series, float, float, float]:
    if prices.empty:
        return pd.Series(dtype=float), 0.0, 0.0, 0.0

    returns = prices.pct_change(fill_method=None)
    month_ends = returns.resample("ME").last().index
    portfolio_returns = []

    for i in range(len(month_ends) - 1):
        rebalance_date = month_ends[i]
        next_rebalance = month_ends[i + 1]

        hist_returns = returns.loc[:rebalance_date].tail(lookback_days)
        hist_returns = hist_returns.dropna(axis=1, how="any")

        if hist_returns.shape[1] < 5:
            continue

        exp_returns = hist_returns.mean() * trading_days
        cov_matrix = hist_returns.cov()

        weights, _, _, _ = optimize_portfolio(exp_returns, cov_matrix, max_weight=max_weight)
        if weights.empty:
            continue

        future_returns = returns.loc[rebalance_date:next_rebalance, weights.index]
        future_returns = future_returns.dropna()
        if future_returns.empty:
            continue

        port_ret = (future_returns @ weights).sum()
        portfolio_returns.append(port_ret)

    portfolio_returns = pd.Series(portfolio_returns)
    equity_curve = (1 + portfolio_returns).cumprod()

    if portfolio_returns.empty:
        return equity_curve, 0.0, 0.0, 0.0

    std = portfolio_returns.std()
    sharpe = 0.0 if std == 0 else float(portfolio_returns.mean() / std * np.sqrt(12))
    cagr = float(equity_curve.iloc[-1] ** (12 / len(equity_curve)) - 1) if len(equity_curve) else 0.0
    max_dd = float((equity_curve / equity_curve.cummax() - 1).min())

    return equity_curve, cagr, sharpe, max_dd


def refresh_nifty50_metrics(
    lookback_days: int = 60,
    trading_days: int = 21,
    optimize_max_weight: float = 1.0,
    backtest_lookback_days: int = 80,
    backtest_max_weight: float = 0.30,
) -> Dict[str, object]:
    settings.metrics_dir.mkdir(parents=True, exist_ok=True)

    target_date = _target_date()

    returns = _read_frame(RETURNS_FILE)
    if returns.empty:
        prices = _read_frame(PRICES_FILE)
        if not prices.empty:
            returns = prices.pct_change(fill_method=None)
            returns.to_csv(RETURNS_FILE)

    if returns.empty:
        return {"updated": False, "reason": "No returns data available"}

    returns = returns.loc[returns.index <= target_date]

    expected_returns = compute_expected_monthly_returns(
        returns,
        lookback_days=lookback_days,
        trading_days=trading_days,
    )
    expected_df = expected_returns.to_frame(name="Expected_1M_Return")
    expected_df.to_csv(EXPECTED_RETURNS_FILE)

    cov_matrix = compute_covariance_matrix(returns, lookback_days=lookback_days)
    cov_matrix.to_csv(COV_MATRIX_FILE)

    weights_df, weights_metrics = compute_optimized_weights(
        expected_returns,
        cov_matrix,
        max_weight=optimize_max_weight,
    )
    weights_df.to_csv(WEIGHTS_FILE)

    as_of = _as_of_date(returns)

    portfolio_metrics = {
        "as_of": as_of,
        "expected_return": float(weights_metrics.get("expected_return", 0.0)),
        "volatility": float(weights_metrics.get("volatility", 0.0)),
        "sharpe": float(weights_metrics.get("sharpe", 0.0)),
        "max_drawdown": 0.0,
        "lookback_days": int(lookback_days),
        "trading_days": int(trading_days),
    }

    if not weights_df.empty:
        aligned_returns = returns.tail(lookback_days)
        aligned_returns = aligned_returns.dropna(axis=1, how="any")
        weight_series = weights_df["Weight"]
        common_assets = aligned_returns.columns.intersection(weight_series.index)
        if not common_assets.empty:
            portfolio_returns = aligned_returns[common_assets] @ weight_series.loc[common_assets]
            if not portfolio_returns.empty:
                equity_curve = (1 + portfolio_returns).cumprod()
                if not equity_curve.empty:
                    max_dd = (equity_curve / equity_curve.cummax() - 1).min()
                    portfolio_metrics["max_drawdown"] = float(max_dd)

    _write_json(PORTFOLIO_METRICS_FILE, portfolio_metrics)
    _write_json(
        WEIGHTS_METRICS_FILE,
        {
            "as_of": as_of,
            **weights_metrics,
        },
    )

    prices = _read_frame(PRICES_FILE)
    if not prices.empty:
        prices = prices.loc[prices.index <= target_date]
    equity_curve, cagr, sharpe, max_dd = run_backtest(
        prices,
        lookback_days=backtest_lookback_days,
        trading_days=trading_days,
        max_weight=backtest_max_weight,
    )

    if not equity_curve.empty:
        equity_curve.to_frame(name="Equity").to_csv(BACKTEST_EQUITY_FILE)

    win_rate = 0.0
    total_return = 0.0
    if equity_curve is not None and not equity_curve.empty:
        portfolio_returns = equity_curve.pct_change().dropna()
        if not portfolio_returns.empty:
            win_rate = float((portfolio_returns > 0).mean())
        total_return = float(equity_curve.iloc[-1] - 1.0)

    _write_json(
        BACKTEST_SUMMARY_FILE,
        {
            "as_of": _as_of_date(prices),
            "cagr": float(cagr),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_dd),
            "win_rate": float(win_rate),
            "total_return": float(total_return),
        },
    )

    return {
        "updated": True,
        "as_of": as_of,
        "expected_returns_rows": int(expected_df.shape[0]),
        "covariance_shape": [int(cov_matrix.shape[0]), int(cov_matrix.shape[1])],
        "weights_rows": int(weights_df.shape[0]),
        "backtest_points": int(equity_curve.shape[0]),
        "files": {
            "expected_returns": str(EXPECTED_RETURNS_FILE),
            "covariance": str(COV_MATRIX_FILE),
            "weights": str(WEIGHTS_FILE),
            "weights_metrics": str(WEIGHTS_METRICS_FILE),
            "portfolio_metrics": str(PORTFOLIO_METRICS_FILE),
            "backtest_equity": str(BACKTEST_EQUITY_FILE),
            "backtest_summary": str(BACKTEST_SUMMARY_FILE),
        },
    }


def refresh_nifty50_data_and_metrics(
    lookback_days: int = 60,
    trading_days: int = 21,
    optimize_max_weight: float = 1.0,
    backtest_lookback_days: int = 80,
    backtest_max_weight: float = 0.30,
) -> Dict[str, object]:
    update_result = data_service.update_local_prices_and_returns()
    metrics_result = refresh_nifty50_metrics(
        lookback_days=lookback_days,
        trading_days=trading_days,
        optimize_max_weight=optimize_max_weight,
        backtest_lookback_days=backtest_lookback_days,
        backtest_max_weight=backtest_max_weight,
    )
    return {
        "data_update": update_result,
        "metrics_update": metrics_result,
    }


def load_precomputed_weights() -> pd.DataFrame:
    return _read_frame(WEIGHTS_FILE, parse_dates=False)


def load_precomputed_metrics() -> Dict[str, object]:
    if not PORTFOLIO_METRICS_FILE.exists():
        return {}
    try:
        return json.loads(PORTFOLIO_METRICS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_backtest_summary() -> Dict[str, object]:
    if not BACKTEST_SUMMARY_FILE.exists():
        return {}
    try:
        return json.loads(BACKTEST_SUMMARY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_backtest_equity_curve() -> pd.Series:
    df = _read_frame(BACKTEST_EQUITY_FILE, parse_dates=True)
    if df.empty:
        return pd.Series(dtype=float)
    if "Equity" in df.columns:
        return df["Equity"].copy()
    # fall back to first column
    return df.iloc[:, 0].copy()
