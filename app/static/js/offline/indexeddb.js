/**
 * MagnetoCursor - IndexedDB Manager
 * 
 * Provides a unified interface for offline data storage using IndexedDB.
 * Handles database operations for storing and retrieving data when offline.
 */

/**
 * IndexedDB Store - handles database operations for a specific object store
 */
class DbStore {
  /**
   * Create a new DbStore
   * @param {IDBDatabase} db - IndexedDB database connection
   * @param {string} storeName - Name of the object store
   */
  constructor(db, storeName) {
    this.db = db;
    this.storeName = storeName;
  }
  
  /**
   * Get a single item by ID
   * @param {any} id - Item ID
   * @returns {Promise<Object>} - The retrieved item or undefined if not found
   */
  async get(id) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.get(id);
      
      request.onsuccess = () => {
        resolve(request.result);
      };
      
      request.onerror = () => {
        reject(request.error);
      };
    });
  }
  
  /**
   * Get all items from the store
   * @param {IDBKeyRange} query - Optional query range
   * @returns {Promise<Array>} - Array of retrieved items
   */
  async getAll(query = null) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.getAll(query);
      
      request.onsuccess = () => {
        resolve(request.result);
      };
      
      request.onerror = () => {
        reject(request.error);
      };
    });
  }
  
  /**
   * Add a new item
   * @param {Object} item - The item to add
   * @returns {Promise<number>} - ID of the added item
   */
  async add(item) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.add(item);
      
      request.onsuccess = () => {
        resolve(request.result);
      };
      
      request.onerror = () => {
        reject(request.error);
      };
    });
  }
  
  /**
   * Put an item (add or update)
   * @param {Object} item - The item to put
   * @returns {Promise<number>} - ID of the item
   */
  async put(item) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.put(item);
      
      request.onsuccess = () => {
        resolve(request.result);
      };
      
      request.onerror = () => {
        reject(request.error);
      };
    });
  }
  
  /**
   * Delete an item by ID
   * @param {any} id - ID of the item to delete
   * @returns {Promise<void>}
   */
  async delete(id) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.delete(id);
      
      request.onsuccess = () => {
        resolve();
      };
      
      request.onerror = () => {
        reject(request.error);
      };
    });
  }
  
  /**
   * Clear all items from the store
   * @returns {Promise<void>}
   */
  async clear() {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.clear();
      
      request.onsuccess = () => {
        resolve();
      };
      
      request.onerror = () => {
        reject(request.error);
      };
    });
  }
  
  /**
   * Get items by index
   * @param {string} indexName - Name of the index
   * @param {any} indexValue - Value to query
   * @returns {Promise<Array>} - Array of matching items
   */
  async getByIndex(indexName, indexValue) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, 'readonly');
      const store = transaction.objectStore(this.storeName);
      const index = store.index(indexName);
      const request = index.getAll(indexValue);
      
      request.onsuccess = () => {
        resolve(request.result);
      };
      
      request.onerror = () => {
        reject(request.error);
      };
    });
  }
  
  /**
   * Count items in the store
   * @param {IDBKeyRange} query - Optional query range
   * @returns {Promise<number>} - Number of items
   */
  async count(query = null) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.count(query);
      
      request.onsuccess = () => {
        resolve(request.result);
      };
      
      request.onerror = () => {
        reject(request.error);
      };
    });
  }
}

/**
 * IndexedDB Manager - main class for interacting with IndexedDB
 */
class IndexedDbManager {
  /**
   * Create a new IndexedDbManager
   * @param {string} dbName - Database name
   * @param {number} version - Database version
   * @param {Array} storeDefinitions - Array of store definitions
   */
  constructor(dbName, version, storeDefinitions) {
    this.dbName = dbName;
    this.version = version;
    this.storeDefinitions = storeDefinitions;
    this.db = null;
    this.stores = {};
  }
  
  /**
   * Open the database connection
   * @returns {Promise<IDBDatabase>} - The database connection
   */
  async open() {
    if (this.db) {
      return this.db;
    }
    
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Process store definitions on database upgrade
        this.storeDefinitions.forEach(storeDef => {
          if (!db.objectStoreNames.contains(storeDef.name)) {
            // Create the object store
            const store = db.createObjectStore(
              storeDef.name, 
              { keyPath: storeDef.keyPath, autoIncrement: !!storeDef.autoIncrement }
            );
            
            // Create indexes if specified
            if (storeDef.indexes) {
              storeDef.indexes.forEach(indexDef => {
                store.createIndex(
                  indexDef.name,
                  indexDef.keyPath, 
                  { unique: !!indexDef.unique }
                );
              });
            }
          }
        });
      };
      
