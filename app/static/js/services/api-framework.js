/**
 * MagnetoCursor - API Integration Framework Client Library
 * 
 * This module provides client-side JavaScript equivalents to the backend API framework
 * for consistent interaction with social media platform APIs.
 */

import { BaseApiService } from './base-api-service.js';
import { ENDPOINTS } from './api-config.js';
import { ErrorHandler } from './error-handler.js';

/**
 * API Request class - mirrors backend APIRequest
 * Standardizes request format for all API framework operations
 */
export class APIRequest {
  /**
   * Create a new API request
   * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
   * @param {string} endpoint - API endpoint or path
   * @param {Object} params - Query parameters
   * @param {Object} data - Request body data
   * @param {Object} headers - Request headers
   * @param {number} timeout - Request timeout in milliseconds
   * @param {string} platform - API platform identifier (e.g., META, TWITTER, GOOGLE)
   * @param {string} operation - Operation name (e.g., create_campaign)
   * @param {boolean} cacheable - Whether this request can be cached
   */
  constructor({
    method,
    endpoint,
    params = {},
    data = {},
    headers = {},
    timeout = 30000,
    platform = null,
    operation = null,
    cacheable = false
  }) {
    this.id = this._generateId();
    this.method = method.toUpperCase();
    this.endpoint = endpoint;
    this.params = params;
    this.data = data;
    this.headers = headers;
    this.timeout = timeout;
    this.platform = platform;
    this.operation = operation;
    this.cacheable = cacheable;
    this.createdAt = Date.now();
  }

  /**
   * Generate a unique ID for this request
   * @returns {string} - Unique request ID
   * @private
   */
  _generateId() {
    return 'req_' + Math.random().toString(36).substring(2, 11);
  }

  /**
   * Generate a cache key for this request
   * @returns {string} - Cache key or empty string if not cacheable
   */
  getCacheKey() {
    if (!this.cacheable || this.method !== 'GET') {
      return '';
    }

    // Create a deterministic representation of the parameters
    const paramStr = Object.entries(this.params)
      .sort()
      .map(([k, v]) => `${k}=${v}`)
      .join('&');
      
    return `${this.platform}:${this.endpoint}:${paramStr}`;
  }

  /**
   * Convert the request to a plain object
   * @returns {Object} - Object representation of the request
   */
  toObject() {
    return {
      id: this.id,
      method: this.method,
      endpoint: this.endpoint,
      params: this.params,
      data: this.data,
      headers: this.headers,
      timeout: this.timeout,
      platform: this.platform,
      operation: this.operation,
      cacheable: this.cacheable,
      createdAt: this.createdAt
    };
  }

  /**
   * Create a request from a plain object
   * @param {Object} data - Object with request data
   * @returns {APIRequest} - New APIRequest instance
   */
  static fromObject(data) {
    const request = new APIRequest({
      method: data.method,
      endpoint: data.endpoint,
      params: data.params,
      data: data.data,
      headers: data.headers,
      timeout: data.timeout,
      platform: data.platform,
      operation: data.operation,
      cacheable: data.cacheable
    });

    request.id = data.id || request.id;
    request.createdAt = data.createdAt || request.createdAt;

    return request;
  }
}

/**
 * API Response class - mirrors backend APIResponse
 * Standardizes response format for all API framework operations
 */
export class APIResponse {
  /**
   * Create a new API response
   * @param {string} requestId - ID of the associated request
   * @param {boolean} success - Whether the request was successful
   * @param {number} statusCode - HTTP status code
   * @param {any} data - Response data
   * @param {string} error - Error message, if any
   * @param {Object} headers - Response headers
   * @param {number} timing - Request-response time in milliseconds
   */
  constructor({
    requestId,
    success,
    statusCode = null,
    data = null,
    error = null,
    headers = {},
    timing = null
  }) {
    this.requestId = requestId;
    this.success = success;
    this.statusCode = statusCode;
    this.data = data;
    this.error = error;
    this.headers = headers;
    this.timing = timing;
    this.timestamp = Date.now();
  }

  /**
   * Convert the response to a plain object
   * @returns {Object} - Object representation of the response
   */
  toObject() {
    return {
      requestId: this.requestId,
      success: this.success,
      statusCode: this.statusCode,
      data: this.data,
      error: this.error,
      headers: this.headers,
      timing: this.timing,
      timestamp: this.timestamp
    };
  }

  /**
   * Create a response from a plain object
   * @param {Object} data - Object with response data
   * @returns {APIResponse} - New APIResponse instance
   */
  static fromObject(data) {
    const response = new APIResponse({
      requestId: data.requestId,
      success: data.success,
      statusCode: data.statusCode,
      data: data.data,
      error: data.error,
      headers: data.headers,
      timing: data.timing
    });

    response.timestamp = data.timestamp || response.timestamp;

    return response;
  }

