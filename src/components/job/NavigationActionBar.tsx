
import React from 'react';
import { Button } from '@/components/ui/button';
import { ArrowLeftIcon, ArrowRightIcon, BookmarkIcon } from 'lucide-react';

interface NavigationActionBarProps {
  currentStep: number;
  totalSteps: number;
  onPrevious: () => void;
  onNext: () => void;
  onSaveDraft: () => void;
  isLastStep: boolean;
  saveButtonText?: string;
}

const NavigationActionBar: React.FC<NavigationActionBarProps> = ({
  currentStep,
  totalSteps,
  onPrevious,
  onNext,
  onSaveDraft,
  isLastStep,
  saveButtonText
}) => {
  
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-background border-t border-border p-4 z-10">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div>
          <Button variant="outline" onClick={onSaveDraft}>
            <BookmarkIcon className="mr-2 h-4 w-4" />
            Save Draft
          </Button>
        </div>
        
        <div className="flex space-x-2">
          {currentStep > 1 && (
            <Button variant="outline" onClick={onPrevious}>
              <ArrowLeftIcon className="mr-2 h-4 w-4" />
              Previous
            </Button>
          )}
          
          <Button 
            onClick={onNext}
            type="button"
          >
            {isLastStep 
              ? (saveButtonText || "Publish Campaign") 
              : "Next"}
            {!isLastStep && <ArrowRightIcon className="ml-2 h-4 w-4" />}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NavigationActionBar;
