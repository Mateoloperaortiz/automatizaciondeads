
import React from 'react';
import { Card } from '@/components/ui/card';
import { Calendar, FileText, Target } from 'lucide-react';

interface CampaignStatsProps {
  createdDate?: string;
  status?: string;
  platform?: string;
}

const CampaignStats: React.FC<CampaignStatsProps> = ({ createdDate, status, platform }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card className="p-4 flex items-center space-x-4 col-span-1">
        <div className="bg-primary/10 p-3 rounded-full">
          <Calendar className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h3 className="text-sm font-medium text-muted-foreground">Created On</h3>
          <p className="text-lg font-medium">{createdDate || 'Unknown'}</p>
        </div>
      </Card>
      
      <Card className="p-4 flex items-center space-x-4 col-span-1">
        <div className="bg-primary/10 p-3 rounded-full">
          <FileText className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h3 className="text-sm font-medium text-muted-foreground">Status</h3>
          <p className="text-lg font-medium capitalize">{status || 'Unknown'}</p>
        </div>
      </Card>
      
      <Card className="p-4 flex items-center space-x-4 col-span-1">
        <div className="bg-primary/10 p-3 rounded-full">
          <Target className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h3 className="text-sm font-medium text-muted-foreground">Platforms</h3>
          <p className="text-lg font-medium">{platform || 'None'}</p>
        </div>
      </Card>
    </div>
  );
};

export default CampaignStats;
