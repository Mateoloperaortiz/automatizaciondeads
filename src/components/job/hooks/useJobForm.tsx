import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useToast } from '@/components/ui/use-toast';
import { useNavigate } from 'react-router-dom';
import { jobFormSchema, JobFormValues } from '../JobFormContext';
import { updateCampaign } from '@/services/campaignService';

interface UseJobFormProps {
  initialValues?: Partial<JobFormValues>;
  isEditing?: boolean;
  campaignId?: string;
}

const useJobForm = ({ initialValues, isEditing = false, campaignId }: UseJobFormProps) => {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  
  const form = useForm<JobFormValues>({
    resolver: zodResolver(jobFormSchema),
    defaultValues: {
      title: '',
      company: 'Magneto',
      location: '',
      jobType: 'full-time',
      description: '',
      requirements: '',
      salary: '',
      applicationUrl: '',
      platforms: [],
      ...initialValues
    },
  });
  
  useEffect(() => {
    if (initialValues) {
      Object.entries(initialValues).forEach(([name, value]) => {
        form.setValue(name as keyof JobFormValues, value);
      });
    }
  }, [initialValues, form]);
  
  const onSubmit = async (data: JobFormValues) => {
    setIsSubmitting(true);
    
    try {
      if (isEditing && campaignId) {
        await updateCampaign(campaignId, { jobDetails: data });
        console.log('Campaign updated:', campaignId, data);
      } else {
        console.log('Form data submitted:', data);
      }
      
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast({
        title: isEditing ? "Campaign updated" : "Campaign created",
        description: isEditing 
          ? `Your job ad for "${data.title}" has been updated.`
          : `Your job ad for "${data.title}" has been created and scheduled for publication.`,
      });
      
      if (isEditing && campaignId) {
        navigate(`/campaign/${campaignId}`);
      } else {
        form.reset();
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      toast({
        title: "Error",
        description: "There was a problem saving your changes. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const saveDraft = () => {
    const currentValues = form.getValues();
    console.log('Draft saved:', currentValues);
    
    if (isEditing) {
      toast({
        title: "Changes saved",
        description: "Your campaign changes have been saved as a draft.",
      });
    }
  };

  return {
    form,
    isSubmitting,
    onSubmit,
    saveDraft
  };
};

export default useJobForm;
