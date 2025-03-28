/**
 * MagnetoCursor - KPI Metrics Panel Component
 * 
 * Displays key performance indicators for campaign analytics in a grid layout.
 * Shows core metrics like impressions, clicks, conversions, CTR, CPC, etc.
 */

export class KpiMetricsPanel {
  /**
   * Initialize the KPI metrics panel component
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      columns: 4, // Number of columns in desktop view
      showTrends: true, // Show trend indicators
      compareWithPrevious: true, // Compare with previous period
      metrics: [
        'impressions',
        'clicks',
        'conversions',
        'ctr',
        'cpc',
        'cpa',
        'spend',
        'revenue',
        'roi'
      ],
      ...options
    };
    
    // State
    this.data = null;
    this.isLoading = false;
    
    // Define metrics formats and icons
    this.metricDefinitions = {
      impressions: {
        label: 'Impressions',
        format: 'number',
        icon: 'fa-eye'
      },
      clicks: {
        label: 'Clicks',
        format: 'number',
        icon: 'fa-mouse-pointer'
      },
      conversions: {
        label: 'Conversions',
        format: 'number',
        icon: 'fa-check-circle'
      },
      ctr: {
        label: 'Click-Through Rate',
        format: 'percent',
        icon: 'fa-percentage'
      },
      cpc: {
        label: 'Cost per Click',
        format: 'currency',
        icon: 'fa-hand-pointer'
      },
      cpa: {
        label: 'Cost per Acquisition',
        format: 'currency',
        icon: 'fa-shopping-cart'
      },
      spend: {
        label: 'Total Spend',
        format: 'currency',
        icon: 'fa-dollar-sign'
      },
      revenue: {
        label: 'Total Revenue',
        format: 'currency',
        icon: 'fa-coins'
      },
      roi: {
        label: 'ROI',
        format: 'percent',
        icon: 'fa-chart-line'
      }
    };
    
    // Initialize component
    this.initialize();
  }
  
  /**
   * Initialize the component
   */
  initialize() {
    // Add styles
    this._addStyles();
    
    // Create initial loading state
    this._renderLoadingState();
  }
  
