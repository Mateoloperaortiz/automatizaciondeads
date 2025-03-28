/**
 * Segment Service
 * Handles segment-related API operations
 */

import { BaseApiService } from './base-api-service.js';
import { ENDPOINTS } from './api-config.js';
import { validate, createSegmentSchema, updateSegmentSchema } from './schemas/index.js';

/**
 * Service for segment-related operations
 */
export class SegmentService extends BaseApiService {
  /**
   * Get all segments
   * @param {Object} filters - Filter parameters
   * @returns {Promise<Array>} - List of segments
   */
  async getSegments(filters = {}) {
    return this.get(ENDPOINTS.SEGMENTS.LIST, {}, filters);
  }
  
  /**
   * Get a single segment by ID
   * @param {number|string} id - Segment ID
   * @returns {Promise<Object>} - Segment details
   */
  async getSegment(id) {
    return this.get(ENDPOINTS.SEGMENTS.DETAIL, { id });
  }
  
  /**
   * Create a new segment
   * @param {Object} segmentData - Segment data
   * @returns {Promise<Object>} - Created segment
   */
  async createSegment(segmentData) {
    // Validate input data
    const validation = validate(segmentData, createSegmentSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid segment data',
        errors: validation.errors
      });
    }
    
    return this.post(ENDPOINTS.SEGMENTS.CREATE, segmentData);
  }
  
  /**
   * Update an existing segment
   * @param {number|string} id - Segment ID
   * @param {Object} segmentData - Updated segment data
   * @returns {Promise<Object>} - Updated segment
   */
  async updateSegment(id, segmentData) {
    // Validate input data
    const validation = validate(segmentData, updateSegmentSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid segment data',
        errors: validation.errors
      });
    }
    
    return this.put(ENDPOINTS.SEGMENTS.UPDATE, segmentData, { id });
  }
  
  /**
   * Delete a segment
   * @param {number|string} id - Segment ID
   * @returns {Promise<Object>} - Deletion response
   */
  async deleteSegment(id) {
    return this.delete(ENDPOINTS.SEGMENTS.DELETE, { id });
  }
  
  /**
   * Get candidates in a segment
   * @param {number|string} id - Segment ID
   * @returns {Promise<Array>} - List of candidates in the segment
   */
  async getSegmentCandidates(id) {
    return this.get(ENDPOINTS.SEGMENTS.CANDIDATES, { id });
  }
  
  /**
   * Run segmentation algorithm
   * @param {Object} options - Segmentation options
   * @returns {Promise<Object>} - Task information
   */
  async runSegmentation(options = {}) {
    return this.post(ENDPOINTS.SEGMENTS.RUN_SEGMENTATION, options);
  }
  
  /**
   * Get segmentation visualization
   * @returns {Promise<Object>} - Visualization data
   */
  async getVisualization() {
    return this.get(ENDPOINTS.SEGMENTS.VISUALIZATION);
  }
  
  /**
   * Compare multiple segments
   * @param {Array<number|string>} segmentIds - Array of segment IDs to compare
   * @returns {Promise<Object>} - Comparison data
   */
  async compareSegments(segmentIds) {
    return this.get(ENDPOINTS.SEGMENTS.COMPARE, {}, { segment_ids: segmentIds });
  }
  
  /**
   * Reset a segment characteristic to its original value
   * @param {number|string} id - Segment ID
   * @param {string} characteristic - Characteristic name to reset
   * @returns {Promise<Object>} - Updated segment
   */
  async resetCharacteristic(id, characteristic) {
    return this.post(ENDPOINTS.SEGMENTS.RESET_CHARACTERISTIC, { 
      characteristic 
    }, { id });
  }
  
  /**
   * Get benchmark data for a segment
   * @param {number|string} id - Segment ID
   * @returns {Promise<Object>} - Benchmark data
   */
  async getSegmentBenchmark(id) {
    return this.get(ENDPOINTS.SEGMENTS.BENCHMARK, { id });
  }
}