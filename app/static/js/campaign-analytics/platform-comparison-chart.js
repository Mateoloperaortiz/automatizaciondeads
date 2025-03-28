/**
 * MagnetoCursor - Platform Comparison Chart Component
 * 
 * Visualizes and compares campaign performance metrics across different 
 * advertising platforms (Meta, Google, Twitter, etc.).
 */

export class PlatformComparisonChart {
  /**
   * Initialize the platform comparison chart component
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      metric: 'impressions',
      platforms: ['meta', 'google', 'twitter'],
      platformColors: {
        meta: '#4267B2',
        google: '#DB4437',
        twitter: '#1DA1F2'
      },
      chartType: 'bar', // 'bar' or 'radar'
      showLegend: true,
      showValues: true,
      animations: {
        duration: 750
      },
      ...options
    };
    
    // State
    this.chart = null;
    this.data = null;
    this.metric = this.options.metric;
    this.isLoading = false;
    this.initialized = false;
    
    // Define metrics formats
    this.metricFormats = {
      impressions: 'number',
      clicks: 'number',
      conversions: 'number',
      ctr: 'percent',
      cpc: 'currency',
      cpa: 'currency',
      spend: 'currency',
      revenue: 'currency',
      roi: 'percent'
    };
    
    // Initialize chart
    this.initialize();
  }
  
  /**
   * Initialize the chart
   */
  async initialize() {
    // Create loading placeholder
    this.container.innerHTML = `
      <div class="chart-loading">
        <div class="spinner"></div>
        <div class="loading-text">Loading chart...</div>
      </div>
    `;
    
    // Add styles
    this._addStyles();
    
    // Load Chart.js
    await this._loadChartJs();
    
    // Replace placeholder with canvas
    this.container.innerHTML = `<canvas id="platform-comparison-canvas"></canvas>`;
    
    // Initialize Chart.js
    this._initializeChart();
    
    this.initialized = true;
    
    // Render initial data if available
    if (this.data) {
      this._renderChart(this.data);
    }
  }
  
