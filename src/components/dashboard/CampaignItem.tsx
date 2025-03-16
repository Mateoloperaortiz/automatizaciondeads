
import React from 'react';
import { Briefcase } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useNavigate } from 'react-router-dom';

export interface CampaignItemProps {
  id?: string;
  title: string;
  platform: string;
  date: string;
  status: 'active' | 'scheduled' | 'ended' | 'draft';
  metrics: {
    views: number;
    clicks: number;
    applications: number;
  };
}

const CampaignItem: React.FC<CampaignItemProps> = ({
  id = 'camp-001', // Default ID if none provided
  title,
  platform,
  date,
  status,
  metrics
}) => {
  const navigate = useNavigate();
  
  const statusColors = {
    active: 'bg-green-500',
    scheduled: 'bg-blue-500',
    ended: 'bg-gray-500',
    draft: 'bg-yellow-500'
  };

  const handleCampaignClick = () => {
    navigate(`/campaign/${id}`);
  };

  return (
    <div 
      className="flex flex-col md:flex-row md:items-center justify-between p-4 rounded-lg border border-border/50 bg-card hover:bg-secondary/50 transition-colors cursor-pointer"
      onClick={handleCampaignClick}
    >
      <div className="flex-1 mb-3 md:mb-0">
        <div className="flex items-start">
          <div className="mr-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <Briefcase className="h-5 w-5" />
            </div>
          </div>
          <div>
            <h3 className="font-medium text-left">{title}</h3>
            <div className="flex items-center text-sm text-muted-foreground mt-1">
              <span>{platform}</span>
              <span className="mx-2">•</span>
              <span>{date}</span>
              <span className="mx-2">•</span>
              <span className={cn("inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium text-white", statusColors[status])}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div className="flex space-x-6">
        <div className="text-center">
          <div className="text-lg font-medium">{metrics.views}</div>
          <div className="text-xs text-muted-foreground">Views</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-medium">{metrics.clicks}</div>
          <div className="text-xs text-muted-foreground">Clicks</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-medium">{metrics.applications}</div>
          <div className="text-xs text-muted-foreground">Applications</div>
        </div>
      </div>
    </div>
  );
};

export default CampaignItem;
