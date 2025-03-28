/**
 * MagnetoCursor - ROI Visualization Component
 * 
 * Visualizes return on investment for campaigns across different platforms,
 * showing the relationship between ad spend and revenue/conversions.
 */

export class RoiVisualization {
  /**
   * Initialize the ROI visualization component
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      platforms: ['meta', 'google', 'twitter'],
      platformColors: {
        meta: '#4267B2',
        google: '#DB4437',
        twitter: '#1DA1F2'
      },
      showLegend: true,
      visualizationType: 'bubble', // 'bubble', 'scatter', 'column'
      animations: {
        duration: 750
      },
      minBubbleSize: 10,
      maxBubbleSize: 50,
      ...options
    };
    
    // State
    this.chart = null;
    this.data = null;
    this.isLoading = false;
    this.initialized = false;
    
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
    this.container.innerHTML = `<canvas id="roi-visualization-canvas"></canvas>`;
    
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
    if (!document.getElementById('roi-visualization-styles')) {
      const style = document.createElement('style');
      style.id = 'roi-visualization-styles';
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
        
        .roi-tooltip {
          background-color: var(--bg-color, white);
          border: 1px solid var(--border-color, #dee2e6);
          border-radius: 0.25rem;
          padding: 0.75rem;
          box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
          max-width: 250px;
          font-size: 0.875rem;
        }
        
        .roi-tooltip-title {
          font-weight: 600;
          margin-bottom: 0.5rem;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid var(--border-color, #dee2e6);
        }
        
        .roi-tooltip-item {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.25rem;
        }
        
        .roi-tooltip-item-label {
          margin-right: 1rem;
          font-weight: 500;
        }
        
        .roi-summary-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 1rem;
          margin-bottom: 1rem;
        }
        
        .roi-summary-card {
          background-color: var(--card-bg, #f8f9fa);
          border-radius: 0.25rem;
          padding: 0.75rem;
          text-align: center;
        }
        
        .roi-summary-label {
          font-size: 0.875rem;
          color: var(--text-color-secondary, #6c757d);
          margin-bottom: 0.25rem;
        }
        
        .roi-summary-value {
          font-size: 1.25rem;
          font-weight: 600;
        }
        
        .roi-summary-secondary {
          font-size: 0.75rem;
          color: var(--text-color-secondary, #6c757d);
          margin-top: 0.25rem;
        }
        
        .dark-mode .roi-tooltip {
          background-color: #343a40;
          border-color: #495057;
        }
        
        .dark-mode .roi-tooltip-title {
          border-color: #495057;
        }
        
        .dark-mode .roi-summary-card {
          background-color: #343a40;
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
    const canvas = document.getElementById('roi-visualization-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Create chart with empty data
    if (this.options.visualizationType === 'bubble') {
      this.chart = new Chart(ctx, {
        type: 'bubble',
        data: {
          datasets: []
        },
        options: this._getBubbleChartOptions()
      });
    } else if (this.options.visualizationType === 'scatter') {
      this.chart = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: []
        },
        options: this._getScatterChartOptions()
      });
    } else {
      this.chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: [],
          datasets: []
        },
        options: this._getColumnChartOptions()
      });
    }
  }
  
  /**
   * Get options for bubble chart
   * @returns {Object} - Chart.js options
   * @private
   */
  _getBubbleChartOptions() {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: this.options.showLegend,
          position: 'top',
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
          enabled: true,
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
              const platform = context.dataset.label || '';
              const spend = context.parsed.x;
              const revenue = context.parsed.y;
              const conversions = context.raw.v;
              
              let lines = [`${platform}`];
              lines.push(`Spend: $${spend.toFixed(2)}`);
              lines.push(`Revenue: $${revenue.toFixed(2)}`);
              lines.push(`Conversions: ${conversions}`);
              lines.push(`ROI: ${((revenue - spend) / spend * 100).toFixed(2)}%`);
              
              return lines;
            }
          }
        },
        title: {
          display: true,
          text: 'Campaign ROI Analysis',
          color: this.options.darkMode ? '#f8f9fa' : '#333',
          font: {
            size: 14,
            weight: 'normal'
          },
          padding: {
            top: 10,
            bottom: 15
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Ad Spend (USD)',
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 11
            }
          },
          grid: {
            color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            },
            callback: (value) => {
              if (value >= 1000) {
                return `$${(value / 1000).toFixed(1)}K`;
              }
              return `$${value}`;
            }
          }
        },
        y: {
          title: {
            display: true,
            text: 'Revenue (USD)',
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 11
            }
          },
          grid: {
            color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            },
            callback: (value) => {
              if (value >= 1000) {
                return `$${(value / 1000).toFixed(1)}K`;
              }
              return `$${value}`;
            }
          }
        }
      },
      animation: this.options.animations
    };
  }
  
  /**
   * Get options for scatter chart
   * @returns {Object} - Chart.js options
   * @private
   */
  _getScatterChartOptions() {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: this.options.showLegend,
          position: 'top',
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
          enabled: true,
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
              const platform = context.dataset.label || '';
              const cpa = context.parsed.x;
              const roi = context.parsed.y;
              
              let lines = [`${platform}`];
              lines.push(`Cost per Acquisition: $${cpa.toFixed(2)}`);
              lines.push(`ROI: ${roi.toFixed(2)}%`);
              
              return lines;
            }
          }
        },
        title: {
          display: true,
          text: 'CPA vs. ROI Analysis',
          color: this.options.darkMode ? '#f8f9fa' : '#333',
          font: {
            size: 14,
            weight: 'normal'
          },
          padding: {
            top: 10,
            bottom: 15
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Cost per Acquisition (USD)',
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 11
            }
          },
          grid: {
            color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            },
            callback: (value) => `$${value.toFixed(2)}`
          }
        },
        y: {
          title: {
            display: true,
            text: 'ROI (%)',
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 11
            }
          },
          grid: {
            color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            },
            callback: (value) => `${value.toFixed(1)}%`
          }
        }
      },
      animation: this.options.animations
    };
  }
  
  /**
   * Get options for column chart
   * @returns {Object} - Chart.js options
   * @private
   */
  _getColumnChartOptions() {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: this.options.showLegend,
          position: 'top',
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
          enabled: true,
          backgroundColor: this.options.darkMode ? 'rgba(33, 37, 41, 0.8)' : 'rgba(255, 255, 255, 0.8)',
          titleColor: this.options.darkMode ? '#f8f9fa' : '#333',
          bodyColor: this.options.darkMode ? '#f8f9fa' : '#333',
          borderColor: this.options.darkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.1)',
          borderWidth: 1,
          padding: 10,
          boxPadding: 5,
          usePointStyle: true
        },
        title: {
          display: true,
          text: 'ROI by Platform',
          color: this.options.darkMode ? '#f8f9fa' : '#333',
          font: {
            size: 14,
            weight: 'normal'
          },
          padding: {
            top: 10,
            bottom: 15
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
              size: 11
            }
          }
        },
        y: {
          title: {
            display: true,
            text: 'ROI (%)',
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 11
            }
          },
          grid: {
            color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            },
            callback: (value) => `${value}%`
          }
        }
      },
      animation: this.options.animations
    };
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
   * @param {Object} data - ROI data
   */
  updateData(data) {
    // Store data
    this.data = data;
    
    // Skip if not initialized
    if (!this.initialized || !this.chart) {
      return;
    }
    
    // Add summary section
    this._addSummarySection(data);
    
    // Render chart
    this._renderChart(data);
  }
  
  /**
   * Add summary section above chart
   * @param {Object} data - ROI data
   * @private
   */
  _addSummarySection(data) {
    // Clean up existing summary
    const existingSummary = this.container.querySelector('.roi-summary');
    if (existingSummary) {
      existingSummary.remove();
    }
    
    // Skip if no overall data
    if (!data.overall) {
      return;
    }
    
    // Create summary container
    const summary = document.createElement('div');
    summary.className = 'roi-summary';
    
    // Create summary grid
    const grid = document.createElement('div');
    grid.className = 'roi-summary-grid';
    
    // Add summary cards
    grid.innerHTML = `
      <div class="roi-summary-card">
        <div class="roi-summary-label">Total Spend</div>
        <div class="roi-summary-value">$${this._formatNumber(data.overall.spend)}</div>
      </div>
      
      <div class="roi-summary-card">
        <div class="roi-summary-label">Total Revenue</div>
        <div class="roi-summary-value">$${this._formatNumber(data.overall.revenue)}</div>
        <div class="roi-summary-secondary">${data.overall.revenue > data.overall.spend ? 'Profitable' : 'Not Profitable'}</div>
      </div>
      
      <div class="roi-summary-card">
        <div class="roi-summary-label">Total Conversions</div>
        <div class="roi-summary-value">${this._formatNumber(data.overall.conversions)}</div>
        <div class="roi-summary-secondary">CPA: $${(data.overall.spend / data.overall.conversions).toFixed(2)}</div>
      </div>
      
      <div class="roi-summary-card">
        <div class="roi-summary-label">Overall ROI</div>
        <div class="roi-summary-value">${((data.overall.revenue - data.overall.spend) / data.overall.spend * 100).toFixed(2)}%</div>
      </div>
    `;
    
    // Add grid to summary container
    summary.appendChild(grid);
    
    // Insert summary before canvas
    const canvas = this.container.querySelector('canvas');
    if (canvas) {
      this.container.insertBefore(summary, canvas);
    }
  }
  
  /**
   * Format number for display
   * @param {number} value - Value to format
   * @returns {string} - Formatted number
   * @private
   */
  _formatNumber(value) {
    if (value === undefined || value === null) {
      return 'N/A';
    }
    
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(2)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(2)}K`;
    }
    
    return value.toString();
  }
  
  /**
   * Render chart with data
   * @param {Object} data - Platform data
   * @private
   */
  _renderChart(data) {
    if (!this.chart) return;
    
    // Clear existing datasets
    this.chart.data.datasets = [];
    
    if (this.options.visualizationType === 'bubble') {
      this._renderBubbleChart(data);
    } else if (this.options.visualizationType === 'scatter') {
      this._renderScatterChart(data);
    } else {
      this._renderColumnChart(data);
    }
    
    // Update chart
    this.chart.update();
  }
  
  /**
   * Render bubble chart
   * @param {Object} data - ROI data
   * @private
   */
  _renderBubbleChart(data) {
    // Extract platform data
    const platforms = Object.keys(data.platforms || {});
    if (platforms.length === 0) {
      platforms.push(...this.options.platforms);
    }
    
    // Add dataset for each platform
    platforms.forEach((platform, index) => {
      // Skip if platform data not available
      if (!data.platforms || !data.platforms[platform]) {
        return;
      }
      
      const platformData = data.platforms[platform];
      const color = this.options.platformColors[platform] || `hsl(${index * 137.5}, 70%, 60%)`;
      
      // Calculate bubble size based on conversion count
      const conversions = platformData.conversions || 0;
      const maxConversions = Math.max(...platforms
        .filter(p => data.platforms[p])
        .map(p => data.platforms[p]?.conversions || 0));
      const minConversions = Math.min(...platforms
        .filter(p => data.platforms[p] && data.platforms[p]?.conversions > 0)
        .map(p => data.platforms[p]?.conversions || 0));
      
      // Scale bubble size
      let size = this.options.minBubbleSize;
      if (maxConversions > minConversions) {
        const range = this.options.maxBubbleSize - this.options.minBubbleSize;
        const scale = (conversions - minConversions) / (maxConversions - minConversions);
        size = Math.max(this.options.minBubbleSize, this.options.minBubbleSize + range * scale);
      } else if (conversions > 0) {
        size = this.options.minBubbleSize + 
          (this.options.maxBubbleSize - this.options.minBubbleSize) / 2;
      }
      
      // Add dataset
      this.chart.data.datasets.push({
        label: this._formatPlatformName(platform),
        data: [{
          x: platformData.spend || 0,
          y: platformData.revenue || 0,
          r: size / 2, // Chart.js uses radius, not diameter
          v: conversions // Store conversions for tooltip
        }],
        backgroundColor: this._hexToRgba(color, 0.6),
        borderColor: color,
        borderWidth: 1
      });
    });
  }
  
  /**
   * Render scatter chart
   * @param {Object} data - ROI data
   * @private
   */
  _renderScatterChart(data) {
    // Extract platform data
    const platforms = Object.keys(data.platforms || {});
    if (platforms.length === 0) {
      platforms.push(...this.options.platforms);
    }
    
    // Create a single dataset with points for each platform
    const dataset = {
      data: [],
      backgroundColor: [],
      borderColor: [],
      borderWidth: 1,
      pointStyle: 'circle',
      pointRadius: 8,
      pointHoverRadius: 12
    };
    
    // Add point for each platform
    platforms.forEach((platform, index) => {
      // Skip if platform data not available
      if (!data.platforms || !data.platforms[platform]) {
        return;
      }
      
      const platformData = data.platforms[platform];
      const color = this.options.platformColors[platform] || `hsl(${index * 137.5}, 70%, 60%)`;
      
      // Calculate metrics
      const spend = platformData.spend || 0;
      const conversions = platformData.conversions || 0;
      const revenue = platformData.revenue || 0;
      
      // Calculate CPA and ROI
      const cpa = conversions > 0 ? spend / conversions : 0;
      const roi = spend > 0 ? (revenue - spend) / spend * 100 : 0;
      
      // Add data point
      dataset.data.push({
        x: cpa,
        y: roi,
        platform: this._formatPlatformName(platform)
      });
      
      dataset.backgroundColor.push(this._hexToRgba(color, 0.6));
      dataset.borderColor.push(color);
    });
    
    // Add dataset to chart
    this.chart.data.datasets.push(dataset);
    
    // Custom tooltip function
    this.chart.options.plugins.tooltip.callbacks.label = (context) => {
      const platform = context.raw.platform || '';
      const cpa = context.parsed.x;
      const roi = context.parsed.y;
      
      let lines = [`${platform}`];
      lines.push(`Cost per Acquisition: $${cpa.toFixed(2)}`);
      lines.push(`ROI: ${roi.toFixed(2)}%`);
      
      return lines;
    };
  }
  
  /**
   * Render column chart
   * @param {Object} data - ROI data
   * @private
   */
  _renderColumnChart(data) {
    // Extract platform data
    const platforms = Object.keys(data.platforms || {});
    if (platforms.length === 0) {
      platforms.push(...this.options.platforms);
    }
    
    // Clear existing labels
    this.chart.data.labels = [];
    
    // Create datasets for spend and revenue
    const spendDataset = {
      label: 'Spend',
      data: [],
      backgroundColor: this._hexToRgba('#FF7043', 0.6),
      borderColor: '#FF7043',
      borderWidth: 1
    };
    
    const revenueDataset = {
      label: 'Revenue',
      data: [],
      backgroundColor: this._hexToRgba('#43A047', 0.6),
      borderColor: '#43A047',
      borderWidth: 1
    };
    
    const roiDataset = {
      label: 'ROI %',
      data: [],
      backgroundColor: this._hexToRgba('#1E88E5', 0.6),
      borderColor: '#1E88E5',
      borderWidth: 1,
      type: 'line',
      yAxisID: 'y1'
    };
    
    // Add data for each platform
    platforms.forEach((platform) => {
      // Skip if platform data not available
      if (!data.platforms || !data.platforms[platform]) {
        return;
      }
      
      const platformData = data.platforms[platform];
      const formattedName = this._formatPlatformName(platform);
      
      // Add label
      this.chart.data.labels.push(formattedName);
      
      // Add spend and revenue
      spendDataset.data.push(platformData.spend || 0);
      revenueDataset.data.push(platformData.revenue || 0);
      
      // Calculate ROI
      const spend = platformData.spend || 0;
      const revenue = platformData.revenue || 0;
      const roi = spend > 0 ? (revenue - spend) / spend * 100 : 0;
      
      roiDataset.data.push(roi);
    });
    
    // Add datasets to chart
    this.chart.data.datasets = [spendDataset, revenueDataset, roiDataset];
    
    // Update chart options for column chart with dual y-axis
    this.chart.options = {
      ...this._getColumnChartOptions(),
      scales: {
        ...this._getColumnChartOptions().scales,
        y: {
          ...this._getColumnChartOptions().scales.y,
          position: 'left',
          title: {
            display: true,
            text: 'Amount (USD)',
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 11
            }
          },
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            },
            callback: (value) => {
              if (value >= 1000) {
                return `$${(value / 1000).toFixed(1)}K`;
              }
              return `$${value}`;
            }
          }
        },
        y1: {
          position: 'right',
          grid: {
            drawOnChartArea: false,
            color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          },
          title: {
            display: true,
            text: 'ROI (%)',
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 11
            }
          },
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            },
            callback: (value) => `${value.toFixed(1)}%`
          }
        }
      }
    };
  }

  /**
   * Update chart options
   * @param {Object} options - New options
   */
  updateOptions(options = {}) {
    // Update options
    this.options = {
      ...this.options,
      ...options
    };
    
    // Skip if not initialized
    if (!this.initialized || !this.chart) {
      return;
    }
    
    // Update chart type if needed
    if (options.visualizationType && options.visualizationType !== this.options.visualizationType) {
      // Destroy current chart
      this.chart.destroy();
      
      // Reinitialize chart
      this._initializeChart();
      
      // Render data if available
      if (this.data) {
        this._renderChart(this.data);
      }
      
      return;
    }
    
    // Update chart options
    if (this.options.visualizationType === 'bubble') {
      this.chart.options = this._getBubbleChartOptions();
    } else if (this.options.visualizationType === 'scatter') {
      this.chart.options = this._getScatterChartOptions();
    } else {
      this.chart.options = this._getColumnChartOptions();
    }
    
    // Update chart
    this.chart.update();
  }
  
  /**
   * Resize the chart
   */
  resize() {
    if (this.chart) {
      this.chart.resize();
    }
  }
  
  /**
   * Destroy the chart instance
   */
  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
    
    this.container.innerHTML = '';
    this.initialized = false;
  }
}