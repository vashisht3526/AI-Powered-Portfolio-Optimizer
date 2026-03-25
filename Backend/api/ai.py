from __future__ import annotations

from fastapi import APIRouter, HTTPException
import numpy as np

from config import settings
from models.schemas import AIChatRequest, AIChatResponse
from services import data_service, metrics_service, optimization_service, news_service
from llm.chatbot import ask_chatbot
from llm.context_builder import build_portfolio_context
from utils.helpers import to_percent


router = APIRouter()


@router.post("/chat", response_model=AIChatResponse)
def chat(request: AIChatRequest):
    question = request.question or request.message
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    tickers = request.tickers or settings.default_tickers

    try:
        prices = data_service.get_prices_frame(tickers)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    returns = metrics_service.compute_daily_returns(prices)
    if returns.empty:
        raise HTTPException(status_code=400, detail="Not enough return history")

    optimization = optimization_service.optimize_portfolio(
        returns.tail(settings.lookback_days),
        max_weight=settings.max_weight,
        risk_free_rate=settings.risk_free_rate,
        lookback_days=settings.lookback_days,
    )
    weights = optimization.get("weights", np.array([]))
    tickers_used = optimization.get("tickers", list(returns.columns))
    if len(weights) == 0:
        weights = np.array([1.0 / len(tickers_used)] * len(tickers_used))

    metrics = metrics_service.compute_portfolio_metrics(returns.tail(settings.lookback_days), weights, settings.risk_free_rate)

    holdings = []
    for ticker, weight in zip(tickers_used, weights):
        profile = data_service.get_ticker_profile(ticker)
        holdings.append(
            {
                "ticker": ticker,
                "name": profile.get("name", ticker),
                "weight": float(weight) * 100.0,
            }
        )

    # Fetch a small set of recent news for context
    news_items = []
    try:
        for ticker in tickers_used[:3]:
            news_items.extend(news_service.get_stock_news(ticker, limit=2))
    except Exception:
        news_items = []

    news_summary = "No news summary available."
    if news_items:
        news_summary = "\n".join([f"- {item['headline']}" for item in news_items])

    context = build_portfolio_context(
        weights={h["ticker"]: h["weight"] for h in holdings},
        expected_return=metrics["expected_return"],
        volatility=metrics["volatility"],
        sharpe=metrics["sharpe"],
        drawdown=metrics["max_drawdown"],
        news_summary=news_summary,
    )

    try:
        reply = ask_chatbot(context, question)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return AIChatResponse(answer=reply, context=context)