  /**
   * Create a success response
   * @param {string} requestId - The request ID
   * @param {any} data - The response data
   * @param {number} statusCode - HTTP status code (default: 200)
   * @returns {APIResponse} - Success response object
   */
  static success(requestId, data, statusCode = 200) {
    return new APIResponse({
      requestId,
      success: true,
      statusCode,
      data
    });
  }

  /**
   * Create an error response
   * @param {string} requestId - The request ID
   * @param {string} error - Error message
   * @param {number} statusCode - HTTP status code (default: 400)
   * @returns {APIResponse} - Error response object
   */
  static error(requestId, error, statusCode = 400) {
    return new APIResponse({
      requestId,
      success: false,
      statusCode,
      error
    });
  }
}

/**
 * Simple TTL Cache for API responses
 * Mirrors backend TTLCache functionality
 */
export class TTLCache {
  /**
   * Create a new TTL cache
   * @param {number} defaultTTL - Default time-to-live in milliseconds
   */
  constructor(defaultTTL = 300000) { // Default: 5 minutes
    this.cache = new Map();
    this.defaultTTL = defaultTTL;
  }

  /**
   * Get a value from the cache
   * @param {string} key - Cache key
   * @returns {any} - Cached value or null if not found or expired
   */
  get(key) {
    if (!this.cache.has(key)) {
      return null;
    }

    const { value, expiry } = this.cache.get(key);
    
    // Check if value has expired
    if (expiry < Date.now()) {
      this.cache.delete(key);
      return null;
    }

    return value;
  }

  /**
   * Set a value in the cache
   * @param {string} key - Cache key
   * @param {any} value - Value to cache
   * @param {number} ttl - Time-to-live in milliseconds (optional)
   */
  set(key, value, ttl = null) {
    const expiry = Date.now() + (ttl || this.defaultTTL);
    this.cache.set(key, { value, expiry });
  }

  /**
   * Remove a value from the cache
   * @param {string} key - Cache key
   */
  delete(key) {
    this.cache.delete(key);
  }

  /**
   * Clear all values from the cache
   */
  clear() {
    this.cache.clear();
  }

  /**
   * Clean expired entries
   */
  cleanup() {
    const now = Date.now();
    for (const [key, { expiry }] of this.cache.entries()) {
      if (expiry < now) {
        this.cache.delete(key);
      }
    }
  }
}

/**
 * Base API client abstract class
 * Mirrors the backend BaseAPIClient functionality
 */
export class BaseAPIClient {
  /**
   * Create a new API client
   * @param {string} platformName - Platform name (META, TWITTER, GOOGLE)
   * @param {Object} credentials - Platform credentials
   * @param {boolean} enableCache - Whether to enable response caching
   * @param {number} cacheTTL - Cache time-to-live in milliseconds
   */
  constructor(platformName, credentials, enableCache = true, cacheTTL = 300000) {
    this.platformName = platformName;
    this.credentials = credentials;
    this.isInitialized = false;
    this.errorHandler = new ErrorHandler();
    
    // Set up cache if enabled
    if (enableCache) {
      this.cache = new TTLCache(cacheTTL);
    }

    // Initialize metrics tracking
    this.metrics = {
      requests: 0,
      success: 0,
      errors: 0,
      cachedResponses: 0,
      startTime: Date.now(),
      timings: []
    };
    
    // Base API service for HTTP operations
    this.apiService = new BaseApiService();
  }

  /**
   * Initialize the client with credentials
   * @returns {Promise<boolean>} - Whether initialization was successful
   */
  async initialize() {
    try {
      // Validate credentials
      if (!this._validateCredentials()) {
        console.error(`${this.platformName} API credentials are invalid or missing`);
        return false;
      }
      
      this.isInitialized = true;
      console.log(`${this.platformName} API client initialized successfully`);
      return true;
    } catch (error) {
      console.error(`Error initializing ${this.platformName} API:`, error);
      this.isInitialized = false;
      return false;
    }
  }

  /**
   * Validate the credentials object
   * Should be implemented by subclasses
   * @returns {boolean} - Whether credentials are valid
   * @protected
   */
  _validateCredentials() {
    // Base implementation - subclasses should override
    return this.credentials && Object.keys(this.credentials).length > 0;
  }

