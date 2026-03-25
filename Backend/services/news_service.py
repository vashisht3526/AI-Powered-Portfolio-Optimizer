from __future__ import annotations

from datetime import datetime, timedelta
from typing import List
import requests

from config import settings


FINNHUB_BASE = "https://finnhub.io/api/v1"


def _require_key() -> str | None:
    if not settings.finnhub_api_key:
        return None
    return settings.finnhub_api_key


def _call(endpoint: str, params: dict) -> list:
    token = _require_key()
    if not token:
        return []
    params = {**params, "token": token}
    try:
        response = requests.get(f"{FINNHUB_BASE}/{endpoint}", params=params, timeout=15)
        if response.status_code != 200:
            return []
        return response.json()
    except requests.RequestException:
        return []


def _format_date(timestamp: int) -> str:
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")


def _map_sentiment(score: float) -> str:
    if score > 0.05:
        return "positive"
    if score < -0.05:
        return "negative"
    return "neutral"


def get_market_news(limit: int = 20) -> List[dict]:
    if not _require_key():
        return []

    # India-focused: aggregate stock news for NSE tickers in the default universe.
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)
    results = []
    for ticker in settings.default_tickers[:6]:
        articles = _call(
            "company-news",
            {
                "symbol": ticker.upper(),
                "from": start_date.isoformat(),
                "to": end_date.isoformat(),
            },
        )
        for item in articles[: max(1, limit // 6)]:
            results.append(
                {
                    "headline": item.get("headline", ""),
                    "summary": item.get("summary", ""),
                    "source": item.get("source", ""),
                    "date": _format_date(item.get("datetime", 0)),
                    "related_stocks": [ticker.upper()],
                    "sentiment": "neutral",
                    "category": "market",
                }
            )
    if results:
        return results[:limit]

    # Fallback: general market news if company news is unavailable.
    general_news = _call("news", {"category": "general"})
    for item in general_news[:limit]:
        results.append(
            {
                "headline": item.get("headline", ""),
                "summary": item.get("summary", ""),
                "source": item.get("source", ""),
                "date": _format_date(item.get("datetime", 0)),
                "related_stocks": [],
                "sentiment": "neutral",
                "category": item.get("category") or "market",
            }
        )
    return results[:limit]


def get_stock_news(ticker: str, limit: int = 20) -> List[dict]:
    if not _require_key():
        return []
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)

    articles = _call(
        "company-news",
        {
            "symbol": ticker.upper(),
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
        },
    )

    sentiment_score = 0.0
    try:
        sentiment = _call("news-sentiment", {"symbol": ticker.upper()})
        bullish = sentiment.get("sentiment", {}).get("bullishPercent", 0)
        bearish = sentiment.get("sentiment", {}).get("bearishPercent", 0)
        sentiment_score = (bullish - bearish) / 100.0
    except Exception:
        sentiment_score = 0.0

    mapped_sentiment = _map_sentiment(sentiment_score)

    results = []
    for item in articles[:limit]:
        results.append(
            {
                "headline": item.get("headline", ""),
                "summary": item.get("summary", ""),
                "source": item.get("source", ""),
                "date": _format_date(item.get("datetime", 0)),
                "related_stocks": [ticker.upper()],
                "sentiment": mapped_sentiment,
                "category": "stock",
            }
        )
    return results
