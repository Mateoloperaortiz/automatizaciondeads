/**
 * Real-Time Notification System
 * Integrates WebSocket service with notification system
 */

import { notificationService, websocketService } from './index.js';

/**
 * RealTimeNotificationManager
 * Manages real-time notifications, desktop notifications, and toast notifications
 */
export class RealTimeNotificationManager {
  /**
   * Create a new RealTimeNotificationManager
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = {
      wsEndpoint: '/api/notifications/ws',
      notificationCountSelector: '.notification-counter',
      notificationListSelector: '.notification-list',
      notificationDropdownSelector: '.notification-dropdown',
      maxNotificationsInDropdown: 5,
      enableDesktopNotifications: true,
      autoConnect: true,
      ...options
    };
    
    // State
    this.isConnected = false;
    this.isInitialized = false;
    this.notifications = [];
    this.unreadCount = 0;
    this.hasDesktopPermission = false;
    
    // Element references
    this.notificationCounter = document.querySelector(this.options.notificationCountSelector);
    this.notificationList = document.querySelector(this.options.notificationListSelector);
    this.notificationDropdown = document.querySelector(this.options.notificationDropdownSelector);
    
    // Init
    if (this.options.autoConnect) {
      this.init();
    }
  }
  
  /**
   * Initialize the notification manager
   */
  async init() {
    if (this.isInitialized) return;
    
    try {
      // Request desktop notification permission
      if (this.options.enableDesktopNotifications) {
        await this.requestNotificationPermission();
      }
      
      // Set up event listeners
      this.setupEventListeners();
      
      // Fetch initial notifications
      await this.fetchNotifications();
      
      // Connect to WebSocket
      this.connect();
      
      this.isInitialized = true;
    } catch (error) {
      console.error('Error initializing RealTimeNotificationManager:', error);
    }
  }
  
