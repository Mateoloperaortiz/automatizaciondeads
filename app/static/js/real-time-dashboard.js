/**
 * Real-Time Dashboard Implementation
 * Demonstrates full integration of service layer architecture
 * - Phase 1: API config, base services and error handling
 * - Phase 2: Feature-specific services with data validation
 * - Phase 3: Real-time capabilities with WebSocket and event-driven architecture
 */

import { realTimeDashboard, DASHBOARD_EVENTS } from './services/real-time-dashboard.js';
import { websocketService } from './services/websocket-service.js';
import { realTimeApiClient, WATCHED_ENTITIES } from './services/real-time-api.js';
import eventHub from './services/event-hub.js';
import { toastService } from './services/toast-service.js';

// Charts instances
let campaignPerformanceChart = null;
let audienceDistributionChart = null;

/**
 * Initialize the real-time dashboard
 */
function initializeRealTimeDashboard() {
  // Initialize chart.js charts
  initializeCharts();
  
  // Set up event listeners for real-time updates
  setupEventListeners();
  
  // Subscribe to specific entities for real-time updates
  setupEntitySubscriptions();
  
  // Set up connection status indicator
  setupConnectionStatus();
  
  // Add refresh button functionality
  setupRefreshButtons();
  
  console.log('Real-time dashboard UI initialized');
}

/**
 * Initialize dashboard charts
 */
function initializeCharts() {
  const ctxPerformance = document.getElementById('campaignPerformanceChart');
  const ctxDistribution = document.getElementById('audienceDistributionChart');
  
  if (ctxPerformance) {
    campaignPerformanceChart = new Chart(ctxPerformance, {
      type: 'bar',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Impressions',
            data: [],
            backgroundColor: 'rgba(99, 102, 241, 0.6)',
            borderColor: 'rgba(99, 102, 241, 1)',
            borderWidth: 1
          },
          {
            label: 'Clicks',
            data: [],
            backgroundColor: 'rgba(14, 165, 233, 0.6)',
            borderColor: 'rgba(14, 165, 233, 1)',
            borderWidth: 1
          },
          {
            label: 'Applications',
            data: [],
            backgroundColor: 'rgba(16, 185, 129, 0.6)',
            borderColor: 'rgba(16, 185, 129, 1)',
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              usePointStyle: true,
              boxWidth: 6
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              drawBorder: false
            }
          },
          x: {
            grid: {
              display: false,
              drawBorder: false
            }
          }
        }
      }
    });
  }
  
  if (ctxDistribution) {
    audienceDistributionChart = new Chart(ctxDistribution, {
      type: 'doughnut',
      data: {
        labels: ['Recent Graduates', 'Mid-Career', 'Executives', 'Career Changers', 'Remote Workers'],
        datasets: [{
          data: [30, 25, 15, 20, 10],
          backgroundColor: [
            'rgba(99, 102, 241, 0.8)',
            'rgba(14, 165, 233, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 15,
              boxWidth: 8
            }
          }
        },
        cutout: '65%'
      }
    });
  }
}

/**
 * Set up event listeners for dashboard updates
 */
function setupEventListeners() {
  // Listen for metrics updates
  eventHub.on(DASHBOARD_EVENTS.METRICS_UPDATED, updateMetricsUI);
  
  // Listen for campaign updates
  eventHub.on(DASHBOARD_EVENTS.CAMPAIGN_UPDATED, updateCampaignsTable);
  
  // Listen for job updates
  eventHub.on(DASHBOARD_EVENTS.JOB_UPDATED, updateJobsTable);
  
  // Listen for chart data updates
  eventHub.on(DASHBOARD_EVENTS.CHART_DATA_UPDATED, updateCharts);
  
  // Listen for conversion metrics updates
  eventHub.on(DASHBOARD_EVENTS.CONVERSION_UPDATED, updateConversionMetrics);
  
  // WebSocket connection status events
  websocketService.on('open', () => {
    updateConnectionStatus(true);
    toastService.show('Real-time connection established', 'success');
  });
  
  websocketService.on('close', () => {
    updateConnectionStatus(false);
  });
  
  websocketService.on('reconnecting', () => {
    updateConnectionStatus(false, true);
    toastService.show('Reconnecting to real-time services...', 'warning');
  });
}

/**
 * Set up entity subscriptions for real-time updates
 */
function setupEntitySubscriptions() {
  // Subscribe to analytics updates for real-time metrics
  realTimeApiClient.subscribeToEntity(WATCHED_ENTITIES.ANALYTICS, 'dashboard');
  
  // Subscribe to platform status updates
  realTimeApiClient.subscribeToEntity(WATCHED_ENTITIES.PLATFORM_STATUS, 'all');
  
  // No need to subscribe to specific campaigns or jobs as we'll get updates
  // through the RealTimeDashboard service which already handles those
}

