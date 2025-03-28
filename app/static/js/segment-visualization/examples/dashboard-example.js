/**
 * MagnetoCursor - Segment Visualization Dashboard Example
 * 
 * This example demonstrates how to integrate the ML segment visualization
 * dashboard into an existing application.
 */

import { 
  createDashboard, 
  createDashboardWithPreset, 
  DashboardPresets,
  ViewMode,
  ChartType,
  MapStyle,
  PerformanceMetric
} from '../index.js';

/**
 * Example 1: Basic Dashboard Initialization
 * 
 * This is the simplest way to initialize the dashboard with default settings.
 * The dashboard will be rendered in the container with ID 'segment-dashboard'.
 */
function initializeBasicDashboard() {
  // Get container element
  const container = document.getElementById('segment-dashboard');
  if (!container) {
    console.error('Dashboard container not found');
    return;
  }
  
  // Clear container
  container.innerHTML = '<h3>Loading dashboard...</h3>';
  
  // Create dashboard with default settings
  const dashboard = createDashboard('segment-dashboard');
  
  // Log dashboard instance for debugging
  console.log('Dashboard initialized:', dashboard);
  
  return dashboard;
}

/**
 * Example 2: Dashboard with Preset Configuration
 * 
 * This example demonstrates how to initialize the dashboard with a preset configuration.
 * The 'DARK_MODE' preset enables dark mode and includes all visualization components.
 */
function initializeDarkModeDashboard() {
  // Create dashboard with dark mode preset
  const dashboard = createDashboardWithPreset('segment-dashboard', 'DARK_MODE');
  
  return dashboard;
}

/**
 * Example 3: Custom Dashboard Configuration
 * 
 * This example demonstrates how to initialize the dashboard with custom settings.
 */
function initializeCustomDashboard() {
  // Create dashboard with custom settings
  const dashboard = createDashboard('segment-dashboard', {
    refreshInterval: 30000, // 30 seconds
    showDistribution: true,
    showPerformance: true,
    showMap: true,
    darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches, // Use system preference
    initialSegmentId: 1 // Initial segment to display
  });
  
  return dashboard;
}

/**
 * Example 4: Advanced Dashboard with Event Handling
 * 
 * This example demonstrates how to initialize the dashboard with event handling
 * for external controls and integration with other application components.
 */
function initializeAdvancedDashboard() {
  // Create dashboard with performance-focused preset and overrides
  const dashboard = createDashboardWithPreset('segment-dashboard', 'PERFORMANCE_FOCUSED', {
    refreshInterval: 120000 // 2 minutes
  });
  
  // Add event listeners to external controls
  const darkModeToggle = document.getElementById('dark-mode-toggle');
  if (darkModeToggle) {
    // Check current state
    darkModeToggle.checked = dashboard.options.darkMode;
    
    // Add event listener
    darkModeToggle.addEventListener('change', (e) => {
      // Get dashboard container
      const container = document.getElementById('segment-dashboard');
      if (!container) return;
      
      // Toggle dark mode
      if (e.target.checked) {
        container.classList.add('dark-mode');
      } else {
        container.classList.remove('dark-mode');
      }
      
      // Destroy and recreate dashboard with new settings
      dashboard.destroy();
      createDashboard('segment-dashboard', {
        ...dashboard.options,
        darkMode: e.target.checked
      });
    });
  }
  
  // Add event listener for metric selector
  const metricSelector = document.getElementById('external-metric-selector');
  if (metricSelector) {
    metricSelector.addEventListener('change', (e) => {
      // Get selected metric
      const metric = e.target.value;
      
      // Get dashboard and performance chart
      if (dashboard.visualizations.performanceChart) {
        // Update metric
        dashboard.visualizations.performanceChart.setMetric(metric);
      }
    });
  }
  
  // Add event listener for segment creation
  const createSegmentButton = document.getElementById('create-segment-button');
  if (createSegmentButton) {
    createSegmentButton.addEventListener('click', () => {
      // Show segment creation modal
      const modal = document.getElementById('create-segment-modal');
      if (modal) {
        modal.style.display = 'block';
      }
    });
  }
  
  return dashboard;
}

/**
 * Example 5: Initialize Dashboard in an Existing Application
 * 
 * This example demonstrates how to integrate the dashboard into an existing application
 * with routing, tab management, and data fetching.
 */
