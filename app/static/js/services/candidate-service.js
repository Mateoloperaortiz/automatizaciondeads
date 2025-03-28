/**
 * Candidate Service
 * Handles candidate-related API operations
 */

import { BaseApiService } from './base-api-service.js';
import { ENDPOINTS } from './api-config.js';
import { validate, createCandidateSchema, updateCandidateSchema } from './schemas/index.js';

/**
 * Service for candidate-related operations
 */
export class CandidateService extends BaseApiService {
  /**
   * Get all candidates with optional filtering
   * @param {Object} filters - Filter parameters
   * @returns {Promise<Array>} - List of candidates
   */
  async getCandidates(filters = {}) {
    return this.get(ENDPOINTS.CANDIDATES.LIST, {}, filters);
  }
  
  /**
   * Get a single candidate by ID
   * @param {number|string} id - Candidate ID
   * @returns {Promise<Object>} - Candidate details
   */
  async getCandidate(id) {
    return this.get(ENDPOINTS.CANDIDATES.DETAIL, { id });
  }
  
  /**
   * Create a new candidate
   * @param {Object} candidateData - Candidate data
   * @returns {Promise<Object>} - Created candidate
   */
  async createCandidate(candidateData) {
    // Validate input data
    const validation = validate(candidateData, createCandidateSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid candidate data',
        errors: validation.errors
      });
    }
    
    return this.post(ENDPOINTS.CANDIDATES.CREATE, candidateData);
  }
  
  /**
   * Update an existing candidate
   * @param {number|string} id - Candidate ID
   * @param {Object} candidateData - Updated candidate data
   * @returns {Promise<Object>} - Updated candidate
   */
  async updateCandidate(id, candidateData) {
    // Validate input data
    const validation = validate(candidateData, updateCandidateSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid candidate data',
        errors: validation.errors
      });
    }
    
    return this.put(ENDPOINTS.CANDIDATES.UPDATE, candidateData, { id });
  }
  
  /**
   * Delete a candidate
   * @param {number|string} id - Candidate ID
   * @returns {Promise<Object>} - Deletion response
   */
  async deleteCandidate(id) {
    return this.delete(ENDPOINTS.CANDIDATES.DELETE, { id });
  }
  
  /**
   * Search for candidates
   * @param {string} query - Search query
   * @param {Object} filters - Additional filters
   * @returns {Promise<Array>} - Matching candidates
   */
  async searchCandidates(query, filters = {}) {
    return this.get(ENDPOINTS.CANDIDATES.SEARCH, {}, { 
      q: query,
      ...filters
    });
  }
  
  /**
   * Get segments for a candidate
   * @param {number|string} id - Candidate ID
   * @returns {Promise<Array>} - List of segments the candidate belongs to
   */
  async getCandidateSegments(id) {
    return this.get(ENDPOINTS.CANDIDATES.SEGMENTS, { id });
  }
  
  /**
   * Upload candidate profile image
   * @param {number|string} id - Candidate ID
   * @param {File} imageFile - Image file to upload
   * @param {Function} progressCallback - Optional progress callback
   * @returns {Promise<Object>} - Upload response with image URL
   */
  async uploadProfileImage(id, imageFile, progressCallback = null) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    return this.upload(ENDPOINTS.CANDIDATES.UPLOAD_IMAGE, formData, { id }, progressCallback);
  }
  
  /**
   * Batch import candidates from CSV
   * @param {File} csvFile - CSV file containing candidate data
   * @param {Object} options - Import options
   * @param {Function} progressCallback - Optional progress callback
   * @returns {Promise<Object>} - Import results
   */
  async importCandidates(csvFile, options = {}, progressCallback = null) {
    const formData = new FormData();
    formData.append('file', csvFile);
    
    // Add options as form data
    Object.keys(options).forEach(key => {
      formData.append(key, options[key]);
    });
    
    return this.upload(ENDPOINTS.CANDIDATES.IMPORT, formData, {}, progressCallback);
  }
}