import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Search, TrendingUp, TrendingDown, Activity, BarChart3, AlertCircle } from "lucide-react";
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import { getPriceHistory, getStockMetrics, searchStocks } from "../../api/stocks";

interface StockData {
  ticker: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  annualizedReturn: number;
  volatility: number;
  maxDrawdown: number;
  beta: number;
  correlationWithPortfolio: number;
  sector: string;
}

interface StockSearchResult {
  ticker: string;
  name: string;
  sector?: string;
}

export function StockExplorerPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStock, setSelectedStock] = useState<StockData | null>(null);
  const [timeRange, setTimeRange] = useState<"1Y" | "3Y" | "5Y">("1Y");
  const [filteredStocks, setFilteredStocks] = useState<StockSearchResult[]>([]);
  const [priceData, setPriceData] = useState<{ date: string; price: number }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      try {
        const results = await searchStocks(query);
        setFilteredStocks(results);
      } catch (error) {
        console.error(error);
        setFilteredStocks([]);
        setErrorMessage("Unable to search stocks. Please try again.");
      }
    } else {
      setFilteredStocks([]);
    }
  };

  const selectStock = async (stock: StockSearchResult) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const metrics = await getStockMetrics(stock.ticker);
      setSelectedStock({
        ...metrics,
        sector: metrics.sector || stock.sector || "Unknown",
      });
    } catch (error) {
      console.error(error);
      setSelectedStock(null);
      setErrorMessage("Unable to load stock metrics. Please try again.");
    }
    setIsLoading(false);
    setSearchQuery("");
    setFilteredStocks([]);
  };

  // Fetch price history for the selected NSE stock.
  useEffect(() => {
    const fetchHistory = async () => {
      if (!selectedStock) {
        setPriceData([]);
        return;
      }
      const range = timeRange.toLowerCase() as "1y" | "3y" | "5y";
      try {
        const history = await getPriceHistory(selectedStock.ticker, range);
        setPriceData(history.history);
      } catch (error) {
        console.error(error);
        setPriceData([]);
        setErrorMessage("Unable to load price history. Please try again.");
      }
    };

    fetchHistory();
  }, [selectedStock?.ticker, timeRange]);

  return (
    <div className="max-w-[1600px] mx-auto px-6 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-slate-900">Stock Explorer</h2>
        <p className="text-sm text-slate-600 mt-1">
          Search and analyze individual stocks with detailed metrics and performance charts
        </p>
        {errorMessage && (
          <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {errorMessage}
          </div>
        )}
      </div>

      {/* Search Section */}
      <Card className="border-slate-200 mb-6">
        <CardHeader>
          <CardTitle>Stock Search</CardTitle>
          <CardDescription>Search for any stock to view detailed analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
            <Input
              placeholder="Search by ticker symbol or company name (e.g., RELIANCE.NS, TCS)..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10 text-base"
            />
          </div>

          {/* Search Results Dropdown */}
          {filteredStocks.length > 0 && (
            <div className="mt-3 border border-slate-200 rounded-lg overflow-hidden">
              {filteredStocks.map((stock) => (
                <div
                  key={stock.ticker}
                  className="flex items-center justify-between p-4 hover:bg-slate-50 border-b border-slate-100 last:border-b-0 cursor-pointer transition-colors"
                  onClick={() => selectStock(stock)}
                >
                  <div className="flex items-center gap-4">
                    <div>
                      <p className="font-semibold text-lg text-slate-900">{stock.ticker}</p>
                      <p className="text-sm text-slate-600">{stock.name}</p>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {stock.sector || "N/A"}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-500">View metrics</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Stock Analysis */}
      {isLoading && (
        <Card className="border-slate-200">
          <CardContent className="py-12 text-center text-slate-500">
            Loading stock data...
          </CardContent>
        </Card>
      )}

      {!isLoading && selectedStock ? (
        <div className="space-y-6">
          {/* Stock Overview */}
          <Card className="border-slate-200">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <CardTitle className="text-2xl">{selectedStock.ticker}</CardTitle>
                    <Badge>{selectedStock.sector}</Badge>
                  </div>
                  <CardDescription className="mt-2 text-base">
                    {selectedStock.name}
                  </CardDescription>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-semibold text-slate-900">
                    INR {selectedStock.currentPrice.toFixed(2)}
                  </p>
                  <div
                    className={`flex items-center gap-1 justify-end mt-1 ${
                      selectedStock.changePercent >= 0 ? "text-emerald-600" : "text-rose-600"
                    }`}
                  >
                    {selectedStock.changePercent >= 0 ? (
                      <TrendingUp className="h-4 w-4" />
                    ) : (
                      <TrendingDown className="h-4 w-4" />
                    )}
                    <span className="font-semibold">
                      {selectedStock.changePercent >= 0 ? "+" : ""}
                      {selectedStock.change.toFixed(2)} (
                      {selectedStock.changePercent.toFixed(2)}%)
                    </span>
                  </div>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Stock Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="border-slate-200">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-slate-600 uppercase tracking-wide">
                    Annualized Return
                  </p>
                  <TrendingUp className="h-4 w-4 text-emerald-600" />
                </div>
                <p className="text-2xl font-semibold text-emerald-600">
                  {selectedStock.annualizedReturn.toFixed(1)}%
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-slate-600 uppercase tracking-wide">Volatility</p>
                  <Activity className="h-4 w-4 text-slate-600" />
                </div>
                <p className="text-2xl font-semibold text-slate-700">
                  {selectedStock.volatility.toFixed(1)}%
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-slate-600 uppercase tracking-wide">Max Drawdown</p>
                  <TrendingDown className="h-4 w-4 text-rose-600" />
                </div>
                <p className="text-2xl font-semibold text-rose-600">
                  {selectedStock.maxDrawdown.toFixed(1)}%
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-slate-600 uppercase tracking-wide">Beta</p>
                  <BarChart3 className="h-4 w-4 text-blue-600" />
                </div>
                <p className="text-2xl font-semibold text-blue-600">
                  {selectedStock.beta.toFixed(2)}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Price Chart */}
          <Card className="border-slate-200">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Price Performance</CardTitle>
                  <CardDescription>Historical price movement over selected period</CardDescription>
                </div>
                <div className="flex gap-2">
                  {(["1Y", "3Y", "5Y"] as const).map((range) => (
                    <Button
                      key={range}
                      size="sm"
                      variant={timeRange === range ? "default" : "outline"}
                      onClick={() => setTimeRange(range)}
                      className={
                        timeRange === range
                          ? "bg-blue-600 text-white"
                          : "text-slate-700 hover:bg-slate-100"
                      }
                    >
                      {range}
                    </Button>
                  ))}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={priceData}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" stroke="#64748b" style={{ fontSize: "12px" }} />
                  <YAxis stroke="#64748b" style={{ fontSize: "12px" }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "white",
                      border: "1px solid #e2e8f0",
                      borderRadius: "8px",
                    }}
                    formatter={(value: number) => [`INR ${value.toFixed(2)}`, "Price"]}
                  />
                  <Area
                    type="monotone"
                    dataKey="price"
                    stroke="#2563eb"
                    strokeWidth={2}
                    fill="url(#colorPrice)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Portfolio Impact Analysis */}
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle>Portfolio Impact Analysis</CardTitle>
              <CardDescription>
                How adding this stock would affect your current portfolio
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm font-medium text-blue-900 mb-2">
                    Correlation with Portfolio
                  </p>
                  <p className="text-3xl font-semibold text-blue-700">
                    {selectedStock.correlationWithPortfolio.toFixed(2)}
                  </p>
                  <p className="text-xs text-blue-600 mt-2">
                    {selectedStock.correlationWithPortfolio > 0.7
                      ? "High correlation - may not improve diversification significantly"
                      : selectedStock.correlationWithPortfolio > 0.4
                      ? "Moderate correlation - reasonable diversification benefit"
                      : "Low correlation - excellent diversification opportunity"}
                  </p>
                </div>

                <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                  <p className="text-sm font-medium text-slate-900 mb-2">
                    Risk Contribution Impact
                  </p>
                  <div className="flex items-baseline gap-2">
                    <p className="text-3xl font-semibold text-slate-700">
                      {selectedStock.volatility > 20 ? "High" : "Moderate"}
                    </p>
                  </div>
                  <p className="text-xs text-slate-600 mt-2">
                    Adding this stock would{" "}
                    {selectedStock.volatility > 20 ? "increase" : "moderately affect"} portfolio
                    volatility
                  </p>
                </div>
              </div>

              <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-amber-900">Analysis Insight</p>
                    <p className="text-xs text-amber-700 mt-1 leading-relaxed">
                      Based on historical data, adding {selectedStock.ticker} to your portfolio
                      would contribute approximately {selectedStock.volatility.toFixed(1)}% to
                      overall volatility. The correlation of{" "}
                      {selectedStock.correlationWithPortfolio.toFixed(2)} suggests{" "}
                      {selectedStock.correlationWithPortfolio > 0.7
                        ? "limited diversification benefits"
                        : "meaningful diversification potential"}
                      .
                    </p>
                  </div>
                </div>
              </div>

              <Button className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white">
                Add to Portfolio Builder
              </Button>
            </CardContent>
          </Card>
        </div>
      ) : !isLoading ? (
        <Card className="border-slate-200">
          <CardContent className="py-24 text-center">
            <Search className="h-16 w-16 mx-auto text-slate-300 mb-4" />
            <h3 className="text-lg font-semibold text-slate-700 mb-2">No Stock Selected</h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              Use the search bar above to find and analyze individual stocks. View detailed metrics,
              performance charts, and portfolio impact analysis.
            </p>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
