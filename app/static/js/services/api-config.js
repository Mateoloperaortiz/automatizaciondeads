/**
 * MagnetoCursor - API Configuration Module
 * Centralizes all API endpoints and configuration
 */

// Environment configuration
const ENV = {
  DEVELOPMENT: 'development',
  PRODUCTION: 'production',
  TESTING: 'testing'
};

// Current environment based on hostname or other detection
const currentEnv = 
  window.location.hostname === 'localhost' || 
  window.location.hostname === '127.0.0.1' ? 
  ENV.DEVELOPMENT : ENV.PRODUCTION;

// Base URLs for different environments
const BASE_URLS = {
  [ENV.DEVELOPMENT]: '/api',
  [ENV.PRODUCTION]: '/api',
  [ENV.TESTING]: '/api'
};

// WebSocket URLs for different environments
const WS_URLS = {
  [ENV.DEVELOPMENT]: '/ws',
  [ENV.PRODUCTION]: '/ws',
  [ENV.TESTING]: '/ws'
};

// API version
const API_VERSION = 'v1';

// Get the base URL for current environment
const getBaseUrl = () => `${BASE_URLS[currentEnv]}`;

// Get the WebSocket URL for current environment
const getWsUrl = () => `${WS_URLS[currentEnv]}`;

/**
 * All API endpoints organized by feature
 */
const ENDPOINTS = {
  // API Framework endpoints for platform-specific operations
  API_FRAMEWORK: {
    // Meta (Facebook & Instagram) endpoints
    META: {
      CREATE_CAMPAIGN: '/api-framework/meta/campaigns',
      CREATE_AD_SET: '/api-framework/meta/ad-sets',
      CREATE_AD: '/api-framework/meta/ads',
      CREATE_CREATIVE: '/api-framework/meta/creatives',
      GET_CAMPAIGN_STATS: '/api-framework/meta/campaigns/:campaign_id/stats',
      GET_TARGETING_OPTIONS: '/api-framework/meta/targeting-options',
      GET_AUDIENCE_INSIGHTS: '/api-framework/meta/audience-insights',
      UPLOAD_IMAGE: '/api-framework/meta/images',
      TEST_CONNECTION: '/api-framework/meta/test-connection'
    },
    
    // Twitter endpoints
    TWITTER: {
      POST_TWEET: '/api-framework/twitter/tweets',
      UPLOAD_MEDIA: '/api-framework/twitter/media',
      CREATE_CAMPAIGN: '/api-framework/twitter/campaigns',
      CREATE_LINE_ITEM: '/api-framework/twitter/line-items',
      CREATE_PROMOTED_TWEET: '/api-framework/twitter/promoted-tweets',
      GET_CAMPAIGN_STATS: '/api-framework/twitter/campaigns/:campaign_id/stats',
      GET_TWEET_ANALYTICS: '/api-framework/twitter/tweets/:tweet_id/analytics',
      GET_AUDIENCE_INSIGHTS: '/api-framework/twitter/audience-insights',
      TEST_CONNECTION: '/api-framework/twitter/test-connection'
    },
    
    // Google endpoints
    GOOGLE: {
      CREATE_CAMPAIGN: '/api-framework/google/campaigns',
      CREATE_AD_GROUP: '/api-framework/google/ad-groups',
      CREATE_RESPONSIVE_SEARCH_AD: '/api-framework/google/responsive-search-ads',
      CREATE_LOCATION_TARGETING: '/api-framework/google/location-targeting',
      CREATE_DEMOGRAPHIC_TARGETING: '/api-framework/google/demographic-targeting',
      GET_CAMPAIGN_STATS: '/api-framework/google/campaigns/:campaign_id/stats',
      GET_KEYWORD_IDEAS: '/api-framework/google/keyword-ideas',
      GET_LOCATION_IDEAS: '/api-framework/google/location-ideas',
      TEST_CONNECTION: '/api-framework/google/test-connection'
    },
    
    // Common endpoints
    COMMON: {
      GET_CREDENTIALS: '/api-framework/credentials',
      UPDATE_CREDENTIALS: '/api-framework/credentials/:platform',
      GET_PLATFORM_STATUS: '/api-framework/status/:platform',
      GET_CAMPAIGN_METRICS: '/api-framework/metrics/:platform/:campaign_id',
      VALIDATE_CREATIVE: '/api-framework/validate-creative/:platform'
    }
  },
  
  CAMPAIGNS: {
    LIST: '/campaigns',
    DETAIL: '/campaigns/:id',
    CREATE: '/campaigns',
    UPDATE: '/campaigns/:id',
    DELETE: '/campaigns/:id',
    PUBLISH: '/campaigns/:id/publish',
    SHARE_USER: '/campaigns/:id/share/user',
    SHARE_TEAM: '/campaigns/:id/share/team',
    REMOVE_COLLABORATOR: '/campaigns/:id/collaborator/:user_id/remove'
  },
  
  JOB_OPENINGS: {
    LIST: '/job_openings',
    DETAIL: '/job_openings/:id',
    CREATE: '/job_openings',
    UPDATE: '/job_openings/:id',
    DELETE: '/job_openings/:id',
    ACTIVATE: '/job_openings/:id/activate',
    DEACTIVATE: '/job_openings/:id/deactivate',
    SEARCH: '/job_openings/search'
  },
  
  CANDIDATES: {
    LIST: '/candidates',
    DETAIL: '/candidates/:id',
    CREATE: '/candidates',
    UPDATE: '/candidates/:id',
    DELETE: '/candidates/:id',
    SEARCH: '/candidates/search',
    SEGMENTS: '/candidates/:id/segments',
    UPLOAD_IMAGE: '/candidates/:id/image',
    IMPORT: '/candidates/import'
  },
  
  SEGMENTS: {
    LIST: '/segments',
    DETAIL: '/segments/:id',
    CREATE: '/segments',
    UPDATE: '/segments/:id',
    DELETE: '/segments/:id',
    REFRESH: '/segments/refresh',
    CANDIDATES: '/segments/:id/candidates',
    RUN_SEGMENTATION: '/segments/run-segmentation',
    VISUALIZATION: '/segments/visualization',
    COMPARE: '/segments/compare',
    RESET_CHARACTERISTIC: '/segments/:id/reset_characteristic',
    BENCHMARK: '/segments/:id/benchmark'
  },
  
  ANALYTICS: {
    CAMPAIGN: '/analytics/campaign/:id',
    OVERALL: '/analytics/overall',
    SEGMENT: '/analytics/segment/:id',
    PLATFORM: '/analytics/platform',
    JOB_OPENING: '/analytics/job_opening/:id',
    ROI: '/analytics/roi',
    USER_ACTIVITY: '/analytics/user_activity',
    CAMPAIGN_COMPARE: '/analytics/campaign/compare',
    GENERATE_REPORT: '/analytics/report'
  },
  
  UPLOADS: {
    IMAGE: '/uploads/image',
    FILE: '/uploads/file',
    CSV: '/uploads/csv'
  },
  
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    STATUS: '/auth/status',
    REGISTER: '/auth/register',
    REQUEST_RESET: '/auth/password/reset',
    CONFIRM_RESET: '/auth/password/reset/confirm',
    PROFILE: '/auth/profile',
    UPLOAD_IMAGE: '/auth/profile/image',
    CHANGE_PASSWORD: '/auth/password/change'
  },
  
  NOTIFICATIONS: {
    LIST: '/notifications',
    DETAIL: '/notifications/:id',
    MARK_READ: '/notifications/:id/read',
    MARK_ALL_READ: '/notifications/read-all',
    DELETE: '/notifications/:id',
    UNREAD_COUNT: '/notifications/unread-count',
    PREFERENCES: '/notifications/preferences',
    CREATE: '/notifications/create',
    SEND_TO_USERS: '/notifications/send-to-users',
    BROADCAST: '/notifications/broadcast'
  },
  
  PLATFORM_STATUS: {
    LIST: '/platforms',
    CHECK: '/platform-status',
    TEST_CONNECTION: '/test/connection',
    HISTORY: '/platform-status/history',
    CAPABILITIES: '/platforms/:platform/capabilities',
    API_USAGE: '/platforms/:platform/usage',
    UPDATE_CREDENTIALS: '/platforms/:platform/credentials',
    TARGETING_CAPABILITIES: '/platforms/:platform/targeting',
    AD_FORMATS: '/platforms/:platform/ad-formats'
  },
  
  TEAMS: {
    LIST: '/teams',
    DETAIL: '/teams/:id',
    CREATE: '/teams',
    UPDATE: '/teams/:id',
    DELETE: '/teams/:id',
    MEMBERS: '/teams/:id/members',
    ADD_MEMBER: '/teams/:id/members',
    REMOVE_MEMBER: '/teams/:id/members/:user_id'
  },
  
  // WebSocket endpoints
  WEBSOCKETS: {
    NOTIFICATIONS: '/ws/notifications',
    REAL_TIME: '/ws/real-time',
    COLLABORATION: '/ws/collaboration',
    ANALYTICS_STREAM: '/ws/analytics/stream'
  }
};

