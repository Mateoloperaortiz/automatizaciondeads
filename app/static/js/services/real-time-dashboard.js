/**
 * Real-Time Dashboard Service
 * Implements real-time updates for the main dashboard
 * Shows integration of all three phases of the service layer architecture
 */

import { campaignService } from './campaign-service.js';
import { jobOpeningService } from './job-opening-service.js';
import { candidateService } from './candidate-service.js';
import { segmentService } from './segment-service.js';
import { analyticsService } from './analytics-service.js';
import { platformService } from './platform-service.js';
import { realTimeApiClient, WATCHED_ENTITIES, UPDATE_TYPES } from './real-time-api.js';
import { toastService } from './toast-service.js';
import eventHub from './event-hub.js';
import { errorHandler } from './error-handler.js';

// Dashboard-specific event types
export const DASHBOARD_EVENTS = {
  METRICS_UPDATED: 'dashboard:metrics_updated',
  CAMPAIGN_UPDATED: 'dashboard:campaign_updated',
  JOB_UPDATED: 'dashboard:job_updated',
  CHART_DATA_UPDATED: 'dashboard:chart_data_updated',
  CONVERSION_UPDATED: 'dashboard:conversion_updated',
};

/**
 * Real-Time Dashboard Service
 * Centralizes dashboard-specific functionality with real-time updates
 */
export class RealTimeDashboard {
  /**
   * Create a new RealTimeDashboard service
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = {
      autoRefresh: true,
      refreshInterval: 60000, // 1 minute
      showToasts: true,
      ...options
    };

    // Dashboard state
    this.metrics = {
      jobCount: 0,
      campaignCount: 0,
      candidateCount: 0,
      segmentCount: 0
    };
    
    this.campaigns = [];
    this.jobs = [];
    this.chartData = {
      platforms: [],
      impressions: [],
      clicks: [],
      applications: []
    };
    this.conversionMetrics = {
      clickThroughRate: 0,
      applicationRate: 0,
      interviewConversion: 0,
      costPerApplication: 0
    };

    // Refresh timer
    this.refreshTimer = null;
    
    // Event cleanup functions
    this.cleanupFunctions = [];

    // Initialize
    this.initialize();
  }

  /**
   * Initialize the dashboard service
   */
  async initialize() {
    try {
      // Load initial data
      await this.refreshAll();
      
      // Subscribe to real-time updates
      this._setupRealTimeUpdates();
      
      // Set up auto-refresh if enabled
      if (this.options.autoRefresh) {
        this._setupAutoRefresh();
      }
      
      console.log('Real-Time Dashboard initialized');
    } catch (error) {
      errorHandler.handleError(error, 'Failed to initialize dashboard');
    }
  }

  /**
   * Refresh all dashboard data
   * @returns {Promise<void>}
   */
  async refreshAll() {
    try {
      // Parallel fetch of all data
      const [metrics, campaigns, jobs, analyticsData] = await Promise.all([
        this._fetchMetrics(),
        this._fetchRecentCampaigns(),
        this._fetchRecentJobs(),
        this._fetchAnalyticsData()
      ]);

      // Update state
      this.metrics = metrics;
      this.campaigns = campaigns;
      this.jobs = jobs;
      this.chartData = analyticsData.chartData;
      this.conversionMetrics = analyticsData.conversionMetrics;

      // Emit events for UI updates
      eventHub.emit(DASHBOARD_EVENTS.METRICS_UPDATED, this.metrics);
      eventHub.emit(DASHBOARD_EVENTS.CHART_DATA_UPDATED, this.chartData);
      eventHub.emit(DASHBOARD_EVENTS.CONVERSION_UPDATED, this.conversionMetrics);
      
      // Notify that refresh is complete
      console.log('Dashboard data refreshed');
    } catch (error) {
      errorHandler.handleError(error, 'Failed to refresh dashboard data');
      throw error;
    }
  }

