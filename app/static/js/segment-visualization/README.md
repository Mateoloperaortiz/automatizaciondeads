# Machine Learning Segment Visualization Interface

A comprehensive visualization interface for ML-driven audience segmentation, providing interactive data exploration and performance analytics.

## Overview

This package provides a complete solution for visualizing machine learning audience segments with an emphasis on:

- Interactive cluster visualization (2D/3D)
- Segment performance metrics across advertising platforms
- Geographic distribution mapping of segment members
- Comparative segment analysis
- Distribution and composition analysis

Designed for seamless integration with the MagnetoCursor platform's segmentation backend, these visualization components bring machine learning insights to life with engaging, interactive displays that help understand audience segments.

## Installation

### 1. Add Required Dependencies

Ensure the following external dependencies are available in your HTML:

```html
<!-- Required CSS -->
<link rel="stylesheet" href="https://api.mapbox.com/mapbox-gl-js/v2.12.0/mapbox-gl.css">

<!-- Core Libraries (if not importing via modules) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
<script src="https://api.mapbox.com/mapbox-gl-js/v2.12.0/mapbox-gl.js"></script>
<script src="https://d3js.org/d3.v7.min.js"></script>
```

### 2. Import Visualization Components

```javascript
// Import all components
import * as SegmentViz from './static/js/segment-visualization/index.js';

// Or import specific components
import { 
  SegmentDashboard, 
  ClusterVisualization, 
  SegmentDistributionChart 
} from './static/js/segment-visualization/index.js';
```

### 3. Create Dashboard Container

```html
<div id="segment-dashboard" style="width: 100%; height: 800px;"></div>
```

### 4. Initialize Dashboard

```javascript
// Simple initialization with default options
const dashboard = SegmentViz.createDashboard('segment-dashboard');

// Or use a preset configuration
const dashboard = SegmentViz.createDashboardWithPreset('segment-dashboard', 'DARK_MODE');
```

## Core Components

The visualization interface consists of the following core components:

### 1. SegmentDashboard

The main container component that integrates all visualizations into a cohesive dashboard. Manages data flow, layout, and interactions between components.

### 2. ClusterVisualization

Renders interactive 2D and 3D visualizations of the ML clusters, allowing users to explore the spatial relationships between segments.

**Features:**
- Toggle between 2D and 3D views
- Highlight specific segments
- Zoom and rotate (3D only)
- Fullscreen mode

### 3. SegmentDistributionChart

Visualizes the distribution of candidates across segments with both pie and bar chart options.

**Features:**
- Toggle between pie and bar chart views
- Hover for detailed information
- Click to select/filter segments

### 4. CandidateProfileMap

Displays geographic distribution of candidates within segments using a map interface.

**Features:**
- Heatmap visualization
- Individual candidate markers
- Multiple map styles (light, dark, streets, satellite)
- Segment filtering

### 5. SegmentComparisonTool

Enables direct comparison between two segments to analyze differences in metrics and characteristics.

**Features:**
- Side-by-side metric comparison
- Radar chart for characteristic comparison
- Similarity score calculation

### 6. PlatformPerformanceChart

Shows performance metrics for segments across different advertising platforms (Meta, Google, Twitter).

**Features:**
- Multiple metric visualizations (impressions, clicks, CTR, CPC, etc.)
- Platform comparison
- Interactive tooltips with detailed data

## API Reference

### SegmentDashboard

```javascript
/**
 * Create a new dashboard
 * @param {string} containerId - DOM element ID for the dashboard
 * @param {Object} options - Configuration options
 */
const dashboard = new SegmentDashboard(containerId, {
  // Options
  refreshInterval: 0, // Auto-refresh interval in ms (0 = disabled)
  initialSegmentId: null, // Initial segment to display
  showDistribution: true, // Show segment size distribution
  showPerformance: true, // Show performance metrics
  showMap: true, // Show candidate geographic distribution
  darkMode: false // Dark mode
});

// Select a segment
dashboard.selectSegment(segmentId);

// Clean up dashboard
dashboard.destroy();
```

### ClusterVisualization

