import { apiRequest } from "./client";

export interface NewsArticle {
  headline: string;
  summary: string;
  source: string;
  date: string;
  sentiment?: "positive" | "neutral" | "negative";
  category?: string;
  related_stocks?: string[];
}

export function getMarketNews() {
  return apiRequest<{ news: NewsArticle[] }>("/news/market");
}

export function getStockNews(ticker: string) {
  return apiRequest<{ news: NewsArticle[] }>(`/news/stock/${ticker}`);
}