  /**
   * Execute an API request
   * @param {APIRequest} request - The request to execute
   * @returns {Promise<APIResponse>} - The API response
   */
  async executeRequest(request) {
    if (!this.isInitialized) {
      return APIResponse.error(
        request.id,
        `${this.platformName} API client is not initialized`,
        500
      );
    }

    // Check cache first for cacheable requests
    if (request.cacheable) {
      const cacheKey = request.getCacheKey();
      if (cacheKey) {
        const cachedResponse = this.cache ? this.cache.get(cacheKey) : null;
        if (cachedResponse) {
          console.debug(`Cache hit for ${this.platformName} request: ${request.operation}`);
          
          // Track metrics for cached responses
          this.metrics.cachedResponses++;
          
          return cachedResponse;
        }
      }
    }

    // Start timing
    const startTime = Date.now();
    
    try {
      // Track request in metrics
      this.metrics.requests++;
      
      // Process request based on method
      let response;
      
      switch (request.method) {
        case 'GET':
          response = await this.apiService.get(request.endpoint, {}, request.params);
          break;
        case 'POST':
          response = await this.apiService.post(request.endpoint, request.data);
          break;
        case 'PUT':
          response = await this.apiService.put(request.endpoint, request.data);
          break;
        case 'DELETE':
          response = await this.apiService.delete(request.endpoint);
          break;
        default:
          throw new Error(`Unsupported method: ${request.method}`);
      }
      
      // Calculate timing
      const timing = Date.now() - startTime;
      
      // Create a standardized response
      const apiResponse = APIResponse.success(request.id, response, 200);
      apiResponse.timing = timing;
      
      // Track success in metrics
      this.metrics.success++;
      this.metrics.timings.push(timing);
      
      // Cache successful GET responses if enabled
      if (this.cache && request.cacheable && request.method === 'GET') {
        const cacheKey = request.getCacheKey();
        if (cacheKey) {
          this.cache.set(cacheKey, apiResponse);
        }
      }
      
      return apiResponse;
    } catch (error) {
      // Calculate timing even for errors
      const timing = Date.now() - startTime;
      
      // Track error in metrics
      this.metrics.errors++;
      
      // Create standardized error response
      const errorResponse = APIResponse.error(
        request.id,
        error.message || 'Unknown error',
        error.status || 500
      );
      errorResponse.timing = timing;
      
      return errorResponse;
    }
  }
  
  /**
   * Execute multiple requests, potentially in parallel
   * @param {Array<APIRequest>} requests - Requests to execute
   * @returns {Promise<Array<APIResponse>>} - Array of responses
   */
  async executeRequests(requests) {
    // Default implementation: execute sequentially
    // Platform-specific implementations could optimize this
    const responses = [];
    for (const request of requests) {
      const response = await this.executeRequest(request);
      responses.push(response);
    }
    return responses;
  }

  /**
   * Clear the client's cache
   */
  clearCache() {
    if (this.cache) {
      this.cache.clear();
    }
  }

  /**
   * Get metrics summary for this client
   * @returns {Object} - Metrics data
   */
  getMetrics() {
    const totalTime = Date.now() - this.metrics.startTime;
    const avgResponseTime = this.metrics.timings.length > 0
      ? this.metrics.timings.reduce((sum, t) => sum + t, 0) / this.metrics.timings.length
      : 0;
    
    return {
      platform: this.platformName,
      totalRequests: this.metrics.requests,
      successRate: this.metrics.requests > 0 
        ? (this.metrics.success / this.metrics.requests) * 100 
        : 0,
      cacheHitRate: this.metrics.requests > 0
        ? (this.metrics.cachedResponses / this.metrics.requests) * 100
        : 0,
      averageResponseTime: avgResponseTime,
      uptime: totalTime,
      errorsCount: this.metrics.errors
    };
  }
}

/**
 * Meta API Client implementation
 * Mirrors the backend MetaAPIClient functionality
 */
export class MetaAPIClient extends BaseAPIClient {
  /**
   * Create a new Meta API client
   * @param {Object} credentials - Meta API credentials
   * @param {boolean} enableCache - Whether to enable caching
   */
  constructor(credentials, enableCache = true) {
    super('META', credentials, enableCache);
  }

  /**
   * Validate Meta API credentials
   * @returns {boolean} - Whether credentials are valid
   * @protected
   */
  _validateCredentials() {
    return (
      this.credentials &&
      typeof this.credentials.META_APP_ID === 'string' &&
      typeof this.credentials.META_APP_SECRET === 'string' &&
      typeof this.credentials.META_ACCESS_TOKEN === 'string'
    );
  }

