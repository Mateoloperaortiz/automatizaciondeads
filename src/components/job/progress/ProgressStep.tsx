
import React from 'react';
import { CheckCircle, Circle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ProgressStepProps {
  id: number;
  label: string;
  currentStep: number;
}

const ProgressStep: React.FC<ProgressStepProps> = ({
  id,
  label,
  currentStep,
}) => {
  const isActive = currentStep >= id;
  const isCompleted = currentStep > id;
  
  return (
    <div className="flex flex-col items-center">
      <div className={cn(
        "flex items-center justify-center w-8 h-8 rounded-full border-2",
        isActive 
          ? "border-primary bg-primary text-primary-foreground" 
          : "border-muted-foreground bg-background text-muted-foreground"
      )}>
        {isCompleted ? (
          <CheckCircle className="w-5 h-5" />
        ) : currentStep === id ? (
          <Circle className="w-5 h-5 fill-current" />
        ) : (
          <Circle className="w-5 h-5" />
        )}
      </div>
      <span className={cn(
        "text-sm mt-1",
        isActive ? "text-foreground font-medium" : "text-muted-foreground"
      )}>
        {label}
      </span>
    </div>
  );
};

export default ProgressStep;
