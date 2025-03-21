
import React from 'react';
import { Check, Activity } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ApiHealthMetrics } from '@/types/platformTypes';
import ApiHealthDisplay from './ApiHealthDisplay';

interface ConnectedAccountInfoProps {
  platformName: string;
  apiHealth: ApiHealthMetrics | null;
  loadingHealth: boolean;
  expanded: boolean;
  onRefreshHealth: () => void;
}

const ConnectedAccountInfo: React.FC<ConnectedAccountInfoProps> = ({
  platformName,
  apiHealth,
  loadingHealth,
  expanded,
  onRefreshHealth
}) => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-3 flex-1">
          <div className="flex items-start">
            <Check className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium">Successfully connected</h4>
              <p className="text-xs text-muted-foreground mt-1">
                Your {platformName} account is now connected and ready to post job ads.
              </p>
            </div>
          </div>
        </div>
        
        <Button 
          variant="outline" 
          size="sm" 
          className="ml-2 h-10" 
          onClick={onRefreshHealth}
          disabled={loadingHealth}
        >
          <Activity className={`h-4 w-4 mr-2 ${loadingHealth ? 'animate-pulse' : ''}`} />
          Refresh
        </Button>
      </div>
      
      <div className="flex flex-col space-y-2">
        <div className="flex justify-between items-center text-sm">
          <span>Account status</span>
          <Badge variant="outline" className="bg-green-500/10 text-green-600 border-green-200">
            Active
          </Badge>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span>Connection type</span>
          <span className="text-muted-foreground">API Key</span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span>Last synced</span>
          <span className="text-muted-foreground">
            {apiHealth ? new Date(apiHealth.lastSyncTime).toLocaleString() : 'Just now'}
          </span>
        </div>
      </div>

      {apiHealth && <ApiHealthDisplay metrics={apiHealth} isExpanded={expanded} />}
    </div>
  );
};

export default ConnectedAccountInfo;
