
import React from 'react';
import { InfoIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import DashboardCard from '@/components/dashboard/DashboardCard';
import { MetricsChart } from '@/components/dashboard/metrics/MetricsChart';
import { useIsMobile } from '@/hooks/use-mobile';

interface PerformanceChartProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  accentColor: string;
  tooltipContent: string;
  chartData: any[];
  comparisonData?: any[];
  showComparison: boolean;
  chartType?: 'area' | 'bar';
  currentColor: string;
  previousColor: string;
  legendLabels?: {
    current: string;
    previous: string;
  };
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({
  title,
  description,
  icon,
  accentColor,
  tooltipContent,
  chartData,
  comparisonData,
  showComparison,
  chartType = 'area',
  currentColor,
  previousColor,
  legendLabels = {
    current: "Current Period",
    previous: "Previous Period"
  }
}) => {
  const isMobile = useIsMobile();
  
  return (
    <DashboardCard 
      title={title} 
      description={description} 
      icon={icon}
      className="hover-lift"
      accentColor={accentColor}
      headerClassName="pb-2"
      footer={
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <InfoIcon className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>{tooltipContent}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      }
    >
      {showComparison && comparisonData ? (
        <MetricsChart 
          data={comparisonData} 
          colors={{
            current: currentColor,
            previous: previousColor
          }}
          showGrid 
          height={isMobile ? 220 : 280}
          chartType={chartType}
          title={title}
          description={description}
          showLegend={true}
          isComparison={true}
          legendLabels={legendLabels}
        />
      ) : (
        <MetricsChart 
          data={chartData} 
          color={currentColor} 
          showGrid 
          height={isMobile ? 220 : 280}
          chartType={chartType}
          title={title}
          description={description}
          showLegend={true}
        />
      )}
    </DashboardCard>
  );
};

export default PerformanceChart;
