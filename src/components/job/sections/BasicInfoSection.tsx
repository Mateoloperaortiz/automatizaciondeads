
import React from 'react';
import { Input } from '@/components/ui/input';
import { 
  FormControl, 
  FormDescription, 
  FormField, 
  FormItem, 
  FormLabel, 
  FormMessage 
} from '@/components/ui/form';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { useJobForm } from '../JobFormContext';
import { Card } from '@/components/ui/card';

interface BasicInfoSectionProps {
  readOnly?: boolean;
  initialData?: {
    title?: string;
    company?: string;
    location?: string;
    jobType?: string;
    salary?: string;
    applicationUrl?: string;
  };
}

const BasicInfoSection: React.FC<BasicInfoSectionProps> = ({ 
  readOnly = false, 
  initialData 
}) => {
  const { form } = useJobForm();
  
  // For readonly mode, we display the data without the form
  if (readOnly) {
    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-sm font-medium mb-2">Job Title</h3>
          <Card className="p-4 text-sm">
            {initialData?.title || "N/A"}
          </Card>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-sm font-medium mb-2">Company</h3>
            <Card className="p-4 text-sm">
              {initialData?.company || "N/A"}
            </Card>
          </div>
          
          <div>
            <h3 className="text-sm font-medium mb-2">Location</h3>
            <Card className="p-4 text-sm">
              {initialData?.location || "N/A"}
            </Card>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-sm font-medium mb-2">Job Type</h3>
            <Card className="p-4 text-sm capitalize">
              {initialData?.jobType?.replace('-', ' ') || "N/A"}
            </Card>
          </div>
          
          <div>
            <h3 className="text-sm font-medium mb-2">Salary Range</h3>
            <Card className="p-4 text-sm">
              {initialData?.salary || "Not specified"}
            </Card>
          </div>
        </div>
        
        <div>
          <h3 className="text-sm font-medium mb-2">Application URL</h3>
          <Card className="p-4 text-sm">
            {initialData?.applicationUrl ? (
              <a 
                href={initialData.applicationUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                {initialData.applicationUrl}
              </a>
            ) : (
              "No application URL provided"
            )}
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
        name="title"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Job Title</FormLabel>
            <FormControl>
              <Input placeholder="Senior Software Engineer" {...field} />
            </FormControl>
            <FormDescription>
              The main title for your job posting
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
      
      <div className="grid grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name="company"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Company</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <FormField
          control={form.control}
          name="location"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Location</FormLabel>
              <FormControl>
                <Input placeholder="City, Country or Remote" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name="jobType"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Job Type</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select job type" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="full-time">Full-time</SelectItem>
                  <SelectItem value="part-time">Part-time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                  <SelectItem value="freelance">Freelance</SelectItem>
                  <SelectItem value="internship">Internship</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <FormField
          control={form.control}
          name="salary"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Salary Range (Optional)</FormLabel>
              <FormControl>
                <Input placeholder="$80,000 - $120,000" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
      
      <FormField
        control={form.control}
        name="applicationUrl"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Application URL</FormLabel>
            <FormControl>
              <Input placeholder="https://careers.company.com/job/123" {...field} />
            </FormControl>
            <FormDescription>
              Where candidates can apply
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
};

export default BasicInfoSection;
