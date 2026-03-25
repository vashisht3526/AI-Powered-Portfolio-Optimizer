import time

import numpy as np
import pandas as pd
import yfinance as yf
from pypfopt import EfficientFrontier

# -----------------------------------
# NIFTY 50 SYMBOLS (Yahoo format)
# -----------------------------------
NIFTY50_SYMBOLS = [
    "ADANIENT.NS","ADANIPORTS.NS","APOLLOHOSP.NS","ASIANPAINT.NS","AXISBANK.NS",
    "BAJAJ-AUTO.NS","BAJFINANCE.NS","BAJAJFINSV.NS","BEL.NS","BHARTIARTL.NS",
    "CIPLA.NS","COALINDIA.NS","DRREDDY.NS","EICHERMOT.NS","ETERNAL.NS",
    "GRASIM.NS","HCLTECH.NS","HDFCBANK.NS","HDFCLIFE.NS","HINDALCO.NS",
    "HINDUNILVR.NS","ICICIBANK.NS","ITC.NS","INFY.NS","INDIGO.NS",
    "JSWSTEEL.NS","JIOFIN.NS","KOTAKBANK.NS","LT.NS","M&M.NS",
    "MARUTI.NS","MAXHEALTH.NS","NTPC.NS","NESTLEIND.NS","ONGC.NS",
    "POWERGRID.NS","RELIANCE.NS","SBILIFE.NS","SHRIRAMFIN.NS","SBIN.NS",
    "SUNPHARMA.NS","TCS.NS","TATACONSUM.NS","TMPV.NS","TATASTEEL.NS",
    "TECHM.NS","TITAN.NS","TRENT.NS","ULTRACEMCO.NS","WIPRO.NS"
]

CLOSE_PRICES_CSV = "nifty50_close_prices_10y.csv"
DAILY_RETURNS_CSV = "nifty50_daily_returns.csv"
EXPECTED_RETURNS_CSV = "expected_monthly_returns.csv"
COV_MATRIX_CSV = "covariance_matrix.csv"
WEIGHTS_CSV = "optimized_portfolio_weights.csv"

# -----------------------------------
# Fetch 10Y close prices (Yahoo)
# -----------------------------------
close_df = pd.DataFrame()

for ticker in NIFTY50_SYMBOLS:
    print(f"Fetching {ticker}")
    try:
        df = yf.download(
            ticker,
            period="10y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False
        )

        if not df.empty:
            close_df[ticker.replace(".NS", "")] = df["Close"]
            print(f"  Rows: {len(df)}")

    except Exception as e:
        print(f"Failed {ticker}: {e}")

    time.sleep(1)

close_df.to_csv(CLOSE_PRICES_CSV)
print(f"Saved: {CLOSE_PRICES_CSV}")

# -----------------------------
# Calculate daily returns
# -----------------------------
close_df = pd.read_csv(
    CLOSE_PRICES_CSV,
    index_col=0,
    parse_dates=True
)

returns_df = close_df.pct_change()

# -----------------------------
# Save returns
# -----------------------------
returns_df.to_csv(DAILY_RETURNS_CSV)
print(f"Saved: {DAILY_RETURNS_CSV}")

# -----------------------------
# Expected monthly returns
# -----------------------------
ROLLING_WINDOW = 60
MONTH_DAYS = 21

returns_df = pd.read_csv(
    DAILY_RETURNS_CSV,
    index_col=0,
    parse_dates=True
)

rolling_mean = returns_df.rolling(window=ROLLING_WINDOW).mean()
expected_monthly_return = rolling_mean.iloc[-1] * MONTH_DAYS
expected_monthly_return = expected_monthly_return.dropna()

expected_monthly_return_df = expected_monthly_return.to_frame(
    name="Expected_1M_Return"
)

expected_monthly_return_df.to_csv(EXPECTED_RETURNS_CSV)

print(f"Saved: {EXPECTED_RETURNS_CSV}")
print("\nTop 10 expected returns:")
print(
    expected_monthly_return_df.sort_values(
        by="Expected_1M_Return",
        ascending=False
    ).head(10)
)

