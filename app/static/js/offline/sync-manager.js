/**
 * MagnetoCursor - Sync Manager
 * 
 * Manages background synchronization of offline changes and resolves conflicts
 * when network connection is restored.
 */

import * as IndexedDB from './indexeddb.js';
import { ConflictResolver } from './conflict-resolver.js';

/**
 * Sync Status enum
 */
export const SyncStatus = {
  IDLE: 'idle',
  SYNCING: 'syncing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CONFLICT: 'conflict'
};

/**
 * Sync Manager
 */
export class SyncManager {
  /**
   * Create a new SyncManager
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = {
      autoSync: true, // Automatically sync when online
      syncInterval: 60000, // Sync interval in milliseconds (1 minute)
      maxRetries: 3, // Maximum number of retry attempts
      priorityEntities: ['campaign', 'filter'], // Entity types to sync first
      conflictResolver: new ConflictResolver(),
      onSyncStart: null, // Callback when sync starts
      onSyncComplete: null, // Callback when sync completes
      onSyncError: null, // Callback when sync fails
      onSyncProgress: null, // Callback for sync progress updates
      onConflict: null, // Callback when a conflict is detected
      ...options
    };
    
    this.status = SyncStatus.IDLE;
    this.pendingChanges = [];
    this.syncInProgress = false;
    this.lastSyncTime = null;
    this.intervalId = null;
    this.conflictResolver = this.options.conflictResolver;
    
    // Bind methods
    this.startAutoSync = this.startAutoSync.bind(this);
    this.stopAutoSync = this.stopAutoSync.bind(this);
    this.syncNow = this.syncNow.bind(this);
    this.handleOnlineStatus = this.handleOnlineStatus.bind(this);
    
    // Initialize
    this._initialize();
  }
  
  /**
   * Initialize the sync manager
   * @private
   */
  _initialize() {
    // Add online/offline event listeners
    window.addEventListener('online', this.handleOnlineStatus);
    window.addEventListener('offline', this.handleOnlineStatus);
    
    // Check if we should start auto sync
    if (this.options.autoSync && navigator.onLine) {
      this.startAutoSync();
    }
    
    // Register with service worker for sync events
    this._registerWithServiceWorker();
  }
  