/**
 * Update metrics UI with new data
 * @param {Object} metrics - Updated metrics data
 */
function updateMetricsUI(metrics) {
  // Update job count
  const jobCountElement = document.querySelector('.metric-card:nth-child(1) .value');
  if (jobCountElement) {
    jobCountElement.textContent = metrics.jobCount;
  }
  
  // Update campaign count
  const campaignCountElement = document.querySelector('.metric-card:nth-child(2) .value');
  if (campaignCountElement) {
    campaignCountElement.textContent = metrics.campaignCount;
  }
  
  // Update candidate count
  const candidateCountElement = document.querySelector('.metric-card:nth-child(3) .value');
  if (candidateCountElement) {
    candidateCountElement.textContent = metrics.candidateCount;
  }
  
  // Update segment count
  const segmentCountElement = document.querySelector('.metric-card:nth-child(4) .value');
  if (segmentCountElement) {
    segmentCountElement.textContent = metrics.segmentCount;
  }
  
  // Add animation to show changes
  document.querySelectorAll('.metric-card').forEach(card => {
    card.classList.add('pulse-update');
    setTimeout(() => card.classList.remove('pulse-update'), 1000);
  });
}

/**
 * Update campaigns table with new data
 * @param {Array} campaigns - Updated campaign data
 */
function updateCampaignsTable(campaigns) {
  const tableBody = document.querySelector('.card:nth-of-type(3) tbody');
  if (!tableBody) return;
  
  // Clear existing rows
  tableBody.innerHTML = '';
  
  // Add new rows
  campaigns.forEach(campaign => {
    const row = document.createElement('tr');
    
    // Platform icon mapping
    const platformIcons = {
      1: '<i class="fab fa-facebook text-primary mr-2"></i> Meta',
      2: '<i class="fab fa-twitter text-info mr-2"></i> X',
      3: '<i class="fab fa-google text-danger mr-2"></i> Google',
      4: '<i class="fab fa-tiktok mr-2"></i> TikTok',
      5: '<i class="fab fa-snapchat text-warning mr-2"></i> Snapchat'
    };
    
    // Status badge mapping
    const statusBadges = {
      active: '<span class="status-badge active"><i class="fas fa-circle"></i> Active</span>',
      draft: '<span class="status-badge draft"><i class="fas fa-circle"></i> Draft</span>',
      completed: '<span class="status-badge inactive"><i class="fas fa-circle"></i> Completed</span>',
      paused: '<span class="status-badge pending"><i class="fas fa-circle"></i> Paused</span>'
    };
    
    // Format date
    const date = new Date(campaign.created_at);
    const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    
    // Create row HTML
    row.innerHTML = `
      <td>${campaign.title}</td>
      <td>${campaign.job_opening ? campaign.job_opening.title : 'Unknown'}</td>
      <td>
        <span class="d-flex align-items-center">
          ${platformIcons[campaign.platform_id] || 'Unknown'}
        </span>
      </td>
      <td>${statusBadges[campaign.status] || `<span class="status-badge pending"><i class="fas fa-circle"></i> ${campaign.status}</span>`}</td>
      <td>$${campaign.budget}</td>
      <td>${formattedDate}</td>
      <td>
        <div class="d-flex">
          <a href="/campaigns/${campaign.id}" class="btn btn-sm btn-light mr-1" data-bs-toggle="tooltip" data-bs-title="View Details">
            <i class="fas fa-eye"></i>
          </a>
          <a href="#" class="btn btn-sm btn-light" data-bs-toggle="tooltip" data-bs-title="Edit Campaign">
            <i class="fas fa-edit"></i>
          </a>
        </div>
      </td>
    `;
    
    // Add highlight animation
    row.classList.add('highlight-update');
    
    // Add to table
    tableBody.appendChild(row);
    
    // Remove highlight after animation completes
    setTimeout(() => row.classList.remove('highlight-update'), 2000);
  });
  
  // Reinitialize tooltips
  initializeTooltips();
}

/**
 * Update jobs table with new data
 * @param {Array} jobs - Updated job data
 */
