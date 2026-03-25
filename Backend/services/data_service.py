from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json

import pandas as pd
try:
    import yfinance as yf
except ModuleNotFoundError:  # Allow local CSV mode without yfinance
    yf = None

from config import settings
from utils.helpers import clean_prices_frame


_METADATA_FILE = settings.metadata_dir / "tickers.json"
_LOCAL_PRICES_FILE = settings.data_dir / "nifty50_close_prices_10y.csv"
_LOCAL_RETURNS_FILE = settings.data_dir / "nifty50_daily_returns.csv"
_local_prices_cache: pd.DataFrame | None = None


def _load_metadata() -> Dict[str, dict]:
    if not _METADATA_FILE.exists():
        return {}
    try:
        return json.loads(_METADATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_metadata(data: Dict[str, dict]) -> None:
    _METADATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _today() -> pd.Timestamp:
    return pd.Timestamp.utcnow().normalize().tz_localize(None)


def _yesterday() -> pd.Timestamp:
    return (_today() - pd.Timedelta(days=1)).normalize()


def _normalize_ticker(ticker: str) -> str:
    ticker = ticker.upper()
    if ticker.endswith(".NS"):
        return ticker[:-3]
    return ticker


def _load_local_prices() -> pd.DataFrame | None:
    global _local_prices_cache
    if _local_prices_cache is not None:
        return _local_prices_cache
    if not _LOCAL_PRICES_FILE.exists():
        return None
    df = pd.read_csv(_LOCAL_PRICES_FILE, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    _local_prices_cache = df.sort_index()
    return _local_prices_cache


def get_local_universe() -> List[str]:
    df = _load_local_prices()
    if df is None or df.empty:
        return []
    return [str(col).upper() for col in df.columns]


def _extract_price_frame(
    data: pd.DataFrame,
    tickers: List[str],
    field: str = "Adj Close",
) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()

    if len(tickers) == 1:
        series = data[field] if field in data.columns else data.get("Close")
        if series is None:
            return pd.DataFrame()
        base = _normalize_ticker(tickers[0])
        return pd.DataFrame({base: series})

    if isinstance(data.columns, pd.MultiIndex):
        level0 = data.columns.get_level_values(0)
        if field in level0:
            field_df = data[field]
        elif "Close" in level0:
            field_df = data["Close"]
        else:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

    mapped_columns = {}
    for col in field_df.columns:
        base = _normalize_ticker(str(col))
        mapped_columns[col] = base
    field_df = field_df.rename(columns=mapped_columns)
    return field_df


def update_local_prices() -> Dict[str, object]:
    """
    Update the local NIFTY50 CSV by fetching only missing rows via yfinance (if available).
    Data is synced up to yesterday (UTC) to avoid partial current-day candles.
    """
    df = _load_local_prices()
    if df is None or df.empty:
        return {
            "updated": False,
            "reason": "Local CSV not found",
        }

    last_date = df.index.max().normalize()
    target_date = _yesterday()
    if last_date >= target_date:
        return {
            "updated": False,
            "last_date": str(last_date.date()),
            "up_to_date": True,
        }

    if yf is None:
        return {
            "updated": False,
            "last_date": str(last_date.date()),
            "up_to_date": False,
            "reason": "yfinance not installed",
        }

    tickers = [f"{col}.NS" for col in df.columns]
    fetch_start = (last_date + pd.Timedelta(days=1)).date().isoformat()
    fetch_end = (target_date + pd.Timedelta(days=1)).date().isoformat()

    try:
        data = yf.download(
            tickers,
            start=fetch_start,
            end=fetch_end,
            interval="1d",
            auto_adjust=False,
            progress=False,
            group_by="column",
        )
    except Exception as exc:
        return {
            "updated": False,
            "last_date": str(last_date.date()),
            "up_to_date": False,
            "reason": f"yfinance error: {exc}",
        }

    new_prices = _extract_price_frame(data, tickers)
    if new_prices.empty:
        return {
            "updated": False,
            "last_date": str(last_date.date()),
            "up_to_date": False,
            "reason": "No new data returned",
        }

    combined = pd.concat([df, new_prices], axis=0)
    combined = combined[~combined.index.duplicated(keep="last")]
    combined = combined.sort_index()
    combined = combined.loc[combined.index <= target_date]
    cutoff = _today() - pd.DateOffset(years=settings.price_start_years)
    combined = combined.loc[combined.index >= cutoff]
    combined.to_csv(_LOCAL_PRICES_FILE)

    # refresh cache
    global _local_prices_cache
    _local_prices_cache = combined

    return {
        "updated": True,
        "last_date": str(combined.index.max().date()),
        "rows_added": len(new_prices),
    }


def update_local_returns() -> Dict[str, object]:
    """
    Update the local daily returns CSV based on the updated prices file.
    """
    prices = _load_local_prices()
    if prices is None or prices.empty:
        return {
            "updated": False,
            "reason": "Local prices CSV not found",
        }

    target_date = _yesterday()
    prices = prices.loc[prices.index <= target_date]

    returns = prices.pct_change(fill_method=None).dropna(how="all")
    if returns.empty:
        return {
            "updated": False,
            "reason": "Not enough price history",
        }

    cutoff = _today() - pd.DateOffset(years=settings.price_start_years)
    returns = returns.loc[(returns.index >= cutoff) & (returns.index <= target_date)]

    if not _LOCAL_RETURNS_FILE.exists():
        returns.to_csv(_LOCAL_RETURNS_FILE)
        return {
            "updated": True,
            "last_date": str(returns.index.max().date()),
            "rows_added": int(returns.shape[0]),
            "rebuilt": True,
        }

    existing = pd.read_csv(_LOCAL_RETURNS_FILE, index_col=0, parse_dates=True)
    existing.index = pd.to_datetime(existing.index)

    if existing.empty or set(existing.columns) != set(returns.columns):
        returns.to_csv(_LOCAL_RETURNS_FILE)
        return {
            "updated": True,
            "last_date": str(returns.index.max().date()),
            "rows_added": int(returns.shape[0]),
            "rebuilt": True,
        }

    last_date = existing.index.max().normalize()
    new_returns = returns.loc[returns.index > last_date]
    if new_returns.empty:
        return {
            "updated": False,
            "last_date": str(last_date.date()),
            "up_to_date": True,
        }

    combined = pd.concat([existing, new_returns], axis=0)
    combined = combined[~combined.index.duplicated(keep="last")]
    combined = combined.sort_index()
    combined = combined.loc[(combined.index >= cutoff) & (combined.index <= target_date)]
    combined.to_csv(_LOCAL_RETURNS_FILE)

    return {
        "updated": True,
        "last_date": str(combined.index.max().date()),
        "rows_added": int(new_returns.shape[0]),
    }


def update_local_prices_and_returns() -> Dict[str, object]:
    prices_result = update_local_prices()
    returns_result = update_local_returns()
    return {
        "prices": prices_result,
        "returns": returns_result,
    }


def get_update_status() -> Dict[str, object]:
    df = _load_local_prices()
    if df is None or df.empty:
        return {"status": "missing"}
    last_date = df.index.max().normalize()
    return {
        "status": "ok",
        "last_date": str(last_date.date()),
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "yfinance_available": yf is not None,
        "up_to_date": last_date >= _yesterday(),
    }


def _get_local_series(
    ticker: str,
    start: Optional[pd.Timestamp] = None,
    end: Optional[pd.Timestamp] = None,
) -> pd.Series | None:
    df = _load_local_prices()
    if df is None or df.empty:
        return None
    base = _normalize_ticker(ticker)
    if base not in df.columns:
        return None
    series = df[base].copy()
    series.name = ticker.upper()
    if start is not None:
        series = series.loc[series.index >= start]
    if end is not None:
        series = series.loc[series.index <= end]
    return series.dropna()


def _ensure_history(
    ticker: str,
    start: Optional[pd.Timestamp] = None,
    end: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    ticker = ticker.upper()
    local_series = _get_local_series(ticker, start=start, end=end)
    if local_series is not None and not local_series.empty:
        local_df = pd.DataFrame(
            {
                "Close": local_series.values,
                "Adj Close": local_series.values,
            },
            index=local_series.index,
        )
        local_df.index.name = "Date"
        return local_df
    if start is None:
        start = _today() - pd.DateOffset(years=settings.price_start_years)
    if end is None:
        end = _yesterday()

    path = settings.prices_dir / f"{ticker}.csv"
    existing = pd.DataFrame()
    if path.exists():
        existing = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
        existing.index = pd.to_datetime(existing.index)

    fetch_start = start
    if not existing.empty:
        last_date = existing.index.max()
        if last_date >= end:
            return existing
        fetch_start = last_date + pd.Timedelta(days=1)

    fetch_end = end + pd.Timedelta(days=1)
    if yf is None:
        return existing

    try:
        data = yf.download(
            ticker,
            start=fetch_start.date().isoformat(),
            end=fetch_end.date().isoformat(),
            interval="1d",
            auto_adjust=False,
            progress=False,
            group_by="column",
        )
    except Exception:
        return existing

    if data.empty:
        return existing

    data.index.name = "Date"
    data.index = pd.to_datetime(data.index)

    if existing.empty:
        combined = data
    else:
        combined = pd.concat([existing, data])
        combined = combined[~combined.index.duplicated(keep="last")]
        combined = combined.sort_index()

    combined.to_csv(path)
    return combined


def get_price_history(
    ticker: str,
    start: Optional[pd.Timestamp] = None,
    end: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    df = _ensure_history(ticker, start, end)
    if df.empty:
        raise ValueError(f"No data available for {ticker}")
    df = df.loc[start:end] if start is not None or end is not None else df
    return clean_prices_frame(df)


def get_prices_frame(
    tickers: List[str],
    start: Optional[pd.Timestamp] = None,
    end: Optional[pd.Timestamp] = None,
    field: str = "Adj Close",
) -> pd.DataFrame:
    frames = []
    for ticker in tickers:
        df = get_price_history(ticker, start, end)
        if field not in df.columns:
            if "Close" in df.columns:
                series = df["Close"].copy()
            else:
                continue
        else:
            series = df[field].copy()
        series.name = ticker.upper()
        frames.append(series)

    if not frames:
        raise ValueError("No price data available for selected tickers")

    combined = pd.concat(frames, axis=1)
    combined = clean_prices_frame(combined)
    return combined


def persist_returns(name: str, returns: pd.DataFrame) -> None:
    if returns.empty:
        return
    safe_name = name.replace("/", "_").replace("\\", "_")
    path = settings.returns_dir / f"{safe_name}.csv"
    returns.to_csv(path)


def get_latest_prices(tickers: List[str]) -> Dict[str, float]:
    prices = {}
    for ticker in tickers:
        df = get_price_history(ticker)
        if df.empty:
            continue
        latest = df["Adj Close"].iloc[-1] if "Adj Close" in df.columns else df["Close"].iloc[-1]
        prices[ticker.upper()] = float(latest)
    return prices


def get_ticker_profile(ticker: str) -> Dict[str, Optional[str]]:
    ticker = ticker.upper()
    metadata = _load_metadata()
    if ticker in metadata:
        return metadata[ticker]

    local_series = _get_local_series(ticker)
    if local_series is not None:
        profile = {"name": _normalize_ticker(ticker), "sector": None}
        metadata[ticker] = profile
        _save_metadata(metadata)
        return profile

    info = {}
    if yf is not None:
        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info or {}
        except Exception:
            info = {}

    profile = {
        "name": info.get("shortName") or info.get("longName") or ticker,
        "sector": info.get("sector"),
    }

    metadata[ticker] = profile
    _save_metadata(metadata)
    return profile


def search_tickers(query: str, universe: Optional[List[str]] = None, limit: int = 10) -> List[Dict[str, str]]:
    query = query.strip().lower()
    if not query:
        return []
    if universe is None:
        local_prices = _load_local_prices()
        if local_prices is not None:
            universe = [f"{ticker}.NS" for ticker in local_prices.columns]
        else:
            universe = settings.default_tickers
    results = []
    for ticker in universe:
        profile = get_ticker_profile(ticker)
        name = profile.get("name", "")
        if query in ticker.lower() or query in name.lower():
            results.append({
                "ticker": ticker,
                "name": name or ticker,
                "sector": profile.get("sector"),
            })
        if len(results) >= limit:
            break
    return results