  /**
   * Register with the service worker for sync events
   * @private
   */
  async _registerWithServiceWorker() {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      try {
        const registration = await navigator.serviceWorker.ready;
        
        // Listen for messages from the service worker
        navigator.serviceWorker.addEventListener('message', (event) => {
          const data = event.data;
          
          if (data.type === 'sync-completed') {
            // Service worker completed a sync
            console.log('Service worker completed sync:', data.results);
            this._handleSyncComplete(data.results);
          } else if (data.type === 'sync-conflict') {
            // Service worker detected a conflict
            console.log('Service worker detected conflict:', data.conflict);
            this._handleConflict(data.conflict);
          }
        });
        
        console.log('Sync Manager registered with Service Worker');
      } catch (error) {
        console.error('Error registering Sync Manager with Service Worker:', error);
      }
    } else {
      console.log('Background Sync not supported. Falling back to manual sync.');
    }
  }
  
  /**
   * Handle online/offline status changes
   * @param {Event} event - Online/offline event
   */
  handleOnlineStatus(event) {
    const isOnline = navigator.onLine;
    console.log(`Network status changed. Online: ${isOnline}`);
    
    if (isOnline) {
      // We're back online, start auto sync
      if (this.options.autoSync) {
        this.startAutoSync();
        
        // Trigger an immediate sync
        this.syncNow();
      }
    } else {
      // We're offline, stop auto sync
      this.stopAutoSync();
    }
    
    // Dispatch custom event
    window.dispatchEvent(new CustomEvent('connectivity-change', { 
      detail: { online: isOnline } 
    }));
  }
  
  /**
   * Start automatic synchronization
   */
  startAutoSync() {
    if (this.intervalId) {
      return;
    }
    
    console.log(`Starting auto sync with interval: ${this.options.syncInterval}ms`);
    
    // Start the sync interval
    this.intervalId = setInterval(() => {
      if (navigator.onLine && !this.syncInProgress) {
        this.syncNow();
      }
    }, this.options.syncInterval);
    
    // Register for background sync if available
    this._registerBackgroundSync();
  }
  
  /**
   * Stop automatic synchronization
   */
  stopAutoSync() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      console.log('Auto sync stopped');
    }
  }
  
  /**
   * Register for background sync
   * @private
   */
  async _registerBackgroundSync() {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      try {
        const registration = await navigator.serviceWorker.ready;
        await registration.sync.register('magnetocursor-sync');
        console.log('Background sync registered');
      } catch (error) {
        console.error('Error registering for background sync:', error);
      }
    }
  }
  
  /**
   * Start a manual synchronization
   * @returns {Promise<Object>} - Sync results
   */
  async syncNow() {
    if (this.syncInProgress) {
      console.log('Sync already in progress');
      return { status: SyncStatus.SYNCING };
    }
    
    if (!navigator.onLine) {
      console.log('Cannot sync: offline');
      return { status: SyncStatus.FAILED, error: 'Offline' };
    }
    
    this.syncInProgress = true;
    this.status = SyncStatus.SYNCING;
    
    // Call the onSyncStart callback if provided
    if (typeof this.options.onSyncStart === 'function') {
      this.options.onSyncStart();
    }
    
    // Dispatch sync start event
    window.dispatchEvent(new CustomEvent('sync-start'));
    
    try {
      // Load all pending changes
      const pendingChanges = await IndexedDB.getPendingChanges();
      this.pendingChanges = pendingChanges;
      
      if (pendingChanges.length === 0) {
        console.log('No pending changes to sync');
        this._completeSyncProcess({
          status: SyncStatus.COMPLETED,
          synced: 0,
          conflicts: 0,
          errors: 0
        });
        return { status: SyncStatus.COMPLETED, changes: 0 };
      }
      
      console.log(`Found ${pendingChanges.length} pending changes to sync`);
      
      // Sort changes by priority and timestamp
      const sortedChanges = this._sortChangesByPriority(pendingChanges);
      
      // Process each change
      const results = {
        synced: 0,
        conflicts: 0,
        errors: 0
      };
      
      let processedCount = 0;
      const totalCount = sortedChanges.length;
      
      for (const change of sortedChanges) {
        try {
          processedCount++;
          
          // Update progress
          this._updateSyncProgress(processedCount, totalCount);
          
          // Process the change
          const changeResult = await this._processChange(change);
          
          if (changeResult.status === 'synced') {
            // Mark the change as synced
            await IndexedDB.markChangeAsSynced(change.id);
            results.synced++;
          } else if (changeResult.status === 'conflict') {
            // Handle conflict
            results.conflicts++;
            
            // Call the onConflict callback if provided
            if (typeof this.options.onConflict === 'function') {
              this.options.onConflict(change, changeResult.serverData);
            }
            
            // Try to resolve the conflict
            const resolution = await this._resolveConflict(change, changeResult.serverData);
            
            if (resolution.resolved) {
              if (resolution.action === 'local') {
                // Use local changes, retry the sync
                const retryResult = await this._processChange(change);
                if (retryResult.status === 'synced') {
                  await IndexedDB.markChangeAsSynced(change.id);
                  results.synced++;
                  results.conflicts--;
                }
              } else if (resolution.action === 'server') {
                // Use server data, mark as synced
                await IndexedDB.markChangeAsSynced(change.id);
                
                // Update local cache with server data
                if (change.entityType && change.entityId) {
                  await IndexedDB.cacheEntityData(change.entityType, changeResult.serverData);
                }
                
                results.synced++;
                results.conflicts--;
              } else if (resolution.action === 'merged') {
                // Use merged data, retry the sync
                change.data = resolution.mergedData;
                const retryResult = await this._processChange(change);
                if (retryResult.status === 'synced') {
                  await IndexedDB.markChangeAsSynced(change.id);
                  results.synced++;
                  results.conflicts--;
                }
              }
            }
          } else {
            // Error
            results.errors++;
            
            // Increment retry count
            change.retryCount = (change.retryCount || 0) + 1;
            await IndexedDB.offlineDataDb.store('pendingChanges').put(change);
            
            // If we've exceeded max retries, mark as failed
            if (change.retryCount >= this.options.maxRetries) {
              change.status = 'failed';
              await IndexedDB.offlineDataDb.store('pendingChanges').put(change);
            }
          }
        } catch (error) {
          console.error(`Error processing change:`, error, change);
          results.errors++;
        }
      }
      
      // Complete the sync process
      results.status = results.errors === 0 ? SyncStatus.COMPLETED : SyncStatus.FAILED;
      this._completeSyncProcess(results);
      
      return results;
    } catch (error) {
      console.error('Sync error:', error);
      this._completeSyncProcess({
        status: SyncStatus.FAILED,
        error: error.message || 'Unknown error'
      });
      
      return { status: SyncStatus.FAILED, error: error.message || 'Unknown error' };
    }
  }
  
  /**
   * Process a single change
   * @param {Object} change - The change to process
   * @returns {Promise<Object>} - Result of the change processing
   * @private
   */
  async _processChange(change) {
    console.log(`Processing change: ${change.operation} ${change.entityType} ${change.entityId}`);
    
    try {
      // Determine the API endpoint based on entity type and operation
      let endpoint, method;
      
      switch (change.entityType) {
        case 'campaign':
          endpoint = `/api/campaigns${change.entityId ? `/${change.entityId}` : ''}`;
          break;
        case 'filter':
          endpoint = `/api/websocket/filters${change.entityId ? `/${change.entityId}` : ''}`;
          break;
        default:
          throw new Error(`Unknown entity type: ${change.entityType}`);
      }
      
      // Determine the HTTP method based on operation
      switch (change.operation) {
        case 'create':
          method = 'POST';
          break;
        case 'update':
          method = 'PUT';
          break;
        case 'delete':
          method = 'DELETE';
          break;
        default:
          throw new Error(`Unknown operation: ${change.operation}`);
      }
      
      // If we're deleting and have an entity ID, append it to the endpoint
      if (change.operation === 'delete' && change.entityId) {
        endpoint = `${endpoint}/${change.entityId}`;
      }
      
      // Add current timestamp to verify data freshness
      if (change.operation !== 'delete') {
        change.data.clientTimestamp = change.timestamp;
      }
      
      // Make the API request
      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'X-Client-Timestamp': change.timestamp
        },
        body: change.operation !== 'delete' ? JSON.stringify(change.data) : undefined
      });
      
      // Check if the request was successful
      if (response.ok) {
        // Parse the response JSON for non-delete operations
        const responseData = change.operation !== 'delete' ? await response.json() : null;
        
        // Return success
        return {
          status: 'synced',
          serverData: responseData
        };
      } else {
        // Check for conflict (412 Precondition Failed)
        if (response.status === 412) {
          // Get the server's current version
          const conflictData = await response.json();
          
          return {
            status: 'conflict',
            serverData: conflictData.currentData
          };
        }
        
        // Other error
        return {
          status: 'error',
          statusCode: response.status,
          statusText: response.statusText
        };
      }
    } catch (error) {
      console.error(`Error processing change:`, error);
      return {
        status: 'error',
        error: error.message || 'Unknown error'
      };
    }
  }
  
  /**
   * Resolve a conflict between local and server data
   * @param {Object} change - The local change
   * @param {Object} serverData - The server data
   * @returns {Promise<Object>} - Resolution result
   * @private
   */
  async _resolveConflict(change, serverData) {
    try {
      // If we have a conflict resolver, use it
      if (this.conflictResolver) {
        return await this.conflictResolver.resolve(change, serverData);
      }
      
      // Default resolution: server wins
      return {
        resolved: true,
        action: 'server'
      };
    } catch (error) {
      console.error('Error resolving conflict:', error);
      return {
        resolved: false,
        error: error.message || 'Unknown error'
      };
    }
  }
  
  /**
   * Sort changes by priority and timestamp
   * @param {Array} changes - Array of changes to sort
   * @returns {Array} - Sorted changes
   * @private
   */
  _sortChangesByPriority(changes) {
    return changes.sort((a, b) => {
      // Sort by priority entity type
      const aTypeIndex = this.options.priorityEntities.indexOf(a.entityType);
      const bTypeIndex = this.options.priorityEntities.indexOf(b.entityType);
      
      if (aTypeIndex !== bTypeIndex) {
        // If one is in priority list and the other isn't, prioritize the one in the list
        if (aTypeIndex === -1) return 1;
        if (bTypeIndex === -1) return -1;
        
        // Sort by priority index
        return aTypeIndex - bTypeIndex;
      }
      
      // Sort by operation (create, update, delete)
      const operationOrder = { create: 0, update: 1, delete: 2 };
      if (operationOrder[a.operation] !== operationOrder[b.operation]) {
        return operationOrder[a.operation] - operationOrder[b.operation];
      }
      
      // If same priority and operation, sort by timestamp (oldest first)
      return a.timestamp - b.timestamp;
    });
  }
  
  /**
   * Update sync progress
   * @param {number} processed - Number of processed changes
   * @param {number} total - Total number of changes
   * @private
   */
  _updateSyncProgress(processed, total) {
    const progress = {
      processed,
      total,
      percentage: Math.round((processed / total) * 100)
    };
    
    // Call the onSyncProgress callback if provided
    if (typeof this.options.onSyncProgress === 'function') {
      this.options.onSyncProgress(progress);
    }
    
    // Dispatch progress event
    window.dispatchEvent(new CustomEvent('sync-progress', { detail: progress }));
  }
  
  /**
   * Complete the sync process
   * @param {Object} results - Sync results
   * @private
   */
  _completeSyncProcess(results) {
    this.syncInProgress = false;
    this.status = results.status;
    this.lastSyncTime = new Date();
    
    // Call the appropriate callback
    if (results.status === SyncStatus.COMPLETED) {
      if (typeof this.options.onSyncComplete === 'function') {
        this.options.onSyncComplete(results);
      }
    } else {
      if (typeof this.options.onSyncError === 'function') {
        this.options.onSyncError(results);
      }
    }
    
    // Dispatch event
    window.dispatchEvent(new CustomEvent('sync-complete', { detail: results }));
    
    // Log sync results
    this._logSyncResults(results);
  }
  
  /**
   * Log sync results to IndexedDB
   * @param {Object} results - Sync results
   * @private
   */
  async _logSyncResults(results) {
    try {
      await IndexedDB.offlineDataDb.open();
      await IndexedDB.offlineDataDb.store('syncLog').add({
        timestamp: Date.now(),
        status: results.status,
        synced: results.synced || 0,
        conflicts: results.conflicts || 0,
        errors: results.errors || 0,
        error: results.error,
        details: results
      });
    } catch (error) {
      console.error('Error logging sync results:', error);
    }
  }
  
  /**
   * Handle sync complete from service worker
   * @param {Object} results - Sync results
   * @private
   */
  _handleSyncComplete(results) {
    this.syncInProgress = false;
    this.status = results.status;
    this.lastSyncTime = new Date();
    
    // Call the appropriate callback
    if (results.status === SyncStatus.COMPLETED) {
      if (typeof this.options.onSyncComplete === 'function') {
        this.options.onSyncComplete(results);
      }
    } else {
      if (typeof this.options.onSyncError === 'function') {
        this.options.onSyncError(results);
      }
    }
    
    // Dispatch event
    window.dispatchEvent(new CustomEvent('sync-complete', { detail: results }));
  }
  
  /**
   * Handle conflict from service worker
   * @param {Object} conflict - Conflict details
   * @private
   */
  _handleConflict(conflict) {
    // Call the onConflict callback if provided
    if (typeof this.options.onConflict === 'function') {
      this.options.onConflict(conflict.change, conflict.serverData);
    }
    
    // Dispatch event
    window.dispatchEvent(new CustomEvent('sync-conflict', { detail: conflict }));
  }
  
  /**
   * Get sync status details
   * @returns {Object} - Sync status details
   */
  getSyncStatus() {
    return {
      status: this.status,
      lastSyncTime: this.lastSyncTime,
      pendingChanges: this.pendingChanges.length,
      autoSyncEnabled: this.options.autoSync && !!this.intervalId
    };
  }
  
  /**
   * Get sync log entries
   * @param {number} limit - Maximum number of entries to retrieve
   * @returns {Promise<Array>} - Array of sync log entries
   */
  async getSyncLog(limit = 10) {
    try {
      await IndexedDB.offlineDataDb.open();
      
      // Get all entries and sort by timestamp descending
      const entries = await IndexedDB.offlineDataDb.store('syncLog').getAll();
      entries.sort((a, b) => b.timestamp - a.timestamp);
      
      // Limit the results
      return entries.slice(0, limit);
    } catch (error) {
      console.error('Error retrieving sync log:', error);
      return [];
    }
  }
  
  /**
   * Get pending changes
   * @returns {Promise<Array>} - Array of pending changes
   */
  async getPendingChanges() {
    try {
      return await IndexedDB.getPendingChanges();
    } catch (error) {
      console.error('Error retrieving pending changes:', error);
      return [];
    }
  }
  
  /**
   * Disable syncing for a specific entity
   * @param {string} entityType - Entity type
   * @param {string|number} entityId - Entity ID
   * @returns {Promise<boolean>} - Success indicator
   */
  async disableSyncForEntity(entityType, entityId) {
    try {
      await IndexedDB.offlineDataDb.open();
      
      // Find pending changes for this entity
      const changes = await IndexedDB.offlineDataDb.store('pendingChanges')
        .getByIndex('entityIdIndex', entityId);
      
      // Mark them as disabled
      for (const change of changes) {
        if (change.entityType === entityType) {
          change.status = 'disabled';
          await IndexedDB.offlineDataDb.store('pendingChanges').put(change);
        }
      }
      
      return true;
    } catch (error) {
      console.error('Error disabling sync for entity:', error);
      return false;
    }
  }
  
  /**
   * Clean up the sync manager
   */
  destroy() {
    // Stop auto sync
    this.stopAutoSync();
    
    // Remove event listeners
    window.removeEventListener('online', this.handleOnlineStatus);
    window.removeEventListener('offline', this.handleOnlineStatus);
    
    console.log('Sync Manager destroyed');
  }
}

