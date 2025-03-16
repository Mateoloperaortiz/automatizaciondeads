
import React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent } from '@/components/ui/card';
import ChartModal from '../ChartModal';
import { ChartProvider, useChartContext } from './ChartProvider';
import { AreaChartComponent } from './AreaChartComponent';
import { BarChartComponent } from './BarChartComponent';
import { ChartLegendComponent } from './ChartLegendComponent';

interface MetricsChartProps {
  data: Array<{
    name: string;
    value?: number;
    current?: number;
    previous?: number;
    [key: string]: any;
  }>;
  color?: string;
  colors?: {
    current: string;
    previous: string;
  };
  showGrid?: boolean;
  height?: number;
  className?: string;
  chartType?: 'area' | 'bar';
  title?: string;
  description?: string;
  showLegend?: boolean;
  isComparison?: boolean;
  legendLabels?: {
    current: string;
    previous: string;
  };
}

const MetricsChartContent: React.FC<MetricsChartProps> = ({
  data,
  color = "#0080ff",
  colors,
  showGrid = false,
  height = 120,
  className,
  chartType = 'area',
  title,
  description,
  showLegend = false,
  isComparison = false,
  legendLabels = {
    current: "Current",
    previous: "Previous"
  }
}) => {
  const { isExpanded, setIsExpanded } = useChartContext();
  
  // Determine if we're showing comparison data
  const showComparison = isComparison && colors;

  // Custom legend formatter for better readability
  const renderLegend = (props: any) => {
    return <ChartLegendComponent payload={props.payload} legendLabels={legendLabels} />;
  };

  return (
    <>
      <Card 
        className={cn(
          "w-full overflow-hidden", 
          className, 
          {
            "fixed inset-4 z-50 max-w-none": isExpanded
          }
        )}
        onClick={() => setIsExpanded(true)}
      >
        <CardContent 
          className={cn(
            "p-4 flex justify-center items-center", 
            {
              "pt-0": title || description
            }
          )}
        >
          <div 
            className={cn(
              "w-full", 
              {
                "h-[80vh]": isExpanded
              }
            )}
          >
            {chartType === 'area' ? (
              <AreaChartComponent
                data={data}
                color={color}
                colors={colors}
                showGrid={showGrid}
                height={height}
                showLegend={showLegend}
                isComparison={isComparison}
                legendLabels={legendLabels}
                renderLegend={renderLegend}
              />
            ) : (
              <BarChartComponent
                data={data}
                color={color}
                colors={colors}
                showGrid={showGrid}
                height={height}
                showLegend={showLegend}
                isComparison={isComparison}
                legendLabels={legendLabels}
                renderLegend={renderLegend}
              />
            )}
          </div>
        </CardContent>
      </Card>

      <ChartModal
        isOpen={isExpanded}
        onClose={() => setIsExpanded(false)}
        title={title || "Chart Detail"}
        description={description}
        chartData={data}
        chartColor={color}
        chartColors={colors}
        chartType={chartType}
        showComparison={isComparison}
        legendLabels={legendLabels}
      />
    </>
  );
};

export const MetricsChart: React.FC<MetricsChartProps> = (props) => {
  return (
    <ChartProvider>
      <MetricsChartContent {...props} />
    </ChartProvider>
  );
};

export default MetricsChart;
