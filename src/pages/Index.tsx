
import React from 'react';
import CampaignsOverview from '@/components/dashboard/CampaignsOverview';
import UpcomingEvents from '@/components/dashboard/UpcomingEvents';
import CampaignTabs from '@/components/dashboard/CampaignTabs';
import NotificationDemo from '@/components/notifications/NotificationDemo';
import WelcomeBanner from '@/components/dashboard/WelcomeBanner';
import OverviewMetrics from '@/components/analytics/OverviewMetrics';
import AnimatedTransition from '@/components/ui/AnimatedTransition';

const Index = () => {
  return (
    <div className="container max-w-7xl mx-auto py-8 px-4 md:px-6 lg:py-12 text-left space-y-8">
      {/* Welcome Banner */}
      <WelcomeBanner />
      
      {/* Quick Metrics Overview */}
      <AnimatedTransition type="slide-up" delay={0.1}>
        <div className="mb-2">
          <h2 className="text-xl font-medium mb-4">Performance Overview</h2>
          <OverviewMetrics />
        </div>
      </AnimatedTransition>
      
      {/* Campaign Tabs */}
      <AnimatedTransition type="slide-up" delay={0.2}>
        <div>
          <CampaignTabs />
        </div>
      </AnimatedTransition>
      
      {/* Two Column Layout */}
      <AnimatedTransition type="slide-up" delay={0.3}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
          {/* Active Campaigns Summary */}
          <CampaignsOverview />
          
          {/* Right Column - Stacked */}
          <div className="lg:col-span-1 space-y-6">
            {/* Upcoming Events Calendar */}
            <UpcomingEvents />

            {/* Notification Demo */}
            <AnimatedTransition type="slide-up" delay={0.4}>
              <NotificationDemo />
            </AnimatedTransition>
          </div>
        </div>
      </AnimatedTransition>
    </div>
  );
};

export default Index;
