import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { AlertCircle, Plus, Search, TrendingDown, TrendingUp, X } from "lucide-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";
import { getPortfolioHoldings, getPortfolioMetrics, optimizePortfolio } from "../../api/portfolio";
import { getStockMetrics, searchStocks } from "../../api/stocks";

interface Stock {
  ticker: string;
  name: string;
  expectedReturn: number;
  volatility: number;
  correlation: number;
}

interface StockSearchResult {
  ticker: string;
  name: string;
  sector?: string;
}

export function PortfolioBuilderPage() {
  const [isSystemMode, setIsSystemMode] = useState(true);
  const [selectedStocks, setSelectedStocks] = useState<Stock[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredStocks, setFilteredStocks] = useState<StockSearchResult[]>([]);
  const [portfolioMetrics, setPortfolioMetrics] = useState({
    expectedReturn: 0,
    volatility: 0,
    sharpeRatio: 0,
  });
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSearchChange = async (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      try {
        const results = await searchStocks(query);
        setFilteredStocks(results);
      } catch (error) {
        console.error(error);
        setFilteredStocks([]);
      }
    } else {
      setFilteredStocks([]);
    }
  };

  const refreshSelectedStocks = async (tickers: string[]) => {
    if (tickers.length === 0) {
      setSelectedStocks([]);
      return;
    }
    try {
      const metricsList = await Promise.all(
        tickers.map((ticker) => getStockMetrics(ticker, tickers))
      );
      const mapped = metricsList.map((metrics) => ({
        ticker: metrics.ticker,
        name: metrics.name,
        expectedReturn: metrics.annualizedReturn,
        volatility: metrics.volatility,
        correlation: metrics.correlationWithPortfolio,
      }));
      setSelectedStocks(mapped);
    } catch (error) {
      console.error(error);
      setErrorMessage("Unable to load stock metrics. Please try again.");
    }
  };

  const addStock = async (stock: StockSearchResult) => {
    if (!selectedStocks.find((s) => s.ticker === stock.ticker)) {
      try {
        const updatedTickers = [...selectedStocks.map((s) => s.ticker), stock.ticker];
        await refreshSelectedStocks(updatedTickers);
        await refreshPortfolioMetrics(updatedTickers);
      } catch (error) {
        console.error(error);
      }
    }
    setSearchQuery("");
    setFilteredStocks([]);
  };

  const removeStock = async (ticker: string) => {
    try {
      const updatedTickers = selectedStocks
        .filter((s) => s.ticker !== ticker)
        .map((s) => s.ticker);
      await refreshSelectedStocks(updatedTickers);
      await refreshPortfolioMetrics(updatedTickers);
    } catch (error) {
      console.error(error);
      setErrorMessage("Unable to update portfolio selection. Please try again.");
    }
  };

  const refreshPortfolioMetrics = async (tickers: string[]) => {
    if (tickers.length === 0) {
      setPortfolioMetrics({ expectedReturn: 0, volatility: 0, sharpeRatio: 0 });
      return;
    }
    setErrorMessage(null);
    try {
      const metrics = await getPortfolioMetrics({
        tickers,
        mode: isSystemMode ? "system" : "user",
      });
      setPortfolioMetrics({
        expectedReturn: metrics.metrics.expectedReturn * 12,
        volatility: metrics.metrics.volatility * Math.sqrt(12),
        sharpeRatio: metrics.metrics.sharpeRatio,
      });
    } catch (error) {
      console.error(error);
      setErrorMessage("Unable to load portfolio metrics. Please try again.");
    }
  };

  const loadSystemPortfolio = async () => {
    try {
      const holdings = await getPortfolioHoldings({ mode: "system" });
      const tickers = holdings.holdings.map((holding) => holding.ticker);
      if (tickers.length === 0) {
        setSelectedStocks([]);
        return;
      }
      await refreshSelectedStocks(tickers);
      await refreshPortfolioMetrics(tickers);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    if (isSystemMode) {
      loadSystemPortfolio();
    } else {
      refreshPortfolioMetrics(selectedStocks.map((s) => s.ticker));
    }
  }, [isSystemMode]);

  const portfolioReturn = portfolioMetrics.expectedReturn;
  const portfolioVolatility = portfolioMetrics.volatility;
  const sharpeRatio = portfolioMetrics.sharpeRatio;

  // Request optimized weights from the backend.
  const handleOptimize = async () => {
    if (selectedStocks.length === 0) {
      setErrorMessage("Please select at least one stock to optimize.");
      return;
    }
    setIsOptimizing(true);
    setErrorMessage(null);
    try {
      const response = await optimizePortfolio({
        tickers: selectedStocks.map((stock) => stock.ticker),
        lookback_days: 180,
        max_weight: 0.25,
      });
      await refreshSelectedStocks(response.holdings.map((holding) => holding.ticker));
      setPortfolioMetrics({
        expectedReturn: response.metrics.expectedReturn * 12,
        volatility: response.metrics.volatility * Math.sqrt(12),
        sharpeRatio: response.metrics.sharpeRatio,
      });
    } catch (error) {
      console.error(error);
      setErrorMessage("Optimization failed. Please ensure the backend is running.");
    } finally {
      setIsOptimizing(false);
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-slate-900">Portfolio Builder</h2>
        <p className="text-sm text-slate-600 mt-1">
          Construct your portfolio with system optimization or manual stock selection
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Portfolio Construction */}
        <div className="lg:col-span-2 space-y-6">
          {errorMessage && (
            <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {errorMessage}
            </div>
          )}
          {/* Mode Selection */}
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle>Portfolio Construction Mode</CardTitle>
              <CardDescription>
                Choose between system-optimized or manually selected portfolio
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Switch
                    checked={isSystemMode}
                    onCheckedChange={setIsSystemMode}
                    id="mode-switch"
                  />
                  <div>
                    <Label htmlFor="mode-switch" className="cursor-pointer">
                      {isSystemMode ? "System-Selected Portfolio" : "User-Selected Portfolio"}
                    </Label>
                    <p className="text-xs text-slate-600 mt-1">
                      {isSystemMode
                        ? "Algorithm automatically selects optimal stocks based on risk-return profile"
                        : "Manually search and add stocks to build your custom portfolio"}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stock Selection (User Mode Only) */}
          {!isSystemMode && (
            <Card className="border-slate-200">
              <CardHeader>
                <CardTitle>Add Stocks to Portfolio</CardTitle>
                <CardDescription>Search and select stocks to add to your portfolio</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                  <Input
                    placeholder="Search stocks by ticker or name (e.g., RELIANCE.NS, TCS)..."
                    value={searchQuery}
                    onChange={(e) => handleSearchChange(e.target.value)}
                    className="pl-10"
                  />
                </div>

                {/* Search Results */}
                {filteredStocks.length > 0 && (
                  <div className="mt-3 border border-slate-200 rounded-lg overflow-hidden max-h-64 overflow-y-auto">
                    {filteredStocks.map((stock) => (
                      <div
                        key={stock.ticker}
                        className="flex items-center justify-between p-3 hover:bg-slate-50 border-b border-slate-100 last:border-b-0 cursor-pointer"
                        onClick={() => addStock(stock)}
                      >
                        <div>
                          <p className="font-semibold text-slate-900">{stock.ticker}</p>
                          <p className="text-xs text-slate-600">{stock.name}</p>
                        </div>
                        <Button size="sm" variant="ghost">
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Selected Stocks */}
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle>Selected Stocks ({selectedStocks.length})</CardTitle>
              <CardDescription>
                {isSystemMode
                  ? "System-optimized stock selection based on efficient frontier"
                  : "Your manually selected portfolio holdings"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedStocks.length === 0 ? (
                <div className="text-center py-12 text-slate-500">
                  <AlertCircle className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No stocks selected. Add stocks to build your portfolio.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow className="hover:bg-transparent">
                      <TableHead>Ticker</TableHead>
                      <TableHead>Company Name</TableHead>
                      <TableHead className="text-right">Expected Return</TableHead>
                      <TableHead className="text-right">Volatility</TableHead>
                      <TableHead className="text-right">Correlation</TableHead>
                      {!isSystemMode && <TableHead className="text-right">Action</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {selectedStocks.map((stock) => (
                      <TableRow key={stock.ticker}>
                        <TableCell className="font-mono font-semibold">{stock.ticker}</TableCell>
                        <TableCell className="text-slate-700">{stock.name}</TableCell>
                        <TableCell className="text-right">
                          <span className="text-emerald-600 font-semibold">
                            {stock.expectedReturn.toFixed(1)}%
                          </span>
                        </TableCell>
                        <TableCell className="text-right text-slate-700">
                          {stock.volatility.toFixed(1)}%
                        </TableCell>
                        <TableCell className="text-right text-slate-700">
                          {stock.correlation.toFixed(2)}
                        </TableCell>
                        {!isSystemMode && (
                          <TableCell className="text-right">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => removeStock(stock.ticker)}
                              className="text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Portfolio Impact */}
        <div className="lg:col-span-1 space-y-6">
          <Card className="border-slate-200 sticky top-24">
            <CardHeader>
              <CardTitle>Portfolio Impact Analysis</CardTitle>
              <CardDescription>How your selection affects portfolio metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Metric Cards */}
              <div className="space-y-4">
                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-xs text-emerald-700 font-medium uppercase tracking-wide">
                      Expected Return
                    </p>
                    <TrendingUp className="h-4 w-4 text-emerald-600" />
                  </div>
                  <p className="text-2xl font-semibold text-emerald-700">
                    {portfolioReturn.toFixed(2)}%
                  </p>
                  <p className="text-xs text-emerald-600 mt-1">Annualized portfolio return</p>
                </div>

                <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-xs text-slate-700 font-medium uppercase tracking-wide">
                      Volatility
                    </p>
                    <TrendingDown className="h-4 w-4 text-slate-600" />
                  </div>
                  <p className="text-2xl font-semibold text-slate-700">
                    {portfolioVolatility.toFixed(2)}%
                  </p>
                  <p className="text-xs text-slate-600 mt-1">Portfolio risk measure</p>
                </div>

                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-xs text-blue-700 font-medium uppercase tracking-wide">
                      Sharpe Ratio
                    </p>
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                  </div>
                  <p className="text-2xl font-semibold text-blue-700">{sharpeRatio.toFixed(2)}</p>
                  <p className="text-xs text-blue-600 mt-1">Risk-adjusted return</p>
                </div>

                <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-xs text-amber-700 font-medium uppercase tracking-wide">
                      Diversification
                    </p>
                  </div>
                  <p className="text-2xl font-semibold text-amber-700">
                    {selectedStocks.length > 5 ? "Good" : "Moderate"}
                  </p>
                  <p className="text-xs text-amber-600 mt-1">
                    {selectedStocks.length} stocks in portfolio
                  </p>
                </div>
              </div>

              <Button
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                onClick={handleOptimize}
                disabled={isOptimizing}
              >
                {isOptimizing ? "Optimizing..." : "Optimize Weights"}
              </Button>

              <div className="pt-4 border-t border-slate-200">
                <p className="text-xs text-slate-500 leading-relaxed">
                  <span className="font-semibold">Analysis Note:</span> Metrics are calculated
                  based on historical data and correlation patterns. Portfolio optimization adjusts
                  weights to maximize Sharpe ratio.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