/**
 * Get the browser's online status
 * @returns {boolean} - Whether browser is online
 */
export function isOnline() {
  return navigator.onLine;
}

/**
 * Check if service worker and background sync are supported
 * @returns {boolean} - Whether background sync is supported
 */
export function isBackgroundSyncSupported() {
  return 'serviceWorker' in navigator && 'SyncManager' in window;
}

/**
 * Add offline change to be synced later
 * @param {string} entityType - Entity type ('campaign' or 'filter')
 * @param {string} operation - Operation ('create', 'update', or 'delete')
 * @param {Object} data - Entity data
 * @param {string|number} entityId - Entity ID (optional for 'create')
 * @returns {Promise<boolean>} - Success indicator
 */
export async function addOfflineChange(entityType, operation, data, entityId = null) {
  try {
    // Validate parameters
    if (!['campaign', 'filter'].includes(entityType)) {
      throw new Error(`Invalid entity type: ${entityType}`);
    }
    
    if (!['create', 'update', 'delete'].includes(operation)) {
      throw new Error(`Invalid operation: ${operation}`);
    }
    
    if (operation !== 'delete' && !data) {
      throw new Error('Data is required for create and update operations');
    }
    
    if ((operation === 'update' || operation === 'delete') && !entityId) {
      throw new Error('Entity ID is required for update and delete operations');
    }
    
    // Save the change for later syncing
    await IndexedDB.savePendingChange({
      entityType,
      entityId,
      operation,
      data,
      timestamp: Date.now(),
      status: 'pending'
    });
    
    // If this is a create or update, cache the data locally
    if (operation !== 'delete' && data) {
      await IndexedDB.cacheEntityData(entityType, data);
    }
    
    // Try to sync if online
    if (navigator.onLine) {
      // Register for background sync
      if (isBackgroundSyncSupported()) {
        const registration = await navigator.serviceWorker.ready;
        await registration.sync.register('magnetocursor-sync');
      }
    }
    
    return true;
  } catch (error) {
    console.error('Error adding offline change:', error);
    return false;
  }
}

// Create a default instance of the sync manager
const defaultSyncManager = new SyncManager();

// Export the sync manager
export default defaultSyncManager;
