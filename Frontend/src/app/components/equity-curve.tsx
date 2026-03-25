import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";

interface EquityPoint {
  date: string;
  value: number;
}

interface EquityCurveProps {
  data: EquityPoint[];
}

export function EquityCurve({ data }: EquityCurveProps) {
  return (
    <Card className="border-slate-200">
      <CardHeader>
        <CardTitle>Portfolio Equity Curve</CardTitle>
        <CardDescription>Historical portfolio value over time with drawdown periods</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="date"
              stroke="#64748b"
              style={{ fontSize: "12px" }}
              tickMargin={8}
            />
            <YAxis
              stroke="#64748b"
              style={{ fontSize: "12px" }}
              tickFormatter={(value) => `INR ${(value / 1000).toFixed(0)}k`}
              tickMargin={8}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                fontSize: "13px",
              }}
              formatter={(value: number) => [`INR ${value.toLocaleString()}`, "Portfolio Value"]}
              labelStyle={{ fontWeight: 600, marginBottom: "4px" }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#2563eb"
              strokeWidth={2}
              fill="url(#colorValue)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
