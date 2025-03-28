/**
 * MagnetoCursor - WebSocket Filter UI Offline Integration
 * 
 * This example demonstrates how to integrate offline functionality with the
 * WebSocket Filter UI components to enable creating, editing, and managing filters
 * while offline with background synchronization when reconnecting.
 */

import { FilterBuilder } from '../filter-builder.js';
import { FilterManager } from '../filter-manager.js';
import OfflineManager from '../../offline/index.js';

// Available fields for filters (normally would come from an API)
const availableFields = [
  { id: 'entity_type', label: 'Entity Type', type: 'string' },
  { id: 'entity_id', label: 'Entity ID', type: 'string' },
  { id: 'action', label: 'Action', type: 'string' },
  { id: 'timestamp', label: 'Timestamp', type: 'date' },
  { id: 'user_id', label: 'User ID', type: 'string' },
  { id: 'campaign_id', label: 'Campaign ID', type: 'string' },
  { id: 'platform', label: 'Platform', type: 'string' },
  { id: 'status', label: 'Status', type: 'string' },
  { id: 'budget', label: 'Budget', type: 'number' },
  { id: 'impressions', label: 'Impressions', type: 'number' },
  { id: 'clicks', label: 'Clicks', type: 'number' },
  { id: 'conversions', label: 'Conversions', type: 'number' },
  { id: 'tags', label: 'Tags', type: 'array' },
  { id: 'is_active', label: 'Is Active', type: 'boolean' }
];

// Entity types for filtering
const entityTypes = [
  { id: 'campaign', label: 'Campaign' },
  { id: 'ad_set', label: 'Ad Set' },
  { id: 'ad', label: 'Ad' },
  { id: 'user', label: 'User' },
  { id: 'notification', label: 'Notification' }
];

// Filter categories
const filterCategories = ['General', 'Campaigns', 'Notifications', 'Alerts', 'Custom'];

// DOM Elements
let filterBuilder;
let filterManager;
let offlineStatusElement;
let pendingChangesElement;
let syncNowButton;
let clearOfflineDataButton;

/**
 * Initialize the offline-enabled WebSocket Filter UI
 */
async function initializeOfflineFilterUI() {
  try {
    // Initialize the OfflineManager
    await OfflineManager.initialize({
      registerServiceWorker: true,
      syncEnabled: true,
      syncInterval: 60000, // 1 minute
      syncOnReconnect: true,
      offlineIndicator: true
    });
    
    // Create UI elements
    createUIElements();
    
    // Initialize the FilterBuilder with offline support
    initializeFilterBuilder();
    
    // Initialize the FilterManager with offline support
    initializeFilterManager();
    
    // Set up event listeners
    setupEventListeners();
    
    // Set up conflict resolution
    setupConflictResolution();
    
    // Update UI with initial state
    updateOfflineUIStatus();
    
    console.log('Offline-enabled WebSocket Filter UI initialized successfully');
  } catch (error) {
    console.error('Error initializing offline filter UI:', error);
  }
}

/**
 * Create UI elements for offline status
 */
