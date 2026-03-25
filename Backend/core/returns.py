import pandas as pd

def compute_daily_returns(price_csv_path: str) -> pd.DataFrame:
    """
    Computes daily returns from close price CSV.
    """
    prices = pd.read_csv(price_csv_path, index_col=0, parse_dates=True)
    returns = prices.pct_change(fill_method=None)
    return returns
