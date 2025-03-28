/**
 * MagnetoCursor - Standardized Error Handler
 * Centralized error processing and notification system
 */

// Error type constants
export const ERROR_TYPES = {
  NETWORK: 'network_error',
  SERVER: 'server_error',
  VALIDATION: 'validation_error',
  AUTHORIZATION: 'authorization_error',
  NOT_FOUND: 'not_found_error',
  API_ERROR: 'api_error',
  UNKNOWN: 'unknown_error'
};

/**
 * ErrorHandler class for centralized error processing
 */
export class ErrorHandler {
  /**
   * Create a new ErrorHandler instance
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = {
      showNotifications: true,  // Whether to show UI notifications
      logErrors: true,          // Whether to log errors to console
      captureAnalytics: true,   // Whether to send errors to analytics
      ...options
    };
    
    this.notificationTimeout = 5000;  // Default notification display time
  }
  
  /**
   * Main error handling method
   * @param {Error|Object} error - The error object
   * @returns {Promise} - Rejected promise with standardized error format
   */
  handleError(error) {
    // Determine error type and extract details
    const errorType = this._categorizeError(error);
    const errorDetails = this._extractErrorDetails(error);
    
    // Log error if enabled
    if (this.options.logErrors) {
      this._logError(error, errorType, errorDetails);
    }
    
    // Generate user-friendly message
    const userMessage = this._formatUserMessage(error, errorType, errorDetails);
    
    // Show notification if enabled
    if (this.options.showNotifications) {
      this._showNotification(userMessage, errorType);
    }
    
    // Send to analytics if enabled
    if (this.options.captureAnalytics) {
      this._captureErrorAnalytics(error, errorType, errorDetails);
    }
    
    // Return standardized rejected promise
    return Promise.reject({
      original: error,
      type: errorType,
      message: userMessage,
      details: errorDetails,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Categorize errors into standard types
   * @param {Error|Object} error - The error to categorize
   * @returns {string} - Error type constant
   * @private
   */
  _categorizeError(error) {
    // Network errors (fetch API)
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      return ERROR_TYPES.NETWORK;
    }
    
    // Handle HTTP response errors
    if (error.status) {
      const status = error.status;
      
      // 401, 403 - Auth errors
      if (status === 401 || status === 403) {
        return ERROR_TYPES.AUTHORIZATION;
      }
      
      // 404 - Not found
      if (status === 404) {
        return ERROR_TYPES.NOT_FOUND;
      }
      
      // 400, 422 - Validation errors
      if (status === 400 || status === 422) {
        return ERROR_TYPES.VALIDATION;
      }
      
      // 500+ - Server errors
      if (status >= 500) {
        return ERROR_TYPES.SERVER;
      }
      
      // Other HTTP errors
      return ERROR_TYPES.API_ERROR;
    }
    
    // Default to unknown error
    return ERROR_TYPES.UNKNOWN;
  }
  
  /**
   * Extract meaningful details from error objects
   * @param {Error|Object} error - The error to examine
   * @returns {Object} - Extracted details
   * @private
   */
  _extractErrorDetails(error) {
    const details = {};
    
    // Extract HTTP details if available
    if (error.status) {
      details.status = error.status;
      details.statusText = error.statusText;
    }
    
    // Extract message or error code
    if (error.message) {
      details.message = error.message;
    }
    
    // Extract API response details
    if (error.data) {
      details.data = error.data;
      
      // Extract validation errors from response
      if (error.data.errors) {
        details.validationErrors = error.data.errors;
      }
    }
    
    return details;
  }
  
  /**
   * Create user-friendly error message
   * @param {Error|Object} error - The original error
   * @param {string} errorType - The categorized error type
   * @param {Object} details - Extracted error details
   * @returns {string} - User-friendly message
   * @private
   */
  _formatUserMessage(error, errorType, details) {
    // Create user message based on error type
    switch (errorType) {
      case ERROR_TYPES.NETWORK:
        return 'Unable to connect to the server. Please check your internet connection.';
        
      case ERROR_TYPES.AUTHORIZATION:
        return 'You don\'t have permission to perform this action.';
        
      case ERROR_TYPES.NOT_FOUND:
        return 'The requested resource was not found.';
        
      case ERROR_TYPES.VALIDATION:
        // Use API validation message if available
        if (details.data && details.data.message) {
          return details.data.message;
        }
        return 'Please check your input and try again.';
        
      case ERROR_TYPES.SERVER:
        return 'The server encountered an error. Please try again later.';
        
      case ERROR_TYPES.API_ERROR:
        // Use API error message if available
        if (details.data && details.data.message) {
          return details.data.message;
        }
        return 'An error occurred while processing your request.';
        
      case ERROR_TYPES.UNKNOWN:
      default:
        return 'An unexpected error occurred. Please try again.';
    }
  }
  
  /**
   * Log error to console
   * @param {Error|Object} error - The original error
   * @param {string} errorType - The categorized error type
   * @param {Object} details - Extracted error details
   * @private
   */
  _logError(error, errorType, details) {
    console.group('API Error');
    console.error(`Error Type: ${errorType}`);
    console.error('Original Error:', error);
    console.error('Details:', details);
    console.groupEnd();
  }
  
  /**
   * Show error notification in the UI
   * @param {string} message - User-friendly message
   * @param {string} errorType - The error type
   * @private
   */
  _showNotification(message, errorType) {
    // Map error types to notification types
    let notificationType = 'error';
    
    if (errorType === ERROR_TYPES.VALIDATION) {
      notificationType = 'warning';
    }
    
    // Use the global showToast function from app.js if available
    if (typeof showToast === 'function') {
      showToast(message, notificationType, this.notificationTimeout);
    } else {
      // Fallback if showToast is not available
      console.warn('Toast notification system not available');
      alert(message);
    }
  }
  
  /**
   * Send error data to analytics service
   * @param {Error|Object} error - The original error
   * @param {string} errorType - The error type
   * @param {Object} details - Error details
   * @private
   */
  _captureErrorAnalytics(error, errorType, details) {
    // Implementation would depend on your analytics system
    // This is a placeholder for future implementation
    
    // Example: send to a hypothetical analytics service
    if (window.analyticsService) {
      window.analyticsService.trackError({
        type: errorType,
        message: details.message || error.message,
        status: details.status,
        timestamp: new Date().toISOString()
      });
    }
  }
}