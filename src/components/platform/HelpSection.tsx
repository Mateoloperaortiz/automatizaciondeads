
import React from 'react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

const HelpSection: React.FC = () => {
  return (
    <div className="mt-12">
      <Separator className="my-8" />
      <h2 className="text-xl font-medium mb-4">API Configuration Help</h2>
      <div className="bg-muted rounded-lg p-6">
        <h3 className="font-medium mb-2">Need help setting up platform connections?</h3>
        <p className="text-muted-foreground mb-4">
          Our documentation provides step-by-step guides for connecting each platform's API.
        </p>
        <div className="grid md:grid-cols-2 gap-4">
          <ul className="list-disc list-inside space-y-2 text-sm text-muted-foreground">
            <li>Learn how to create a Meta Business Developer account</li>
            <li>Set up X (Twitter) developer credentials</li>
            <li>Configure LinkedIn Recruiter API access</li>
          </ul>
          <ul className="list-disc list-inside space-y-2 text-sm text-muted-foreground">
            <li>Connect to the Google Ads API</li>
            <li>Set up TikTok Business API credentials</li>
            <li>Configure Snapchat Business API access</li>
          </ul>
        </div>
        <Button variant="secondary" className="mt-4">
          View Documentation
        </Button>
      </div>
    </div>
  );
};

export default HelpSection;
