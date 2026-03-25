import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";

interface Holding {
  ticker: string;
  name: string;
  weight: number;
}

interface PortfolioTableProps {
  holdings: Holding[];
}

export function PortfolioTable({ holdings }: PortfolioTableProps) {
  // Sort by weight descending
  const sortedHoldings = [...holdings].sort((a, b) => b.weight - a.weight);

  return (
    <Card className="border-slate-200">
      <CardHeader>
        <CardTitle>Optimized Portfolio</CardTitle>
        <CardDescription>Asset allocation based on risk-return optimization</CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="font-semibold">Ticker</TableHead>
              <TableHead className="font-semibold">Company Name</TableHead>
              <TableHead className="text-right font-semibold">Portfolio Weight (%)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedHoldings.map((holding) => (
              <TableRow key={holding.ticker}>
                <TableCell className="font-mono font-medium text-slate-900">{holding.ticker}</TableCell>
                <TableCell className="text-slate-700">{holding.name}</TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div className="w-24 bg-slate-100 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-blue-600 h-full rounded-full transition-all"
                        style={{ width: `${holding.weight}%` }}
                      />
                    </div>
                    <span className="font-semibold text-slate-900 w-12 text-right">
                      {holding.weight.toFixed(1)}%
                    </span>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
