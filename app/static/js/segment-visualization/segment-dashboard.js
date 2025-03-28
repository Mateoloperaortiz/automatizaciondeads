/**
 * MagnetoCursor - Segment Visualization Dashboard
 * 
 * This component provides an interactive dashboard for visualizing
 * audience segments from machine learning clustering.
 */

import { segmentService } from '../services/segment-service.js';
import { ClusterVisualization } from './cluster-visualization.js';
import { SegmentDistributionChart } from './segment-distribution-chart.js';
import { CandidateProfileMap } from './candidate-profile-map.js';
import { SegmentComparisonTool } from './segment-comparison-tool.js';
import { PlatformPerformanceChart } from './platform-performance-chart.js';

export class SegmentDashboard {
  /**
   * Initialize the segment visualization dashboard
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
      initialSegmentId: null, // Initial segment to display
      showDistribution: true, // Show segment size distribution
      showPerformance: true, // Show performance metrics
      showMap: true, // Show candidate geographic distribution
      darkMode: false, // Dark mode
      ...options
    };
    
    // State
    this.segments = [];
    this.selectedSegment = null;
    this.isLoading = false;
    this.refreshTimer = null;
    this.visualizations = {};
    
    // Initialize dashboard
    this.initialize();
  }
  
  /**
   * Initialize the dashboard
   */
  async initialize() {
    // Create dashboard structure
    this.createDashboardStructure();
    
    // Initialize components
    this.initializeComponents();
    
    // Load initial data
    await this.loadData();
    
    // Set up auto-refresh if enabled
    if (this.options.refreshInterval > 0) {
      this.refreshTimer = setInterval(() => {
        this.loadData();
      }, this.options.refreshInterval);
    }
    
    // Set initial segment if provided
    if (this.options.initialSegmentId && this.segments.length > 0) {
      const segment = this.segments.find(s => s.id === this.options.initialSegmentId);
      if (segment) {
        this.selectSegment(segment.id);
      }
    } else if (this.segments.length > 0) {
      // Select first segment by default
      this.selectSegment(this.segments[0].id);
    }
  }
  
