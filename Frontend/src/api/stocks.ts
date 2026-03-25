import { apiRequest } from "./client";

export interface StockSearchResult {
  ticker: string;
  name: string;
  sector?: string;
}

export interface StockMetrics {
  ticker: string;
  name: string;
  sector?: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  annualizedReturn: number;
  volatility: number;
  maxDrawdown: number;
  beta: number;
  correlationWithPortfolio: number;
}

export interface PriceHistoryPoint {
  date: string;
  price: number;
}

export function searchStocks(query: string) {
  return apiRequest<StockSearchResult[]>(
    `/stocks/search?q=${encodeURIComponent(query)}`
  );
}

export function getStockMetrics(ticker: string, portfolioTickers?: string[]) {
  const query = new URLSearchParams();
  if (portfolioTickers?.length) query.set("portfolio_tickers", portfolioTickers.join(","));
  return apiRequest<StockMetrics>(`/stocks/${ticker}/metrics?${query.toString()}`);
}

export function getPriceHistory(ticker: string, range: "1y" | "3y" | "5y") {
  return apiRequest<{ ticker: string; history: PriceHistoryPoint[] }>(
    `/stocks/${ticker}/price-history?range=${range}`
  );
}
