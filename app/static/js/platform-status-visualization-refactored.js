/**
 * Platform Status Visualization
 * Handles real-time monitoring and visualization of platform connection status.
 * Refactored to use the service layer.
 */

import { platformService } from './services/index.js';

class PlatformStatusMonitor {
    constructor(options) {
        this.options = Object.assign({
            refreshInterval: 60000, // 1 minute refresh by default
            showNotifications: true,
            autoRefresh: true
        }, options);
        
        this.platformData = {};
        this.charts = {};
        this.statusIndicators = {};
        this.navbarIndicator = null;
        
        // Elements
        this.elements = {
            globalStatus: document.getElementById('global-platform-status'),
            detailsContainer: document.getElementById('platform-status-details'),
            platformList: document.getElementById('platform-status-list'),
            charts: document.getElementById('platform-status-charts'),
            refreshButton: document.getElementById('refresh-platform-status')
        };
        
        // Colors for status visualization
        this.colors = {
            connected: '#10b981',  // Green
            disconnected: '#ef4444', // Red
            warning: '#f59e0b',    // Amber
            excellent: '#10b981',  // Green
            good: '#34d399',       // Light green
            fair: '#f59e0b',       // Amber
            poor: '#f87171',       // Light red
            critical: '#ef4444'    // Red
        };
        
        this.initialize();
    }
    
