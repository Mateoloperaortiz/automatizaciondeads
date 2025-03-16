
import React from 'react';
import { BarChart3, Users, TrendingUp, DollarSign } from 'lucide-react';
import { MetricsSummary } from '@/components/dashboard/metrics/MetricsSummary';
import AnimatedTransition from '@/components/ui/AnimatedTransition';

const overviewMetrics = [
  {
    label: "Total Campaigns",
    value: "24",
    change: { value: 12, direction: 'up' as const },
    icon: <BarChart3 className="h-4 w-4" />,
    tooltip: "Total number of campaigns created",
    color: "#8B5CF6" // Vivid Purple
  },
  {
    label: "Total Impressions",
    value: "3.2M",
    change: { value: 8, direction: 'up' as const },
    icon: <Users className="h-4 w-4" />,
    tooltip: "Total impressions across all campaigns",
    color: "#0EA5E9" // Ocean Blue
  },
  {
    label: "Conversion Rate",
    value: "3.8%",
    change: { value: 1.5, direction: 'up' as const },
    icon: <TrendingUp className="h-4 w-4" />,
    tooltip: "Average conversion rate across all campaigns",
    color: "#10B981" // Green
  },
  {
    label: "Ad Spend",
    value: "$12,450",
    change: { value: 5, direction: 'up' as const },
    icon: <DollarSign className="h-4 w-4" />,
    tooltip: "Total spend across all active campaigns",
    color: "#F97316" // Bright Orange
  }
];

const OverviewMetrics: React.FC = () => {
  return (
    <AnimatedTransition type="slide-up" delay={0.1}>
      <div>
        <MetricsSummary 
          metrics={overviewMetrics} 
          className="gap-3 md:gap-4" 
        />
      </div>
    </AnimatedTransition>
  );
};

export default OverviewMetrics;
