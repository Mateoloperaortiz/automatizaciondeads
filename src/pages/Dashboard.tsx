
import React from 'react';
import { BarChart3, Users, Calendar, TrendingUp } from 'lucide-react';
import { MetricsSummary } from '@/components/dashboard/metrics';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import DashboardHeader from '@/components/dashboard/DashboardHeader';
import ChartSection from '@/components/dashboard/ChartSection';
import CampaignTabs from '@/components/dashboard/CampaignTabs';

const Dashboard: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-24">
      <AnimatedTransition type="fade" className="space-y-8">
        <DashboardHeader />

        <AnimatedTransition type="slide-up" delay={0.1}>
          <MetricsSummary metrics={[
            {
              label: 'Total Campaigns',
              value: '24',
              change: {
                value: 12,
                direction: 'up'
              },
              icon: <BarChart3 className="h-4 w-4" />
            },
            {
              label: 'Active Campaigns',
              value: '7',
              change: {
                value: 3,
                direction: 'up'
              },
              icon: <TrendingUp className="h-4 w-4" />
            },
            {
              label: 'Total Applicants',
              value: '1,482',
              change: {
                value: 8,
                direction: 'up'
              },
              icon: <Users className="h-4 w-4" />
            },
            {
              label: 'Scheduled Posts',
              value: '12',
              change: {
                value: 2,
                direction: 'down'
              },
              icon: <Calendar className="h-4 w-4" />
            }
          ]} />
        </AnimatedTransition>
        
        <ChartSection />
        
        <AnimatedTransition type="slide-up" delay={0.4}>
          <CampaignTabs />
        </AnimatedTransition>
      </AnimatedTransition>
    </div>
  );
};

export default Dashboard;
