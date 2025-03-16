
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchDashboardMetrics } from '@/services/metricsService';
import { useToast } from '@/hooks/use-toast';

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

  return (
    <div className="py-4">
      <h2 className="text-2xl font-semibold mb-4">Dashboard Overview</h2>
      <p className="text-muted-foreground">Charts have been temporarily removed.</p>
    </div>
  );
};

export default ChartSection;