function updateJobsTable(jobs) {
  const tableBody = document.querySelector('.card:nth-of-type(4) tbody');
  if (!tableBody) return;
  
  // Clear existing rows
  tableBody.innerHTML = '';
  
  // Add new rows
  jobs.forEach(job => {
    const row = document.createElement('tr');
    
    // Format date
    const date = new Date(job.created_at);
    const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    
    // Create row HTML
    row.innerHTML = `
      <td>${job.title}</td>
      <td><i class="fas fa-map-marker-alt text-muted mr-1"></i> ${job.location}</td>
      <td>${job.department}</td>
      <td>${formattedDate}</td>
      <td>
        <div class="d-flex">
          <a href="/jobs/${job.id}" class="btn btn-sm btn-light mr-1" data-bs-toggle="tooltip" data-bs-title="View Details">
            <i class="fas fa-eye"></i>
          </a>
          <a href="/campaigns/create?job_id=${job.id}" class="btn btn-sm btn-primary" data-bs-toggle="tooltip" data-bs-title="Create Campaign">
            <i class="fas fa-bullhorn"></i>
          </a>
        </div>
      </td>
    `;
    
    // Add highlight animation
    row.classList.add('highlight-update');
    
    // Add to table
    tableBody.appendChild(row);
    
    // Remove highlight after animation completes
    setTimeout(() => row.classList.remove('highlight-update'), 2000);
  });
  
  // Reinitialize tooltips
  initializeTooltips();
}

/**
 * Update charts with new data
 * @param {Object} chartData - Updated chart data
 */
function updateCharts(chartData) {
  // Update campaign performance chart
  if (campaignPerformanceChart) {
    campaignPerformanceChart.data.labels = chartData.platforms;
    campaignPerformanceChart.data.datasets[0].data = chartData.impressions;
    campaignPerformanceChart.data.datasets[1].data = chartData.clicks;
    campaignPerformanceChart.data.datasets[2].data = chartData.applications;
    campaignPerformanceChart.update();
    
    // Add animation to chart container
    const chartContainer = document.querySelector('.card:nth-of-type(1) .chart-container');
    if (chartContainer) {
      chartContainer.classList.add('pulse-update');
      setTimeout(() => chartContainer.classList.remove('pulse-update'), 1000);
    }
  }
}

/**
 * Update conversion metrics with new data
 * @param {Object} metrics - Updated conversion metrics
 */
function updateConversionMetrics(metrics) {
  // Update click-through rate
  const ctrElement = document.querySelector('.progress-labels:nth-of-type(1) .label:nth-child(2)');
  const ctrBar = document.querySelector('.progress:nth-of-type(1) .progress-bar');
  
  if (ctrElement && ctrBar) {
    const ctrPercent = (metrics.clickThroughRate * 100).toFixed(1);
    ctrElement.textContent = `${ctrPercent}%`;
    ctrBar.style.width = `${ctrPercent * 10}%`; // Scale for visualization
  }
  
  // Update application rate
  const appRateElement = document.querySelector('.progress-labels:nth-of-type(2) .label:nth-child(2)');
  const appRateBar = document.querySelector('.progress:nth-of-type(2) .progress-bar');
  
  if (appRateElement && appRateBar) {
    const appRatePercent = (metrics.applicationRate * 100).toFixed(1);
    appRateElement.textContent = `${appRatePercent}%`;
    appRateBar.style.width = `${appRatePercent * 10}%`; // Scale for visualization
  }
  
  // Update interview conversion
  const intConvElement = document.querySelector('.progress-labels:nth-of-type(3) .label:nth-child(2)');
  const intConvBar = document.querySelector('.progress:nth-of-type(3) .progress-bar');
  
  if (intConvElement && intConvBar) {
    const intConvPercent = (metrics.interviewConversion * 100).toFixed(1);
    intConvElement.textContent = `${intConvPercent}%`;
    intConvBar.style.width = `${intConvPercent}%`;
  }
  
  // Update cost per application
  const cpaElement = document.querySelector('.progress-labels:nth-of-type(4) .label:nth-child(2)');
  const cpaBar = document.querySelector('.progress:nth-of-type(4) .progress-bar');
  
  if (cpaElement && cpaBar) {
    cpaElement.textContent = `$${metrics.costPerApplication.toFixed(2)}`;
    
    // CPA is normalized to a percentage for display
    const normalizedCpa = Math.min(100, (metrics.costPerApplication / 50) * 100);
    cpaBar.style.width = `${normalizedCpa}%`;
  }
  
  // Add animation to container
  const metricsContainer = document.querySelector('.card:nth-of-type(2) .card-body');
  if (metricsContainer) {
    metricsContainer.classList.add('pulse-update');
    setTimeout(() => metricsContainer.classList.remove('pulse-update'), 1000);
  }
}

/**
 * Set up connection status indicator
 */
