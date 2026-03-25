import { TrendingUp, Activity, Target, TrendingDown } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: "positive" | "negative" | "neutral";
}

function MetricCard({ title, value, subtitle, icon, trend = "neutral" }: MetricCardProps) {
  const trendColor =
    trend === "positive" ? "text-emerald-600" : trend === "negative" ? "text-rose-600" : "text-slate-600";

  return (
    <Card className="border-slate-200">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-slate-600">{title}</CardTitle>
        <div className={`${trendColor}`}>{icon}</div>
      </CardHeader>
      <CardContent>
        <div className={`text-2xl font-semibold ${trendColor}`}>{value}</div>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      </CardContent>
    </Card>
  );
}

interface PortfolioMetricsCardsProps {
  metrics: {
    expectedReturn: number;
    volatility: number;
    sharpeRatio: number;
    maxDrawdown: number;
  };
}

export function PortfolioMetricsCards({ metrics }: PortfolioMetricsCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        title="Expected Monthly Return"
        value={`${metrics.expectedReturn.toFixed(2)}%`}
        subtitle="Projected average monthly return"
        icon={<TrendingUp className="h-5 w-5" />}
        trend={metrics.expectedReturn > 0 ? "positive" : "negative"}
      />
      <MetricCard
        title="Portfolio Volatility"
        value={`${metrics.volatility.toFixed(2)}%`}
        subtitle="Standard deviation of returns"
        icon={<Activity className="h-5 w-5" />}
        trend="neutral"
      />
      <MetricCard
        title="Sharpe Ratio"
        value={metrics.sharpeRatio.toFixed(2)}
        subtitle="Risk-adjusted return measure"
        icon={<Target className="h-5 w-5" />}
        trend={metrics.sharpeRatio > 1 ? "positive" : "neutral"}
      />
      <MetricCard
        title="Maximum Drawdown"
        value={`${metrics.maxDrawdown.toFixed(2)}%`}
        subtitle="Largest peak-to-trough decline"
        icon={<TrendingDown className="h-5 w-5" />}
        trend="negative"
      />
    </div>
  );
}
