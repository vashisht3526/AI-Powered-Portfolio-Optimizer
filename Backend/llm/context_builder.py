def build_portfolio_context(
    weights,
    expected_return,
    volatility,
    sharpe,
    drawdown,
    news_summary
):
    context = f"""
PORTFOLIO SUMMARY
- Expected Monthly Return: {expected_return*100:.2f}%
- Volatility: {volatility*100:.2f}%
- Sharpe Ratio: {sharpe:.2f}
- Max Drawdown: {drawdown*100:.2f}%

TOP HOLDINGS
"""

    for stock, weight in weights.items():
        context += f"- {stock}: {weight*100:.2f}%\n"

    context += f"""

RECENT MARKET NEWS
{news_summary}

INSTRUCTIONS
You are a portfolio analysis assistant.
Explain risks, insights, and implications.
Do NOT give buy/sell instructions.
Do NOT predict prices.
Do NOT give financial advice.
"""

    return context
