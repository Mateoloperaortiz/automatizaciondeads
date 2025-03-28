/**
 * MagnetoCursor - WebSocket Filter Manager
 * 
 * Manages saved WebSocket subscription filters with features for:
 * - Saving and loading filters
 * - Filter organization and categorization 
 * - Filter performance statistics
 * - Filter debugging tools
 */

import { toastService } from '../../services/toast-service.js';
import FilterModal from './filter-modal.js';
import FilterValidator from './filter-validator.js';

export class FilterManager {
  /**
   * Initialize the filter manager component
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      onLoadFilter: null,
      onDeleteFilter: null,
      onDuplicateFilter: null,
      initialFilter: null,
      filterListUrl: '/api/websocket/filters',
      filterStatsUrl: '/api/websocket/filter-stats',
      categories: ['General', 'Campaigns', 'Notifications', 'Alerts', 'Custom'],
      ...options
    };
    
    // State
    this.filters = [];
    this.filterStats = {};
    this.isLoading = false;
    this.activeFilterId = null;
    this.searchQuery = '';
    this.activeCategory = 'all';
    
    // Initialize validation
    this.validator = new FilterValidator({
      fields: this.options.fields || [],
      entityTypes: this.options.entityTypes || []
    });
    
    // Initialize modal
    this.filterModal = new FilterModal({
      onSave: this._handleFilterSave.bind(this),
      categories: this.options.categories,
      fields: this.options.fields || [],
      entityTypes: this.options.entityTypes || []
    });
    
    // Initialize the component
    this.initialize();
  }
  
  /**
   * Initialize the component
   */
  async initialize() {
    // Add styles
    this._addStyles();
    
    // Set initial loading state
    this._setLoadingState(true);
    
    // Render the filter manager
    this._renderFilterManager();
    
    // Load saved filters
    try {
      await this._loadSavedFilters();
    } catch (error) {
      console.error('Error loading saved filters:', error);
      toastService.error('Failed to load saved filters');
    }
    
    // Set loading state to false
    this._setLoadingState(false);
    
    // Load filter statistics
    try {
      await this._loadFilterStats();
    } catch (error) {
      console.error('Error loading filter statistics:', error);
      toastService.error('Failed to load filter statistics');
    }
    
    // Set active filter if provided
    if (this.options.initialFilter) {
      this.setActiveFilter(this.options.initialFilter.id);
    }
  }
  
