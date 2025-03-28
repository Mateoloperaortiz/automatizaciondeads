/**
 * MagnetoCursor - Campaign Analytics Dashboard
 * 
 * A comprehensive dashboard for visualizing cross-platform campaign 
 * performance metrics and analytics.
 */

import { TimeSeriesChart } from './time-series-chart.js';
import { PlatformComparisonChart } from './platform-comparison-chart.js';
import { RoiVisualization } from './roi-visualization.js';
import { KpiMetricsPanel } from './kpi-metrics-panel.js';
import { CampaignPerformanceTable } from './campaign-performance-table.js';
import { CampaignBreakdownChart } from './campaign-breakdown-chart.js';

export class CampaignDashboard {
  /**
   * Initialize the campaign analytics dashboard
   * @param {string} containerId - ID of the container element
   * @param {Object} options - Configuration options
   */
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      throw new Error(`Container element with ID "${containerId}" not found`);
    }
    
    this.options = {
      refreshInterval: 0, // Auto-refresh interval in ms (0 = disabled)
      initialCampaignId: null, // Initial campaign to display
      initialDateRange: {
        start: this._getDefaultStartDate(),
        end: this._getDefaultEndDate()
      },
      showTimeSeriesChart: true, // Show time series performance chart
      showPlatformComparison: true, // Show platform comparison chart
      showRoiVisualization: true, // Show ROI visualization
      showKpiMetrics: true, // Show KPI metrics panel
      showPerformanceTable: true, // Show detailed performance table
      showBreakdownChart: true, // Show campaign breakdown chart
      darkMode: false, // Dark mode
      ...options
    };
    
    // State
    this.selectedCampaignId = this.options.initialCampaignId;
    this.dateRange = this.options.initialDateRange;
    this.campaigns = [];
    this.platforms = ['meta', 'google', 'twitter'];
    this.metrics = [
      { id: 'impressions', label: 'Impressions', format: 'number' },
      { id: 'clicks', label: 'Clicks', format: 'number' },
      { id: 'conversions', label: 'Conversions', format: 'number' },
      { id: 'ctr', label: 'CTR', format: 'percent' },
      { id: 'cpc', label: 'CPC', format: 'currency' },
      { id: 'cpa', label: 'CPA', format: 'currency' },
      { id: 'spend', label: 'Spend', format: 'currency' },
      { id: 'revenue', label: 'Revenue', format: 'currency' },
      { id: 'roi', label: 'ROI', format: 'percent' }
    ];
    this.selectedMetric = 'impressions';
    this.isLoading = false;
    this.refreshTimer = null;
    this.platformColors = {
      meta: '#4267B2',
      google: '#DB4437',
      twitter: '#1DA1F2'
    };
    
    // Components
    this.components = {};
    
    // Initialize dashboard
    this.initialize();
  }
  
  /**
   * Get default start date (30 days ago)
   * @private
   * @returns {Date} Default start date
   */
  _getDefaultStartDate() {
    const date = new Date();
    date.setDate(date.getDate() - 30);
    return date;
  }
  
  /**
   * Get default end date (today)
   * @private
   * @returns {Date} Default end date
   */
  _getDefaultEndDate() {
    return new Date();
  }
  
  /**
   * Format date for input field
   * @private
   * @param {Date} date - Date to format
   * @returns {string} Formatted date (YYYY-MM-DD)
   */
  _formatDateForInput(date) {
    return date.toISOString().split('T')[0];
  }
  
  /**
   * Initialize the dashboard
   */
  async initialize() {
    // Create dashboard structure
    this.createDashboardStructure();
    
    // Initialize components
    this.initializeComponents();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Load initial data
    await this.loadData();
    
    // Set up auto-refresh if enabled
    if (this.options.refreshInterval > 0) {
      this.refreshTimer = setInterval(() => {
        this.loadData();
      }, this.options.refreshInterval);
    }
    
    // Select initial campaign if available
    if (this.selectedCampaignId && this.campaigns.length > 0) {
      this.selectCampaign(this.selectedCampaignId);
    } else if (this.campaigns.length > 0) {
      // Select first campaign by default
      this.selectCampaign(this.campaigns[0].id);
    }
  }
  
  /**
   * Create the dashboard structure
   */
  createDashboardStructure() {
    // Clear container
    this.container.innerHTML = '';
    
    // Set container class
    this.container.classList.add('campaign-dashboard');
    if (this.options.darkMode) {
      this.container.classList.add('dark-mode');
    }
    
    // Create dashboard layout
    this.container.innerHTML = `
      <div class="dashboard-header">
        <h2>Campaign Analytics Dashboard</h2>
        <div class="dashboard-controls">
          <div class="control-group">
            <select id="campaign-selector" class="campaign-selector">
              <option value="">Loading campaigns...</option>
            </select>
          </div>
          <div class="control-group date-range-picker">
            <label for="date-start">From:</label>
            <input type="date" id="date-start" class="date-input">
            <label for="date-end">To:</label>
            <input type="date" id="date-end" class="date-input">
            <button id="apply-date-range" class="btn">Apply</button>
          </div>
          <div class="control-group">
            <button id="refresh-btn" class="btn refresh-btn">
              <i class="fas fa-sync-alt"></i> Refresh
            </button>
          </div>
        </div>
      </div>
      
      <div class="dashboard-content">
        ${this.options.showKpiMetrics ? `
          <div class="panel kpi-panel">
            <div id="kpi-metrics" class="kpi-metrics"></div>
          </div>
        ` : ''}
        
        <div class="charts-row">
          ${this.options.showTimeSeriesChart ? `
            <div class="panel chart-panel time-series-panel">
              <div class="panel-header">
                <h3>Performance Over Time</h3>
                <div class="panel-controls">
                  <select id="time-series-metric" class="metric-selector">
                    ${this.metrics.map(metric => `
                      <option value="${metric.id}">${metric.label}</option>
                    `).join('')}
                  </select>
                </div>
              </div>
              <div id="time-series-chart" class="chart-container"></div>
            </div>
          ` : ''}
          
          ${this.options.showPlatformComparison ? `
            <div class="panel chart-panel platform-comparison-panel">
              <div class="panel-header">
                <h3>Platform Comparison</h3>
                <div class="panel-controls">
                  <select id="platform-comparison-metric" class="metric-selector">
                    ${this.metrics.map(metric => `
                      <option value="${metric.id}">${metric.label}</option>
                    `).join('')}
                  </select>
                </div>
              </div>
              <div id="platform-comparison-chart" class="chart-container"></div>
            </div>
          ` : ''}
        </div>
        
        <div class="charts-row">
          ${this.options.showRoiVisualization ? `
            <div class="panel chart-panel roi-panel">
              <div class="panel-header">
                <h3>ROI Analysis</h3>
              </div>
              <div id="roi-visualization" class="chart-container"></div>
            </div>
          ` : ''}
          
          ${this.options.showBreakdownChart ? `
            <div class="panel chart-panel breakdown-panel">
              <div class="panel-header">
                <h3>Campaign Breakdown</h3>
                <div class="panel-controls">
                  <select id="breakdown-type" class="breakdown-selector">
                    <option value="platform">By Platform</option>
                    <option value="ad_type">By Ad Type</option>
                    <option value="placement">By Placement</option>
                    <option value="device">By Device</option>
                  </select>
                </div>
              </div>
              <div id="campaign-breakdown-chart" class="chart-container"></div>
            </div>
          ` : ''}
        </div>
        
        ${this.options.showPerformanceTable ? `
          <div class="panel table-panel">
            <div class="panel-header">
              <h3>Detailed Performance</h3>
              <div class="panel-controls">
                <button id="export-data-btn" class="btn">
                  <i class="fas fa-download"></i> Export
                </button>
              </div>
            </div>
            <div id="performance-table" class="table-container"></div>
          </div>
        ` : ''}
      </div>
    `;
    
    // Add dashboard stylesheet
    this._addStyles();
  }
  
  /**
   * Add dashboard styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('campaign-dashboard-styles')) {
      const style = document.createElement('style');
      style.id = 'campaign-dashboard-styles';
      style.textContent = `
        .campaign-dashboard {
          display: flex;
          flex-direction: column;
          font-family: var(--font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif);
          color: var(--text-color, #333);
          background: var(--bg-color, #f8f9fa);
          height: 100%;
          min-height: 600px;
        }
        
        .campaign-dashboard.dark-mode {
          --bg-color: #212529;
          --text-color: #f8f9fa;
          --panel-bg: #343a40;
          --panel-border: #495057;
          --highlight-color: #0d6efd;
          color: var(--text-color);
          background: var(--bg-color);
        }
        
        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid var(--panel-border, #dee2e6);
        }
        
        .dashboard-header h2 {
          margin: 0;
          font-size: 1.5rem;
        }
        
        .dashboard-controls {
          display: flex;
          gap: 1rem;
          align-items: center;
        }
        
        .control-group {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .date-range-picker {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .date-input {
          width: 120px;
          padding: 0.375rem 0.5rem;
          border: 1px solid var(--panel-border, #dee2e6);
          border-radius: 0.25rem;
          background-color: var(--panel-bg, white);
          color: var(--text-color, #333);
        }
        
        .dashboard-content {
          flex: 1;
          padding: 1rem;
          overflow: auto;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .charts-row {
          display: flex;
          gap: 1rem;
          height: 300px;
        }
        
        .panel {
          background: var(--panel-bg, white);
          border-radius: 0.25rem;
          border: 1px solid var(--panel-border, #dee2e6);
          box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
          overflow: hidden;
        }
        
        .chart-panel {
          flex: 1;
          display: flex;
          flex-direction: column;
        }
        
        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem 1rem;
          border-bottom: 1px solid var(--panel-border, #dee2e6);
        }
        
        .panel-header h3 {
          margin: 0;
          font-size: 1rem;
          font-weight: 600;
        }
        
        .panel-controls {
          display: flex;
          gap: 0.5rem;
        }
        
        .chart-container {
          flex: 1;
          padding: 1rem;
          min-height: 200px;
        }
        
        .kpi-metrics {
          display: flex;
          justify-content: space-between;
          padding: 1rem;
          flex-wrap: wrap;
        }
        
        .table-container {
          padding: 0;
          overflow: auto;
          max-height: 300px;
        }
        
        .campaign-selector, .metric-selector, .breakdown-selector {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--panel-border, #dee2e6);
          border-radius: 0.25rem;
          background-color: var(--panel-bg, white);
          color: var(--text-color, #333);
        }
        
        .btn {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--panel-border, #dee2e6);
          border-radius: 0.25rem;
          background-color: var(--panel-bg, white);
          color: var(--text-color, #333);
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
        }
        
        .refresh-btn i {
          transition: transform 0.3s;
        }
        
        .refresh-btn.loading i {
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 992px) {
          .charts-row {
            flex-direction: column;
            height: auto;
          }
          
          .chart-panel {
            height: 300px;
          }
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Initialize dashboard components
   */
  initializeComponents() {
    // Initialize KPI metrics panel
    if (this.options.showKpiMetrics) {
      const kpiContainer = document.getElementById('kpi-metrics');
      if (kpiContainer) {
        this.components.kpiPanel = new KpiMetricsPanel(kpiContainer, {
          darkMode: this.options.darkMode
        });
      }
    }
    
    // Initialize time series chart
    if (this.options.showTimeSeriesChart) {
      const timeSeriesContainer = document.getElementById('time-series-chart');
      if (timeSeriesContainer) {
        this.components.timeSeriesChart = new TimeSeriesChart(timeSeriesContainer, {
          darkMode: this.options.darkMode,
          metric: this.selectedMetric,
          dateRange: this.dateRange,
          platformColors: this.platformColors
        });
      }
    }
    
    // Initialize platform comparison chart
    if (this.options.showPlatformComparison) {
      const platformComparisonContainer = document.getElementById('platform-comparison-chart');
      if (platformComparisonContainer) {
        this.components.platformComparisonChart = new PlatformComparisonChart(platformComparisonContainer, {
          darkMode: this.options.darkMode,
          metric: this.selectedMetric,
          platforms: this.platforms,
          platformColors: this.platformColors
        });
      }
    }
    
    // Initialize ROI visualization
    if (this.options.showRoiVisualization) {
      const roiContainer = document.getElementById('roi-visualization');
      if (roiContainer) {
        this.components.roiVisualization = new RoiVisualization(roiContainer, {
          darkMode: this.options.darkMode,
          platforms: this.platforms,
          platformColors: this.platformColors
        });
      }
    }
    
    // Initialize campaign breakdown chart
    if (this.options.showBreakdownChart) {
      const breakdownContainer = document.getElementById('campaign-breakdown-chart');
      if (breakdownContainer) {
        this.components.breakdownChart = new CampaignBreakdownChart(breakdownContainer, {
          darkMode: this.options.darkMode,
          platformColors: this.platformColors,
          breakdownType: 'platform'
        });
      }
    }
    
    // Initialize performance table
    if (this.options.showPerformanceTable) {
      const tableContainer = document.getElementById('performance-table');
      if (tableContainer) {
        this.components.performanceTable = new CampaignPerformanceTable(tableContainer, {
          darkMode: this.options.darkMode,
          metrics: this.metrics
        });
      }
    }
  }
  
  /**
   * Set up dashboard event listeners
   */
  setupEventListeners() {
    // Campaign selector change
    const campaignSelector = document.getElementById('campaign-selector');
    if (campaignSelector) {
      campaignSelector.addEventListener('change', (e) => {
        const campaignId = parseInt(e.target.value, 10);
        if (!isNaN(campaignId)) {
          this.selectCampaign(campaignId);
        }
      });
    }
    
    // Date range inputs
    const dateStartInput = document.getElementById('date-start');
    const dateEndInput = document.getElementById('date-end');
    
    if (dateStartInput && dateEndInput) {
      // Set initial values
      dateStartInput.value = this._formatDateForInput(this.dateRange.start);
      dateEndInput.value = this._formatDateForInput(this.dateRange.end);
      
      // Apply date range button
      const applyDateBtn = document.getElementById('apply-date-range');
      if (applyDateBtn) {
        applyDateBtn.addEventListener('click', () => {
          const startDate = new Date(dateStartInput.value);
          const endDate = new Date(dateEndInput.value);
          
          if (startDate && endDate && startDate <= endDate) {
            this.setDateRange(startDate, endDate);
          } else {
            // Reset to current values
            dateStartInput.value = this._formatDateForInput(this.dateRange.start);
            dateEndInput.value = this._formatDateForInput(this.dateRange.end);
            console.error('Invalid date range');
          }
        });
      }
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.loadData();
      });
    }
    
    // Time series metric selector
    const timeSeriesMetricSelector = document.getElementById('time-series-metric');
    if (timeSeriesMetricSelector) {
      // Set initial value
      timeSeriesMetricSelector.value = this.selectedMetric;
      
      timeSeriesMetricSelector.addEventListener('change', (e) => {
        const metric = e.target.value;
        this.setTimeSeriesMetric(metric);
      });
    }
    
    // Platform comparison metric selector
    const platformComparisonMetricSelector = document.getElementById('platform-comparison-metric');
    if (platformComparisonMetricSelector) {
      // Set initial value
      platformComparisonMetricSelector.value = this.selectedMetric;
      
      platformComparisonMetricSelector.addEventListener('change', (e) => {
        const metric = e.target.value;
        this.setPlatformComparisonMetric(metric);
      });
    }
    
    // Breakdown type selector
    const breakdownTypeSelector = document.getElementById('breakdown-type');
    if (breakdownTypeSelector) {
      breakdownTypeSelector.addEventListener('change', (e) => {
        const breakdownType = e.target.value;
        this.setBreakdownType(breakdownType);
      });
    }
    
    // Export data button
    const exportDataBtn = document.getElementById('export-data-btn');
    if (exportDataBtn) {
      exportDataBtn.addEventListener('click', () => {
        this.exportData();
      });
    }
  }
  
  /**
   * Update loading state
   * @param {boolean} isLoading - Whether loading is in progress
   * @private
   */
  _updateLoadingState(isLoading) {
    // Update refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      const icon = refreshBtn.querySelector('i');
      if (icon) {
        if (isLoading) {
          icon.classList.add('fa-spin');
          refreshBtn.classList.add('loading');
        } else {
          icon.classList.remove('fa-spin');
          refreshBtn.classList.remove('loading');
        }
      }
      refreshBtn.disabled = isLoading;
    }
    
    // Update campaign selector
    const campaignSelector = document.getElementById('campaign-selector');
    if (campaignSelector) {
      campaignSelector.disabled = isLoading;
    }
    
    // Update date inputs
    const dateInputs = document.querySelectorAll('.date-input');
    dateInputs.forEach(input => {
      input.disabled = isLoading;
    });
    
    // Update apply button
    const applyBtn = document.getElementById('apply-date-range');
    if (applyBtn) {
      applyBtn.disabled = isLoading;
    }
  }
  
  /**
   * Update campaign selector
   * @private
   */
  _updateCampaignSelector() {
    const campaignSelector = document.getElementById('campaign-selector');
    if (!campaignSelector) return;
    
    // Clear existing options
    campaignSelector.innerHTML = '';
    
    if (this.campaigns.length === 0) {
      // No campaigns available
      const option = document.createElement('option');
      option.value = '';
      option.textContent = 'No campaigns available';
      campaignSelector.appendChild(option);
      
      // Disable selector
      campaignSelector.disabled = true;
    } else {
      // Add campaigns to selector
      this.campaigns.forEach(campaign => {
        const option = document.createElement('option');
        option.value = campaign.id;
        option.textContent = campaign.name;
        campaignSelector.appendChild(option);
      });
      
      // Enable selector
      campaignSelector.disabled = false;
    }
  }
  
  /**
   * Fetch campaigns
   * @returns {Promise<Array>} - Array of campaign objects
   * @private
   */
  async _fetchCampaigns() {
    try {
      const response = await fetch('/api/campaigns/list');
      const data = await response.json();
      
      if (data.status === 'success' && Array.isArray(data.campaigns)) {
        return data.campaigns.map(campaign => ({
          id: campaign.id,
          name: campaign.name,
          description: campaign.description,
          status: campaign.status,
          budget: campaign.budget,
          platform: campaign.platform,
          startDate: campaign.startDate,
          endDate: campaign.endDate
        }));
      } else {
        console.error('Invalid campaign data format:', data);
        return [];
      }
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      
      // Fallback to mock data if API call fails
      return [
        { id: 1, name: 'Q1 2025 Product Launch' },
        { id: 2, name: 'Summer Sale 2025' },
        { id: 3, name: 'Holiday Promotion 2024' },
        { id: 4, name: 'Brand Awareness Campaign' },
        { id: 5, name: 'Lead Generation Q2 2025' }
      ];
    }
  }
  
  /**
   * Fetch time series data
   * @param {number} campaignId - Campaign ID
   * @param {Object} dateRange - Date range
   * @returns {Promise<Object>} - Time series data
   * @private
   */
  async _fetchTimeSeriesData(campaignId, dateRange) {
    // Simulate network request
    await new Promise(resolve => setTimeout(resolve, 700));
    
    // Generate mock data
    const days = this._getDaysBetweenDates(dateRange.start, dateRange.end);
    const platformData = {};
    
    this.platforms.forEach(platform => {
      platformData[platform] = {
        impressions: [],
        clicks: [],
        conversions: [],
        ctr: [],
        cpc: [],
        cpa: [],
        spend: [],
        revenue: [],
        roi: []
      };
      
      let trend = Math.random() * 100;
      
      days.forEach(day => {
        // Add random variation to trend
        trend = Math.max(0, trend + (Math.random() - 0.5) * 20);
        
        // Base metrics
        const impressions = Math.round(trend * 100);
        const clicks = Math.round(impressions * (Math.random() * 0.05 + 0.01));
        const conversions = Math.round(clicks * (Math.random() * 0.1 + 0.05));
        const spend = Math.round(clicks * (Math.random() * 1.5 + 0.5) * 100) / 100;
        const revenue = Math.round(conversions * (Math.random() * 30 + 10) * 100) / 100;
        
        // Calculated metrics
        const ctr = clicks / impressions * 100;
        const cpc = spend / clicks;
        const cpa = conversions > 0 ? spend / conversions : 0;
        const roi = spend > 0 ? (revenue - spend) / spend * 100 : 0;
        
        // Add to arrays
        platformData[platform].impressions.push({ x: day, y: impressions });
        platformData[platform].clicks.push({ x: day, y: clicks });
        platformData[platform].conversions.push({ x: day, y: conversions });
        platformData[platform].ctr.push({ x: day, y: ctr });
        platformData[platform].cpc.push({ x: day, y: cpc });
        platformData[platform].cpa.push({ x: day, y: cpa });
        platformData[platform].spend.push({ x: day, y: spend });
        platformData[platform].revenue.push({ x: day, y: revenue });
        platformData[platform].roi.push({ x: day, y: roi });
      });
    });
    
    return {
      campaignId,
      dateRange,
      platforms: this.platforms,
      data: platformData
    };
  }
  
  /**
   * Get array of dates between two dates
   * @param {Date} startDate - Start date
   * @param {Date} endDate - End date
   * @returns {Array<string>} - Array of date strings
   * @private
   */
  _getDaysBetweenDates(startDate, endDate) {
    const days = [];
    let currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
      days.push(currentDate.toISOString().split('T')[0]);
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return days;
  }
  
  /**
   * Fetch platform comparison data
   * @param {number} campaignId - Campaign ID
   * @param {Object} dateRange - Date range
   * @returns {Promise<Object>} - Platform comparison data
   * @private
   */
  async _fetchPlatformData(campaignId, dateRange) {
    // Simulate network request
    await new Promise(resolve => setTimeout(resolve, 600));
    
    // Generate mock data
    const platformData = {};
    
    this.metrics.forEach(metric => {
      platformData[metric.id] = {};
      
      this.platforms.forEach(platform => {
        switch (metric.id) {
          case 'impressions':
            platformData[metric.id][platform] = Math.floor(Math.random() * 500000) + 50000;
            break;
          case 'clicks':
            platformData[metric.id][platform] = Math.floor(Math.random() * 20000) + 1000;
            break;
          case 'conversions':
            platformData[metric.id][platform] = Math.floor(Math.random() * 1000) + 50;
            break;
          case 'ctr':
            platformData[metric.id][platform] = Math.random() * 5 + 0.5;
            break;
          case 'cpc':
            platformData[metric.id][platform] = Math.random() * 2 + 0.5;
            break;
          case 'cpa':
            platformData[metric.id][platform] = Math.random() * 50 + 10;
            break;
          case 'spend':
            platformData[metric.id][platform] = Math.floor(Math.random() * 10000) + 1000;
            break;
          case 'revenue':
            platformData[metric.id][platform] = Math.floor(Math.random() * 30000) + 5000;
            break;
          case 'roi':
            platformData[metric.id][platform] = Math.random() * 300 + 50;
            break;
          default:
            platformData[metric.id][platform] = Math.random() * 100;
            break;
        }
      });
    });
    
    return {
      campaignId,
      dateRange,
      platforms: this.platforms,
      data: platformData
    };
  }
  
  /**
   * Fetch ROI data
   * @param {number} campaignId - Campaign ID
   * @param {Object} dateRange - Date range
   * @returns {Promise<Object>} - ROI data
   * @private
   */
  async _fetchRoiData(campaignId, dateRange) {
    // Simulate network request
    await new Promise(resolve => setTimeout(resolve, 550));
    
    // Generate mock data
    const roiData = {
      overall: {
        spend: 0,
        revenue: 0,
        roi: 0,
        conversions: 0
      },
      platforms: {}
    };
    
    // Generate data for each platform
    this.platforms.forEach(platform => {
      const spend = Math.floor(Math.random() * 10000) + 1000;
      const revenue = Math.floor(Math.random() * 30000) + 5000;
      const conversions = Math.floor(Math.random() * 1000) + 50;
      const roi = (revenue - spend) / spend * 100;
      
      roiData.platforms[platform] = {
        spend,
        revenue,
        roi,
        conversions
      };
      
      // Accumulate in overall
      roiData.overall.spend += spend;
      roiData.overall.revenue += revenue;
      roiData.overall.conversions += conversions;
    });
    
    // Calculate overall ROI
    roiData.overall.roi = (roiData.overall.revenue - roiData.overall.spend) / roiData.overall.spend * 100;
    
    // Add breakdown data
    roiData.breakdowns = {
      platform: this._generateBreakdownData('platform'),
      ad_type: this._generateBreakdownData('ad_type'),
      placement: this._generateBreakdownData('placement'),
      device: this._generateBreakdownData('device')
    };
    
    return {
      campaignId,
      dateRange,
      data: roiData
    };
  }
  
  /**
   * Generate breakdown data for different types
   * @param {string} type - Breakdown type
   * @returns {Array} - Breakdown data
   * @private
   */
  _generateBreakdownData(type) {
    const data = [];
    
    switch (type) {
      case 'platform':
        this.platforms.forEach(platform => {
          data.push({
            name: platform,
            spend: Math.floor(Math.random() * 10000) + 1000,
            revenue: Math.floor(Math.random() * 30000) + 5000,
            impressions: Math.floor(Math.random() * 500000) + 50000,
            clicks: Math.floor(Math.random() * 20000) + 1000,
            conversions: Math.floor(Math.random() * 1000) + 50
          });
        });
        break;
      
      case 'ad_type':
        ['Image', 'Video', 'Carousel', 'Collection'].forEach(adType => {
          data.push({
            name: adType,
            spend: Math.floor(Math.random() * 10000) + 1000,
            revenue: Math.floor(Math.random() * 30000) + 5000,
            impressions: Math.floor(Math.random() * 500000) + 50000,
            clicks: Math.floor(Math.random() * 20000) + 1000,
            conversions: Math.floor(Math.random() * 1000) + 50
          });
        });
        break;
      
      case 'placement':
        ['Feed', 'Stories', 'Search', 'Display'].forEach(placement => {
          data.push({
            name: placement,
            spend: Math.floor(Math.random() * 10000) + 1000,
            revenue: Math.floor(Math.random() * 30000) + 5000,
            impressions: Math.floor(Math.random() * 500000) + 50000,
            clicks: Math.floor(Math.random() * 20000) + 1000,
            conversions: Math.floor(Math.random() * 1000) + 50
          });
        });
        break;
      
      case 'device':
        ['Desktop', 'Mobile', 'Tablet'].forEach(device => {
          data.push({
            name: device,
            spend: Math.floor(Math.random() * 10000) + 1000,
            revenue: Math.floor(Math.random() * 30000) + 5000,
            impressions: Math.floor(Math.random() * 500000) + 50000,
            clicks: Math.floor(Math.random() * 20000) + 1000,
            conversions: Math.floor(Math.random() * 1000) + 50
          });
        });
        break;
    }
    
    return data;
  }
  
  /**
   * Fetch campaign details
   * @param {number} campaignId - Campaign ID
   * @returns {Promise<Object>} - Campaign details
   * @private
   */
  async _fetchCampaignDetails(campaignId) {
    // Simulate network request
    await new Promise(resolve => setTimeout(resolve, 400));
    
    // Find campaign in list
    const campaign = this.campaigns.find(c => c.id === campaignId);
    
    if (!campaign) {
      throw new Error(`Campaign with ID ${campaignId} not found`);
    }
    
    // Generate mock data
    return {
      id: campaign.id,
      name: campaign.name,
      status: Math.random() > 0.3 ? 'Active' : 'Paused',
      startDate: this._generateRandomDate(90),
      endDate: null,
      budget: Math.floor(Math.random() * 50000) + 5000,
      platforms: this.platforms,
      objectives: {
        primary: 'Conversions',
        secondary: 'Brand Awareness'
      },
      targeting: {
        audience: 'Job Seekers',
        demographics: ['Ages 25-45', 'Professionals'],
        locations: ['United States', 'Canada', 'United Kingdom'],
        interests: ['Technology', 'Career Development', 'Job Hunting']
      }
    };
  }
  
  /**
   * Generate a random date within the past X days
   * @param {number} daysAgo - Maximum days ago
   * @returns {Date} - Random date
   * @private
   */
  _generateRandomDate(daysAgo) {
    const date = new Date();
    date.setDate(date.getDate() - Math.floor(Math.random() * daysAgo));
    return date;
  }
  
  /**
   * Load dashboard data
   * @returns {Promise<void>}
   */
  async loadData() {
    if (this.isLoading) return;
    
    this.isLoading = true;
    this._updateLoadingState(true);
    
    try {
      // Fetch campaigns
      this.campaigns = await this._fetchCampaigns();
      this._updateCampaignSelector();
      
      // Set campaign if needed
      if (this.selectedCampaignId === null && this.campaigns.length > 0) {
        this.selectedCampaignId = this.campaigns[0].id;
      }
      
      // Set selected campaign in selector
      const campaignSelector = document.getElementById('campaign-selector');
      if (campaignSelector && this.selectedCampaignId) {
        campaignSelector.value = this.selectedCampaignId;
      }
      
      // Load campaign data if campaign is selected
      if (this.selectedCampaignId) {
        await this._loadCampaignData(this.selectedCampaignId);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      this.isLoading = false;
      this._updateLoadingState(false);
    }
  }
  
  /**
   * Load data for a specific campaign
   * @param {number} campaignId - Campaign ID
   * @returns {Promise<void>}
   * @private
   */
  async _loadCampaignData(campaignId) {
    try {
      // Format date range for API
      const dateStart = this._formatDateForInput(this.dateRange.start);
      const dateEnd = this._formatDateForInput(this.dateRange.end);
      
      // Fetch campaign analytics data from API
      const response = await fetch(`/api/campaign/analytics/${campaignId}?date_from=${dateStart}&date_to=${dateEnd}`);
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      const analyticsData = await response.json();
      
      if (analyticsData.status !== 'success') {
        throw new Error('Failed to load campaign analytics data');
      }
      
      // Extract data from response
      const timeSeriesData = analyticsData.timeSeriesData;
      const platformData = analyticsData.platformData;
      const roiData = analyticsData.roiData;
      const campaignDetails = analyticsData.campaign;
      
      // Update platforms array
      if (analyticsData.platforms) {
        this.platforms = analyticsData.platforms;
      }
      
      // Update time series chart
      if (this.components.timeSeriesChart) {
        this.components.timeSeriesChart.updateData(timeSeriesData, {
          metric: this.selectedMetric,
          dateRange: this.dateRange
        });
      }
      
      // Update platform comparison chart
      if (this.components.platformComparisonChart) {
        this.components.platformComparisonChart.updateData(platformData, {
          metric: this.selectedMetric
        });
      }
      
      // Update ROI visualization
      if (this.components.roiVisualization) {
        this.components.roiVisualization.updateData(roiData);
      }
      
      // Update breakdown chart
      if (this.components.breakdownChart) {
        const breakdownType = document.getElementById('breakdown-type')?.value || 'platform';
        this.components.breakdownChart.updateData(roiData.breakdowns[breakdownType], {
          breakdownType
        });
      }
      
      // Update KPI panel
      if (this.components.kpiPanel) {
        this.components.kpiPanel.updateData({
          impressions: this._sumMetricAcrossPlatforms(platformData, 'impressions'),
          clicks: this._sumMetricAcrossPlatforms(platformData, 'clicks'),
          conversions: this._sumMetricAcrossPlatforms(platformData, 'conversions'),
          spend: this._sumMetricAcrossPlatforms(platformData, 'spend'),
          revenue: this._sumMetricAcrossPlatforms(platformData, 'revenue'),
          roi: roiData.overall.roi
        });
      }
      
      // Update performance table
      if (this.components.performanceTable) {
        this.components.performanceTable.updateData({
          campaigns: [campaignDetails],
          timeframe: `${this._formatDate(this.dateRange.start)} - ${this._formatDate(this.dateRange.end)}`,
          metrics: platformData,
          platforms: this.platforms
        });
      }
    } catch (error) {
      console.error('Error loading campaign data:', error);
      
      // Fallback to mock data generation
      const [timeSeriesData, platformData, roiData, campaignDetails] = await Promise.all([
        this._fetchTimeSeriesData(campaignId, this.dateRange),
        this._fetchPlatformData(campaignId, this.dateRange),
        this._fetchRoiData(campaignId, this.dateRange),
        this._fetchCampaignDetails(campaignId)
      ]);
      
      // Update components with mock data (same code as before)
      if (this.components.timeSeriesChart) {
        this.components.timeSeriesChart.updateData(timeSeriesData.data, {
          metric: this.selectedMetric,
          dateRange: this.dateRange
        });
      }
      
      if (this.components.platformComparisonChart) {
        this.components.platformComparisonChart.updateData(platformData.data, {
          metric: this.selectedMetric
        });
      }
      
      if (this.components.roiVisualization) {
        this.components.roiVisualization.updateData(roiData.data);
      }
      
      if (this.components.breakdownChart) {
        const breakdownType = document.getElementById('breakdown-type')?.value || 'platform';
        this.components.breakdownChart.updateData(roiData.data.breakdowns[breakdownType], {
          breakdownType
        });
      }
      
      if (this.components.kpiPanel) {
        this.components.kpiPanel.updateData({
          impressions: this._sumMetricAcrossPlatforms(platformData.data, 'impressions'),
          clicks: this._sumMetricAcrossPlatforms(platformData.data, 'clicks'),
          conversions: this._sumMetricAcrossPlatforms(platformData.data, 'conversions'),
          spend: this._sumMetricAcrossPlatforms(platformData.data, 'spend'),
          revenue: this._sumMetricAcrossPlatforms(platformData.data, 'revenue'),
          roi: roiData.data.overall.roi
        });
      }
      
      if (this.components.performanceTable) {
        this.components.performanceTable.updateData({
          campaigns: [campaignDetails],
          timeframe: `${this._formatDate(this.dateRange.start)} - ${this._formatDate(this.dateRange.end)}`,
          metrics: platformData.data,
          platforms: this.platforms
        });
      }
    }
  }
  
  /**
   * Sum a metric across all platforms
   * @param {Object} data - Platform data
   * @param {string} metric - Metric to sum
   * @returns {number} - Sum of metric across platforms
   * @private
   */
  _sumMetricAcrossPlatforms(data, metric) {
    let sum = 0;
    
    if (data && data[metric]) {
      for (const platform of this.platforms) {
        sum += data[metric][platform] || 0;
      }
    }
    
    return sum;
  }
  
  /**
   * Format date for display
   * @param {Date} date - Date to format
   * @returns {string} - Formatted date
   * @private
   */
  _formatDate(date) {
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
  
  /**
   * Select a campaign
   * @param {number} campaignId - Campaign ID
   */
  async selectCampaign(campaignId) {
    if (campaignId === this.selectedCampaignId || this.isLoading) return;
    
    this.selectedCampaignId = campaignId;
    
    // Update campaign selector
    const campaignSelector = document.getElementById('campaign-selector');
    if (campaignSelector) {
      campaignSelector.value = this.selectedCampaignId;
    }
    
    // Load campaign data
    await this._loadCampaignData(campaignId);
  }
  
  /**
   * Set date range
   * @param {Date} startDate - Start date
   * @param {Date} endDate - End date
   */
  async setDateRange(startDate, endDate) {
    if (!startDate || !endDate || startDate > endDate) {
      console.error('Invalid date range');
      return;
    }
    
    this.dateRange = {
      start: startDate,
      end: endDate
    };
    
    // Update inputs
    const dateStartInput = document.getElementById('date-start');
    const dateEndInput = document.getElementById('date-end');
    
    if (dateStartInput) {
      dateStartInput.value = this._formatDateForInput(startDate);
    }
    
    if (dateEndInput) {
      dateEndInput.value = this._formatDateForInput(endDate);
    }
    
    // Reload data for selected campaign
    if (this.selectedCampaignId) {
      await this._loadCampaignData(this.selectedCampaignId);
    }
  }
  
  /**
   * Set time series metric
   * @param {string} metric - Metric to display
   */
  setTimeSeriesMetric(metric) {
    if (!this.components.timeSeriesChart) return;
    
    // Update time series chart
    this.components.timeSeriesChart.updateOptions({
      metric
    });
  }
  
  /**
   * Set platform comparison metric
   * @param {string} metric - Metric to display
   */
  setPlatformComparisonMetric(metric) {
    if (!this.components.platformComparisonChart) return;
    
    // Update platform comparison chart
    this.components.platformComparisonChart.updateOptions({
      metric
    });
  }
  
  /**
   * Set breakdown type
   * @param {string} breakdownType - Breakdown type
   */
  setBreakdownType(breakdownType) {
    if (!this.components.breakdownChart) return;
    
    if (this.selectedCampaignId) {
      // Fetch ROI data again to get the needed breakdown
      this._fetchRoiData(this.selectedCampaignId, this.dateRange)
        .then(roiData => {
          // Update breakdown chart
          this.components.breakdownChart.updateData(roiData.data.breakdowns[breakdownType], {
            breakdownType
          });
        })
        .catch(error => {
          console.error('Error fetching breakdown data:', error);
        });
    }
  }
  
  /**
   * Export dashboard data
   */
  exportData() {
    if (!this.selectedCampaignId) {
      console.error('No campaign selected');
      return;
    }
    
    // Format data for export
    const campaign = this.campaigns.find(c => c.id === this.selectedCampaignId);
    
    const exportData = {
      campaign: {
        id: this.selectedCampaignId,
        name: campaign ? campaign.name : `Campaign ${this.selectedCampaignId}`
      },
      dateRange: {
        start: this._formatDate(this.dateRange.start),
        end: this._formatDate(this.dateRange.end)
      },
      exportDate: this._formatDate(new Date()),
      platforms: this.platforms,
      data: {
        // Will be populated by the data
      }
    };
    
    // Get platform data
    this._fetchPlatformData(this.selectedCampaignId, this.dateRange)
      .then(platformData => {
        exportData.data.metrics = platformData.data;
        
        // Convert to CSV
        const csv = this._generateCsv(exportData);
        
        // Create download link
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `campaign_${this.selectedCampaignId}_report.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      })
      .catch(error => {
        console.error('Error exporting data:', error);
      });
  }
  
  /**
   * Generate CSV from campaign data
   * @param {Object} data - Export data
   * @returns {string} - CSV content
   * @private
   */
  _generateCsv(data) {
    const rows = [];
    
    // Header row
    rows.push(`Campaign Report: ${data.campaign.name}`);
    rows.push(`Date Range: ${data.dateRange.start} - ${data.dateRange.end}`);
    rows.push(`Generated: ${data.exportDate}`);
    rows.push('');
    
    // Metrics header
    const platformsHeader = ['Metric', ...data.platforms];
    rows.push(platformsHeader.join(','));
    
    // Metrics rows
    for (const metricId of Object.keys(data.data.metrics)) {
      const metric = this.metrics.find(m => m.id === metricId);
      if (!metric) continue;
      
      const row = [metric.label];
      
      for (const platform of data.platforms) {
        const value = data.data.metrics[metricId][platform];
        let formattedValue;
        
        switch (metric.format) {
          case 'percent':
            formattedValue = `${value.toFixed(2)}%`;
            break;
          case 'currency':
            formattedValue = `$${value.toFixed(2)}`;
            break;
          default:
            formattedValue = value.toLocaleString();
            break;
        }
        
        row.push(formattedValue);
      }
      
      rows.push(row.join(','));
    }
    
    return rows.join('\n');
  }
  
  /**
   * Destroy the dashboard and clean up
   */
  destroy() {
    // Clear auto-refresh timer
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
    
    // Destroy components
    for (const component of Object.values(this.components)) {
      if (component && typeof component.destroy === 'function') {
        component.destroy();
      }
    }
    
    // Clear container
    if (this.container) {
      this.container.innerHTML = '';
      this.container.classList.remove('campaign-dashboard', 'dark-mode');
    }
    
    // Clear references
    this.components = {};
    this.campaigns = [];
    this.selectedCampaignId = null;
  }
}