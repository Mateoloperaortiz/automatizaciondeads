
import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card';
import { useAudience } from './AudienceContext';

const AudienceInformation: React.FC = () => {
  const { audience, setAudience } = useAudience();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Audience Information</CardTitle>
        <CardDescription>
          Configure the basic information for your target audience
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="audience-name">Audience Name</Label>
          <Input
            id="audience-name"
            value={audience.name}
            onChange={(e) => setAudience({ ...audience, name: e.target.value })}
            placeholder="E.g., Tech professionals in New York"
          />
        </div>
        
        <div className="space-y-4">
          <div>
            <Label className="mb-2 block">Age Range</Label>
            <div className="flex items-center space-x-4">
              <div className="w-12 text-center font-medium">{audience.ageRange?.[0]}</div>
              <Slider
                value={audience.ageRange}
                min={18}
                max={65}
                step={1}
                onValueChange={(value) => setAudience({ ...audience, ageRange: value as [number, number] })}
                className="flex-1"
              />
              <div className="w-12 text-center font-medium">{audience.ageRange?.[1]}</div>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label>Experience (years)</Label>
            <div className="flex items-center space-x-4">
              <div className="w-12 text-center font-medium">{audience.experienceYears?.[0]}</div>
              <Slider
                value={audience.experienceYears}
                min={0}
                max={20}
                step={1}
                onValueChange={(value) => setAudience({ ...audience, experienceYears: value as [number, number] })}
                className="flex-1"
              />
              <div className="w-12 text-center font-medium">{audience.experienceYears?.[1]}</div>
            </div>
          </div>
        </div>
        
        <div className="space-y-2">
          <Label>Enable Advanced Targeting</Label>
          <div className="flex items-center space-x-2">
            <Switch
              checked={audience.isAdvancedTargeting}
              onCheckedChange={(checked) => setAudience({ ...audience, isAdvancedTargeting: checked })}
            />
            <span className="text-sm text-muted-foreground">
              {audience.isAdvancedTargeting ? 'Advanced targeting enabled' : 'Advanced targeting disabled'}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AudienceInformation;
