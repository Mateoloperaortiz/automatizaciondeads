
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { TrendingUp, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import { useQuery } from '@tanstack/react-query';
import { fetchDashboardMetrics } from '@/services/metricsService';
import { useToast } from '@/hooks/use-toast';

const CampaignsOverview = () => {
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

  if (error) {
    return (
      <AnimatedTransition type="slide-up" delay={0.2} className="lg:col-span-2">
        <Card className="overflow-hidden">
          <div className="bg-secondary px-6 py-4">
            <h2 className="text-xl font-medium">Campaigns Overview</h2>
          </div>
          <CardContent className="p-6 text-center py-12">
            <p className="text-muted-foreground">Failed to load campaign data</p>
            <Button 
              variant="outline" 
              className="mt-4"
              onClick={() => window.location.reload()}
            >
              Retry
            </Button>
          </CardContent>
        </Card>
      </AnimatedTransition>
    );
  }

  return (
    <AnimatedTransition type="slide-up" delay={0.2} className="lg:col-span-2">
      <Card className="overflow-hidden">
        <div className="bg-secondary px-6 py-4">
          <h2 className="text-xl font-medium">Campaigns Overview</h2>
        </div>
        <CardContent className="p-6">
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary/70" />
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Active Campaigns</p>
                  <h3 className="text-2xl font-bold">{data?.activeCampaigns}</h3>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Impressions</p>
                  <h3 className="text-2xl font-bold">{data?.totalImpressions}</h3>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Applications</p>
                  <h3 className="text-2xl font-bold">{data?.applications}</h3>
                </div>
              </div>
              
              <Separator />
              
              {/* Top Performing Campaigns */}
              <div>
                <h3 className="text-lg font-medium mb-4">Top Performing</h3>
                <div className="space-y-4">
                  <div className="bg-secondary/50 p-4 rounded-md">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium">Senior Frontend Developer</h4>
                        <p className="text-sm text-muted-foreground">LinkedIn, Meta</p>
                      </div>
                      <div className="text-right">
                        <span className="inline-flex items-center bg-green-500/10 text-green-600 text-xs px-2 py-1 rounded-full">
                          <TrendingUp className="w-3 h-3 mr-1" /> 12% CTR
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-secondary/50 p-4 rounded-md">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium">UI/UX Designer</h4>
                        <p className="text-sm text-muted-foreground">LinkedIn, Twitter</p>
                      </div>
                      <div className="text-right">
                        <span className="inline-flex items-center bg-green-500/10 text-green-600 text-xs px-2 py-1 rounded-full">
                          <TrendingUp className="w-3 h-3 mr-1" /> 8.5% CTR
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end">
                <Link to="/analytics">
                  <Button variant="outline">
                    View All Analytics
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </AnimatedTransition>
  );
};

export default CampaignsOverview;
