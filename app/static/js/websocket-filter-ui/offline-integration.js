/**
 * MagnetoCursor - WebSocket Filter UI Offline Integration
 * 
 * Integrates offline functionality with the WebSocket Filter UI components
 * enabling creating, editing, and managing filters while offline with
 * background synchronization when reconnecting.
 */

import { FilterBuilder } from './filter-builder.js';
import { FilterManager } from './filter-manager.js';
import FilterValidator from './filter-validator.js';
import OfflineManager from '../offline/index.js';
import { toastService } from '../services/toast-service.js';

/**
 * Offline-Enabled WebSocket Filter UI
 */
export class OfflineFilterUI {
  /**
   * Initialize the OfflineFilterUI
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    // Default options
    this.options = {
      builderContainerId: 'filter-builder-container',
      managerContainerId: 'filter-manager-container',
      filterListEndpoint: '/api/websocket/filters',
      filterStatsEndpoint: '/api/websocket/filter-stats',
      testFilterEndpoint: '/api/websocket/test-filter',
      fieldDefinitionsEndpoint: '/api/websocket/fields',
      entityTypesEndpoint: '/api/websocket/entity-types',
      autoSync: true,
      syncInterval: 60000, // 1 minute
      showOfflineIndicator: true,
      darkMode: false,
      ...options
    };

    // State variables
    this.isInitialized = false;
    this.fields = [];
    this.entityTypes = [];
    this.filterCategories = ['General', 'Campaigns', 'Notifications', 'Alerts', 'Custom'];
    this.filterBuilder = null;
    this.filterManager = null;
    this.offlineStatusElement = null;
    this.pendingChangesElement = null;
    this.syncNowButton = null;
    this.validator = null;
    
    // Confirm containers exist
    const builderContainer = document.getElementById(this.options.builderContainerId);
    const managerContainer = document.getElementById(this.options.managerContainerId);
    
    if (!builderContainer || !managerContainer) {
      throw new Error('Filter containers not found. Make sure the container elements exist in the DOM.');
    }
  }

  /**
   * Initialize the offline filter UI
   * @returns {Promise<boolean>} - Whether initialization was successful
   */
  async initialize() {
    try {
      // Initialize the OfflineManager
      await OfflineManager.initialize({
        registerServiceWorker: true,
        syncEnabled: this.options.autoSync,
        syncInterval: this.options.syncInterval,
        syncOnReconnect: true,
        offlineIndicator: this.options.showOfflineIndicator
      });
      
      // Fetch field definitions and entity types
      await this._fetchFieldDefinitions();
      
      // Initialize validator
      this.validator = new FilterValidator({
        fields: this.fields,
        entityTypes: this.entityTypes
      });
      
      // Create UI elements for offline status
      if (this.options.showOfflineIndicator) {
        this._createOfflineStatusUI();
      }
      
      // Initialize the filter builder
      this._initializeFilterBuilder();
      
      // Initialize the filter manager
      this._initializeFilterManager();
      
      // Set up event listeners
      this._setupEventListeners();
      
      // Set up conflict resolution
      this._setupConflictResolution();
      
      // Update UI with initial status
      this._updateOfflineUIStatus();
      
      // Mark as initialized
      this.isInitialized = true;
      
      return true;
    } catch (error) {
      toastService.error(`Failed to initialize offline filter UI: ${error.message}`);
      console.error('Error initializing offline filter UI:', error);
      return false;
    }
  }
  
  /**
   * Fetch field definitions and entity types from the server
   * @private
   */
  async _fetchFieldDefinitions() {
    try {
      // First try to get from cache
      const cachedFields = await OfflineManager.getCachedFieldDefinitions();
      const cachedEntityTypes = await OfflineManager.getCachedEntityTypes();
      
      if (cachedFields?.length > 0 && cachedEntityTypes?.length > 0) {
        this.fields = cachedFields;
        this.entityTypes = cachedEntityTypes;
      }
      
      // Try to fetch the latest from server if online
      if (OfflineManager.getNetworkStatus()) {
        try {
          const [fieldsResponse, typesResponse] = await Promise.all([
            fetch(this.options.fieldDefinitionsEndpoint),
            fetch(this.options.entityTypesEndpoint)
          ]);
          
          if (fieldsResponse.ok && typesResponse.ok) {
            const fieldsData = await fieldsResponse.json();
            const typesData = await typesResponse.json();
            
            this.fields = fieldsData.fields || [];
            this.entityTypes = typesData.entityTypes || [];
            
            // Cache for offline use
            await OfflineManager.cacheFieldDefinitions(this.fields);
            await OfflineManager.cacheEntityTypes(this.entityTypes);
          }
        } catch (error) {
          console.warn('Error fetching field definitions from server, using cached data:', error);
          
          // If we don't have cached data and server fetch failed, use defaults
          if (this.fields.length === 0) {
            this.fields = this._getDefaultFields();
          }
          
          if (this.entityTypes.length === 0) {
            this.entityTypes = this._getDefaultEntityTypes();
          }
        }
      } else if (this.fields.length === 0 || this.entityTypes.length === 0) {
        // Use defaults if offline and no cached data
        this.fields = this._getDefaultFields();
        this.entityTypes = this._getDefaultEntityTypes();
      }
    } catch (error) {
      console.error('Error fetching field definitions:', error);
      
      // Use defaults as fallback
      this.fields = this._getDefaultFields();
      this.entityTypes = this._getDefaultEntityTypes();
    }
  }
  
