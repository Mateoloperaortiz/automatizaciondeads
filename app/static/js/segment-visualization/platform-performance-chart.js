/**
 * MagnetoCursor - Platform Performance Chart
 * 
 * Visualizes segment performance metrics across different
 * social media advertising platforms (Meta, Google, Twitter).
 */

export class PlatformPerformanceChart {
  /**
   * Initialize the platform performance chart
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      initialMetric: 'impressions', // 'impressions', 'clicks', 'conversions', 'ctr', 'cpc', 'roi'
      platforms: ['meta', 'google', 'twitter'],
      platformNames: {
        meta: 'Meta',
        google: 'Google',
        twitter: 'Twitter'
      },
      platformColors: {
        meta: '#4267B2',
        google: '#DB4437',
        twitter: '#1DA1F2'
      },
      animations: {
        duration: 750
      },
      ...options
    };
    
    // State
    this.metric = this.options.initialMetric;
    this.chart = null;
    this.data = null;
    this.segmentId = null;
    this.initialized = false;
    
    // Initialize component
    this.initialize();
  }
  
  /**
   * Initialize the chart
   */
  async initialize() {
    // Add placeholder
    this.container.innerHTML = `
      <div class="chart-placeholder">
        <div class="spinner"></div>
        <div class="placeholder-text">Loading chart...</div>
      </div>
    `;
    
    // Add styles
    this._addStyles();
    
    // Load Chart.js
    await this._loadChartJs();
    
    // Create chart canvas
    this.container.innerHTML = `<canvas id="platform-performance-canvas"></canvas>`;
    
    // Initialize chart
    this._initializeChart();
    
    this.initialized = true;
    
    // Render initial data if available
    if (this.segmentId) {
      this.updateData(this.segmentId);
    }
  }
  
  /**
   * Add component styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('platform-performance-chart-styles')) {
      const style = document.createElement('style');
      style.id = 'platform-performance-chart-styles';
      style.textContent = `
        .chart-placeholder {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          width: 100%;
        }
        
        .placeholder-text {
          margin-top: 1rem;
          font-size: 0.875rem;
          color: var(--text-color-secondary, #6c757d);
        }
        
        .spinner {
          width: 30px;
          height: 30px;
          border: 3px solid rgba(0, 0, 0, 0.1);
          border-top: 3px solid var(--highlight-color, #0d6efd);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        .dark-mode .spinner {
          border-color: rgba(255, 255, 255, 0.1);
          border-top-color: var(--highlight-color, #0d6efd);
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Load Chart.js library
   * @returns {Promise} - Promise that resolves when library is loaded
   * @private
   */
  async _loadChartJs() {
    // Check if Chart.js is already loaded
    if (window.Chart) {
      return Promise.resolve();
    }
    
    // Load Chart.js
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js';
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }
  