class SegmentationPage {
  constructor() {
    this.dashboard = null;
    this.activeTab = 'visualization';
    this.segmentId = null;
    
    // Initialize page
    this.initialize();
  }
  
  async initialize() {
    // Set up tab switching
    this.setupTabs();
    
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    this.segmentId = urlParams.get('segment_id');
    
    // Initialize dashboard when visualization tab is active
    if (this.activeTab === 'visualization') {
      this.initializeDashboard();
    }
  }
  
  setupTabs() {
    // Get tab elements
    const tabs = document.querySelectorAll('.segment-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Add click handlers
    tabs.forEach(tab => {
      tab.addEventListener('click', (e) => {
        // Get tab ID
        const tabId = e.target.getAttribute('data-tab');
        
        // Update active tab
        this.activeTab = tabId;
        
        // Update UI
        tabs.forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        
        // Show/hide tab content
        tabContents.forEach(content => {
          if (content.getAttribute('data-tab') === tabId) {
            content.classList.add('active');
            
            // Initialize dashboard if visualization tab
            if (tabId === 'visualization' && !this.dashboard) {
              this.initializeDashboard();
            }
          } else {
            content.classList.remove('active');
          }
        });
      });
    });
    
    // Set initial active tab
    const activeTab = document.querySelector('.segment-tab[data-tab="visualization"]');
    if (activeTab) {
      activeTab.click();
    }
  }
  
  initializeDashboard() {
    // Create dashboard with custom settings
    this.dashboard = createDashboard('segment-visualization', {
      refreshInterval: 0,
      showDistribution: true,
      showPerformance: true,
      showMap: true,
      darkMode: document.body.classList.contains('dark-theme'),
      initialSegmentId: this.segmentId ? parseInt(this.segmentId) : null
    });
    
    // Add window resize handler
    window.addEventListener('resize', this.handleResize.bind(this));
    
    // Add segment change handler
    window.addEventListener('segment-change', this.handleSegmentChange.bind(this));
  }
  
  handleResize() {
    // Resize dashboard
    if (this.dashboard) {
      // Resize after short delay to avoid too many updates
      clearTimeout(this.resizeTimer);
      this.resizeTimer = setTimeout(() => {
        const dashboardContainer = document.getElementById('segment-visualization');
        if (dashboardContainer) {
          // Trigger resize on all visualizations
          for (const key in this.dashboard.visualizations) {
            if (this.dashboard.visualizations[key] && typeof this.dashboard.visualizations[key].resize === 'function') {
              this.dashboard.visualizations[key].resize();
            }
          }
        }
      }, 250);
    }
  }
  
  handleSegmentChange(event) {
    // Update segment ID
    this.segmentId = event.detail.segmentId;
    
    // Update URL
    const url = new URL(window.location.href);
    url.searchParams.set('segment_id', this.segmentId);
    window.history.replaceState({}, '', url.toString());
    
    // Update dashboard
    if (this.dashboard) {
      this.dashboard.selectSegment(this.segmentId);
    }
  }
  
  destroy() {
    // Clean up dashboard
    if (this.dashboard) {
      this.dashboard.destroy();
      this.dashboard = null;
    }
    
    // Remove event listeners
    window.removeEventListener('resize', this.handleResize);
    window.removeEventListener('segment-change', this.handleSegmentChange);
  }
}

// Initialize the example based on the container available
document.addEventListener('DOMContentLoaded', () => {
  // Check for dashboard container
  const dashboardContainer = document.getElementById('segment-dashboard');
  if (dashboardContainer) {
    // Determine which example to run based on URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const example = urlParams.get('example') || 'basic';
    
    // Initialize appropriate example
    switch (example) {
      case 'dark':
        initializeDarkModeDashboard();
        break;
      case 'custom':
        initializeCustomDashboard();
        break;
      case 'advanced':
        initializeAdvancedDashboard();
        break;
      case 'app':
        new SegmentationPage();
        break;
      case 'basic':
      default:
        initializeBasicDashboard();
        break;
    }
  }
});

// Export examples for external use
export {
  initializeBasicDashboard,
  initializeDarkModeDashboard,
  initializeCustomDashboard,
  initializeAdvancedDashboard,
  SegmentationPage
};
