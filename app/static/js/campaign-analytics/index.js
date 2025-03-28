/**
 * MagnetoCursor - Campaign Analytics Module
 * 
 * This module provides a comprehensive set of components for visualizing 
 * cross-platform campaign performance metrics and analytics.
 */

// Main components
export { CampaignDashboard } from './campaign-dashboard.js';
export { TimeSeriesChart } from './time-series-chart.js';
export { PlatformComparisonChart } from './platform-comparison-chart.js';
export { RoiVisualization } from './roi-visualization.js';
export { KpiMetricsPanel } from './kpi-metrics-panel.js';
export { CampaignPerformanceTable } from './campaign-performance-table.js';
export { CampaignBreakdownChart } from './campaign-breakdown-chart.js';

// Constants and enums
export const MetricType = {
  IMPRESSIONS: 'impressions',
  CLICKS: 'clicks',
  CONVERSIONS: 'conversions',
  CTR: 'ctr',
  CPC: 'cpc',
  CPA: 'cpa',
  SPEND: 'spend',
  REVENUE: 'revenue',
  ROI: 'roi'
};

export const BreakdownType = {
  PLATFORM: 'platform',
  AD_TYPE: 'ad_type',
  PLACEMENT: 'placement',
  DEVICE: 'device'
};

export const VisualizationType = {
  BUBBLE: 'bubble',
  SCATTER: 'scatter',
  COLUMN: 'column',
  LINE: 'line',
  BAR: 'bar'
};

export const TimeRange = {
  LAST_7_DAYS: {
    label: 'Last 7 Days',
    days: 7
  },
  LAST_30_DAYS: {
    label: 'Last 30 Days',
    days: 30
  },
  LAST_90_DAYS: {
    label: 'Last 90 Days',
    days: 90
  },
  YEAR_TO_DATE: {
    label: 'Year to Date',
    days: 'ytd'
  },
  CUSTOM: {
    label: 'Custom Range',
    days: 'custom'
  }
};

// Configuration presets
export const DashboardPresets = {
  STANDARD: {
    showTimeSeriesChart: true,
    showPlatformComparison: true,
    showRoiVisualization: true,
    showKpiMetrics: true,
    showPerformanceTable: true,
    showBreakdownChart: true,
    darkMode: false,
    refreshInterval: 0
  },
  PERFORMANCE_FOCUSED: {
    showTimeSeriesChart: true,
    showPlatformComparison: true,
    showRoiVisualization: true,
    showKpiMetrics: true,
    showPerformanceTable: true,
    showBreakdownChart: false,
    darkMode: false,
    refreshInterval: 60000 // 1 minute
  },
  ROI_FOCUSED: {
    showTimeSeriesChart: false,
    showPlatformComparison: false,
    showRoiVisualization: true,
    showKpiMetrics: true,
    showPerformanceTable: true,
    showBreakdownChart: true,
    darkMode: false,
    refreshInterval: 0
  },
  DARK_MODE: {
    showTimeSeriesChart: true,
    showPlatformComparison: true,
    showRoiVisualization: true,
    showKpiMetrics: true,
    showPerformanceTable: true,
    showBreakdownChart: true,
    darkMode: true,
    refreshInterval: 0
  }
};

/**
 * Create and initialize a campaign analytics dashboard
 * @param {string} containerId - ID of the container element
 * @param {Object} options - Dashboard configuration options
 * @returns {CampaignDashboard} - Dashboard instance
 */
export function createDashboard(containerId, options = {}) {
  return new CampaignDashboard(containerId, options);
}

/**
 * Initialize dashboard with a preset configuration
 * @param {string} containerId - ID of the container element 
 * @param {string} presetName - Name of the preset configuration
 * @param {Object} overrides - Option overrides for the preset
 * @returns {CampaignDashboard} - Dashboard instance
 */
export function createDashboardWithPreset(containerId, presetName = 'STANDARD', overrides = {}) {
  const preset = DashboardPresets[presetName] || DashboardPresets.STANDARD;
  return createDashboard(containerId, { ...preset, ...overrides });
}

/**
 * Generate default date range (last 30 days)
 * @returns {Object} - Start and end dates
 */
export function getDefaultDateRange() {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 30);
  
  return { start, end };
}

/**
 * Format a date for display
 * @param {Date} date - Date to format
 * @param {string} format - Format type ('short', 'medium', 'long')
 * @returns {string} - Formatted date string
 */
export function formatDate(date, format = 'medium') {
  if (!date) return '';
  
  const dateObj = date instanceof Date ? date : new Date(date);
  
  try {
    switch (format) {
      case 'short':
        return dateObj.toLocaleDateString(undefined, { 
          month: 'numeric', 
          day: 'numeric'
        });
      case 'long':
        return dateObj.toLocaleDateString(undefined, { 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric'
        });
      case 'medium':
      default:
        return dateObj.toLocaleDateString(undefined, { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric'
        });
    }
  } catch (e) {
    // Fallback to ISO format
    return dateObj.toISOString().split('T')[0];
  }
}

/**
 * Format a value according to its metric type
 * @param {number} value - Value to format
 * @param {string} metricType - Type of metric
 * @param {Object} options - Formatting options
 * @returns {string} - Formatted value
 */
export function formatMetricValue(value, metricType, options = {}) {
  if (value === undefined || value === null) {
    return 'N/A';
  }
  
  const defaults = {
    decimal: 2,
    abbreviate: true,
    currency: '$'
  };
  
  const config = { ...defaults, ...options };
  
  switch (metricType) {
    case MetricType.IMPRESSIONS:
    case MetricType.CLICKS:
    case MetricType.CONVERSIONS:
      return formatNumber(value, { decimal: 0, abbreviate: config.abbreviate });
    case MetricType.CTR:
    case MetricType.ROI:
      return `${formatNumber(value, { decimal: config.decimal, abbreviate: false })}%`;
    case MetricType.CPC:
    case MetricType.CPA:
    case MetricType.SPEND:
    case MetricType.REVENUE:
      return `${config.currency}${formatNumber(value, { decimal: config.decimal, abbreviate: config.abbreviate })}`;
    default:
      return formatNumber(value, { decimal: config.decimal, abbreviate: config.abbreviate });
  }
}

/**
 * Format a number with abbreviations (K, M, B)
 * @param {number} value - Number to format
 * @param {Object} options - Formatting options
 * @returns {string} - Formatted number
 */
export function formatNumber(value, options = {}) {
  const defaults = {
    decimal: 2,
    abbreviate: true
  };
  
  const config = { ...defaults, ...options };
  
  if (config.abbreviate) {
    if (value >= 1000000000) {
      return `${(value / 1000000000).toFixed(config.decimal)}B`;
    } else if (value >= 1000000) {
      return `${(value / 1000000).toFixed(config.decimal)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(config.decimal)}K`;
    }
  }
  
  return value.toFixed(config.decimal);
}
