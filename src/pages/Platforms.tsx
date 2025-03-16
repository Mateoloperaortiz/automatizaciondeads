
import React, { useState } from 'react';
import { platforms } from '@/data/platformsData';
import RefreshButton from '@/components/platform/RefreshButton';
import PlatformGrid from '@/components/platform/PlatformGrid';
import HelpSection from '@/components/platform/HelpSection';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const Platforms: React.FC = () => {
  const [view] = useState<'list'>('list');
  const [isRefreshing, setIsRefreshing] = useState(false);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-24 min-h-screen">
      <AnimatedTransition type="fade" className="space-y-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-medium tracking-tight">Platform Connections</h1>
            <p className="text-muted-foreground mt-1">
              Connect your social media platforms to automate job posting
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <RefreshButton isRefreshing={isRefreshing} setIsRefreshing={setIsRefreshing} />
          </div>
        </div>
        
        <Tabs defaultValue="all" className="w-full">
          <TabsList className="mb-6">
            <TabsTrigger value="all">All Platforms</TabsTrigger>
            <TabsTrigger value="connected">Connected</TabsTrigger>
            <TabsTrigger value="unconnected">Not Connected</TabsTrigger>
          </TabsList>
          
          <TabsContent value="all" className="mt-0">
            <PlatformGrid platforms={platforms} view={view} />
          </TabsContent>
          
          <TabsContent value="connected" className="mt-0">
            <PlatformGrid platforms={platforms} view={view} filterConnected={true} />
          </TabsContent>
          
          <TabsContent value="unconnected" className="mt-0">
            <PlatformGrid platforms={platforms} view={view} filterConnected={false} />
          </TabsContent>
        </Tabs>
        
        <HelpSection />
      </AnimatedTransition>
    </div>
  );
};

export default Platforms;
