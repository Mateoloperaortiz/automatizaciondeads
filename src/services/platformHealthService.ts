
import { simulateNetworkDelay } from './mockDatabase';
import { ApiHealthMetrics, PlatformStatus } from '@/types/platformTypes';
import { platforms } from '@/data/platformsData';

// Mock API health metrics for connected platforms
const mockApiHealthMetrics: Record<string, ApiHealthMetrics> = {
  meta: {
    status: 'healthy',
    quotaUsed: 8500,
    quotaLimit: 10000,
    rateLimit: 100,
    rateLimitRemaining: 65,
    lastSyncTime: new Date(Date.now() - 45 * 60000).toISOString(), // 45 minutes ago
    resetTime: new Date(Date.now() + 6 * 3600000).toISOString(), // 6 hours from now
    averageResponseTime: 187
  },
  twitter: {
    status: 'degraded',
    quotaUsed: 950,
    quotaLimit: 1000,
    rateLimit: 50,
    rateLimitRemaining: 5,
    lastSyncTime: new Date(Date.now() - 2 * 3600000).toISOString(), // 2 hours ago
    resetTime: new Date(Date.now() + 2 * 3600000).toISOString(), // 2 hours from now
    averageResponseTime: 356
  },
  linkedin: {
    status: 'healthy',
    quotaUsed: 3200,
    quotaLimit: 5000,
    rateLimit: 80,
    rateLimitRemaining: 45,
    lastSyncTime: new Date(Date.now() - 30 * 60000).toISOString(), // 30 minutes ago
    resetTime: new Date(Date.now() + 5 * 3600000).toISOString(), // 5 hours from now
    averageResponseTime: 209
  },
  google: {
    status: 'healthy',
    quotaUsed: 1500,
    quotaLimit: 5000,
    rateLimit: 120,
    rateLimitRemaining: 98,
    lastSyncTime: new Date(Date.now() - 15 * 60000).toISOString(), // 15 minutes ago
    resetTime: new Date(Date.now() + 12 * 3600000).toISOString(), // 12 hours from now
    averageResponseTime: 143
  },
  tiktok: {
    status: 'down',
    quotaUsed: 980,
    quotaLimit: 1000,
    rateLimit: 60,
    rateLimitRemaining: 0,
    lastSyncTime: new Date(Date.now() - 5 * 3600000).toISOString(), // 5 hours ago
    resetTime: new Date(Date.now() + 1 * 3600000).toISOString(), // 1 hour from now
    averageResponseTime: 523
  },
  snapchat: {
    status: 'healthy',
    quotaUsed: 1200,
    quotaLimit: 3000,
    rateLimit: 90,
    rateLimitRemaining: 72,
    lastSyncTime: new Date(Date.now() - 90 * 60000).toISOString(), // 90 minutes ago
    resetTime: new Date(Date.now() + 8 * 3600000).toISOString(), // 8 hours from now
    averageResponseTime: 231
  }
};

// Fetch API health metrics for a specific platform
export const fetchPlatformHealth = async (platformId: string): Promise<ApiHealthMetrics | null> => {
  await simulateNetworkDelay(300);
  return mockApiHealthMetrics[platformId] || null;
};

// Fetch API health metrics for all connected platforms
export const fetchAllPlatformHealth = async (connectedPlatformIds: string[]): Promise<PlatformStatus[]> => {
  await simulateNetworkDelay(600);
  
  return connectedPlatformIds
    .filter(id => mockApiHealthMetrics[id])
    .map(id => ({
      platformId: id,
      ...mockApiHealthMetrics[id]
    }));
};

// Update platform connection status in the mock database
export const updatePlatformConnection = async (
  platformId: string, 
  isConnected: boolean
): Promise<boolean> => {
  await simulateNetworkDelay(800);
  
  // In a real implementation, this would update the database
  // For now, we just simulate the update
  
  return true;
};