  /**
   * Set up event listeners
   */
  setupEventListeners() {
    // Mark as read click handler
    document.addEventListener('click', (e) => {
      if (e.target.closest('.mark-read-btn')) {
        const btn = e.target.closest('.mark-read-btn');
        const notificationId = btn.dataset.id;
        
        if (notificationId) {
          this.markAsRead(notificationId);
          e.preventDefault();
        }
      }
    });
    
    // Mark all as read button
    const markAllReadBtn = document.querySelector('.mark-all-read-btn');
    if (markAllReadBtn) {
      markAllReadBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.markAllAsRead();
      });
    }
  }
  
  /**
   * Connect to WebSocket for real-time notifications
   */
  async connect() {
    try {
      // Connect to WebSocket endpoint
      await websocketService.connect(this.options.wsEndpoint);
      
      // Register event listeners
      websocketService.on('notification', (data) => this.handleNewNotification(data));
      websocketService.on('notification_read', (data) => this.handleNotificationRead(data));
      websocketService.on('notification_count', (data) => this.updateUnreadCount(data.count));
      
      // Set connected state
      this.isConnected = true;
      
      console.log('Real-time notification system connected');
    } catch (error) {
      console.error('Failed to connect to notification WebSocket:', error);
      
      // Retry connection after delay
      setTimeout(() => this.connect(), 5000);
    }
  }
  
  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    websocketService.disconnect();
    this.isConnected = false;
  }
  
  /**
   * Fetch notifications from API
   */
  async fetchNotifications() {
    try {
      // Get unread count
      const countResponse = await notificationService.getUnreadCount();
      this.updateUnreadCount(countResponse.count);
      
      // Get recent notifications
      const response = await notificationService.getNotifications({
        limit: this.options.maxNotificationsInDropdown,
        unread_only: true
      });
      
      if (response.success) {
        this.notifications = response.data;
        this.updateNotificationUI();
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  }
  
  /**
   * Handle a new notification received via WebSocket
   * @param {Object} notification - Notification data
   */
  handleNewNotification(notification) {
    // Add to local notifications array
    this.notifications.unshift(notification);
    
    // Limit the number of notifications in memory
    if (this.notifications.length > this.options.maxNotificationsInDropdown) {
      this.notifications.pop();
    }
    
    // Update the UI
    this.updateNotificationUI();
    
    // Increment unread count
    this.updateUnreadCount(this.unreadCount + 1);
    
    // Show desktop notification if enabled
    this.showDesktopNotification(notification);
    
    // Show toast notification
    this.showToastNotification(notification);
  }
  
  /**
   * Handle notification read event from WebSocket
   * @param {Object} data - Notification read data
   */
  handleNotificationRead(data) {
    const { notification_id } = data;
    
    // Find and update the notification
    const notification = this.notifications.find(n => n.id === notification_id);
    if (notification) {
      notification.is_read = true;
    }
    
    // Update UI
    this.updateNotificationUI();
    
    // Update count (the server should send a separate count update event)
  }
  
  /**
   * Update notification counter display
   * @param {number} count - Unread count
   */
  updateUnreadCount(count) {
    this.unreadCount = count;
    
    // Update counter badge if it exists
    if (this.notificationCounter) {
      this.notificationCounter.textContent = count;
      this.notificationCounter.style.display = count > 0 ? 'block' : 'none';
    }
    
    // Update document title to show notification count
    this.updateDocumentTitle(count);
  }
  
  /**
   * Update document title to show notification count
   * @param {number} count - Unread count
   */
  updateDocumentTitle(count) {
    // Get original title without count
    const originalTitle = document.title.replace(/^\(\d+\) /, '');
    
    // Add count to title if there are unread notifications
    if (count > 0) {
      document.title = `(${count}) ${originalTitle}`;
    } else {
      document.title = originalTitle;
    }
  }
  
  /**
   * Update notification list UI
   */
  updateNotificationUI() {
    if (!this.notificationList) return;
    
    // Clear existing notifications
    this.notificationList.innerHTML = '';
    
    if (this.notifications.length === 0) {
      // Show empty state
      const emptyItem = document.createElement('div');
      emptyItem.className = 'dropdown-item text-center p-3';
      emptyItem.textContent = 'No notifications';
      this.notificationList.appendChild(emptyItem);
      return;
    }
    
    // Add notifications to list
    for (const notification of this.notifications) {
      const item = document.createElement('div');
      item.className = `dropdown-item notification-item ${notification.is_read ? 'read' : 'unread'}`;
      
      // Determine icon based on notification type
      let iconClass = 'fa-info-circle text-primary';
      if (notification.type === 'success') iconClass = 'fa-check-circle text-success';
      if (notification.type === 'warning') iconClass = 'fa-exclamation-triangle text-warning';
      if (notification.type === 'error') iconClass = 'fa-exclamation-circle text-danger';
      
      // Format time
      const time = this.formatTime(notification.created_at);
      
      // Create HTML
      item.innerHTML = `
        <div class="d-flex align-items-center">
          <div class="flex-shrink-0">
            <i class="fas ${iconClass} fa-lg mt-1"></i>
          </div>
          <div class="flex-grow-1 ms-3">
            <h6 class="mb-0">${notification.title}</h6>
            <div class="text-muted small">${notification.message}</div>
            <div class="d-flex justify-content-between align-items-center mt-1">
              <small class="text-muted">${time}</small>
              ${!notification.is_read ? `
              <button class="btn btn-sm btn-link p-0 mark-read-btn" data-id="${notification.id}">
                Mark as read
              </button>
              ` : ''}
            </div>
          </div>
        </div>
      `;
      
      this.notificationList.appendChild(item);
    }
    
    // Add separator
    const separator = document.createElement('div');
    separator.className = 'dropdown-divider';
    this.notificationList.appendChild(separator);
    
    // Add "View all" link
    const viewAll = document.createElement('a');
    viewAll.href = '/notifications';
    viewAll.className = 'dropdown-item text-center';
    viewAll.textContent = 'View all notifications';
    this.notificationList.appendChild(viewAll);
  }
  
  /**
   * Format notification timestamp to relative time
   * @param {string} timestamp - ISO datetime string
   * @returns {string} - Formatted relative time
   */
  formatTime(timestamp) {
    const now = new Date();
    const notificationTime = new Date(timestamp);
    const diffMs = now - notificationTime;
    const diffSeconds = Math.floor(diffMs / 1000);
    
    // Less than a minute
    if (diffSeconds < 60) {
      return 'Just now';
    }
    
    // Less than an hour
    const diffMinutes = Math.floor(diffSeconds / 60);
    if (diffMinutes < 60) {
      return `${diffMinutes} minute${diffMinutes === 1 ? '' : 's'} ago`;
    }
    
    // Less than a day
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) {
      return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
    }
    
    // Less than a week
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) {
      return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;
    }
    
    // Format as date
    return notificationTime.toLocaleDateString();
  }
  
  /**
   * Mark a notification as read
   * @param {number|string} id - Notification ID
   */
  async markAsRead(id) {
    try {
      await notificationService.markAsRead(id);
      
      // Update local state
      const notification = this.notifications.find(n => n.id === parseInt(id));
      if (notification) {
        notification.is_read = true;
      }
      
      // Update UI
      this.updateNotificationUI();
      
      // Update count
      this.updateUnreadCount(Math.max(0, this.unreadCount - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  }
  
  /**
   * Mark all notifications as read
   */
  async markAllAsRead() {
    try {
      await notificationService.markAllAsRead();
      
      // Update all notifications to read
      this.notifications.forEach(notification => {
        notification.is_read = true;
      });
      
      // Update UI
      this.updateNotificationUI();
      
      // Update count
      this.updateUnreadCount(0);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  }
  
  /**
   * Request permission for desktop notifications
   * @returns {Promise<boolean>} - Whether permission was granted
   */
  async requestNotificationPermission() {
    if (!('Notification' in window)) {
      return false;
    }
    
    if (Notification.permission === 'granted') {
      this.hasDesktopPermission = true;
      return true;
    }
    
    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      this.hasDesktopPermission = permission === 'granted';
      return this.hasDesktopPermission;
    }
    
    return false;
  }
  
  /**
   * Show desktop notification
   * @param {Object} notification - Notification data
   */
  showDesktopNotification(notification) {
    if (!this.hasDesktopPermission || !('Notification' in window)) {
      return;
    }
    
    const title = `MagnetoCursor: ${notification.title}`;
    const options = {
      body: notification.message,
      icon: '/static/img/logo-sm.png',
      badge: '/static/img/badge.png',
      tag: `notification-${notification.id}`,
      requireInteraction: notification.type === 'error'
    };
    
    const desktopNotification = new Notification(title, options);
    
    // Handle click on the notification
    desktopNotification.onclick = () => {
      window.focus();
      
      // Navigate to related entity if available
      if (notification.related_entity_type && notification.related_entity_id) {
        window.location.href = `/${notification.related_entity_type}/${notification.related_entity_id}`;
      } else {
        window.location.href = '/notifications';
      }
      
      // Close the notification
      desktopNotification.close();
    };
  }
  
  /**
   * Show toast notification
   * @param {Object} notification - Notification data
   */
  showToastNotification(notification) {
    // Map notification type to toast type
    let toastType = 'info';
    if (notification.type === 'success') toastType = 'success';
    if (notification.type === 'warning') toastType = 'warning';
    if (notification.type === 'error') toastType = 'error';
    
    // Use the global showToast function if available
    if (typeof showToast === 'function') {
      showToast(notification.message, toastType, 5000);
    }
  }
}

// Create singleton instance
const realTimeNotificationManager = new RealTimeNotificationManager();

export { realTimeNotificationManager };