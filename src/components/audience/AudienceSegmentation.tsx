
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { Save } from 'lucide-react';
import { AudienceData, AudienceProvider, defaultAudience } from './AudienceContext';
import AudienceInformation from './AudienceInformation';
import LocationsSection from './LocationsSection';
import JobTitlesSection from './JobTitlesSection';
import SkillsSection from './SkillsSection';
import EducationSection from './EducationSection';
import AdvancedTargeting from './AdvancedTargeting';

interface AudienceSegmentationProps {
  initialValues?: AudienceData;
}

const AudienceSegmentation: React.FC<AudienceSegmentationProps> = ({ initialValues }) => {
  const { toast } = useToast();
  const [saving, setSaving] = useState(false);
  
  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      toast({
        title: "Audience saved",
        description: "Your audience segmentation has been saved successfully.",
      });
    }, 1000);
  };
  
  return (
    <AudienceProvider initialValues={initialValues}>
      <div className="space-y-6 animate-fade-in">
        <Tabs defaultValue="basic" className="w-full">
          <TabsList className="mb-6">
            <TabsTrigger value="basic">Basic Targeting</TabsTrigger>
            <TabsTrigger value="advanced" disabled={!initialValues?.isAdvancedTargeting}>
              Advanced Targeting
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="basic" className="space-y-6">
            <AudienceInformation />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <LocationsSection />
              <JobTitlesSection />
              <SkillsSection />
              <EducationSection />
            </div>
          </TabsContent>
          
          <TabsContent value="advanced">
            <AdvancedTargeting />
          </TabsContent>
        </Tabs>
        
        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={saving}>
            {saving ? (
              <>
                <Save className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Audience
              </>
            )}
          </Button>
        </div>
      </div>
    </AudienceProvider>
  );
};

export default AudienceSegmentation;
