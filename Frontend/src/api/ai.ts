import { apiRequest } from "./client";
import type { NewsArticle } from "./news";
import type { PortfolioMetrics } from "./portfolio";

export interface AIChatPayload {
  question: string;
  portfolio?: PortfolioMetrics;
  news?: NewsArticle[];
  tickers?: string[];
}

export interface AIChatResponse {
  answer: string;
}

export function sendAiMessage(payload: AIChatPayload) {
  return apiRequest<AIChatResponse>("/ai/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
