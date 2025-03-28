/**
 * MagnetoCursor - Base API Service
 * Core service layer for handling API communication
 */

import { buildUrl, buildQueryUrl } from './api-config.js';
import { ErrorHandler } from './error-handler.js';

/**
 * Base service class for API communication
 * All feature-specific services should extend this class
 */
export class BaseApiService {
  /**
   * Create a new BaseApiService instance
   */
  constructor() {
    // Initialize error handler
    this.errorHandler = new ErrorHandler();
    
    // Default headers for all requests
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    };
    
    // Request options (timeout, credentials)
    this.requestOptions = {
      timeout: 30000, // 30 seconds
      credentials: 'same-origin'
    };
  }
  
  /**
   * Perform GET request
   * @param {string} endpoint - API endpoint path
   * @param {Object} params - Path parameters to replace in URL
   * @param {Object} queryParams - Query string parameters
   * @returns {Promise<Object>} - API response data
   */
  async get(endpoint, params = {}, queryParams = {}) {
    try {
      const url = this._buildUrlWithQuery(endpoint, params, queryParams);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: this.defaultHeaders,
        credentials: this.requestOptions.credentials
      });
      
      return this._handleResponse(response);
    } catch (error) {
      return this.errorHandler.handleError(error);
    }
  }
  
  /**
   * Perform POST request
   * @param {string} endpoint - API endpoint path
   * @param {Object} data - Request payload
   * @param {Object} params - Path parameters to replace in URL
   * @returns {Promise<Object>} - API response data
   */
  async post(endpoint, data = {}, params = {}) {
    try {
      const url = buildUrl(endpoint, params);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: this.defaultHeaders,
        credentials: this.requestOptions.credentials,
        body: JSON.stringify(data)
      });
      
      return this._handleResponse(response);
    } catch (error) {
      return this.errorHandler.handleError(error);
    }
  }
  
  /**
   * Perform PUT request
   * @param {string} endpoint - API endpoint path
   * @param {Object} data - Request payload
   * @param {Object} params - Path parameters to replace in URL
   * @returns {Promise<Object>} - API response data
   */
  async put(endpoint, data = {}, params = {}) {
    try {
      const url = buildUrl(endpoint, params);
      
      const response = await fetch(url, {
        method: 'PUT',
        headers: this.defaultHeaders,
        credentials: this.requestOptions.credentials,
        body: JSON.stringify(data)
      });
      
      return this._handleResponse(response);
    } catch (error) {
      return this.errorHandler.handleError(error);
    }
  }
  
  /**
   * Perform PATCH request
   * @param {string} endpoint - API endpoint path
   * @param {Object} data - Request payload
   * @param {Object} params - Path parameters to replace in URL
   * @returns {Promise<Object>} - API response data
   */
  async patch(endpoint, data = {}, params = {}) {
    try {
      const url = buildUrl(endpoint, params);
      
      const response = await fetch(url, {
        method: 'PATCH',
        headers: this.defaultHeaders,
        credentials: this.requestOptions.credentials,
        body: JSON.stringify(data)
      });
      
      return this._handleResponse(response);
    } catch (error) {
      return this.errorHandler.handleError(error);
    }
  }
  
  /**
   * Perform DELETE request
   * @param {string} endpoint - API endpoint path
   * @param {Object} params - Path parameters to replace in URL
   * @returns {Promise<Object>} - API response data
   */
  async delete(endpoint, params = {}) {
    try {
      const url = buildUrl(endpoint, params);
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: this.defaultHeaders,
        credentials: this.requestOptions.credentials
      });
      
      return this._handleResponse(response);
    } catch (error) {
      return this.errorHandler.handleError(error);
    }
  }
  
  /**
   * Upload files to the API
   * @param {string} endpoint - API endpoint path
   * @param {FormData} formData - FormData object with files
   * @param {Object} params - Path parameters to replace in URL
   * @param {Function} progressCallback - Optional callback for upload progress
   * @returns {Promise<Object>} - API response data
   */
  async upload(endpoint, formData, params = {}, progressCallback = null) {
    try {
      const url = buildUrl(endpoint, params);
      
      // Remove Content-Type header to let browser set it with boundary
      const headers = { ...this.defaultHeaders };
      delete headers['Content-Type'];
      
      const fetchOptions = {
        method: 'POST',
        headers: headers,
        credentials: this.requestOptions.credentials,
        body: formData
      };
      
      // Use XMLHttpRequest if progress reporting is needed
      if (progressCallback && typeof progressCallback === 'function') {
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          
          xhr.open('POST', url, true);
          
          // Set headers
          Object.keys(headers).forEach(key => {
            xhr.setRequestHeader(key, headers[key]);
          });
          
          // Handle progress events
          xhr.upload.addEventListener('progress', (event) => {
            if (event.lengthComputable) {
              const percentComplete = (event.loaded / event.total) * 100;
              progressCallback(percentComplete, event);
            }
          });
          
          // Handle completion
          xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                const data = JSON.parse(xhr.responseText);
                resolve(data);
              } catch (e) {
                resolve(xhr.responseText);
              }
            } else {
              reject({
                status: xhr.status,
                statusText: xhr.statusText,
                response: xhr.responseText
              });
            }
          };
          
          // Handle errors
          xhr.onerror = () => {
            reject({
              status: xhr.status,
              statusText: xhr.statusText,
              response: xhr.responseText
            });
          };
          
          // Send the request
          xhr.send(formData);
        }).catch(error => this.errorHandler.handleError(error));
      }
      
      // Use regular fetch if no progress reporting needed
      const response = await fetch(url, fetchOptions);
      return this._handleResponse(response);
      
    } catch (error) {
      return this.errorHandler.handleError(error);
    }
  }
  
  /**
   * Process API response
   * @param {Response} response - Fetch API response
   * @returns {Promise<Object>} - Parsed response data
   * @private
   */
  async _handleResponse(response) {
    // Check for JSON content
    const contentType = response.headers.get('content-type');
    const isJson = contentType && contentType.includes('application/json');
    
    // Parse response data
    const data = isJson ? await response.json() : await response.text();
    
    // Handle unsuccessful responses
    if (!response.ok) {
      const error = {
        status: response.status,
        statusText: response.statusText,
        data: data
      };
      
      return Promise.reject(error);
    }
    
    // Return successful response data
    return data;
  }
  
  /**
   * Build complete URL with query parameters
   * @param {string} endpoint - API endpoint
   * @param {Object} params - Path parameters
   * @param {Object} queryParams - Query parameters
   * @returns {string} - Complete URL
   * @private
   */
  _buildUrlWithQuery(endpoint, params, queryParams) {
    // First build the URL with path parameters
    const url = buildUrl(endpoint, params);
    
    // Then add query parameters
    return buildQueryUrl(url, queryParams);
  }
}