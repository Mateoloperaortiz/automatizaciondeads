
import React from 'react';
import { cn } from '@/lib/utils';
import { MetricItem } from './MetricItem';

interface MetricsSummaryProps {
  metrics: Array<{
    label: string;
    value: string | number;
    change?: {
      value: number;
      direction: 'up' | 'down' | 'neutral';
    };
    icon?: React.ReactNode;
    tooltip?: string;
    onClick?: () => void;
    color?: string;
  }>;
  className?: string;
}

export const MetricsSummary: React.FC<MetricsSummaryProps> = ({
  metrics,
  className
}) => {
  return (
    <div className={cn("grid grid-cols-2 md:grid-cols-4 gap-4", className)}>
      {metrics.map((metric, index) => (
        <MetricItem 
          key={index} 
          label={metric.label} 
          value={metric.value} 
          change={metric.change} 
          icon={metric.icon} 
          tooltip={metric.tooltip} 
          onClick={metric.onClick}
          color={metric.color}
        />
      ))}
    </div>
  );
};

export default MetricsSummary;
