
import { simulateNetworkDelay } from './mockDatabase';

export interface ChartDataPoint {
  name: string;
  value: number;
}

export interface DashboardMetrics {
  activeCampaigns: number;
  totalImpressions: string;
  applications: number;
  campaignData: ChartDataPoint[];
  applicationsData: ChartDataPoint[];
}

// Metrics data service
export const fetchDashboardMetrics = async (): Promise<DashboardMetrics> => {
  await simulateNetworkDelay(700);
  
  return {
    activeCampaigns: 9,
    totalImpressions: "245.8K",
    applications: 83,
    campaignData: [
      { name: 'Jan', value: 12 },
      { name: 'Feb', value: 25 },
      { name: 'Mar', value: 18 },
      { name: 'Apr', value: 30 },
      { name: 'May', value: 42 },
      { name: 'Jun', value: 35 },
      { name: 'Jul', value: 55 }
    ],
    applicationsData: [
      { name: 'Mon', value: 10 },
      { name: 'Tue', value: 15 },
      { name: 'Wed', value: 35 },
      { name: 'Thu', value: 42 },
      { name: 'Fri', value: 29 },
      { name: 'Sat', value: 12 },
      { name: 'Sun', value: 8 }
    ]
  };
};
