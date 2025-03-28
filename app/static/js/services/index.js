/**
 * Service Layer Index
 * Exports all services for easy import
 */

// Phase 1: Foundation
export { errorHandler } from './error-handler.js';
export { BaseApiService } from './base-api-service.js';
export { apiConfig } from './api-config.js';

// Phase 2: Feature-specific services
export { campaignService } from './campaign-service.js';
export { jobOpeningService } from './job-opening-service.js';
export { candidateService } from './candidate-service.js';
export { segmentService } from './segment-service.js';
export { analyticsService } from './analytics-service.js';
export { platformService } from './platform-service.js';
export { authService } from './auth-service.js';

// API Framework - Unified Integration Layer
export { 
  APIRequest, 
  APIResponse, 
  TTLCache,
  BaseAPIClient,
  MetaAPIClient,
  TwitterAPIClient,
  GoogleAPIClient,
  APIFrameworkCampaignManager
} from './api-framework.js';

// Phase 3: Real-time services
export { websocketService } from './websocket-service.js';
export { toastService } from './toast-service.js';
export { realTimeApiClient, WATCHED_ENTITIES, UPDATE_TYPES } from './real-time-api.js';
export { default as eventHub } from './event-hub.js';
export { realTimeDashboard, DASHBOARD_EVENTS } from './real-time-dashboard.js';

// Additional utilities
export { compatibility } from './compatibility.js';

// Schemas
export { validateSchema, SchemaValidator } from './schemas/schema-validator.js';
export { campaignSchema } from './schemas/campaign-schema.js';
export { jobOpeningSchema } from './schemas/job-opening-schema.js';
export { candidateSchema } from './schemas/candidate-schema.js';
export { segmentSchema } from './schemas/segment-schema.js';
export { analyticsSchema } from './schemas/analytics-schema.js';
export { authSchema } from './schemas/auth-schema.js';
