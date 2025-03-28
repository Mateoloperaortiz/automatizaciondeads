/**
 * Real-Time API Client
 * Provides real-time updates for various entities using WebSockets
 */

import { websocketService } from './websocket-service.js';
import { toastService } from './toast-service.js';

/**
 * Entity types that can be watched for real-time updates
 */
export const WATCHED_ENTITIES = {
  CAMPAIGN: 'campaign',
  SEGMENT: 'segment',
  CANDIDATE: 'candidate',
  JOB_OPENING: 'job_opening',
  PLATFORM_STATUS: 'platform_status',
  ANALYTICS: 'analytics'
};

/**
 * Update types that can be received
 */
export const UPDATE_TYPES = {
  CREATED: 'created',
  UPDATED: 'updated',
  DELETED: 'deleted',
  PUBLISHED: 'published',
  STATUS_CHANGE: 'status_change'
};

/**
 * RealTimeApiClient
 * Centralizes real-time API communication using WebSockets
 */
export class RealTimeApiClient {
  /**
   * Create a new RealTimeApiClient
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = {
      wsEndpoint: '/api/real-time',
      autoConnect: true,
      debug: false,
      showNotifications: true,
      ...options
    };
    
    this.isConnected = false;
    this.subscribedEntities = new Set();
    this.eventListeners = new Map();
    this.pendingSubscriptions = [];
    
    // Connect if autoConnect is enabled
    if (this.options.autoConnect) {
      this.connect();
    }
  }
  
  /**
   * Connect to WebSocket server
   * @returns {Promise<boolean>} - Whether connection was successful
   */
  async connect() {
    try {
      // Connect to WebSocket
      await websocketService.connect(this.options.wsEndpoint);
      
      // Set up event handlers
      this._setupEventHandlers();
      
      // Process any pending subscriptions
      this._processPendingSubscriptions();
      
      this.isConnected = true;
      this._debug('Real-time API client connected');
      
      return true;
    } catch (error) {
      console.error('Failed to connect to real-time API:', error);
      this.isConnected = false;
      return false;
    }
  }
  
  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    // Unsubscribe from all entities
    this.unsubscribeAll();
    
    // Disconnect WebSocket
    websocketService.disconnect();
    this.isConnected = false;
    
