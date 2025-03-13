/**
 * Tipos comunes para las integraciones de API de redes sociales
 */

export interface AdContent {
  title: string;
  description: string;
  imageUrl?: string;
  videoUrl?: string;
  callToAction: string;
  landingPageUrl: string;
}

export interface TargetAudience {
  locations: string[];
  ageRange: {
    min: number;
    max: number;
  };
  genders: ('male' | 'female' | 'all')[];
  interests: string[];
  jobTitles?: string[];
  educationLevels?: string[];
  languages?: string[];
}

export interface AdCampaign {
  name: string;
  startDate: Date;
  endDate: Date;
  budget: number;
  dailyBudget?: number;
  content: AdContent;
  targetAudience: TargetAudience;
  platform: SocialPlatform;
  status: 'draft' | 'pending' | 'active' | 'paused' | 'completed' | 'error';
}

export type SocialPlatform = 'meta' | 'x' | 'google' | 'tiktok' | 'snapchat';

export interface ApiErrorDetail {
  code: string;
  message: string;
  platform?: SocialPlatform;
  statusCode?: number;
  originalError?: unknown;
  retryable?: boolean;
  rateLimited?: boolean;
  authError?: boolean;
  recommendedAction?: string;
}

export interface ApiResponse {
  success: boolean;
  data?: Record<string, unknown>;
  error?: ApiErrorDetail;
  // Metadata for pagination and rate limiting
  meta?: {
    pagination?: {
      hasNext: boolean;
      hasPrevious: boolean;
      totalCount?: number;
      nextCursor?: string;
      previousCursor?: string;
    };
    rateLimit?: {
      limit: number;
      remaining: number;
      resetAt: Date | string;
    };
    requestId?: string;
  };
}

export interface SocialMediaApi {
  createAd(campaign: AdCampaign): Promise<ApiResponse>;
  updateAd(adId: string, campaign: Partial<AdCampaign>): Promise<ApiResponse>;
  deleteAd(adId: string): Promise<ApiResponse>;
  getAdStatus(adId: string): Promise<ApiResponse>;
  getAdPerformance(adId: string, metrics: string[]): Promise<ApiResponse>;
}
