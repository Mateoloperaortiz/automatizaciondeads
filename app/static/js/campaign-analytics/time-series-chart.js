/**
 * MagnetoCursor - Time Series Chart Component
 * 
 * Visualizes performance metrics over time for multi-platform campaigns.
 * Supports all standard metrics with customizable time ranges.
 */

export class TimeSeriesChart {
  /**
   * Initialize the time series chart component
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      metric: 'impressions',
      dateRange: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
        end: new Date()
      },
      platformColors: {
        meta: '#4267B2',
        google: '#DB4437',
        twitter: '#1DA1F2'
      },
      showLegend: true,
      showTooltips: true,
      smoothLines: true,
      fillArea: true,
      animations: {
        duration: 750
      },
      ...options
    };
    
    // State
    this.chart = null;
    this.data = null;
    this.metric = this.options.metric;
    this.dateRange = this.options.dateRange;
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
    this.container.innerHTML = `<canvas id="time-series-canvas"></canvas>`;
    
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
    if (!document.getElementById('time-series-chart-styles')) {
      const style = document.createElement('style');
      style.id = 'time-series-chart-styles';
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
    const canvas = document.getElementById('time-series-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Create chart with empty data
    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        datasets: []
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
    
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: this.options.showLegend,
          position: 'bottom',
          labels: {
            boxWidth: 12,
            padding: 15,
            usePointStyle: true,
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 11
            }
          }
        },
        tooltip: {
          enabled: this.options.showTooltips,
          backgroundColor: this.options.darkMode ? 'rgba(33, 37, 41, 0.8)' : 'rgba(255, 255, 255, 0.8)',
          titleColor: this.options.darkMode ? '#f8f9fa' : '#333',
          bodyColor: this.options.darkMode ? '#f8f9fa' : '#333',
          borderColor: this.options.darkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.1)',
          borderWidth: 1,
          padding: 10,
          boxPadding: 5,
          usePointStyle: true,
          callbacks: {
            label: (context) => {
              let label = context.dataset.label || '';
              let value = context.parsed.y;
              
              if (label) {
                label += ': ';
              }
              
              label += this._formatValue(value, metricFormat);
              return label;
            }
          }
        }
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: this._getTimeUnit(this.dateRange),
            displayFormats: {
              day: 'MMM d',
              week: 'MMM d',
              month: 'MMM yyyy'
            },
            tooltipFormat: 'll'
          },
          grid: {
            color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            maxRotation: 0,
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
              return this._formatAxisLabel(value, metricFormat);
            }
          },
          title: {
            display: true,
            text: metricLabel,
            color: this.options.darkMode ? '#f8f9fa' : '#333',
            font: {
              size: 11
            }
          }
        }
      },
      animations: this.options.animations
    };
  }
  
  /**
   * Get appropriate time unit based on date range
   * @param {Object} dateRange - Date range
   * @returns {string} - Time unit
   * @private
   */
  _getTimeUnit(dateRange) {
    const days = Math.round((dateRange.end - dateRange.start) / (1000 * 60 * 60 * 24));
    
    if (days <= 14) {
      return 'day';
    } else if (days <= 90) {
      return 'week';
    } else {
      return 'month';
    }
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
   * Format a value for y-axis labels
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
   * Update chart with new data
   * @param {Object} data - Time series data
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
   * @param {Object} data - Time series data
   * @private
   */
  _renderChart(data) {
    if (!this.chart) return;
    
    // Clear existing datasets
    this.chart.data.datasets = [];
    
    // Extract platform data for current metric
    const platforms = data.platforms || [];
    
    // Add dataset for each platform
    platforms.forEach((platform, index) => {
      const color = this.options.platformColors[platform] || `hsl(${index * 137.5}, 70%, 60%)`;
      
      // Skip if platform data not available
      if (!data.data || !data.data[platform] || !data.data[platform][this.metric]) {
        return;
      }
      
      // Convert data points to Chart.js format
      const points = data.data[platform][this.metric].map(point => ({
        x: new Date(point.x),
        y: point.y
      }));
      
      // Add dataset
      this.chart.data.datasets.push({
        label: this._formatPlatformName(platform),
        data: points,
        borderColor: color,
        backgroundColor: this.options.fillArea ? 
          this._hexToRgba(color, 0.2) : 
          color,
        fill: this.options.fillArea,
        tension: this.options.smoothLines ? 0.4 : 0,
        borderWidth: 2,
        pointRadius: 2,
        pointHoverRadius: 5
      });
    });
    
    // Update chart options
    this.chart.options = this._getChartOptions();
    
    // Update chart
    this.chart.update();
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
   * Set date range
   * @param {Object} dateRange - Date range with start and end dates
   */
  setDateRange(dateRange) {
    this.dateRange = dateRange;
    
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
