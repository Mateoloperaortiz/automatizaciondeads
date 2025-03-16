
import React from 'react';
import { Separator } from '@/components/ui/separator';
import { Card } from '@/components/ui/card';
import BasicInfoSection from '@/components/job/sections/BasicInfoSection';
import JobDetailsSection from '@/components/job/sections/JobDetailsSection';
import PlatformSection from '@/components/job/sections/PlatformSection';
import AudienceDisplay from './AudienceDisplay';

interface TabContentProps {
  tab: string;
  campaign: any;
}

const CampaignTabContent: React.FC<TabContentProps> = ({ tab, campaign }) => {
  switch (tab) {
    case "details":
      return (
        <div className="space-y-6">
          <div className="space-y-2">
            <h2 className="text-lg font-medium">Job Information</h2>
            <p className="text-muted-foreground text-sm">
              Details of the job being advertised
            </p>
          </div>
          <Separator className="my-6" />
          
          {campaign?.jobDetails ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-6">
                <BasicInfoSection readOnly={true} initialData={campaign.jobDetails} />
              </div>
              <div className="space-y-6">
                <JobDetailsSection readOnly={true} initialData={campaign.jobDetails} />
              </div>
            </div>
          ) : (
            <Card className="p-6 text-center">
              <p className="text-muted-foreground">No job details available</p>
            </Card>
          )}
        </div>
      );
    
    case "platforms":
      return (
        <div className="space-y-6">
          <div className="space-y-2">
            <h2 className="text-lg font-medium">Selected Platforms</h2>
            <p className="text-muted-foreground text-sm">
              Platforms where this job is published
            </p>
          </div>
          <Separator className="my-6" />
          
          {campaign?.platforms && campaign.platforms.length > 0 ? (
            <PlatformSection 
              standalone={true} 
              readOnly={true} 
              initialPlatforms={campaign.platforms} 
            />
          ) : (
            <Card className="p-6 text-center">
              <p className="text-muted-foreground">No platform data available</p>
            </Card>
          )}
        </div>
      );
    
    case "audience":
      return (
        <div className="space-y-6">
          <div className="space-y-2">
            <h2 className="text-lg font-medium">Audience Targeting</h2>
            <p className="text-muted-foreground text-sm">
              Target audience for this campaign
            </p>
          </div>
          <Separator className="my-6" />
          
          <AudienceDisplay audience={campaign?.audience} />
        </div>
      );
    
    default:
      return null;
  }
};

export default CampaignTabContent;