      request.onsuccess = (event) => {
        this.db = event.target.result;
        
        // Create store objects for each store
        this.storeDefinitions.forEach(storeDef => {
          this.stores[storeDef.name] = new DbStore(this.db, storeDef.name);
        });
        
        resolve(this.db);
      };
      
      request.onerror = () => {
        reject(request.error);
      };
    });
  }
  
  /**
   * Close the database connection
   */
  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
  
  /**
   * Get a store object
   * @param {string} storeName - Name of the store
   * @returns {DbStore} - The store object
   */
  store(storeName) {
    if (!this.db) {
      throw new Error('Database not open. Call open() first.');
    }
    
    if (!this.stores[storeName]) {
      throw new Error(`Store '${storeName}' not found`);
    }
    
    return this.stores[storeName];
  }
  
  /**
   * Delete the entire database
   * @returns {Promise<void>}
   */
  static async deleteDatabase(dbName) {
    return new Promise((resolve, reject) => {
      const request = indexedDB.deleteDatabase(dbName);
      
      request.onsuccess = () => {
        resolve();
      };
      
      request.onerror = () => {
        reject(request.error);
      };
    });
  }
}

// Default database configurations

// Offline requests database
const offlineRequestsDb = new IndexedDbManager('offline-requests', 1, [
  {
    name: 'requests',
    keyPath: 'id',
    autoIncrement: true,
    indexes: [
      { name: 'urlIndex', keyPath: 'url' },
      { name: 'timestampIndex', keyPath: 'timestamp' }
    ]
  }
]);

// Offline data cache database
const offlineDataDb = new IndexedDbManager('offline-data', 1, [
  {
    name: 'campaigns',
    keyPath: 'id',
    indexes: [
      { name: 'entityTypeIndex', keyPath: 'entityType' },
      { name: 'updatedAtIndex', keyPath: 'updatedAt' }
    ]
  },
  {
    name: 'filters',
    keyPath: 'id',
    indexes: [
      { name: 'categoryIndex', keyPath: 'category' },
      { name: 'updatedAtIndex', keyPath: 'updatedAt' }
    ]
  },
  {
    name: 'syncLog',
    keyPath: 'id',
    autoIncrement: true,
    indexes: [
      { name: 'timestampIndex', keyPath: 'timestamp' },
      { name: 'statusIndex', keyPath: 'status' }
    ]
  },
  {
    name: 'pendingChanges',
    keyPath: 'id',
    autoIncrement: true,
    indexes: [
      { name: 'entityIdIndex', keyPath: 'entityId' },
      { name: 'entityTypeIndex', keyPath: 'entityType' },
      { name: 'operationIndex', keyPath: 'operation' },
      { name: 'timestampIndex', keyPath: 'timestamp' }
    ]
  }
]);

// Local settings database
const localSettingsDb = new IndexedDbManager('local-settings', 1, [
  {
    name: 'settings',
    keyPath: 'key'
  },
  {
    name: 'userPreferences',
    keyPath: 'key'
  }
]);

/**
 * Get a store from any of the default databases
 * @param {string} databaseName - Database name ('offline-requests', 'offline-data', or 'local-settings')
 * @param {string} storeName - Store name
 * @returns {Promise<DbStore>} - The store object
 */
async function getStore(databaseName, storeName) {
  let db;
  
  switch (databaseName) {
    case 'offline-requests':
      db = offlineRequestsDb;
      break;
    case 'offline-data':
      db = offlineDataDb;
      break;
    case 'local-settings':
      db = localSettingsDb;
      break;
    default:
      throw new Error(`Unknown database: ${databaseName}`);
  }
  
  await db.open();
  return db.store(storeName);
}

// Export the core classes and utility functions
export {
  IndexedDbManager,
  DbStore,
  offlineRequestsDb,
  offlineDataDb,
  localSettingsDb,
  getStore
};

// Export convenience functions for common operations

/**
 * Save a request for offline syncing
 * @param {Object} request - The request object to save
 * @returns {Promise<number>} - ID of the saved request
 */
export async function saveOfflineRequest(request) {
  await offlineRequestsDb.open();
  return offlineRequestsDb.store('requests').add({
    url: request.url,
    method: request.method,
    headers: request.headers,
    body: request.body,
    timestamp: Date.now(),
    retryCount: 0
  });
}

/**
 * Get all pending offline requests
 * @returns {Promise<Array>} - Array of pending requests
 */
export async function getPendingRequests() {
  await offlineRequestsDb.open();
  return offlineRequestsDb.store('requests').getAll();
}

