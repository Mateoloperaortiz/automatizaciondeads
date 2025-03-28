/**
 * MagnetoCursor - Campaign Performance Table
 * 
 * A component for displaying detailed campaign performance metrics in a sortable table.
 */

export class CampaignPerformanceTable {
  /**
   * Initialize the campaign performance table
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
      metrics: [],
      ...options
    };
    
    this.initialize();
  }
  
  /**
   * Initialize the component
   */
  initialize() {
    // Create table structure
    this.container.innerHTML = `
      <table class="performance-table">
        <thead>
          <tr class="header-row">
            <th class="sortable" data-sort="campaign">Campaign</th>
            <th class="sortable" data-sort="platform">Platform</th>
            <th class="sortable" data-sort="impressions">Impressions</th>
            <th class="sortable" data-sort="clicks">Clicks</th>
            <th class="sortable" data-sort="ctr">CTR</th>
            <th class="sortable" data-sort="conversions">Conversions</th>
            <th class="sortable" data-sort="cpa">CPA</th>
            <th class="sortable" data-sort="spend">Spend</th>
            <th class="sortable" data-sort="roi">ROI</th>
          </tr>
        </thead>
        <tbody>
          <tr class="empty-row">
            <td colspan="9">No data available</td>
          </tr>
        </tbody>
      </table>
    `;
    
    // Apply styles
    this._addStyles();
    
    // Set up event listeners
    this._setupEventListeners();
    
    // Set initial sort
    this.sortColumn = 'impressions';
    this.sortDirection = 'desc';
  }
  
  /**
   * Add component styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('campaign-performance-table-styles')) {
      const style = document.createElement('style');
      style.id = 'campaign-performance-table-styles';
      style.textContent = `
        .performance-table {
          width: 100%;
          border-collapse: collapse;
          border-spacing: 0;
          font-size: 0.875rem;
          border: 1px solid var(--border-color, #e5e7eb);
        }
        
        .performance-table th,
        .performance-table td {
          padding: 0.75rem 1rem;
          text-align: left;
          border-bottom: 1px solid var(--border-color, #e5e7eb);
          white-space: nowrap;
        }
        
        .performance-table th {
          font-weight: 600;
          color: var(--text-secondary, #4b5563);
          background-color: var(--table-header-bg, #f9fafb);
          position: sticky;
          top: 0;
          z-index: 10;
        }
        
        .performance-table tbody tr:hover {
          background-color: var(--hover-bg, #f9fafb);
        }
        
        .sortable {
          cursor: pointer;
          position: relative;
          padding-right: 1.5rem;
        }
        
        .sortable:after {
          content: "↑";
          position: absolute;
          right: 0.5rem;
          opacity: 0.3;
        }
        
        .sortable.sort-asc:after {
          content: "↑";
          opacity: 1;
        }
        
        .sortable.sort-desc:after {
          content: "↓";
          opacity: 1;
        }
        
        .empty-row td {
          text-align: center;
          padding: 2rem;
          color: var(--text-muted, #9ca3af);
        }
        
        .platform-badge {
          display: inline-flex;
          align-items: center;
          padding: 0.25rem 0.5rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
        }
        
        .platform-badge i {
          margin-right: 0.35rem;
        }
        
        .platform-badge.meta {
          background-color: rgba(66, 103, 178, 0.1);
          color: #4267B2;
        }
        
        .platform-badge.google {
          background-color: rgba(234, 67, 53, 0.1);
          color: #EA4335;
        }
        
        .platform-badge.twitter {
          background-color: rgba(29, 161, 242, 0.1);
          color: #1DA1F2;
        }
        
        .campaign-name {
          font-weight: 500;
        }
        
        .campaign-status {
          display: inline-block;
          margin-left: 0.5rem;
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        
        .campaign-status.active {
          background-color: #10B981;
        }
        
        .campaign-status.paused {
          background-color: #F59E0B;
        }
        
        .campaign-status.ended {
          background-color: #6B7280;
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Set up event listeners
   * @private
   */
  _setupEventListeners() {
    // Sort headers
    const headers = this.container.querySelectorAll('.sortable');
    
    headers.forEach(header => {
      header.addEventListener('click', () => {
        const column = header.getAttribute('data-sort');
        
        // Toggle direction if same column
        if (column === this.sortColumn) {
          this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
          this.sortColumn = column;
          this.sortDirection = 'desc';
        }
        
        // Update sort indicators
        headers.forEach(h => {
          h.classList.remove('sort-asc', 'sort-desc');
        });
        
        header.classList.add(`sort-${this.sortDirection}`);
        
        // Resort data
        this._sortData();
      });
    });
  }
  
  /**
   * Sort the data
   * @private
   */
  _sortData() {
    if (!this.data || !this.data.platforms || !this.data.metrics) {
      return;
    }
    
    // Get all rows
    const rows = Array.from(this.container.querySelectorAll('tbody tr:not(.empty-row)'));
    
    // Sort rows
    rows.sort((a, b) => {
      const aValue = a.getAttribute(`data-${this.sortColumn}`);
      const bValue = b.getAttribute(`data-${this.sortColumn}`);
      
      // Handle string vs number comparison
      let comparison;
      
      if (!isNaN(aValue) && !isNaN(bValue)) {
        // Numeric comparison
        comparison = parseFloat(aValue) - parseFloat(bValue);
      } else {
        // String comparison
        comparison = aValue.localeCompare(bValue);
      }
      
      // Apply sort direction
      return this.sortDirection === 'asc' ? comparison : -comparison;
    });
    
    // Reinsert rows in new order
    const tbody = this.container.querySelector('tbody');
    rows.forEach(row => {
      tbody.appendChild(row);
    });
  }
  
