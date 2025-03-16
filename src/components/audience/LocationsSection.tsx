
import React from 'react';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card';
import { MapPin } from 'lucide-react';
import TagInput from './TagInput';
import { useAudience } from './AudienceContext';

const LocationsSection: React.FC = () => {
  const { audience } = useAudience();
  
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center space-x-2">
          <MapPin className="h-4 w-4 text-muted-foreground" />
          <CardTitle className="text-lg">Locations</CardTitle>
        </div>
        <CardDescription>
          Target audience based on geographic locations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <TagInput 
          field="locations" 
          placeholder="Add a location" 
          items={audience.locations || []} 
        />
      </CardContent>
    </Card>
  );
};

export default LocationsSection;
