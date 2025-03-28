/**
 * MagnetoCursor - Offline Functionality
 * 
 * Main entry point for offline features including:
 * - Service Worker registration and management
 * - IndexedDB data storage and retrieval
 * - Background synchronization of changes
 * - Conflict resolution
 * - Connectivity monitoring
 */

// Import all components
import * as IndexedDB from './indexeddb.js';
import SyncManager, { addOfflineChange, isOnline, isBackgroundSyncSupported } from './sync-manager.js';
import { ConflictResolver, ResolutionType, createTimestampResolver, createFieldPriorityResolver, deepMerge } from './conflict-resolver.js';

// Connectivity state
let isInitialized = false;
let networkStatus = navigator.onLine;
const connectionListeners = [];

/**
 * Initialize offline functionality
 * @param {Object} options - Configuration options
 * @returns {Promise<boolean>} - Success indicator
 */
export async function initialize(options = {}) {
  if (isInitialized) {
    console.log('Offline functionality already initialized');
    return true;
  }
  
  try {
    // Default options
    const defaultOptions = {
      registerServiceWorker: true,
      serviceWorkerPath: '/static/js/offline/service-worker.js',
      syncEnabled: true,
      syncInterval: 60000, // 1 minute
      syncOnReconnect: true,
      cacheApiResponses: true,
      persistFilterPreferences: true,
      offlineIndicator: true,
      offlineIndicatorSelector: '#offline-indicator',
      debug: false
    };
    
    // Merge with user options
    const mergedOptions = { ...defaultOptions, ...options };
    
    // Set debug mode
    setDebugMode(mergedOptions.debug);
    
    // Register service worker if enabled
    if (mergedOptions.registerServiceWorker) {
      await registerServiceWorker(mergedOptions.serviceWorkerPath);
    }
    
    // Set up connectivity monitoring
    initConnectivityMonitoring(mergedOptions);
    
    // Configure sync manager if enabled
    if (mergedOptions.syncEnabled) {
      configureSyncManager({
        autoSync: true,
        syncInterval: mergedOptions.syncInterval
      });
    }
    
    // Initialize IndexedDB
    await initializeIndexedDB();
    
    // Set flag
    isInitialized = true;
    
    // Log success
    console.log('Offline functionality initialized successfully');
    return true;
  } catch (error) {
    console.error('Error initializing offline functionality:', error);
    return false;
  }
}

/**
 * Register the service worker
 * @param {string} path - Path to service worker file
 * @returns {Promise<ServiceWorkerRegistration|null>} - Service worker registration or null if not supported
 */
export async function registerServiceWorker(path = '/static/js/offline/service-worker.js') {
  if (!('serviceWorker' in navigator)) {
    console.log('Service Worker not supported');
    return null;
  }
  
  try {
    const registration = await navigator.serviceWorker.register(path);
    console.log('Service Worker registered successfully:', registration.scope);
    
    // Wait for the service worker to be ready
    await navigator.serviceWorker.ready;
    console.log('Service Worker ready');
    
    return registration;
  } catch (error) {
    console.error('Service Worker registration failed:', error);
    return null;
  }
}

/**
 * Initialize IndexedDB databases
 * @returns {Promise<boolean>} - Success indicator
 */
async function initializeIndexedDB() {
  try {
    // Open all databases to ensure they're created
    await IndexedDB.offlineRequestsDb.open();
    await IndexedDB.offlineDataDb.open();
    await IndexedDB.localSettingsDb.open();
    
    // Close connections for now
    IndexedDB.offlineRequestsDb.close();
    IndexedDB.offlineDataDb.close();
    IndexedDB.localSettingsDb.close();
    
    return true;
  } catch (error) {
    console.error('Error initializing IndexedDB:', error);
    return false;
  }
}

/**
 * Configure the sync manager
 * @param {Object} options - Sync manager options
 */
export function configureSyncManager(options = {}) {
  // Update sync manager options
  SyncManager.updateOptions(options);
  
  // Start auto sync if specified and we're online
  if (options.autoSync !== undefined) {
    if (options.autoSync && navigator.onLine) {
      SyncManager.startAutoSync();
    } else {
      SyncManager.stopAutoSync();
    }
  }
}

/**
 * Initialize connectivity monitoring
 * @param {Object} options - Configuration options
 */
function initConnectivityMonitoring(options) {
  // Set initial network status
  networkStatus = navigator.onLine;
  
  // Add online/offline event listeners
  window.addEventListener('online', () => {
    networkStatus = true;
    
    // Show online status
    if (options.offlineIndicator) {
      updateOfflineIndicator(false);
    }
    
    // Trigger sync if enabled
    if (options.syncOnReconnect) {
      SyncManager.syncNow().catch(console.error);
    }
    
    // Notify connection listeners
    notifyConnectionListeners();
  });
  
  window.addEventListener('offline', () => {
    networkStatus = false;
    
    // Show offline status
    if (options.offlineIndicator) {
      updateOfflineIndicator(true);
    }
    
    // Notify connection listeners
    notifyConnectionListeners();
  });
  
  // Set up offline indicator if enabled
  if (options.offlineIndicator) {
    setupOfflineIndicator(options.offlineIndicatorSelector);
  }
}

