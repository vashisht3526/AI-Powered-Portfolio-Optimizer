import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Newspaper, TrendingUp, TrendingDown, Minus, Filter } from "lucide-react";
import { getMarketNews, getStockNews } from "../../api/news";

interface NewsArticle {
  id: string;
  headline: string;
  source: string;
  date: string;
  summary: string;
  sentiment: "positive" | "neutral" | "negative";
  category: "market" | "stock" | "sector";
  relatedStocks?: string[];
}

function SentimentBadge({ sentiment }: { sentiment: NewsArticle["sentiment"] }) {
  const config = {
    positive: {
      label: "Positive",
      className: "bg-emerald-100 text-emerald-700 border-emerald-200",
      icon: <TrendingUp className="h-3 w-3 mr-1" />,
    },
    neutral: {
      label: "Neutral",
      className: "bg-slate-100 text-slate-700 border-slate-200",
      icon: <Minus className="h-3 w-3 mr-1" />,
    },
    negative: {
      label: "Negative",
      className: "bg-rose-100 text-rose-700 border-rose-200",
      icon: <TrendingDown className="h-3 w-3 mr-1" />,
    },
  };

  const { label, className, icon } = config[sentiment];

  return (
    <Badge variant="outline" className={`${className} flex items-center w-fit`}>
      {icon}
      {label}
    </Badge>
  );
}

export function MarketNewsPage() {
  const [activeCategory, setActiveCategory] = useState<"all" | "market" | "stock" | "sector">("all");
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Fetch market + stock-specific news from the backend.
  useEffect(() => {
    const fetchNews = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const [market, stockA, stockM] = await Promise.allSettled([
          getMarketNews(),
          getStockNews("RELIANCE.NS"),
          getStockNews("TCS.NS"),
        ]);

        const articles: NewsArticle[] = [];

        if (market.status === "fulfilled") {
          market.value.news.forEach((item, index) => {
            articles.push({
              id: `market-${index}`,
              headline: item.headline,
              source: item.source,
              date: item.date,
              summary: item.summary,
              sentiment: item.sentiment || "neutral",
              category: (item.category as NewsArticle["category"]) || "market",
              relatedStocks: item.related_stocks || [],
            });
          });
        }

        const stockResults = [stockA, stockM];
        stockResults.forEach((result, batchIndex) => {
          if (result.status === "fulfilled") {
            result.value.news.forEach((item, index) => {
              articles.push({
                id: `stock-${batchIndex}-${index}`,
                headline: item.headline,
                source: item.source,
                date: item.date,
                summary: item.summary,
                sentiment: item.sentiment || "neutral",
                category: (item.category as NewsArticle["category"]) || "stock",
                relatedStocks: item.related_stocks || [],
              });
            });
          }
        });

        setNewsArticles(articles);
      } catch (error) {
        console.error(error);
        setNewsArticles([]);
        setErrorMessage("Unable to load news. Please ensure the backend is running.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchNews();
  }, []);

  const filteredNews =
    activeCategory === "all"
      ? newsArticles
      : newsArticles.filter((article) => article.category === activeCategory);

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-slate-900">Market Intelligence & News</h2>
        <p className="text-sm text-slate-600 mt-1">
          Stay informed with latest financial news and AI-generated market analysis
        </p>
        {errorMessage && (
          <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {errorMessage}
          </div>
        )}
      </div>

      {/* Category Filter */}
      <Card className="border-slate-200 mb-6">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-slate-600" />
            <CardTitle className="text-lg">Filter News</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={activeCategory} onValueChange={(v) => setActiveCategory(v as any)}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">All News</TabsTrigger>
              <TabsTrigger value="market">Market-Wide</TabsTrigger>
              <TabsTrigger value="stock">Stock-Specific</TabsTrigger>
              <TabsTrigger value="sector">Sector News</TabsTrigger>
            </TabsList>
          </Tabs>
        </CardContent>
      </Card>

      {/* News Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {isLoading && (
          <Card className="border-slate-200">
            <CardContent className="p-6">
              <p className="text-sm text-slate-600">Loading latest news...</p>
            </CardContent>
          </Card>
        )}

        {!isLoading && filteredNews.length === 0 && (
          <Card className="border-slate-200">
            <CardContent className="p-6">
              <p className="text-sm text-slate-600">
                No news available for this category. If you are running locally, make sure
                `FINNHUB_API_KEY` is set in `Backend/.env`.
              </p>
            </CardContent>
          </Card>
        )}

        {filteredNews.map((article) => (
          <Card
            key={article.id}
            className="border-slate-200 hover:border-slate-300 transition-all hover:shadow-md"
          >
            <CardHeader>
              <div className="flex items-start justify-between gap-3 mb-2">
                <CardTitle className="text-lg leading-snug line-clamp-2">
                  {article.headline}
                </CardTitle>
                <Newspaper className="h-5 w-5 text-slate-400 flex-shrink-0" />
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <span className="font-medium">{article.source}</span>
                <span>-</span>
                <span>{article.date}</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-slate-700 leading-relaxed">{article.summary}</p>

              <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                <SentimentBadge sentiment={article.sentiment} />
                {article.relatedStocks && article.relatedStocks.length > 0 && (
                  <div className="flex gap-1.5">
                    {article.relatedStocks.map((ticker) => (
                      <Badge key={ticker} variant="outline" className="text-xs font-mono">
                        {ticker}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Disclaimer */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="p-6">
          <div className="flex items-start gap-3">
            <Newspaper className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-blue-900 mb-2">
                Informational Purpose Only
              </p>
              <p className="text-xs text-blue-800 leading-relaxed">
                News sentiment analysis is provided for informational and educational purposes only.
                It should not be used as the sole basis for investment decisions. AI-generated
                summaries are meant to assist with information processing but may not capture all
                nuances. Always conduct thorough research, consider multiple sources, and consult
                with qualified financial professionals before making investment decisions. Past
                performance and current news do not guarantee future results.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