  /**
   * Initialize Chart.js instance
   * @private
   */
  _initializeChart() {
    const canvas = document.getElementById('platform-performance-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Create chart
    this.chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: this.options.platforms.map(platform => this.options.platformNames[platform] || platform),
        datasets: [{
          data: [],
          backgroundColor: this.options.platforms.map(platform => this.options.platformColors[platform] || '#ccc'),
          borderColor: this.options.platforms.map(platform => this.options.platformColors[platform] || '#ccc'),
          borderWidth: 1
        }]
      },
      options: this._getChartOptions()
    });
  }
  
  /**
   * Get chart options based on current settings
   * @returns {Object} - Chart.js options object
   * @private
   */
  _getChartOptions() {
    // Get metric details
    const metricDetails = this._getMetricDetails(this.metric);
    
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const value = context.raw;
              return `${metricDetails.label}: ${this._formatValue(value, metricDetails.format)}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            }
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            },
            callback: (value) => {
              return this._formatAxisValue(value, metricDetails.format);
            }
          },
          title: {
            display: true,
            text: metricDetails.label,
            color: this.options.darkMode ? '#f8f9fa' : '#333',
            font: {
              size: 11
            }
          }
        }
      },
      animation: this.options.animations
    };
  }
  
  /**
   * Get metric details
   * @param {string} metricId - Metric ID
   * @returns {Object} - Metric details
   * @private
   */
  _getMetricDetails(metricId) {
    const metrics = {
      impressions: {
        label: 'Impressions',
        format: 'number'
      },
      clicks: {
        label: 'Clicks',
        format: 'number'
      },
      conversions: {
        label: 'Conversions',
        format: 'number'
      },
      ctr: {
        label: 'Click-Through Rate',
        format: 'percent'
      },
      cpc: {
        label: 'Cost per Click',
        format: 'currency'
      },
      roi: {
        label: 'Return on Investment',
        format: 'percent'
      }
    };
    
    return metrics[metricId] || metrics.impressions;
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
        return `$${value.toFixed(2)}`;
      case 'number':
      default:
        return value >= 1000 ? 
          value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') : 
          value.toString();
    }
  }
  
  /**
   * Format a value for axis labels
   * @param {number} value - Value to format
   * @param {string} format - Format type
   * @returns {string} - Formatted value
   * @private
   */
  _formatAxisValue(value, format) {
    if (value === 0) return '0';
    
    switch (format) {
      case 'percent':
        return `${value}%`;
      case 'currency':
        return `$${value}`;
      case 'number':
      default:
        if (value >= 1000000) {
          return `${(value / 1000000).toFixed(1)}M`;
        } else if (value >= 1000) {
          return `${(value / 1000).toFixed(1)}K`;
        }
        return value.toString();
    }
  }
  
  /**
   * Fetch platform performance data for segment
   * @param {number} segmentId - Segment ID
   * @returns {Promise<Object>} - Platform performance data
   * @private
   */
  async _fetchData(segmentId) {
    // In a real implementation, this would fetch data from an API
    // For this example, we'll generate sample data
    
    const getRandomValue = (metric) => {
      switch (metric) {
        case 'impressions':
          return Math.floor(Math.random() * 100000) + 5000;
        case 'clicks':
          return Math.floor(Math.random() * 5000) + 100;
        case 'conversions':
          return Math.floor(Math.random() * 500) + 10;
        case 'ctr':
          return (Math.random() * 5) + 0.5; // 0.5% to 5.5%
        case 'cpc':
          return (Math.random() * 2) + 0.5; // $0.50 to $2.50
        case 'roi':
          return (Math.random() * 200) + 50; // 50% to 250%
        default:
          return Math.random() * 100;
      }
    };
    
    // Generate data for all metrics and platforms
    const data = {};
    
    const metrics = ['impressions', 'clicks', 'conversions', 'ctr', 'cpc', 'roi'];
    
    metrics.forEach(metric => {
      data[metric] = {};
      
      this.options.platforms.forEach(platform => {
        data[metric][platform] = getRandomValue(metric);
      });
    });
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return data;
  }
  
  /**
   * Update chart with data for current metric
   * @param {Object} data - Performance data for all metrics and platforms
   * @private
   */
  _updateChartWithData(data) {
    if (!this.chart) return;
    
    // Get data for current metric
    const metricData = data[this.metric] || {};
    
    // Extract values for each platform
    const values = this.options.platforms.map(platform => metricData[platform] || 0);
    
    // Update chart data
    this.chart.data.datasets[0].data = values;
    
    // Update chart options (may have changed if metric changed)
    this.chart.options = this._getChartOptions();
    
    // Update chart
    this.chart.update();
  }
  
  /**
   * Update chart with new data
   * @param {number} segmentId - Segment ID
   */
  async updateData(segmentId) {
    try {
      this.segmentId = segmentId;
      
      // Skip if not initialized
      if (!this.initialized || !this.chart) {
        return;
      }
      
      // Show placeholder/loading state
      this.container.innerHTML = `
        <div class="chart-placeholder">
          <div class="spinner"></div>
          <div class="placeholder-text">Loading data...</div>
        </div>
      `;
      
      // Fetch data
      this.data = await this._fetchData(segmentId);
      
      // Restore chart canvas
      this.container.innerHTML = `<canvas id="platform-performance-canvas"></canvas>`;
      
      // Re-initialize chart
      this._initializeChart();
      
      // Update chart with data
      this._updateChartWithData(this.data);
    } catch (error) {
      console.error('Error updating platform performance chart:', error);
      
      // Show error message
      this.container.innerHTML = `
        <div class="chart-placeholder">
          <div class="placeholder-text">Error loading data. Please try again.</div>
        </div>
      `;
    }
  }
  
  /**
   * Set metric to display
   * @param {string} metric - Metric ID
   */
  setMetric(metric) {
    // Skip if same metric
    if (this.metric === metric) {
      return;
    }
    
    this.metric = metric;
    
    // Skip if no data or not initialized
    if (!this.data || !this.initialized || !this.chart) {
      return;
    }
    
    // Update chart with new metric
    this._updateChartWithData(this.data);
  }
  
  /**
   * Force chart resize
   */
  resize() {
    if (this.chart) {
      this.chart.resize();
    }
  }
  
  /**
   * Clean up chart
   */
  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
    
    // Clear container
    this.container.innerHTML = '';
  }
}