  /**
   * Get default fields in case server fetch fails
   * @returns {Array} Default fields
   * @private
   */
  _getDefaultFields() {
    return [
      { id: 'entity_type', name: 'Entity Type', type: 'string', entityType: 'all' },
      { id: 'entity_id', name: 'Entity ID', type: 'string', entityType: 'all' },
      { id: 'action', name: 'Action', type: 'string', entityType: 'all' },
      { id: 'timestamp', name: 'Timestamp', type: 'date', entityType: 'all' },
      { id: 'user_id', name: 'User ID', type: 'string', entityType: 'all' },
      { id: 'campaign_id', name: 'Campaign ID', type: 'string', entityType: 'campaign' },
      { id: 'platform', name: 'Platform', type: 'string', entityType: 'campaign' },
      { id: 'status', name: 'Status', type: 'string', entityType: 'campaign' },
      { id: 'budget', name: 'Budget', type: 'number', entityType: 'campaign' },
      { id: 'impressions', name: 'Impressions', type: 'number', entityType: 'analytics' },
      { id: 'clicks', name: 'Clicks', type: 'number', entityType: 'analytics' },
      { id: 'conversions', name: 'Conversions', type: 'number', entityType: 'analytics' },
      { id: 'tags', name: 'Tags', type: 'array', entityType: 'all' },
      { id: 'is_active', name: 'Is Active', type: 'boolean', entityType: 'all' }
    ];
  }
  
  /**
   * Get default entity types in case server fetch fails
   * @returns {Array} Default entity types
   * @private
   */
  _getDefaultEntityTypes() {
    return [
      { id: 'campaign', name: 'Campaign' },
      { id: 'ad_set', name: 'Ad Set' },
      { id: 'ad', name: 'Ad' },
      { id: 'user', name: 'User' },
      { id: 'analytics', name: 'Analytics' },
      { id: 'notification', name: 'Notification' }
    ];
  }
  
  /**
   * Create UI elements for offline status
   * @private
   */
  _createOfflineStatusUI() {
    // Create offline status bar
    const statusBar = document.createElement('div');
    statusBar.className = 'offline-status-bar';
    statusBar.style.cssText = `
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 16px;
      background-color: var(--bg-color, #f8f9fa);
      border-bottom: 1px solid var(--border-color, #dee2e6);
      font-size: 14px;
    `;
    
    if (this.options.darkMode) {
      statusBar.style.backgroundColor = 'var(--bg-color, #212529)';
      statusBar.style.borderColor = 'var(--border-color, #495057)';
      statusBar.style.color = 'var(--text-color, #f8f9fa)';
    }
    
    // Status indicator
    const statusContainer = document.createElement('div');
    statusContainer.className = 'status-container';
    statusContainer.style.display = 'flex';
    statusContainer.style.alignItems = 'center';
    statusContainer.style.gap = '8px';
    
    this.offlineStatusElement = document.createElement('span');
    this.offlineStatusElement.className = 'offline-status';
    this.offlineStatusElement.style.display = 'flex';
    this.offlineStatusElement.style.alignItems = 'center';
    this.offlineStatusElement.style.gap = '6px';
    
    const statusDot = document.createElement('span');
    statusDot.className = 'status-dot';
    statusDot.style.cssText = `
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background-color: #198754;
    `;
    
    const statusText = document.createElement('span');
    statusText.textContent = 'Online';
    
    this.offlineStatusElement.appendChild(statusDot);
    this.offlineStatusElement.appendChild(statusText);
    
    this.pendingChangesElement = document.createElement('span');
    this.pendingChangesElement.className = 'pending-changes';
    this.pendingChangesElement.style.marginLeft = '16px';
    this.pendingChangesElement.style.padding = '2px 8px';
    this.pendingChangesElement.style.backgroundColor = 'var(--btn-primary-bg, #0d6efd)';
    this.pendingChangesElement.style.color = 'white';
    this.pendingChangesElement.style.borderRadius = '12px';
    this.pendingChangesElement.style.fontSize = '12px';
    this.pendingChangesElement.style.display = 'none'; // Hide initially
    this.pendingChangesElement.textContent = '0 pending changes';
    
    statusContainer.appendChild(this.offlineStatusElement);
    statusContainer.appendChild(this.pendingChangesElement);
    
    // Actions
    const actionsContainer = document.createElement('div');
    actionsContainer.className = 'actions-container';
    actionsContainer.style.display = 'flex';
    actionsContainer.style.gap = '8px';
    
    this.syncNowButton = document.createElement('button');
    this.syncNowButton.className = 'sync-now-button btn-primary btn-sm';
    this.syncNowButton.style.cssText = `
      padding: 4px 12px;
      background-color: var(--btn-primary-bg, #0d6efd);
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 6px;
    `;
    this.syncNowButton.innerHTML = '<i class="fas fa-sync"></i> Sync Now';
    this.syncNowButton.disabled = true; // Disable initially
    
    const clearOfflineDataButton = document.createElement('button');
    clearOfflineDataButton.className = 'clear-offline-button btn-danger btn-sm';
    clearOfflineDataButton.style.cssText = `
      padding: 4px 12px;
      background-color: var(--btn-danger-bg, #dc3545);
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 6px;
    `;
    clearOfflineDataButton.innerHTML = '<i class="fas fa-trash"></i> Clear Offline Data';
    
    actionsContainer.appendChild(this.syncNowButton);
    actionsContainer.appendChild(clearOfflineDataButton);
    
    statusBar.appendChild(statusContainer);
    statusBar.appendChild(actionsContainer);
    
    // Add to document before the builder container
    const builderContainer = document.getElementById(this.options.builderContainerId);
    if (builderContainer && builderContainer.parentNode) {
      builderContainer.parentNode.insertBefore(statusBar, builderContainer);
    }
    
    // Add event listeners for buttons
    this.syncNowButton.addEventListener('click', () => {
      this._syncNow();
    });
    
    clearOfflineDataButton.addEventListener('click', () => {
      this._clearOfflineData();
    });
  }
  