  /**
   * Create a campaign request
   * @param {string} name - Campaign name
   * @param {string} objective - Campaign objective (e.g., 'REACH', 'BRAND_AWARENESS')
   * @param {string} status - Campaign status ('ACTIVE', 'PAUSED')
   * @param {Array<string>} specialAdCategories - Special ad categories if applicable
   * @returns {APIRequest} - API request object ready to be executed
   */
  createCampaignRequest(name, objective = 'REACH', status = 'PAUSED', specialAdCategories = null) {
    const params = {
      name,
      objective,
      status
    };

    if (specialAdCategories) {
      params.special_ad_categories = specialAdCategories;
    }

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.META.CREATE_CAMPAIGN,
      data: params,
      platform: 'META',
      operation: 'create_campaign'
    });
  }

  /**
   * Create an ad set request
   * @param {string} campaignId - Campaign ID
   * @param {string} name - Ad set name
   * @param {Object} targeting - Targeting specifications
   * @param {number} budget - Daily budget in account currency
   * @param {number} bidAmount - Bid amount in cents
   * @param {string} billingEvent - Billing event type ('IMPRESSIONS', 'LINK_CLICKS')
   * @param {string} status - Ad set status ('ACTIVE', 'PAUSED')
   * @returns {APIRequest} - API request object
   */
  createAdSetRequest(campaignId, name, targeting, budget, bidAmount, billingEvent = 'IMPRESSIONS', status = 'PAUSED') {
    const params = {
      name,
      campaign_id: campaignId,
      daily_budget: budget,
      billing_event: billingEvent,
      optimization_goal: 'REACH',
      bid_amount: bidAmount,
      targeting: targeting,
      status: status
    };

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.META.CREATE_AD_SET,
      data: params,
      platform: 'META',
      operation: 'create_ad_set'
    });
  }

  /**
   * Create an ad request
   * @param {string} adSetId - Ad set ID
   * @param {string} name - Ad name
   * @param {string} creativeId - Creative ID
   * @param {string} status - Ad status ('ACTIVE', 'PAUSED')
   * @returns {APIRequest} - API request object
   */
  createAdRequest(adSetId, name, creativeId, status = 'PAUSED') {
    const params = {
      name,
      adset_id: adSetId,
      creative: { creative_id: creativeId },
      status: status
    };

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.META.CREATE_AD,
      data: params,
      platform: 'META',
      operation: 'create_ad'
    });
  }

  /**
   * Create a request to get campaign statistics
   * @param {string} campaignId - Campaign ID
   * @returns {APIRequest} - API request object
   */
  getCampaignStatsRequest(campaignId) {
    return new APIRequest({
      method: 'GET',
      endpoint: ENDPOINTS.API_FRAMEWORK.META.GET_CAMPAIGN_STATS,
      params: { campaign_id: campaignId },
      platform: 'META',
      operation: 'get_campaign_stats',
      cacheable: true
    });
  }
}

/**
 * Twitter API Client implementation
 * Mirrors the backend TwitterAPIClient functionality
 */
export class TwitterAPIClient extends BaseAPIClient {
  /**
   * Create a new Twitter API client
   * @param {Object} credentials - Twitter API credentials
   * @param {boolean} enableCache - Whether to enable caching
   */
  constructor(credentials, enableCache = true) {
    super('TWITTER', credentials, enableCache);
  }

  /**
   * Validate Twitter API credentials
   * @returns {boolean} - Whether credentials are valid
   * @protected
   */
  _validateCredentials() {
    return (
      this.credentials &&
      typeof this.credentials.X_API_KEY === 'string' &&
      typeof this.credentials.X_API_SECRET === 'string' &&
      typeof this.credentials.X_ACCESS_TOKEN === 'string' &&
      typeof this.credentials.X_ACCESS_TOKEN_SECRET === 'string'
    );
  }