function createUIElements() {
  // Create offline status bar
  const statusBar = document.createElement('div');
  statusBar.className = 'offline-status-bar';
  statusBar.style.cssText = `
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    font-size: 14px;
  `;
  
  // Status indicator
  const statusContainer = document.createElement('div');
  statusContainer.className = 'status-container';
  statusContainer.style.display = 'flex';
  statusContainer.style.alignItems = 'center';
  statusContainer.style.gap = '8px';
  
  offlineStatusElement = document.createElement('span');
  offlineStatusElement.className = 'offline-status';
  offlineStatusElement.style.display = 'flex';
  offlineStatusElement.style.alignItems = 'center';
  offlineStatusElement.style.gap = '6px';
  
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
  
  offlineStatusElement.appendChild(statusDot);
  offlineStatusElement.appendChild(statusText);
  
  pendingChangesElement = document.createElement('span');
  pendingChangesElement.className = 'pending-changes';
  pendingChangesElement.style.marginLeft = '16px';
  pendingChangesElement.style.padding = '2px 8px';
  pendingChangesElement.style.backgroundColor = '#0d6efd';
  pendingChangesElement.style.color = 'white';
  pendingChangesElement.style.borderRadius = '12px';
  pendingChangesElement.style.fontSize = '12px';
  pendingChangesElement.style.display = 'none'; // Hide initially
  pendingChangesElement.textContent = '0 pending changes';
  
  statusContainer.appendChild(offlineStatusElement);
  statusContainer.appendChild(pendingChangesElement);
  
  // Actions
  const actionsContainer = document.createElement('div');
  actionsContainer.className = 'actions-container';
  actionsContainer.style.display = 'flex';
  actionsContainer.style.gap = '8px';
  
  syncNowButton = document.createElement('button');
  syncNowButton.className = 'sync-now-button';
  syncNowButton.style.cssText = `
    padding: 4px 12px;
    background-color: #0d6efd;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
  `;
  syncNowButton.innerHTML = '<i class="fas fa-sync"></i> Sync Now';
  syncNowButton.disabled = true; // Disable initially
  
  clearOfflineDataButton = document.createElement('button');
  clearOfflineDataButton.className = 'clear-offline-button';
  clearOfflineDataButton.style.cssText = `
    padding: 4px 12px;
    background-color: #dc3545;
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
  
  actionsContainer.appendChild(syncNowButton);
  actionsContainer.appendChild(clearOfflineDataButton);
  
  statusBar.appendChild(statusContainer);
  statusBar.appendChild(actionsContainer);
  
  // Add to document
  document.body.insertBefore(statusBar, document.body.firstChild);
  
  // Create tabs for builder and manager
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
  
  document.body.insertBefore(tabsContainer, document.body.children[1]);
  
  // Create containers for builder and manager
  const builderContainer = document.createElement('div');
  builderContainer.id = 'filter-builder-container';
  builderContainer.className = 'tab-content active';
  builderContainer.dataset.tab = 'builder';
  builderContainer.style.cssText = `
    padding: 16px;
    height: 600px;
  `;
  
  const managerContainer = document.createElement('div');
  managerContainer.id = 'filter-manager-container';
  managerContainer.className = 'tab-content';
  managerContainer.dataset.tab = 'manager';
  managerContainer.style.cssText = `
    padding: 16px;
    height: 600px;
    display: none;
  `;
  
  document.body.appendChild(builderContainer);
  document.body.appendChild(managerContainer);
  
  // Add tab switching functionality
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Remove active class from all tabs
      tabs.forEach(t => {
        t.classList.remove('active');
        t.style.backgroundColor = '#f8f9fa';
        t.style.color = '#333';
      });
      
      // Add active class to clicked tab
      tab.classList.add('active');
      tab.style.backgroundColor = '#0d6efd';
      tab.style.color = 'white';
      
      // Hide all tab content
      document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
        content.classList.remove('active');
      });
      
      // Show corresponding tab content
      const tabName = tab.dataset.tab;
      const tabContent = document.querySelector(`.tab-content[data-tab="${tabName}"]`);
      tabContent.style.display = 'block';
      tabContent.classList.add('active');
    });
  });
}

/**
 * Initialize the FilterBuilder with offline support
 */
function initializeFilterBuilder() {
  const builderContainer = document.getElementById('filter-builder-container');
  
  // Create offline-aware save function
  const saveFilter = async (filter) => {
    try {
      // Check if online
      if (OfflineManager.getNetworkStatus()) {
        // Try to save online
        try {
          const response = await fetch('/api/websocket/filters', {
            method: filter.id ? 'PUT' : 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(filter)
          });
          
          if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
          }
          
          const savedFilter = await response.json();
          console.log('Filter saved online:', savedFilter);
          
          // Cache filter for offline use
          await OfflineManager.saveFilterOffline(savedFilter);
          
          return savedFilter;
        } catch (error) {
          console.error('Error saving filter online, falling back to offline:', error);
          // Fall back to offline save if online save fails
          return saveOffline(filter);
        }
      } else {
        // Save offline
        return saveOffline(filter);
      }
    } catch (error) {
      console.error('Error saving filter:', error);
      throw error;
    }
  };
  
  // Function to save filter offline
  const saveOffline = async (filter) => {
    if (filter.id && filter.id.toString().startsWith('temp_')) {
      // This is a new filter created offline, just queue it
      const savedFilter = await OfflineManager.createFilterOffline(filter);
      console.log('New filter queued for sync:', savedFilter);
      updatePendingChangesCount();
      return savedFilter;
    } else if (filter.id) {
      // This is an update to an existing filter
      await OfflineManager.updateFilterOffline(filter.id, filter);
      console.log('Filter update queued for sync:', filter);
      updatePendingChangesCount();
      return filter;
    } else {
      // Brand new filter
      const newFilter = await OfflineManager.createFilterOffline(filter);
      console.log('New filter created offline:', newFilter);
      updatePendingChangesCount();
      return newFilter;
    }
  };
  
  // Create offline-aware test function
  const testFilter = async (filter) => {
    try {
      // Check if online
      if (OfflineManager.getNetworkStatus()) {
        // Try to test online
        try {
          const response = await fetch('/api/websocket/test-filter', {
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
          console.error('Error testing filter online:', error);
          // Return mock results if online test fails
          return createMockTestResults(filter);
        }
      } else {
        // Return mock test results when offline
        return createMockTestResults(filter);
      }
    } catch (error) {
      console.error('Error testing filter:', error);
      throw error;
    }
  };
  
  // Function to create mock test results
  const createMockTestResults = (filter) => {
    return {
      success: true,
      offline: true,
      totalMessages: 100,
      matchedMessages: 25,
      matchRate: 25,
      avgProcessingTime: 0.5,
      examples: [
        { entity_type: 'campaign', matched: true },
        { entity_type: 'notification', matched: false }
      ],
      note: 'These are simulated results because you are offline'
    };
  };
  
  // Initialize the FilterBuilder
  filterBuilder = new FilterBuilder(builderContainer, {
    availableFields,
    filterableEntityTypes: entityTypes,
    onChange: (filter) => {
      console.log('Filter changed:', filter);
    },
    onSave: saveFilter,
    onTest: testFilter
  });
  
  // Add offline indicator to the filter builder
  addOfflineIndicatorToBuilder();
}

/**
 * Add offline indicator to the filter builder
 */
function addOfflineIndicatorToBuilder() {
  const builderContainer = document.getElementById('filter-builder-container');
  const filterToolbar = builderContainer.querySelector('.filter-toolbar');
  
  if (filterToolbar) {
    const offlineIndicator = document.createElement('div');
    offlineIndicator.className = 'filter-offline-indicator';
    offlineIndicator.style.cssText = `
      margin-left: auto;
      padding: 0.25rem 0.5rem;
      font-size: 0.75rem;
      color: white;
      background-color: #dc3545;
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
 * Initialize the FilterManager with offline support
 */
function initializeFilterManager() {
  const managerContainer = document.getElementById('filter-manager-container');
  
  // Offline-aware function to load filter
  const loadFilter = async (filter) => {
    console.log('Loading filter:', filter);
    
    // Switch to builder tab
    document.querySelector('.tab[data-tab="builder"]').click();
    
    // Load filter into builder
    if (filterBuilder) {
      filterBuilder.loadFilter(filter);
    }
    
    return true;
  };
  
  // Offline-aware function to delete filter
  const deleteFilter = async (filterId) => {
    try {
      // Check if online
      if (OfflineManager.getNetworkStatus()) {
        // Try to delete online
        try {
          const response = await fetch(`/api/websocket/filters/${filterId}`, {
            method: 'DELETE'
          });
          
          if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
          }
          
          console.log('Filter deleted online:', filterId);
          return true;
        } catch (error) {
          console.error('Error deleting filter online, queueing for offline deletion:', error);
          // Queue for deletion when back online
          await OfflineManager.deleteFilterOffline(filterId);
          updatePendingChangesCount();
          return true;
        }
      } else {
        // Queue deletion for when we're back online
        await OfflineManager.deleteFilterOffline(filterId);
        console.log('Filter deletion queued for sync:', filterId);
        updatePendingChangesCount();
        return true;
      }
    } catch (error) {
      console.error('Error deleting filter:', error);
      return false;
    }
  };
  
  // Offline-aware function to duplicate filter
  const duplicateFilter = (filter) => {
    // Create a copy of the filter with a new name
    const duplicatedFilter = {
      ...filter,
      id: null, // Clear ID to create new
      name: `${filter.name} (Copy)`,
      createdAt: null,
      updatedAt: null
    };
    
    // Switch to builder tab
    document.querySelector('.tab[data-tab="builder"]').click();
    
    // Load the duplicated filter into the builder
    if (filterBuilder) {
      filterBuilder.loadFilter(duplicatedFilter);
    }
    
    return duplicatedFilter;
  };
  
  // Mock fetchFilters function that works offline
  const fetchFilters = async () => {
    // Check if online
    if (OfflineManager.getNetworkStatus()) {
      try {
        // Try to fetch from server
        const response = await fetch('/api/websocket/filters');
        
        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Cache filters for offline use
        if (data && data.filters) {
          for (const filter of data.filters) {
            await OfflineManager.saveFilterOffline(filter);
          }
        }
        
        return data;
      } catch (error) {
        console.error('Error fetching filters online, falling back to offline cache:', error);
        // Fall back to offline
        return fetchOfflineFilters();
      }
    } else {
      // Fetch from offline cache
      return fetchOfflineFilters();
    }
  };
  
  // Function to fetch filters from offline cache
  const fetchOfflineFilters = async () => {
    const filters = await OfflineManager.getAllOfflineFilters();
    return { filters };
  };
  
  // Override fetch API for the demo
  const originalFetch = window.fetch;
  window.fetch = async (url, options) => {
    if (url.includes('/api/websocket/filters')) {
      if (!options || options.method === 'GET' || !options.method) {
        const data = await fetchFilters();
        return {
          ok: true,
          json: async () => data
        };
      }
    } else if (url.includes('/api/websocket/filter-stats')) {
      // Return mock stats
      return {
        ok: true,
        json: async () => ({
          stats: {
            // Mock statistics for demo purposes
          }
        })
      };
    }
    
    // For all other requests, use original fetch
    return originalFetch(url, options);
  };
  
  // Initialize FilterManager
  filterManager = new FilterManager(managerContainer, {
    filterListUrl: '/api/websocket/filters',
    filterStatsUrl: '/api/websocket/filter-stats',
    categories: filterCategories,
    onLoadFilter: loadFilter,
    onDeleteFilter: deleteFilter,
    onDuplicateFilter: duplicateFilter
  });
}

