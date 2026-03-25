import pandas as pd

def compute_covariance_matrix(
    returns: pd.DataFrame,
    lookback_window: int = 60
) -> pd.DataFrame:
    """
    Computes covariance matrix from recent returns.
    """
    recent_returns = returns.tail(lookback_window)
    recent_returns = recent_returns.dropna(axis=1)
    cov_matrix = recent_returns.cov()
    return cov_matrix
