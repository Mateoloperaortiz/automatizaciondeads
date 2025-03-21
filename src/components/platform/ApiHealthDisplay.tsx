
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  Clock, 
  Activity, 
  CheckCircle, 
  XCircle, 
  AlertCircle 
} from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { ApiHealthMetrics, calculatePercentage, formatRelativeTime } from '@/types/platformTypes';

interface ApiHealthDisplayProps {
  metrics: ApiHealthMetrics;
  isExpanded: boolean;
}

const ApiHealthDisplay: React.FC<ApiHealthDisplayProps> = ({ metrics, isExpanded }) => {
  if (!isExpanded) return null;
  
  const quotaPercentage = calculatePercentage(metrics.quotaUsed, metrics.quotaLimit);
  const rateLimitPercentage = calculatePercentage(
    metrics.rateLimit - metrics.rateLimitRemaining, 
    metrics.rateLimit
  );
  
  return (
    <Card className="mt-4 bg-muted/30 border-dashed">
      <CardContent className="pt-4 pb-3">
        <div className="space-y-3">
          {/* Status indicator */}
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium">API Status</span>
            <StatusBadge status={metrics.status} />
          </div>
          
          {/* Quota usage */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground">API Quota Usage</span>
              <span className="font-medium">{metrics.quotaUsed.toLocaleString()} / {metrics.quotaLimit.toLocaleString()}</span>
            </div>
            <Progress 
              value={quotaPercentage} 
              className="h-1.5" 
              indicatorClassName={getProgressColor(quotaPercentage)}
            />
          </div>
          
          {/* Rate limit */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground">Rate Limit Remaining</span>
              <span className="font-medium">{metrics.rateLimitRemaining} / {metrics.rateLimit}</span>
            </div>
            <Progress 
              value={rateLimitPercentage} 
              className="h-1.5" 
              indicatorClassName={getProgressColor(rateLimitPercentage)}
            />
          </div>
          
          {/* Last synced and reset time */}
          <div className="grid grid-cols-2 gap-4 pt-1">
            <div className="text-xs">
              <div className="flex items-center text-muted-foreground mb-1">
                <Clock className="h-3 w-3 mr-1" />
                <span>Last Synced</span>
              </div>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger className="text-left font-medium">
                    {formatRelativeTime(metrics.lastSyncTime)}
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{new Date(metrics.lastSyncTime).toLocaleString()}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            
            <div className="text-xs">
              <div className="flex items-center text-muted-foreground mb-1">
                <Activity className="h-3 w-3 mr-1" />
                <span>Avg Response</span>
              </div>
              <span className="font-medium">{metrics.averageResponseTime}ms</span>
            </div>
          </div>
          
          <div className="text-xs pt-1 border-t border-border/50 mt-2">
            <div className="flex items-center text-muted-foreground mb-1">
              <Clock className="h-3 w-3 mr-1" />
              <span>Quota Reset</span>
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger className="text-left font-medium">
                  {formatRelativeTime(metrics.resetTime)}
                </TooltipTrigger>
                <TooltipContent>
                  <p>{new Date(metrics.resetTime).toLocaleString()}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const StatusBadge: React.FC<{ status: ApiHealthMetrics['status'] }> = ({ status }) => {
  switch (status) {
    case 'healthy':
      return (
        <Badge className="bg-green-500 text-white gap-1">
          <CheckCircle className="h-3 w-3" />
          Operational
        </Badge>
      );
    case 'degraded':
      return (
        <Badge className="bg-amber-500 text-white gap-1">
          <AlertTriangle className="h-3 w-3" />
          Degraded
        </Badge>
      );
    case 'down':
      return (
        <Badge className="bg-red-500 text-white gap-1">
          <XCircle className="h-3 w-3" />
          Down
        </Badge>
      );
    default:
      return (
        <Badge className="bg-gray-500 text-white gap-1">
          <AlertCircle className="h-3 w-3" />
          Unknown
        </Badge>
      );
  }
};

const getProgressColor = (percentage: number): string => {
  if (percentage < 60) return 'bg-green-500';
  if (percentage < 80) return 'bg-amber-500';
  return 'bg-red-500';
};

export default ApiHealthDisplay;
