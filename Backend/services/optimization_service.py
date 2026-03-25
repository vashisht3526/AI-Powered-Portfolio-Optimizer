from __future__ import annotations

from typing import Dict
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from core.covariance import compute_covariance_matrix as core_covariance
from core.expected_return import compute_expected_monthly_return
from core.optimizer import optimize_portfolio as core_optimize
from utils.helpers import clip_weights
from services.metrics_service import (
    compute_covariance_matrix,
    compute_expected_returns,
    compute_portfolio_metrics,
)


def _optimize_portfolio_legacy(
    returns: pd.DataFrame,
    max_weight: float = 0.2,
    risk_free_rate: float = 0.0,
    lookback_days: int = 60,
    min_holdings: int = 6,
    diversification_penalty: float = 0.1,
) -> Dict[str, object]:
    # Use recent history only (Streamlit-style rolling window).
    returns = returns.tail(lookback_days).dropna(how="any")
    if returns.empty:
        return {"weights": np.array([]), "metrics": {}}

    expected_returns = compute_expected_returns(returns, lookback_days=lookback_days)
    cov_matrix = compute_covariance_matrix(returns, lookback_days=lookback_days)
    common_assets = expected_returns.index.intersection(cov_matrix.index)
    expected_returns = expected_returns.loc[common_assets]
    cov_matrix = cov_matrix.loc[common_assets, common_assets]

    mu_values = expected_returns.values
    cov_values = cov_matrix.values
    tickers = list(common_assets)
    n_assets = len(tickers)
    if n_assets == 0:
        return {"weights": np.array([]), "metrics": {}}

    min_max_weight = 1.0 / n_assets
    max_weight = max(max_weight, min_max_weight)

    # Convert annual risk-free rate to monthly to match expected returns frequency.
    risk_free_monthly = risk_free_rate / 12.0

    def neg_sharpe_with_diversification(weights: np.ndarray) -> float:
        """
        Maximize Sharpe-like objective with a soft diversification penalty.
        Effective number of holdings = 1 / sum(w^2).
        """
        port_return = np.dot(weights, mu_values)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_values, weights)))
        if port_vol == 0:
            return 1e6

        sharpe = (port_return - risk_free_monthly) / port_vol

        # Soft diversification preference (penalize overly concentrated portfolios).
        effective_n = 1.0 / np.sum(np.square(weights))
        target_holdings = min(min_holdings, n_assets)
        penalty = 0.0
        if target_holdings > 1 and effective_n < target_holdings:
            penalty = diversification_penalty * (target_holdings - effective_n) ** 2

        return -sharpe + penalty

    constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    bounds = [(0.0, max_weight) for _ in range(n_assets)]
    initial = np.array([1.0 / n_assets] * n_assets)

    result = minimize(
        neg_sharpe_with_diversification,
        initial,
        bounds=bounds,
        constraints=constraints,
        method="SLSQP",
        options={"maxiter": 500},
    )

    if not result.success:
        weights = clip_weights(initial, max_weight)
    else:
        weights = clip_weights(result.x, max_weight)

    aligned_returns = returns[common_assets]
    metrics = compute_portfolio_metrics(aligned_returns, np.array(weights), risk_free_rate)

    return {
        "weights": np.array(weights),
        "tickers": list(common_assets),
        "metrics": metrics,
    }


def _optimize_portfolio_core(
    returns: pd.DataFrame,
    max_weight: float = 0.2,
    risk_free_rate: float = 0.0,
    lookback_days: int = 60,
) -> Dict[str, object]:
    # Use recent history only (core-style rolling window).
    returns = returns.tail(lookback_days).dropna(how="any")
    if returns.empty:
        return {"weights": np.array([]), "metrics": {}}

    expected_returns = compute_expected_monthly_return(returns, lookback_window=lookback_days)
    cov_matrix = core_covariance(returns, lookback_window=lookback_days)
    common_assets = expected_returns.index.intersection(cov_matrix.index)
    expected_returns = expected_returns.loc[common_assets]
    cov_matrix = cov_matrix.loc[common_assets, common_assets]

    if expected_returns.empty:
        return {"weights": np.array([]), "metrics": {}}

    weights_series, _, _, _ = core_optimize(expected_returns, cov_matrix, max_weight)
    if weights_series.empty:
        return {"weights": np.array([]), "metrics": {}}

    weights_series = weights_series.reindex(common_assets, fill_value=0.0)
    tickers = list(common_assets)
    weights = weights_series.values
    aligned_returns = returns[tickers]
    metrics = compute_portfolio_metrics(aligned_returns, np.array(weights), risk_free_rate)

    return {
        "weights": np.array(weights),
        "tickers": tickers,
        "metrics": metrics,
    }


def optimize_portfolio(
    returns: pd.DataFrame,
    max_weight: float = 0.2,
    risk_free_rate: float = 0.0,
    lookback_days: int = 60,
    min_holdings: int = 6,
    diversification_penalty: float = 0.1,
) -> Dict[str, object]:
    try:
        result = _optimize_portfolio_core(
            returns,
            max_weight=max_weight,
            risk_free_rate=risk_free_rate,
            lookback_days=lookback_days,
        )
        if result.get("weights") is not None and len(result.get("weights")) > 0:
            return result
    except Exception:
        pass

    return _optimize_portfolio_legacy(
        returns,
        max_weight=max_weight,
        risk_free_rate=risk_free_rate,
        lookback_days=lookback_days,
        min_holdings=min_holdings,
        diversification_penalty=diversification_penalty,
    )
