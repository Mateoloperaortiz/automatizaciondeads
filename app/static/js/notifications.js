/**
 * MagnetoCursor - Real-time Notification System
 * Handles fetching, displaying, and managing notifications
 */

class NotificationManager {
    constructor(options = {}) {
        // Default options
        this.options = {
            apiEndpoint: '/notifications/api/list',
            countEndpoint: '/notifications/api/counts',
            markReadEndpoint: '/notifications/api/mark-read',
            markAllReadEndpoint: '/notifications/api/mark-all-read',
            autoRefreshInterval: 60000, // 1 minute
            maxNotifications: 5,
            enableRealtime: true,
            enableDesktopNotifications: true,
            ...options
        };
        
        // Element references
        this.notificationCounter = document.querySelector('.notification-counter');
        this.unreadCount = document.querySelector('.notification-header .unread-count');
        this.notificationList = document.querySelector('.notification-list');
        this.notificationLoading = document.querySelector('.notification-loading');
        this.notificationEmpty = document.querySelector('.notification-empty');
        this.markAllReadBtn = document.querySelector('.mark-all-read');
        
        // State
        this.lastFetchTime = null;
        this.refreshIntervalId = null;
        this.notifications = [];
        this.desktopNotificationsEnabled = false;
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize the notification manager
     */
    init() {
        // Request desktop notification permission if enabled
        if (this.options.enableDesktopNotifications && 'Notification' in window) {
            this.requestNotificationPermission();
        }
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initial fetch
        this.fetchNotifications();
        
        // Set up auto-refresh
        if (this.options.autoRefreshInterval > 0) {
            this.startAutoRefresh();
        }
        
        // Set up WebSocket connection for real-time updates if enabled
        if (this.options.enableRealtime && 'WebSocket' in window) {
            this.connectWebSocket();
        }
    }
    
    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Mark all as read button
        if (this.markAllReadBtn) {
            this.markAllReadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.markAllAsRead();
            });
        }
        
        // Close dropdown when clicking "mark as read"
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('mark-notification-read')) {
                e.preventDefault();
                const notificationId = e.target.dataset.id;
                this.markAsRead(notificationId);
            }
        });
    }
    
    /**
     * Start auto-refresh interval
     */
    startAutoRefresh() {
        this.refreshIntervalId = setInterval(() => {
            this.fetchUnreadCount();
        }, this.options.autoRefreshInterval);
    }
    
    /**
     * Stop auto-refresh interval
     */
    stopAutoRefresh() {
        if (this.refreshIntervalId) {
            clearInterval(this.refreshIntervalId);
            this.refreshIntervalId = null;
        }
    }
    
    /**
     * Request permission for desktop notifications
     */
    requestNotificationPermission() {
        if (Notification.permission === 'granted') {
            this.desktopNotificationsEnabled = true;
        } else if (Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                this.desktopNotificationsEnabled = permission === 'granted';
            });
        }
    }
    
    /**
     * Connect to WebSocket for real-time notifications
     */
    connectWebSocket() {
        // This is a placeholder - actual implementation would depend on your backend
        // For example, you might use Socket.IO or a native WebSocket connection
        
        // Example using native WebSocket:
        // const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // const wsUrl = `${wsProtocol}//${window.location.host}/ws/notifications`;
        // this.socket = new WebSocket(wsUrl);
        
        // this.socket.onmessage = (event) => {
        //     const data = JSON.parse(event.data);
        //     if (data.type === 'notification') {
        //         this.handleNewNotification(data.notification);
        //     }
        // };
        
        // this.socket.onclose = () => {
        //     // Reconnect after delay
        //     setTimeout(() => this.connectWebSocket(), 5000);
        // };
    }
    
    /**
     * Handle a new notification received via WebSocket
     * @param {Object} notification - The notification data
     */
    handleNewNotification(notification) {
        // Add to local cache
        this.notifications.unshift(notification);
        if (this.notifications.length > this.options.maxNotifications) {
            this.notifications.pop();
        }
        
        // Update UI
        this.updateNotificationUI();
        
        // Show desktop notification if enabled
        this.showDesktopNotification(notification);
        
        // Show toast notification
        this.showToastNotification(notification);
    }
    
    /**
     * Show desktop notification
     * @param {Object} notification - The notification data
     */
    showDesktopNotification(notification) {
        if (!this.desktopNotificationsEnabled) return;
        
        const title = `MagnetoCursor: ${notification.title}`;
        const options = {
            body: notification.message,
            icon: '/static/images/logo-icon.png',
            tag: `magneto-notification-${notification.id}`
        };
        
        const desktopNotification = new Notification(title, options);
        
        desktopNotification.onclick = () => {
            window.focus();
            if (notification.related_entity_type && notification.related_entity_id) {
                // Navigate to related entity if applicable
                // This is a placeholder - customize based on your app's routing
                // window.location.href = `/${notification.related_entity_type}/${notification.related_entity_id}`;
            } else {
                window.location.href = '/notifications';
            }
        };
    }
    
    /**
     * Show toast notification
     * @param {Object} notification - The notification data
     */
    showToastNotification(notification) {
        // Use the existing toast notification system
        if (typeof showToast === 'function') {
            showToast(notification.message, notification.type, 5000);
        }
    }
    
    /**
     * Fetch notifications from the API
     */
    fetchNotifications() {
        if (!this.notificationList) return;
        
        this.showLoading(true);
        
        fetch(this.options.apiEndpoint + `?limit=${this.options.maxNotifications}&unread_only=true`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.notifications = data.data;
                    this.updateNotificationUI();
                    this.updateUnreadCount(data.unread_count);
                    this.lastFetchTime = new Date();
                }
            })
            .catch(error => {
                console.error('Error fetching notifications:', error);
                this.showEmpty(true);
            })
            .finally(() => {
                this.showLoading(false);
            });
    }
    
    /**
     * Fetch only the unread count (more efficient for regular polling)
     */
    fetchUnreadCount() {
        fetch(this.options.countEndpoint)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.updateUnreadCount(data.unread_total);
                    
                    // If there are new notifications, fetch the full list
                    if (data.unread_total > 0 && 
                        (!this.notifications.length || 
                         data.unread_total > this.notifications.filter(n => !n.is_read).length)) {
                        this.fetchNotifications();
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching notification count:', error);
            });
    }
    
    /**
     * Mark a notification as read
     * @param {number} id - Notification ID
     */
    markAsRead(id) {
        fetch(`${this.options.markReadEndpoint}/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update local state
                    const index = this.notifications.findIndex(n => n.id === parseInt(id));
                    if (index !== -1) {
                        this.notifications[index].is_read = true;
                        this.updateNotificationUI();
                    }
                    
                    // Update unread count
                    this.updateUnreadCount(data.unread_count);
                }
            })
            .catch(error => {
                console.error('Error marking notification as read:', error);
            });
    }
    
    /**
     * Mark all notifications as read
     */
    markAllAsRead() {
        fetch(this.options.markAllReadEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update local state
                    this.notifications.forEach(notification => {
                        notification.is_read = true;
                    });
                    
                    // Update UI
                    this.updateNotificationUI();
                    this.updateUnreadCount(0);
                }
            })
            .catch(error => {
                console.error('Error marking all notifications as read:', error);
            });
    }
    
    /**
     * Update the notification counter and header
     * @param {number} count - Unread notification count
     */
    updateUnreadCount(count) {
        // Update counter badge
        if (this.notificationCounter) {
            this.notificationCounter.textContent = count;
            this.notificationCounter.style.display = count > 0 ? 'block' : 'none';
        }
        
        // Update header text
        if (this.unreadCount) {
            this.unreadCount.textContent = count;
        }
    }
    
    /**
     * Update the notification list UI
     */
    updateNotificationUI() {
        if (!this.notificationList) return;
        
        // Clear existing items
        const existingItems = this.notificationList.querySelectorAll('.notification-item');
        existingItems.forEach(item => item.remove());
        
        // Check if we have notifications to show
        if (this.notifications.length === 0) {
            this.showEmpty(true);
            return;
        } else {
            this.showEmpty(false);
        }
        
        // Create HTML for each notification
        for (const notification of this.notifications) {
            const item = document.createElement('a');
            item.href = '#';
            item.className = `list-group-item notification-item ${notification.is_read ? 'read' : 'unread'}`;
            
            // Set icon based on notification type
            let icon = 'info';
            if (notification.type === 'success') icon = 'check-circle';
            if (notification.type === 'warning') icon = 'alert-triangle';
            if (notification.type === 'error') icon = 'alert-octagon';
            
            item.innerHTML = `
                <div class="row g-0 align-items-center">
                    <div class="col-2 text-center">
                        <i data-feather="${notification.icon || icon}" class="notification-icon ${notification.type}"></i>
                    </div>
                    <div class="col-10">
                        <div class="text-dark">${notification.title}</div>
                        <div class="text-muted small mt-1">${notification.message}</div>
                        <div class="text-muted small mt-1 d-flex justify-content-between">
                            <div>${notification.formatted_time}</div>
                            ${!notification.is_read ? `
                            <a href="#" class="mark-notification-read" data-id="${notification.id}">
                                Mark as read
                            </a>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
            
            // Add to list before the loading and empty elements
            this.notificationList.insertBefore(item, this.notificationLoading);
        }
        
        // Re-initialize feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    /**
     * Show or hide the loading indicator
     * @param {boolean} show - Whether to show or hide
     */
    showLoading(show) {
        if (this.notificationLoading) {
            this.notificationLoading.style.display = show ? 'block' : 'none';
        }
    }
    
    /**
     * Show or hide the empty state
     * @param {boolean} show - Whether to show or hide
     */
    showEmpty(show) {
        if (this.notificationEmpty) {
            this.notificationEmpty.classList.toggle('d-none', !show);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize NotificationManager
    window.notificationManager = new NotificationManager();
});