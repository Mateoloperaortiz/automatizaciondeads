
import { useState, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useToast } from '@/components/ui/use-toast';
import { fetchCampaignDetails } from '@/services/campaignService';

export const useEditCampaign = (campaignId: string) => {
  const [currentTab, setCurrentTab] = useState<string>("job");
  const submitButtonRef = useRef<HTMLButtonElement>(null);
  const saveDraftButtonRef = useRef<HTMLButtonElement>(null);
  const { toast } = useToast();

  const { 
    data: campaign, 
    isLoading, 
    error 
  } = useQuery({
    queryKey: ['campaign', campaignId],
    queryFn: () => fetchCampaignDetails(campaignId),
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

  useEffect(() => {
    if (error) {
      toast({
        title: "Error",
        description: "Failed to load campaign details for editing",
        variant: "destructive"
      });
    }
  }, [error, toast]);

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
      title: "Changes saved",
      description: "Your campaign changes have been saved.",
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

  return {
    campaign,
    isLoading,
    currentTab,
    handleTabChange,
    goToNextStep,
    goToPreviousStep,
    saveDraft,
    getCurrentStep,
    setSubmitButtonRef,
    setSaveDraftButtonRef,
    isLastStep
  };
};
