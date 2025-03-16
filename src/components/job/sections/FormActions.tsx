
import React from 'react';
import { Button } from '@/components/ui/button';
import { useJobForm } from '../JobFormContext';

interface FormActionsProps {
  isEditing?: boolean;
}

const FormActions: React.FC<FormActionsProps> = ({ isEditing = false }) => {
  const {
    form,
    isSubmitting,
    onSubmit
  } = useJobForm();
  
  const handleSubmit = () => {
    if (form && onSubmit) {
      // Get form data and pass to onSubmit
      const data = form.getValues();
      onSubmit(data);
    }
  };
  
  return (
    <div className="flex justify-end pt-4">
      <Button 
        type={isEditing ? "button" : "submit"} 
        disabled={isSubmitting}
        onClick={isEditing ? handleSubmit : undefined}
      >
        {isSubmitting 
          ? (isEditing ? "Updating..." : "Creating...") 
          : (isEditing ? "Update Campaign" : "Create Campaign")}
      </Button>
    </div>
  );
};

export default FormActions;
