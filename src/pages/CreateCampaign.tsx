
import React, { useState, useRef } from 'react';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import JobPostingForm from '@/components/job/JobPostingForm';
import AudienceSegmentation from '@/components/audience/AudienceSegmentation';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import CampaignProgress from '@/components/job/CampaignProgress';
import NavigationActionBar from '@/components/job/NavigationActionBar';
import PlatformSection from '@/components/job/sections/PlatformSection';
import { useToast } from '@/components/ui/use-toast';

const CreateCampaign: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>("job");
  const submitButtonRef = useRef<HTMLButtonElement>(null);
  const saveDraftButtonRef = useRef<HTMLButtonElement>(null);
  const { toast } = useToast();
  
  const handleTabChange = (value: string) => {
    setCurrentTab(value);
  };

  const goToNextStep = () => {
    if (currentTab === "job") {
      setCurrentTab("platforms");
    } else if (currentTab === "platforms") {
      setCurrentTab("audience");
    } else if (currentTab === "audience" && submitButtonRef.current) {
      // Trigger form submission
      submitButtonRef.current.click();
    }
  };

  const goToPreviousStep = () => {
    if (currentTab === "audience") {
      setCurrentTab("platforms");
    } else if (currentTab === "platforms") {
      setCurrentTab("job");
    }
  };

  const saveDraft = () => {
    if (saveDraftButtonRef.current) {
      saveDraftButtonRef.current.click();
    }
    
    toast({
      title: "Draft saved",
      description: "Your campaign has been saved as a draft.",
    });
  };

  const getCurrentStep = () => {
    switch (currentTab) {
      case "job":
        return 1;
      case "platforms":
        return 2;
      case "audience":
        return 3;
      default:
        return 1;
    }
  };

  // To capture the submit button reference
  const setSubmitButtonRef = (ref: HTMLButtonElement | null) => {
    if (ref) {
      submitButtonRef.current = ref;
    }
  };
  
  // To capture the save draft button reference
  const setSaveDraftButtonRef = (ref: HTMLButtonElement | null) => {
    if (ref) {
      saveDraftButtonRef.current = ref;
    }
  };

  const isLastStep = currentTab === "audience";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-24 pb-32">
      <AnimatedTransition type="fade" className="space-y-8">
        <div>
          <h1 className="text-3xl font-medium tracking-tight">Create New Campaign</h1>
          <p className="text-muted-foreground mt-1">
            Publish job openings across multiple platforms
          </p>
        </div>
        
        <CampaignProgress 
          currentStep={getCurrentStep()} 
          totalSteps={3} 
        />
        
        <Tabs value={currentTab} onValueChange={handleTabChange} className="space-y-8">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="job">Job Details</TabsTrigger>
            <TabsTrigger value="platforms">Platforms</TabsTrigger>
            <TabsTrigger value="audience">Audience Targeting</TabsTrigger>
          </TabsList>
          
          <TabsContent value="job" className="space-y-4">
            <div className="space-y-2">
              <h2 className="text-lg font-medium">Job Information</h2>
              <p className="text-muted-foreground text-sm">
                Enter the details of the job you want to advertise
              </p>
            </div>
            <Separator className="my-6" />
            <JobPostingForm setSaveDraftRef={setSaveDraftButtonRef} />
          </TabsContent>
          
          <TabsContent value="platforms" className="space-y-4">
            <div className="space-y-2">
              <h2 className="text-lg font-medium">Select Platforms</h2>
              <p className="text-muted-foreground text-sm">
                Choose which platforms you want to publish your job on
              </p>
            </div>
            <Separator className="my-6" />
            <PlatformSection standalone={true} />
          </TabsContent>
          
          <TabsContent value="audience" className="space-y-4">
            <div className="space-y-2">
              <h2 className="text-lg font-medium">Audience Targeting</h2>
              <p className="text-muted-foreground text-sm">
                Define the target audience for your job advertisement
              </p>
            </div>
            <Separator className="my-6" />
            <AudienceSegmentation />
            <button 
              ref={setSubmitButtonRef} 
              type="submit" 
              className="hidden"
            >
              Submit
            </button>
          </TabsContent>
        </Tabs>
      </AnimatedTransition>
      
      <NavigationActionBar
        currentStep={getCurrentStep()}
        totalSteps={3}
        onPrevious={goToPreviousStep}
        onNext={goToNextStep}
        onSaveDraft={saveDraft}
        isLastStep={isLastStep}
      />
    </div>
  );
};

export default CreateCampaign;