  /**
   * Fetch dashboard metrics
   * @returns {Promise<Object>} - Metrics data
   * @private
   */
  async _fetchMetrics() {
    try {
      // Use Phase 2 services to fetch data
      const jobCount = await jobOpeningService.count();
      const campaignCount = await campaignService.count();
      const candidateCount = await candidateService.count();
      const segmentCount = await segmentService.count();

      return {
        jobCount,
        campaignCount,
        candidateCount,
        segmentCount
      };
    } catch (error) {
      errorHandler.handleError(error, 'Failed to fetch metrics');
      throw error;
    }
  }

  /**
   * Fetch recent campaigns
   * @returns {Promise<Array>} - Campaign data
   * @private
   */
  async _fetchRecentCampaigns() {
    try {
      // Use Phase 2 services with pagination
      const result = await campaignService.list({
        page: 1,
        limit: 5,
        sortBy: 'created_at',
        sortDirection: 'desc'
      });

      return result.items;
    } catch (error) {
      errorHandler.handleError(error, 'Failed to fetch recent campaigns');
      throw error;
    }
  }

  /**
   * Fetch recent job openings
   * @returns {Promise<Array>} - Job data
   * @private
   */
  async _fetchRecentJobs() {
    try {
      // Use Phase 2 services with pagination
      const result = await jobOpeningService.list({
        page: 1,
        limit: 5,
        sortBy: 'created_at',
        sortDirection: 'desc'
      });

      return result.items;
    } catch (error) {
      errorHandler.handleError(error, 'Failed to fetch recent jobs');
      throw error;
    }
  }

  /**
   * Fetch analytics data for charts
   * @returns {Promise<Object>} - Analytics data
   * @private
   */
  async _fetchAnalyticsData() {
    try {
      // Use analytics service from Phase 2
      const platformStats = await analyticsService.getPlatformStats();
      const conversionStats = await analyticsService.getConversionMetrics();

      // Transform platform stats for chart data
      const chartData = {
        platforms: platformStats.map(item => item.platform_name),
        impressions: platformStats.map(item => item.impressions),
        clicks: platformStats.map(item => item.clicks),
        applications: platformStats.map(item => item.applications)
      };

      // Format conversion metrics
      const conversionMetrics = {
        clickThroughRate: conversionStats.click_through_rate,
        applicationRate: conversionStats.application_rate,
        interviewConversion: conversionStats.interview_conversion,
        costPerApplication: conversionStats.cost_per_application
      };

      return {
        chartData,
        conversionMetrics
      };
    } catch (error) {
      errorHandler.handleError(error, 'Failed to fetch analytics data');
      throw error;
    }
  }

  /**
   * Set up real-time updates for dashboard data
   * @private
   */
  _setupRealTimeUpdates() {
    // Subscribe to campaign updates
    const removeCampaignListener = realTimeApiClient.onAnyEntityUpdate(
      WATCHED_ENTITIES.CAMPAIGN, 
      this._handleCampaignUpdate.bind(this)
    );
    this.cleanupFunctions.push(removeCampaignListener);

    // Subscribe to job opening updates
    const removeJobListener = realTimeApiClient.onAnyEntityUpdate(
      WATCHED_ENTITIES.JOB_OPENING,
      this._handleJobUpdate.bind(this)
    );
    this.cleanupFunctions.push(removeJobListener);

    // Subscribe to analytics updates
    const removeAnalyticsListener = realTimeApiClient.onAnyEntityUpdate(
      WATCHED_ENTITIES.ANALYTICS,
      this._handleAnalyticsUpdate.bind(this)
    );
    this.cleanupFunctions.push(removeAnalyticsListener);

    // Subscribe to candidate and segment updates for count updates
    const removeCandidateListener = realTimeApiClient.onEntityUpdate(
      WATCHED_ENTITIES.CANDIDATE,
      UPDATE_TYPES.CREATED,
      () => this._updateMetricCount('candidateCount')
    );
    this.cleanupFunctions.push(removeCandidateListener);

    const removeSegmentListener = realTimeApiClient.onEntityUpdate(
      WATCHED_ENTITIES.SEGMENT,
      UPDATE_TYPES.CREATED,
      () => this._updateMetricCount('segmentCount')
    );
    this.cleanupFunctions.push(removeSegmentListener);

    // Subscribe to platform status updates
    const removePlatformListener = realTimeApiClient.onEntityUpdate(
      WATCHED_ENTITIES.PLATFORM_STATUS,
      UPDATE_TYPES.STATUS_CHANGE,
      this._handlePlatformStatusUpdate.bind(this)
    );
    this.cleanupFunctions.push(removePlatformListener);

    console.log('Real-time updates configured for dashboard');
  }

