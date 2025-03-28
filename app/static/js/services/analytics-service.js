/**
 * Analytics Service
 * Handles analytics-related API operations
 */

import { BaseApiService } from './base-api-service.js';
import { ENDPOINTS } from './api-config.js';
import { validate, campaignAnalyticsRequestSchema, segmentAnalyticsRequestSchema, reportGenerationSchema } from './schemas/index.js';

/**
 * Service for analytics-related operations
 */
export class AnalyticsService extends BaseApiService {
  /**
   * Get overall analytics dashboard data
   * @param {Object} timeframe - Timeframe parameters
   * @returns {Promise<Object>} - Overall analytics data
   */
  async getOverallAnalytics(timeframe = {}) {
    return this.get(ENDPOINTS.ANALYTICS.OVERALL, {}, timeframe);
  }
  
  /**
   * Get analytics for a specific campaign
   * @param {number|string} id - Campaign ID
   * @param {Object} options - Analytics options (timeframe, metrics)
   * @returns {Promise<Object>} - Campaign analytics data
   */
  async getCampaignAnalytics(id, options = {}) {
    // Prepare request data
    const requestData = {
      campaign_id: id,
      ...options
    };
    
    // Validate input data
    const validation = validate(requestData, campaignAnalyticsRequestSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid analytics request',
        errors: validation.errors
      });
    }
    
    return this.get(ENDPOINTS.ANALYTICS.CAMPAIGN, { id }, options);
  }
  
  /**
   * Get analytics for a specific segment
   * @param {number|string} id - Segment ID
   * @param {Object} options - Analytics options (timeframe, metrics)
   * @returns {Promise<Object>} - Segment analytics data
   */
  async getSegmentAnalytics(id, options = {}) {
    // Prepare request data
    const requestData = {
      segment_id: id,
      ...options
    };
    
    // Validate input data
    const validation = validate(requestData, segmentAnalyticsRequestSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid analytics request',
        errors: validation.errors
      });
    }
    
    return this.get(ENDPOINTS.ANALYTICS.SEGMENT, { id }, options);
  }
  
  /**
   * Compare analytics between multiple campaigns
   * @param {Array<number|string>} campaignIds - Array of campaign IDs to compare
   * @param {Object} options - Comparison options
   * @returns {Promise<Object>} - Comparison data
   */
  async compareCampaigns(campaignIds, options = {}) {
    return this.get(ENDPOINTS.ANALYTICS.CAMPAIGN_COMPARE, {}, {
      campaign_ids: campaignIds,
      ...options
    });
  }
  
  /**
   * Get platform performance analytics
   * @param {Object} timeframe - Timeframe parameters
   * @returns {Promise<Object>} - Platform analytics data
   */
  async getPlatformAnalytics(timeframe = {}) {
    return this.get(ENDPOINTS.ANALYTICS.PLATFORM, {}, timeframe);
  }
  
  /**
   * Get job opening performance analytics
   * @param {number|string} id - Job opening ID
   * @param {Object} timeframe - Timeframe parameters
   * @returns {Promise<Object>} - Job opening analytics data
   */
  async getJobOpeningAnalytics(id, timeframe = {}) {
    return this.get(ENDPOINTS.ANALYTICS.JOB_OPENING, { id }, timeframe);
  }
  
  /**
   * Generate analytics report
   * @param {Object} reportOptions - Report generation options
   * @returns {Promise<Object>} - Report task information or download URL
   */
  async generateReport(reportOptions) {
    // Validate input data
    const validation = validate(reportOptions, reportGenerationSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid report options',
        errors: validation.errors
      });
    }
    
    return this.post(ENDPOINTS.ANALYTICS.GENERATE_REPORT, reportOptions);
  }
  
  /**
   * Get ROI analysis
   * @param {Object} options - Analysis options
   * @returns {Promise<Object>} - ROI analysis data
   */
  async getROIAnalysis(options = {}) {
    return this.get(ENDPOINTS.ANALYTICS.ROI, {}, options);
  }
  
  /**
   * Get user activity analytics
   * @param {Object} timeframe - Timeframe parameters
   * @returns {Promise<Object>} - User activity data
   */
  async getUserActivityAnalytics(timeframe = {}) {
    return this.get(ENDPOINTS.ANALYTICS.USER_ACTIVITY, {}, timeframe);
  }
}