  /**
   * Create a request to post a tweet
   * @param {string} text - Tweet text
   * @param {Array<string>} mediaIds - Media IDs to attach
   * @returns {APIRequest} - API request object
   */
  postTweetRequest(text, mediaIds = null) {
    const data = { text };
    if (mediaIds) {
      data.media_ids = mediaIds;
    }

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.TWITTER.POST_TWEET,
      data: data,
      platform: 'TWITTER',
      operation: 'post_tweet'
    });
  }

  /**
   * Create a request to upload media
   * @param {string} mediaPath - Path to media file
   * @returns {APIRequest} - API request object
   */
  uploadMediaRequest(mediaPath) {
    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.TWITTER.UPLOAD_MEDIA,
      data: { media_path: mediaPath },
      platform: 'TWITTER',
      operation: 'upload_media'
    });
  }

  /**
   * Create a campaign request
   * @param {string} name - Campaign name
   * @param {string} fundingInstrumentId - Funding instrument ID
   * @param {number} dailyBudget - Daily budget in account currency
   * @param {string} startTime - Campaign start time (ISO format)
   * @param {string} endTime - Campaign end time (ISO format)
   * @returns {APIRequest} - API request object
   */
  createCampaignRequest(name, fundingInstrumentId, dailyBudget, startTime, endTime = null) {
    const data = {
      name,
      funding_instrument_id: fundingInstrumentId,
      daily_budget: dailyBudget,
      start_time: startTime
    };

    if (endTime) {
      data.end_time = endTime;
    }

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.TWITTER.CREATE_CAMPAIGN,
      data: data,
      platform: 'TWITTER',
      operation: 'create_campaign'
    });
  }

  /**
   * Create a line item request
   * @param {string} campaignId - Campaign ID
   * @param {string} name - Line item name
   * @param {string} productType - Product type (default: PROMOTED_TWEETS)
   * @param {Array<Object>} placements - Placement objects
   * @param {Object} targeting - Targeting criteria
   * @param {number} bidAmount - Bid amount in account currency
   * @returns {APIRequest} - API request object
   */
  createLineItemRequest(campaignId, name, productType = 'PROMOTED_TWEETS', placements = null, targeting = null, bidAmount = null) {
    const data = {
      campaign_id: campaignId,
      name,
      product_type: productType
    };

    if (placements) data.placements = placements;
    if (targeting) data.targeting = targeting;
    if (bidAmount) data.bid_amount = bidAmount;

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.TWITTER.CREATE_LINE_ITEM,
      data: data,
      platform: 'TWITTER',
      operation: 'create_line_item'
    });
  }

  /**
   * Create a promoted tweet request
   * @param {string} campaignId - Campaign ID
   * @param {string} tweetId - Tweet ID to promote
   * @param {string} lineItemId - Line item ID
   * @returns {APIRequest} - API request object
   */
  createPromotedTweetRequest(campaignId, tweetId, lineItemId) {
    const data = {
      campaign_id: campaignId,
      tweet_id: tweetId,
      line_item_id: lineItemId
    };

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.TWITTER.CREATE_PROMOTED_TWEET,
      data: data,
      platform: 'TWITTER',
      operation: 'create_promoted_tweet'
    });
  }

  /**
   * Create a request to get campaign statistics
   * @param {string} campaignId - Campaign ID
   * @returns {APIRequest} - API request object
   */
  getCampaignStatsRequest(campaignId) {
    return new APIRequest({
      method: 'GET',
      endpoint: ENDPOINTS.API_FRAMEWORK.TWITTER.GET_CAMPAIGN_STATS,
      params: { campaign_id: campaignId },
      platform: 'TWITTER',
      operation: 'get_campaign_stats',
      cacheable: true
    });
  }
}

/**
 * Google API Client implementation
 * Mirrors the backend GoogleAPIClient functionality
 */
export class GoogleAPIClient extends BaseAPIClient {
  /**
   * Create a new Google API client
   * @param {Object} credentials - Google API credentials
   * @param {boolean} enableCache - Whether to enable caching
   */
  constructor(credentials, enableCache = true) {
    super('GOOGLE', credentials, enableCache);
  }

  /**
   * Validate Google API credentials
   * @returns {boolean} - Whether credentials are valid
   * @protected
   */
  _validateCredentials() {
    return (
      this.credentials &&
      typeof this.credentials.GOOGLE_CLIENT_ID === 'string' &&
      typeof this.credentials.GOOGLE_CLIENT_SECRET === 'string' &&
      typeof this.credentials.GOOGLE_REFRESH_TOKEN === 'string'
    );
  }

  /**
   * Create a campaign request
   * @param {string} name - Campaign name
   * @param {number} budget - Daily budget in account currency
   * @param {string} status - Campaign status ('ACTIVE', 'PAUSED')
   * @returns {APIRequest} - API request object
   */
  createCampaignRequest(name, budget, status = 'PAUSED') {
    const data = {
      name,
      budget,
      status
    };

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.GOOGLE.CREATE_CAMPAIGN,
      data: data,
      platform: 'GOOGLE',
      operation: 'create_campaign'
    });
  }

  /**
   * Create an ad group request
   * @param {string} campaignId - Campaign ID
   * @param {string} name - Ad group name
   * @param {string} status - Ad group status ('ACTIVE', 'PAUSED')
   * @returns {APIRequest} - API request object
   */
  createAdGroupRequest(campaignId, name, status = 'PAUSED') {
    const data = {
      campaign_id: campaignId,
      name,
      status
    };

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.GOOGLE.CREATE_AD_GROUP,
      data: data,
      platform: 'GOOGLE',
      operation: 'create_ad_group'
    });
  }

  /**
   * Create a responsive search ad request
   * @param {string} adGroupId - Ad group ID
   * @param {Array<string>} headlines - Ad headlines
   * @param {Array<string>} descriptions - Ad descriptions
   * @param {string} finalUrl - Landing page URL
   * @param {string} status - Ad status ('ACTIVE', 'PAUSED')
   * @returns {APIRequest} - API request object
   */
  createResponsiveSearchAdRequest(adGroupId, headlines, descriptions, finalUrl, status = 'PAUSED') {
    const data = {
      ad_group_id: adGroupId,
      headlines,
      descriptions,
      final_url: finalUrl,
      status
    };

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.GOOGLE.CREATE_RESPONSIVE_SEARCH_AD,
      data: data,
      platform: 'GOOGLE',
      operation: 'create_responsive_search_ad'
    });
  }

  /**
   * Create a location targeting request
   * @param {string} campaignId - Campaign ID
   * @param {Array<string>} locations - Location strings
   * @returns {APIRequest} - API request object
   */
  createLocationTargetingRequest(campaignId, locations) {
    const data = {
      campaign_id: campaignId,
      locations
    };

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.GOOGLE.CREATE_LOCATION_TARGETING,
      data: data,
      platform: 'GOOGLE',
      operation: 'create_location_targeting'
    });
  }

  /**
   * Create a demographic targeting request
   * @param {string} adGroupId - Ad group ID
   * @param {Object} criteria - Demographic criteria
   * @returns {APIRequest} - API request object
   */
  createDemographicTargetingRequest(adGroupId, criteria) {
    const data = {
      ad_group_id: adGroupId,
      criteria
    };

    return new APIRequest({
      method: 'POST',
      endpoint: ENDPOINTS.API_FRAMEWORK.GOOGLE.CREATE_DEMOGRAPHIC_TARGETING,
      data: data,
      platform: 'GOOGLE',
      operation: 'create_demographic_targeting'
    });
  }

  /**
   * Create a request to get campaign statistics
   * @param {string} campaignId - Campaign ID
   * @returns {APIRequest} - API request object
   */
  getCampaignStatsRequest(campaignId) {
    return new APIRequest({
      method: 'GET',
      endpoint: ENDPOINTS.API_FRAMEWORK.GOOGLE.GET_CAMPAIGN_STATS,
      params: { campaign_id: campaignId },
      platform: 'GOOGLE',
      operation: 'get_campaign_stats',
      cacheable: true
    });
  }
}

