
import React from 'react';
import { Card } from '@/components/ui/card';

interface AudienceData {
  ageRange?: number[];
  experienceYears?: number[];
  locations?: string[];
  skills?: string[];
}

interface AudienceDisplayProps {
  audience?: AudienceData;
}

const AudienceDisplay: React.FC<AudienceDisplayProps> = ({ audience }) => {
  if (!audience) {
    return (
      <Card className="p-6 text-center">
        <p className="text-muted-foreground">No audience data available</p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-medium mb-2">Demographics</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Age range: {audience.ageRange?.[0]} - {audience.ageRange?.[1]}
          </p>
          
          <h3 className="font-medium mb-2">Experience</h3>
          <p className="text-sm text-muted-foreground">
            {audience.experienceYears?.[0]} - {audience.experienceYears?.[1]} years
          </p>
        </div>
        
        <div>
          <h3 className="font-medium mb-2">Locations</h3>
          <div className="flex flex-wrap gap-2 mb-4">
            {audience.locations?.map((location, index) => (
              <div key={index} className="bg-muted px-2 py-1 rounded text-sm">
                {location}
              </div>
            ))}
          </div>
          
          <h3 className="font-medium mb-2">Skills</h3>
          <div className="flex flex-wrap gap-2">
            {audience.skills?.map((skill, index) => (
              <div key={index} className="bg-muted px-2 py-1 rounded text-sm">
                {skill}
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default AudienceDisplay;
