/**
 * MagnetoCursor - Real-time Notification System
 * Refactored to use the service layer
 */

import { notificationService, websocketService } from './services/index.js';
import { realTimeNotificationManager } from './services/real-time-notification.js';

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize real-time notification manager
  realTimeNotificationManager.init();
  
  // Get DOM elements for notification page (if on notification page)
  const notificationPageContainer = document.getElementById('notification-page-container');
  
  // If we're on the notification page, set up advanced features
  if (notificationPageContainer) {
    initNotificationPage();
  }
});

/**
 * Initialize the notification page interface
 */
async function initNotificationPage() {
  // Elements
  const notificationList = document.getElementById('notification-list');
  const notificationFilters = document.getElementById('notification-filters');
  const loadMoreBtn = document.getElementById('load-more-notifications');
  const markAllReadBtn = document.getElementById('mark-all-read-btn');
  
  // State
  let currentPage = 1;
  let hasMoreNotifications = true;
  let currentFilters = {
    type: 'all',
    read: 'all'
  };
  
  // Load initial notifications
  await loadNotifications();
  
  // Set up event listeners
  setupEventListeners();
  
  /**
   * Set up event listeners for the notification page
   */
  function setupEventListeners() {
    // Filter change
    if (notificationFilters) {
      const typeFilter = notificationFilters.querySelector('select[name="type"]');
      const readFilter = notificationFilters.querySelector('select[name="read"]');
      
      if (typeFilter) {
        typeFilter.addEventListener('change', () => {
          currentFilters.type = typeFilter.value;
          resetAndReload();
        });
      }
      
      if (readFilter) {
        readFilter.addEventListener('change', () => {
          currentFilters.read = readFilter.value;
          resetAndReload();
        });
      }
    }
    
    // Load more button
    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        currentPage++;
        await loadNotifications(false); // Don't reset, append
      });
    }
    
    // Mark all as read button
    if (markAllReadBtn) {
      markAllReadBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        await markAllAsRead();
      });
    }
    
    // Individual notification actions
    if (notificationList) {
      notificationList.addEventListener('click', async (e) => {
        // Mark as read button
        if (e.target.closest('.mark-read-btn')) {
          e.preventDefault();
          const btn = e.target.closest('.mark-read-btn');
          const notificationId = btn.dataset.id;
          
          if (notificationId) {
            await markAsRead(notificationId);
          }
        }
        
        // Delete button
        if (e.target.closest('.delete-notification-btn')) {
          e.preventDefault();
          const btn = e.target.closest('.delete-notification-btn');
          const notificationId = btn.dataset.id;
          
          if (notificationId) {
            await deleteNotification(notificationId);
          }
        }
      });
    }
    
    // Setup WebSocket for real-time updates
    setupRealTimeUpdates();
  }
  
  /**
   * Reset pagination and reload notifications
   */
  function resetAndReload() {
    currentPage = 1;
    hasMoreNotifications = true;
    loadNotifications(true); // Reset list
  }
  
  /**
   * Load notifications with current filters and pagination
   * @param {boolean} reset - Whether to reset the list or append
   */
  async function loadNotifications(reset = true) {
    // Show loading state
    toggleLoading(true);
    
    try {
      // Prepare query parameters
      const params = {
        page: currentPage,
        per_page: 10,
        ...currentFilters
      };
      
      // Convert filter values to API expected format
      if (params.type === 'all') delete params.type;
      if (params.read === 'all') delete params.read;
      if (params.read === 'read') params.is_read = true;
      if (params.read === 'unread') params.is_read = false;
      
      delete params.read; // Remove the read param as we use is_read
      
      // Fetch notifications using service
      const response = await notificationService.getNotifications(params);
      
      if (response.success) {
        // Render notifications
        renderNotifications(response.data, reset);
        
        // Update load more button
        hasMoreNotifications = response.has_more || false;
        if (loadMoreBtn) {
          loadMoreBtn.style.display = hasMoreNotifications ? 'block' : 'none';
        }
      } else {
        showError('Failed to load notifications');
      }
    } catch (error) {
      console.error('Error loading notifications:', error);
      showError('Error loading notifications');
    } finally {
      toggleLoading(false);
    }
  }
  
  /**
   * Render notifications to the list
   * @param {Array} notifications - List of notifications
   * @param {boolean} reset - Whether to reset the list or append
   */
  function renderNotifications(notifications, reset = true) {
    if (!notificationList) return;
    
    // Reset list if needed
    if (reset) {
      notificationList.innerHTML = '';
    }
    
    // Show empty state if no notifications
    if (notifications.length === 0 && reset) {
      const emptyState = document.createElement('div');
      emptyState.className = 'notification-empty-state text-center p-5';
      emptyState.innerHTML = `
        <i class="fas fa-bell fa-3x text-muted mb-3"></i>
        <h5>No notifications</h5>
        <p class="text-muted">You don't have any notifications matching the current filters.</p>
      `;
      notificationList.appendChild(emptyState);
      return;
    }
    
    // Render each notification
    notifications.forEach(notification => {
      const item = createNotificationElement(notification);
      notificationList.appendChild(item);
    });
  }
  
  /**
   * Create a notification list item element
   * @param {Object} notification - Notification data
   * @returns {HTMLElement} - Notification element
   */
  function createNotificationElement(notification) {
    const item = document.createElement('div');
    item.className = `notification-item ${notification.is_read ? 'read' : 'unread'}`;
    item.dataset.id = notification.id;
    
    // Determine icon based on notification type
    let iconClass = 'fa-info-circle text-primary';
    if (notification.type === 'success') iconClass = 'fa-check-circle text-success';
    if (notification.type === 'warning') iconClass = 'fa-exclamation-triangle text-warning';
    if (notification.type === 'error') iconClass = 'fa-exclamation-circle text-danger';
    
    // Format time
    const time = formatTime(notification.created_at);
    
    // Create HTML
    item.innerHTML = `
      <div class="card mb-3">
        <div class="card-body">
          <div class="row">
            <div class="col-auto">
              <i class="fas ${iconClass} fa-2x"></i>
            </div>
            <div class="col">
              <h5 class="card-title">${notification.title}</h5>
              <p class="card-text">${notification.message}</p>
              <div class="d-flex justify-content-between align-items-center">
                <small class="text-muted">${time}</small>
                <div class="btn-group">
                  ${!notification.is_read ? `
                    <button class="btn btn-sm btn-outline-primary mark-read-btn" data-id="${notification.id}">
                      Mark as read
                    </button>
                  ` : ''}
                  <button class="btn btn-sm btn-outline-danger delete-notification-btn" data-id="${notification.id}">
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    
    return item;
  }
  
  /**
   * Format notification timestamp to relative time
   * @param {string} timestamp - ISO datetime string
   * @returns {string} - Formatted relative time
   */
  function formatTime(timestamp) {
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
  async function markAsRead(id) {
    try {
      const response = await notificationService.markAsRead(id);
      
      if (response.success) {
        // Update UI
        const notificationItem = notificationList.querySelector(`.notification-item[data-id="${id}"]`);
        if (notificationItem) {
          // Add read class
          notificationItem.classList.add('read');
          notificationItem.classList.remove('unread');
          
          // Remove mark as read button
          const readBtn = notificationItem.querySelector('.mark-read-btn');
          if (readBtn) {
            readBtn.remove();
          }
        }
        
        // Show success message
        showToast('Notification marked as read', 'success');
      } else {
        showToast('Failed to mark notification as read', 'error');
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
      showToast('Error marking notification as read', 'error');
    }
  }
  
  /**
   * Mark all notifications as read
   */
  async function markAllAsRead() {
    try {
      const response = await notificationService.markAllAsRead();
      
      if (response.success) {
        // Update UI - add read class to all notifications
        const unreadItems = notificationList.querySelectorAll('.notification-item.unread');
        unreadItems.forEach(item => {
          item.classList.add('read');
          item.classList.remove('unread');
          
          // Remove mark as read button
          const readBtn = item.querySelector('.mark-read-btn');
          if (readBtn) {
            readBtn.remove();
          }
        });
        
        // Show success message
        showToast('All notifications marked as read', 'success');
      } else {
        showToast('Failed to mark all notifications as read', 'error');
      }
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      showToast('Error marking all notifications as read', 'error');
    }
  }
  
  /**
   * Delete a notification
   * @param {number|string} id - Notification ID
   */
  async function deleteNotification(id) {
    try {
      const response = await notificationService.deleteNotification(id);
      
      if (response.success) {
        // Remove notification from UI with animation
        const notificationItem = notificationList.querySelector(`.notification-item[data-id="${id}"]`);
        if (notificationItem) {
          notificationItem.style.opacity = '0';
          setTimeout(() => {
            notificationItem.remove();
            
            // Check if list is empty
            if (notificationList.children.length === 0) {
              resetAndReload();
            }
          }, 300);
        }
        
        // Show success message
        showToast('Notification deleted', 'success');
      } else {
        showToast('Failed to delete notification', 'error');
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
      showToast('Error deleting notification', 'error');
    }
  }
  
  /**
   * Toggle loading state
   * @param {boolean} isLoading - Whether loading is active
   */
  function toggleLoading(isLoading) {
    const loadingElement = document.getElementById('notification-loading');
    if (loadingElement) {
      loadingElement.style.display = isLoading ? 'block' : 'none';
    }
    
    if (loadMoreBtn) {
      loadMoreBtn.disabled = isLoading;
      loadMoreBtn.innerHTML = isLoading ? 
        '<i class="fas fa-spinner fa-spin"></i> Loading...' : 
        'Load more';
    }
  }
  
  /**
   * Show error message
   * @param {string} message - Error message
   */
  function showError(message) {
    const errorElement = document.getElementById('notification-error');
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.style.display = 'block';
      
      // Hide after 3 seconds
      setTimeout(() => {
        errorElement.style.display = 'none';
      }, 3000);
    }
  }
  
  /**
   * Set up real-time updates for notifications
   */
  function setupRealTimeUpdates() {
    // Subscribe to new notifications
    notificationService.onNotification('notification', (notification) => {
      // Add new notification to the top of the list if it matches filters
      if (shouldShowNotification(notification)) {
        const notificationElement = createNotificationElement(notification);
        
        // Add to top with animation
        notificationElement.style.opacity = '0';
        if (notificationList.firstChild) {
          notificationList.insertBefore(notificationElement, notificationList.firstChild);
        } else {
          notificationList.appendChild(notificationElement);
        }
        
        // Animate in
        setTimeout(() => {
          notificationElement.style.opacity = '1';
        }, 10);
        
        // Remove empty state if present
        const emptyState = notificationList.querySelector('.notification-empty-state');
        if (emptyState) {
          emptyState.remove();
        }
      }
    });
    
    // Listen for read status changes
    notificationService.onNotification('notification_read', (data) => {
      const { notification_id } = data;
      const notificationItem = notificationList.querySelector(`.notification-item[data-id="${notification_id}"]`);
      
      if (notificationItem) {
        // Update UI
        notificationItem.classList.add('read');
        notificationItem.classList.remove('unread');
        
        // Remove mark as read button
        const readBtn = notificationItem.querySelector('.mark-read-btn');
        if (readBtn) {
          readBtn.remove();
        }
      }
    });
    
    // Listen for notification deletions
    notificationService.onNotification('notification_deleted', (data) => {
      const { notification_id } = data;
      const notificationItem = notificationList.querySelector(`.notification-item[data-id="${notification_id}"]`);
      
      if (notificationItem) {
        // Remove with animation
        notificationItem.style.opacity = '0';
        setTimeout(() => {
          notificationItem.remove();
          
          // Check if list is empty
          if (notificationList.children.length === 0) {
            resetAndReload();
          }
        }, 300);
      }
    });
  }
  
  /**
   * Check if a notification matches current filters
   * @param {Object} notification - Notification to check
   * @returns {boolean} - Whether notification should be shown
   */
  function shouldShowNotification(notification) {
    // Check type filter
    if (currentFilters.type !== 'all' && notification.type !== currentFilters.type) {
      return false;
    }
    
    // Check read filter
    if (currentFilters.read === 'read' && !notification.is_read) {
      return false;
    }
    
    if (currentFilters.read === 'unread' && notification.is_read) {
      return false;
    }
    
    return true;
  }
}