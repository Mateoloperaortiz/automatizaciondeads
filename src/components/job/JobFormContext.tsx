
import React, { createContext, useContext } from 'react';
import { UseFormReturn } from 'react-hook-form';
import { z } from 'zod';

// Define form schema with Zod
export const jobFormSchema = z.object({
  title: z.string().min(5, { message: 'Title must be at least 5 characters' }),
  company: z.string().min(2, { message: 'Company name is required' }),
  location: z.string().min(2, { message: 'Location is required' }),
  jobType: z.string(),
  description: z.string().min(20, { message: 'Description must be at least 20 characters' }),
  requirements: z.string().min(20, { message: 'Requirements must be at least 20 characters' }),
  salary: z.string().optional(),
  applicationUrl: z.string().url({ message: 'Please enter a valid URL' }),
  platforms: z.array(z.string()).min(1, { message: 'Select at least one platform' }),
});

export type JobFormValues = z.infer<typeof jobFormSchema>;

type JobFormContextType = {
  form: UseFormReturn<JobFormValues> | null;
  isSubmitting: boolean;
  onSubmit?: (data: JobFormValues) => void;
};

const JobFormContext = createContext<JobFormContextType>({
  form: null,
  isSubmitting: false,
});

export const useJobForm = () => useContext(JobFormContext);

export const JobFormProvider: React.FC<{
  children: React.ReactNode;
  form: UseFormReturn<JobFormValues>;
  isSubmitting: boolean;
  onSubmit?: (data: JobFormValues) => void;
}> = ({ children, form, isSubmitting, onSubmit }) => {
  return (
    <JobFormContext.Provider value={{ form, isSubmitting, onSubmit }}>
      {children}
    </JobFormContext.Provider>
  );
};
