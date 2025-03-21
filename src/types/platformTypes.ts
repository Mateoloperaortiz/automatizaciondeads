
export interface ApiHealthMetrics {
  status: 'healthy' | 'degraded' | 'down';
  quotaUsed: number;
  quotaLimit: number;
  rateLimit: number;
  rateLimitRemaining: number;
  lastSyncTime: string;
  resetTime: string;
  averageResponseTime: number;
}

export interface PlatformStatus extends ApiHealthMetrics {
  platformId: string;
}

// Helper to calculate percentage
export const calculatePercentage = (used: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((used / total) * 100);
};

// Format date to relative time (e.g., "2 hours ago")
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.round(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`;
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
  
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
};