/**
 * API Framework Campaign Manager
 * Unified interface for managing campaigns across multiple platforms
 * Mirrors the backend APIFrameworkCampaignManager functionality
 */
export class APIFrameworkCampaignManager {
  /**
   * Create a new Campaign Manager instance
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    // Initialize platform clients
    this.metaClient = options.metaClient || null;
    this.twitterClient = options.twitterClient || null;
    this.googleClient = options.googleClient || null;
    
    // Platform client map
    this.platformClients = {
      'meta': this.metaClient,
      'facebook': this.metaClient, // Alias
      'instagram': this.metaClient, // Alias
      'google': this.googleClient,
      'twitter': this.twitterClient,
      'x': this.twitterClient  // Alias
    };
    
    // Error handler
    this.errorHandler = new ErrorHandler();
  }
  
  /**
   * Set platform client
   * @param {string} platform - Platform name
   * @param {BaseAPIClient} client - API client instance
   */
  setPlatformClient(platform, client) {
    if (!(client instanceof BaseAPIClient)) {
      throw new Error(`Invalid client for ${platform}`);
    }
    
    // Store in specific client property
    if (platform.toLowerCase() === 'meta' || 
        platform.toLowerCase() === 'facebook' || 
        platform.toLowerCase() === 'instagram') {
      this.metaClient = client;
    } else if (platform.toLowerCase() === 'twitter' || 
              platform.toLowerCase() === 'x') {
      this.twitterClient = client;
    } else if (platform.toLowerCase() === 'google') {
      this.googleClient = client;
    }
    
    // Update platform client map
    this.platformClients[platform.toLowerCase()] = client;
    
    // Add aliases as needed
    if (platform.toLowerCase() === 'meta') {
      this.platformClients['facebook'] = client;
      this.platformClients['instagram'] = client;
    } else if (platform.toLowerCase() === 'twitter') {
      this.platformClients['x'] = client;
    }
  }
  
  /**
   * Create a campaign across multiple platforms
   * @param {number} jobOpeningId - ID of the job opening to advertise
   * @param {Array<string>} platforms - List of platform names to create campaigns on
   * @param {number} segmentId - ID of the audience segment to target
   * @param {number} budget - Daily budget per platform in account currency
   * @param {string} status - Initial campaign status ('ACTIVE', 'PAUSED')
   * @param {string} adContent - Optional ad content
   * @returns {Promise<Object>} - Results for each platform
   */
  async createCampaign(jobOpeningId, platforms, segmentId = null, budget = 1000.0, status = 'PAUSED', adContent = '') {
    // Validate inputs
    if (!platforms || !platforms.length) {
      throw new Error('At least one platform must be specified');
    }
    
    if (budget <= 0) {
      throw new Error('Budget must be greater than zero');
    }
    
    if (status !== 'ACTIVE' && status !== 'PAUSED') {
      throw new Error('Status must be ACTIVE or PAUSED');
    }
    
    // Initialize results object
    const results = {
      success: false,
      platforms: {}
    };
    
    // Process each platform
    for (const platform of platforms) {
      try {
        const client = this.platformClients[platform.toLowerCase()];
        
        if (!client) {
          results.platforms[platform] = {
            success: false,
            error: `Platform ${platform} not supported`
          };
          continue;
        }
        
        if (!client.isInitialized) {
          results.platforms[platform] = {
            success: false,
            error: `Client for ${platform} is not initialized`
          };
          continue;
        }
        
        // Create campaign based on platform
        let result;
        if (['meta', 'facebook', 'instagram'].includes(platform.toLowerCase())) {
          result = await this._createMetaCampaign(client, jobOpeningId, segmentId, budget, status, adContent);
        } else if (platform.toLowerCase() === 'google') {
          result = await this._createGoogleCampaign(client, jobOpeningId, segmentId, budget, status, adContent);
        } else { // Twitter/X
          result = await this._createTwitterCampaign(client, jobOpeningId, segmentId, budget, status, adContent);
        }
        
        // Store result
        results.platforms[platform] = result;
        
        // Set overall success if at least one platform succeeds
        if (result.success) {
          results.success = true;
        }
      } catch (error) {
        results.platforms[platform] = {
          success: false,
          error: error.message || 'Unknown error'
        };
      }
    }
    
    return results;
  }
  
