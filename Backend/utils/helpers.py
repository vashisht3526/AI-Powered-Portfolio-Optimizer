from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional
import pandas as pd


def parse_tickers(value: Optional[str], default: List[str]) -> List[str]:
    if not value:
        return [ticker.upper() for ticker in default]
    return [item.strip().upper() for item in value.split(",") if item.strip()]


def parse_date(value: Optional[str]) -> Optional[pd.Timestamp]:
    if not value:
        return None
    return pd.to_datetime(value)


def format_date(value: pd.Timestamp) -> str:
    return value.strftime("%Y-%m-%d")


def to_percent(value: float) -> float:
    return float(value) * 100.0


def ensure_weights(tickers: List[str], weights: Optional[List[float]]) -> List[float]:
    if weights and len(weights) == len(tickers):
        total = sum(weights)
        if total == 0:
            return [1.0 / len(tickers)] * len(tickers)
        return [w / total for w in weights]
    return [1.0 / len(tickers)] * len(tickers)


def compute_drawdown(equity_curve: pd.Series) -> float:
    if equity_curve.empty:
        return 0.0
    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve / rolling_max) - 1.0
    return float(drawdown.min())


def compute_win_rate(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    return float((returns > 0).mean())


def clean_prices_frame(prices: pd.DataFrame) -> pd.DataFrame:
    prices = prices.copy()
    prices.replace([pd.NA, pd.NaT, float("inf"), float("-inf")], pd.NA, inplace=True)
    prices = prices.sort_index()
    prices = prices.ffill()
    prices = prices.dropna(how="all")
    return prices


def clip_weights(weights: Iterable[float], max_weight: float) -> List[float]:
    weights = list(weights)
    if not weights:
        return weights
    max_weight = max(max_weight, 0.0)
    clipped = [min(max(w, 0.0), max_weight) for w in weights]
    total = sum(clipped)
    if total == 0:
        return [1.0 / len(clipped)] * len(clipped)
    return [w / total for w in clipped]


def ensure_min_history(returns: pd.DataFrame, min_points: int = 30) -> pd.DataFrame:
    if returns.empty:
        return returns
    valid = returns.dropna(axis=1, how="any")
    if len(valid) < min_points:
        return returns
    return valid