/**
 * Set up the offline indicator element
 * @param {string} selector - CSS selector for the indicator element
 */
function setupOfflineIndicator(selector) {
  let indicator = document.querySelector(selector);
  
  // If indicator doesn't exist, create it
  if (!indicator) {
    indicator = document.createElement('div');
    indicator.id = selector.replace('#', '');
    indicator.className = 'offline-indicator';
    indicator.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background-color: #f44336;
      color: white;
      text-align: center;
      padding: 5px;
      font-size: 14px;
      font-weight: bold;
      z-index: 9999;
      display: none;
    `;
    indicator.textContent = 'You are offline. Changes will be saved and synced when you reconnect.';
    document.body.appendChild(indicator);
  }
  
  // Set initial state
  updateOfflineIndicator(!navigator.onLine);
}

/**
 * Update the offline indicator visibility
 * @param {boolean} isOffline - Whether device is offline
 */
function updateOfflineIndicator(isOffline) {
  const indicator = document.querySelector('#offline-indicator');
  if (indicator) {
    indicator.style.display = isOffline ? 'block' : 'none';
  }
}

/**
 * Notify all connection listeners about network status change
 */
function notifyConnectionListeners() {
  const status = {
    online: networkStatus,
    timestamp: new Date()
  };
  
  connectionListeners.forEach(listener => {
    try {
      listener(status);
    } catch (error) {
      console.error('Error in connection listener:', error);
    }
  });
}

/**
 * Add a connection listener
 * @param {Function} listener - Callback function
 * @returns {Function} - Function to remove the listener
 */
export function addConnectionListener(listener) {
  if (typeof listener === 'function') {
    connectionListeners.push(listener);
    
    // Return function to remove the listener
    return () => {
      const index = connectionListeners.indexOf(listener);
      if (index !== -1) {
        connectionListeners.splice(index, 1);
      }
    };
  }
  return () => {}; // No-op if invalid listener
}

/**
 * Enable or disable debug mode
 * @param {boolean} enabled - Whether debug mode is enabled
 */
export function setDebugMode(enabled) {
  const debugMode = !!enabled;
  
  // Store debug mode preference
  try {
    localStorage.setItem('magnetocursor_offline_debug', debugMode.toString());
  } catch (e) {
    // Ignore localStorage errors
  }
  
  // Override console methods if disabled
  if (!debugMode) {
    // Save original console methods
    if (!window._originalConsole) {
      window._originalConsole = {
        log: console.log,
        debug: console.debug
      };
      
      // Filter offline-related logs
      console.log = function(...args) {
        if (typeof args[0] === 'string' && 
            (args[0].includes('[Service Worker]') || 
             args[0].includes('offline') || 
             args[0].includes('Sync'))) {
          return;
        }
        window._originalConsole.log.apply(console, args);
      };
      
      console.debug = function(...args) {
        if (typeof args[0] === 'string' && 
            (args[0].includes('[Service Worker]') || 
             args[0].includes('offline') || 
             args[0].includes('Sync'))) {
          return;
        }
        window._originalConsole.debug.apply(console, args);
      };
    }
  } else {
    // Restore original console methods
    if (window._originalConsole) {
      console.log = window._originalConsole.log;
      console.debug = window._originalConsole.debug;
      delete window._originalConsole;
    }
  }
}

/**
 * Get current network status
 * @returns {boolean} - Whether device is online
 */
export function getNetworkStatus() {
  return networkStatus;
}

/**
 * Force a synchronization
 * @returns {Promise<Object>} - Sync result
 */
export function syncNow() {
  return SyncManager.syncNow();
}

/**
 * Set manual conflict resolution handler
 * @param {Function} handler - Conflict resolution handler
 */
export function setConflictHandler(handler) {
  if (typeof handler === 'function') {
    const resolver = new ConflictResolver({
      defaultResolution: ResolutionType.MANUAL,
      manualResolutionCallback: handler
    });
    
    SyncManager.updateOptions({
      conflictResolver: resolver
    });
  }
}

/**
 * Save a WebSocket filter for offline use
 * @param {Object} filter - The filter object
 * @returns {Promise<boolean>} - Success indicator
 */
export async function saveFilterOffline(filter) {
  try {
    // Validate filter
    if (!filter || !filter.id) {
      throw new Error('Invalid filter object');
    }
    
    // Cache the filter data
    await IndexedDB.cacheEntityData('filter', filter);
    
    return true;
  } catch (error) {
    console.error('Error saving filter offline:', error);
    return false;
  }
}

/**
 * Get a WebSocket filter from offline cache
 * @param {string} filterId - Filter ID
 * @returns {Promise<Object|null>} - Filter object or null if not found
 */
export async function getOfflineFilter(filterId) {
  try {
    return await IndexedDB.getCachedEntity('filter', filterId);
  } catch (error) {
    console.error('Error getting offline filter:', error);
    return null;
  }
}

/**
 * Get all WebSocket filters from offline cache
 * @returns {Promise<Array>} - Array of filter objects
 */
export async function getAllOfflineFilters() {
  try {
    return await IndexedDB.getAllCachedEntities('filter');
  } catch (error) {
    console.error('Error getting all offline filters:', error);
    return [];
  }
}

/**
 * Update a WebSocket filter with offline changes
 * @param {string} filterId - Filter ID
 * @param {Object} changes - Changes to apply
 * @returns {Promise<boolean>} - Success indicator
 */
export async function updateFilterOffline(filterId, changes) {
  try {
    // Get current filter from cache
    const filter = await IndexedDB.getCachedEntity('filter', filterId);
    
    if (!filter) {
      throw new Error(`Filter with ID ${filterId} not found in offline cache`);
    }
    
    // Apply changes
    const updatedFilter = { ...filter, ...changes };
    
    // Queue for sync
    await addOfflineChange('filter', 'update', updatedFilter, filterId);
    
    return true;
  } catch (error) {
    console.error('Error updating filter offline:', error);
    return false;
  }
}

/**
 * Create a new WebSocket filter with offline support
 * @param {Object} filter - New filter object
 * @returns {Promise<Object>} - Created filter with generated ID
 */
export async function createFilterOffline(filter) {
  try {
    // Generate a temporary ID
    const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Create a new filter object with temporary ID
    const newFilter = {
      ...filter,
      id: tempId,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    // Queue for sync
    await addOfflineChange('filter', 'create', newFilter);
    
    return newFilter;
  } catch (error) {
    console.error('Error creating filter offline:', error);
    throw error;
  }
}

/**
 * Delete a WebSocket filter with offline support
 * @param {string} filterId - Filter ID
 * @returns {Promise<boolean>} - Success indicator
 */
export async function deleteFilterOffline(filterId) {
  try {
    // Queue for sync
    await addOfflineChange('filter', 'delete', null, filterId);
    
    return true;
  } catch (error) {
    console.error('Error deleting filter offline:', error);
    return false;
  }
}

/**
 * Save user preferences for offline use
 * @param {string} key - Preference key
 * @param {any} value - Preference value
 * @returns {Promise<boolean>} - Success indicator
 */
export async function savePreference(key, value) {
  try {
    await IndexedDB.saveUserPreference(key, value);
    return true;
  } catch (error) {
    console.error('Error saving preference:', error);
    return false;
  }
}

/**
 * Get user preference
 * @param {string} key - Preference key
 * @returns {Promise<any>} - Preference value
 */
export async function getPreference(key) {
  try {
    return await IndexedDB.getUserPreference(key);
  } catch (error) {
    console.error('Error getting preference:', error);
    return null;
  }
}

/**
 * Get pending changes count
 * @returns {Promise<number>} - Number of pending changes
 */
export async function getPendingChangesCount() {
  try {
    const changes = await IndexedDB.getPendingChanges();
    return changes.length;
  } catch (error) {
    console.error('Error getting pending changes count:', error);
    return 0;
  }
}

/**
 * Check if the browser supports offline functionality
 * @returns {Object} - Support status for various features
 */
export function checkOfflineSupport() {
  return {
    serviceWorker: 'serviceWorker' in navigator,
    backgroundSync: 'serviceWorker' in navigator && 'SyncManager' in window,
    indexedDB: 'indexedDB' in window,
    cacheAPI: 'caches' in window,
    offlineEvents: 'onLine' in navigator
  };
}

/**
 * Clear all offline data
 * @returns {Promise<boolean>} - Success indicator
 */
export async function clearOfflineData() {
  try {
    // Stop sync manager
    SyncManager.stopAutoSync();
    
    // Clear all data
    await IndexedDB.clearAllOfflineData();
    
    // Clear caches if cache API is available
    if ('caches' in window) {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName.startsWith('magnetocursor-')) {
            return caches.delete(cacheName);
          }
        })
      );
    }
    
    return true;
  } catch (error) {
    console.error('Error clearing offline data:', error);
    return false;
  }
}

// Export everything from IndexedDB, SyncManager, and ConflictResolver
export {
  IndexedDB,
  SyncManager,
  ResolutionType,
  deepMerge,
  createTimestampResolver,
  createFieldPriorityResolver,
  isOnline,
  isBackgroundSyncSupported,
  addOfflineChange
};

// Create a default instance
const OfflineManager = {
  initialize,
  registerServiceWorker,
  configureSyncManager,
  getNetworkStatus,
  syncNow,
  setConflictHandler,
  saveFilterOffline,
  getOfflineFilter,
  getAllOfflineFilters,
  updateFilterOffline,
  createFilterOffline,
  deleteFilterOffline,
  savePreference,
  getPreference,
  getPendingChangesCount,
  checkOfflineSupport,
  clearOfflineData,
  addConnectionListener
};

// Export the default instance
export default OfflineManager;