  /**
   * Add component styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('filter-manager-styles')) {
      const style = document.createElement('style');
      style.id = 'filter-manager-styles';
      style.textContent = `
        .ws-filter-manager {
          font-family: var(--font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif);
          color: var(--text-color, #333);
          background: var(--bg-color, #f8f9fa);
          border-radius: 0.25rem;
          border: 1px solid var(--border-color, #dee2e6);
          overflow: hidden;
          display: flex;
          flex-direction: column;
          height: 100%;
        }
        
        .ws-filter-manager.dark-mode {
          --bg-color: #212529;
          --text-color: #f8f9fa;
          --border-color: #495057;
          --input-bg: #343a40;
          --input-border: #495057;
          --input-text: #f8f9fa;
          --panel-bg: #343a40;
          --panel-border: #495057;
          --item-bg: #2c3034;
          --item-border: #495057;
          --item-hover: #495057;
          --item-active: #0d6efd;
          --btn-default-bg: #343a40;
          --btn-default-border: #495057;
          --btn-default-text: #f8f9fa;
          --btn-primary-bg: #0d6efd;
          --btn-primary-border: #0d6efd;
          --btn-primary-text: #fff;
          --btn-danger-bg: #dc3545;
          --btn-danger-border: #dc3545;
          --btn-danger-text: #fff;
        }
        
        .filter-manager-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          background-color: var(--bg-color, #f8f9fa);
          border-bottom: 1px solid var(--border-color, #dee2e6);
        }
        
        .filter-manager-title {
          font-size: 1rem;
          font-weight: 600;
          margin: 0;
        }
        
        .filter-manager-search {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }
        
        .filter-manager-content {
          display: flex;
          flex: 1;
          overflow: hidden;
        }
        
        .filter-list-container {
          width: 300px;
          border-right: 1px solid var(--border-color, #dee2e6);
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }
        
        .filter-list-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          background-color: var(--bg-color, #f8f9fa);
          border-bottom: 1px solid var(--border-color, #dee2e6);
        }
        
        .filter-categories {
          display: flex;
          gap: 0.25rem;
          padding: 0.75rem;
          overflow-x: auto;
          white-space: nowrap;
          border-bottom: 1px solid var(--border-color, #dee2e6);
        }
        
        .filter-category {
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          cursor: pointer;
          font-size: 0.75rem;
          background-color: var(--btn-default-bg, #f8f9fa);
          border: 1px solid var(--btn-default-border, #dee2e6);
          color: var(--btn-default-text, #333);
        }
        
        .filter-category.active {
          background-color: var(--btn-primary-bg, #0d6efd);
          border-color: var(--btn-primary-border, #0d6efd);
          color: var(--btn-primary-text, #fff);
        }
        
        .filter-list {
          overflow-y: auto;
          flex: 1;
          padding: 0.5rem;
        }
        
        .filter-item {
          padding: 0.75rem;
          border-radius: 0.25rem;
          margin-bottom: 0.5rem;
          cursor: pointer;
          border: 1px solid var(--item-border, #dee2e6);
          background-color: var(--item-bg, #fff);
          transition: background-color 0.2s;
        }
        
        .filter-item:hover {
          background-color: var(--item-hover, #f2f2f2);
        }
        
        .filter-item.active {
          border-color: var(--item-active, #0d6efd);
          background-color: rgba(13, 110, 253, 0.1);
        }
        
        .filter-item-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.25rem;
        }
        
        .filter-item-name {
          font-weight: 600;
          font-size: 0.875rem;
          margin: 0;
          word-break: break-word;
        }
        
        .filter-item-category {
          font-size: 0.7rem;
          padding: 0.125rem 0.25rem;
          border-radius: 0.25rem;
          background-color: var(--btn-default-bg, #f8f9fa);
          color: var(--btn-default-text, #333);
        }
        
        .filter-item-description {
          font-size: 0.75rem;
          margin-bottom: 0.5rem;
          opacity: 0.8;
        }
        
        .filter-item-meta {
          display: flex;
          justify-content: space-between;
          font-size: 0.7rem;
          opacity: 0.6;
        }
        
        .filter-details-container {
          flex: 1;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }
        
        .filter-details-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          background-color: var(--bg-color, #f8f9fa);
          border-bottom: 1px solid var(--border-color, #dee2e6);
        }
        
        .filter-details-title {
          font-size: 1rem;
          font-weight: 600;
          margin: 0;
        }
        
        .filter-details-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .filter-details-content {
          padding: 1rem;
          overflow-y: auto;
          flex: 1;
        }
        
        .filter-details-section {
          margin-bottom: 1.5rem;
        }
        
        .filter-details-section-title {
          font-size: 0.875rem;
          font-weight: 600;
          margin: 0 0 0.75rem 0;
          padding-bottom: 0.25rem;
          border-bottom: 1px solid var(--border-color, #dee2e6);
        }
        
        .filter-details-info {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0.75rem;
          margin-bottom: 1rem;
        }
        
        .filter-info-item {
          display: flex;
          flex-direction: column;
        }
        
        .filter-info-label {
          font-size: 0.75rem;
          opacity: 0.6;
          margin-bottom: 0.25rem;
        }
        
        .filter-info-value {
          font-size: 0.875rem;
        }
        
        .filter-details-description {
          margin-bottom: 1rem;
          font-size: 0.875rem;
          padding: 0.75rem;
          background-color: var(--panel-bg, #f8f9fa);
          border-radius: 0.25rem;
          border: 1px solid var(--panel-border, #dee2e6);
        }
        
        .filter-stats {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 0.75rem;
          margin-bottom: 1rem;
        }
        
        .filter-stat-item {
          padding: 0.75rem;
          border-radius: 0.25rem;
          background-color: var(--panel-bg, #f8f9fa);
          border: 1px solid var(--panel-border, #dee2e6);
          text-align: center;
        }
        
        .filter-stat-value {
          font-size: 1.25rem;
          font-weight: 600;
          margin-bottom: 0.25rem;
        }
        
        .filter-stat-label {
          font-size: 0.75rem;
          opacity: 0.6;
        }
        
        .filter-efficiency {
          margin-bottom: 1rem;
        }
        
        .filter-efficiency-bar {
          height: 0.5rem;
          width: 100%;
          background-color: var(--panel-border, #dee2e6);
          border-radius: 0.25rem;
          margin-bottom: 0.5rem;
          overflow: hidden;
        }
        
        .filter-efficiency-progress {
          height: 100%;
          background-color: var(--btn-primary-bg, #0d6efd);
          border-radius: 0.25rem;
        }
        
        .filter-efficiency-labels {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
        }
        
        .filter-json-preview {
          padding: 0.75rem;
          border-radius: 0.25rem;
          background-color: var(--panel-bg, #f8f9fa);
          border: 1px solid var(--panel-border, #dee2e6);
          font-family: monospace;
          font-size: 0.875rem;
          white-space: pre-wrap;
          overflow-x: auto;
          max-height: 300px;
          overflow-y: auto;
        }
        
        .filter-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 1rem;
        }
        
        .filter-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.875rem;
        }
        
        .filter-table th,
        .filter-table td {
          padding: 0.5rem;
          border: 1px solid var(--panel-border, #dee2e6);
          text-align: left;
        }
        
        .filter-table th {
          background-color: var(--bg-color, #f8f9fa);
          font-weight: 600;
        }
        
        .filter-empty-state {
          text-align: center;
          padding: 2rem;
          font-size: 0.875rem;
          color: var(--text-color-secondary, #6c757d);
        }
        
        .filter-loading-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 2rem;
          font-size: 0.875rem;
          color: var(--text-color-secondary, #6c757d);
        }
        
        .filter-loading-spinner {
          width: 30px;
          height: 30px;
          border: 3px solid rgba(0, 0, 0, 0.1);
          border-top: 3px solid var(--btn-primary-bg, #0d6efd);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 1rem;
        }
        
        .dark-mode .filter-loading-spinner {
          border-color: rgba(255, 255, 255, 0.1);
          border-top-color: var(--btn-primary-bg, #0d6efd);
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        /* Form controls */
        select, input, button {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--input-border, #ced4da);
          border-radius: 0.25rem;
          background-color: var(--input-bg, #fff);
          color: var(--input-text, #333);
          font-size: 0.875rem;
        }
        
        button {
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 0.25rem;
          white-space: nowrap;
          user-select: none;
        }
        
        button:hover {
          opacity: 0.9;
        }
        
        button:active {
          opacity: 0.8;
        }
        
        button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .btn-default {
          background-color: var(--btn-default-bg, #f8f9fa);
          border-color: var(--btn-default-border, #ced4da);
          color: var(--btn-default-text, #333);
        }
        
        .btn-primary {
          background-color: var(--btn-primary-bg, #0d6efd);
          border-color: var(--btn-primary-border, #0d6efd);
          color: var(--btn-primary-text, #fff);
        }
        
        .btn-danger {
          background-color: var(--btn-danger-bg, #dc3545);
          border-color: var(--btn-danger-border, #dc3545);
          color: var(--btn-danger-text, #fff);
        }
        
        .btn-sm {
          padding: 0.25rem 0.5rem;
          font-size: 0.75rem;
        }
        
        .btn-icon {
          width: 28px;
          height: 28px;
          padding: 0;
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }
        
        .search-input {
          display: flex;
          align-items: center;
          position: relative;
        }
        
        .search-input input {
          padding-left: 2rem;
        }
        
        .search-input i {
          position: absolute;
          left: 0.75rem;
          opacity: 0.5;
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Render the filter manager
   * @private
   */
  _renderFilterManager() {
    // Create main container
    const managerElement = document.createElement('div');
    managerElement.className = 'ws-filter-manager';
    
    if (this.options.darkMode) {
      managerElement.classList.add('dark-mode');
    }
    
    // Create header
    const header = this._createHeader();
    managerElement.appendChild(header);
    
    // Create content container
    const content = document.createElement('div');
    content.className = 'filter-manager-content';
    
    // Create filter list
    const filterList = this._createFilterList();
    content.appendChild(filterList);
    
    // Create filter details
    const filterDetails = this._createFilterDetails();
    content.appendChild(filterDetails);
    
    // Add content to manager
    managerElement.appendChild(content);
    
    // Clear container and append manager
    this.container.innerHTML = '';
    this.container.appendChild(managerElement);
  }
  
  /**
   * Create header
   * @returns {HTMLElement} Header element
   * @private
   */
  _createHeader() {
    const header = document.createElement('div');
    header.className = 'filter-manager-header';
    
    // Title
    const title = document.createElement('h3');
    title.className = 'filter-manager-title';
    title.textContent = 'WebSocket Filter Manager';
    header.appendChild(title);
    
    // Search
    const search = document.createElement('div');
    search.className = 'filter-manager-search';
    
    const searchInput = document.createElement('div');
    searchInput.className = 'search-input';
    
    const searchIcon = document.createElement('i');
    searchIcon.className = 'fas fa-search';
    searchInput.appendChild(searchIcon);
    
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Search filters...';
    input.addEventListener('input', (e) => {
      this.searchQuery = e.target.value;
      this._filterFilterList();
    });
    searchInput.appendChild(input);
    
    search.appendChild(searchInput);
    
    header.appendChild(search);
    
    return header;
  }
  
  /**
   * Create filter list
   * @returns {HTMLElement} Filter list element
   * @private
   */
  _createFilterList() {
    const container = document.createElement('div');
    container.className = 'filter-list-container';
    
    // List header
    const header = document.createElement('div');
    header.className = 'filter-list-header';
    
    const listTitle = document.createElement('h4');
    listTitle.textContent = 'Saved Filters';
    listTitle.style.margin = '0';
    listTitle.style.fontSize = '0.875rem';
    header.appendChild(listTitle);
    
    const newFilterBtn = document.createElement('button');
    newFilterBtn.className = 'btn-primary btn-sm';
    newFilterBtn.innerHTML = '<i class="fas fa-plus"></i> New';
    newFilterBtn.addEventListener('click', () => {
      this._createNewFilter();
    });
    header.appendChild(newFilterBtn);
    
    container.appendChild(header);
    
    // Categories
    const categories = document.createElement('div');
    categories.className = 'filter-categories';
    
    // Add "All" category
    const allCategory = document.createElement('div');
    allCategory.className = 'filter-category active';
    allCategory.textContent = 'All';
    allCategory.dataset.category = 'all';
    allCategory.addEventListener('click', () => {
      this._selectCategory('all');
    });
    categories.appendChild(allCategory);
    
    // Add other categories
    this.options.categories.forEach(category => {
      const categoryElement = document.createElement('div');
      categoryElement.className = 'filter-category';
      categoryElement.textContent = category;
      categoryElement.dataset.category = category.toLowerCase();
      categoryElement.addEventListener('click', () => {
        this._selectCategory(category.toLowerCase());
      });
      categories.appendChild(categoryElement);
    });
    
    container.appendChild(categories);
    
    // Filter list
    const list = document.createElement('div');
    list.className = 'filter-list';
    
    // Initial list will be populated when filters are loaded
    if (this.isLoading) {
      // Loading state
      list.appendChild(this._createLoadingState());
    } else if (this.filters.length === 0) {
      // Empty state
      list.appendChild(this._createEmptyState());
    }
    
    container.appendChild(list);
    
    return container;
  }
  
  /**
   * Create filter details
   * @returns {HTMLElement} Filter details element
   * @private
   */
  _createFilterDetails() {
    const container = document.createElement('div');
    container.className = 'filter-details-container';
    
    // Header
    const header = document.createElement('div');
    header.className = 'filter-details-header';
    
    const title = document.createElement('h4');
    title.className = 'filter-details-title';
    title.textContent = 'Filter Details';
    header.appendChild(title);
    
    const actions = document.createElement('div');
    actions.className = 'filter-details-actions';
    
    const editButton = document.createElement('button');
    editButton.className = 'btn-primary btn-sm';
    editButton.innerHTML = '<i class="fas fa-edit"></i> Edit';
    editButton.addEventListener('click', () => {
      this._editCurrentFilter();
    });
    actions.appendChild(editButton);
    
    const duplicateButton = document.createElement('button');
    duplicateButton.className = 'btn-default btn-sm';
    duplicateButton.innerHTML = '<i class="fas fa-copy"></i> Duplicate';
    duplicateButton.addEventListener('click', () => {
      this._duplicateCurrentFilter();
    });
    actions.appendChild(duplicateButton);
    
    const deleteButton = document.createElement('button');
    deleteButton.className = 'btn-danger btn-sm';
    deleteButton.innerHTML = '<i class="fas fa-trash"></i> Delete';
    deleteButton.addEventListener('click', () => {
      this._deleteCurrentFilter();
    });
    actions.appendChild(deleteButton);
    
    header.appendChild(actions);
    container.appendChild(header);
    
    // Content
    const content = document.createElement('div');
    content.className = 'filter-details-content';
    
    // Initial empty or select message
    const emptyMessage = document.createElement('div');
    emptyMessage.className = 'filter-empty-state';
    emptyMessage.innerHTML = '<i class="fas fa-filter" style="font-size: 2rem; opacity: 0.3; margin-bottom: 1rem;"></i><br>Select a filter to view details or create a new filter.';
    content.appendChild(emptyMessage);
    
    container.appendChild(content);
    
    return container;
  }
  
  /**
   * Create loading state
   * @returns {HTMLElement} Loading state element
   * @private
   */
  _createLoadingState() {
    const loadingState = document.createElement('div');
    loadingState.className = 'filter-loading-state';
    
    const spinner = document.createElement('div');
    spinner.className = 'filter-loading-spinner';
    loadingState.appendChild(spinner);
    
    const text = document.createElement('div');
    text.textContent = 'Loading filters...';
    loadingState.appendChild(text);
    
    return loadingState;
  }
  
  /**
   * Create empty state
   * @returns {HTMLElement} Empty state element
   * @private
   */
  _createEmptyState() {
    const emptyState = document.createElement('div');
    emptyState.className = 'filter-empty-state';
    
    const icon = document.createElement('i');
    icon.className = 'fas fa-filter';
    icon.style.fontSize = '2rem';
    icon.style.opacity = '0.3';
    icon.style.marginBottom = '1rem';
    emptyState.appendChild(icon);
    
    const text = document.createElement('div');
    text.innerHTML = 'No filters found.<br>Create a new filter to get started.';
    emptyState.appendChild(text);
    
    const newButton = document.createElement('button');
    newButton.className = 'btn-primary';
    newButton.innerHTML = '<i class="fas fa-plus"></i> Create New Filter';
    newButton.style.marginTop = '1rem';
    newButton.addEventListener('click', () => {
      this._createNewFilter();
    });
    emptyState.appendChild(newButton);
    
    return emptyState;
  }
  
  /**
   * Set loading state
   * @param {boolean} isLoading - Loading state
   * @private
   */
  _setLoadingState(isLoading) {
    this.isLoading = isLoading;
    
    // Update UI if rendered
    const filterList = this.container.querySelector('.filter-list');
    if (filterList) {
      filterList.innerHTML = '';
      
      if (isLoading) {
        filterList.appendChild(this._createLoadingState());
      } else if (this.filters.length === 0) {
        filterList.appendChild(this._createEmptyState());
      } else {
        this._renderFilterItems();
      }
    }
  }
  
  /**
   * Load saved filters
   * @returns {Promise<void>}
   * @private
   */
  async _loadSavedFilters() {
    try {
      const response = await fetch(this.options.filterListUrl);
      if (!response.ok) {
        throw new Error(`Failed to load filters: ${response.statusText}`);
      }
      
      const data = await response.json();
      this.filters = data.filters || [];
      
      // Render filter items
      this._renderFilterItems();
    } catch (error) {
      console.error('Error loading filters:', error);
      // Set empty list
      this.filters = [];
      
      // Show error message
      const filterList = this.container.querySelector('.filter-list');
      if (filterList) {
        filterList.innerHTML = '';
        
        const errorMessage = document.createElement('div');
        errorMessage.className = 'filter-empty-state';
        errorMessage.innerHTML = '<i class="fas fa-exclamation-circle" style="font-size: 2rem; opacity: 0.3; margin-bottom: 1rem; color: var(--btn-danger-bg, #dc3545);"></i><br>Failed to load filters. Please try again.';
        
        const retryButton = document.createElement('button');
        retryButton.className = 'btn-primary';
        retryButton.innerHTML = '<i class="fas fa-sync"></i> Retry';
        retryButton.style.marginTop = '1rem';
        retryButton.addEventListener('click', () => {
          this._setLoadingState(true);
          this._loadSavedFilters().finally(() => {
            this._setLoadingState(false);
          });
        });
        errorMessage.appendChild(retryButton);
        
        filterList.appendChild(errorMessage);
      }
      
      // Notify the user
      toastService.error('Failed to load filters. Please try again.');
    }
  }
  
  /**
   * Load filter statistics
   * @returns {Promise<void>}
   * @private
   */
  async _loadFilterStats() {
    try {
      const response = await fetch(this.options.filterStatsUrl);
      if (!response.ok) {
        throw new Error(`Failed to load filter statistics: ${response.statusText}`);
      }
      
      const data = await response.json();
      this.filterStats = data.stats || {};
      
      // Update filter stats in UI
      this._updateFilterStats();
    } catch (error) {
      console.error('Error loading filter statistics:', error);
      // Leave stats empty
      this.filterStats = {};
      
      // Notify the user
      toastService.error('Failed to load filter statistics.');
    }
  }
  
  /**
   * Update filter statistics in UI
   * @private
   */
  _updateFilterStats() {
    // If no active filter, nothing to update
    if (!this.activeFilterId) {
      return;
    }
    
    // Find filter stats container
    const statsContainer = this.container.querySelector('.filter-stats');
    if (!statsContainer) {
      return;
    }
    
    // Get stats for active filter
    const stats = this.filterStats[this.activeFilterId];
    if (!stats) {
      // No stats available
      statsContainer.innerHTML = `
        <div class="filter-stat-item">
          <div class="filter-stat-value">-</div>
          <div class="filter-stat-label">Messages Received</div>
        </div>
        <div class="filter-stat-item">
          <div class="filter-stat-value">-</div>
          <div class="filter-stat-label">Messages Matched</div>
        </div>
        <div class="filter-stat-item">
          <div class="filter-stat-value">-</div>
          <div class="filter-stat-label">Match Rate</div>
        </div>
      `;
      
      // Update efficiency bar
      const efficiencyBar = this.container.querySelector('.filter-efficiency-progress');
      if (efficiencyBar) {
        efficiencyBar.style.width = '0%';
      }
      
      return;
    }
    
    // Update statistics display with actual data
    statsContainer.innerHTML = `
      <div class="filter-stat-item">
        <div class="filter-stat-value">${stats.received.toLocaleString()}</div>
        <div class="filter-stat-label">Messages Received</div>
      </div>
      <div class="filter-stat-item">
        <div class="filter-stat-value">${stats.matched.toLocaleString()}</div>
        <div class="filter-stat-label">Messages Matched</div>
      </div>
      <div class="filter-stat-item">
        <div class="filter-stat-value">${stats.matchRate.toFixed(2)}%</div>
        <div class="filter-stat-label">Match Rate</div>
      </div>
    `;
    
    // Add second row for processing time and last match
    statsContainer.innerHTML += `
      <div class="filter-stat-item">
        <div class="filter-stat-value">${stats.avgProcessingTime.toFixed(2)}ms</div>
        <div class="filter-stat-label">Avg Processing Time</div>
      </div>
      <div class="filter-stat-item">
        <div class="filter-stat-value">${new Date(stats.lastMatched).toLocaleString()}</div>
        <div class="filter-stat-label">Last Match</div>
      </div>
      <div class="filter-stat-item">
        <div class="filter-stat-value">${stats.efficiency}</div>
        <div class="filter-stat-label">Efficiency Score</div>
      </div>
    `;
    
    // Update efficiency bar
    const efficiencyBar = this.container.querySelector('.filter-efficiency-progress');
    if (efficiencyBar) {
      efficiencyBar.style.width = `${stats.efficiency}%`;
      
      // Add color based on efficiency
      if (stats.efficiency < 50) {
        efficiencyBar.style.backgroundColor = 'var(--btn-danger-bg, #dc3545)';
      } else if (stats.efficiency < 80) {
        efficiencyBar.style.backgroundColor = 'var(--warning-color, #ffc107)';
      } else {
        efficiencyBar.style.backgroundColor = 'var(--btn-primary-bg, #0d6efd)';
      }
    }
    
    // Update efficiency label
    const efficiencyLabel = this.container.querySelector('.filter-efficiency-labels div:last-child');
    if (efficiencyLabel) {
      efficiencyLabel.textContent = `${stats.efficiency}%`;
    }
  }

  /**
   * Filters the list of filters based on search query and active category
   * @private
   */
  _filterFilterList() {
    // Get all filter items
    const filterItems = this.container.querySelectorAll('.filter-item');
    
    // Clear previous list if empty search and no category filter
    if (!this.searchQuery && this.activeCategory === 'all') {
      this._renderFilterItems();
      return;
    }
    
    // Show/hide items based on search query and category
    filterItems.forEach(item => {
      const filterName = item.querySelector('.filter-item-name').textContent.toLowerCase();
      const filterCategory = item.dataset.category.toLowerCase();
      
      const matchesSearch = !this.searchQuery || filterName.includes(this.searchQuery.toLowerCase());
      const matchesCategory = this.activeCategory === 'all' || filterCategory === this.activeCategory;
      
      if (matchesSearch && matchesCategory) {
        item.style.display = '';
      } else {
        item.style.display = 'none';
      }
    });
  }

  /**
   * Creates a new filter
   * @private
   */
  _createNewFilter() {
    // Show the filter creation modal
    this.filterModal.showCreateModal({
      name: '',
      category: 'general',
      description: '',
      definition: {
        entityType: '',
        conditions: {
          operator: 'AND',
          conditions: []
        }
      }
    });
  }

  /**
   * Selects a category for filtering
   * @param {string} category - Category to select
   * @private
   */
  _selectCategory(category) {
    // Update active category
    this.activeCategory = category;
    
    // Update UI to reflect selected category
    const categories = this.container.querySelectorAll('.filter-category');
    categories.forEach(cat => {
      if (cat.dataset.category === category) {
        cat.classList.add('active');
      } else {
        cat.classList.remove('active');
      }
    });
    
    // Filter the list based on new category and existing search
    this._filterFilterList();
  }

  /**
   * Renders the list of filter items
   * @private
   */
  _renderFilterItems() {
    const filterList = this.container.querySelector('.filter-list');
    if (!filterList) return;
    
    // Clear list
    filterList.innerHTML = '';
    
    // If no filters, show empty state
    if (this.filters.length === 0) {
      filterList.appendChild(this._createEmptyState());
      return;
    }
    
    // Create items for each filter
    this.filters.forEach(filter => {
      const filterItem = this._createFilterItem(filter);
      filterList.appendChild(filterItem);
    });
  }
  
  /**
   * Creates a filter item element
   * @param {Object} filter - Filter data
   * @returns {HTMLElement} Filter item element
   * @private
   */
  _createFilterItem(filter) {
    const item = document.createElement('div');
    item.className = 'filter-item';
    item.dataset.id = filter.id;
    item.dataset.category = filter.category.toLowerCase();
    
    if (filter.id === this.activeFilterId) {
      item.classList.add('active');
    }
    
    // Add click event to select filter
    item.addEventListener('click', () => {
      this.setActiveFilter(filter.id);
    });
    
    // Create item content
    const header = document.createElement('div');
    header.className = 'filter-item-header';
    
    const name = document.createElement('h5');
    name.className = 'filter-item-name';
    name.textContent = filter.name;
    header.appendChild(name);
    
    const category = document.createElement('div');
    category.className = 'filter-item-category';
    category.textContent = filter.category;
    header.appendChild(category);
    
    item.appendChild(header);
    
    // Description
    if (filter.description) {
      const description = document.createElement('div');
      description.className = 'filter-item-description';
      description.textContent = filter.description;
      item.appendChild(description);
    }
    
    // Meta info (created date, etc)
    const meta = document.createElement('div');
    meta.className = 'filter-item-meta';
    
    const createdDate = new Date(filter.createdAt);
    const dateText = document.createElement('div');
    dateText.textContent = `Created: ${createdDate.toLocaleDateString()}`;
    meta.appendChild(dateText);
    
    item.appendChild(meta);
    
    return item;
  }

  /**
   * Set the active filter and update UI
   * @param {string} filterId - Filter ID to set as active
   * @public
   */
  setActiveFilter(filterId) {
    // Update active filter ID
    this.activeFilterId = filterId;
    
    // Update filter list UI
    const filterItems = this.container.querySelectorAll('.filter-item');
    filterItems.forEach(item => {
      if (item.dataset.id === filterId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
    
    // Update filter details
    this._updateFilterDetails();
    
    // Update filter statistics
    this._updateFilterStats();
    
    // Call onLoadFilter callback if provided
    if (this.options.onLoadFilter) {
      const filter = this.filters.find(f => f.id === filterId);
      if (filter) {
        this.options.onLoadFilter(filter);
      }
    }
  }
  
  /**
   * Update filter details content
   * @private
   */
  _updateFilterDetails() {
    const detailsContent = this.container.querySelector('.filter-details-content');
    if (!detailsContent) return;
    
    // Clear content
    detailsContent.innerHTML = '';
    
    // If no active filter, show empty state
    if (!this.activeFilterId) {
      const emptyMessage = document.createElement('div');
      emptyMessage.className = 'filter-empty-state';
      emptyMessage.innerHTML = '<i class="fas fa-filter" style="font-size: 2rem; opacity: 0.3; margin-bottom: 1rem;"></i><br>Select a filter to view details or create a new filter.';
      detailsContent.appendChild(emptyMessage);
      return;
    }
    
    // Get filter data
    const filter = this.filters.find(f => f.id === this.activeFilterId);
    if (!filter) {
      // Filter not found
      const errorMessage = document.createElement('div');
      errorMessage.className = 'filter-empty-state';
      errorMessage.innerHTML = '<i class="fas fa-exclamation-circle" style="font-size: 2rem; opacity: 0.3; margin-bottom: 1rem; color: var(--btn-danger-bg, #dc3545);"></i><br>Filter not found.';
      detailsContent.appendChild(errorMessage);
      return;
    }
    
    // Update header title
    const detailsTitle = this.container.querySelector('.filter-details-title');
    if (detailsTitle) {
      detailsTitle.textContent = filter.name;
    }
    
    // Create details sections
    
    // Filter info section
    const infoSection = document.createElement('div');
    infoSection.className = 'filter-details-section';
    
    const infoTitle = document.createElement('h5');
    infoTitle.className = 'filter-details-section-title';
    infoTitle.textContent = 'Filter Information';
    infoSection.appendChild(infoTitle);
    
    const infoGrid = document.createElement('div');
    infoGrid.className = 'filter-details-info';
    
    // ID
    const idItem = document.createElement('div');
    idItem.className = 'filter-info-item';
    
    const idLabel = document.createElement('div');
    idLabel.className = 'filter-info-label';
    idLabel.textContent = 'ID';
    idItem.appendChild(idLabel);
    
    const idValue = document.createElement('div');
    idValue.className = 'filter-info-value';
    idValue.textContent = filter.id;
    idItem.appendChild(idValue);
    
    infoGrid.appendChild(idItem);
    
    // Category
    const categoryItem = document.createElement('div');
    categoryItem.className = 'filter-info-item';
    
    const categoryLabel = document.createElement('div');
    categoryLabel.className = 'filter-info-label';
    categoryLabel.textContent = 'Category';
    categoryItem.appendChild(categoryLabel);
    
    const categoryValue = document.createElement('div');
    categoryValue.className = 'filter-info-value';
    categoryValue.textContent = filter.category;
    categoryItem.appendChild(categoryValue);
    
    infoGrid.appendChild(categoryItem);
    
    // Created date
    const createdItem = document.createElement('div');
    createdItem.className = 'filter-info-item';
    
    const createdLabel = document.createElement('div');
    createdLabel.className = 'filter-info-label';
    createdLabel.textContent = 'Created';
    createdItem.appendChild(createdLabel);
    
    const createdValue = document.createElement('div');
    createdValue.className = 'filter-info-value';
    createdValue.textContent = new Date(filter.createdAt).toLocaleString();
    createdItem.appendChild(createdValue);
    
    infoGrid.appendChild(createdItem);
    
    // Updated date
    const updatedItem = document.createElement('div');
    updatedItem.className = 'filter-info-item';
    
    const updatedLabel = document.createElement('div');
    updatedLabel.className = 'filter-info-label';
    updatedLabel.textContent = 'Last Updated';
    updatedItem.appendChild(updatedLabel);
    
    const updatedValue = document.createElement('div');
    updatedValue.className = 'filter-info-value';
    updatedValue.textContent = filter.updatedAt ? new Date(filter.updatedAt).toLocaleString() : 'N/A';
    updatedItem.appendChild(updatedValue);
    
    infoGrid.appendChild(updatedItem);
    
    infoSection.appendChild(infoGrid);
    
    // Description
    if (filter.description) {
      const descSection = document.createElement('div');
      descSection.className = 'filter-details-description';
      descSection.textContent = filter.description;
      infoSection.appendChild(descSection);
    }
    
    detailsContent.appendChild(infoSection);
    
    // Statistics section
    const statsSection = document.createElement('div');
    statsSection.className = 'filter-details-section';
    
    const statsTitle = document.createElement('h5');
    statsTitle.className = 'filter-details-section-title';
    statsTitle.textContent = 'Performance Statistics';
    statsSection.appendChild(statsTitle);
    
    // Stats grid
    const statsGrid = document.createElement('div');
    statsGrid.className = 'filter-stats';
    statsSection.appendChild(statsGrid);
    
    // Efficiency bar
    const efficiency = document.createElement('div');
    efficiency.className = 'filter-efficiency';
    
    const efficiencyBar = document.createElement('div');
    efficiencyBar.className = 'filter-efficiency-bar';
    
    const efficiencyProgress = document.createElement('div');
    efficiencyProgress.className = 'filter-efficiency-progress';
    efficiencyBar.appendChild(efficiencyProgress);
    
    efficiency.appendChild(efficiencyBar);
    
    const efficiencyLabels = document.createElement('div');
    efficiencyLabels.className = 'filter-efficiency-labels';
    
    const efficiencyLabelText = document.createElement('div');
    efficiencyLabelText.textContent = 'Efficiency';
    efficiencyLabels.appendChild(efficiencyLabelText);
    
    const efficiencyValue = document.createElement('div');
    efficiencyValue.textContent = '0%';
    efficiencyLabels.appendChild(efficiencyValue);
    
    efficiency.appendChild(efficiencyLabels);
    
    statsSection.appendChild(efficiency);
    
    detailsContent.appendChild(statsSection);
    
    // Filter JSON section
    const jsonSection = document.createElement('div');
    jsonSection.className = 'filter-details-section';
    
    const jsonTitle = document.createElement('h5');
    jsonTitle.className = 'filter-details-section-title';
    jsonTitle.textContent = 'Filter Definition';
    jsonSection.appendChild(jsonTitle);
    
    const jsonPreview = document.createElement('pre');
    jsonPreview.className = 'filter-json-preview';
    jsonPreview.textContent = JSON.stringify(filter.definition, null, 2);
    jsonSection.appendChild(jsonPreview);
    
    detailsContent.appendChild(jsonSection);
    
    // Action buttons
    const actions = document.createElement('div');
    actions.className = 'filter-actions';
    
    const useButton = document.createElement('button');
    useButton.className = 'btn-primary';
    useButton.innerHTML = '<i class="fas fa-check"></i> Use This Filter';
    useButton.addEventListener('click', () => {
      if (this.options.onLoadFilter) {
        this.options.onLoadFilter(filter);
      }
      toastService.success(`Filter "${filter.name}" applied`);
    });
    actions.appendChild(useButton);
    
    detailsContent.appendChild(actions);
    
    // Update stats display
    this._updateFilterStats();
  }

  /**
   * Opens edit interface for current filter
   * @private
   */
  _editCurrentFilter() {
    if (!this.activeFilterId) {
      toastService.warning('Please select a filter to edit');
      return;
    }
    
    const filter = this.filters.find(f => f.id === this.activeFilterId);
    if (!filter) return;
    
    // Show the filter edit modal
    this.filterModal.showEditModal(filter);
  }

  /**
   * Duplicates the current filter
   * @private
   */
  _duplicateCurrentFilter() {
    if (!this.activeFilterId) {
      toastService.warning('Please select a filter to duplicate');
      return;
    }
    
    const filter = this.filters.find(f => f.id === this.activeFilterId);
    if (!filter) return;
    
    // Show the filter duplication modal
    this.filterModal.showDuplicateModal(filter);
  }

  /**
   * Deletes the current filter after confirmation
   * @private
   */
  _deleteCurrentFilter() {
    if (!this.activeFilterId) {
      toastService.warning('Please select a filter to delete');
      return;
    }
    
    const filter = this.filters.find(f => f.id === this.activeFilterId);
    if (!filter) return;
    
    // Create and show a confirmation dialog
    const confirmDialog = document.createElement('div');
    confirmDialog.className = 'confirm-dialog';
    confirmDialog.innerHTML = `
      <div class="confirm-dialog-backdrop"></div>
      <div class="confirm-dialog-container">
        <div class="confirm-dialog-header">
          <h4>Confirm Deletion</h4>
        </div>
        <div class="confirm-dialog-body">
          <p>Are you sure you want to delete the filter "${filter.name}"?</p>
          <p class="text-danger">This action cannot be undone.</p>
        </div>
        <div class="confirm-dialog-footer">
          <button class="btn-default" id="cancelDeleteBtn">Cancel</button>
          <button class="btn-danger" id="confirmDeleteBtn">Delete</button>
        </div>
      </div>
    `;
    
    // Add styles for the dialog
    const dialogStyle = document.createElement('style');
    dialogStyle.textContent = `
      .confirm-dialog {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
      }
      
      .confirm-dialog-backdrop {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
      }
      
      .confirm-dialog-container {
        position: relative;
        width: 400px;
        max-width: 90%;
        background-color: var(--bg-color, #fff);
        border-radius: 0.25rem;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
        z-index: 1;
      }
      
      .confirm-dialog-header {
        padding: 1rem;
        border-bottom: 1px solid var(--border-color, #dee2e6);
      }
      
      .confirm-dialog-header h4 {
        margin: 0;
        font-size: 1.25rem;
      }
      
      .confirm-dialog-body {
        padding: 1rem;
      }
      
      .confirm-dialog-footer {
        padding: 1rem;
        border-top: 1px solid var(--border-color, #dee2e6);
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
      }
      
      .text-danger {
        color: var(--btn-danger-bg, #dc3545);
      }
    `;
    
    document.head.appendChild(dialogStyle);
    document.body.appendChild(confirmDialog);
    
    // Add event listeners
    const cancelBtn = document.getElementById('cancelDeleteBtn');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    
    cancelBtn.addEventListener('click', () => {
      document.body.removeChild(confirmDialog);
    });
    
    confirmBtn.addEventListener('click', async () => {
      // Remove dialog
      document.body.removeChild(confirmDialog);
      
      try {
        // Delete from backend
        const response = await fetch(`${this.options.filterListUrl}/${filter.id}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`Failed to delete filter: ${response.statusText}`);
        }
        
        // Remove from filters array
        this.filters = this.filters.filter(f => f.id !== this.activeFilterId);
        
        // Clear active filter
        this.activeFilterId = null;
        
        // Update UI
        this._renderFilterItems();
        
        // Clear details view
        const detailsContent = this.container.querySelector('.filter-details-content');
        if (detailsContent) {
          detailsContent.innerHTML = '';
          const emptyMessage = document.createElement('div');
          emptyMessage.className = 'filter-empty-state';
          emptyMessage.innerHTML = '<i class="fas fa-filter" style="font-size: 2rem; opacity: 0.3; margin-bottom: 1rem;"></i><br>Select a filter to view details or create a new filter.';
          detailsContent.appendChild(emptyMessage);
        }
        
        // Call delete callback if provided
        if (this.options.onDeleteFilter) {
          this.options.onDeleteFilter(filter.id);
        }
        
        // Notify success
        toastService.success(`Filter "${filter.name}" deleted successfully`);
      } catch (error) {
        console.error('Error deleting filter:', error);
        toastService.error(`Failed to delete filter: ${error.message}`);
      }
    });
  }
  
  /**
   * Handle filter save from modal
   * @param {Object} filter - Filter data
   * @param {boolean} isEdit - Whether this is an edit operation
   * @private
   */
  async _handleFilterSave(filter, isEdit) {
    try {
      // Validate filter
      const validation = this.validator.validateFilter(filter);
      if (!validation.valid) {
        toastService.error(`Validation failed: ${validation.errors[0]}`);
        return;
      }
      
      // Prepare request
      const url = isEdit ? `${this.options.filterListUrl}/${filter.id}` : this.options.filterListUrl;
      const method = isEdit ? 'PUT' : 'POST';
      
      // Save to backend
      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(filter)
      });
      
      if (!response.ok) {
        throw new Error(`Failed to save filter: ${response.statusText}`);
      }
      
      // Get updated/created filter from response
      const savedFilter = await response.json();
      
      // Update local data
      if (isEdit) {
        // Update existing filter
        const index = this.filters.findIndex(f => f.id === filter.id);
        if (index !== -1) {
          this.filters[index] = savedFilter;
        }
      } else {
        // Add new filter
        this.filters.push(savedFilter);
      }
      
      // Update UI
      this._renderFilterItems();
      
      // Set active filter to the saved filter
      this.setActiveFilter(savedFilter.id);
      
      // Notify success
      const action = isEdit ? 'updated' : 'created';
      toastService.success(`Filter "${savedFilter.name}" ${action} successfully`);
      
      return savedFilter;
    } catch (error) {
      console.error('Error saving filter:', error);
      toastService.error(`Failed to save filter: ${error.message}`);
      return null;
    }
  }
  
  /**
   * Export filter as JSON
   * @param {string} filterId - Filter ID to export (defaults to active filter)
   * @returns {Object|null} Filter data or null if not found
   * @public
   */
  exportFilter(filterId = null) {
    const id = filterId || this.activeFilterId;
    if (!id) return null;
    
    const filter = this.filters.find(f => f.id === id);
    return filter ? { ...filter } : null;
  }
  
  /**
   * Import filter from JSON
   * @param {Object} filterData - Filter data to import
   * @returns {boolean} Success status
   * @public
   */
  importFilter(filterData) {
    if (!filterData || !filterData.id || !filterData.name || !filterData.definition) {
      console.error('Invalid filter data for import');
      toastService.error('Invalid filter data for import');
      return false;
    }
    
    // Validate the filter
    const validation = this.validator.validateFilter(filterData);
    if (!validation.valid) {
      toastService.error(`Filter validation failed: ${validation.errors[0]}`);
      return false;
    }
    
    // Check if filter with same ID already exists
    const existingIndex = this.filters.findIndex(f => f.id === filterData.id);
    
    if (existingIndex >= 0) {
      // Update existing filter
      this.filters[existingIndex] = {
        ...filterData,
        updatedAt: new Date().toISOString()
      };
    } else {
      // Add new filter
      this.filters.push({
        ...filterData,
        createdAt: filterData.createdAt || new Date().toISOString()
      });
    }
    
    // Update UI
    this._renderFilterItems();
    
    // Set as active filter
    this.setActiveFilter(filterData.id);
    
    // Notify user
    toastService.success(`Filter "${filterData.name}" imported successfully`);
    
    return true;
  }
  
  /**
   * Get all filters
   * @returns {Array} Array of filter objects
   * @public
   */
  getFilters() {
    return [...this.filters];
  }
  
  /**
   * Get active filter
   * @returns {Object|null} Active filter or null if none
   * @public
   */
  getActiveFilter() {
    if (!this.activeFilterId) return null;
    return this.filters.find(f => f.id === this.activeFilterId) || null;
  }
  
  /**
   * Refresh filter statistics
   * @returns {Promise<void>}
   * @public
   */
  async refreshStats() {
    try {
      await this._loadFilterStats();
      toastService.info('Filter statistics refreshed');
    } catch (error) {
      console.error('Error refreshing filter statistics:', error);
      toastService.error('Failed to refresh filter statistics');
    }
  }
}