    this._debug('Real-time API client disconnected');
  }
  
  /**
   * Subscribe to real-time updates for an entity
   * @param {string} entityType - Type of entity to watch
   * @param {string|number} entityId - ID of entity to watch
   * @returns {Promise<boolean>} - Whether subscription was successful
   */
  async subscribeToEntity(entityType, entityId) {
    // Validate entity type
    if (!Object.values(WATCHED_ENTITIES).includes(entityType)) {
      console.error(`Invalid entity type: ${entityType}`);
      return false;
    }
    
    // Create unique subscription key
    const subscriptionKey = this._createSubscriptionKey(entityType, entityId);
    
    // If already subscribed, do nothing
    if (this.subscribedEntities.has(subscriptionKey)) {
      return true;
    }
    
    // If not connected, queue subscription for later
    if (!this.isConnected) {
      this.pendingSubscriptions.push({ entityType, entityId });
      this._debug(`Queued subscription to ${entityType}:${entityId}`);
      return false;
    }
    
    try {
      // Send subscription request
      websocketService.send({
        type: 'subscribe',
        entity_type: entityType,
        entity_id: entityId
      });
      
      // Add to subscribed entities
      this.subscribedEntities.add(subscriptionKey);
      
      this._debug(`Subscribed to ${entityType}:${entityId}`);
      return true;
    } catch (error) {
      console.error(`Error subscribing to ${entityType}:${entityId}:`, error);
      return false;
    }
  }
  
  /**
   * Unsubscribe from updates for an entity
   * @param {string} entityType - Type of entity
   * @param {string|number} entityId - ID of entity
   * @returns {boolean} - Whether unsubscription was successful
   */
  unsubscribeFromEntity(entityType, entityId) {
    // Create unique subscription key
    const subscriptionKey = this._createSubscriptionKey(entityType, entityId);
    
    // If not subscribed, do nothing
    if (!this.subscribedEntities.has(subscriptionKey)) {
      return true;
    }
    
    // If not connected, remove from pending subscriptions
    if (!this.isConnected) {
      this.pendingSubscriptions = this.pendingSubscriptions.filter(
        sub => !(sub.entityType === entityType && sub.entityId === entityId)
      );
      return true;
    }
    
    try {
      // Send unsubscription request
      websocketService.send({
        type: 'unsubscribe',
        entity_type: entityType,
        entity_id: entityId
      });
      
      // Remove from subscribed entities
      this.subscribedEntities.delete(subscriptionKey);
      
      this._debug(`Unsubscribed from ${entityType}:${entityId}`);
      return true;
    } catch (error) {
      console.error(`Error unsubscribing from ${entityType}:${entityId}:`, error);
      return false;
    }
  }
  
  /**
   * Unsubscribe from all entities
   */
  unsubscribeAll() {
    // If not connected, clear pending subscriptions
    if (!this.isConnected) {
      this.pendingSubscriptions = [];
      return;
    }
    
    try {
      // Send unsubscribe all request
      websocketService.send({
        type: 'unsubscribe_all'
      });
      
      // Clear subscribed entities
      this.subscribedEntities.clear();
      
      this._debug('Unsubscribed from all entities');
    } catch (error) {
      console.error('Error unsubscribing from all entities:', error);
    }
  }
  
  /**
   * Register an event listener for entity updates
   * @param {string} entityType - Type of entity
   * @param {string} updateType - Type of update
   * @param {Function} callback - Event handler function
   * @returns {Function} - Function to remove the listener
   */
  onEntityUpdate(entityType, updateType, callback) {
    // Create event key
    const eventKey = `${entityType}:${updateType}`;
    
    // Create event entry if it doesn't exist
    if (!this.eventListeners.has(eventKey)) {
      this.eventListeners.set(eventKey, []);
    }
    
    // Add callback to listeners
    this.eventListeners.get(eventKey).push(callback);
    
    // Return function to remove the listener
    return () => {
      const listeners = this.eventListeners.get(eventKey);
      if (!listeners) return;
      
      const index = listeners.indexOf(callback);
      if (index !== -1) {
        listeners.splice(index, 1);
      }
    };
  }
  
  /**
   * Register an event listener for all updates of an entity type
   * @param {string} entityType - Type of entity
   * @param {Function} callback - Event handler function
   * @returns {Function} - Function to remove the listener
   */
  onAnyEntityUpdate(entityType, callback) {
    // Register for all update types
    const removeListeners = Object.values(UPDATE_TYPES).map(updateType => {
      return this.onEntityUpdate(entityType, updateType, callback);
    });
    
    // Return function to remove all listeners
    return () => {
      removeListeners.forEach(remove => remove());
    };
  }
  
  /**
   * Set up WebSocket event handlers
   * @private
   */
  _setupEventHandlers() {
    // Handle entity update messages
    websocketService.on('message', data => {
      if (data.type === 'entity_update') {
        this._handleEntityUpdate(data);
      }
    });
    
    // Handle reconnection
    websocketService.on('reconnecting', () => {
      this.isConnected = false;
    });
    
    websocketService.on('open', () => {
      this.isConnected = true;
      
      // Resubscribe to all entities after reconnection
      this._resubscribeAll();
    });
  }
  
  /**
   * Process any pending subscriptions
   * @private
   */
  _processPendingSubscriptions() {
    if (this.pendingSubscriptions.length === 0) return;
    
    // Subscribe to all pending entities
    this.pendingSubscriptions.forEach(async ({ entityType, entityId }) => {
      await this.subscribeToEntity(entityType, entityId);
    });
    
    // Clear pending subscriptions
    this.pendingSubscriptions = [];
  }
  
  /**
   * Resubscribe to all entities after reconnection
   * @private
   */
  _resubscribeAll() {
    // Create subscription requests for all subscribed entities
    const subscriptions = Array.from(this.subscribedEntities).map(key => {
      const [entityType, entityId] = key.split(':');
      return { entityType, entityId };
    });
    
    // Clear subscribed entities
    this.subscribedEntities.clear();
    
    // Resubscribe to each entity
    subscriptions.forEach(async ({ entityType, entityId }) => {
      await this.subscribeToEntity(entityType, entityId);
    });
  }
  
  /**
   * Handle entity update message
   * @param {Object} data - Update message data
   * @private
   */
  _handleEntityUpdate(data) {
    const { entity_type: entityType, update_type: updateType, entity } = data;
    
    // Create event key
    const eventKey = `${entityType}:${updateType}`;
    
    // Notify listeners for this specific event
    if (this.eventListeners.has(eventKey)) {
      this.eventListeners.get(eventKey).forEach(callback => {
        try {
          callback(entity, data);
        } catch (error) {
          console.error(`Error in entity update handler for ${eventKey}:`, error);
        }
      });
    }
    
    // Show notification if enabled
    if (this.options.showNotifications) {
      this._showUpdateNotification(entityType, updateType, entity);
    }
  }
  
  /**
   * Show notification for entity update
   * @param {string} entityType - Type of entity
   * @param {string} updateType - Type of update
   * @param {Object} entity - Updated entity
   * @private
   */
  _showUpdateNotification(entityType, updateType, entity) {
    // Skip if entity doesn't have a name or title
    if (!entity) return;
    
    const entityName = entity.name || entity.title || `#${entity.id}`;
    let message = '';
    let type = 'info';
    
    switch (updateType) {
      case UPDATE_TYPES.CREATED:
        message = `New ${this._formatEntityType(entityType)}: ${entityName}`;
        type = 'success';
        break;
        
      case UPDATE_TYPES.UPDATED:
        message = `${this._formatEntityType(entityType)} updated: ${entityName}`;
        break;
        
      case UPDATE_TYPES.DELETED:
        message = `${this._formatEntityType(entityType)} deleted: ${entityName}`;
        type = 'warning';
        break;
        
      case UPDATE_TYPES.PUBLISHED:
        message = `${this._formatEntityType(entityType)} published: ${entityName}`;
        type = 'success';
        break;
        
      case UPDATE_TYPES.STATUS_CHANGE:
        const status = entity.status || 'unknown';
        message = `${this._formatEntityType(entityType)} ${entityName} status changed to ${status}`;
        
        // Set notification type based on status
        if (status === 'active' || status === 'published' || status === 'completed') {
          type = 'success';
        } else if (status === 'draft' || status === 'paused') {
          type = 'info';
        } else if (status === 'cancelled' || status === 'failed') {
          type = 'error';
        }
        break;
    }
    
    // Show notification
    if (message) {
      toastService.show(message, type);
    }
  }
  
  /**
   * Format entity type for display
   * @param {string} entityType - Entity type
   * @returns {string} - Formatted entity type
   * @private
   */
  _formatEntityType(entityType) {
    // Convert from snake_case or camelCase to Title Case
    return entityType
      .replace(/([A-Z])/g, ' $1') // Add space before capital letters
      .replace(/_/g, ' ') // Replace underscores with spaces
      .trim() // Remove leading/trailing spaces
      .split(' ') // Split into words
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize first letter
      .join(' '); // Join words with spaces
  }
  
  /**
   * Create unique subscription key
   * @param {string} entityType - Type of entity
   * @param {string|number} entityId - ID of entity
   * @returns {string} - Subscription key
   * @private
   */
  _createSubscriptionKey(entityType, entityId) {
    return `${entityType}:${entityId}`;
  }
  
  /**
   * Log debug messages if debug is enabled
   * @param {string} message - Debug message
   * @private
   */
  _debug(message) {
    if (this.options.debug) {
      console.log(`[RealTimeApiClient] ${message}`);
    }
  }
}

// Create singleton instance
const realTimeApiClient = new RealTimeApiClient();

export { realTimeApiClient };