import numpy as np
import pandas as pd
from scipy.optimize import minimize

try:
    from pypfopt import EfficientFrontier
except ModuleNotFoundError:  # Allow fallback when PyPortfolioOpt isn't installed.
    EfficientFrontier = None

def _optimize_with_scipy(
    expected_returns: pd.Series,
    covariance_matrix: pd.DataFrame,
    max_weight: float,
):
    mu = expected_returns
    sigma = covariance_matrix
    if len(mu) == 0:
        return pd.Series(dtype=float), 0.0, 0.0, 0.0

    min_max_weight = 1.0 / len(mu)
    max_weight = max(max_weight, min_max_weight)

    def neg_sharpe(weights: np.ndarray) -> float:
        port_return = float(np.dot(weights, mu.values))
        port_vol = float(np.sqrt(np.dot(weights.T, np.dot(sigma.values, weights))))
        if port_vol == 0:
            return 1e6
        return -(port_return / port_vol)

    bounds = [(0.0, max_weight) for _ in range(len(mu))]
    constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    initial = np.array([1.0 / len(mu)] * len(mu))

    result = minimize(
        neg_sharpe,
        initial,
        bounds=bounds,
        constraints=constraints,
        method="SLSQP",
        options={"maxiter": 500},
    )

    if not result.success:
        weights = initial
    else:
        weights = result.x

    # Normalize in case of numerical drift.
    weights = np.clip(weights, 0.0, max_weight)
    total = weights.sum()
    if total == 0:
        weights = initial
        total = weights.sum()
    weights = weights / total

    weights = pd.Series(weights, index=mu.index)
    ret = float(np.dot(weights.values, mu.values))
    vol = float(np.sqrt(np.dot(weights.values.T, np.dot(sigma.values, weights.values))))
    vol = vol * (21 ** 0.5)
    sharpe = ret / vol if vol > 0 else 0.0
    return weights[weights > 0], ret, vol, sharpe


def optimize_portfolio(
    expected_returns: pd.Series,
    covariance_matrix: pd.DataFrame,
    max_weight: float = 0.20
):
    """
    Optimizes portfolio using Max Sharpe Ratio.
    """
    common_assets = expected_returns.index.intersection(covariance_matrix.index)
    mu = expected_returns.loc[common_assets]
    sigma = covariance_matrix.loc[common_assets, common_assets]

    if len(mu) == 0:
        return pd.Series(dtype=float), 0.0, 0.0, 0.0

    min_max_weight = 1.0 / len(mu)
    max_weight = max(max_weight, min_max_weight)

    if EfficientFrontier is None:
        return _optimize_with_scipy(mu, sigma, max_weight)

    ef = EfficientFrontier(mu, sigma)
    ef.add_constraint(lambda w: w <= max_weight)

    try:
        ef.max_sharpe(risk_free_rate=0.0)
        weights = pd.Series(ef.clean_weights())

        ret, vol, sharpe = ef.portfolio_performance(risk_free_rate=0.0)

        # Convert volatility to monthly
        vol = vol * (21 ** 0.5)
        sharpe = ret / vol if vol > 0 else 0.0

        return weights[weights > 0], ret, vol, sharpe
    except Exception:
        # Fallback to scipy optimizer if PyPortfolioOpt fails.
        return _optimize_with_scipy(mu, sigma, max_weight)