  /**
   * Initialize the filter builder with offline support
   * @private
   */
  _initializeFilterBuilder() {
    const builderContainer = document.getElementById(this.options.builderContainerId);
    if (!builderContainer) return;
    
    // Initialize the FilterBuilder
    this.filterBuilder = new FilterBuilder(builderContainer, {
      availableFields: this.fields,
      filterableEntityTypes: this.entityTypes,
      darkMode: this.options.darkMode,
      onChange: (filter) => {
        // Handle filter changes
      },
      onSave: async (filter) => {
        return this._saveFilter(filter);
      },
      onTest: async (filter) => {
        return this._testFilter(filter);
      }
    });
    
    // Add offline indicator to the filter builder
    if (this.options.showOfflineIndicator) {
      this._addOfflineIndicatorToBuilder();
    }
  }
  
  /**
   * Initialize the filter manager with offline support
   * @private
   */
  _initializeFilterManager() {
    const managerContainer = document.getElementById(this.options.managerContainerId);
    if (!managerContainer) return;
    
    // Initialize FilterManager
    this.filterManager = new FilterManager(managerContainer, {
      filterListUrl: this.options.filterListEndpoint,
      filterStatsUrl: this.options.filterStatsEndpoint,
      categories: this.filterCategories,
      darkMode: this.options.darkMode,
      fields: this.fields,
      entityTypes: this.entityTypes,
      onLoadFilter: (filter) => {
        return this._loadFilter(filter);
      },
      onDeleteFilter: (filterId) => {
        return this._deleteFilter(filterId);
      },
      onDuplicateFilter: (filter) => {
        return this._duplicateFilter(filter);
      }
    });
  }
  
  /**
   * Add offline indicator to the filter builder
   * @private
   */
  _addOfflineIndicatorToBuilder() {
    const builderContainer = document.getElementById(this.options.builderContainerId);
    const filterToolbar = builderContainer?.querySelector('.filter-toolbar');
    
    if (filterToolbar) {
      const offlineIndicator = document.createElement('div');
      offlineIndicator.className = 'filter-offline-indicator';
      offlineIndicator.style.cssText = `
        margin-left: auto;
        padding: 0.25rem 0.5rem;
        font-size: 0.75rem;
        color: white;
        background-color: var(--btn-danger-bg, #dc3545);
        border-radius: 0.25rem;
        display: none;
      `;
      offlineIndicator.textContent = 'Offline';
      
      // Insert before actions
      const actions = filterToolbar.querySelector('.filter-actions');
      if (actions) {
        filterToolbar.insertBefore(offlineIndicator, actions);
      } else {
        filterToolbar.appendChild(offlineIndicator);
      }
    }
  }
  
