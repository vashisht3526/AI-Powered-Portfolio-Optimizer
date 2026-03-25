from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
from typing import List

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)


def _parse_list(value: str | None, default: List[str], *, upper: bool = False) -> List[str]:
    if not value:
        return default
    items = [item.strip() for item in value.split(",") if item.strip()]
    if upper:
        return [item.upper() for item in items]
    return items


@dataclass
class Settings:
    app_name: str = "AI Portfolio Optimizer API"
    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent)

    data_dir: Path = field(init=False)
    prices_dir: Path = field(init=False)
    returns_dir: Path = field(init=False)
    metadata_dir: Path = field(init=False)
    metrics_dir: Path = field(init=False)

    default_tickers: List[str] = field(default_factory=lambda: [
        "RELIANCE.NS",
        "TCS.NS",
        "HDFCBANK.NS",
        "INFY.NS",
        "ICICIBANK.NS",
        "HINDUNILVR.NS",
        "AXISBANK.NS",
        "LT.NS",
        "SBIN.NS",
        "BAJFINANCE.NS",
    ])
    market_benchmark: str = "^NSEI"

    lookback_days: int = 180
    backtest_lookback_days: int = 2520
    max_weight: float = 0.2
    risk_free_rate: float = 0.06
    price_start_years: int = 10
    data_update_enabled: bool = True

    finnhub_api_key: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3-flash-preview"

    allowed_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ])

    def __post_init__(self) -> None:
        self.data_dir = self.base_dir / "data"
        self.prices_dir = self.data_dir / "prices"
        self.returns_dir = self.data_dir / "returns"
        self.metadata_dir = self.data_dir / "metadata"
        self.metrics_dir = self.data_dir / "metrics"

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.prices_dir.mkdir(parents=True, exist_ok=True)
        self.returns_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.default_tickers = _parse_list(
            os.getenv("DEFAULT_TICKERS"),
            self.default_tickers,
            upper=True,
        )
        self.market_benchmark = os.getenv("MARKET_BENCHMARK", self.market_benchmark)
        self.lookback_days = int(os.getenv("LOOKBACK_DAYS", str(self.lookback_days)))
        self.backtest_lookback_days = int(
            os.getenv("BACKTEST_LOOKBACK_DAYS", str(self.backtest_lookback_days))
        )
        self.max_weight = float(os.getenv("MAX_WEIGHT", str(self.max_weight)))
        self.risk_free_rate = float(os.getenv("RISK_FREE_RATE", str(self.risk_free_rate)))
        self.price_start_years = int(os.getenv("PRICE_START_YEARS", str(self.price_start_years)))
        self.data_update_enabled = os.getenv("DATA_UPDATE_ENABLED", "true").lower() in ("1", "true", "yes")

        self.finnhub_api_key = os.getenv("FINNHUB_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", self.gemini_model)

        self.allowed_origins = _parse_list(
            os.getenv("ALLOWED_ORIGINS"),
            self.allowed_origins,
            upper=False,
        )


settings = Settings()
