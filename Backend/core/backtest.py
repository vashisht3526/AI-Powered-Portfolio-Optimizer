import pandas as pd
import numpy as np
from core.expected_return import compute_expected_monthly_return
from core.covariance import compute_covariance_matrix
from core.optimizer import optimize_portfolio

def backtest_strategy(
    prices: pd.DataFrame,
    lookback_window: int = 60,
    max_weight: float = 0.20
):
    """
    Walk-forward monthly backtest.
    """
    returns = prices.pct_change(fill_method=None)
    month_ends = returns.resample("ME").last().index

    portfolio_returns = []

    for i in range(len(month_ends) - 1):
        rebalance_date = month_ends[i]
        next_date = month_ends[i + 1]

        hist_returns = returns.loc[:rebalance_date].tail(lookback_window)
        hist_returns = hist_returns.dropna(axis=1)

        if hist_returns.shape[1] < 5:
            continue

        exp_returns = compute_expected_monthly_return(hist_returns, lookback_window)
        cov_matrix = compute_covariance_matrix(hist_returns, lookback_window)

        weights, _, _, _ = optimize_portfolio(
            exp_returns, cov_matrix, max_weight
        )

        future_returns = returns.loc[rebalance_date:next_date, weights.index]
        future_returns = future_returns.dropna()

        portfolio_return = (future_returns @ weights).sum()
        portfolio_returns.append(portfolio_return)

    portfolio_returns = pd.Series(portfolio_returns)
    equity_curve = (1 + portfolio_returns).cumprod()

    sharpe = portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(12)
    cagr = equity_curve.iloc[-1] ** (12 / len(equity_curve)) - 1
    max_dd = (equity_curve / equity_curve.cummax() - 1).min()

    return equity_curve, cagr, sharpe, max_dd
