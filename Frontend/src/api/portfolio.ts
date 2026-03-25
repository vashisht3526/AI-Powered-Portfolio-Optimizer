import { apiRequest } from "./client";

export interface PortfolioMetrics {
  expectedReturn: number;
  volatility: number;
  sharpeRatio: number;
  maxDrawdown: number;
}

export interface Holding {
  ticker: string;
  name: string;
  weight: number;
}

export function getPortfolioMetrics(params: {
  tickers?: string[];
  lookbackDays?: number;
  maxWeight?: number;
  mode?: "system" | "user";
  rebalanceDate?: string;
}) {
  const query = new URLSearchParams();
  if (params.tickers?.length) query.set("tickers", params.tickers.join(","));
  if (params.lookbackDays) query.set("lookback_days", String(params.lookbackDays));
  if (params.maxWeight) query.set("max_weight", String(params.maxWeight));
  if (params.mode) query.set("mode", params.mode);
  if (params.rebalanceDate) query.set("rebalance_date", params.rebalanceDate);

  return apiRequest<{ metrics: PortfolioMetrics }>(`/portfolio/metrics?${query.toString()}`);
}

export function getPortfolioHoldings(params: {
  tickers?: string[];
  lookbackDays?: number;
  maxWeight?: number;
  mode?: "system" | "user";
}) {
  const query = new URLSearchParams();
  if (params.tickers?.length) query.set("tickers", params.tickers.join(","));
  if (params.lookbackDays) query.set("lookback_days", String(params.lookbackDays));
  if (params.maxWeight) query.set("max_weight", String(params.maxWeight));
  if (params.mode) query.set("mode", params.mode);

  return apiRequest<{ holdings: Holding[] }>(`/portfolio/holdings?${query.toString()}`);
}

export function optimizePortfolio(body: {
  tickers: string[];
  lookback_days?: number;
  max_weight?: number;
  risk_free_rate?: number;
}) {
  return apiRequest<{ holdings: Holding[]; metrics: PortfolioMetrics }>("/portfolio/optimize", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
