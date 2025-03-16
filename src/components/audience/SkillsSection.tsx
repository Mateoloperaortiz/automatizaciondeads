
import React from 'react';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card';
import { Users } from 'lucide-react';
import TagInput from './TagInput';
import { useAudience } from './AudienceContext';

const SkillsSection: React.FC = () => {
  const { audience } = useAudience();
  
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center space-x-2">
          <Users className="h-4 w-4 text-muted-foreground" />
          <CardTitle className="text-lg">Skills</CardTitle>
        </div>
        <CardDescription>
          Target audience based on professional skills
        </CardDescription>
      </CardHeader>
      <CardContent>
        <TagInput 
          field="skills" 
          placeholder="Add a skill" 
          items={audience.skills || []} 
        />
      </CardContent>
    </Card>
  );
};

export default SkillsSection;
