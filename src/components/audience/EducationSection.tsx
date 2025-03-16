
import React from 'react';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card';
import { GraduationCap } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { X } from 'lucide-react';
import { useAudience } from './AudienceContext';

const EducationSection: React.FC = () => {
  const { audience, handleAddItem, handleRemoveItem } = useAudience();
  
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center space-x-2">
          <GraduationCap className="h-4 w-4 text-muted-foreground" />
          <CardTitle className="text-lg">Education</CardTitle>
        </div>
        <CardDescription>
          Target audience based on education level
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Select 
            defaultValue={audience.education?.[0]}
            onValueChange={(value) => {
              if (!audience.education?.includes(value)) {
                handleAddItem('education', value);
              }
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select education level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="High school">High school</SelectItem>
              <SelectItem value="Associate degree">Associate degree</SelectItem>
              <SelectItem value="Bachelor degree">Bachelor degree</SelectItem>
              <SelectItem value="Master degree">Master degree</SelectItem>
              <SelectItem value="Doctorate">Doctorate</SelectItem>
            </SelectContent>
          </Select>
          
          <div className="flex flex-wrap gap-2 mt-2">
            {audience.education?.map((edu, index) => (
              <Badge 
                key={index} 
                variant="secondary"
                className="pl-2 pr-1 py-1 flex items-center space-x-1"
              >
                <span>{edu}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-4 w-4 rounded-full"
                  onClick={() => handleRemoveItem('education', index)}
                >
                  <X className="h-2 w-2" />
                </Button>
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default EducationSection;
