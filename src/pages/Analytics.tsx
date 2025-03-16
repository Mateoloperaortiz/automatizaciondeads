
import React, { useState } from 'react';
import AnalyticsHeader from '@/components/analytics/AnalyticsHeader';
import OverviewMetrics from '@/components/analytics/OverviewMetrics';
import PerformanceCharts from '@/components/analytics/PerformanceCharts';
import PlatformDistribution from '@/components/analytics/PlatformDistribution';
import CampaignDetails from '@/components/analytics/CampaignDetails';
import DateRangeFilter from '@/components/analytics/DateRangeFilter';
import ExportShareOptions from '@/components/analytics/ExportShareOptions';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useIsMobile } from '@/hooks/use-mobile';
import { Card, CardContent } from '@/components/ui/card';

const Analytics: React.FC = () => {
  const isMobile = useIsMobile();
  const [currentView, setCurrentView] = useState<'overview' | 'details'>('overview');
  const [dateRange, setDateRange] = useState({
    startDate: new Date(new Date().setDate(new Date().getDate() - 30)),
    endDate: new Date(),
    label: 'Last 30 days'
  });

  const handleDateRangeChange = (startDate: Date, endDate: Date, label: string) => {
    setDateRange({ startDate, endDate, label });
    // In a real app, you would fetch new data based on the date range here
  };

  return (
    <div className="container max-w-7xl mx-auto py-6 px-4 md:px-6 lg:py-10 space-y-6">
      <AnalyticsHeader 
        title="Analytics Dashboard"
        description="Get detailed insights about your campaign performance"
      />
      
      <Card className="hover-lift">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <h3 className="text-lg font-medium">{dateRange.label}</h3>
            <div className="flex flex-col sm:flex-row gap-3">
              <DateRangeFilter onRangeChange={handleDateRangeChange} />
              <ExportShareOptions dateRange={dateRange} />
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Tabs 
        defaultValue="overview" 
        className="w-full"
        onValueChange={(value) => setCurrentView(value as 'overview' | 'details')}
      >
        <TabsList className="mb-6 w-full sm:w-auto">
          <TabsTrigger value="overview" className="flex-1 sm:flex-initial">Overview</TabsTrigger>
          <TabsTrigger value="details" className="flex-1 sm:flex-initial">Campaign Details</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-6 mt-2">
          {/* Overview Metrics */}
          <OverviewMetrics />
          
          {/* Charts Section */}
          <PerformanceCharts />
          
          {/* Platform Distribution */}
          <PlatformDistribution />
        </TabsContent>
        
        <TabsContent value="details" className="mt-2">
          {/* Detailed Campaign Analytics */}
          <CampaignDetails />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Analytics;
