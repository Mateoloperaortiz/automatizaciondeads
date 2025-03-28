/**
 * MagnetoCursor - Campaign Breakdown Chart
 * 
 * A component for visualizing campaign performance data broken down by different
 * dimensions like platform, ad type, placement, or device.
 */

export class CampaignBreakdownChart {
  /**
   * Initialize the campaign breakdown chart
   * @param {HTMLElement} container - Container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    if (!this.container) {
      throw new Error('Container element is required');
    }
    
    this.options = {
      darkMode: false,
      breakdownType: 'platform',
      platformColors: {
        meta: '#4267B2',
        google: '#DB4437',
        twitter: '#1DA1F2'
      },
      ...options
    };
    
    this.chart = null;
    this.initialize();
  }
  
  /**
   * Initialize the component
   */
  initialize() {
    // Create canvas element for chart
    const canvas = document.createElement('canvas');
    canvas.width = this.container.clientWidth;
    canvas.height = this.container.clientHeight;
    
    this.container.innerHTML = '';
    this.container.appendChild(canvas);
    
    // Set up chart
    this._setupChart(canvas);
  }
  
  /**
   * Set up Chart.js instance
   * @param {HTMLCanvasElement} canvas - Canvas element for chart
   * @private
   */
  _setupChart(canvas) {
    // Default empty data
    const data = {
      labels: [],
      datasets: [
        {
          label: 'Impressions',
          data: [],
          backgroundColor: this._getColors(0),
          borderColor: this._getBorderColors(0),
          borderWidth: 1
        }
      ]
    };
    
    // Chart options
    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: this.options.darkMode ? '#f9fafb' : '#111827',
            font: {
              family: "'Inter', sans-serif",
              size: 12
            },
            boxWidth: 12,
            padding: 15
          }
        },
        tooltip: {
          backgroundColor: this.options.darkMode ? '#374151' : 'rgba(255, 255, 255, 0.9)',
          titleColor: this.options.darkMode ? '#f9fafb' : '#111827',
          bodyColor: this.options.darkMode ? '#e5e7eb' : '#374151',
          borderColor: this.options.darkMode ? '#4b5563' : '#e5e7eb',
          borderWidth: 1,
          padding: 12,
          boxPadding: 6,
          usePointStyle: true,
          callbacks: {
            label: (context) => {
              const value = context.raw;
              return `${context.dataset.label}: ${this._formatValue(context.dataset.label, value)}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: this.options.darkMode ? '#374151' : '#e5e7eb',
            drawBorder: false
          },
          ticks: {
            color: this.options.darkMode ? '#d1d5db' : '#4b5563',
            font: {
              family: "'Inter', sans-serif",
              size: 11
            }
          }
        },
        y: {
          grid: {
            color: this.options.darkMode ? '#374151' : '#e5e7eb',
            drawBorder: false
          },
          ticks: {
            color: this.options.darkMode ? '#d1d5db' : '#4b5563',
            font: {
              family: "'Inter', sans-serif",
              size: 11
            },
            callback: (value) => {
              return this._formatAxisValue('Impressions', value);
            }
          }
        }
      }
    };
    
    // Create chart
    this.chart = new Chart(canvas, {
      type: 'bar',
      data: data,
      options: options
    });
  }
  
  /**
   * Get array of colors for chart based on breakdown type
   * @param {number} datasetIndex - Index of dataset
   * @returns {Array<string>} - Array of colors
   * @private
   */
  _getColors(datasetIndex) {
    // Different color schemes based on breakdown type
    const colorSchemes = {
      platform: [
        '#4267B2', // Meta blue
        '#DB4437', // Google red
        '#1DA1F2'  // Twitter blue
      ],
      ad_type: [
        '#8B5CF6', // Purple for image
        '#EC4899', // Pink for video
        '#F59E0B', // Amber for carousel
        '#10B981'  // Emerald for collection
      ],
      placement: [
        '#3B82F6', // Blue for feed
        '#F43F5E', // Rose for stories
        '#6366F1', // Indigo for search
        '#14B8A6'  // Teal for display
      ],
      device: [
        '#6366F1', // Indigo for desktop
        '#10B981', // Emerald for mobile
        '#F59E0B'  // Amber for tablet
      ]
    };
    
    // Alpha transparency for different datasets
    const alphas = [0.8, 0.6, 0.7, 0.65];
    const alpha = alphas[datasetIndex % alphas.length];
    
    // Get colors for current breakdown type
    const colors = colorSchemes[this.options.breakdownType] || colorSchemes.platform;
    
    // Apply alpha transparency
    return colors.map(color => {
      // If color is hex, convert to rgba
      if (color.startsWith('#')) {
        const r = parseInt(color.slice(1, 3), 16);
        const g = parseInt(color.slice(3, 5), 16);
        const b = parseInt(color.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
      }
      
      // If already rgba, just update alpha
      if (color.startsWith('rgba')) {
        return color.replace(/[\d\.]+\)$/, `${alpha})`);
      }
      
      return color;
    });
  }
  
  /**
   * Get array of border colors for chart
   * @param {number} datasetIndex - Index of dataset
   * @returns {Array<string>} - Array of colors
   * @private
   */
  _getBorderColors(datasetIndex) {
    // Get base colors and just use more solid alpha
    const baseColors = this._getColors(datasetIndex);
    
    return baseColors.map(color => {
      // If color is rgba, make the border more solid
      if (color.startsWith('rgba')) {
        return color.replace(/[\d\.]+\)$/, '1)');
      }
      
      return color;
    });
  }
  
  /**
   * Format value for display in tooltip
   * @param {string} label - Dataset label
   * @param {number} value - Value to format
   * @returns {string} - Formatted value
   * @private
   */
  _formatValue(label, value) {
    if (value === undefined || value === null) {
      return '-';
    }
    
    // Different formatting based on metric
    if (label.includes('Impressions')) {
      return value.toLocaleString();
    }
    
    if (label.includes('Clicks')) {
      return value.toLocaleString();
    }
    
    if (label.includes('CTR') || label.includes('Rate')) {
      return `${value.toFixed(2)}%`;
    }
    
    if (label.includes('Cost') || label.includes('Spend') || label.includes('Revenue')) {
      return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    
    if (label.includes('ROI')) {
      return `${value.toFixed(0)}%`;
    }
    
    // Default formatting
    return value.toLocaleString();
  }
  
  /**
   * Format value for display on axis
   * @param {string} metric - Metric name
   * @param {number} value - Value to format
   * @returns {string} - Formatted value
   * @private
   */
  _formatAxisValue(metric, value) {
    if (value === 0) return '0';
    
    // Different formatting based on metric
    if (metric.includes('Impressions')) {
      return value >= 1000000 ? `${(value / 1000000).toFixed(1)}M` : value >= 1000 ? `${(value / 1000).toFixed(0)}K` : value;
    }
    
    if (metric.includes('Clicks') || metric.includes('Conversions')) {
      return value >= 1000 ? `${(value / 1000).toFixed(1)}K` : value;
    }
    
    if (metric.includes('CTR') || metric.includes('Rate') || metric.includes('ROI')) {
      return `${value}%`;
    }
    
    if (metric.includes('Cost') || metric.includes('Spend') || metric.includes('Revenue')) {
      return `$${value >= 1000 ? `${(value / 1000).toFixed(0)}K` : value}`;
    }
    
    // Default formatting
    return value.toLocaleString();
  }
  
  /**
   * Update chart data
   * @param {Array} data - Campaign breakdown data
   * @param {Object} options - Update options
   */
  updateData(data, options = {}) {
    // Merge options
    this.options = {
      ...this.options,
      ...options
    };
    
    if (!data || !Array.isArray(data) || data.length === 0) {
      // Show empty state
      this.chart.data.labels = [];
      this.chart.data.datasets = [{
        label: 'No Data',
        data: []
      }];
      this.chart.update();
      return;
    }
    
    // Get labels from data
    const labels = data.map(item => item.name);
    
    // Prepare datasets
    const datasets = [];
    
    // Impressions dataset
    if (data[0].impressions !== undefined) {
      datasets.push({
        label: 'Impressions',
        data: data.map(item => item.impressions),
        backgroundColor: this._getColors(0),
        borderColor: this._getBorderColors(0),
        borderWidth: 1
      });
    }
    
    // Clicks dataset
    if (data[0].clicks !== undefined) {
      datasets.push({
        label: 'Clicks',
        data: data.map(item => item.clicks),
        backgroundColor: this._getColors(1),
        borderColor: this._getBorderColors(1),
        borderWidth: 1
      });
    }
    
    // Conversions dataset
    if (data[0].conversions !== undefined) {
      datasets.push({
        label: 'Conversions',
        data: data.map(item => item.conversions),
        backgroundColor: this._getColors(2),
        borderColor: this._getBorderColors(2),
        borderWidth: 1
      });
    }
    
    // Spend dataset
    if (data[0].spend !== undefined) {
      datasets.push({
        label: 'Spend',
        data: data.map(item => item.spend),
        backgroundColor: this._getColors(3),
        borderColor: this._getBorderColors(3),
        borderWidth: 1
      });
    }
    
    // Update y-axis formatter based on active dataset
    if (this.chart.options.scales.y) {
      this.chart.options.scales.y.ticks.callback = function(value) {
        if (datasets.length > 0) {
          const metric = datasets[0].label;
          
          if (metric.includes('Impressions')) {
            return value >= 1000000 ? `${(value / 1000000).toFixed(1)}M` : value >= 1000 ? `${(value / 1000).toFixed(0)}K` : value;
          }
          
          if (metric.includes('Clicks') || metric.includes('Conversions')) {
            return value >= 1000 ? `${(value / 1000).toFixed(1)}K` : value;
          }
          
          if (metric.includes('Spend') || metric.includes('Revenue')) {
            return `$${value >= 1000 ? `${(value / 1000).toFixed(0)}K` : value}`;
          }
        }
        
        return value;
      };
    }
    
    // Update chart data
    this.chart.data.labels = labels;
    this.chart.data.datasets = datasets;
    
    // Update chart
    this.chart.update();
  }
  
  /**
   * Update chart options
   * @param {Object} options - New options
   */
  updateOptions(options) {
    // Merge options
    this.options = {
      ...this.options,
      ...options
    };
    
    // Apply dark mode changes if needed
    if (options.darkMode !== undefined) {
      this.chart.options.plugins.legend.labels.color = options.darkMode ? '#f9fafb' : '#111827';
      this.chart.options.plugins.tooltip.backgroundColor = options.darkMode ? '#374151' : 'rgba(255, 255, 255, 0.9)';
      this.chart.options.plugins.tooltip.titleColor = options.darkMode ? '#f9fafb' : '#111827';
      this.chart.options.plugins.tooltip.bodyColor = options.darkMode ? '#e5e7eb' : '#374151';
      this.chart.options.plugins.tooltip.borderColor = options.darkMode ? '#4b5563' : '#e5e7eb';
      this.chart.options.scales.x.grid.color = options.darkMode ? '#374151' : '#e5e7eb';
      this.chart.options.scales.x.ticks.color = options.darkMode ? '#d1d5db' : '#4b5563';
      this.chart.options.scales.y.grid.color = options.darkMode ? '#374151' : '#e5e7eb';
      this.chart.options.scales.y.ticks.color = options.darkMode ? '#d1d5db' : '#4b5563';
      
      // Redraw with new colors
      const datasets = this.chart.data.datasets;
      for (let i = 0; i < datasets.length; i++) {
        datasets[i].backgroundColor = this._getColors(i);
        datasets[i].borderColor = this._getBorderColors(i);
      }
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
   * Clean up resources
   */
  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
    
    this.container.innerHTML = '';
  }
}