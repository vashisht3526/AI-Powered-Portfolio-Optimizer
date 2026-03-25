🚀 AI-Powered Dynamic Portfolio Optimizer

This project is an end-to-end AI-driven portfolio optimization system designed for the Indian stock market (NIFTY 50). It combines quantitative finance, backend engineering, and AI integration into a full-stack web application.

📌 Overview

The system fetches and maintains 10 years of historical NSE stock data, computes financial metrics using a configurable lookback window, and performs risk-adjusted portfolio optimization. It supports dynamic rebalancing, backtesting, and provides AI-powered portfolio insights.

⚙️ Features
📊 Historical data ingestion with automatic updates
📈 Expected return, volatility, covariance & correlation calculation
🧠 Risk-adjusted portfolio optimization (Sharpe-based)
🔁 Rolling backtesting with equity curve generation
📰 Market news integration (Finnhub API)
🤖 AI Assistant (Gemini API) for:
Portfolio risk explanation
Metric interpretation
News impact analysis
🌐 Interactive frontend dashboard (React + TypeScript)
🧠 Key Concepts
Modern Portfolio Theory
Sharpe Ratio Optimization
Rolling Lookback Windows
Rebalancing Strategy
Risk-Constrained Allocation
Backend–Frontend API Architecture
🛠 Tech Stack

Backend: Python, FastAPI, Pandas, NumPy
Frontend: React, TypeScript
Data: yFinance (NSE), CSV-based storage
AI Integration: Gemini API
News API: Finnhub
Visualization: Recharts
