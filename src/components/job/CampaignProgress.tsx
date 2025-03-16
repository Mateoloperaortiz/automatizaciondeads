
import React from 'react';
import ProgressStep from './progress/ProgressStep';
import ProgressConnector from './progress/ProgressConnector';
import ProgressBar from './progress/ProgressBar';

export interface Step {
  id: number;
  label: string;
}

interface CampaignProgressProps {
  currentStep: number;
  totalSteps: number;
  steps?: Step[];
}

const DEFAULT_STEPS: Step[] = [
  { id: 1, label: 'Job Details' },
  { id: 2, label: 'Platforms' },
  { id: 3, label: 'Audience Targeting' },
];

const CampaignProgress: React.FC<CampaignProgressProps> = ({
  currentStep,
  totalSteps,
  steps = DEFAULT_STEPS,
}) => {
  const progressPercentage = ((currentStep) / totalSteps) * 100;

  return (
    <div className="mb-6 space-y-2">
      <div className="flex justify-between items-center mb-2">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <ProgressStep 
              id={step.id} 
              label={step.label} 
              currentStep={currentStep} 
            />
            
            {index < steps.length - 1 && (
              <ProgressConnector isActive={currentStep > index + 1} />
            )}
          </div>
        ))}
      </div>
      <ProgressBar value={progressPercentage} />
    </div>
  );
};

export default CampaignProgress;
