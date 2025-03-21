
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchDashboardMetrics } from '@/services/metricsService';
import { useToast } from '@/components/ui/use-toast';
import { AreaChart, BarChart } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import MetricsChart from './metrics/MetricsChart';

const ChartSection: React.FC = () => {
  const { toast } = useToast();
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboardMetrics'],
    queryFn: fetchDashboardMetrics,
    meta: {
      onError: (error: Error) => {
        toast({
          title: "Error loading metrics",
          description: "Could not load dashboard metrics. Please try again.",
          variant: "destructive"
        });
      }
    }
  });

  if (isLoading) {
    return (
      <div className="py-4">
        <h2 className="text-2xl font-semibold mb-4">Dashboard Overview</h2>
        <Card>
          <CardContent className="p-8 flex justify-center items-center">
            <p className="text-muted-foreground">Loading metrics data...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="py-4">
        <h2 className="text-2xl font-semibold mb-4">Dashboard Overview</h2>
        <Card>
          <CardContent className="p-8">
            <p className="text-muted-foreground">Could not load metrics data. Please try again later.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="py-4">
      <h2 className="text-2xl font-semibold mb-4">Dashboard Overview</h2>
      
      <Tabs defaultValue="campaigns" className="w-full">
        <TabsList>
          <TabsTrigger value="campaigns">Campaign Activity</TabsTrigger>
          <TabsTrigger value="applications">Application Rate</TabsTrigger>
        </TabsList>
        
        <TabsContent value="campaigns" className="mt-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Campaign Performance</CardTitle>
                  <CardDescription>Monthly campaign metrics</CardDescription>
                </div>
                <BarChart className="h-4 w-4 text-muted-foreground" />
              </div>
            </CardHeader>
            <CardContent>
              <MetricsChart 
                data={data.campaignData}
                chartType="bar"
                color="#8b5cf6"
                height={250}
                showGrid={true}
                showLegend={false}
              />
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="applications" className="mt-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Application Rate</CardTitle>
                  <CardDescription>Daily application submissions</CardDescription>
                </div>
                <AreaChart className="h-4 w-4 text-muted-foreground" />
              </div>
            </CardHeader>
            <CardContent>
              <MetricsChart 
                data={data.applicationsData}
                chartType="area"
                color="#10b981"
                height={250}
                showGrid={true}
                showLegend={false}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ChartSection;
