# Campaign Analytics Dashboard

A comprehensive dashboard for visualizing and analyzing cross-platform advertising campaign performance metrics.

## Overview

The Campaign Analytics Dashboard provides a unified view of campaign performance across multiple advertising platforms (Meta, Google, Twitter), enabling data-driven decision making through interactive visualizations and real-time analytics.

Key features include:
- Time-series performance visualization
- Cross-platform performance comparison
- ROI analysis and visualization
- Key performance indicators
- Campaign breakdown by various dimensions
- Detailed performance data tables

![Campaign Analytics Dashboard](https://via.placeholder.com/1200x800?text=Campaign+Analytics+Dashboard)

## Components

### Core Components

1. **CampaignDashboard**
   - Main container component that orchestrates all visualizations
   - Manages data flow, state, and interactions between components
   - Handles date range selection, campaign selection, and data refresh

2. **TimeSeriesChart**
   - Visualizes campaign metrics over time
   - Supports multiple platforms in a single chart
   - Interactive tooltips and zoom capabilities
   - Multiple metric options (impressions, clicks, conversions, etc.)

3. **PlatformComparisonChart**
   - Directly compares performance across platforms
   - Bar chart or radar chart visualization options
   - Interactive and customizable

4. **RoiVisualization**
   - Visualizes ROI data in multiple formats (bubble, scatter, column)
   - Shows relationship between spend, revenue, and conversions
   - Summary metrics and visualization options

5. **KpiMetricsPanel**
   - Displays key performance indicators in a grid of cards
   - Shows trends compared to previous period
   - Visual indicators for positive/negative trends

6. **CampaignPerformanceTable**
   - Detailed tabular data with sorting and filtering
   - Export capabilities
   - Customizable columns

7. **CampaignBreakdownChart**
   - Breaks down campaign performance by various dimensions
   - Platform, ad type, placement, device, etc.
   - Multiple visualization options

## Usage

### Basic Usage

```javascript
import { createDashboard } from '../static/js/campaign-analytics/index.js';

// Create dashboard with default options
const dashboard = createDashboard('dashboard-container');
```

### Using Configuration Presets

```javascript
import { createDashboardWithPreset } from '../static/js/campaign-analytics/index.js';

// Create dashboard with a preset configuration
const dashboard = createDashboardWithPreset('dashboard-container', 'PERFORMANCE_FOCUSED');
```

### Custom Configuration

```javascript
import { createDashboard } from '../static/js/campaign-analytics/index.js';

// Create dashboard with custom options
const dashboard = createDashboard('dashboard-container', {
  refreshInterval: 60000, // Auto-refresh every minute
  showTimeSeriesChart: true,
  showPlatformComparison: true,
  showRoiVisualization: true,
  showKpiMetrics: true,
  showPerformanceTable: true,
  showBreakdownChart: false,
  darkMode: true,
  initialCampaignId: 123,
  initialDateRange: {
    start: new Date('2025-01-01'),
    end: new Date('2025-03-31')
  }
});
```

### Dashboard Methods

```javascript
// Select a different campaign
dashboard.selectCampaign(campaignId);

// Change date range
dashboard.setDateRange(startDate, endDate);

// Manually refresh data
dashboard.loadData();

// Export dashboard data
dashboard.exportData();

// Clean up dashboard
dashboard.destroy();
```

## Configuration Options

### Dashboard Presets

The following presets are available for quick dashboard configuration:

- **STANDARD**: Balanced configuration with all visualizations
- **PERFORMANCE_FOCUSED**: Emphasis on performance metrics with auto-refresh
- **ROI_FOCUSED**: Focused on ROI and financial metrics
- **DARK_MODE**: Dark theme with all visualizations

### Dashboard Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `refreshInterval` | Number | 0 | Auto-refresh interval in ms (0 = disabled) |
| `initialCampaignId` | Number | null | Initial campaign to display |
| `initialDateRange` | Object | Last 30 days | Initial date range for data |
| `showTimeSeriesChart` | Boolean | true | Show time series chart |
| `showPlatformComparison` | Boolean | true | Show platform comparison chart |
| `showRoiVisualization` | Boolean | true | Show ROI visualization |
| `showKpiMetrics` | Boolean | true | Show KPI metrics panel |
| `showPerformanceTable` | Boolean | true | Show performance data table |
| `showBreakdownChart` | Boolean | true | Show campaign breakdown chart |
| `darkMode` | Boolean | false | Use dark color theme |

## Data Format

### Campaign Data

```javascript
{
  id: 123,
  name: "Q1 Product Launch",
  status: "active",
  dateRange: {
    start: "2025-01-01T00:00:00Z",
    end: "2025-03-31T23:59:59Z"
  },
  platforms: ["meta", "google", "twitter"],
  metrics: {
    impressions: 1245678,
    clicks: 45678,
    conversions: 2345,
    ctr: 3.67,
    cpc: 0.75,
    cpa: 14.50,
    spend: 34000,
    revenue: 102000,
    roi: 200
  }
}
```

### Time Series Data

```javascript
{
  campaignId: 123,
  dateRange: {
    start: "2025-01-01T00:00:00Z",
    end: "2025-03-31T23:59:59Z"
  },
  platforms: ["meta", "google", "twitter"],
  data: {
    meta: {
      impressions: [
        { x: "2025-01-01", y: 12345 },
        { x: "2025-01-02", y: 13456 },
        // ...
      ],
      clicks: [
        { x: "2025-01-01", y: 456 },
        { x: "2025-01-02", y: 567 },
        // ...
      ],
      // Other metrics...
    },
    google: {
      // Similar structure...
    },
    twitter: {
      // Similar structure...
    }
  }
}
```

### ROI Data

```javascript
{
  campaignId: 123,
  dateRange: {
    start: "2025-01-01T00:00:00Z",
    end: "2025-03-31T23:59:59Z"
  },
  platforms: ["meta", "google", "twitter"],
  overall: {
    spend: 34000,
    revenue: 102000,
    conversions: 2345,
    roi: 200
  },
  platformData: {
    meta: {
      spend: 15000,
      revenue: 45000,
      conversions: 1200,
      roi: 200
    },
    google: {
      spend: 12000,
      revenue: 40000,
      conversions: 800,
      roi: 233.33
    },
    twitter: {
      spend: 7000,
      revenue: 17000,
      conversions: 345,
      roi: 142.86
    }
  }
}
```

## API Reference

### Helper Functions

```javascript
// Create dashboard with options
createDashboard(containerId, options);

// Create dashboard with preset
createDashboardWithPreset(containerId, presetName, overrides);

// Get default date range (last 30 days)
getDefaultDateRange();

// Format date for display
formatDate(date, format);

// Format metric value
formatMetricValue(value, metricType, options);

// Format number with abbreviations
formatNumber(value, options);
```

### Constants

```javascript
// Metric types
MetricType.IMPRESSIONS
MetricType.CLICKS
MetricType.CONVERSIONS
MetricType.CTR
MetricType.CPC
MetricType.CPA
MetricType.SPEND
MetricType.REVENUE
MetricType.ROI

// Breakdown types
BreakdownType.PLATFORM
BreakdownType.AD_TYPE
BreakdownType.PLACEMENT
BreakdownType.DEVICE

// Visualization types
VisualizationType.BUBBLE
VisualizationType.SCATTER
VisualizationType.COLUMN
VisualizationType.LINE
VisualizationType.BAR

// Time ranges
TimeRange.LAST_7_DAYS
TimeRange.LAST_30_DAYS
TimeRange.LAST_90_DAYS
TimeRange.YEAR_TO_DATE
TimeRange.CUSTOM
```

## Examples

See the `examples` directory for complete working examples:

- `campaign-dashboard-demo.html` - Fully interactive demo with all features

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Dependencies

- [Chart.js](https://www.chartjs.org/) - For all visualizations
- [Font Awesome](https://fontawesome.com/) - For icons

## Integration with API Framework

This dashboard integrates with the MagnetoCursor API Framework to fetch cross-platform campaign data. It consumes the data from the following endpoints:

- `/api/campaigns` - List of campaigns
- `/api/campaigns/:id` - Campaign details
- `/api/campaigns/:id/timeseries` - Time series data
- `/api/campaigns/:id/platforms` - Platform comparison data
- `/api/campaigns/:id/roi` - ROI analysis data

## License

This dashboard is part of the MagnetoCursor platform and is subject to the MagnetoCursor license agreement.
