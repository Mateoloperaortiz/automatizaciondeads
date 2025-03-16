
import React from 'react';
import { useParams } from 'react-router-dom';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import CampaignProgress from '@/components/job/CampaignProgress';
import NavigationActionBar from '@/components/job/NavigationActionBar';
import CampaignLoading from '@/components/campaign/CampaignLoading';
import EditCampaignHeader from '@/components/campaign/edit/EditCampaignHeader';
import EditCampaignTabs from '@/components/campaign/edit/EditCampaignTabs';
import { useEditCampaign } from '@/hooks/useEditCampaign';

const EditCampaign: React.FC = () => {
  const { id = '' } = useParams<{ id: string }>();
  
  const {
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
  } = useEditCampaign(id);

  if (isLoading) {
    return <CampaignLoading />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-24 pb-32">
      <AnimatedTransition type="fade" className="space-y-8">
        <EditCampaignHeader campaignId={id} />
        
        <CampaignProgress 
          currentStep={getCurrentStep()} 
          totalSteps={3} 
        />
        
        <EditCampaignTabs
          campaign={campaign}
          currentTab={currentTab}
          onTabChange={handleTabChange}
          setSubmitButtonRef={setSubmitButtonRef}
          setSaveDraftButtonRef={setSaveDraftButtonRef}
        />
      </AnimatedTransition>
      
      <NavigationActionBar
        currentStep={getCurrentStep()}
        totalSteps={3}
        onPrevious={goToPreviousStep}
        onNext={goToNextStep}
        onSaveDraft={saveDraft}
        isLastStep={isLastStep}
        saveButtonText={isLastStep ? "Save Changes" : undefined}
      />
    </div>
  );
};

export default EditCampaign;
