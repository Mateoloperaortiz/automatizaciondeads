import React from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import CampaignItem, { CampaignItemProps } from './CampaignItem';
import { useQuery } from '@tanstack/react-query';
import { fetchCampaigns, Campaign } from '@/services/campaignService';
import { useToast } from '@/hooks/use-toast';

const CampaignTabs: React.FC = () => {
  const { toast } = useToast();
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['campaigns'],
    queryFn: fetchCampaigns,
    meta: {
      onError: () => {
        toast({
          title: "Error loading campaigns",
          description: "Could not load campaign data. Please try again.",
          variant: "destructive"
        });
      }
    }
  });

  const activeCampaigns = data?.active || [];
  const allCampaigns = data?.all || [];

  const mapCampaignToProps = (campaign: Campaign): CampaignItemProps => {
    const validStatus = ['active', 'scheduled', 'ended', 'draft'].includes(campaign.status)
      ? campaign.status as CampaignItemProps['status']
      : 'active';

    return {
      id: campaign.id,
      title: campaign.title,
      platform: campaign.platform,
      date: campaign.date,
      status: validStatus,
      metrics: campaign.metrics
    };
  };

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center py-12">
          <h2 className="text-xl font-medium mb-4">Recent Campaigns</h2>
          <p className="text-muted-foreground mb-4">Failed to load campaign data</p>
          <Button 
            variant="outline"
            onClick={() => window.location.reload()}
          >
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <Tabs defaultValue="active">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-medium">Recent Campaigns</h2>
          <TabsList>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="all">All Campaigns</TabsTrigger>
          </TabsList>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-10 w-10 animate-spin text-primary/70" />
          </div>
        ) : (
          <>
            <TabsContent value="active" className="space-y-4">
              {activeCampaigns.map((campaign: Campaign) => (
                <CampaignItem key={campaign.id} {...mapCampaignToProps(campaign)} />
              ))}
            </TabsContent>
            
            <TabsContent value="all" className="space-y-4">
              {allCampaigns.map((campaign: Campaign) => (
                <CampaignItem key={campaign.id} {...mapCampaignToProps(campaign)} />
              ))}
            </TabsContent>
          </>
        )}
      </Tabs>
    </Card>
  );
};

export default CampaignTabs;
