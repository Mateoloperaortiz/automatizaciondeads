/**
 * Job Opening Service
 * Handles job opening-related API operations
 */

import { BaseApiService } from './base-api-service.js';
import { ENDPOINTS } from './api-config.js';
import { validate, createJobOpeningSchema, updateJobOpeningSchema } from './schemas/index.js';

/**
 * Service for job opening-related operations
 */
export class JobOpeningService extends BaseApiService {
  /**
   * Get all job openings with optional filtering
   * @param {Object} filters - Filter parameters
   * @returns {Promise<Array>} - List of job openings
   */
  async getJobOpenings(filters = {}) {
    return this.get(ENDPOINTS.JOB_OPENINGS.LIST, {}, filters);
  }
  
  /**
   * Get a single job opening by ID
   * @param {number|string} id - Job opening ID
   * @returns {Promise<Object>} - Job opening details
   */
  async getJobOpening(id) {
    return this.get(ENDPOINTS.JOB_OPENINGS.DETAIL, { id });
  }
  
  /**
   * Create a new job opening
   * @param {Object} jobData - Job opening data
   * @returns {Promise<Object>} - Created job opening
   */
  async createJobOpening(jobData) {
    // Validate input data
    const validation = validate(jobData, createJobOpeningSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid job opening data',
        errors: validation.errors
      });
    }
    
    return this.post(ENDPOINTS.JOB_OPENINGS.CREATE, jobData);
  }
  
  /**
   * Update an existing job opening
   * @param {number|string} id - Job opening ID
   * @param {Object} jobData - Updated job opening data
   * @returns {Promise<Object>} - Updated job opening
   */
  async updateJobOpening(id, jobData) {
    // Validate input data
    const validation = validate(jobData, updateJobOpeningSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid job opening data',
        errors: validation.errors
      });
    }
    
    return this.put(ENDPOINTS.JOB_OPENINGS.UPDATE, jobData, { id });
  }
  
  /**
   * Delete a job opening
   * @param {number|string} id - Job opening ID
   * @returns {Promise<Object>} - Deletion response
   */
  async deleteJobOpening(id) {
    return this.delete(ENDPOINTS.JOB_OPENINGS.DELETE, { id });
  }
  
  /**
   * Activate a job opening
   * @param {number|string} id - Job opening ID
   * @returns {Promise<Object>} - Updated job opening
   */
  async activateJobOpening(id) {
    return this.post(ENDPOINTS.JOB_OPENINGS.ACTIVATE, {}, { id });
  }
  
  /**
   * Deactivate a job opening
   * @param {number|string} id - Job opening ID
   * @returns {Promise<Object>} - Updated job opening
   */
  async deactivateJobOpening(id) {
    return this.post(ENDPOINTS.JOB_OPENINGS.DEACTIVATE, {}, { id });
  }
  
  /**
   * Search for job openings
   * @param {string} query - Search query
   * @param {Object} filters - Additional filters
   * @returns {Promise<Array>} - Matching job openings
   */
  async searchJobOpenings(query, filters = {}) {
    return this.get(ENDPOINTS.JOB_OPENINGS.SEARCH, {}, { 
      q: query,
      ...filters
    });
  }
}