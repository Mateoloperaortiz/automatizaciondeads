
import React from 'react';
import { Textarea } from '@/components/ui/textarea';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from '@/components/ui/form';
import { useJobForm } from '../JobFormContext';
import { Card } from '@/components/ui/card';

interface JobDetailsSectionProps {
  readOnly?: boolean;
  initialData?: {
    description?: string;
    requirements?: string;
  };
}

const JobDetailsSection: React.FC<JobDetailsSectionProps> = ({ 
  readOnly = false, 
  initialData 
}) => {
  const { form } = useJobForm();
  
  // For readonly mode, we display the data without the form
  if (readOnly) {
    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-sm font-medium mb-2">Job Description</h3>
          <Card className="p-4 text-sm">
            {initialData?.description || "No description available"}
          </Card>
        </div>
        
        <div>
          <h3 className="text-sm font-medium mb-2">Requirements</h3>
          <Card className="p-4 text-sm">
            {initialData?.requirements || "No requirements available"}
          </Card>
        </div>
      </div>
    );
  }
  
  if (!form) return null;
  
  return (
    <div className="space-y-6">
      <FormField
        control={form.control}
        name="description"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Job Description</FormLabel>
            <FormControl>
              <Textarea
                placeholder="Describe the role, responsibilities, and what a typical day looks like"
                rows={4}
                {...field}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      
      <FormField
        control={form.control}
        name="requirements"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Requirements</FormLabel>
            <FormControl>
              <Textarea
                placeholder="List the skills, experience, and qualifications needed"
                rows={4}
                {...field}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
};

export default JobDetailsSection;
