
import React from 'react';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card';
import { Briefcase } from 'lucide-react';
import TagInput from './TagInput';
import { useAudience } from './AudienceContext';

const JobTitlesSection: React.FC = () => {
  const { audience } = useAudience();
  
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center space-x-2">
          <Briefcase className="h-4 w-4 text-muted-foreground" />
          <CardTitle className="text-lg">Job Titles</CardTitle>
        </div>
        <CardDescription>
          Target audience based on job titles and roles
        </CardDescription>
      </CardHeader>
      <CardContent>
        <TagInput 
          field="jobTitles" 
          placeholder="Add a job title" 
          items={audience.jobTitles || []} 
        />
      </CardContent>
    </Card>
  );
};

export default JobTitlesSection;