  /**
   * Add component styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('kpi-metrics-panel-styles')) {
      const style = document.createElement('style');
      style.id = 'kpi-metrics-panel-styles';
      style.textContent = `
        .kpi-metrics-container {
          display: grid;
          grid-template-columns: repeat(1, 1fr);
          gap: 1rem;
          width: 100%;
        }
        
        @media (min-width: 576px) {
          .kpi-metrics-container {
            grid-template-columns: repeat(2, 1fr);
          }
        }
        
        @media (min-width: 768px) {
          .kpi-metrics-container {
            grid-template-columns: repeat(3, 1fr);
          }
        }
        
        @media (min-width: 992px) {
          .kpi-metrics-container {
            grid-template-columns: repeat(4, 1fr);
          }
        }
        
        .kpi-metric-card {
          background-color: var(--card-bg, white);
          border-radius: 0.25rem;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
          border: 1px solid var(--card-border-color, #eee);
          transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .kpi-metric-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .dark-mode .kpi-metric-card {
          background-color: var(--card-bg, #343a40);
          border-color: var(--card-border-color, #495057);
        }
        
        .kpi-metric-header {
          display: flex;
          align-items: center;
          margin-bottom: 0.5rem;
        }
        
        .kpi-metric-icon {
          margin-right: 0.5rem;
          color: var(--icon-color, #6c757d);
          width: 18px;
          text-align: center;
        }
        
        .dark-mode .kpi-metric-icon {
          color: var(--icon-color, #adb5bd);
        }
        
        .kpi-metric-label {
          font-size: 0.875rem;
          color: var(--text-color-secondary, #6c757d);
          flex: 1;
        }
        
        .dark-mode .kpi-metric-label {
          color: var(--text-color-secondary, #adb5bd);
        }
        
        .kpi-metric-value {
          font-size: 1.5rem;
          font-weight: 600;
          margin: 0.25rem 0;
          color: var(--text-color, #333);
        }
        
        .dark-mode .kpi-metric-value {
          color: var(--text-color, #f8f9fa);
        }
        
        .kpi-metric-trend {
          font-size: 0.75rem;
          display: flex;
          align-items: center;
        }
        
        .trend-positive {
          color: var(--success-color, #28a745);
        }
        
        .trend-negative {
          color: var(--danger-color, #dc3545);
        }
        
        .trend-neutral {
          color: var(--text-color-secondary, #6c757d);
        }
        
        .kpi-metric-trend-icon {
          margin-right: 0.25rem;
        }
        
        .kpi-metric-trend-value {
          font-weight: 500;
        }
        
        .kpi-metric-trend-period {
          color: var(--text-color-secondary, #6c757d);
          margin-left: 0.25rem;
          font-size: 0.7rem;
        }
        
        .loading-placeholder {
          border-radius: 0.25rem;
          background: linear-gradient(90deg, 
            var(--placeholder-start, #f3f3f3) 0%, 
            var(--placeholder-end, #e3e3e3) 50%, 
            var(--placeholder-start, #f3f3f3) 100%);
          background-size: 200% 100%;
          animation: shimmer 1.5s infinite;
        }
        
        .dark-mode .loading-placeholder {
          --placeholder-start: #3a3a3a;
          --placeholder-end: #2a2a2a;
        }
        
        @keyframes shimmer {
          0% {
            background-position: 200% 0;
          }
          100% {
            background-position: -200% 0;
          }
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Render loading state
   * @private
   */
  _renderLoadingState() {
    const container = document.createElement('div');
    container.className = 'kpi-metrics-container';
    
    // Create placeholder cards for each metric
    for (let i = 0; i < this.options.metrics.length; i++) {
      const card = document.createElement('div');
      card.className = 'kpi-metric-card';
      
      // Header placeholder
      const header = document.createElement('div');
      header.className = 'kpi-metric-header';
      
      const iconPlaceholder = document.createElement('div');
      iconPlaceholder.className = 'kpi-metric-icon loading-placeholder';
      iconPlaceholder.style.width = '18px';
      iconPlaceholder.style.height = '18px';
      header.appendChild(iconPlaceholder);
      
      const labelPlaceholder = document.createElement('div');
      labelPlaceholder.className = 'kpi-metric-label loading-placeholder';
      labelPlaceholder.style.width = '80%';
      labelPlaceholder.style.height = '14px';
      header.appendChild(labelPlaceholder);
      
      card.appendChild(header);
      
      // Value placeholder
      const valuePlaceholder = document.createElement('div');
      valuePlaceholder.className = 'kpi-metric-value loading-placeholder';
      valuePlaceholder.style.width = '60%';
      valuePlaceholder.style.height = '24px';
      card.appendChild(valuePlaceholder);
      
      // Trend placeholder
      const trendPlaceholder = document.createElement('div');
      trendPlaceholder.className = 'kpi-metric-trend loading-placeholder';
      trendPlaceholder.style.width = '70%';
      trendPlaceholder.style.height = '12px';
      card.appendChild(trendPlaceholder);
      
      container.appendChild(card);
    }
    
    // Replace container content
    this.container.innerHTML = '';
    this.container.appendChild(container);
  }
  
  /**
   * Update panel with new data
   * @param {Object} data - KPI metrics data
   */
  updateData(data) {
    // Store data
    this.data = data;
    
    // Render metrics
    this._renderMetrics(data);
  }
  