    /**
     * Initialize the platform status monitor
     */
    initialize() {
        this.fetchStatusData();
        this.initializeEventListeners();
        
        if (this.options.autoRefresh) {
            this.startAutoRefresh();
        }
        
        // Initialize navbar indicator if present
        if (document.getElementById('navbar-platform-status')) {
            this.navbarIndicator = document.getElementById('navbar-platform-status');
        }
    }
    
    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        if (this.elements.refreshButton) {
            this.elements.refreshButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.fetchStatusData();
            });
        }
        
        // Global event listener for test buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.test-platform-btn')) {
                const btn = e.target.closest('.test-platform-btn');
                const platform = btn.dataset.platform;
                this.testPlatformConnection(platform, btn);
            }
        });
    }
    
    /**
     * Start auto-refresh of platform status
     */
    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.fetchStatusData(true); // Quiet update (no spinners)
        }, this.options.refreshInterval);
    }
    
    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
    
    /**
     * Fetch platform status data from the API using service layer
     * @param {boolean} quiet - If true, don't show loading indicators
     */
    async fetchStatusData(quiet = false) {
        if (!quiet && this.elements.refreshButton) {
            this.elements.refreshButton.innerHTML = '<i class="fas fa-spin fa-spinner"></i>';
            this.elements.refreshButton.disabled = true;
        }
        
        try {
            // Use platform service to get status
            const data = await platformService.getPlatformStatus();
            
            if (data.success) {
                this.platformData = data.platforms;
                
                this.updateStatusIndicators();
                this.updateDetailViews();
                this.updateGlobalStatus();
                this.updateNavbarIndicator();
                
                if (this.elements.charts) {
                    this.renderCharts();
                }
                
                // Show notification if status changed and notifications are enabled
                if (this.options.showNotifications && !quiet) {
                    this.checkForStatusChanges();
                }
            } else {
                throw new Error(data.message || 'Failed to fetch platform status');
            }
        } catch (error) {
            console.error('Error fetching platform status:', error);
            
            if (this.options.showNotifications) {
                showToast('Error', 'Failed to fetch platform status data', 'error');
            }
        } finally {
            if (!quiet && this.elements.refreshButton) {
                this.elements.refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i>';
                this.elements.refreshButton.disabled = false;
            }
        }
    }
    
    /**
     * Update status indicators for each platform
     */
    updateStatusIndicators() {
        // Clear existing indicators if any
        if (this.elements.platformList) {
            // Update existing indicators or create new ones
            this.elements.platformList.innerHTML = '';
            
            Object.keys(this.platformData).forEach(platform => {
                const status = this.platformData[platform];
                
                // Create list item
                const li = document.createElement('li');
                li.className = 'platform-item';
                
                // Create content
                li.innerHTML = `
                    <div class="platform-icon">
                        <i class="${status.icon}"></i>
                    </div>
                    <div class="platform-info">
                        <div class="platform-name">${status.display_name}</div>
                        <div class="platform-status">
                            <span class="status-indicator ${status.is_connected ? 'connected' : 'disconnected'}"></span>
                            ${status.is_connected ? 'Connected' : 'Disconnected'}
                        </div>
                        <div class="platform-health">
                            <i class="${this.getHealthIcon(status.health_status)}"></i>
                            <span class="health-label">${status.health_status.charAt(0).toUpperCase() + status.health_status.slice(1)}</span>
                        </div>
                    </div>
                    <div class="platform-actions">
                        <button class="btn btn-sm btn-outline-primary test-platform-btn" data-platform="${platform}">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                `;
                
                this.elements.platformList.appendChild(li);
            });
        }
    }
    
    // Other UI methods remain the same (updateDetailViews, updateGlobalStatus, etc.)
    // ...
    
    /**
     * Test connection to a specific platform using service layer
     * @param {string} platform - Platform identifier (meta, google, twitter, etc.)
     * @param {HTMLElement} button - Button element that triggered the test
     */
    async testPlatformConnection(platform, button) {
        // Show spinner
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        button.disabled = true;
        
        // Find closest platform item if in list view
        const platformItem = button.closest('.platform-item');
        const statusIndicator = platformItem ? platformItem.querySelector('.status-indicator') : null;
        const statusText = platformItem ? platformItem.querySelector('.platform-status') : null;
        
        try {
            // Use platform service to test connection
            const data = await platformService.testConnection(platform);
            
            // Update platform data with new info
            if (this.platformData[platform]) {
                this.platformData[platform] = { 
                    ...this.platformData[platform], 
                    ...data 
                };
            }
            
            // Update status indicator if found
            if (statusIndicator && statusText) {
                if (data.success) {
                    statusIndicator.className = 'status-indicator connected';
                    statusText.innerHTML = '<span class="status-indicator connected"></span>Connected';
                } else {
                    statusIndicator.className = 'status-indicator disconnected';
                    statusText.innerHTML = '<span class="status-indicator disconnected"></span>Disconnected';
                }
            }
            
            // Refresh all views to ensure consistency
            this.updateDetailViews();
            this.updateGlobalStatus();
            this.updateNavbarIndicator();
            
            if (this.elements.charts) {
                this.renderCharts();
            }
            
            // Show toast
            if (this.options.showNotifications) {
                if (data.success) {
                    showToast(
                        'Connection Successful', 
                        `Successfully connected to ${platform.toUpperCase()} API (${data.response_time_ms}ms)`, 
                        'success'
                    );
                } else {
                    showToast(
                        'Connection Failed', 
                        data.message || `Failed to connect to ${platform.toUpperCase()} API`, 
                        'error'
                    );
                }
            }
        } catch (error) {
            console.error(`Error testing ${platform} connection:`, error);
            
            if (this.options.showNotifications) {
                showToast('Error', `Failed to test ${platform.toUpperCase()} connection`, 'error');
            }
        } finally {
            // Restore button
            button.innerHTML = originalHTML;
            button.disabled = false;
        }
    }
    
    // Remaining helper methods...
    /**
     * Get the appropriate Font Awesome icon for health status
     * @param {string} health - Health status (excellent, good, fair, poor, critical)
     * @returns {string} Font Awesome icon class
     */
    getHealthIcon(health) {
        switch (health) {
            case 'excellent':
                return 'fas fa-circle-check text-success';
            case 'good':
                return 'fas fa-circle-check text-success';
            case 'fair':
                return 'fas fa-triangle-exclamation text-warning';
            case 'poor':
                return 'fas fa-circle-exclamation text-danger';
            case 'critical':
                return 'fas fa-circle-xmark text-danger';
            default:
                return 'fas fa-question-circle text-secondary';
        }
    }
    
    /**
     * Get the appropriate Bootstrap color for health status
     * @param {string} health - Health status
     * @returns {string} Bootstrap color name
     */
    getHealthColor(health) {
        switch (health) {
            case 'excellent':
                return 'success';
            case 'good':
                return 'success';
            case 'fair':
                return 'warning';
            case 'poor':
                return 'danger';
            case 'critical':
                return 'danger';
            default:
                return 'secondary';
        }
    }
    
    /**
     * Get the appropriate Bootstrap badge class for health status
     * @param {string} health - Health status
     * @returns {string} Bootstrap badge class
     */
    getHealthBadgeClass(health) {
        switch (health) {
            case 'excellent':
                return 'bg-success';
            case 'good':
                return 'bg-success';
            case 'fair':
                return 'bg-warning';
            case 'poor':
                return 'bg-danger';
            case 'critical':
                return 'bg-danger';
            default:
                return 'bg-secondary';
        }
    }
}

// Initialize platform status monitor when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a page that needs platform status monitoring
    const platformStatusElement = document.getElementById('platform-status-container');
    
    if (platformStatusElement || document.getElementById('navbar-platform-status')) {
        window.platformStatusMonitor = new PlatformStatusMonitor({
            refreshInterval: 60000, // 1 minute
            showNotifications: true
        });
    }
});