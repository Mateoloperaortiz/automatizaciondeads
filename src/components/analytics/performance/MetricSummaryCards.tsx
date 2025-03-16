
import React from 'react';
import { ArrowUpRight } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface MetricSummaryCardsProps {
  latestValue: number | string;
  averageValue: number | string;
  totalValue: number | string;
  growth: number;
  unit?: string;
  showPercentInLatest?: boolean;
  isCurrency?: boolean;
  previousAverage?: number | string;
  trendValue?: number;
  showComparison?: boolean;
}

const MetricSummaryCards: React.FC<MetricSummaryCardsProps> = ({
  latestValue,
  averageValue,
  totalValue,
  growth,
  unit = '',
  showPercentInLatest = false,
  isCurrency = false,
  previousAverage,
  trendValue,
  showComparison = false,
}) => {
  return (
    <div className="grid grid-cols-3 gap-4">
      <Card className="p-4 border-l-4 border-l-purple-500">
        <div className="flex flex-col">
          <span className="text-sm text-muted-foreground">Latest</span>
          <span className="text-2xl font-bold">
            {isCurrency && '$'}
            {latestValue}
            {showPercentInLatest && '%'}
          </span>
          <div className="flex items-center mt-1 text-xs">
            <span className={growth >= 0 ? "text-green-500" : "text-red-500"}>
              {growth >= 0 ? "+" : ""}{growth}%
            </span>
            <ArrowUpRight className={`h-3 w-3 ml-1 ${growth >= 0 ? "text-green-500" : "text-red-500 transform rotate-90"}`} />
          </div>
        </div>
      </Card>
      
      <Card className="p-4">
        <div className="flex flex-col">
          <span className="text-sm text-muted-foreground">Average</span>
          <span className="text-2xl font-bold">
            {isCurrency && '$'}
            {averageValue}
            {unit}
          </span>
          <span className="text-xs text-muted-foreground mt-1">
            {showComparison ? `vs ${previousAverage}${unit} prev` : `per month`}
          </span>
        </div>
      </Card>
      
      {trendValue !== undefined ? (
        <Card className="p-4">
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">Trend</span>
            <span className="text-2xl font-bold">
              {trendValue > 0 ? "↗" : "↘"}
            </span>
            <span className="text-xs text-muted-foreground mt-1">
              {Math.abs(trendValue)}% change
            </span>
          </div>
        </Card>
      ) : (
        <Card className="p-4">
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">Total</span>
            <span className="text-2xl font-bold">
              {isCurrency && '$'}
              {totalValue}
            </span>
            <span className="text-xs text-muted-foreground mt-1">all campaigns</span>
          </div>
        </Card>
      )}
    </div>
  );
};

export default MetricSummaryCards;
