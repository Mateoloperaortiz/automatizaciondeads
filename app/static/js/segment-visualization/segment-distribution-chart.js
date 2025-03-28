/**
 * MagnetoCursor - Segment Distribution Chart
 * 
 * Visualizes the distribution of candidates across segments
 * with support for both pie and bar chart views.
 */

export class SegmentDistributionChart {
  /**
   * Initialize the segment distribution chart
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      initialType: 'pie', // 'pie' or 'bar'
      colors: [
        '#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f',
        '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab'
      ],
      animation: {
        duration: 750
      },
      ...options
    };
    
    // State
    this.chartType = this.options.initialType;
    this.chart = null;
    this.data = null;
    this.initialized = false;
    
    // Initialize chart
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
    this.container.innerHTML = `<canvas id="segment-distribution-canvas"></canvas>`;
    
    // Initialize chart
    this._initializeChart();
    
    this.initialized = true;
    
    // Render initial data if available
    if (this.data) {
      this.updateData(this.data);
    }
  }
  
  /**
   * Add component styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('segment-distribution-chart-styles')) {
      const style = document.createElement('style');
      style.id = 'segment-distribution-chart-styles';
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
    const canvas = document.getElementById('segment-distribution-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Set chart options based on type
    const chartOptions = this._getChartOptions();
    
    // Create chart
    this.chart = new Chart(ctx, {
      type: this.chartType,
      data: {
        labels: [],
        datasets: [{
          data: [],
          backgroundColor: this.options.colors
        }]
      },
      options: chartOptions
    });
  }
  
  /**
   * Get chart options based on current chart type
   * @returns {Object} - Chart.js options object
   * @private
   */
  _getChartOptions() {
    // Common options
    const commonOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            },
            boxWidth: 12,
            padding: 10,
            usePointStyle: true
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || '';
              const value = context.raw || 0;
              const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return `${label}: ${value} candidates (${percentage}%)`;
            }
          }
        }
      },
      animation: this.options.animation
    };
    
    // Pie chart specific options
    if (this.chartType === 'pie') {
      return {
        ...commonOptions,
        cutout: '30%',
        radius: '90%'
      };
    }
    
    // Bar chart specific options
    return {
      ...commonOptions,
      scales: {
        x: {
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            }
          },
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: true,
          ticks: {
            color: this.options.darkMode ? '#adb5bd' : '#666',
            font: {
              size: 10
            }
          },
          grid: {
            color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          },
          title: {
            display: true,
            text: 'Candidates',
            color: this.options.darkMode ? '#f8f9fa' : '#333',
            font: {
              size: 11
            }
          }
        }
      }
    };
  }
  
  /**
   * Update chart with new data
   * @param {Array} segments - Array of segment objects
   */
  updateData(segments) {
    // Store data
    this.data = segments;
    
    // Skip if not initialized
    if (!this.initialized || !this.chart) {
      return;
    }
    
    // Process segment data
    const labels = [];
    const data = [];
    
    segments.forEach(segment => {
      const count = segment.candidate_count || 0;
      labels.push(segment.name);
      data.push(count);
    });
    
    // Update chart data
    this.chart.data.labels = labels;
    this.chart.data.datasets[0].data = data;
    
    // Update chart
    this.chart.update();
  }
  
  /**
   * Get current chart type
   * @returns {string} - Chart type ('pie' or 'bar')
   */
  getChartType() {
    return this.chartType;
  }
  
  /**
   * Set chart type
   * @param {string} type - Chart type ('pie' or 'bar')
   */
  setChartType(type) {
    if (type !== 'pie' && type !== 'bar') {
      console.error('Invalid chart type. Use "pie" or "bar".');
      return;
    }
    
    // Skip if same type
    if (this.chartType === type) {
      return;
    }
    
    this.chartType = type;
    
    // Destroy old chart
    if (this.chart) {
      this.chart.destroy();
    }
    
    // Re-initialize with new type
    this._initializeChart();
    
    // Re-render data
    if (this.data) {
      this.updateData(this.data);
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