/**
 * Set up event listeners for offline functionality
 */
function setupEventListeners() {
  // Listen for online/offline events
  OfflineManager.addConnectionListener((status) => {
    console.log('Connection status changed:', status);
    updateOfflineUIStatus();
  });
  
  // Sync now button
  syncNowButton.addEventListener('click', async () => {
    // Disable button during sync
    syncNowButton.disabled = true;
    syncNowButton.innerHTML = '<i class="fas fa-sync fa-spin"></i> Syncing...';
    
    try {
      const result = await OfflineManager.syncNow();
      console.log('Sync result:', result);
      
      // Update UI
      updatePendingChangesCount();
      
      // Show success message
      const successMessage = document.createElement('div');
      successMessage.className = 'sync-success-message';
      successMessage.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 10px 20px;
        background-color: #198754;
        color: white;
        border-radius: 4px;
        font-size: 14px;
        z-index: 9999;
      `;
      successMessage.textContent = `Sync completed: ${result.synced} changes synced`;
      document.body.appendChild(successMessage);
      
      // Remove message after 3 seconds
      setTimeout(() => {
        successMessage.remove();
      }, 3000);
    } catch (error) {
      console.error('Sync error:', error);
      
      // Show error message
      const errorMessage = document.createElement('div');
      errorMessage.className = 'sync-error-message';
      errorMessage.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 10px 20px;
        background-color: #dc3545;
        color: white;
        border-radius: 4px;
        font-size: 14px;
        z-index: 9999;
      `;
      errorMessage.textContent = `Sync failed: ${error.message}`;
      document.body.appendChild(errorMessage);
      
      // Remove message after 3 seconds
      setTimeout(() => {
        errorMessage.remove();
      }, 3000);
    } finally {
      // Re-enable button
      syncNowButton.disabled = false;
      syncNowButton.innerHTML = '<i class="fas fa-sync"></i> Sync Now';
    }
  });
  
  // Clear offline data button
  clearOfflineDataButton.addEventListener('click', async () => {
    // Confirm with user
    const confirmed = confirm('Are you sure you want to clear all offline data? This will delete all pending changes and cached filters.');
    
    if (confirmed) {
      try {
        await OfflineManager.clearOfflineData();
        console.log('Offline data cleared');
        
        // Update UI
        updatePendingChangesCount();
        
        // Show success message
        const successMessage = document.createElement('div');
        successMessage.className = 'clear-success-message';
        successMessage.style.cssText = `
          position: fixed;
          top: 20px;
          right: 20px;
          padding: 10px 20px;
          background-color: #198754;
          color: white;
          border-radius: 4px;
          font-size: 14px;
          z-index: 9999;
        `;
        successMessage.textContent = 'Offline data cleared successfully';
        document.body.appendChild(successMessage);
        
        // Remove message after 3 seconds
        setTimeout(() => {
          successMessage.remove();
        }, 3000);
      } catch (error) {
        console.error('Error clearing offline data:', error);
        
        // Show error message
        const errorMessage = document.createElement('div');
        errorMessage.className = 'clear-error-message';
        errorMessage.style.cssText = `
          position: fixed;
          top: 20px;
          right: 20px;
          padding: 10px 20px;
          background-color: #dc3545;
          color: white;
          border-radius: 4px;
          font-size: 14px;
          z-index: 9999;
        `;
        errorMessage.textContent = `Error clearing offline data: ${error.message}`;
        document.body.appendChild(errorMessage);
        
        // Remove message after 3 seconds
        setTimeout(() => {
          errorMessage.remove();
        }, 3000);
      }
    }
  });
}