  /**
   * Add component styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('platform-comparison-chart-styles')) {
      const style = document.createElement('style');
      style.id = 'platform-comparison-chart-styles';
      style.textContent = `
        .chart-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          width: 100%;
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
        
        .loading-text {
          margin-top: 0.5rem;
          font-size: 0.875rem;
          color: var(--text-color-secondary, #6c757d);
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
    const canvas = document.getElementById('platform-comparison-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Create chart with empty data
    this.chart = new Chart(ctx, {
      type: this.options.chartType,
      data: {
        labels: this.options.platforms.map(platform => this._formatPlatformName(platform)),
        datasets: [{
          data: [],
          backgroundColor: this.options.platforms.map(platform => this._hexToRgba(this.options.platformColors[platform] || '#ccc', 0.6)),
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
    const metricFormat = this.metricFormats[this.metric] || 'number';
    const metricLabel = this._getMetricLabel(this.metric);
    
    // Common options
    const commonOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: metricLabel,
          color: this.options.darkMode ? '#f8f9fa' : '#333',
          font: {
            size: 14,
            weight: 'normal'
          },
          padding: {
            top: 10,
            bottom: 15
          }
        },
        tooltip: {
          enabled: true,
          backgroundColor: this.options.darkMode ? 'rgba(33, 37, 41, 0.8)' : 'rgba(255, 255, 255, 0.8)',
          titleColor: this.options.darkMode ? '#f8f9fa' : '#333',
          bodyColor: this.options.darkMode ? '#f8f9fa' : '#333',
          borderColor: this.options.darkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.1)',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (context) => {
              let label = context.dataset.label || '';
              let value = context.raw;
              
              if (label) {
                label += ': ';
              }
              
              label += this._formatValue(value, metricFormat);
              return label;
            }
          }
        },
        datalabels: this.options.showValues ? {
          display: true,
          color: this.options.darkMode ? '#f8f9fa' : '#333',
          font: {
            weight: 'bold'
          },
          formatter: (value) => this._formatValue(value, metricFormat)
        } : { display: false }
      },
      animation: this.options.animations
    };
    
    // Chart type specific options
    if (this.options.chartType === 'bar') {
      return {
        ...commonOptions,
        indexAxis: 'y', // Horizontal bar chart
        scales: {
          x: {
            beginAtZero: true,
            grid: {
              color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
            },
            ticks: {
              color: this.options.darkMode ? '#adb5bd' : '#666',
              font: {
                size: 10
              },
              callback: (value) => this._formatAxisLabel(value, metricFormat)
            }
          },
          y: {
            grid: {
              display: false
            },
            ticks: {
              color: this.options.darkMode ? '#adb5bd' : '#666',
              font: {
                size: 12
              }
            }
          }
        }
      };
    } else if (this.options.chartType === 'radar') {
      return {
        ...commonOptions,
        scales: {
          r: {
            beginAtZero: true,
            angleLines: {
              color: this.options.darkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.1)'
            },
            grid: {
              color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
            },
            pointLabels: {
              color: this.options.darkMode ? '#adb5bd' : '#666',
              font: {
                size: 12
              }
            },
            ticks: {
              color: this.options.darkMode ? '#adb5bd' : '#666',
              font: {
                size: 10
              },
              backdropColor: 'transparent',
              callback: (value) => this._formatAxisLabel(value, metricFormat)
            }
          }
        }
      };
    }
    
    return commonOptions;
  }
  
  /**
   * Get metric label
   * @param {string} metric - Metric ID
   * @returns {string} - Human-readable label
   * @private
   */
  _getMetricLabel(metric) {
    const labels = {
      impressions: 'Impressions',
      clicks: 'Clicks',
      conversions: 'Conversions',
      ctr: 'Click-Through Rate',
      cpc: 'Cost per Click',
      cpa: 'Cost per Acquisition',
      spend: 'Spend',
      revenue: 'Revenue',
      roi: 'Return on Investment'
    };
    
    return labels[metric] || metric;
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
  _formatAxisLabel(value, format) {
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
   * Format platform name for display
   * @param {string} platform - Platform ID
   * @returns {string} - Formatted platform name
   * @private
   */
  _formatPlatformName(platform) {
    const names = {
      meta: 'Meta',
      google: 'Google',
      twitter: 'Twitter',
      linkedin: 'LinkedIn',
      tiktok: 'TikTok',
      snapchat: 'Snapchat',
      pinterest: 'Pinterest'
    };
    
    return names[platform] || platform;
  }
  
  /**
   * Convert hex color to rgba
   * @param {string} hex - Hex color string
   * @param {number} alpha - Alpha value (0-1)
   * @returns {string} - RGBA color string
   * @private
   */
  _hexToRgba(hex, alpha) {
    if (!/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)) {
      return hex; // Return original value if not a valid hex color
    }
    
    let r, g, b;
    if (hex.length === 4) {
      r = parseInt(hex[1] + hex[1], 16);
      g = parseInt(hex[2] + hex[2], 16);
      b = parseInt(hex[3] + hex[3], 16);
    } else {
      r = parseInt(hex.substring(1, 3), 16);
      g = parseInt(hex.substring(3, 5), 16);
      b = parseInt(hex.substring(5, 7), 16);
    }
    
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }
  
  /**
   * Update chart with new data
   * @param {Object} data - Platform comparison data
   */
  updateData(data) {
    // Store data
    this.data = data;
    
    // Skip if not initialized
    if (!this.initialized || !this.chart) {
      return;
    }
    
    // Render chart
    this._renderChart(data);
  }
  
  /**
   * Render chart with data
   * @param {Object} data - Platform data
   * @private
   */
  _renderChart(data) {
    if (!this.chart) return;
    
    // Get data for current metric
    const metricData = data.data?.[this.metric] || {};
    
    // Extract values for each platform
    const values = this.options.platforms.map(platform => metricData[platform] || 0);
    
    // Update chart data
    this.chart.data.datasets[0].data = values;
    
    // Update chart options
    this.chart.options = this._getChartOptions();
    
    // Update chart
    this.chart.update();
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
    
    // Re-render chart if data available
    if (this.data) {
      this._renderChart(this.data);
    }
  }
  
  /**
   * Set chart type (bar or radar)
   * @param {string} chartType - Chart type ('bar' or 'radar')
   */
  setChartType(chartType) {
    if (chartType !== 'bar' && chartType !== 'radar') {
      console.error(`Invalid chart type: ${chartType}. Must be 'bar' or 'radar'.`);
      return;
    }
    
    if (this.options.chartType === chartType) {
      return;
    }
    
    this.options.chartType = chartType;
    
    // Need to completely recreate the chart
    if (this.chart) {
      this.chart.destroy();
      this._initializeChart();
      
      // Re-render if data available
      if (this.data) {
        this._renderChart(this.data);
      }
    }
  }
  
  /**
   * Toggle value labels
   * @param {boolean} show - Whether to show value labels
   */
  toggleValueLabels(show) {
    this.options.showValues = show;
    
    // Update chart options
    if (this.chart) {
      this.chart.options = this._getChartOptions();
      this.chart.update();
    }
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