  /**
   * Create a campaign on Meta platforms
   * @param {MetaAPIClient} client - Meta API client
   * @param {number} jobOpeningId - Job opening ID
   * @param {number} segmentId - Segment ID
   * @param {number} budget - Daily budget
   * @param {string} status - Status
   * @param {string} adContent - Ad content
   * @returns {Promise<Object>} - Campaign creation result
   * @private
   */
  async _createMetaCampaign(client, jobOpeningId, segmentId, budget, status, adContent) {
    // Create campaign request
    const campaignRequest = client.createCampaignRequest(
      `Job ${jobOpeningId} - Meta Campaign`,
      'REACH',
      status,
      ['EMPLOYMENT'] // Special ad category for job ads
    );
    
    // Execute campaign creation request
    const campaignResponse = await client.executeRequest(campaignRequest);
    
    if (!campaignResponse.success) {
      return {
        success: false,
        error: campaignResponse.error
      };
    }
    
    // Create ad set with targeting
    const targeting = await this._buildMetaTargeting(segmentId);
    
    const adSetRequest = client.createAdSetRequest(
      campaignResponse.data.campaign_id,
      `AdSet for Job ${jobOpeningId}`,
      targeting,
      budget,
      500, // $5.00 bid
      'IMPRESSIONS',
      status
    );
    
    // Execute ad set creation request
    const adSetResponse = await client.executeRequest(adSetRequest);
    
    if (!adSetResponse.success) {
      return {
        success: false,
        error: adSetResponse.error
      };
    }
    
    // Return combined result
    return {
      success: true,
      campaign_id: campaignResponse.data.campaign_id,
      ad_set_id: adSetResponse.data.ad_set_id,
      platform: 'meta'
    };
  }
  
  /**
   * Create a campaign on Google Ads
   * @param {GoogleAPIClient} client - Google API client
   * @param {number} jobOpeningId - Job opening ID
   * @param {number} segmentId - Segment ID
   * @param {number} budget - Daily budget
   * @param {string} status - Status
   * @param {string} adContent - Ad content
   * @returns {Promise<Object>} - Campaign creation result
   * @private
   */
  async _createGoogleCampaign(client, jobOpeningId, segmentId, budget, status, adContent) {
    // Create campaign request
    const campaignRequest = client.createCampaignRequest(
      `Job ${jobOpeningId} - Google Campaign`,
      budget,
      status
    );
    
    // Execute campaign creation request
    const campaignResponse = await client.executeRequest(campaignRequest);
    
    if (!campaignResponse.success) {
      return {
        success: false,
        error: campaignResponse.error
      };
    }
    
    // Create ad group
    const adGroupRequest = client.createAdGroupRequest(
      campaignResponse.data.campaign_id,
      `AdGroup for Job ${jobOpeningId}`,
      status
    );
    
    // Execute ad group creation request
    const adGroupResponse = await client.executeRequest(adGroupRequest);
    
    if (!adGroupResponse.success) {
      return {
        success: false,
        error: adGroupResponse.error
      };
    }
    
    // Return combined result
    return {
      success: true,
      campaign_id: campaignResponse.data.campaign_id,
      ad_group_id: adGroupResponse.data.ad_group_id,
      platform: 'google'
    };
  }
  
