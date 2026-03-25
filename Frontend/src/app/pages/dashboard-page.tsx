import { useEffect, useState } from "react";
import { PortfolioMetricsCards } from "../components/portfolio-metrics-cards";
import { PortfolioTable } from "../components/portfolio-table";
import { EquityCurve } from "../components/equity-curve";
import { BacktestSummary } from "../components/backtest-summary";
import { ControlsSidebar } from "../components/controls-sidebar";
import { getPortfolioHoldings, getPortfolioMetrics } from "../../api/portfolio";
import { getBacktestSummary, getEquityCurve, runBacktest } from "../../api/backtest";

const emptyMetrics = {
  expectedReturn: 0,
  volatility: 0,
  sharpeRatio: 0,
  maxDrawdown: 0,
};

const emptyBacktest = {
  cagr: 0,
  sharpeRatio: 0,
  maxDrawdown: 0,
  winRate: 0,
  totalReturn: 0,
};

export function DashboardPage() {
  const [lookbackWindow, setLookbackWindow] = useState(180);
  const [maxWeight, setMaxWeight] = useState(20);
  const [rebalanceDate, setRebalanceDate] = useState<Date>(new Date());
  const [isCalculating, setIsCalculating] = useState(false);
  const [portfolioMetrics, setPortfolioMetrics] = useState(emptyMetrics);
  const [holdings, setHoldings] = useState<{ ticker: string; name: string; weight: number }[]>(
    []
  );
  const [equityCurve, setEquityCurve] = useState<{ date: string; value: number }[]>([]);
  const [backtestMetrics, setBacktestMetrics] = useState(emptyBacktest);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load portfolio analytics from the backend API.
  const fetchDashboardData = async () => {
    setIsCalculating(true);
    setErrorMessage(null);
    try {
      await runBacktest({
        lookback_days: lookbackWindow,
        max_weight: maxWeight / 100,
        rebalance_frequency: "M",
      });

      const [metricsRes, holdingsRes, equityRes, summaryRes] = await Promise.all([
        getPortfolioMetrics({
          lookbackDays: lookbackWindow,
          maxWeight: maxWeight / 100,
          mode: "system",
          rebalanceDate: rebalanceDate.toISOString().split("T")[0],
        }),
        getPortfolioHoldings({
          lookbackDays: lookbackWindow,
          maxWeight: maxWeight / 100,
          mode: "system",
        }),
        getEquityCurve(),
        getBacktestSummary(),
      ]);

      setPortfolioMetrics(metricsRes.metrics);
      setHoldings(holdingsRes.holdings);
      setEquityCurve(equityRes.equityCurve);
      setBacktestMetrics(summaryRes);
    } catch (error) {
      console.error(error);
      setErrorMessage("Unable to load portfolio data. Please ensure the backend is running.");
    } finally {
      setIsCalculating(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleRecalculate = () => {
    fetchDashboardData();
  };

  return (
    <div className="max-w-[1600px] mx-auto px-6 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-slate-900">Portfolio Overview</h2>
        <p className="text-sm text-slate-600 mt-1">
          Comprehensive analysis of your optimized portfolio performance and risk metrics
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <ControlsSidebar
            lookbackWindow={lookbackWindow}
            maxWeight={maxWeight}
            rebalanceDate={rebalanceDate}
            onLookbackChange={setLookbackWindow}
            onMaxWeightChange={setMaxWeight}
            onRebalanceDateChange={(date) => date && setRebalanceDate(date)}
            onRecalculate={handleRecalculate}
            isCalculating={isCalculating}
          />
        </div>

        {/* Main Dashboard */}
        <div className="lg:col-span-3 space-y-6">
          {errorMessage && (
            <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {errorMessage}
            </div>
          )}
          <PortfolioMetricsCards metrics={portfolioMetrics} />
          <PortfolioTable holdings={holdings} />
          <EquityCurve data={equityCurve} />
          <BacktestSummary metrics={backtestMetrics} />
        </div>
      </div>
    </div>
  );
}
