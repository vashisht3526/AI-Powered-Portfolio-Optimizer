from __future__ import annotations

from typing import Dict, Optional
import numpy as np
import pandas as pd

from utils.helpers import compute_drawdown


def compute_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    returns = prices.pct_change(fill_method=None)
    returns = returns.dropna(how="all")
    return returns


def compute_expected_returns(
    returns: pd.DataFrame,
    lookback_days: int = 60,
    trading_days: int = 21,
) -> pd.Series:
    """
    Expected monthly returns based on historical mean daily returns.
    Mirrors the Streamlit rolling-mean approach (mean * trading_days).
    """
    recent_returns = returns.tail(lookback_days)
    expected_returns = recent_returns.mean() * trading_days
    return expected_returns.dropna()


def compute_covariance_matrix(
    returns: pd.DataFrame,
    lookback_days: int = 60,
    trading_days: int = 21,
) -> pd.DataFrame:
    """
    Monthly covariance matrix from recent daily returns.
    Daily covariance is scaled by trading_days to match expected returns frequency.
    """
    recent_returns = returns.tail(lookback_days).dropna(axis=1, how="any")
    cov_daily = recent_returns.cov()
    cov_monthly = cov_daily * trading_days
    return cov_monthly


def compute_cagr(prices: pd.Series) -> float:
    prices = prices.dropna()
    if len(prices) < 2:
        return 0.0
    total_return = prices.iloc[-1] / prices.iloc[0] - 1.0
    years = len(prices) / 252.0
    if years <= 0:
        return 0.0
    return float((1 + total_return) ** (1 / years) - 1.0)


def compute_volatility(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    return float(returns.std() * np.sqrt(252))


def compute_beta(stock_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    if stock_returns.empty or benchmark_returns.empty:
        return 0.0
    aligned = pd.concat([stock_returns, benchmark_returns], axis=1).dropna()
    if aligned.empty:
        return 0.0
    cov = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])[0][1]
    var = np.var(aligned.iloc[:, 1])
    if var == 0:
        return 0.0
    return float(cov / var)


def compute_portfolio_returns(returns: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    returns = returns.dropna(how="any")
    if returns.empty:
        return pd.Series(dtype=float)
    return returns @ weights


def compute_portfolio_metrics(
    returns: pd.DataFrame,
    weights: np.ndarray,
    risk_free_rate: float = 0.0,
) -> Dict[str, float]:
    portfolio_returns = compute_portfolio_returns(returns, weights)
    if portfolio_returns.empty:
        return {
            "expected_return": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
            "max_drawdown": 0.0,
        }

    mean_daily = portfolio_returns.mean()
    annual_return = mean_daily * 252
    annual_vol = portfolio_returns.std() * np.sqrt(252)
    sharpe = 0.0
    if annual_vol > 0:
        sharpe = (annual_return - risk_free_rate) / annual_vol

    equity_curve = (1 + portfolio_returns).cumprod()
    max_dd = compute_drawdown(equity_curve)

    # Convert to monthly figures for display
    expected_monthly = mean_daily * 21
    monthly_vol = portfolio_returns.std() * np.sqrt(21)

    return {
        "expected_return": float(expected_monthly),
        "volatility": float(monthly_vol),
        "sharpe": float(sharpe),
        "max_drawdown": float(max_dd),
    }


def compute_stock_metrics(
    prices: pd.Series,
    benchmark_prices: Optional[pd.Series] = None,
    portfolio_returns: Optional[pd.Series] = None,
) -> Dict[str, float]:
    prices = prices.dropna()
    if prices.empty:
        return {
            "annualized_return": 0.0,
            "volatility": 0.0,
            "max_drawdown": 0.0,
            "beta": 0.0,
            "correlation": 0.0,
        }

    returns = prices.pct_change(fill_method=None).dropna()
    annualized_return = compute_cagr(prices)
    volatility = compute_volatility(returns)
    equity_curve = (1 + returns).cumprod()
    max_dd = compute_drawdown(equity_curve)

    beta = 0.0
    if benchmark_prices is not None:
        benchmark_returns = benchmark_prices.pct_change(fill_method=None).dropna()
        beta = compute_beta(returns, benchmark_returns)

    correlation = 0.0
    if portfolio_returns is not None and not portfolio_returns.empty:
        aligned = pd.concat([returns, portfolio_returns], axis=1).dropna()
        if not aligned.empty:
            correlation = float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))

    return {
        "annualized_return": float(annualized_return),
        "volatility": float(volatility),
        "max_drawdown": float(max_dd),
        "beta": float(beta),
        "correlation": float(correlation),
    }
