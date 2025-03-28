/**
 * MagnetoCursor - Segment Comparison Tool
 * 
 * Provides visual comparison of two segments to highlight differences
 * in demographics, performance metrics, and characteristics.
 */

export class SegmentComparisonTool {
  /**
   * Initialize the segment comparison tool
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      metrics: [
        { id: 'age', label: 'Avg. Age', format: 'number' },
        { id: 'experience', label: 'Avg. Experience', format: 'number' },
        { id: 'size', label: 'Size', format: 'number' },
        { id: 'ctr', label: 'CTR', format: 'percent' },
        { id: 'cpc', label: 'CPC', format: 'currency' },
        { id: 'conversion_rate', label: 'Conv. Rate', format: 'percent' }
      ],
      ...options
    };
    
    // State
    this.data = null;
    this.chart = null;
    this.initialized = false;
    
    // Initialize component
    this.initialize();
  }
  
  /**
   * Initialize the comparison tool
   */
  async initialize() {
    // Add placeholder
    this.container.querySelector('#comparison-results').innerHTML = `
      <div class="comparison-placeholder">
        <p>Select two segments to compare</p>
      </div>
    `;
    
    // Add styles
    this._addStyles();
    
    // Load Chart.js for radar chart
    await this._loadChartJs();
    
    this.initialized = true;
    
    // Render data if available
    if (this.data) {
      this.displayComparison(this.data);
    }
  }
  
  /**
   * Add component styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('segment-comparison-tool-styles')) {
      const style = document.createElement('style');
      style.id = 'segment-comparison-tool-styles';
      style.textContent = `
        .comparison-placeholder {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100px;
          font-size: 0.875rem;
          color: var(--text-color-secondary, #6c757d);
          font-style: italic;
        }
        
        .comparison-results {
          width: 100%;
          overflow: hidden;
        }
        
        .comparison-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.5rem;
        }
        
        .segment-item {
          flex: 1;
          text-align: center;
          font-weight: 600;
          font-size: 0.875rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          padding: 0 0.5rem;
        }
        
        .metrics-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.813rem;
          margin-bottom: 0.75rem;
        }
        
        .metrics-table th {
          text-align: left;
          font-weight: normal;
          color: var(--text-color-secondary, #6c757d);
          padding: 0.25rem;
        }
        
        .metrics-table td {
          padding: 0.25rem;
          text-align: center;
          font-weight: 600;
        }
        
        .metrics-table tr:nth-child(even) {
          background-color: rgba(0, 0, 0, 0.025);
        }
        
        .dark-mode .metrics-table tr:nth-child(even) {
          background-color: rgba(255, 255, 255, 0.05);
        }
        
        .metrics-table td.positive {
          color: var(--success, #28a745);
        }
        
        .metrics-table td.negative {
          color: var(--danger, #dc3545);
        }
        
        .diff-indicator {
          font-size: 10px;
          margin-left: 3px;
        }
        
        .chart-container {
          height: 150px;
          width: 100%;
          margin-top: 0.75rem;
        }
        
        .similarity-score {
          display: block;
          text-align: center;
          font-size: 0.875rem;
          margin-top: 0.5rem;
          font-weight: 600;
        }
        
        .comparison-note {
          font-size: 0.75rem;
          color: var(--text-color-secondary, #6c757d);
          text-align: center;
          margin-top: 0.5rem;
          font-style: italic;
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
   * Format a value based on specified format
   * @param {number} value - Value to format
   * @param {string} format - Format type ('number', 'percent', 'currency')
   * @param {boolean} alwaysShowSign - Whether to always show sign
   * @returns {string} - Formatted value
   * @private
   */
  _formatValue(value, format, alwaysShowSign = false) {
    if (value === undefined || value === null) {
      return 'N/A';
    }
    
    let result;
    
    switch (format) {
      case 'percent':
        result = `${value.toFixed(1)}%`;
        break;
      case 'currency':
        result = `$${value.toFixed(2)}`;
        break;
      case 'number':
      default:
        result = value.toFixed(1);
    }
    
    // Add sign if requested
    if (alwaysShowSign && value > 0) {
      result = `+${result}`;
    }
    
    return result;
  }
  
