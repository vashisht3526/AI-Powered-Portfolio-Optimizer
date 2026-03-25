import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Separator } from "./ui/separator";

interface BacktestMetrics {
  cagr: number;
  sharpeRatio: number;
  winRate: number;
  totalReturn: number;
}

interface BacktestSummaryProps {
  metrics: BacktestMetrics;
}

export function BacktestSummary({ metrics }: BacktestSummaryProps) {
  return (
    <Card className="border-slate-200">
      <CardHeader>
        <CardTitle>Backtest Performance Summary</CardTitle>
        <CardDescription>Historical performance metrics based on simulation period</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <div className="space-y-1">
            <p className="text-xs text-slate-500 uppercase tracking-wide">CAGR</p>
            <p className="text-2xl font-semibold text-emerald-600">{metrics.cagr.toFixed(2)}%</p>
            <p className="text-xs text-slate-600">Compounded annual growth</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-slate-500 uppercase tracking-wide">Sharpe Ratio</p>
            <p className="text-2xl font-semibold text-blue-600">{metrics.sharpeRatio.toFixed(2)}</p>
            <p className="text-xs text-slate-600">Risk-adjusted performance</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-slate-500 uppercase tracking-wide">Win Rate</p>
            <p className="text-2xl font-semibold text-slate-700">{metrics.winRate.toFixed(1)}%</p>
            <p className="text-xs text-slate-600">Profitable periods</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-slate-500 uppercase tracking-wide">Total Return</p>
            <p className="text-2xl font-semibold text-emerald-600">{metrics.totalReturn.toFixed(1)}%</p>
            <p className="text-xs text-slate-600">Cumulative gain</p>
          </div>
        </div>
        <Separator className="my-4" />
        <div className="bg-slate-50 p-4 rounded-lg">
          <p className="text-sm text-slate-700 leading-relaxed">
            <span className="font-semibold">Analysis Overview:</span> The portfolio demonstrates
            strong risk-adjusted returns with a Sharpe ratio above 1.5, indicating efficient
            allocation. The CAGR reflects consistent compounding, while the win rate highlights
            stability across market regimes.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
