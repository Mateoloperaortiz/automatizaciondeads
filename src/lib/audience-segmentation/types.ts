/**
 * Tipos para la segmentación de audiencias
 */

export interface UserProfile {
  id: string;
  demographics: {
    age?: number;
    gender?: 'male' | 'female' | 'other';
    location?: string;
    language?: string;
    educationLevel?: string;
    jobTitle?: string;
    industry?: string;
    income?: number;
  };
  behavior: {
    interests: string[];
    recentSearches?: string[];
    clickedCategories?: string[];
    timeSpentOnCategories?: Record<string, number>;
    purchaseHistory?: string[];
    deviceUsage?: {
      mobile?: number;
      desktop?: number;
      tablet?: number;
    };
    activeHours?: number[];
    activeDays?: ('monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday')[];
  };
  engagement: {
    clickRate?: number;
    conversionRate?: number;
    timeOnSite?: number;
    pageViewsPerSession?: number;
    returnRate?: number;
    socialInteractions?: number;
  };
}

export interface AudienceSegment {
  id: string;
  name: string;
  description: string;
  size: number;
  users: string[]; // IDs de usuarios en este segmento
  characteristics: {
    dominantDemographics: Partial<UserProfile['demographics']>;
    dominantInterests: string[];
    engagementLevel: 'low' | 'medium' | 'high';
    conversionPotential: 'low' | 'medium' | 'high';
    bestTimeToTarget?: {
      hours: number[];
      days: ('monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday')[];
    };
  };
  createdAt: Date;
  updatedAt: Date;
  visualizationData?: Record<string, unknown>; // Datos para visualizar el segmento
}

export interface SegmentationResult {
  segments: AudienceSegment[];
  metadata: {
    totalUsers: number;
    segmentationMethod: string;
    segmentationDate: Date;
    qualityScore: number; // 0-1, indica la calidad de la segmentación
  };
}

export interface SegmentationOptions {
  method: 'kmeans' | 'hierarchical' | 'dbscan';
  numberOfClusters?: number; // Para k-means
  minSimilarity?: number; // Para hierarchical
  minPoints?: number; // Para DBSCAN
  epsilon?: number; // Para DBSCAN
  features?: (keyof UserProfile['demographics'] | keyof UserProfile['behavior'] | keyof UserProfile['engagement'])[];
  weights?: Record<string, number>; // Pesos para diferentes características
}
