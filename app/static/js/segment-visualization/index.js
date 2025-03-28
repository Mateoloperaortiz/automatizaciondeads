/**
 * MagnetoCursor - Segment Visualization Module
 * 
 * This module provides a comprehensive set of components for visualizing 
 * machine learning-driven audience segments and their performance metrics.
 */

// Main dashboard component
export { SegmentDashboard } from './segment-dashboard.js';

// Cluster visualization components
export { ClusterVisualization } from './cluster-visualization.js';
export { SegmentDistributionChart } from './segment-distribution-chart.js';
export { CandidateProfileMap } from './candidate-profile-map.js';
export { SegmentComparisonTool } from './segment-comparison-tool.js';
export { PlatformPerformanceChart } from './platform-performance-chart.js';

// Constants and enums
export const ViewMode = {
  MODE_2D: '2d',
  MODE_3D: '3d'
};

export const ChartType = {
  PIE: 'pie',
  BAR: 'bar'
};

export const MapStyle = {
  LIGHT: 'light',
  DARK: 'dark',
  STREETS: 'streets',
  SATELLITE: 'satellite'
};

export const PerformanceMetric = {
  IMPRESSIONS: 'impressions',
  CLICKS: 'clicks',
  CONVERSIONS: 'conversions',
  CTR: 'ctr',
  CPC: 'cpc',
  ROI: 'roi'
};

// Configuration presets
export const DashboardPresets = {
  STANDARD: {
    showDistribution: true,
    showPerformance: true,
    showMap: true,
    darkMode: false,
    refreshInterval: 0
  },
  PERFORMANCE_FOCUSED: {
    showDistribution: true,
    showPerformance: true,
    showMap: false,
    darkMode: false,
    refreshInterval: 60000 // 1 minute
  },
  GEOGRAPHIC_FOCUSED: {
    showDistribution: true,
    showPerformance: false,
    showMap: true,
    darkMode: false,
    refreshInterval: 0
  },
  DARK_MODE: {
    showDistribution: true,
    showPerformance: true,
    showMap: true,
    darkMode: true,
    refreshInterval: 0
  }
};

/**
 * Create and initialize a segment dashboard
 * @param {string} containerId - ID of the container element
 * @param {Object} options - Dashboard configuration options
 * @returns {SegmentDashboard} - Dashboard instance
 */
export function createDashboard(containerId, options = {}) {
  return new SegmentDashboard(containerId, options);
}

/**
 * Initialize dashboard with a preset configuration
 * @param {string} containerId - ID of the container element 
 * @param {string} presetName - Name of the preset configuration
 * @param {Object} overrides - Option overrides for the preset
 * @returns {SegmentDashboard} - Dashboard instance
 */
export function createDashboardWithPreset(containerId, presetName = 'STANDARD', overrides = {}) {
  const preset = DashboardPresets[presetName] || DashboardPresets.STANDARD;
  return createDashboard(containerId, { ...preset, ...overrides });
}
