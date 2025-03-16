
import React from 'react';
import {
  FormControl,
  FormField,
  FormItem,
  FormMessage
} from '@/components/ui/form';
import PlatformSelector from '@/components/platform/PlatformSelector';
import { useJobForm } from '../JobFormContext';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Form } from '@/components/ui/form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { platforms } from '@/data/platformsData';

interface PlatformSectionProps {
  standalone?: boolean;
  readOnly?: boolean;
  initialPlatforms?: string[];
}

const platformSchema = z.object({
  platforms: z.array(z.string()).min(1, { message: 'Select at least one platform' })
});

type PlatformFormValues = z.infer<typeof platformSchema>;

const PlatformSection: React.FC<PlatformSectionProps> = ({ 
  standalone = false, 
  readOnly = false,
  initialPlatforms = []
}) => {
  const { form } = useJobForm();
  
  // Only create standalone form if not using the JobFormContext
  const standaloneForm = useForm<PlatformFormValues>({
    resolver: zodResolver(platformSchema),
    defaultValues: {
      platforms: initialPlatforms,
    },
  });
  
  // Use either the form from context or the standalone form
  const activeForm = standalone ? standaloneForm : form;
  
  if (!activeForm && !readOnly) return null;
  
  // If read-only, display platforms without interaction
  if (readOnly) {
    // Find platform names from IDs
    const selectedPlatforms = platforms
      .filter(p => initialPlatforms?.includes(p.id))
      .map(p => p.name);
    
    return (
      <div className="animate-fade-in">
        <div className="flex flex-wrap gap-2">
          {selectedPlatforms.length > 0 ? (
            selectedPlatforms.map((name, index) => (
              <Badge key={index} variant="outline" className="px-3 py-1 text-sm">
                {name}
              </Badge>
            ))
          ) : (
            <Card className="p-4 w-full text-center">
              <p className="text-muted-foreground">No platforms selected</p>
            </Card>
          )}
        </div>
      </div>
    );
  }
  
  // If standalone, we render a complete form, otherwise just the field
  if (standalone) {
    return (
      <div className="animate-fade-in">
        <Form {...standaloneForm}>
          <form className="space-y-8">
            <h3 className="text-lg font-medium mb-4">Select Platforms</h3>
            <FormField
              control={standaloneForm.control}
              name="platforms"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <PlatformSelector
                      value={field.value}
                      onChange={field.onChange}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </form>
        </Form>
      </div>
    );
  }
  
  return (
    <div>
      <h3 className="text-lg font-medium mb-4">Select Platforms</h3>
      <FormField
        control={form.control}
        name="platforms"
        render={({ field }) => (
          <FormItem>
            <FormControl>
              <PlatformSelector
                value={field.value}
                onChange={field.onChange}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
};

export default PlatformSection;
