
import React from 'react';
import DetailedChart from '../DetailedChart';

interface ChartModalContentProps {
  chartData: Array<{ name: string; value?: number; current?: number; previous?: number; [key: string]: any }>;
  chartColor?: string;
  chartColors?: {
    current: string;
    previous: string;
  };
  chartType: 'area' | 'bar';
  showComparison?: boolean;
  legendLabels?: {
    current: string;
    previous: string;
  };
}

const ChartModalContent: React.FC<ChartModalContentProps> = ({
  chartData,
  chartColor = "#0080ff",
  chartColors,
  chartType,
  showComparison = false,
  legendLabels = {
    current: "Current Period",
    previous: "Previous Period"
  }
}) => {
  return (
    <div className="h-[70vh] py-4">
      <DetailedChart 
        chartData={chartData}
        chartColor={chartColor}
        chartColors={chartColors}
        chartType={chartType}
        showComparison={showComparison}
        legendLabels={legendLabels}
      />
    </div>
  );
};

export default ChartModalContent;
