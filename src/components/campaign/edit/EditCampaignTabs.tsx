
import React, { useRef } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import JobPostingForm from '@/components/job/JobPostingForm';
import PlatformSection from '@/components/job/sections/PlatformSection';
import AudienceSegmentation from '@/components/audience/AudienceSegmentation';

interface EditCampaignTabsProps {
  campaign: any;
  currentTab: string;
  onTabChange: (value: string) => void;
  setSubmitButtonRef: (ref: HTMLButtonElement | null) => void;
  setSaveDraftButtonRef: (ref: HTMLButtonElement | null) => void;
}

const EditCampaignTabs: React.FC<EditCampaignTabsProps> = ({
  campaign,
  currentTab,
  onTabChange,
  setSubmitButtonRef,
  setSaveDraftButtonRef,
}) => {
  return (
    <Tabs value={currentTab} onValueChange={onTabChange} className="space-y-8">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="job">Job Details</TabsTrigger>
        <TabsTrigger value="platforms">Platforms</TabsTrigger>
        <TabsTrigger value="audience">Audience Targeting</TabsTrigger>
      </TabsList>
      
      <TabsContent value="job" className="space-y-4">
        <div className="space-y-2">
          <h2 className="text-lg font-medium">Job Information</h2>
          <p className="text-muted-foreground text-sm">
            Update the details of your job
          </p>
        </div>
        <Separator className="my-6" />
        {campaign?.jobDetails && (
          <JobPostingForm 
            setSaveDraftRef={setSaveDraftButtonRef}
            initialValues={campaign.jobDetails}
            isEditing={true}
            campaignId={campaign.id}
          />
        )}
      </TabsContent>
      
      <TabsContent value="platforms" className="space-y-4">
        <div className="space-y-2">
          <h2 className="text-lg font-medium">Select Platforms</h2>
          <p className="text-muted-foreground text-sm">
            Choose which platforms you want to publish your job on
          </p>
        </div>
        <Separator className="my-6" />
        <PlatformSection 
          standalone={true} 
          initialPlatforms={campaign?.platforms || []}
        />
      </TabsContent>
      
      <TabsContent value="audience" className="space-y-4">
        <div className="space-y-2">
          <h2 className="text-lg font-medium">Audience Targeting</h2>
          <p className="text-muted-foreground text-sm">
            Define the target audience for your job advertisement
          </p>
        </div>
        <Separator className="my-6" />
        {campaign?.audience && (
          <AudienceSegmentation 
            initialValues={campaign.audience} 
          />
        )}
        <button 
          ref={setSubmitButtonRef} 
          type="submit" 
          className="hidden"
        >
          Submit
        </button>
      </TabsContent>
    </Tabs>
  );
};

export default EditCampaignTabs;