  /**
   * Set up event listeners for offline functionality
   * @private
   */
  _setupEventListeners() {
    // Listen for online/offline events
    OfflineManager.addConnectionListener((status) => {
      this._updateOfflineUIStatus();
    });
  }
  
  /**
   * Set up conflict resolution
   * @private
   */
  _setupConflictResolution() {
    OfflineManager.setConflictHandler(async (localChange, serverData) => {
      // Return a promise that resolves with the conflict resolution choice
      return new Promise((resolve) => {
        // Create conflict resolution dialog element
        const dialog = document.createElement('div');
        dialog.className = 'conflict-dialog';
        dialog.style.cssText = `
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 9999;
        `;
        
        // Dialog content
        const content = document.createElement('div');
        content.className = 'conflict-content';
        content.style.cssText = `
          background-color: var(--bg-color, #fff);
          border-radius: 8px;
          padding: 20px;
          width: 500px;
          max-width: 90%;
        `;
        
        if (this.options.darkMode) {
          content.style.backgroundColor = 'var(--bg-color, #212529)';
          content.style.color = 'var(--text-color, #f8f9fa)';
          content.style.borderColor = 'var(--border-color, #495057)';
        }
        
        // Dialog header
        const header = document.createElement('h3');
        header.style.cssText = `
          margin-top: 0;
          margin-bottom: 15px;
          font-size: 18px;
          border-bottom: 1px solid var(--border-color, #dee2e6);
          padding-bottom: 10px;
        `;
        header.textContent = 'Conflict Detected';
        
        // Dialog message
        const message = document.createElement('p');
        message.textContent = 'Changes have been made both locally and on the server. How would you like to resolve this conflict?';
        
        // Buttons
        const buttons = document.createElement('div');
        buttons.style.cssText = `
          display: flex;
          gap: 10px;
          margin-top: 20px;
          justify-content: flex-end;
        `;
        
        const useLocalButton = document.createElement('button');
        useLocalButton.className = 'btn-primary btn-sm';
        useLocalButton.textContent = 'Use My Changes';
        useLocalButton.style.cssText = `
          padding: 8px 16px;
          background-color: var(--btn-primary-bg, #0d6efd);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        `;
        
        const useServerButton = document.createElement('button');
        useServerButton.className = 'btn-default btn-sm';
        useServerButton.textContent = 'Use Server Changes';
        useServerButton.style.cssText = `
          padding: 8px 16px;
          background-color: var(--btn-default-bg, #f8f9fa);
          color: var(--btn-default-text, #333);
          border: 1px solid var(--btn-default-border, #dee2e6);
          border-radius: 4px;
          cursor: pointer;
        `;
        
        const mergeButton = document.createElement('button');
        mergeButton.className = 'btn-success btn-sm';
        mergeButton.textContent = 'Merge Changes';
        mergeButton.style.cssText = `
          padding: 8px 16px;
          background-color: var(--btn-success-bg, #198754);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        `;
        
        // Add event listeners
        useLocalButton.addEventListener('click', () => {
          dialog.remove();
          resolve({
            resolved: true,
            action: 'local'
          });
        });
        
        useServerButton.addEventListener('click', () => {
          dialog.remove();
          resolve({
            resolved: true,
            action: 'server'
          });
        });
        
        mergeButton.addEventListener('click', () => {
          dialog.remove();
          
          // Create merged data with local changes taking precedence for conflicts
          const mergedData = { ...serverData, ...localChange.data };
          
          resolve({
            resolved: true,
            action: 'merged',
            mergedData
          });
        });
        
        // Add buttons to dialog
        buttons.appendChild(useServerButton);
        buttons.appendChild(mergeButton);
        buttons.appendChild(useLocalButton);
        
        // Add elements to content
        content.appendChild(header);
        content.appendChild(message);
        
        // Display changes
        const changesContainer = document.createElement('div');
        changesContainer.style.cssText = `
          display: flex;
          gap: 20px;
          margin-top: 15px;
        `;
        
        // Local changes
        const localContainer = document.createElement('div');
        localContainer.style.cssText = `
          flex: 1;
          border: 1px solid var(--border-color, #dee2e6);
          border-radius: 4px;
          padding: 10px;
        `;
        
        const localTitle = document.createElement('div');
        localTitle.style.cssText = `
          font-weight: bold;
          margin-bottom: 5px;
        `;
        localTitle.textContent = 'Your Changes';
        
        const localContent = document.createElement('pre');
        localContent.style.cssText = `
          font-size: 12px;
          white-space: pre-wrap;
          word-break: break-all;
          max-height: 150px;
          overflow-y: auto;
          margin: 0;
          background-color: var(--panel-bg, #f8f9fa);
          border-radius: 4px;
          padding: 5px;
        `;
        
        if (this.options.darkMode) {
          localContent.style.backgroundColor = 'var(--panel-bg, #343a40)';
          localContent.style.color = 'var(--text-color, #f8f9fa)';
        }
        
        localContent.textContent = JSON.stringify(localChange.data, null, 2);
        
        localContainer.appendChild(localTitle);
        localContainer.appendChild(localContent);
        
        // Server changes
        const serverContainer = document.createElement('div');
        serverContainer.style.cssText = `
          flex: 1;
          border: 1px solid var(--border-color, #dee2e6);
          border-radius: 4px;
          padding: 10px;
        `;
        
        const serverTitle = document.createElement('div');
        serverTitle.style.cssText = `
          font-weight: bold;
          margin-bottom: 5px;
        `;
        serverTitle.textContent = 'Server Changes';
        
        const serverContent = document.createElement('pre');
        serverContent.style.cssText = `
          font-size: 12px;
          white-space: pre-wrap;
          word-break: break-all;
          max-height: 150px;
          overflow-y: auto;
          margin: 0;
          background-color: var(--panel-bg, #f8f9fa);
          border-radius: 4px;
          padding: 5px;
        `;
        
        if (this.options.darkMode) {
          serverContent.style.backgroundColor = 'var(--panel-bg, #343a40)';
          serverContent.style.color = 'var(--text-color, #f8f9fa)';
        }
        
        serverContent.textContent = JSON.stringify(serverData, null, 2);
        
        serverContainer.appendChild(serverTitle);
        serverContainer.appendChild(serverContent);
        
        changesContainer.appendChild(localContainer);
        changesContainer.appendChild(serverContainer);
        
        content.appendChild(changesContainer);
        content.appendChild(buttons);
        
        dialog.appendChild(content);
        document.body.appendChild(dialog);
      });
    });
  }
  