  /**
   * Create the dashboard structure
   */
  createDashboardStructure() {
    // Clear container
    this.container.innerHTML = '';
    
    // Set container class
    this.container.classList.add('segment-dashboard');
    if (this.options.darkMode) {
      this.container.classList.add('dark-mode');
    }
    
    // Create dashboard layout
    this.container.innerHTML = `
      <div class="dashboard-header">
        <h2>Audience Segment Dashboard</h2>
        <div class="dashboard-controls">
          <select id="segment-selector" class="segment-selector">
            <option value="">Loading segments...</option>
          </select>
          <button id="refresh-btn" class="refresh-btn">
            <i class="fas fa-sync-alt"></i> Refresh
          </button>
          <button id="run-segmentation-btn" class="action-btn">
            Run Segmentation
          </button>
        </div>
      </div>
      
      <div class="dashboard-content">
        <div class="visualization-container">
          <div class="main-visualization">
            <div class="panel">
              <div class="panel-header">
                <h3>Cluster Visualization</h3>
                <div class="panel-controls">
                  <button id="2d-view-btn" class="view-btn active">2D</button>
                  <button id="3d-view-btn" class="view-btn">3D</button>
                  <button id="fullscreen-viz-btn" class="icon-btn">
                    <i class="fas fa-expand"></i>
                  </button>
                </div>
              </div>
              <div id="cluster-visualization" class="visualization-canvas"></div>
              <div class="legend" id="cluster-legend"></div>
            </div>
          </div>
          
          <div class="dashboard-grid">
            <!-- Segment size distribution -->
            <div class="panel" id="distribution-panel">
              <div class="panel-header">
                <h3>Segment Distribution</h3>
                <div class="panel-controls">
                  <button id="chart-type-btn" class="icon-btn">
                    <i class="fas fa-chart-pie"></i>
                  </button>
                </div>
              </div>
              <div id="segment-distribution" class="chart-container"></div>
            </div>
            
            <!-- Segment characteristics -->
            <div class="panel">
              <div class="panel-header">
                <h3>Segment Characteristics</h3>
              </div>
              <div id="segment-details" class="detail-container">
                <div class="placeholder">Select a segment to view details</div>
              </div>
            </div>
            
            <!-- Performance metrics by platform -->
            <div class="panel" id="performance-panel">
              <div class="panel-header">
                <h3>Platform Performance</h3>
                <div class="panel-controls">
                  <select id="metric-selector" class="metric-selector">
                    <option value="impressions">Impressions</option>
                    <option value="clicks">Clicks</option>
                    <option value="conversions">Conversions</option>
                    <option value="ctr">CTR</option>
                    <option value="cpc">CPC</option>
                    <option value="roi">ROI</option>
                  </select>
                </div>
              </div>
              <div id="platform-performance" class="chart-container"></div>
            </div>
            
            <!-- Candidate geographic distribution -->
            <div class="panel" id="map-panel">
              <div class="panel-header">
                <h3>Geographic Distribution</h3>
              </div>
              <div id="candidate-map" class="map-container"></div>
            </div>
          </div>
        </div>
        
        <div class="dashboard-sidebar">
          <!-- Segment details sidebar -->
          <div class="panel">
            <div class="panel-header">
              <h3>Selected Segment</h3>
            </div>
            <div id="selected-segment-details" class="sidebar-content">
              <div class="placeholder">No segment selected</div>
            </div>
          </div>
          
          <!-- Segment comparison tool -->
          <div class="panel">
            <div class="panel-header">
              <h3>Compare Segments</h3>
            </div>
            <div id="segment-comparison" class="sidebar-content">
              <select id="comparison-segment-1" class="full-width-select">
                <option value="">Select first segment</option>
              </select>
              <select id="comparison-segment-2" class="full-width-select mt-2">
                <option value="">Select second segment</option>
              </select>
              <button id="compare-btn" class="full-width-btn mt-2">
                Compare
              </button>
              <div id="comparison-results" class="comparison-results mt-2"></div>
            </div>
          </div>
          
          <!-- Actions panel -->
          <div class="panel">
            <div class="panel-header">
              <h3>Segment Actions</h3>
            </div>
            <div class="sidebar-content">
              <button id="create-campaign-btn" class="full-width-btn">
                Create Campaign for Segment
              </button>
              <button id="export-segment-btn" class="full-width-btn mt-2">
                Export Segment Data
              </button>
              <button id="customize-segment-btn" class="full-width-btn mt-2">
                Customize Segment
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
    
    // Add dashboard stylesheet
    if (!document.getElementById('segment-dashboard-styles')) {
      const style = document.createElement('style');
      style.id = 'segment-dashboard-styles';
      style.textContent = `
        .segment-dashboard {
          display: flex;
          flex-direction: column;
          font-family: var(--font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif);
          color: var(--text-color, #333);
          background: var(--bg-color, #f8f9fa);
          height: 100%;
          min-height: 600px;
        }
        
        .segment-dashboard.dark-mode {
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
        
        .dashboard-controls {
          display: flex;
          gap: 0.5rem;
        }
        
        .dashboard-content {
          display: flex;
          flex: 1;
          overflow: hidden;
        }
        
        .visualization-container {
          flex: 1;
          padding: 1rem;
          overflow-y: auto;
        }
        
        .dashboard-sidebar {
          width: 300px;
          padding: 1rem;
          border-left: 1px solid var(--panel-border, #dee2e6);
          overflow-y: auto;
        }
        
        .dashboard-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1rem;
          margin-top: 1rem;
        }
        
        .panel {
          background: var(--panel-bg, white);
          border-radius: 0.25rem;
          border: 1px solid var(--panel-border, #dee2e6);
          box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
          margin-bottom: 1rem;
          overflow: hidden;
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
        
        .main-visualization {
          margin-bottom: 1rem;
        }
        
        .visualization-canvas {
          height: 400px;
          background: var(--panel-bg, white);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .chart-container, .map-container {
          height: 250px;
          padding: 1rem;
        }
        
        .detail-container, .sidebar-content {
          padding: 1rem;
        }
        
        .legend {
          padding: 0.5rem 1rem;
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
        }
        
        .placeholder {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #6c757d;
          font-style: italic;
        }
        
        .segment-selector, .metric-selector {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--panel-border, #dee2e6);
          border-radius: 0.25rem;
          background-color: var(--panel-bg, white);
          color: var(--text-color, #333);
        }
        
        .refresh-btn, .action-btn, .view-btn, .icon-btn {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--panel-border, #dee2e6);
          border-radius: 0.25rem;
          background-color: var(--panel-bg, white);
          color: var(--text-color, #333);
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .action-btn {
          background-color: var(--highlight-color, #0d6efd);
          color: white;
          border-color: var(--highlight-color, #0d6efd);
        }
        
        .icon-btn {
          padding: 0.375rem 0.5rem;
        }
        
        .view-btn.active {
          background-color: var(--highlight-color, #0d6efd);
          color: white;
          border-color: var(--highlight-color, #0d6efd);
        }
        
        .full-width-select, .full-width-btn {
          width: 100%;
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--panel-border, #dee2e6);
          border-radius: 0.25rem;
          background-color: var(--panel-bg, white);
          color: var(--text-color, #333);
        }
        
        .full-width-btn {
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .mt-2 {
          margin-top: 0.5rem;
        }
        
        .comparison-results {
          border: 1px solid var(--panel-border, #dee2e6);
          border-radius: 0.25rem;
          padding: 0.5rem;
          min-height: 100px;
        }
        
        @media (max-width: 1200px) {
          .dashboard-content {
            flex-direction: column;
          }
          
          .dashboard-sidebar {
            width: 100%;
            border-left: none;
            border-top: 1px solid var(--panel-border, #dee2e6);
          }
        }
        
        @media (max-width: 768px) {
          .dashboard-grid {
            grid-template-columns: 1fr;
          }
        }
      `;
      
      document.head.appendChild(style);
    }
    
    // Set up event listeners
    this.setupEventListeners();
  }
  
  /**
   * Set up dashboard event listeners
   */
  setupEventListeners() {
    // Segment selector change
    const segmentSelector = document.getElementById('segment-selector');
    if (segmentSelector) {
      segmentSelector.addEventListener('change', (e) => {
        const segmentId = parseInt(e.target.value, 10);
        if (!isNaN(segmentId)) {
          this.selectSegment(segmentId);
        }
      });
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.loadData();
      });
    }
    
    // Run segmentation button
    const runSegmentationBtn = document.getElementById('run-segmentation-btn');
    if (runSegmentationBtn) {
      runSegmentationBtn.addEventListener('click', () => {
        this.runSegmentation();
      });
    }
    
    // View buttons (2D/3D)
    const view2dBtn = document.getElementById('2d-view-btn');
    const view3dBtn = document.getElementById('3d-view-btn');
    
    if (view2dBtn && view3dBtn) {
      view2dBtn.addEventListener('click', () => {
        view2dBtn.classList.add('active');
        view3dBtn.classList.remove('active');
        if (this.visualizations.clusterViz) {
          this.visualizations.clusterViz.setViewMode('2d');
        }
      });
      
      view3dBtn.addEventListener('click', () => {
        view3dBtn.classList.add('active');
        view2dBtn.classList.remove('active');
        if (this.visualizations.clusterViz) {
          this.visualizations.clusterViz.setViewMode('3d');
        }
      });
    }
    
    // Fullscreen button
    const fullscreenBtn = document.getElementById('fullscreen-viz-btn');
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', () => {
        const vizContainer = document.getElementById('cluster-visualization');
        if (vizContainer) {
          if (document.fullscreenElement) {
            document.exitFullscreen();
          } else {
            vizContainer.requestFullscreen();
          }
        }
      });
    }
    
    // Chart type toggle
    const chartTypeBtn = document.getElementById('chart-type-btn');
    if (chartTypeBtn) {
      chartTypeBtn.addEventListener('click', () => {
        if (this.visualizations.distributionChart) {
          const currentType = this.visualizations.distributionChart.getChartType();
          const newType = currentType === 'pie' ? 'bar' : 'pie';
          this.visualizations.distributionChart.setChartType(newType);
          
          // Update button icon
          const icon = chartTypeBtn.querySelector('i');
          if (icon) {
            icon.className = newType === 'pie' ? 'fas fa-chart-pie' : 'fas fa-chart-bar';
          }
        }
      });
    }
    
    // Metric selector
    const metricSelector = document.getElementById('metric-selector');
    if (metricSelector) {
      metricSelector.addEventListener('change', (e) => {
        const metric = e.target.value;
        if (this.visualizations.performanceChart) {
          this.visualizations.performanceChart.setMetric(metric);
        }
      });
    }
    
    // Compare button
    const compareBtn = document.getElementById('compare-btn');
    if (compareBtn) {
      compareBtn.addEventListener('click', () => {
        const segment1 = document.getElementById('comparison-segment-1').value;
        const segment2 = document.getElementById('comparison-segment-2').value;
        
        if (segment1 && segment2 && segment1 !== segment2) {
          this.compareSegments(segment1, segment2);
        }
      });
    }
    
    // Create campaign button
    const createCampaignBtn = document.getElementById('create-campaign-btn');
    if (createCampaignBtn) {
      createCampaignBtn.addEventListener('click', () => {
        if (this.selectedSegment) {
          window.location.href = `/campaigns/create?segment_id=${this.selectedSegment.id}`;
        }
      });
    }
    
    // Export segment button
    const exportSegmentBtn = document.getElementById('export-segment-btn');
    if (exportSegmentBtn) {
      exportSegmentBtn.addEventListener('click', () => {
        if (this.selectedSegment) {
          this.exportSegmentData(this.selectedSegment.id);
        }
      });
    }
    
    // Customize segment button
    const customizeSegmentBtn = document.getElementById('customize-segment-btn');
    if (customizeSegmentBtn) {
      customizeSegmentBtn.addEventListener('click', () => {
        if (this.selectedSegment) {
          this.openSegmentCustomizer(this.selectedSegment.id);
        }
      });
    }
  }
  
  /**
   * Initialize visualization components
   */
  initializeComponents() {
    // Initialize cluster visualization
    const clusterContainer = document.getElementById('cluster-visualization');
    if (clusterContainer) {
      this.visualizations.clusterViz = new ClusterVisualization(clusterContainer, {
        darkMode: this.options.darkMode
      });
    }
    
    // Initialize segment distribution chart
    if (this.options.showDistribution) {
      const distributionContainer = document.getElementById('segment-distribution');
      if (distributionContainer) {
        this.visualizations.distributionChart = new SegmentDistributionChart(distributionContainer, {
          darkMode: this.options.darkMode,
          initialType: 'pie'
        });
      }
    } else {
      const distributionPanel = document.getElementById('distribution-panel');
      if (distributionPanel) {
        distributionPanel.style.display = 'none';
      }
    }
    
    // Initialize performance chart
    if (this.options.showPerformance) {
      const performanceContainer = document.getElementById('platform-performance');
      if (performanceContainer) {
        this.visualizations.performanceChart = new PlatformPerformanceChart(performanceContainer, {
          darkMode: this.options.darkMode,
          initialMetric: 'impressions'
        });
      }
    } else {
      const performancePanel = document.getElementById('performance-panel');
      if (performancePanel) {
        performancePanel.style.display = 'none';
      }
    }
    
    // Initialize candidate map
    if (this.options.showMap) {
      const mapContainer = document.getElementById('candidate-map');
      if (mapContainer) {
        this.visualizations.candidateMap = new CandidateProfileMap(mapContainer, {
          darkMode: this.options.darkMode
        });
      }
    } else {
      const mapPanel = document.getElementById('map-panel');
      if (mapPanel) {
        mapPanel.style.display = 'none';
      }
    }
    
    // Initialize segment comparison tool
    const comparisonContainer = document.getElementById('segment-comparison');
    if (comparisonContainer) {
      this.visualizations.comparisonTool = new SegmentComparisonTool(comparisonContainer, {
        darkMode: this.options.darkMode
      });
    }
  }
  
  /**
   * Load dashboard data
   */
  async loadData() {
    try {
      this.isLoading = true;
      this.updateLoadingState(true);
      
      // Get segments
      const segmentsResponse = await segmentService.getSegments();
      if (segmentsResponse && segmentsResponse.success) {
        this.segments = segmentsResponse.data;
        this.updateSegmentSelector();
      }
      
      // Get visualization data
      const visualizationResponse = await segmentService.getVisualization();
      if (visualizationResponse && visualizationResponse.success) {
        this.updateVisualizations(visualizationResponse.data);
      }
      
      this.isLoading = false;
      this.updateLoadingState(false);
    } catch (error) {
      console.error('Error loading segment data:', error);
      this.isLoading = false;
      this.updateLoadingState(false);
      
      // Show error toast
      if (typeof showToast === 'function') {
        showToast('Error loading segment data. Please try again.', 'error');
      }
    }
  }
  
  /**
   * Update segment selector dropdown
   */
  updateSegmentSelector() {
    const segmentSelector = document.getElementById('segment-selector');
    const comparisonSelector1 = document.getElementById('comparison-segment-1');
    const comparisonSelector2 = document.getElementById('comparison-segment-2');
    
    if (segmentSelector) {
      // Clear existing options
      segmentSelector.innerHTML = '';
      
      if (this.segments.length === 0) {
        // No segments available
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'No segments available';
        segmentSelector.appendChild(option);
        
        // Disable selector
        segmentSelector.disabled = true;
      } else {
        // Add segments to selector
        this.segments.forEach(segment => {
          const option = document.createElement('option');
          option.value = segment.id;
          option.textContent = `${segment.name} (${segment.candidate_count || 0} candidates)`;
          segmentSelector.appendChild(option);
        });
        
        // Enable selector
        segmentSelector.disabled = false;
        
        // Update comparison selectors
        if (comparisonSelector1 && comparisonSelector2) {
          comparisonSelector1.innerHTML = '';
          comparisonSelector2.innerHTML = '';
          
          // Add placeholder
          const placeholder1 = document.createElement('option');
          placeholder1.value = '';
          placeholder1.textContent = 'Select first segment';
          comparisonSelector1.appendChild(placeholder1);
          
          const placeholder2 = document.createElement('option');
          placeholder2.value = '';
          placeholder2.textContent = 'Select second segment';
          comparisonSelector2.appendChild(placeholder2);
          
          // Add segments to selectors
          this.segments.forEach(segment => {
            const option1 = document.createElement('option');
            option1.value = segment.id;
            option1.textContent = segment.name;
            comparisonSelector1.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = segment.id;
            option2.textContent = segment.name;
            comparisonSelector2.appendChild(option2);
          });
        }
      }
    }
  }
  
  /**
   * Update visualizations with new data
   * @param {Object} data - Visualization data
   */
  updateVisualizations(data) {
    // Update cluster visualization
    if (this.visualizations.clusterViz && data.clusters) {
      this.visualizations.clusterViz.updateData(data.clusters);
    }
    
    // Update distribution chart
    if (this.visualizations.distributionChart && this.segments) {
      this.visualizations.distributionChart.updateData(this.segments);
    }
    
    // Update cluster legend
    this.updateClusterLegend();
  }
  
  /**
   * Update cluster legend
   */
  updateClusterLegend() {
    const legendContainer = document.getElementById('cluster-legend');
    if (!legendContainer || !this.segments) return;
    
    // Clear existing legend
    legendContainer.innerHTML = '';
    
    // Create legend items
    this.segments.forEach((segment, index) => {
      const legendItem = document.createElement('div');
      legendItem.className = 'legend-item';
      
      const color = this.visualizations.clusterViz ? 
        this.visualizations.clusterViz.getColorForCluster(index) : 
        `hsl(${(index * 137) % 360}, 70%, 50%)`;
      
      legendItem.innerHTML = `
        <span class="legend-color" style="background-color: ${color}"></span>
        <span class="legend-label">${segment.name}</span>
      `;
      
      // Add click handler to highlight cluster
      legendItem.addEventListener('click', () => {
        if (this.visualizations.clusterViz) {
          this.visualizations.clusterViz.highlightCluster(index);
        }
        this.selectSegment(segment.id);
      });
      
      legendContainer.appendChild(legendItem);
    });
    
    // Add legend styles if not already added
    if (!document.getElementById('legend-styles')) {
      const style = document.createElement('style');
      style.id = 'legend-styles';
      style.textContent = `
        .legend-item {
          display: inline-flex;
          align-items: center;
          cursor: pointer;
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          transition: background-color 0.2s;
        }
        
        .legend-item:hover {
          background-color: rgba(0, 0, 0, 0.05);
        }
        
        .dark-mode .legend-item:hover {
          background-color: rgba(255, 255, 255, 0.05);
        }
        
        .legend-color {
          display: inline-block;
          width: 12px;
          height: 12px;
          border-radius: 50%;
          margin-right: 0.5rem;
        }
        
        .legend-label {
          font-size: 0.875rem;
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Select a segment and update displays
   * @param {number} segmentId - ID of segment to select
   */
  async selectSegment(segmentId) {
    try {
      // Find segment in loaded segments
      const segment = this.segments.find(s => s.id === segmentId);
      if (!segment) return;
      
      this.selectedSegment = segment;
      
      // Update selector value
      const segmentSelector = document.getElementById('segment-selector');
      if (segmentSelector) {
        segmentSelector.value = segmentId;
      }
      
      // Show loading state
      this.updateLoadingState(true, 'segment-details');
      
      // Get detailed segment data
      const response = await segmentService.getSegment(segmentId);
      if (response && response.success) {
        const detailedSegment = response.data;
        
        // Update segment details panel
        this.updateSegmentDetails(detailedSegment);
        
        // Update sidebar details
        this.updateSidebarDetails(detailedSegment);
        
        // Get segment candidates for map
        if (this.visualizations.candidateMap) {
          const candidatesResponse = await segmentService.getSegmentCandidates(segmentId);
          if (candidatesResponse && candidatesResponse.success) {
            this.visualizations.candidateMap.updateData(candidatesResponse.data, detailedSegment);
          }
        }
        
        // Update performance chart
        if (this.visualizations.performanceChart) {
          this.visualizations.performanceChart.updateData(segmentId);
        }
        
        // Highlight cluster in visualization
        if (this.visualizations.clusterViz) {
          const clusterIndex = this.segments.findIndex(s => s.id === segmentId);
          if (clusterIndex !== -1) {
            this.visualizations.clusterViz.highlightCluster(clusterIndex);
          }
        }
      }
      
      // Hide loading state
      this.updateLoadingState(false, 'segment-details');
    } catch (error) {
      console.error('Error selecting segment:', error);
      this.updateLoadingState(false, 'segment-details');
      
      // Show error toast
      if (typeof showToast === 'function') {
        showToast('Error loading segment details. Please try again.', 'error');
      }
    }
  }
  
  /**
   * Update segment details panel
   * @param {Object} segment - Segment data
   */
  updateSegmentDetails(segment) {
    const detailsContainer = document.getElementById('segment-details');
    if (!detailsContainer) return;
    
    // Format segment characteristics
    const characteristics = this.formatSegmentCharacteristics(segment);
    
    // Create HTML content
    detailsContainer.innerHTML = `
      <div class="segment-characteristics">
        <h4>${segment.name}</h4>
        <p class="segment-description">${segment.description || 'No description available.'}</p>
        
        <div class="characteristics-grid">
          ${characteristics.map(char => `
            <div class="characteristic-item">
              <div class="characteristic-label">${char.label}</div>
              <div class="characteristic-value">${char.value}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
    
    // Add characteristics styles if not already added
    if (!document.getElementById('characteristics-styles')) {
      const style = document.createElement('style');
      style.id = 'characteristics-styles';
      style.textContent = `
        .segment-characteristics {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .segment-description {
          margin: 0;
          color: var(--text-color-secondary, #6c757d);
        }
        
        .characteristics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 0.75rem;
          margin-top: 0.5rem;
        }
        
        .characteristic-item {
          background: var(--bg-color, #f8f9fa);
          border-radius: 0.25rem;
          padding: 0.75rem;
          border: 1px solid var(--panel-border, #dee2e6);
        }
        
        .characteristic-label {
          font-size: 0.75rem;
          color: var(--text-color-secondary, #6c757d);
          margin-bottom: 0.25rem;
        }
        
        .characteristic-value {
          font-size: 0.875rem;
          font-weight: 600;
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Format segment characteristics for display
   * @param {Object} segment - Segment data
   * @returns {Array<Object>} - Formatted characteristics
   */
  formatSegmentCharacteristics(segment) {
    const characteristics = [];
    
    // Add candidate count
    characteristics.push({
      label: 'Candidates',
      value: segment.candidate_count || '0'
    });
    
    // Add segment code
    if (segment.segment_code) {
      characteristics.push({
        label: 'Segment Code',
        value: segment.segment_code
      });
    }
    
    // Add creation date
    if (segment.created_at) {
      const date = new Date(segment.created_at);
      characteristics.push({
        label: 'Created',
        value: date.toLocaleDateString()
      });
    }
    
    // Add characteristics from criteria
    if (segment.criteria) {
      // Extract algorithm info
      if (segment.criteria.algorithm) {
        characteristics.push({
          label: 'Algorithm',
          value: segment.criteria.algorithm
        });
      }
      
      // Add cluster ID if available
      if (segment.criteria.cluster_id !== undefined) {
        characteristics.push({
          label: 'Cluster ID',
          value: segment.criteria.cluster_id
        });
      }
      
      // Add other criteria
      if (segment.criteria.demographics) {
        // Age range
        if (segment.criteria.demographics.age_range) {
          characteristics.push({
            label: 'Age Range',
            value: segment.criteria.demographics.age_range
          });
        }
        
        // Experience
        if (segment.criteria.demographics.experience) {
          characteristics.push({
            label: 'Experience',
            value: segment.criteria.demographics.experience
          });
        }
        
        // Locations
        if (segment.criteria.demographics.locations) {
          const locations = Array.isArray(segment.criteria.demographics.locations) ?
            segment.criteria.demographics.locations.join(', ') :
            segment.criteria.demographics.locations;
            
          characteristics.push({
            label: 'Locations',
            value: locations
          });
        }
      }
    }
    
    return characteristics;
  }
  
  /**
   * Update sidebar details
   * @param {Object} segment - Segment data
   */
  updateSidebarDetails(segment) {
    const sidebarContainer = document.getElementById('selected-segment-details');
    if (!sidebarContainer) return;
    
    // Create HTML content
    sidebarContainer.innerHTML = `
      <h4>${segment.name}</h4>
      <div class="segment-info">
        <div class="info-item">
          <span class="info-label">Candidates:</span>
          <span class="info-value">${segment.candidate_count || '0'}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Code:</span>
          <span class="info-value">${segment.segment_code || 'N/A'}</span>
        </div>
      </div>
      <div class="segment-description mt-2">
        ${segment.description || 'No description available.'}
      </div>
      
      <div class="segment-stats mt-2">
        <h5>Performance Summary</h5>
        <div class="stat-grid">
          <div class="stat-item">
            <div class="stat-value">0</div>
            <div class="stat-label">Campaigns</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">0%</div>
            <div class="stat-label">CTR</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">$0.00</div>
            <div class="stat-label">CPC</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">0%</div>
            <div class="stat-label">Conv. Rate</div>
          </div>
        </div>
      </div>
    `;
    
    // Add sidebar styles if not already added
    if (!document.getElementById('sidebar-styles')) {
      const style = document.createElement('style');
      style.id = 'sidebar-styles';
      style.textContent = `
        .segment-info {
          margin-top: 0.5rem;
        }
        
        .info-item {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.25rem;
        }
        
        .info-label {
          color: var(--text-color-secondary, #6c757d);
          font-size: 0.875rem;
        }
        
        .info-value {
          font-weight: 600;
          font-size: 0.875rem;
        }
        
        .segment-description {
          font-size: 0.875rem;
          line-height: 1.4;
          color: var(--text-color, #333);
        }
        
        .segment-stats h5 {
          font-size: 0.875rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
        }
        
        .stat-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 0.5rem;
        }
        
        .stat-item {
          padding: 0.5rem;
          border: 1px solid var(--panel-border, #dee2e6);
          border-radius: 0.25rem;
          text-align: center;
        }
        
        .stat-value {
          font-size: 1rem;
          font-weight: 600;
        }
        
        .stat-label {
          font-size: 0.75rem;
          color: var(--text-color-secondary, #6c757d);
          margin-top: 0.25rem;
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Run segmentation algorithm
   */
  async runSegmentation() {
    try {
      // Show loading state
      this.updateLoadingState(true, 'full-page');
      
      // Show progress toast
      if (typeof showToast === 'function') {
        showToast('Running segmentation algorithm. This may take a few moments...', 'info', 0);
      }
      
      // Call API to run segmentation
      const response = await segmentService.runSegmentation();
      
      // Hide loading state
      this.updateLoadingState(false, 'full-page');
      
      // Check response
      if (response && response.success) {
        // Show success toast
        if (typeof showToast === 'function') {
          showToast('Segmentation completed successfully!', 'success');
        }
        
        // Reload data
        await this.loadData();
      } else {
        // Show error toast
        if (typeof showToast === 'function') {
          showToast('Error running segmentation algorithm. Please try again.', 'error');
        }
      }
    } catch (error) {
      console.error('Error running segmentation:', error);
      this.updateLoadingState(false, 'full-page');
      
      // Show error toast
      if (typeof showToast === 'function') {
        showToast('Error running segmentation algorithm. Please try again.', 'error');
      }
    }
  }
  
  /**
   * Compare two segments
   * @param {number} segment1Id - First segment ID
   * @param {number} segment2Id - Second segment ID
   */
  async compareSegments(segment1Id, segment2Id) {
    if (!segment1Id || !segment2Id || segment1Id === segment2Id) {
      return;
    }
    
    try {
      // Show loading state in comparison results
      const resultsContainer = document.getElementById('comparison-results');
      if (resultsContainer) {
        resultsContainer.innerHTML = '<div class="loading-indicator">Loading comparison...</div>';
      }
      
      // Get comparison data
      const response = await segmentService.compareSegments([segment1Id, segment2Id]);
      
      if (response && response.success) {
        // Update comparison tool
        if (this.visualizations.comparisonTool) {
          this.visualizations.comparisonTool.displayComparison(response.data);
        } else if (resultsContainer) {
          // Fallback if comparison tool not initialized
          const segment1 = this.segments.find(s => s.id === parseInt(segment1Id));
          const segment2 = this.segments.find(s => s.id === parseInt(segment2Id));
          
          resultsContainer.innerHTML = `
            <div class="comparison-summary">
              <h5>Comparison Results</h5>
              <div class="comparison-row">
                <div class="comparison-label">Segments:</div>
                <div class="comparison-value">${segment1?.name || 'Unknown'} vs ${segment2?.name || 'Unknown'}</div>
              </div>
              <div class="comparison-row">
                <div class="comparison-label">Candidates:</div>
                <div class="comparison-value">${segment1?.candidate_count || '0'} / ${segment2?.candidate_count || '0'}</div>
              </div>
              <div class="comparison-row">
                <div class="comparison-label">Similarity:</div>
                <div class="comparison-value">${response.data.similarity || 'N/A'}</div>
              </div>
            </div>
          `;
        }
      } else {
        // Show error
        if (resultsContainer) {
          resultsContainer.innerHTML = '<div class="error-message">Error comparing segments. Please try again.</div>';
        }
      }
    } catch (error) {
      console.error('Error comparing segments:', error);
      
      // Show error in results container
      const resultsContainer = document.getElementById('comparison-results');
      if (resultsContainer) {
        resultsContainer.innerHTML = '<div class="error-message">Error comparing segments. Please try again.</div>';
      }
    }
  }
  
  /**
   * Export segment data
   * @param {number} segmentId - Segment ID to export
   */
  async exportSegmentData(segmentId) {
    try {
      // Get segment data
      const response = await segmentService.getSegmentCandidates(segmentId);
      
      if (response && response.success && response.data) {
        // Convert to CSV
        const candidates = response.data;
        const headers = candidates.length > 0 ? Object.keys(candidates[0]) : [];
        
        const csvContent = [
          headers.join(','),
          ...candidates.map(candidate => 
            headers.map(header => {
              const value = candidate[header];
              // Handle strings with commas by quoting them
              return typeof value === 'string' && value.includes(',') ? 
                `"${value}"` : 
                value;
            }).join(',')
          )
        ].join('\n');
        
        // Create download link
        const segment = this.segments.find(s => s.id === segmentId);
        const fileName = `segment_${segment ? segment.name.replace(/\s+/g, '_').toLowerCase() : segmentId}_${new Date().toISOString().split('T')[0]}.csv`;
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', fileName);
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Show success toast
        if (typeof showToast === 'function') {
          showToast(`Segment data exported successfully as ${fileName}`, 'success');
        }
      } else {
        // Show error toast
        if (typeof showToast === 'function') {
          showToast('Error exporting segment data. Please try again.', 'error');
        }
      }
    } catch (error) {
      console.error('Error exporting segment data:', error);
      
      // Show error toast
      if (typeof showToast === 'function') {
        showToast('Error exporting segment data. Please try again.', 'error');
      }
    }
  }
  
  /**
   * Open segment customizer
   * @param {number} segmentId - Segment ID to customize
   */
  openSegmentCustomizer(segmentId) {
    // Redirect to segment edit page or open modal
    window.location.href = `/segments/customize/${segmentId}`;
  }
  
  /**
   * Update loading state
   * @param {boolean} isLoading - Whether loading is in progress
   * @param {string} type - Type of loading state ('full-page', specific element ID)
   */
  updateLoadingState(isLoading, type = 'full-page') {
    if (type === 'full-page') {
      // Update refresh button
      const refreshBtn = document.getElementById('refresh-btn');
      if (refreshBtn) {
        const icon = refreshBtn.querySelector('i');
        if (icon) {
          if (isLoading) {
            icon.classList.add('fa-spin');
          } else {
            icon.classList.remove('fa-spin');
          }
        }
        
        refreshBtn.disabled = isLoading;
      }
      
      // Update run segmentation button
      const runBtn = document.getElementById('run-segmentation-btn');
      if (runBtn) {
        runBtn.disabled = isLoading;
      }
    } else {
      // Update specific container
      const container = document.getElementById(type);
      if (container) {
        if (isLoading) {
          container.classList.add('loading');
          
          // Add loading overlay if not exists
          if (!container.querySelector('.loading-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
              <div class="spinner"></div>
              <p>Loading...</p>
            `;
            
            container.appendChild(overlay);
          }
        } else {
          container.classList.remove('loading');
          
          // Remove loading overlay
          const overlay = container.querySelector('.loading-overlay');
          if (overlay) {
            overlay.remove();
          }
        }
      }
    }
    
    // Add loading styles if not already added
    if (!document.getElementById('loading-styles')) {
      const style = document.createElement('style');
      style.id = 'loading-styles';
      style.textContent = `
        .loading {
          position: relative;
        }
        
        .loading-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255, 255, 255, 0.7);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          z-index: 10;
        }
        
        .dark-mode .loading-overlay {
          background: rgba(33, 37, 41, 0.7);
        }
        
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid rgba(0, 0, 0, 0.1);
          border-top: 4px solid var(--highlight-color, #0d6efd);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .error-message {
          color: var(--danger, #dc3545);
          font-size: 0.875rem;
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Clean up dashboard
   */
  destroy() {
    // Clear auto-refresh timer
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
    
    // Destroy visualizations
    for (const key in this.visualizations) {
      if (this.visualizations[key] && typeof this.visualizations[key].destroy === 'function') {
        this.visualizations[key].destroy();
      }
    }
    
    // Clear container
    if (this.container) {
      this.container.innerHTML = '';
      this.container.classList.remove('segment-dashboard', 'dark-mode');
    }
  }
}
