
import React, { useState } from 'react';
import { BarChart3, LineChart, ArrowUpRight, InfoIcon, Eye, DollarSign } from 'lucide-react';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import MetricSummaryCards from './MetricSummaryCards';
import PerformanceChart from './PerformanceChart';
import { 
  performanceData, performanceDataPrevious, 
  conversionData, conversionDataPrevious,
  impressionsData, impressionsDataPrevious,
  adSpendData, adSpendDataPrevious
} from './performanceData';
import { 
  combineDataForComparison, 
  calculateGrowth, 
  calculateAverage, 
  formatNumber 
} from './utils';

const PerformanceCharts: React.FC = () => {
  const [showComparison, setShowComparison] = useState(false);
  
  // Prepare combined data for comparison
  const performanceComparisonData = combineDataForComparison(performanceData, performanceDataPrevious);
  const conversionComparisonData = combineDataForComparison(conversionData, conversionDataPrevious);
  const impressionsComparisonData = combineDataForComparison(impressionsData, impressionsDataPrevious);
  const adSpendComparisonData = combineDataForComparison(adSpendData, adSpendDataPrevious);
  
  // Calculate summary metrics
  const currentAvgPerformance = calculateAverage(performanceData);
  const previousAvgPerformance = calculateAverage(performanceDataPrevious);
  const performanceGrowth = calculateGrowth(currentAvgPerformance, previousAvgPerformance);
  
  const currentAvgConversion = calculateAverage(conversionData);
  const previousAvgConversion = calculateAverage(conversionDataPrevious);
  const conversionGrowth = calculateGrowth(currentAvgConversion, previousAvgConversion);
  
  // Calculate impressions metrics
  const totalImpressions = impressionsData.reduce((sum, item) => sum + item.value, 0);
  const totalImpressionsPrevious = impressionsDataPrevious.reduce((sum, item) => sum + item.value, 0);
  const impressionsGrowth = calculateGrowth(totalImpressions, totalImpressionsPrevious);
  const avgImpressions = calculateAverage(impressionsData);
  
  // Calculate ad spend metrics
  const totalAdSpend = adSpendData.reduce((sum, item) => sum + item.value, 0);
  const totalAdSpendPrevious = adSpendDataPrevious.reduce((sum, item) => sum + item.value, 0);
  const adSpendGrowth = calculateGrowth(totalAdSpend, totalAdSpendPrevious);
  const avgAdSpend = calculateAverage(adSpendData);
  
  // Latest values
  const latestPerformance = performanceData[performanceData.length - 1].value;
  const latestConversion = conversionData[conversionData.length - 1].value;
  const latestImpressions = impressionsData[impressionsData.length - 1].value;
  const latestAdSpend = adSpendData[adSpendData.length - 1].value;
  
  const conversionTrendChange = calculateGrowth(
    conversionData[conversionData.length - 1].value, 
    conversionData[0].value
  );
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-2xl font-bold">Performance Analytics</h2>
        <div className="flex items-center space-x-2">
          <Label htmlFor="comparison-switch" className="text-sm text-muted-foreground cursor-pointer">
            Compare with previous period
          </Label>
          <Switch 
            id="comparison-switch" 
            checked={showComparison} 
            onCheckedChange={setShowComparison} 
          />
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AnimatedTransition type="slide-up" delay={0.2}>
          <div className="space-y-4">
            <MetricSummaryCards
              latestValue={latestPerformance}
              averageValue={currentAvgPerformance}
              totalValue={performanceData.reduce((sum, item) => sum + item.value, 0)}
              growth={performanceGrowth}
              previousAverage={previousAvgPerformance}
              showComparison={showComparison}
            />
            
            <PerformanceChart
              title="Campaign Performance"
              description="Monthly performance tracking"
              icon={<BarChart3 className="h-5 w-5" />}
              accentColor="#9b87f5"
              tooltipContent="Performance data across all active campaigns"
              chartData={performanceData}
              comparisonData={performanceComparisonData}
              showComparison={showComparison}
              chartType="bar"
              currentColor="#9b87f5"
              previousColor="#D6BCFA"
            />
          </div>
        </AnimatedTransition>
        
        <AnimatedTransition type="slide-up" delay={0.3}>
          <div className="space-y-4">
            <MetricSummaryCards
              latestValue={latestConversion}
              averageValue={currentAvgConversion}
              totalValue={conversionData.reduce((sum, item) => sum + item.value, 0)} 
              growth={conversionGrowth}
              trendValue={conversionTrendChange}
              showPercentInLatest={true}
              unit="%"
              previousAverage={`${previousAvgConversion}%`}
              showComparison={showComparison}
            />
            
            <PerformanceChart
              title="Conversion Rate"
              description="Weekly conversion trend"
              icon={<LineChart className="h-5 w-5" />}
              accentColor="#10b981"
              tooltipContent="Percentage of views that resulted in applications"
              chartData={conversionData}
              comparisonData={conversionComparisonData}
              showComparison={showComparison}
              currentColor="#10b981"
              previousColor="#86efac"
            />
          </div>
        </AnimatedTransition>

        <AnimatedTransition type="slide-up" delay={0.4}>
          <div className="space-y-4">
            <MetricSummaryCards
              latestValue={formatNumber(latestImpressions)}
              averageValue={formatNumber(avgImpressions)}
              totalValue={formatNumber(totalImpressions)}
              growth={impressionsGrowth}
              showComparison={showComparison}
            />
            
            <PerformanceChart
              title="Total Impressions"
              description="Monthly impression tracking"
              icon={<Eye className="h-5 w-5" />}
              accentColor="#0EA5E9"
              tooltipContent="Total views across all campaigns"
              chartData={impressionsData}
              comparisonData={impressionsComparisonData}
              showComparison={showComparison}
              chartType="area"
              currentColor="#0EA5E9"
              previousColor="#D3E4FD"
            />
          </div>
        </AnimatedTransition>

        <AnimatedTransition type="slide-up" delay={0.5}>
          <div className="space-y-4">
            <MetricSummaryCards
              latestValue={formatNumber(latestAdSpend)}
              averageValue={formatNumber(avgAdSpend)}
              totalValue={formatNumber(totalAdSpend)}
              growth={adSpendGrowth}
              isCurrency={true}
              showComparison={showComparison}
            />
            
            <PerformanceChart
              title="Ad Spend"
              description="Monthly spending tracking"
              icon={<DollarSign className="h-5 w-5" />}
              accentColor="#F97316"
              tooltipContent="Total advertising spend across all platforms"
              chartData={adSpendData}
              comparisonData={adSpendComparisonData}
              showComparison={showComparison}
              chartType="bar"
              currentColor="#F97316"
              previousColor="#FDE1D3"
            />
          </div>
        </AnimatedTransition>
      </div>
    </div>
  );
};

export default PerformanceCharts;
