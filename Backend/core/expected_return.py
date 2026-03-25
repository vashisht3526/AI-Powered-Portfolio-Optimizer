import pandas as pd

def compute_expected_monthly_return(
    returns: pd.DataFrame,
    lookback_window: int = 60,
    trading_days: int = 21
) -> pd.Series:
    """
    Computes expected 1-month return using rolling mean.
    """
    recent_returns = returns.tail(lookback_window)
    expected_returns = recent_returns.mean() * trading_days
    return expected_returns.dropna()