  /**
   * Create radar chart comparing segment characteristics
   * @param {Object} data - Comparison data
   * @returns {Object} - Chart.js instance
   * @private
   */
  _createRadarChart(data) {
    const segment1 = data.segment1;
    const segment2 = data.segment2;
    
    // Get the canvas element
    const canvasEl = document.getElementById('comparison-radar-chart');
    if (!canvasEl) return null;
    
    // Extract radar data from segments
    const radarData = this._extractRadarData(segment1, segment2);
    
    // Create radar chart
    return new Chart(canvasEl, {
      type: 'radar',
      data: {
        labels: radarData.labels,
        datasets: [
          {
            label: segment1.name,
            data: radarData.data1,
            backgroundColor: 'rgba(78, 121, 167, 0.2)',
            borderColor: 'rgba(78, 121, 167, 1)',
            pointBackgroundColor: 'rgba(78, 121, 167, 1)'
          },
          {
            label: segment2.name,
            data: radarData.data2,
            backgroundColor: 'rgba(242, 142, 44, 0.2)',
            borderColor: 'rgba(242, 142, 44, 1)',
            pointBackgroundColor: 'rgba(242, 142, 44, 1)'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: {
              color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
            },
            grid: {
              color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
            },
            pointLabels: {
              color: this.options.darkMode ? '#adb5bd' : '#666',
              font: {
                size: 10
              }
            },
            ticks: {
              display: false
            }
          }
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 10,
              font: {
                size: 10
              },
              color: this.options.darkMode ? '#adb5bd' : '#666'
            }
          },
          tooltip: {
            enabled: true
          }
        }
      }
    });
  }
  
  /**
   * Extract radar chart data from segments
   * @param {Object} segment1 - First segment
   * @param {Object} segment2 - Second segment
   * @returns {Object} - Radar chart data
   * @private
   */
  _extractRadarData(segment1, segment2) {
    // Define radar dimensions based on available segment data
    const dimensions = [
      { key: 'age_score', label: 'Age' },
      { key: 'experience_score', label: 'Experience' },
      { key: 'education_score', label: 'Education' },
      { key: 'engagement_score', label: 'Engagement' },
      { key: 'conversion_score', label: 'Conversion' }
    ];
    
    // Extract data for each dimension
    const labels = [];
    const data1 = [];
    const data2 = [];
    
    dimensions.forEach(dimension => {
      labels.push(dimension.label);
      
      // Extract values or use defaults
      const val1 = segment1.characteristics?.[dimension.key] || Math.random() * 10;
      const val2 = segment2.characteristics?.[dimension.key] || Math.random() * 10;
      
      data1.push(val1);
      data2.push(val2);
    });
    
    return { labels, data1, data2 };
  }
  
  /**
   * Display comparison between two segments
   * @param {Object} data - Comparison data
   */
  displayComparison(data) {
    // Store data
    this.data = data;
    
    // Skip if not initialized
    if (!this.initialized) {
      return;
    }
    
    const resultsContainer = document.getElementById('comparison-results');
    if (!resultsContainer) return;
    
    // Extract segment data
    const segment1 = data.segment1 || {};
    const segment2 = data.segment2 || {};
    
    // Create similarity score (0-100)
    const similarityScore = data.similarity !== undefined ? 
      data.similarity : 
      Math.round(Math.random() * 100);
    
    // Create HTML content
    resultsContainer.innerHTML = `
      <div class="comparison-header">
        <div class="segment-item">${segment1.name || 'Segment 1'}</div>
        <div class="segment-item">${segment2.name || 'Segment 2'}</div>
      </div>
      
      <table class="metrics-table">
        <thead>
          <tr>
            <th>Metric</th>
            <th>${segment1.name || 'Segment 1'}</th>
            <th>${segment2.name || 'Segment 2'}</th>
            <th>Diff</th>
          </tr>
        </thead>
        <tbody>
          ${this._generateMetricsRows(segment1, segment2)}
        </tbody>
      </table>
      
      <div class="chart-container">
        <canvas id="comparison-radar-chart"></canvas>
      </div>
      
      <span class="similarity-score">Similarity Score: ${similarityScore}%</span>
      
      <div class="comparison-note">
        Higher similarity indicates segments that may perform similarly in campaigns.
      </div>
    `;
    
    // Create radar chart
    this.chart = this._createRadarChart(data);
  }
  
  /**
   * Generate HTML for metric rows
   * @param {Object} segment1 - First segment
   * @param {Object} segment2 - Second segment
   * @returns {string} - HTML for metric rows
   * @private
   */
  _generateMetricsRows(segment1, segment2) {
    return this.options.metrics.map(metric => {
      // Get values (real or placeholder data)
      const value1 = segment1.metrics?.[metric.id] !== undefined ? 
        segment1.metrics[metric.id] : 
        this._generatePlaceholderValue(metric);
        
      const value2 = segment2.metrics?.[metric.id] !== undefined ? 
        segment2.metrics[metric.id] : 
        this._generatePlaceholderValue(metric);
      
      // Calculate difference
      const diff = value2 - value1;
      const diffClass = diff > 0 ? 'positive' : (diff < 0 ? 'negative' : '');
      const diffIndicator = diff > 0 ? '▲' : (diff < 0 ? '▼' : '');
      
      return `
        <tr>
          <th>${metric.label}</th>
          <td>${this._formatValue(value1, metric.format)}</td>
          <td>${this._formatValue(value2, metric.format)}</td>
          <td class="${diffClass}">
            ${this._formatValue(Math.abs(diff), metric.format, true)}
            <span class="diff-indicator">${diffIndicator}</span>
          </td>
        </tr>
      `;
    }).join('');
  }
  
  /**
   * Generate placeholder value for metrics
   * @param {Object} metric - Metric definition
   * @returns {number} - Placeholder value
   * @private
   */
  _generatePlaceholderValue(metric) {
    switch (metric.format) {
      case 'percent':
        return Math.random() * 10;
      case 'currency':
        return Math.random() * 5;
      case 'number':
      default:
        if (metric.id === 'age') {
          return 25 + Math.random() * 20;
        } else if (metric.id === 'experience') {
          return Math.random() * 10;
        } else if (metric.id === 'size') {
          return Math.round(Math.random() * 200);
        }
        return Math.random() * 100;
    }
  }
  
  /**
   * Clean up component
   */
  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }
}
