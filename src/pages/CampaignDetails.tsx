
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { fetchCampaignDetails } from '@/services/campaignService';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import ActionBar from '@/components/campaign/ActionBar';
import CampaignStats from '@/components/campaign/CampaignStats';
import CampaignTabContent from '@/components/campaign/CampaignTabContent';
import CampaignLoading from '@/components/campaign/CampaignLoading';

const CampaignDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { toast } = useToast();
  const [currentTab, setCurrentTab] = useState<string>("details");
  
  const { data: campaign, isLoading, error } = useQuery({
    queryKey: ['campaign', id],
    queryFn: () => fetchCampaignDetails(id || ''),
    meta: {
      onError: () => {
        toast({
          title: "Error loading campaign",
          description: "Could not load campaign details. Please try again.",
          variant: "destructive"
        });
      }
    }
  });

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-24">
        <AnimatedTransition type="fade">
          <Button onClick={() => history.back()} variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Card className="p-12 text-center">
            <h2 className="text-xl font-medium mb-4">Campaign Not Found</h2>
            <p className="text-muted-foreground mb-6">
              The campaign you're looking for could not be found or has been removed.
            </p>
            <Button onClick={() => history.back()}>Return to Dashboard</Button>
          </Card>
        </AnimatedTransition>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-24">
      <AnimatedTransition type="fade" className="space-y-8">
        <ActionBar 
          campaignId={id} 
          campaignTitle={campaign?.title} 
          isLoading={isLoading} 
        />
        
        {isLoading ? (
          <CampaignLoading />
        ) : (
          <>
            <CampaignStats 
              createdDate={campaign?.createdDate} 
              status={campaign?.status} 
              platform={campaign?.platform} 
            />
            
            <Tabs value={currentTab} onValueChange={setCurrentTab} className="pt-4">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="details">Job Details</TabsTrigger>
                <TabsTrigger value="platforms">Platforms</TabsTrigger>
                <TabsTrigger value="audience">Audience</TabsTrigger>
              </TabsList>
              
              <div className="mt-6">
                <TabsContent value="details">
                  <CampaignTabContent tab="details" campaign={campaign} />
                </TabsContent>
                
                <TabsContent value="platforms">
                  <CampaignTabContent tab="platforms" campaign={campaign} />
                </TabsContent>
                
                <TabsContent value="audience">
                  <CampaignTabContent tab="audience" campaign={campaign} />
                </TabsContent>
              </div>
            </Tabs>
          </>
        )}
      </AnimatedTransition>
    </div>
  );
};

export default CampaignDetails;
