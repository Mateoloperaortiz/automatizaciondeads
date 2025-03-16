
import React from 'react';
import { Form } from '@/components/ui/form';
import { JobFormProvider, JobFormValues } from './JobFormContext';
import BasicInfoSection from './sections/BasicInfoSection';
import JobDetailsSection from './sections/JobDetailsSection';
import FormActions from './sections/FormActions';
import useJobForm from './hooks/useJobForm';

interface JobPostingFormProps {
  setSaveDraftRef?: (ref: HTMLButtonElement | null) => void;
  initialValues?: Partial<JobFormValues>;
  isEditing?: boolean;
  campaignId?: string;
}

const JobPostingForm: React.FC<JobPostingFormProps> = ({ 
  setSaveDraftRef, 
  initialValues, 
  isEditing = false,
  campaignId
}) => {
  const {
    form,
    isSubmitting,
    onSubmit,
    saveDraft
  } = useJobForm({ initialValues, isEditing, campaignId });
  
  return (
    <JobFormProvider form={form} isSubmitting={isSubmitting} onSubmit={onSubmit}>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 animate-fade-in">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <BasicInfoSection />
            <JobDetailsSection />
          </div>
          
          <FormActions isEditing={isEditing} />

          {/* Hidden button for saving draft */}
          <button
            type="button"
            ref={setSaveDraftRef}
            onClick={saveDraft}
            className="hidden"
          >
            Save Draft
          </button>
        </form>
      </Form>
    </JobFormProvider>
  );
};

export default JobPostingForm;