function setupConnectionStatus() {
  // Create status indicator
  const statusContainer = document.createElement('div');
  statusContainer.className = 'connection-status';
  statusContainer.innerHTML = `
    <div class="status-indicator offline">
      <i class="fas fa-wifi"></i>
    </div>
    <span class="status-text">Offline</span>
  `;
  
  // Add to page
  const headerActions = document.querySelector('.page-title-actions');
  if (headerActions) {
    headerActions.prepend(statusContainer);
  } else {
    // Fallback if page-title-actions doesn't exist
    const pageTitle = document.querySelector('.page-title');
    if (pageTitle) {
      pageTitle.parentNode.insertBefore(statusContainer, pageTitle.nextSibling);
    }
  }
  
  // Initial status update
  updateConnectionStatus(websocketService.isConnected());
}

/**
 * Update connection status indicator
 * @param {boolean} isConnected - Whether connection is active
 * @param {boolean} isReconnecting - Whether reconnection is in progress
 */
function updateConnectionStatus(isConnected, isReconnecting = false) {
  const indicator = document.querySelector('.status-indicator');
  const statusText = document.querySelector('.status-text');
  
  if (!indicator || !statusText) return;
  
  if (isConnected) {
    indicator.className = 'status-indicator online';
    statusText.textContent = 'Online';
    statusText.className = 'status-text online';
  } else if (isReconnecting) {
    indicator.className = 'status-indicator reconnecting';
    statusText.textContent = 'Reconnecting...';
    statusText.className = 'status-text reconnecting';
  } else {
    indicator.className = 'status-indicator offline';
    statusText.textContent = 'Offline';
    statusText.className = 'status-text offline';
  }
}

/**
 * Set up refresh buttons
 */
function setupRefreshButtons() {
  // Campaign performance chart refresh button
  const performanceRefreshBtn = document.querySelector('.card:nth-of-type(1) .card-header .actions button:nth-child(2)');
  if (performanceRefreshBtn) {
    performanceRefreshBtn.addEventListener('click', () => {
      const loader = createLoader(performanceRefreshBtn.parentNode);
      
      realTimeDashboard.refreshAll()
        .then(() => {
          toastService.show('Dashboard data refreshed', 'success');
        })
        .catch(() => {
          toastService.show('Failed to refresh data', 'error');
        })
        .finally(() => {
          if (loader) loader.remove();
        });
    });
  }
}

// Add dashboard-specific styles
function addDashboardStyles() {
  const style = document.createElement('style');
  style.textContent = `
    /* Connection status indicator */
    .connection-status {
      display: flex;
      align-items: center;
      margin-right: 15px;
      padding: 5px 10px;
      border-radius: var(--radius);
      background: var(--neutral-50);
      border: 1px solid var(--neutral-200);
    }
    
    .status-indicator {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 8px;
      position: relative;
    }
    
    .status-indicator.online {
      background-color: var(--success-500);
    }
    
    .status-indicator.offline {
      background-color: var(--danger-500);
    }
    
    .status-indicator.reconnecting {
      background-color: var(--warning-500);
      animation: pulse 1.5s infinite;
    }
    
    .status-indicator i {
      font-size: 12px;
      position: absolute;
      top: -6px;
      left: -1px;
      color: var(--neutral-600);
    }
    
    .status-text {
      font-size: 12px;
      font-weight: 500;
    }
    
    .status-text.online {
      color: var(--success-600);
    }
    
    .status-text.offline {
      color: var(--danger-600);
    }
    
    .status-text.reconnecting {
      color: var(--warning-600);
    }
    
    /* Animation for updates */
    @keyframes pulse-update {
      0% { box-shadow: 0 0 0 0 rgba(var(--primary-500-rgb), 0.4); }
      70% { box-shadow: 0 0 0 10px rgba(var(--primary-500-rgb), 0); }
      100% { box-shadow: 0 0 0 0 rgba(var(--primary-500-rgb), 0); }
    }
    
    .pulse-update {
      animation: pulse-update 1s 1;
    }
    
    /* Row highlight for updates */
    @keyframes highlight-row {
      0% { background-color: rgba(var(--primary-100-rgb), 0.8); }
      100% { background-color: transparent; }
    }
    
    .highlight-update {
      animation: highlight-row 2s 1;
    }
    
    /* Pulse animation */
    @keyframes pulse {
      0% { opacity: 0.6; }
      50% { opacity: 1; }
      100% { opacity: 0.6; }
    }
  `;
  
  document.head.appendChild(style);
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Add dashboard styles
  addDashboardStyles();
  
  // Initialize dashboard
  initializeRealTimeDashboard();
});

// Clean up when page unloads
window.addEventListener('beforeunload', function() {
  // Unsubscribe from real-time updates
  realTimeApiClient.unsubscribeAll();
  
  // Disconnect WebSocket
  websocketService.disconnect();
});