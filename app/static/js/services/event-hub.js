/**
 * Event Hub Service
 * Provides a centralized event system for cross-component communication
 */

/**
 * EventHub class for managing application-wide events
 */
export class EventHub {
  /**
   * Create a new EventHub
   */
  constructor() {
    this.events = new Map();
    this.eventListenerIds = 0;
  }
  
  /**
   * Subscribe to an event
   * @param {string} eventName - Name of the event to subscribe to
   * @param {Function} callback - Function to call when event is triggered
   * @returns {number} - Subscription ID for unsubscribing
   */
  on(eventName, callback) {
    if (!this.events.has(eventName)) {
      this.events.set(eventName, new Map());
    }
    
    const id = ++this.eventListenerIds;
    this.events.get(eventName).set(id, callback);
    
    return id;
  }
  
  /**
   * Subscribe to an event once
   * @param {string} eventName - Name of the event to subscribe to
   * @param {Function} callback - Function to call when event is triggered
   * @returns {number} - Subscription ID for unsubscribing
   */
  once(eventName, callback) {
    const wrappedCallback = (...args) => {
      this.off(eventName, id);
      callback(...args);
    };
    
    const id = this.on(eventName, wrappedCallback);
    return id;
  }
  
  /**
   * Unsubscribe from an event
   * @param {string} eventName - Name of the event
   * @param {number} id - Subscription ID returned from on() or once()
   * @returns {boolean} - Whether the unsubscribe was successful
   */
  off(eventName, id) {
    if (!this.events.has(eventName)) {
      return false;
    }
    
    const eventMap = this.events.get(eventName);
    const result = eventMap.delete(id);
    
    // Remove event if no more listeners
    if (eventMap.size === 0) {
      this.events.delete(eventName);
    }
    
    return result;
  }
  
  /**
   * Unsubscribe from all events with a specific name
   * @param {string} eventName - Name of the event
   * @returns {boolean} - Whether the unsubscribe was successful
   */
  offAll(eventName) {
    if (!this.events.has(eventName)) {
      return false;
    }
    
    return this.events.delete(eventName);
  }
  
  /**
   * Clear all event subscriptions
   */
  clear() {
    this.events.clear();
    this.eventListenerIds = 0;
  }
  
  /**
   * Trigger an event
   * @param {string} eventName - Name of the event to trigger
   * @param {...any} args - Arguments to pass to the event handlers
   * @returns {boolean} - Whether any handlers were triggered
   */
  emit(eventName, ...args) {
    if (!this.events.has(eventName)) {
      return false;
    }
    
    const eventMap = this.events.get(eventName);
    const errors = [];
    
    // Call all event handlers
    for (const [id, callback] of eventMap.entries()) {
      try {
        callback(...args);
      } catch (error) {
        console.error(`Error in event handler for ${eventName}:`, error);
        errors.push({ id, error });
      }
    }
    
    // Log all errors after calling all handlers
    if (errors.length > 0) {
      console.error(`${errors.length} errors occurred while emitting event ${eventName}`);
    }
    
    return eventMap.size > 0;
  }
  
  /**
   * Check if an event has subscribers
   * @param {string} eventName - Name of the event
   * @returns {boolean} - Whether the event has subscribers
   */
  hasListeners(eventName) {
    return this.events.has(eventName) && this.events.get(eventName).size > 0;
  }
  
  /**
   * Get the number of subscribers for an event
   * @param {string} eventName - Name of the event
   * @returns {number} - Number of subscribers
   */
  listenerCount(eventName) {
    if (!this.events.has(eventName)) {
      return 0;
    }
    
    return this.events.get(eventName).size;
  }
  
  /**
   * List all event names that have subscribers
   * @returns {Array<string>} - Array of event names
   */
  eventNames() {
    return Array.from(this.events.keys());
  }
}

// Create singleton instance
const eventHub = new EventHub();

// Export default and named export
export default eventHub;