  /**
   * Render metrics cards
   * @param {Object} data - KPI metrics data
   * @private
   */
  _renderMetrics(data) {
    // Create container
    const container = document.createElement('div');
    container.className = 'kpi-metrics-container';
    
    // Add dark mode class if enabled
    if (this.options.darkMode) {
      container.classList.add('dark-mode');
    }
    
    // Get available metrics from options
    const metricsToShow = this.options.metrics;
    
    // Create a card for each metric
    metricsToShow.forEach(metricId => {
      // Skip if metric data not available
      if (!data[metricId] && data[metricId] !== 0) {
        return;
      }
      
      // Get metric definition
      const metricDef = this.metricDefinitions[metricId] || {
        label: metricId,
        format: 'number',
        icon: 'fa-chart-bar'
      };
      
      // Get current and previous values
      const currentValue = data[metricId];
      const previousValue = data[`previous_${metricId}`];
      
      // Create card
      const card = document.createElement('div');
      card.className = 'kpi-metric-card';
      
      // Create header with icon and label
      const header = document.createElement('div');
      header.className = 'kpi-metric-header';
      
      const icon = document.createElement('i');
      icon.className = `fas ${metricDef.icon} kpi-metric-icon`;
      header.appendChild(icon);
      
      const label = document.createElement('div');
      label.className = 'kpi-metric-label';
      label.textContent = metricDef.label;
      header.appendChild(label);
      
      card.appendChild(header);
      
      // Create value
      const value = document.createElement('div');
      value.className = 'kpi-metric-value';
      value.textContent = this._formatValue(currentValue, metricDef.format);
      card.appendChild(value);
      
      // Create trend if enabled and previous data available
      if (this.options.showTrends && previousValue !== undefined && this.options.compareWithPrevious) {
        const trend = document.createElement('div');
        trend.className = 'kpi-metric-trend';
        
        // Calculate percentage change
        const change = this._calculateChange(currentValue, previousValue);
        
        // Determine if positive or negative trend (higher is better, except for cost metrics)
        const isPositive = (metricId === 'cpc' || metricId === 'cpa') 
          ? change < 0 
          : change > 0;
        
        // Determine CSS class based on trend direction
        const trendClass = change === 0 
          ? 'trend-neutral' 
          : (isPositive ? 'trend-positive' : 'trend-negative');
        
        trend.classList.add(trendClass);
        
        // Add trend icon
        const trendIcon = document.createElement('i');
        trendIcon.className = `fas ${change === 0 ? 'fa-minus' : (isPositive ? 'fa-arrow-up' : 'fa-arrow-down')} kpi-metric-trend-icon`;
        trend.appendChild(trendIcon);
        
        // Add trend percentage
        const trendValue = document.createElement('span');
        trendValue.className = 'kpi-metric-trend-value';
        trendValue.textContent = `${Math.abs(change).toFixed(1)}%`;
        trend.appendChild(trendValue);
        
        // Add period label
        const trendPeriod = document.createElement('span');
        trendPeriod.className = 'kpi-metric-trend-period';
        trendPeriod.textContent = 'vs. previous period';
        trend.appendChild(trendPeriod);
        
        card.appendChild(trend);
      }
      
      container.appendChild(card);
    });
    
    // Replace container content
    this.container.innerHTML = '';
    this.container.appendChild(container);
  }
  
  /**
   * Format a value for display
   * @param {number} value - Value to format
   * @param {string} format - Format type
   * @returns {string} - Formatted value
   * @private
   */
  _formatValue(value, format) {
    if (value === undefined || value === null) {
      return 'N/A';
    }
    
    switch (format) {
      case 'percent':
        return `${value.toFixed(2)}%`;
      case 'currency':
        return `$${this._formatNumber(value)}`;
      case 'number':
      default:
        return this._formatNumber(value);
    }
  }
  
  /**
   * Format a number with thousand separators and abbreviations
   * @param {number} value - Number to format
   * @returns {string} - Formatted number
   * @private
   */
  _formatNumber(value) {
    // Use abbreviations for large numbers
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    
    // Add thousand separators
    return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  
  /**
   * Calculate percentage change between current and previous values
   * @param {number} current - Current value
   * @param {number} previous - Previous value
   * @returns {number} - Percentage change
   * @private
   */
  _calculateChange(current, previous) {
    if (previous === 0) {
      return current > 0 ? 100 : 0;
    }
    
    return ((current - previous) / Math.abs(previous)) * 100;
  }
  
  /**
   * Toggle dark mode
   * @param {boolean} darkMode - Enable dark mode
   */
  setDarkMode(darkMode) {
    this.options.darkMode = darkMode;
    
    // Update container if data available
    if (this.data) {
      this._renderMetrics(this.data);
    }
  }
  
  /**
   * Set metrics to display
   * @param {Array} metrics - Array of metric IDs
   */
  setMetrics(metrics) {
    this.options.metrics = metrics;
    
    // Update container if data available
    if (this.data) {
      this._renderMetrics(this.data);
    } else {
      this._renderLoadingState();
    }
  }
  
  /**
   * Set comparison option
   * @param {boolean} compare - Whether to compare with previous period
   */
  setCompareWithPrevious(compare) {
    this.options.compareWithPrevious = compare;
    
    // Update container if data available
    if (this.data) {
      this._renderMetrics(this.data);
    }
  }
  
  /**
   * Clean up component
   */
  destroy() {
    // Clear container
    this.container.innerHTML = '';
  }
}