  /**
   * Create a campaign on Twitter/X
   * @param {TwitterAPIClient} client - Twitter API client
   * @param {number} jobOpeningId - Job opening ID
   * @param {number} segmentId - Segment ID
   * @param {number} budget - Daily budget
   * @param {string} status - Status
   * @param {string} adContent - Ad content
   * @returns {Promise<Object>} - Campaign creation result
   * @private
   */
  async _createTwitterCampaign(client, jobOpeningId, segmentId, budget, status, adContent) {
    // Create campaign request
    const campaignRequest = client.createCampaignRequest(
      `Job ${jobOpeningId} - Twitter Campaign`,
      'test_funding', // Would be real in production
      budget,
      new Date().toISOString() // Start time (now)
    );
    
    // Execute campaign creation request
    const campaignResponse = await client.executeRequest(campaignRequest);
    
    if (!campaignResponse.success) {
      return {
        success: false,
        error: campaignResponse.error
      };
    }
    
    // Create a tweet for the job
    const tweetRequest = client.postTweetRequest(
      `New Job Opening: Job ${jobOpeningId}\n\nApply now!`
    );
    
    // Execute tweet creation request
    const tweetResponse = await client.executeRequest(tweetRequest);
    
    if (!tweetResponse.success) {
      return {
        success: false,
        error: tweetResponse.error
      };
    }
    
    // Return combined result
    return {
      success: true,
      campaign_id: campaignResponse.data.campaign_id,
      tweet_id: tweetResponse.data.tweet_id,
      platform: 'twitter'
    };
  }
  
  /**
   * Build Meta targeting from segment
   * @param {number} segmentId - Segment ID
   * @returns {Promise<Object>} - Meta targeting object
   * @private
   */
  async _buildMetaTargeting(segmentId) {
    // Default targeting
    const targeting = {
      age_min: 18,
      age_max: 65,
      genders: [1, 2], // Both men and women
      geo_locations: { countries: ['US'] },
      interests: [{ id: '6003139266461', name: 'Job hunting' }]
    };
    
    // Query segment data if segment ID is provided
    if (segmentId) {
      try {
        // Get segment data from API
        const segmentResponse = await fetch(`/api/segments/${segmentId}`);
        if (segmentResponse.ok) {
          const segmentData = await segmentResponse.json();
          
          // Enhance targeting with segment data
          if (segmentData && segmentData.data) {
            const segment = segmentData.data;
            
            // Update age targeting if segment has age data
            if (segment.age_min || segment.age_max) {
              targeting.age_min = segment.age_min || targeting.age_min;
              targeting.age_max = segment.age_max || targeting.age_max;
            }
            
            // Update gender targeting if segment has gender data
            if (segment.genders && Array.isArray(segment.genders) && segment.genders.length > 0) {
              targeting.genders = segment.genders;
            }
            
            // Update location targeting if segment has location data
            if (segment.locations && Array.isArray(segment.locations) && segment.locations.length > 0) {
              targeting.geo_locations = {
                countries: [],
                cities: [],
                regions: []
              };
              
              // Process each location in segment
              segment.locations.forEach(location => {
                if (location.type === 'country' && location.code) {
                  targeting.geo_locations.countries.push(location.code);
                } else if (location.type === 'city' && location.key) {
                  targeting.geo_locations.cities.push({
                    key: location.key,
                    name: location.name || '',
                    radius: location.radius || 50,
                    distance_unit: 'kilometer'
                  });
                } else if (location.type === 'region' && location.key) {
                  targeting.geo_locations.regions.push({
                    key: location.key,
                    name: location.name || ''
                  });
                }
              });
              
              // If no locations were added, revert to default
              if (targeting.geo_locations.countries.length === 0 &&
                  targeting.geo_locations.cities.length === 0 &&
                  targeting.geo_locations.regions.length === 0) {
                targeting.geo_locations = { countries: ['US'] };
              }
            }
            
            // Update interests targeting if segment has interest data
            if (segment.interests && Array.isArray(segment.interests) && segment.interests.length > 0) {
              targeting.interests = segment.interests.map(interest => ({
                id: interest.id || '6003139266461', // Default to 'Job hunting' if no ID
                name: interest.name || 'Job hunting'
              }));
            }
            
            // Add any custom audience targeting
            if (segment.custom_audiences && Array.isArray(segment.custom_audiences) && segment.custom_audiences.length > 0) {
              targeting.custom_audiences = segment.custom_audiences;
            }
            
            // Add exclusions if available
            if (segment.exclusions) {
              targeting.exclusions = segment.exclusions;
            }
            
            console.debug('Enhanced Meta targeting with segment data', targeting);
          }
        } else {
          console.warn(`Failed to fetch segment data for segment ID ${segmentId}`);
        }
      } catch (error) {
        console.error('Error enhancing targeting with segment data:', error);
      }
    }
    
    return targeting;
  }
  
  /**
   * Get metrics from all platforms
   * @returns {Object} - Metrics for each platform
   */
  getMetrics() {
    const metrics = {};
    
    for (const [platform, client] of Object.entries(this.platformClients)) {
      if (client && client.getMetrics) {
        if (!metrics[platform]) { // Avoid duplicates for aliases
          metrics[platform] = client.getMetrics();
        }
      }
    }
    
    return metrics;
  }
}