  /**
   * Set up auto-refresh for dashboard data
   * @private
   */
  _setupAutoRefresh() {
    // Clear any existing timer
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }

    // Set up new timer
    this.refreshTimer = setInterval(() => {
      this.refreshAll().catch(error => {
        console.error('Auto-refresh failed:', error);
      });
    }, this.options.refreshInterval);

    console.log(`Auto-refresh enabled (${this.options.refreshInterval / 1000}s)`);
  }

  /**
   * Handle campaign update event
   * @param {Object} campaign - Updated campaign data
   * @param {Object} data - Update event data
   * @private
   */
  async _handleCampaignUpdate(campaign, data) {
    try {
      const updateType = data.update_type;

      // Update campaign count for new campaigns
      if (updateType === UPDATE_TYPES.CREATED) {
        await this._updateMetricCount('campaignCount');
        
        // Add to recent campaigns if we have fewer than 5
        if (this.campaigns.length < 5) {
          this.campaigns.unshift(campaign);
          if (this.campaigns.length > 5) {
            this.campaigns.pop();
          }
          eventHub.emit(DASHBOARD_EVENTS.CAMPAIGN_UPDATED, this.campaigns);
        }
      } 
      // Update existing campaign in list
      else if (updateType === UPDATE_TYPES.UPDATED || updateType === UPDATE_TYPES.STATUS_CHANGE) {
        const index = this.campaigns.findIndex(c => c.id === campaign.id);
        if (index !== -1) {
          this.campaigns[index] = { ...this.campaigns[index], ...campaign };
          eventHub.emit(DASHBOARD_EVENTS.CAMPAIGN_UPDATED, this.campaigns);
        }
      }
      // Remove deleted campaign from list
      else if (updateType === UPDATE_TYPES.DELETED) {
        const index = this.campaigns.findIndex(c => c.id === campaign.id);
        if (index !== -1) {
          this.campaigns.splice(index, 1);
          
          // Fetch a replacement to keep the list at 5 items
          const newCampaigns = await this._fetchRecentCampaigns();
          this.campaigns = newCampaigns;
          
          eventHub.emit(DASHBOARD_EVENTS.CAMPAIGN_UPDATED, this.campaigns);
          await this._updateMetricCount('campaignCount');
        }
      }
    } catch (error) {
      errorHandler.handleError(error, 'Error handling campaign update');
    }
  }

  /**
   * Handle job opening update event
   * @param {Object} job - Updated job data
   * @param {Object} data - Update event data
   * @private
   */
  async _handleJobUpdate(job, data) {
    try {
      const updateType = data.update_type;

      // Update job count for new jobs
      if (updateType === UPDATE_TYPES.CREATED) {
        await this._updateMetricCount('jobCount');
        
        // Add to recent jobs if we have fewer than 5
        if (this.jobs.length < 5) {
          this.jobs.unshift(job);
          if (this.jobs.length > 5) {
            this.jobs.pop();
          }
          eventHub.emit(DASHBOARD_EVENTS.JOB_UPDATED, this.jobs);
        }
      } 
      // Update existing job in list
      else if (updateType === UPDATE_TYPES.UPDATED) {
        const index = this.jobs.findIndex(j => j.id === job.id);
        if (index !== -1) {
          this.jobs[index] = { ...this.jobs[index], ...job };
          eventHub.emit(DASHBOARD_EVENTS.JOB_UPDATED, this.jobs);
        }
      }
      // Remove deleted job from list
      else if (updateType === UPDATE_TYPES.DELETED) {
        const index = this.jobs.findIndex(j => j.id === job.id);
        if (index !== -1) {
          this.jobs.splice(index, 1);
          
          // Fetch a replacement to keep the list at 5 items
          const newJobs = await this._fetchRecentJobs();
          this.jobs = newJobs;
          
          eventHub.emit(DASHBOARD_EVENTS.JOB_UPDATED, this.jobs);
          await this._updateMetricCount('jobCount');
        }
      }
    } catch (error) {
      errorHandler.handleError(error, 'Error handling job update');
    }
  }

  /**
   * Handle analytics update event
   * @param {Object} analytics - Updated analytics data
   * @private
   */
  async _handleAnalyticsUpdate() {
    try {
      // Fetch updated analytics data
      const analyticsData = await this._fetchAnalyticsData();
      
      // Update state
      this.chartData = analyticsData.chartData;
      this.conversionMetrics = analyticsData.conversionMetrics;
      
      // Emit events for UI updates
      eventHub.emit(DASHBOARD_EVENTS.CHART_DATA_UPDATED, this.chartData);
      eventHub.emit(DASHBOARD_EVENTS.CONVERSION_UPDATED, this.conversionMetrics);
      
      if (this.options.showToasts) {
        toastService.show('Dashboard analytics updated', 'info');
      }
    } catch (error) {
      errorHandler.handleError(error, 'Error handling analytics update');
    }
  }

  /**
   * Handle platform status update event
   * @param {Object} platform - Updated platform status
   * @private
   */
  async _handlePlatformStatusUpdate(platform) {
    try {
      if (this.options.showToasts) {
        const status = platform.status || 'unknown';
        let toastType = 'info';
        
        // Determine toast type based on status
        if (status === 'operational') {
          toastType = 'success';
        } else if (status === 'degraded') {
          toastType = 'warning';
        } else if (status === 'outage') {
          toastType = 'error';
        }
        
        toastService.show(`${platform.name} status: ${status}`, toastType);
      }
      
      // Refresh platform-related data
      const analyticsData = await this._fetchAnalyticsData();
      this.chartData = analyticsData.chartData;
      eventHub.emit(DASHBOARD_EVENTS.CHART_DATA_UPDATED, this.chartData);
    } catch (error) {
      errorHandler.handleError(error, 'Error handling platform status update');
    }
  }

  /**
   * Update a specific metric count
   * @param {string} metricName - Name of the metric to update
   * @private
   */
  async _updateMetricCount(metricName) {
    try {
      let newValue = 0;
      
      switch (metricName) {
        case 'jobCount':
          newValue = await jobOpeningService.count();
          break;
        case 'campaignCount':
          newValue = await campaignService.count();
          break;
        case 'candidateCount':
          newValue = await candidateService.count();
          break;
        case 'segmentCount':
          newValue = await segmentService.count();
          break;
        default:
          return;
      }
      
      // Update the metric
      this.metrics[metricName] = newValue;
      
      // Emit metrics updated event
      eventHub.emit(DASHBOARD_EVENTS.METRICS_UPDATED, this.metrics);
    } catch (error) {
      errorHandler.handleError(error, `Error updating ${metricName}`);
    }
  }

  /**
   * Destroy the dashboard service
   * Clean up event listeners and timers
   */
  destroy() {
    // Clear auto-refresh timer
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
    
    // Clean up event listeners
    this.cleanupFunctions.forEach(cleanup => cleanup());
    this.cleanupFunctions = [];
    
    console.log('Dashboard service destroyed');
  }
}

// Create singleton instance
const realTimeDashboard = new RealTimeDashboard();

export { realTimeDashboard };