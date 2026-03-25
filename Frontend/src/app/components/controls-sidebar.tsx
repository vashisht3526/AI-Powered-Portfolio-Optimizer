import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Slider } from "./ui/slider";
import { Button } from "./ui/button";
import { Calendar } from "./ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { CalendarIcon, Settings2, RefreshCw } from "lucide-react";
import { format } from "date-fns";

interface ControlsSidebarProps {
  lookbackWindow: number;
  maxWeight: number;
  rebalanceDate: Date;
  onLookbackChange: (value: number) => void;
  onMaxWeightChange: (value: number) => void;
  onRebalanceDateChange: (date: Date | undefined) => void;
  onRecalculate: () => void;
  isCalculating?: boolean;
}

export function ControlsSidebar({
  lookbackWindow,
  maxWeight,
  rebalanceDate,
  onLookbackChange,
  onMaxWeightChange,
  onRebalanceDateChange,
  onRecalculate,
  isCalculating = false,
}: ControlsSidebarProps) {
  return (
    <Card className="border-slate-200 h-fit sticky top-6">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Settings2 className="h-5 w-5 text-slate-600" />
          <CardTitle className="text-lg">Portfolio Controls</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Lookback Window Slider */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="lookback" className="text-sm">
              Lookback Window
            </Label>
            <span className="text-sm font-semibold text-slate-900">{lookbackWindow} days</span>
          </div>
          <Slider
            id="lookback"
            min={30}
            max={365}
            step={30}
            value={[lookbackWindow]}
            onValueChange={(value) => onLookbackChange(value[0])}
            className="w-full"
          />
          <p className="text-xs text-slate-500">Historical data period for calculations</p>
        </div>

        {/* Max Weight Slider */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="maxweight" className="text-sm">
              Max Weight per Stock
            </Label>
            <span className="text-sm font-semibold text-slate-900">{maxWeight}%</span>
          </div>
          <Slider
            id="maxweight"
            min={5}
            max={50}
            step={5}
            value={[maxWeight]}
            onValueChange={(value) => onMaxWeightChange(value[0])}
            className="w-full"
          />
          <p className="text-xs text-slate-500">Maximum allocation per individual asset</p>
        </div>

        {/* Rebalance Date Picker */}
        <div className="space-y-3">
          <Label className="text-sm">Rebalance Date</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className="w-full justify-start text-left font-normal border-slate-200"
              >
                <CalendarIcon className="mr-2 h-4 w-4 text-slate-500" />
                {rebalanceDate ? format(rebalanceDate, "PPP") : <span>Select date</span>}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={rebalanceDate}
                onSelect={onRebalanceDateChange}
                initialFocus
              />
            </PopoverContent>
          </Popover>
          <p className="text-xs text-slate-500">Date for portfolio rebalancing</p>
        </div>

        {/* Recalculate Button */}
        <Button
          onClick={onRecalculate}
          disabled={isCalculating}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white"
          size="lg"
        >
          {isCalculating ? (
            <>
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              Calculating...
            </>
          ) : (
            <>
              <RefreshCw className="mr-2 h-4 w-4" />
              Recalculate Portfolio
            </>
          )}
        </Button>

        <div className="pt-4 border-t border-slate-200">
          <p className="text-xs text-slate-500 leading-relaxed">
            Adjust parameters to optimize your portfolio based on different risk preferences and time horizons. Click recalculate to update all metrics and charts.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
