from __future__ import annotations

from typing import Dict
import numpy as np
import pandas as pd

from core.backtest import backtest_strategy
from services.optimization_service import optimize_portfolio
from utils.helpers import compute_drawdown, compute_win_rate


def _run_backtest_core(
    prices: pd.DataFrame,
    lookback_days: int,
    max_weight: float,
    initial_value: float,
) -> Dict[str, object]:
    if prices.empty:
        return {
            "equity_curve": pd.Series(dtype=float),
            "summary": {
                "cagr": 0.0,
                "sharpe": 0.0,
                "max_drawdown": 0.0,
                "win_rate": 0.0,
                "total_return": 0.0,
            },
        }

    equity_curve, cagr, sharpe, max_dd = backtest_strategy(
        prices,
        lookback_window=lookback_days,
        max_weight=max_weight,
    )

    if equity_curve is None or equity_curve.empty:
        return {
            "equity_curve": pd.Series(dtype=float),
            "summary": {
                "cagr": 0.0,
                "sharpe": 0.0,
                "max_drawdown": 0.0,
                "win_rate": 0.0,
                "total_return": 0.0,
            },
        }

    equity_curve = equity_curve * initial_value
    portfolio_returns = equity_curve.pct_change().dropna()
    win_rate = compute_win_rate(portfolio_returns)
    total_return = equity_curve.iloc[-1] / initial_value - 1.0

    # Ensure month-end series for charting.
    equity_curve = equity_curve.resample("M").last().dropna()

    return {
        "equity_curve": equity_curve,
        "summary": {
            "cagr": float(cagr),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_dd),
            "win_rate": float(win_rate),
            "total_return": float(total_return),
        },
    }


def run_backtest(
    prices: pd.DataFrame,
    lookback_days: int = 2520,
    max_weight: float = 0.2,
    rebalance_frequency: str = "M",
    risk_free_rate: float = 0.0,
    initial_value: float = 100000.0,
) -> Dict[str, object]:
    """
    Monthly (or quarterly) rebalance backtest using rolling lookback history.
    Expected returns/covariance follow the Streamlit-style mean/cov approach.
    """
    try:
        result = _run_backtest_core(
            prices=prices,
            lookback_days=lookback_days,
            max_weight=max_weight,
            initial_value=initial_value,
        )
        if result.get("equity_curve") is not None and not result.get("equity_curve").empty:
            return result
    except Exception:
        pass
    returns = prices.pct_change(fill_method=None).dropna(how="all")
    returns = returns.dropna(axis=1, how="any")

    if returns.empty:
        return {
            "equity_curve": pd.Series(dtype=float),
            "summary": {
                "cagr": 0.0,
                "sharpe": 0.0,
                "max_drawdown": 0.0,
                "win_rate": 0.0,
                "total_return": 0.0,
            },
        }

    rebalance_rule = "M" if rebalance_frequency.upper() == "M" else "Q"
    rebalance_dates = returns.resample(rebalance_rule).last().index
    if len(rebalance_dates) < 2:
        rebalance_dates = returns.index

    portfolio_returns = pd.Series(index=returns.index, dtype=float)

    for i in range(len(rebalance_dates) - 1):
        rebalance_date = rebalance_dates[i]
        next_date = rebalance_dates[i + 1]

        history = returns.loc[:rebalance_date].tail(lookback_days)
        history = history.dropna(axis=1, how="any")
        if history.shape[1] < 2:
            continue

        optimization = optimize_portfolio(
            history,
            max_weight=max_weight,
            risk_free_rate=risk_free_rate,
            lookback_days=min(lookback_days, len(history)),
        )
        weights = optimization.get("weights")
        tickers = optimization.get("tickers", list(history.columns))
        if weights is None or len(weights) == 0 or len(tickers) == 0:
            continue

        period_returns = returns.loc[rebalance_date:next_date, tickers]
        if period_returns.empty:
            continue

        period_portfolio_returns = period_returns @ weights
        portfolio_returns.loc[period_portfolio_returns.index] = period_portfolio_returns

    portfolio_returns = portfolio_returns.dropna()
    if portfolio_returns.empty:
        equity_curve = pd.Series(dtype=float)
    else:
        equity_curve = (1 + portfolio_returns).cumprod() * initial_value

    # Summary metrics
    total_return = 0.0
    if not equity_curve.empty:
        total_return = equity_curve.iloc[-1] / initial_value - 1.0

    years = max(len(portfolio_returns) / 252.0, 1e-6)
    cagr = (1 + total_return) ** (1 / years) - 1.0 if total_return > -1 else -1.0

    annual_return = portfolio_returns.mean() * 252
    annual_vol = portfolio_returns.std() * np.sqrt(252)
    sharpe = (annual_return - risk_free_rate) / annual_vol if annual_vol > 0 else 0.0

    max_dd = compute_drawdown(equity_curve) if not equity_curve.empty else 0.0
    win_rate = compute_win_rate(portfolio_returns)

    # Resample equity curve to month-end for charting
    if not equity_curve.empty:
        equity_curve = equity_curve.resample("M").last().dropna()

    return {
        "equity_curve": equity_curve,
        "summary": {
            "cagr": float(cagr),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_dd),
            "win_rate": float(win_rate),
            "total_return": float(total_return),
        },
    }
