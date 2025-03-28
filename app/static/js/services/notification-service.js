/**
 * Notification Service
 * Handles notification-related API operations
 */

import { BaseApiService } from './base-api-service.js';
import { ENDPOINTS } from './api-config.js';
import { websocketService } from './websocket-service.js';

/**
 * Service for notification-related operations
 */
export class NotificationService extends BaseApiService {
  /**
   * Create a new NotificationService
   */
  constructor() {
    super();
    this.wsEndpoint = '/api/notifications/ws';
    this.activeSubscription = null;
    this.messageListeners = new Map();
  }
  
  /**
   * Get all notifications for the current user
   * @param {Object} options - Filtering and pagination options
   * @returns {Promise<Array>} - List of notifications
   */
  async getNotifications(options = {}) {
    return this.get(ENDPOINTS.NOTIFICATIONS.LIST, {}, options);
  }
  
  /**
   * Get a single notification by ID
   * @param {number|string} id - Notification ID
   * @returns {Promise<Object>} - Notification details
   */
  async getNotification(id) {
    return this.get(ENDPOINTS.NOTIFICATIONS.DETAIL, { id });
  }
  
  /**
   * Mark a notification as read
   * @param {number|string} id - Notification ID
   * @returns {Promise<Object>} - Updated notification
   */
  async markAsRead(id) {
    return this.post(ENDPOINTS.NOTIFICATIONS.MARK_READ, {}, { id });
  }
  
  /**
   * Mark all notifications as read
   * @returns {Promise<Object>} - Operation response
   */
  async markAllAsRead() {
    return this.post(ENDPOINTS.NOTIFICATIONS.MARK_ALL_READ);
  }
  
  /**
   * Delete a notification
   * @param {number|string} id - Notification ID
   * @returns {Promise<Object>} - Deletion response
   */
  async deleteNotification(id) {
    return this.delete(ENDPOINTS.NOTIFICATIONS.DELETE, { id });
  }
  
  /**
   * Get unread notification count
   * @returns {Promise<Object>} - Unread count data
   */
  async getUnreadCount() {
    return this.get(ENDPOINTS.NOTIFICATIONS.UNREAD_COUNT);
  }
  
  /**
   * Update notification preferences
   * @param {Object} preferences - Notification preferences
   * @returns {Promise<Object>} - Updated preferences
   */
  async updatePreferences(preferences) {
    return this.put(ENDPOINTS.NOTIFICATIONS.PREFERENCES, preferences);
  }
  
  /**
   * Subscribe to notification channels for real-time updates
   * @returns {Promise<boolean>} - Whether subscription was successful
   */
  async subscribeToNotifications() {
    try {
      // Connect to WebSocket
      await websocketService.connect(this.wsEndpoint);
      
      // Authentication handshake
      const authSuccess = await this._performAuthHandshake();
      if (!authSuccess) {
        throw new Error('Failed to authenticate with notification server');
      }
      
      this.activeSubscription = true;
      return true;
    } catch (error) {
      console.error('Failed to subscribe to notifications:', error);
      this.activeSubscription = false;
      return false;
    }
  }
  
  /**
   * Unsubscribe from notification channels
   */
  unsubscribeFromNotifications() {
    if (this.activeSubscription) {
      // Send unsubscribe message if socket is open
      if (websocketService.getState() === 'CONNECTED') {
        websocketService.send({
          type: 'unsubscribe',
          channels: ['notifications']
        });
      }
      
      this.activeSubscription = false;
    }
  }
  
  /**
   * Register a listener for a specific notification event
   * @param {string} event - Event name
   * @param {Function} callback - Event handler function
   * @returns {Function} - Function to remove the listener
   */
  onNotification(event, callback) {
    // Ensure we're connected to the WebSocket
    if (!this.activeSubscription) {
      this.subscribeToNotifications();
    }
    
    // Register with WebSocket service
    websocketService.on(event, callback);
    
    // Return function to remove the listener
    return () => {
      websocketService.off(event, callback);
    };
  }
  
  /**
   * Listen for all notifications
   * @param {Function} callback - Function to call with notification data
   * @returns {Function} - Function to remove the listener
   */
  onAnyNotification(callback) {
    return this.onNotification('notification', callback);
  }
  
  /**
   * Create a notification (admin only)
   * @param {Object} notificationData - Notification data
   * @returns {Promise<Object>} - Created notification
   */
  async createNotification(notificationData) {
    return this.post(ENDPOINTS.NOTIFICATIONS.CREATE, notificationData);
  }
  
  /**
   * Send a notification to specific users (admin only)
   * @param {Object} notification - Notification data
   * @param {Array<number>} userIds - User IDs to send to
   * @returns {Promise<Object>} - Result
   */
  async sendToUsers(notification, userIds) {
    return this.post(ENDPOINTS.NOTIFICATIONS.SEND_TO_USERS, {
      notification,
      user_ids: userIds
    });
  }
  
  /**
   * Send a notification to all users (admin only)
   * @param {Object} notification - Notification data
   * @returns {Promise<Object>} - Result
   */
  async broadcastToAll(notification) {
    return this.post(ENDPOINTS.NOTIFICATIONS.BROADCAST, { notification });
  }
  
  /**
   * Perform authentication handshake with WebSocket server
   * @returns {Promise<boolean>} - Whether authentication was successful
   * @private
   */
  async _performAuthHandshake() {
    return new Promise((resolve) => {
      // Set up handler for auth response
      const authHandler = (data) => {
        if (data.type === 'auth_response') {
          websocketService.off('message', authHandler);
          resolve(data.success === true);
        }
      };
      
      // Listen for auth response
      websocketService.on('message', authHandler);
      
      // Send auth request (the actual JWT will be sent in the cookies)
      websocketService.send({
        type: 'auth',
        timestamp: Date.now()
      });
      
      // Set timeout for auth response
      setTimeout(() => {
        websocketService.off('message', authHandler);
        resolve(false);
      }, 5000);
    });
  }
}