/**
 * Delete a synced request
 * @param {number} id - ID of the request to delete
 * @returns {Promise<void>}
 */
export async function deleteSyncedRequest(id) {
  await offlineRequestsDb.open();
  return offlineRequestsDb.store('requests').delete(id);
}

/**
 * Cache entity data for offline use
 * @param {string} entityType - Entity type (e.g., 'campaign', 'filter')
 * @param {Object} data - Entity data
 * @returns {Promise<any>} - Result of the operation
 */
export async function cacheEntityData(entityType, data) {
  await offlineDataDb.open();
  
  // Determine the appropriate store based on entity type
  let storeName;
  switch (entityType) {
    case 'campaign':
      storeName = 'campaigns';
      break;
    case 'filter':
      storeName = 'filters';
      break;
    default:
      throw new Error(`Unknown entity type: ${entityType}`);
  }
  
  // Add cache timestamp
  const dataWithTimestamp = {
    ...data,
    cachedAt: Date.now()
  };
  
  return offlineDataDb.store(storeName).put(dataWithTimestamp);
}

/**
 * Get cached entity data
 * @param {string} entityType - Entity type
 * @param {string|number} id - Entity ID
 * @returns {Promise<Object>} - Cached entity data
 */
export async function getCachedEntity(entityType, id) {
  await offlineDataDb.open();
  
  // Determine the appropriate store based on entity type
  let storeName;
  switch (entityType) {
    case 'campaign':
      storeName = 'campaigns';
      break;
    case 'filter':
      storeName = 'filters';
      break;
    default:
      throw new Error(`Unknown entity type: ${entityType}`);
  }
  
  return offlineDataDb.store(storeName).get(id);
}

/**
 * Get all cached entities of a type
 * @param {string} entityType - Entity type
 * @returns {Promise<Array>} - Array of cached entities
 */
export async function getAllCachedEntities(entityType) {
  await offlineDataDb.open();
  
  // Determine the appropriate store based on entity type
  let storeName;
  switch (entityType) {
    case 'campaign':
      storeName = 'campaigns';
      break;
    case 'filter':
      storeName = 'filters';
      break;
    default:
      throw new Error(`Unknown entity type: ${entityType}`);
  }
  
  return offlineDataDb.store(storeName).getAll();
}

/**
 * Save a pending change for later syncing
 * @param {Object} change - The change object
 * @returns {Promise<number>} - ID of the saved change
 */
export async function savePendingChange(change) {
  await offlineDataDb.open();
  return offlineDataDb.store('pendingChanges').add({
    entityId: change.entityId,
    entityType: change.entityType,
    operation: change.operation, // 'create', 'update', or 'delete'
    data: change.data,
    timestamp: Date.now(),
    retryCount: 0,
    status: 'pending'
  });
}

/**
 * Get all pending changes
 * @returns {Promise<Array>} - Array of pending changes
 */
export async function getPendingChanges() {
  await offlineDataDb.open();
  return offlineDataDb.store('pendingChanges').getAll();
}

/**
 * Mark a change as synced
 * @param {number} id - ID of the change
 * @returns {Promise<void>}
 */
export async function markChangeAsSynced(id) {
  await offlineDataDb.open();
  const change = await offlineDataDb.store('pendingChanges').get(id);
  if (change) {
    change.status = 'synced';
    change.syncedAt = Date.now();
    await offlineDataDb.store('pendingChanges').put(change);
  }
}

/**
 * Save a user preference
 * @param {string} key - Preference key
 * @param {any} value - Preference value
 * @returns {Promise<void>}
 */
export async function saveUserPreference(key, value) {
  await localSettingsDb.open();
  return localSettingsDb.store('userPreferences').put({
    key,
    value,
    updatedAt: Date.now()
  });
}

/**
 * Get a user preference
 * @param {string} key - Preference key
 * @returns {Promise<any>} - Preference value
 */
export async function getUserPreference(key) {
  await localSettingsDb.open();
  const preference = await localSettingsDb.store('userPreferences').get(key);
  return preference ? preference.value : null;
}

/**
 * Check if browser supports IndexedDB
 * @returns {boolean} - True if supported
 */
export function isIndexedDbSupported() {
  return !!window.indexedDB;
}

/**
 * Clear all offline data
 * @returns {Promise<void>}
 */
export async function clearAllOfflineData() {
  // Close any open connections
  offlineRequestsDb.close();
  offlineDataDb.close();
  localSettingsDb.close();
  
  // Delete the databases
  await IndexedDbManager.deleteDatabase('offline-requests');
  await IndexedDbManager.deleteDatabase('offline-data');
  
  // Don't delete local settings as they contain user preferences
}
