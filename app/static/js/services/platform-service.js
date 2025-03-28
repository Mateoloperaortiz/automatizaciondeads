/**
 * Platform Service
 * Handles social media platform-related API operations
 */

import { BaseApiService } from './base-api-service.js';
import { ENDPOINTS } from './api-config.js';

/**
 * Service for platform-related operations
 */
export class PlatformService extends BaseApiService {
  /**
   * Get all platforms
   * @param {Object} filters - Filter options (active, etc.)
   * @returns {Promise<Array>} - List of platforms
   */
  async getPlatforms(filters = {}) {
    return this.get(ENDPOINTS.PLATFORM_STATUS.LIST, {}, filters);
  }
  
  /**
   * Get platform status
   * @returns {Promise<Object>} - Platform status data
   */
  async getPlatformStatus() {
    return this.get(ENDPOINTS.PLATFORM_STATUS.CHECK);
  }
  
  /**
   * Test connection to a specific platform
   * @param {string} platform - Platform identifier (meta, google, twitter, etc.)
   * @returns {Promise<Object>} - Connection test results
   */
  async testConnection(platform) {
    return this.post(ENDPOINTS.PLATFORM_STATUS.TEST_CONNECTION, { platform });
  }
  
  /**
   * Get platform connection history
   * @param {string} platform - Platform identifier (optional, if not provided returns all platforms)
   * @param {string} period - Time period (day, week, month)
   * @returns {Promise<Object>} - Connection history data
   */
  async getConnectionHistory(platform = null, period = 'day') {
    const params = { period };
    if (platform) {
      params.platform = platform;
    }
    
    return this.get(ENDPOINTS.PLATFORM_STATUS.HISTORY, {}, params);
  }
  
  /**
   * Get platform-specific attributes and capabilities
   * @param {string} platform - Platform identifier
   * @returns {Promise<Object>} - Platform capabilities data
   */
  async getPlatformCapabilities(platform) {
    return this.get(ENDPOINTS.PLATFORM_STATUS.CAPABILITIES, {}, { platform });
  }
  
  /**
   * Get platform API usage and quotas
   * @param {string} platform - Platform identifier
   * @returns {Promise<Object>} - API usage data
   */
  async getApiUsage(platform) {
    return this.get(ENDPOINTS.PLATFORM_STATUS.API_USAGE, {}, { platform });
  }
  
  /**
   * Update platform credentials
   * @param {string} platform - Platform identifier
   * @param {Object} credentials - Platform credentials
   * @returns {Promise<Object>} - Update response
   */
  async updateCredentials(platform, credentials) {
    return this.put(ENDPOINTS.PLATFORM_STATUS.UPDATE_CREDENTIALS, credentials, { platform });
  }
  
  /**
   * Get audience targeting capabilities for a platform
   * @param {string} platform - Platform identifier
   * @returns {Promise<Object>} - Targeting capabilities data
   */
  async getTargetingCapabilities(platform) {
    return this.get(ENDPOINTS.PLATFORM_STATUS.TARGETING_CAPABILITIES, {}, { platform });
  }
  
  /**
   * Get ad format specifications for a platform
   * @param {string} platform - Platform identifier
   * @returns {Promise<Object>} - Ad format specifications
   */
  async getAdFormats(platform) {
    return this.get(ENDPOINTS.PLATFORM_STATUS.AD_FORMATS, {}, { platform });
  }
}