/**
 * Set up conflict resolution
 */
function setupConflictResolution() {
  OfflineManager.setConflictHandler(async (localChange, serverData) => {
    // Show conflict resolution dialog
    return new Promise((resolve) => {
      // Create dialog
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
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        width: 500px;
        max-width: 90%;
      `;
      
      // Dialog header
      const header = document.createElement('h3');
      header.style.cssText = `
        margin-top: 0;
        margin-bottom: 15px;
        font-size: 18px;
        border-bottom: 1px solid #dee2e6;
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
      useLocalButton.textContent = 'Use My Changes';
      useLocalButton.style.cssText = `
        padding: 8px 16px;
        background-color: #0d6efd;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
      `;
      
      const useServerButton = document.createElement('button');
      useServerButton.textContent = 'Use Server Changes';
      useServerButton.style.cssText = `
        padding: 8px 16px;
        background-color: #6c757d;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
      `;
      
      const mergeButton = document.createElement('button');
      mergeButton.textContent = 'Merge Changes';
      mergeButton.style.cssText = `
        padding: 8px 16px;
        background-color: #198754;
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
        border: 1px solid #dee2e6;
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
      `;
      localContent.textContent = JSON.stringify(localChange.data, null, 2);
      
      localContainer.appendChild(localTitle);
      localContainer.appendChild(localContent);
      
      // Server changes
      const serverContainer = document.createElement('div');
      serverContainer.style.cssText = `
        flex: 1;
        border: 1px solid #dee2e6;
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
      `;
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
 */
function updateOfflineUIStatus() {
  const isOnline = OfflineManager.getNetworkStatus();
  const statusDot = offlineStatusElement.querySelector('.status-dot');
  const statusText = offlineStatusElement.querySelector('span:last-child');
  
  if (isOnline) {
    statusDot.style.backgroundColor = '#198754'; // Green
    statusText.textContent = 'Online';
    
    // Show sync button if there are pending changes
    const pendingCount = OfflineManager.getPendingChangesCount();
    syncNowButton.disabled = pendingCount === 0;
    
    // Hide offline indicators in UI
    document.querySelectorAll('.filter-offline-indicator').forEach(indicator => {
      indicator.style.display = 'none';
    });
  } else {
    statusDot.style.backgroundColor = '#dc3545'; // Red
    statusText.textContent = 'Offline';
    
    // Disable sync button when offline
    syncNowButton.disabled = true;
    
    // Show offline indicators in UI
    document.querySelectorAll('.filter-offline-indicator').forEach(indicator => {
      indicator.style.display = 'block';
    });
  }
  
  // Update pending changes count
  updatePendingChangesCount();
}

/**
 * Update pending changes count in UI
 */
function updatePendingChangesCount() {
  const pendingCount = OfflineManager.getPendingChangesCount();
  
  if (pendingCount > 0) {
    pendingChangesElement.textContent = `${pendingCount} pending ${pendingCount === 1 ? 'change' : 'changes'}`;
    pendingChangesElement.style.display = 'inline-block';
    
    // Enable sync button if online
    if (OfflineManager.getNetworkStatus()) {
      syncNowButton.disabled = false;
    }
  } else {
    pendingChangesElement.style.display = 'none';
    syncNowButton.disabled = true;
  }
}

// Export public functions
export {
  initializeOfflineFilterUI,
  updateOfflineUIStatus,
  updatePendingChangesCount
};

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('Initializing offline filter UI...');
  initializeOfflineFilterUI();
});