```javascript
/**
 * Create a cluster visualization
 * @param {HTMLElement} container - DOM element for the visualization
 * @param {Object} options - Configuration options
 */
const clusterViz = new ClusterVisualization(container, {
  darkMode: false,
  transitionDuration: 750,
  pointSize: 6,
  highlightSize: 8,
  colors: ['#4e79a7', '#f28e2c', '#e15759', /*...*/]
});

// Update with new data
clusterViz.updateData(clusterData);

// Set 2D or 3D view
clusterViz.setViewMode('2d'); // or '3d'

// Highlight a specific cluster
clusterViz.highlightCluster(clusterIndex);
```

For full API documentation of all components, refer to the JSDoc comments in the source code.

## Example Usage

### Basic Dashboard

```javascript
import { createDashboard } from './static/js/segment-visualization/index.js';

document.addEventListener('DOMContentLoaded', () => {
  // Initialize dashboard
  const dashboard = createDashboard('segment-dashboard');
});
```

### Custom Integration

```javascript
import { 
  ClusterVisualization, 
  SegmentDistributionChart,
  PlatformPerformanceChart
} from './static/js/segment-visualization/index.js';

// Initialize custom dashboard layout
function initializeCustomDashboard() {
  // Initialize cluster visualization
  const clusterViz = new ClusterVisualization(
    document.getElementById('cluster-container'),
    { darkMode: true }
  );
  
  // Initialize distribution chart
  const distributionChart = new SegmentDistributionChart(
    document.getElementById('distribution-container'),
    { initialType: 'bar' }
  );
  
  // Initialize performance chart
  const performanceChart = new PlatformPerformanceChart(
    document.getElementById('performance-container'),
    { initialMetric: 'ctr' }
  );
  
  // Fetch segment data
  fetchSegmentData().then(data => {
    // Update visualizations
    clusterViz.updateData(data.clusters);
    distributionChart.updateData(data.segments);
    performanceChart.updateData(data.segmentId);
  });
}
```

For more examples, check out the `examples` directory.

## Configuration Presets

For convenience, the visualization system provides predefined configuration presets:

```javascript
import { createDashboardWithPreset } from './static/js/segment-visualization/index.js';

// Available presets:
// - STANDARD: Balanced configuration with all visualizations
// - PERFORMANCE_FOCUSED: Emphasizes platform performance metrics
// - GEOGRAPHIC_FOCUSED: Emphasizes geographic distribution
// - DARK_MODE: Dark theme with all visualizations

// Create a dashboard with the DARK_MODE preset
const dashboard = createDashboardWithPreset('segment-dashboard', 'DARK_MODE');

// Create a dashboard with a preset and override specific options
const dashboard = createDashboardWithPreset('segment-dashboard', 'STANDARD', {
  refreshInterval: 60000, // Override refresh interval to 1 minute
  showMap: false // Disable map
});
```

## Browser Compatibility

- **Supported Browsers**: Chrome (latest), Firefox (latest), Safari (latest), Edge (latest)
- **Minimum Requirements**: WebGL support for 3D visualization
- **Responsive Design**: Supports desktop and tablet viewports (min width: 768px)

## Mapbox Token

The geographic visualization requires a Mapbox access token for the map features. You can either:

1. Set it globally: 
```javascript
mapboxgl.accessToken = 'your_mapbox_token';
```

2. Pass it in the CandidateProfileMap options:
```javascript
new CandidateProfileMap(element, {
  mapboxToken: 'your_mapbox_token'
});
```

For testing and development, a placeholder token is included, but you should replace it with your own for production use.

## Troubleshooting

### Common Issues

1. **Visualizations not appearing**: Ensure the container element has a defined height.
2. **3D view not working**: Check that WebGL is supported by the browser.
3. **Map not loading**: Verify that a valid Mapbox token is provided.
4. **Charts showing "No data available"**: Ensure data is properly formatted and contains the expected properties.

## Contributing

We welcome contributions to improve the visualization interface:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please follow the existing code style and include JSDoc comments for any new methods or components.

## License

This package is part of the MagnetoCursor platform and is subject to the MagnetoCursor license agreement.

## Credits

Developed by the MagnetoCursor team. Leverages the following open-source libraries:

- Chart.js for 2D charting
- Three.js for 3D visualization
- Mapbox GL JS for geographic mapping
- D3.js for data transformations and color scales
