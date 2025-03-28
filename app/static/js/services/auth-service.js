/**
 * Auth Service
 * Handles authentication-related API operations
 */

import { BaseApiService } from './base-api-service.js';
import { ENDPOINTS } from './api-config.js';
import { validate, loginSchema, registrationSchema, passwordResetRequestSchema, passwordResetConfirmSchema, userProfileSchema } from './schemas/index.js';

/**
 * Service for authentication and user-related operations
 */
export class AuthService extends BaseApiService {
  /**
   * Get current authentication status
   * @returns {Promise<Object>} - Auth status data
   */
  async getAuthStatus() {
    return this.get(ENDPOINTS.AUTH.STATUS);
  }
  
  /**
   * Log in a user
   * @param {string} username - Username
   * @param {string} password - Password
   * @param {boolean} rememberMe - Whether to remember the user
   * @returns {Promise<Object>} - Login response
   */
  async login(username, password, rememberMe = false) {
    // Prepare login data
    const loginData = { username, password, remember_me: rememberMe };
    
    // Validate input data
    const validation = validate(loginData, loginSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid login data',
        errors: validation.errors
      });
    }
    
    return this.post(ENDPOINTS.AUTH.LOGIN, loginData);
  }
  
  /**
   * Log out the current user
   * @returns {Promise<Object>} - Logout response
   */
  async logout() {
    return this.post(ENDPOINTS.AUTH.LOGOUT);
  }
  
  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} - Registration response
   */
  async register(userData) {
    // Validate input data
    const validation = validate(userData, registrationSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid registration data',
        errors: validation.errors
      });
    }
    
    // Check if password matches confirmation
    if (userData.password !== userData.confirm_password) {
      return Promise.reject({
        status: 400,
        message: 'Passwords do not match',
        errors: [
          {
            field: 'confirm_password',
            message: 'Passwords do not match'
          }
        ]
      });
    }
    
    return this.post(ENDPOINTS.AUTH.REGISTER, userData);
  }
  
  /**
   * Request a password reset
   * @param {string} email - User email
   * @returns {Promise<Object>} - Password reset request response
   */
  async requestPasswordReset(email) {
    // Validate input data
    const validation = validate({ email }, passwordResetRequestSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid email',
        errors: validation.errors
      });
    }
    
    return this.post(ENDPOINTS.AUTH.REQUEST_RESET, { email });
  }
  
  /**
   * Confirm password reset
   * @param {string} token - Reset token
   * @param {string} password - New password
   * @param {string} confirmPassword - Confirmation of new password
   * @returns {Promise<Object>} - Password reset confirmation response
   */
  async confirmPasswordReset(token, password, confirmPassword) {
    // Prepare reset data
    const resetData = { token, password, confirm_password: confirmPassword };
    
    // Validate input data
    const validation = validate(resetData, passwordResetConfirmSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid password reset data',
        errors: validation.errors
      });
    }
    
    // Check if password matches confirmation
    if (password !== confirmPassword) {
      return Promise.reject({
        status: 400,
        message: 'Passwords do not match',
        errors: [
          {
            field: 'confirm_password',
            message: 'Passwords do not match'
          }
        ]
      });
    }
    
    return this.post(ENDPOINTS.AUTH.CONFIRM_RESET, resetData);
  }
  
  /**
   * Get current user profile
   * @returns {Promise<Object>} - User profile data
   */
  async getUserProfile() {
    return this.get(ENDPOINTS.AUTH.PROFILE);
  }
  
  /**
   * Update user profile
   * @param {Object} profileData - Updated profile data
   * @returns {Promise<Object>} - Updated profile
   */
  async updateUserProfile(profileData) {
    // Validate input data
    const validation = validate(profileData, userProfileSchema);
    if (!validation.isValid) {
      return Promise.reject({
        status: 400,
        message: 'Invalid profile data',
        errors: validation.errors
      });
    }
    
    return this.put(ENDPOINTS.AUTH.PROFILE, profileData);
  }
  
  /**
   * Upload profile image
   * @param {File} imageFile - Image file to upload
   * @param {Function} progressCallback - Optional progress callback
   * @returns {Promise<Object>} - Upload response with image URL
   */
  async uploadProfileImage(imageFile, progressCallback = null) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    return this.upload(ENDPOINTS.AUTH.UPLOAD_IMAGE, formData, {}, progressCallback);
  }
  
  /**
   * Change user password
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   * @param {string} confirmPassword - Confirmation of new password
   * @returns {Promise<Object>} - Password change response
   */
  async changePassword(currentPassword, newPassword, confirmPassword) {
    // Check if new password matches confirmation
    if (newPassword !== confirmPassword) {
      return Promise.reject({
        status: 400,
        message: 'Passwords do not match',
        errors: [
          {
            field: 'confirm_password',
            message: 'Passwords do not match'
          }
        ]
      });
    }
    
    return this.post(ENDPOINTS.AUTH.CHANGE_PASSWORD, {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    });
  }
}