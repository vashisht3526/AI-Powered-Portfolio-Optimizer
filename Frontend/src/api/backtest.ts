import { apiRequest } from "./client";

export interface EquityPoint {
  date: string;
  value: number;
}

export interface BacktestSummary {
  cagr: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalReturn: number;
}

export function runBacktest(body: {
  tickers?: string[];
  lookback_days?: number;
  max_weight?: number;
  rebalance_frequency?: "M" | "Q";
  start_date?: string;
  end_date?: string;
}) {
  return apiRequest<{ equityCurve: EquityPoint[]; summary: BacktestSummary }>("/backtest/run", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getEquityCurve() {
  return apiRequest<{ equityCurve: EquityPoint[] }>("/backtest/equity-curve");
}

export function getBacktestSummary() {
  return apiRequest<BacktestSummary>("/backtest/summary");
}