  /**
   * Update UI based on offline status
   * @private
   */
  _updateOfflineUIStatus() {
    if (!this.options.showOfflineIndicator) return;
    
    const isOnline = OfflineManager.getNetworkStatus();
    const statusDot = this.offlineStatusElement?.querySelector('.status-dot');
    const statusText = this.offlineStatusElement?.querySelector('span:last-child');
    
    if (statusDot && statusText) {
      if (isOnline) {
        statusDot.style.backgroundColor = '#198754'; // Green
        statusText.textContent = 'Online';
        
        // Enable sync button if there are pending changes
        const pendingCount = OfflineManager.getPendingChangesCount();
        if (this.syncNowButton) {
          this.syncNowButton.disabled = pendingCount === 0;
        }
        
        // Hide offline indicators in UI
        document.querySelectorAll('.filter-offline-indicator').forEach(indicator => {
          indicator.style.display = 'none';
        });
      } else {
        statusDot.style.backgroundColor = '#dc3545'; // Red
        statusText.textContent = 'Offline';
        
        // Disable sync button when offline
        if (this.syncNowButton) {
          this.syncNowButton.disabled = true;
        }
        
        // Show offline indicators in UI
        document.querySelectorAll('.filter-offline-indicator').forEach(indicator => {
          indicator.style.display = 'block';
        });
      }
      
      // Update pending changes count
      this._updatePendingChangesCount();
    }
  }
  
  /**
   * Update pending changes count in UI
   * @private
   */
  _updatePendingChangesCount() {
    if (!this.pendingChangesElement) return;
    
    const pendingCount = OfflineManager.getPendingChangesCount();
    
    if (pendingCount > 0) {
      this.pendingChangesElement.textContent = `${pendingCount} pending ${pendingCount === 1 ? 'change' : 'changes'}`;
      this.pendingChangesElement.style.display = 'inline-block';
      
      // Enable sync button if online
      if (this.syncNowButton && OfflineManager.getNetworkStatus()) {
        this.syncNowButton.disabled = false;
      }
    } else {
      this.pendingChangesElement.style.display = 'none';
      if (this.syncNowButton) {
        this.syncNowButton.disabled = true;
      }
    }
  }
  
  /**
   * Sync pending changes with the server
   * @private
   */
  async _syncNow() {
    if (!this.syncNowButton) return;
    
    // Disable button during sync
    this.syncNowButton.disabled = true;
    this.syncNowButton.innerHTML = '<i class="fas fa-sync fa-spin"></i> Syncing...';
    
    try {
      const result = await OfflineManager.syncNow();
      
      // Update UI
      this._updatePendingChangesCount();
      
      // Show success message
      toastService.success(`Sync completed: ${result.synced} changes synced`);
      
      // Refresh filter list in filter manager
      if (this.filterManager) {
        await this.filterManager._loadSavedFilters();
      }
      
      return result;
    } catch (error) {
      toastService.error(`Sync failed: ${error.message}`);
      console.error('Sync error:', error);
      return { synced: 0, error: error.message };
    } finally {
      // Re-enable button
      this.syncNowButton.disabled = false;
      this.syncNowButton.innerHTML = '<i class="fas fa-sync"></i> Sync Now';
    }
  }
  