  /**
   * Format a value based on metric type
   * @param {string} metricId - Metric ID
   * @param {number} value - Value to format
   * @returns {string} - Formatted value
   * @private
   */
  _formatValue(metricId, value) {
    if (value === undefined || value === null) {
      return '-';
    }
    
    const metric = this.options.metrics.find(m => m.id === metricId);
    
    if (!metric) {
      return value.toLocaleString();
    }
    
    switch (metric.format) {
      case 'percent':
        return `${value.toFixed(2)}%`;
      case 'currency':
        return `$${value.toFixed(2)}`;
      default:
        return value.toLocaleString();
    }
  }
  
  /**
   * Get platform badge HTML
   * @param {string} platform - Platform name
   * @returns {string} - HTML for platform badge
   * @private
   */
  _getPlatformBadge(platform) {
    const icons = {
      meta: '<i class="fab fa-facebook"></i>',
      google: '<i class="fab fa-google"></i>',
      twitter: '<i class="fab fa-twitter"></i>'
    };
    
    const icon = icons[platform] || '';
    
    return `<span class="platform-badge ${platform}">${icon}${platform.charAt(0).toUpperCase() + platform.slice(1)}</span>`;
  }
  
  /**
   * Get campaign status indicator
   * @param {string} status - Campaign status
   * @returns {string} - HTML for status indicator
   * @private
   */
  _getStatusIndicator(status) {
    if (!status) return '';
    
    const statusClass = status.toLowerCase();
    return `<span class="campaign-status ${statusClass}" title="${status}"></span>`;
  }
  
  /**
   * Update table data
   * @param {Object} data - Campaign performance data
   */
  updateData(data) {
    this.data = data;
    
    if (!data || !data.campaigns || !data.metrics || !data.platforms) {
      // Show empty state
      const tbody = this.container.querySelector('tbody');
      tbody.innerHTML = `
        <tr class="empty-row">
          <td colspan="9">No data available</td>
        </tr>
      `;
      return;
    }
    
    // Get references
    const tbody = this.container.querySelector('tbody');
    const { campaigns, metrics, platforms, timeframe } = data;
    
    // Clear existing rows
    tbody.innerHTML = '';
    
    // Add platform rows for each campaign
    campaigns.forEach(campaign => {
      platforms.forEach(platform => {
        const row = document.createElement('tr');
        
        // Set data attributes for sorting
        row.setAttribute('data-campaign', campaign.name);
        row.setAttribute('data-platform', platform);
        
        if (metrics.impressions && metrics.impressions[platform]) {
          row.setAttribute('data-impressions', metrics.impressions[platform]);
        }
        
        if (metrics.clicks && metrics.clicks[platform]) {
          row.setAttribute('data-clicks', metrics.clicks[platform]);
        }
        
        if (metrics.conversions && metrics.conversions[platform]) {
          row.setAttribute('data-conversions', metrics.conversions[platform]);
        }
        
        if (metrics.ctr && metrics.ctr[platform]) {
          row.setAttribute('data-ctr', metrics.ctr[platform]);
        }
        
        if (metrics.cpa && metrics.cpa[platform]) {
          row.setAttribute('data-cpa', metrics.cpa[platform]);
        }
        
        if (metrics.spend && metrics.spend[platform]) {
          row.setAttribute('data-spend', metrics.spend[platform]);
        }
        
        if (metrics.roi && metrics.roi[platform]) {
          row.setAttribute('data-roi', metrics.roi[platform]);
        }
        
        // Build row content
        row.innerHTML = `
          <td>
            <div class="campaign-name">
              ${campaign.name}${this._getStatusIndicator(campaign.status)}
            </div>
          </td>
          <td>${this._getPlatformBadge(platform)}</td>
          <td>${this._formatValue('impressions', metrics.impressions?.[platform])}</td>
          <td>${this._formatValue('clicks', metrics.clicks?.[platform])}</td>
          <td>${this._formatValue('ctr', metrics.ctr?.[platform])}</td>
          <td>${this._formatValue('conversions', metrics.conversions?.[platform])}</td>
          <td>${this._formatValue('cpa', metrics.cpa?.[platform])}</td>
          <td>${this._formatValue('spend', metrics.spend?.[platform])}</td>
          <td>${this._formatValue('roi', metrics.roi?.[platform])}</td>
        `;
        
        tbody.appendChild(row);
      });
    });
    
    // Apply current sort
    const header = this.container.querySelector(`[data-sort="${this.sortColumn}"]`);
    if (header) {
      header.classList.add(`sort-${this.sortDirection}`);
      this._sortData();
    }
  }
  
  /**
   * Clean up resources
   */
  destroy() {
    // No specific cleanup needed for now
    this.container.innerHTML = '';
  }
}