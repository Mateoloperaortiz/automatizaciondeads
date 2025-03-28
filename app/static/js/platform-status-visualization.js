/**
 * Platform Status Visualization
 * Handles real-time monitoring and visualization of platform connection status.
 */

class PlatformStatusMonitor {
    constructor(options) {
        this.options = Object.assign({
            statusEndpoint: '/api/platform-status',
            testEndpoint: '/api/test/connection',
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
     * Fetch platform status data from the API
     * @param {boolean} quiet - If true, don't show loading indicators
     */
    async fetchStatusData(quiet = false) {
        if (!quiet && this.elements.refreshButton) {
            this.elements.refreshButton.innerHTML = '<i class="fas fa-spin fa-spinner"></i>';
            this.elements.refreshButton.disabled = true;
        }
        
        try {
            const response = await fetch(this.options.statusEndpoint);
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
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
        } catch (error) {
            console.error('Error fetching platform status:', error);
            
            if (this.options.showNotifications) {
                this.showToast('Error', 'Failed to fetch platform status data', 'error');
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
    
    /**
     * Update detailed views for each platform
     */
    updateDetailViews() {
        if (!this.elements.detailsContainer) return;
        
        // Create detail cards for each platform
        this.elements.detailsContainer.innerHTML = '';
        
        Object.keys(this.platformData).forEach(platform => {
            const status = this.platformData[platform];
            
            // Create card
            const card = document.createElement('div');
            card.className = 'col-md-6 col-xl-4 mb-4';
            
            // Format times for display
            const lastChecked = status.last_checked ? new Date(status.last_checked).toLocaleString() : 'Never';
            const lastSuccess = status.last_successful_connection ? new Date(status.last_successful_connection).toLocaleString() : 'Never';
            
            card.innerHTML = `
                <div class="card platform-status-card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="card-title mb-0">
                            <i class="${status.icon}"></i> ${status.display_name}
                        </h5>
                        <span class="badge ${status.is_connected ? 'bg-success' : 'bg-danger'}">
                            ${status.is_connected ? 'Connected' : 'Disconnected'}
                        </span>
                    </div>
                    <div class="card-body">
                        <div class="health-score mb-3">
                            <label>Health Score</label>
                            <div class="progress">
                                <div class="progress-bar bg-${this.getHealthColor(status.health_status)}" 
                                     role="progressbar" style="width: ${status.performance_score}%" 
                                     aria-valuenow="${status.performance_score}" aria-valuemin="0" aria-valuemax="100">
                                     ${status.performance_score}%
                                </div>
                            </div>
                            <small class="text-muted">${status.health_status.charAt(0).toUpperCase() + status.health_status.slice(1)}</small>
                        </div>
                        <div class="platform-status-details">
                            <div class="row mb-1">
                                <div class="col-5">Response Time:</div>
                                <div class="col-7 text-end">${status.response_time_ms ? status.response_time_ms + 'ms' : 'N/A'}</div>
                            </div>
                            <div class="row mb-1">
                                <div class="col-5">Last Checked:</div>
                                <div class="col-7 text-end">${lastChecked}</div>
                            </div>
                            <div class="row mb-1">
                                <div class="col-5">Last Success:</div>
                                <div class="col-7 text-end">${lastSuccess}</div>
                            </div>
                            <div class="row mb-1">
                                <div class="col-5">API Version:</div>
                                <div class="col-7 text-end">${status.api_version || 'Unknown'}</div>
                            </div>
                            <div class="row mb-1">
                                <div class="col-5">Status:</div>
                                <div class="col-7 text-end">${status.status_message || 'No message'}</div>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-sm btn-primary test-platform-btn" data-platform="${platform}">
                            Test Connection
                        </button>
                        <a href="/api/logs?platform=${platform}" class="btn btn-sm btn-outline-secondary">
                            View Logs
                        </a>
                    </div>
                </div>
            `;
            
            this.elements.detailsContainer.appendChild(card);
        });
    }
    
    /**
     * Update global status indicator
     */
    updateGlobalStatus() {
        if (!this.elements.globalStatus) return;
        
        // Calculate overall status
        const platforms = Object.values(this.platformData);
        const totalPlatforms = platforms.length;
        const connectedPlatforms = platforms.filter(p => p.is_connected).length;
        
        let statusClass = 'bg-success';
        let statusText = 'All Systems Operational';
        let statusIcon = 'check-circle';
        
        if (connectedPlatforms === 0) {
            statusClass = 'bg-danger';
            statusText = 'All Systems Down';
            statusIcon = 'times-circle';
        } else if (connectedPlatforms < totalPlatforms) {
            statusClass = 'bg-warning';
            statusText = `${connectedPlatforms}/${totalPlatforms} Systems Operational`;
            statusIcon = 'exclamation-triangle';
        }
        
        // Update the global status display
        this.elements.globalStatus.innerHTML = `
            <div class="alert ${statusClass} mb-4">
                <div class="d-flex align-items-center">
                    <i class="fas fa-${statusIcon} fa-2x me-3"></i>
                    <div>
                        <h4 class="alert-heading mb-1">${statusText}</h4>
                        <div class="text-small">Last updated: ${new Date().toLocaleString()}</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Update navbar indicator if it exists
     */
    updateNavbarIndicator() {
        if (!this.navbarIndicator) return;
        
        // Calculate overall status
        const platforms = Object.values(this.platformData);
        const totalPlatforms = platforms.length;
        const connectedPlatforms = platforms.filter(p => p.is_connected).length;
        
        let statusClass = 'bg-success';
        let statusIcon = 'check-circle';
        
        if (connectedPlatforms === 0) {
            statusClass = 'bg-danger';
            statusIcon = 'times-circle';
        } else if (connectedPlatforms < totalPlatforms) {
            statusClass = 'bg-warning';
            statusIcon = 'exclamation-triangle';
        }
        
        this.navbarIndicator.className = `nav-link position-relative`;
        this.navbarIndicator.innerHTML = `
            <i class="fas fa-plug"></i>
            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill ${statusClass}">
                ${connectedPlatforms}/${totalPlatforms}
            </span>
        `;
    }
    
    /**
     * Render charts for platform performance
     */
    renderCharts() {
        if (!this.elements.charts) return;
        
        // Clear charts container
        this.elements.charts.innerHTML = '';
        
        // Create row for charts
        const row = document.createElement('div');
        row.className = 'row';
        this.elements.charts.appendChild(row);
        
        // Create charts column
        const chartsCol = document.createElement('div');
        chartsCol.className = 'col-lg-8';
        row.appendChild(chartsCol);
        
        // Create metrics column
        const metricsCol = document.createElement('div');
        metricsCol.className = 'col-lg-4';
        row.appendChild(metricsCol);
        
        // Create canvas for response time chart
        const responseTimeCanvas = document.createElement('canvas');
        responseTimeCanvas.id = 'response-time-chart';
        responseTimeCanvas.height = 300;
        chartsCol.appendChild(responseTimeCanvas);
        
        // Create health metrics
        metricsCol.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5 class="card-title">Health Metrics</h5>
                </div>
                <div class="card-body">
                    <div class="platform-health-metrics">
                        ${Object.keys(this.platformData).map(platform => {
                            const status = this.platformData[platform];
                            return `
                                <div class="platform-health-metric mb-3">
                                    <div class="d-flex justify-content-between mb-1">
                                        <span><i class="${status.icon}"></i> ${status.display_name}</span>
                                        <span class="badge ${this.getHealthBadgeClass(status.health_status)}">
                                            ${status.health_status.charAt(0).toUpperCase() + status.health_status.slice(1)}
                                        </span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar bg-${this.getHealthColor(status.health_status)}" 
                                             role="progressbar" style="width: ${status.performance_score}%" 
                                             aria-valuenow="${status.performance_score}" aria-valuemin="0" aria-valuemax="100">
                                        </div>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
        
        // Initialize Chart.js if available
        if (window.Chart) {
            this.initializeResponseTimeChart(responseTimeCanvas);
        }
    }
    
    /**
     * Initialize response time chart with Chart.js
     * @param {HTMLCanvasElement} canvas - The canvas element for the chart
     */
    initializeResponseTimeChart(canvas) {
        const ctx = canvas.getContext('2d');
        
        // Prepare data
        const platforms = Object.keys(this.platformData);
        const labels = platforms.map(p => this.platformData[p].display_name);
        const data = platforms.map(p => this.platformData[p].response_time_ms || 0);
        const colors = platforms.map(p => {
            const status = this.platformData[p];
            return status.is_connected ? this.colors[status.health_status] : this.colors.disconnected;
        });
        
        // Create chart
        this.charts.responseTime = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Response Time (ms)',
                    data: data,
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'API Response Times'
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: (context) => {
                                const platform = platforms[context.dataIndex];
                                const status = this.platformData[platform];
                                return [
                                    `Status: ${status.is_connected ? 'Connected' : 'Disconnected'}`,
                                    `Health: ${status.health_status}`,
                                    `Score: ${status.performance_score}/100`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Test connection to a specific platform
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
            // Send request to test connection
            const response = await fetch(this.options.testEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ platform })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
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
                    this.showToast(
                        'Connection Successful', 
                        `Successfully connected to ${platform.toUpperCase()} API (${data.response_time_ms}ms)`, 
                        'success'
                    );
                } else {
                    this.showToast(
                        'Connection Failed', 
                        data.message || `Failed to connect to ${platform.toUpperCase()} API`, 
                        'error'
                    );
                }
            }
        } catch (error) {
            console.error(`Error testing ${platform} connection:`, error);
            
            if (this.options.showNotifications) {
                this.showToast('Error', `Failed to test ${platform.toUpperCase()} connection`, 'error');
            }
        } finally {
            // Restore button
            button.innerHTML = originalHTML;
            button.disabled = false;
        }
    }
    
    /**
     * Check for platform status changes and show notifications
     */
    checkForStatusChanges() {
        // This would compare current status with previous status
        // For now, we'll skip implementation as we don't store previous state
    }
    
    /**
     * Show a toast notification
     * @param {string} title - Toast title
     * @param {string} message - Toast message
     * @param {string} type - Toast type (success, error, warning, info)
     */
    showToast(title, message, type) {
        // Check if we have a toast container
        let toastContainer = document.querySelector('.toast-container');
        
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create a bootstrap toast
        const toastId = `toast-${Date.now()}`;
        const toastEl = document.createElement('div');
        
        toastEl.className = `toast align-items-center border-0`;
        toastEl.id = toastId;
        
        // Set toast background color based on type
        switch (type) {
            case 'success':
                toastEl.className += ' text-white bg-success';
                break;
            case 'error':
                toastEl.className += ' text-white bg-danger';
                break;
            case 'warning':
                toastEl.className += ' text-dark bg-warning';
                break;
            default:
                toastEl.className += ' text-white bg-primary';
        }
        
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        // Toast content
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong>: ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add toast to container
        toastContainer.appendChild(toastEl);
        
        // Initialize and show the toast if Bootstrap is available
        if (window.bootstrap && window.bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastEl);
            toast.show();
        }
    }
    
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
            statusEndpoint: '/api/platform-status',
            testEndpoint: '/api/test/connection',
            refreshInterval: 60000, // 1 minute
            showNotifications: true
        });
    }
});