# -----------------------------
# Covariance matrix
# -----------------------------
COV_WINDOW = 60

returns_df = pd.read_csv(
    DAILY_RETURNS_CSV,
    index_col=0,
    parse_dates=True
)

recent_returns = returns_df.tail(COV_WINDOW)
recent_returns = recent_returns.dropna(axis=1)

cov_matrix = recent_returns.cov()

cov_matrix.to_csv(COV_MATRIX_CSV)
print(f"Saved: {COV_MATRIX_CSV}")
print("Covariance matrix shape:", cov_matrix.shape)

# -----------------------------
# Optimize portfolio (Max Sharpe)
# -----------------------------
exp_ret_df = pd.read_csv(
    EXPECTED_RETURNS_CSV,
    index_col=0
)

expected_returns_series = exp_ret_df["Expected_1M_Return"]

cov_matrix = pd.read_csv(
    COV_MATRIX_CSV,
    index_col=0
)

common_assets = expected_returns_series.index.intersection(cov_matrix.index)
expected_returns_series = expected_returns_series.loc[common_assets]
cov_matrix = cov_matrix.loc[common_assets, common_assets]

ef = EfficientFrontier(expected_returns_series, cov_matrix)
weights = ef.max_sharpe(risk_free_rate=0.0)
cleaned_weights = ef.clean_weights()

expected_return, volatility, sharpe = ef.portfolio_performance(
    risk_free_rate=0.0,
    verbose=False
)

volatility = volatility * (21 ** 0.5)
sharpe = expected_return / volatility

weights_df = pd.DataFrame.from_dict(
    cleaned_weights,
    orient="index",
    columns=["Weight"]
)

weights_df.to_csv(WEIGHTS_CSV)

print("Optimized Portfolio Weights:")
print(
    weights_df[weights_df["Weight"] > 0].sort_values(
        by="Weight",
        ascending=False
    )
)

print("\nPortfolio Performance:")
print(f"Expected Return (1M): {expected_return:.4f}")
print(f"Volatility (1M): {volatility:.4f}")
print(f"Sharpe Ratio: {sharpe:.4f}")

# -----------------------------
# Walk-forward backtest
# -----------------------------
prices = pd.read_csv(
    CLOSE_PRICES_CSV,
    index_col=0,
    parse_dates=True
)
returns = prices.pct_change(fill_method=None)

month_ends = returns.resample("ME").last().index
portfolio_returns = []

for i in range(len(month_ends) - 1):
    rebalance_date = month_ends[i]
    next_rebalance = month_ends[i + 1]

    hist_returns = returns.loc[:rebalance_date].tail(80)
    hist_returns = hist_returns.dropna(axis=1)

    if hist_returns.shape[1] < 5:
        continue

    exp_returns = hist_returns.mean() * MONTH_DAYS
    cov_matrix = hist_returns.cov()

    ef = EfficientFrontier(exp_returns, cov_matrix)
    ef.add_constraint(lambda w: w <= 0.30)

    weights = ef.max_sharpe()
    weights = pd.Series(ef.clean_weights())

    future_returns = returns.loc[rebalance_date:next_rebalance, weights.index]
    future_returns = future_returns.dropna()

    port_ret = (future_returns @ weights).sum()
    portfolio_returns.append(port_ret)

portfolio_returns = pd.Series(portfolio_returns)
equity_curve = (1 + portfolio_returns).cumprod()

sharpe = portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(12)
cagr = equity_curve.iloc[-1] ** (12 / len(equity_curve)) - 1
max_dd = (equity_curve / equity_curve.cummax() - 1).min()

print("Backtest Results")
print("----------------")
print(f"CAGR: {cagr:.2%}")
print(f"Sharpe Ratio: {sharpe:.2f}")
print(f"Max Drawdown: {max_dd:.2%}")

# -----------------------------
# Plot equity curve
# -----------------------------
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))
plt.plot(equity_curve, linewidth=2)
plt.title("Equity Curve - Dynamic Portfolio Strategy")
plt.xlabel("Time (Months)")
plt.ylabel("Portfolio Value")
plt.grid(True)
plt.show()