/**
 * Build a complete URL with path parameters replaced
 * 
 * @param {string} endpoint - The endpoint path with placeholders
 * @param {Object} params - Key-value pairs for path parameters
 * @returns {string} - The complete URL with parameters substituted
 */
const buildUrl = (endpoint, params = {}) => {
  let url = endpoint;
  
  // Replace path parameters
  Object.keys(params).forEach(key => {
    const placeholder = `:${key}`;
    if (url.includes(placeholder)) {
      url = url.replace(placeholder, params[key]);
    }
  });
  
  return `${getBaseUrl()}${url}`;
};

/**
 * Build a WebSocket URL
 * 
 * @param {string} endpoint - The WebSocket endpoint
 * @returns {string} - Complete WebSocket URL
 */
const buildWsUrl = (endpoint) => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}${getWsUrl()}${endpoint}`;
};

/**
 * Build a URL with query parameters
 * 
 * @param {string} url - The base URL
 * @param {Object} queryParams - Key-value pairs for query parameters
 * @returns {string} - URL with query string
 */
const buildQueryUrl = (url, queryParams = {}) => {
  // Return the original URL if no query params
  if (Object.keys(queryParams).length === 0) {
    return url;
  }
  
  // Build query string
  const queryString = Object.keys(queryParams)
    .map(key => {
      // Handle array parameters
      if (Array.isArray(queryParams[key])) {
        return queryParams[key]
          .map(value => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
          .join('&');
      }
      return `${encodeURIComponent(key)}=${encodeURIComponent(queryParams[key])}`;
    })
    .join('&');
    
  // Append query string to URL
  return `${url}${url.includes('?') ? '&' : '?'}${queryString}`;
};

// Export all configuration
export { 
  ENV, 
  currentEnv, 
  API_VERSION, 
  ENDPOINTS, 
  buildUrl,
  buildWsUrl,
  buildQueryUrl
};
