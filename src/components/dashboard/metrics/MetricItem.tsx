
import React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent } from '@/components/ui/card';
import { InfoIcon, ExternalLink, ArrowUpIcon, ArrowDownIcon, MinusIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface MetricItemProps {
  label: string;
  value: string | number;
  change?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
  };
  icon?: React.ReactNode;
  className?: string;
  tooltip?: string;
  onClick?: () => void;
  color?: string;
}

export const MetricItem: React.FC<MetricItemProps> = ({
  label,
  value,
  change,
  icon,
  className,
  tooltip,
  onClick,
  color = '#8B5CF6' // Default to purple if no color provided
}) => {
  return (
    <Card 
      className={cn(
        "overflow-hidden transition-all duration-300", 
        onClick ? "cursor-pointer" : "", 
        className
      )} 
      onClick={onClick}
      style={{
        borderLeft: `4px solid ${color}`,
        boxShadow: `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)`
      }}
    >
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5">
            <span className="text-sm font-medium text-muted-foreground">{label}</span>
            {tooltip && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoIcon className="h-3.5 w-3.5 text-muted-foreground/70" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="text-xs max-w-[200px]">{tooltip}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </div>
          {icon && (
            <div 
              className="p-1.5 rounded-full" 
              style={{ backgroundColor: `${color}20` }}
            >
              <div style={{ color: color }}>{icon}</div>
            </div>
          )}
        </div>
        <div className="flex items-baseline justify-between">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-semibold tracking-tight">{value}</span>
            {change && (
              <div 
                className={cn(
                  "flex items-center text-xs font-medium rounded-full px-1.5 py-0.5", 
                  {
                    "text-green-500 bg-green-500/10": change.direction === 'up',
                    "text-red-500 bg-red-500/10": change.direction === 'down',
                    "text-muted-foreground bg-muted/30": change.direction === 'neutral'
                  }
                )}
              >
                {change.direction === 'up' ? (
                  <ArrowUpIcon className="h-3 w-3 mr-0.5" />
                ) : change.direction === 'down' ? (
                  <ArrowDownIcon className="h-3 w-3 mr-0.5" />
                ) : (
                  <MinusIcon className="h-3 w-3 mr-0.5" />
                )}
                {Math.abs(change.value)}%
              </div>
            )}
          </div>
          {onClick && (
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
              <ExternalLink className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default MetricItem;