  /**
   * Clear all offline data
   * @private
   */
  async _clearOfflineData() {
    // Create and show a confirmation dialog
    const confirmDialog = document.createElement('div');
    confirmDialog.className = 'confirm-dialog';
    confirmDialog.innerHTML = `
      <div class="confirm-dialog-backdrop"></div>
      <div class="confirm-dialog-container">
        <div class="confirm-dialog-header">
          <h4>Confirm Clear Offline Data</h4>
        </div>
        <div class="confirm-dialog-body">
          <p>Are you sure you want to clear all offline data? This will delete all pending changes and cached filters.</p>
          <p class="text-danger">This action cannot be undone.</p>
        </div>
        <div class="confirm-dialog-footer">
          <button class="btn-default" id="cancelClearBtn">Cancel</button>
          <button class="btn-danger" id="confirmClearBtn">Clear Data</button>
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
    
    // Apply dark mode styles if needed
    if (this.options.darkMode) {
      const container = confirmDialog.querySelector('.confirm-dialog-container');
      if (container) {
        container.style.backgroundColor = 'var(--bg-color, #212529)';
        container.style.color = 'var(--text-color, #f8f9fa)';
        container.style.borderColor = 'var(--border-color, #495057)';
      }
    }
    
    document.head.appendChild(dialogStyle);
    document.body.appendChild(confirmDialog);
    
    // Add event listeners
    const cancelBtn = document.getElementById('cancelClearBtn');
    const confirmBtn = document.getElementById('confirmClearBtn');
    
    return new Promise((resolve) => {
      cancelBtn.addEventListener('click', () => {
        document.body.removeChild(confirmDialog);
        resolve(false);
      });
      
      confirmBtn.addEventListener('click', async () => {
        // Remove dialog
        document.body.removeChild(confirmDialog);
        
        try {
          await OfflineManager.clearOfflineData();
          
          // Update UI
          this._updatePendingChangesCount();
          
          // Show success message
          toastService.success('Offline data cleared successfully');
          
          // Refresh filter list in filter manager
          if (this.filterManager) {
            await this.filterManager._loadSavedFilters();
          }
          
          resolve(true);
        } catch (error) {
          toastService.error(`Error clearing offline data: ${error.message}`);
          console.error('Error clearing offline data:', error);
          resolve(false);
        }
      });
    });
  }
  
  /**
   * Save a filter with offline support
   * @param {Object} filter - Filter to save
   * @returns {Promise<Object>} The saved filter
   * @private
   */
  async _saveFilter(filter) {
    try {
      // Validate filter first
      const validation = this.validator.validateFilter(filter);
      if (!validation.valid) {
        toastService.error(`Validation failed: ${validation.errors[0]}`);
        throw new Error(`Validation failed: ${validation.errors[0]}`);
      }
      
      // Check if online
      if (OfflineManager.getNetworkStatus()) {
        try {
          // Try to save online
          const isEdit = filter.id && !filter.id.toString().startsWith('temp_');
          const url = isEdit ? 
            `${this.options.filterListEndpoint}/${filter.id}` : 
            this.options.filterListEndpoint;
          
          const response = await fetch(url, {
            method: isEdit ? 'PUT' : 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(filter)
          });
          
          if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
          }
          
          const savedFilter = await response.json();
          
          // Cache filter for offline use
          await OfflineManager.saveFilterOffline(savedFilter);
          
          toastService.success(`Filter ${isEdit ? 'updated' : 'created'} successfully`);
          return savedFilter;
        } catch (error) {
          console.warn('Error saving filter online, falling back to offline:', error);
          // Fall back to offline save if online save fails
          toastService.warning(`Could not save to server - saving offline`);
          return this._saveFilterOffline(filter);
        }
      } else {
        // Save offline
        toastService.info(`Saving filter offline - will sync when online`);
        return this._saveFilterOffline(filter);
      }
    } catch (error) {
      console.error('Error saving filter:', error);
      toastService.error(`Error saving filter: ${error.message}`);
      throw error;
    }
  }
  
  /**
   * Save a filter offline
   * @param {Object} filter - Filter to save
   * @returns {Promise<Object>} The saved filter
   * @private
   */
  async _saveFilterOffline(filter) {
    if (filter.id && !filter.id.toString().startsWith('temp_')) {
      // This is an update to an existing filter
      const updatedFilter = await OfflineManager.updateFilterOffline(filter.id, filter);
      this._updatePendingChangesCount();
      return updatedFilter;
    } else {
      // This is a new filter
      const newFilter = await OfflineManager.createFilterOffline(filter);
      this._updatePendingChangesCount();
      return newFilter;
    }
  }
  
  /**
   * Test a filter with offline support
   * @param {Object} filter - Filter to test
   * @returns {Promise<Object>} Test results
   * @private
   */
  async _testFilter(filter) {
    try {
      // Validate filter first
      const validation = this.validator.validateFilter(filter);
      if (!validation.valid) {
        toastService.error(`Validation failed: ${validation.errors[0]}`);
        throw new Error(`Validation failed: ${validation.errors[0]}`);
      }
      
      // Check if online
      if (OfflineManager.getNetworkStatus()) {
        try {
          // Try to test online
          const response = await fetch(this.options.testFilterEndpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(filter)
          });
          
          if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
          }
          
          return await response.json();
        } catch (error) {
          console.warn('Error testing filter online, using simulation:', error);
          // Return simulated results if online test fails
          toastService.warning('Could not connect to server - using simulated results');
          return this._createSimulatedTestResults(filter);
        }
      } else {
        // Return simulated test results when offline
        toastService.info('Offline mode - using simulated results');
        return this._createSimulatedTestResults(filter);
      }
    } catch (error) {
      console.error('Error testing filter:', error);
      toastService.error(`Error testing filter: ${error.message}`);
      throw error;
    }
  }
  
  /**
   * Create simulated test results for a filter
   * @param {Object} filter - Filter to test
   * @returns {Object} Simulated test results
   * @private
   */
  _createSimulatedTestResults(filter) {
    // Generate some realistic-looking test results based on the filter
    // The goal is to have something useful to show when offline
    
    // Calculate a match rate based on filter complexity
    let complexityScore = 0;
    
    if (filter.definition && filter.definition.conditions) {
      // More conditions = lower match rate
      const conditions = filter.definition.conditions.conditions || [];
      complexityScore = conditions.length * 0.1;
    }
    
    const matchRate = Math.max(5, Math.min(80, 50 - (complexityScore * 10)));
    const received = Math.floor(Math.random() * 500) + 100; // 100-600 messages
    const matched = Math.floor(received * (matchRate / 100));
    
    // Generate example matches
    const examples = [];
    if (filter.definition && filter.definition.entityType) {
      // Generate a matching example
      examples.push({
        entity_type: filter.definition.entityType,
        entity_id: `example-${Math.floor(Math.random() * 1000)}`,
        timestamp: new Date().toISOString(),
        matched: true
      });
      
      // Generate a non-matching example
      examples.push({
        entity_type: filter.definition.entityType,
        entity_id: `example-${Math.floor(Math.random() * 1000)}`,
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        matched: false
      });
    }
    
    return {
      success: true,
      offline: true,
      totalMessages: received,
      matchedMessages: matched,
      matchRate: matchRate,
      avgProcessingTime: (Math.random() * 1.5).toFixed(2),
      examples: examples,
      note: 'These are simulated results because you are offline or unable to reach the server'
    };
  }
  
  /**
   * Load a filter into the builder
   * @param {Object} filter - Filter to load
   * @returns {Promise<boolean>} Success status
   * @private
   */
  async _loadFilter(filter) {
    if (!this.filterBuilder) {
      toastService.error('Filter builder not initialized');
      return false;
    }
    
    try {
      // Load filter into builder
      await this.filterBuilder.loadFilter(filter);
      toastService.success(`Loaded filter: ${filter.name}`);
      return true;
    } catch (error) {
      console.error('Error loading filter:', error);
      toastService.error(`Error loading filter: ${error.message}`);
      return false;
    }
  }
  
  /**
   * Delete a filter with offline support
   * @param {string} filterId - ID of filter to delete
   * @returns {Promise<boolean>} Success status
   * @private
   */
  async _deleteFilter(filterId) {
    try {
      // Check if online
      if (OfflineManager.getNetworkStatus()) {
        try {
          // Try to delete online
          const response = await fetch(`${this.options.filterListEndpoint}/${filterId}`, {
            method: 'DELETE'
          });
          
          if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
          }
          
          toastService.success('Filter deleted successfully');
          return true;
        } catch (error) {
          console.warn('Error deleting filter online, queueing for offline deletion:', error);
          // Queue for deletion when back online
          await OfflineManager.deleteFilterOffline(filterId);
          this._updatePendingChangesCount();
          toastService.warning('Could not connect to server - filter will be deleted when online');
          return true;
        }
      } else {
        // Queue deletion for when we're back online
        await OfflineManager.deleteFilterOffline(filterId);
        this._updatePendingChangesCount();
        toastService.info('Filter marked for deletion - will be removed when online');
        return true;
      }
    } catch (error) {
      console.error('Error deleting filter:', error);
      toastService.error(`Error deleting filter: ${error.message}`);
      return false;
    }
  }
  
  /**
   * Duplicate a filter
   * @param {Object} filter - Filter to duplicate
   * @returns {Object} The duplicated filter (not yet saved)
   * @private
   */
  _duplicateFilter(filter) {
    if (!this.filterBuilder) {
      toastService.error('Filter builder not initialized');
      return null;
    }
    
    try {
      // Create a copy of the filter with a new name
      const duplicatedFilter = {
        ...filter,
        id: null, // Clear ID to create new
        name: `${filter.name} (Copy)`,
        createdAt: null,
        updatedAt: null
      };
      
      // Load the duplicated filter into the builder
      this.filterBuilder.loadFilter(duplicatedFilter);
      toastService.success(`Duplicated filter: ${filter.name}`);
      
      return duplicatedFilter;
    } catch (error) {
      console.error('Error duplicating filter:', error);
      toastService.error(`Error duplicating filter: ${error.message}`);
      return null;
    }
  }
}

// Create an instance for use in the current example
const offlineFilterUI = new OfflineFilterUI({
  builderContainerId: 'filter-builder-container',
  managerContainerId: 'filter-manager-container',
  // Use demo endpoint paths
  filterListEndpoint: '/api/websocket/filters',
  filterStatsEndpoint: '/api/websocket/filter-stats',
  testFilterEndpoint: '/api/websocket/test-filter',
  fieldDefinitionsEndpoint: '/api/websocket/fields',
  entityTypesEndpoint: '/api/websocket/entity-types',
  showOfflineIndicator: true,
  autoSync: true
});

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  // Check if containers exist
  const builderContainer = document.getElementById('filter-builder-container');
  const managerContainer = document.getElementById('filter-manager-container');
  
  if (!builderContainer || !managerContainer) {
    console.error('Filter containers not found. Make sure the container elements exist in the DOM.');
    
    // Create containers if they don't exist
    if (!builderContainer) {
      const newBuilderContainer = document.createElement('div');
      newBuilderContainer.id = 'filter-builder-container';
      newBuilderContainer.style.cssText = `
        padding: 16px;
        height: 600px;
      `;
      document.body.appendChild(newBuilderContainer);
    }
    
    if (!managerContainer) {
      const newManagerContainer = document.createElement('div');
      newManagerContainer.id = 'filter-manager-container';
      newManagerContainer.style.cssText = `
        padding: 16px;
        height: 600px;
        display: none;
      `;
      document.body.appendChild(newManagerContainer);
    }
    
    // Add tab controls if both containers are new
    if (!builderContainer && !managerContainer) {
      const tabsContainer = document.createElement('div');
      tabsContainer.className = 'tabs-container';
      tabsContainer.style.cssText = `
        display: flex;
        gap: 8px;
        padding: 16px;
        border-bottom: 1px solid #dee2e6;
      `;
      
      const builderTab = document.createElement('button');
      builderTab.className = 'tab active';
      builderTab.dataset.tab = 'builder';
      builderTab.style.cssText = `
        padding: 8px 16px;
        background-color: #0d6efd;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
      `;
      builderTab.textContent = 'Filter Builder';
      
      const managerTab = document.createElement('button');
      managerTab.className = 'tab';
      managerTab.dataset.tab = 'manager';
      managerTab.style.cssText = `
        padding: 8px 16px;
        background-color: #f8f9fa;
        color: #333;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
      `;
      managerTab.textContent = 'Filter Manager';
      
      tabsContainer.appendChild(builderTab);
      tabsContainer.appendChild(managerTab);
      
      document.body.prepend(tabsContainer);
      
      // Add tab switching functionality
      builderTab.addEventListener('click', () => {
        builderTab.classList.add('active');
        builderTab.style.backgroundColor = '#0d6efd';
        builderTab.style.color = 'white';
        managerTab.classList.remove('active');
        managerTab.style.backgroundColor = '#f8f9fa';
        managerTab.style.color = '#333';
        
        document.getElementById('filter-builder-container').style.display = 'block';
        document.getElementById('filter-manager-container').style.display = 'none';
      });
      
      managerTab.addEventListener('click', () => {
        managerTab.classList.add('active');
        managerTab.style.backgroundColor = '#0d6efd';
        managerTab.style.color = 'white';
        builderTab.classList.remove('active');
        builderTab.style.backgroundColor = '#f8f9fa';
        builderTab.style.color = '#333';
        
        document.getElementById('filter-builder-container').style.display = 'none';
        document.getElementById('filter-manager-container').style.display = 'block';
      });
    }
  }
  
  // Initialize the offline filter UI
  offlineFilterUI.initialize()
    .then(success => {
      if (success) {
        console.log('Offline filter UI initialized successfully');
      } else {
        console.error('Failed to initialize offline filter UI');
      }
    })
    .catch(error => {
      console.error('Error initializing offline filter UI:', error);
    });
});

export default offlineFilterUI;