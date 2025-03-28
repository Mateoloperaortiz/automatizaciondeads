/**
 * MagnetoCursor - Campaign Service
 * Handles campaign-related API operations
 */

import { BaseApiService } from './base-api-service.js';
import { ENDPOINTS } from './api-config.js';

/**
 * Service for campaign-related operations
 */
export class CampaignService extends BaseApiService {
  /**
   * Get all campaigns with optional filtering
   * @param {Object} filters - Filter parameters 
   * @returns {Promise<Array>} - List of campaigns
   */
  async getCampaigns(filters = {}) {
    return this.get(ENDPOINTS.CAMPAIGNS.LIST, {}, filters);
  }
  
  /**
   * Get a single campaign by ID
   * @param {number|string} id - Campaign ID
   * @returns {Promise<Object>} - Campaign details
   */
  async getCampaign(id) {
    return this.get(ENDPOINTS.CAMPAIGNS.DETAIL, { id });
  }
  
  /**
   * Create a new campaign
   * @param {Object} campaignData - Campaign data
   * @returns {Promise<Object>} - Created campaign
   */
  async createCampaign(campaignData) {
    return this.post(ENDPOINTS.CAMPAIGNS.CREATE, campaignData);
  }
  
  /**
   * Update an existing campaign
   * @param {number|string} id - Campaign ID
   * @param {Object} campaignData - Updated campaign data
   * @returns {Promise<Object>} - Updated campaign
   */
  async updateCampaign(id, campaignData) {
    return this.put(ENDPOINTS.CAMPAIGNS.UPDATE, campaignData, { id });
  }
  
  /**
   * Delete a campaign
   * @param {number|string} id - Campaign ID
   * @returns {Promise<Object>} - Deletion response
   */
  async deleteCampaign(id) {
    return this.delete(ENDPOINTS.CAMPAIGNS.DELETE, { id });
  }
  
  /**
   * Publish a campaign to social media platforms
   * @param {number|string} id - Campaign ID
   * @param {Object} publishOptions - Publishing options
   * @returns {Promise<Object>} - Publishing response
   */
  async publishCampaign(id, publishOptions = {}) {
    return this.post(ENDPOINTS.CAMPAIGNS.PUBLISH, publishOptions, { id });
  }
  
  /**
   * Upload campaign image
   * @param {File} imageFile - Image file to upload
   * @param {Function} progressCallback - Optional progress callback
   * @returns {Promise<Object>} - Upload response with image URL
   */
  async uploadCampaignImage(imageFile, progressCallback = null) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    return this.upload(ENDPOINTS.UPLOADS.IMAGE, formData, {}, progressCallback);
  }
  
  /**
   * Validates campaign data before submission
   * @param {Object} campaignData - Campaign data to validate
   * @returns {Object} - Validation result {valid: boolean, errors: Array}
   */
  validateCampaignData(campaignData) {
    const errors = [];
    
    // Check title
    if (!campaignData.title) {
      errors.push('Campaign title is required');
    }
    
    // Check dates
    if (!campaignData.start_date || !campaignData.end_date) {
      errors.push('Campaign start and end dates are required');
    } else if (new Date(campaignData.start_date) >= new Date(campaignData.end_date)) {
      errors.push('Start date must be before end date');
    }
    
    // Check budget
    if (!campaignData.budget || campaignData.budget <= 0) {
      errors.push('Campaign budget must be greater than 0');
    }
    
    // Check platforms
    if (!campaignData.platform_ids || campaignData.platform_ids.length === 0) {
      errors.push('Please select at least one platform');
    }
    
    // Check jobs
    if (!campaignData.job_opening_ids || campaignData.job_opening_ids.length === 0) {
      errors.push('Please select at least one job opening');
    }
    
    // Check ad content
    if (!campaignData.ad_headline || !campaignData.ad_text) {
      errors.push('Ad headline and text are required');
    }
    
    return {
      valid: errors.length === 0,
      errors: errors
    };
  }
}