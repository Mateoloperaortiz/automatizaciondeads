/**
 * WebSocket Service
 * Provides utilities for WebSocket connections and real-time features
 */

/**
 * WebSocketService class for managing WebSocket connections
 */
export class WebSocketService {
  /**
   * Create a new WebSocketService instance
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = {
      reconnectAttempts: 5,
      reconnectInterval: 3000,
      pingInterval: 30000,
      pongTimeout: 5000,
      enableAcknowledgments: true,  // Enable message acknowledgments for critical updates
      acknowledgmentTimeout: 2000,  // 2 seconds timeout for acknowledgments
      tokenRefreshThreshold: 300,   // Refresh token 5 minutes before expiry
      autoAuthenticate: true,       // Auto fetch token on init
      ...options
    };
    
    this.socket = null;
    this.reconnectAttempt = 0;
    this.isConnecting = false;
    this.eventListeners = new Map();
    this.reconnectTimer = null;
    this.pingTimer = null;
    this.pongTimer = null;
    this.lastMessageTime = 0;
    
    // Authentication
    this.authToken = null;
    this.tokenExpiry = null;
    this.tokenRefreshTimer = null;
    this.permissions = [];
    
    // Message acknowledgment tracking
    this.pendingAcknowledgments = new Map();
    this.acknowledgmentId = 1;
    
    // Auto-authenticate if configured
    if (this.options.autoAuthenticate) {
      this.refreshAuthToken().catch(err => console.error('Failed to auto-authenticate:', err));
    }
  }
  
  /**
   * Set auth token for WebSocket connections
   * @param {string} token - JWT token
   * @param {number} expiresIn - Token expiry time in seconds
   * @param {Array} permissions - Optional array of permissions
   */
  setAuthToken(token, expiresIn, permissions = []) {
    this.authToken = token;
    this.tokenExpiry = Date.now() + (expiresIn * 1000);
    this.permissions = permissions;
    
    // Setup token refresh timer
    this._setupTokenRefreshTimer();
    
    console.debug(`WebSocket auth token set, expires in ${expiresIn}s`);
  }
  
  /**
   * Setup timer for token refresh
   * @private
   */
  _setupTokenRefreshTimer() {
    // Clear existing timer
    if (this.tokenRefreshTimer) {
      clearTimeout(this.tokenRefreshTimer);
      this.tokenRefreshTimer = null;
    }
    
    // Skip if no token expiry
    if (!this.tokenExpiry) return;
    
    // Calculate refresh time (before token expires)
    const now = Date.now();
    const refreshTime = this.tokenExpiry - (this.options.tokenRefreshThreshold * 1000);
    
    // If already past refresh time, refresh immediately
    if (now >= refreshTime) {
      this.refreshAuthToken();
      return;
    }
    
    // Set timer for refresh
    const delay = refreshTime - now;
    this.tokenRefreshTimer = setTimeout(() => {
      this.refreshAuthToken();
    }, delay);
    
    console.debug(`Token refresh scheduled in ${Math.round(delay/1000)}s`);
  }
  
  /**
   * Refresh auth token
   * @returns {Promise<boolean>} Success status
   */
  async refreshAuthToken() {
    try {
      console.debug('Refreshing WebSocket authentication token...');
      
      const response = await fetch('/api/websocket/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin'
      });
      
      if (!response.ok) {
        throw new Error(`Token refresh failed: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status !== 'success' || !data.token) {
        throw new Error('Invalid token response');
      }
      
      // Store the new token
      this.setAuthToken(data.token, data.expires_in, data.permissions);
      
      // If socket is connected, reconnect with new token
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this._reconnectWithNewToken();
      }
      
      return true;
    } catch (error) {
      console.error('Error refreshing auth token:', error);
      return false;
    }
  }
  
  /**
   * Reconnect with new token
   * @private
   */
  _reconnectWithNewToken() {
    console.debug('Reconnecting WebSocket with new token...');
    
    // Store current URL
    const currentUrl = this._currentUrl;
    
    if (!currentUrl) {
      console.error('No current URL for reconnection');
      return;
    }
    
    // Close current connection
    this.disconnect(1000, 'Token refresh');
    
    // Reconnect with new token
    setTimeout(() => {
      this.connect(currentUrl);
    }, 100);
  }
  
  /**
   * Connect to a WebSocket endpoint
   * @param {string} url - WebSocket endpoint URL
   * @returns {Promise<WebSocket>} - Promise resolving to WebSocket instance
   */
  connect(url) {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return Promise.resolve(this.socket);
    }
    
    if (this.isConnecting) {
      return new Promise((resolve, reject) => {
        const checkInterval = setInterval(() => {
          if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            clearInterval(checkInterval);
            resolve(this.socket);
          } else if (!this.isConnecting) {
            clearInterval(checkInterval);
            reject(new Error('Connection failed'));
          }
        }, 100);
      });
    }
    
    this.isConnecting = true;
    
    return new Promise((resolve, reject) => {
      try {
        // Determine protocol based on current page protocol
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        let wsUrl = url.startsWith('ws') ? url : `${protocol}//${window.location.host}${url.startsWith('/') ? url : `/${url}`}`;
        
        // Add auth token if available
        if (this.authToken) {
          wsUrl += (wsUrl.includes('?') ? '&' : '?') + `token=${encodeURIComponent(this.authToken)}`;
        }
        
        // Store URL for reconnect
        this._currentUrl = url;
        
        this.socket = new WebSocket(wsUrl);
        
        // Set up event handlers
        this.socket.onopen = (event) => {
          console.log('WebSocket connection established');
          this.isConnecting = false;
          this.reconnectAttempt = 0;
          
          // Start heartbeat
          this._startHeartbeat();
          
          // Dispatch the open event to any listeners
          this._dispatchEvent('open', event);
          
          resolve(this.socket);
        };
        
        this.socket.onclose = (event) => {
          console.log(`WebSocket connection closed: ${event.code} - ${event.reason}`);
          this.isConnecting = false;
          
          // Clear heartbeat
          this._stopHeartbeat();
          
          // Dispatch the close event to any listeners
          this._dispatchEvent('close', event);
          
          // Attempt to reconnect if not closed cleanly
          if (!event.wasClean) {
            this._attemptReconnect(url);
          }
        };
        
        this.socket.onerror = (event) => {
          console.error('WebSocket error:', event);
          this.isConnecting = false;
          
          // Dispatch the error event to any listeners
          this._dispatchEvent('error', event);
          
          if (this.socket.readyState !== WebSocket.OPEN) {
            reject(new Error('WebSocket connection failed'));
          }
        };
        
        this.socket.onmessage = (event) => {
          this.lastMessageTime = Date.now();
          
          try {
            const data = JSON.parse(event.data);
            
            // Handle pong message for heartbeat
            if (data.type === 'pong') {
              this._handlePong();
              return;
            }
            
            // Handle acknowledgment
            if (data.event === 'acknowledge' && data.payload && data.payload.id) {
              this._handleAcknowledgment(data.payload.id);
              return;
            }
            
            // Handle batch messages
            if (data.type === 'batch' && data.messages) {
              const processingStartTime = performance.now();
              const batchCount = data.messages.length;
              let processedCount = 0;
              
              // Process each message in the batch
              for (const message of data.messages) {
                try {
                  // Check for acknowledgment requests
                  const processedData = this._processAcknowledgmentRequests(message.data);
                  
                  // Dispatch message event
                  this._dispatchEvent(message.event, processedData);
                  processedCount++;
                } catch (batchError) {
                  console.error('Error processing batch message:', batchError);
                }
              }
              
              // Log batch processing performance
              const processingTime = performance.now() - processingStartTime;
              console.debug(`Processed batch: ${processedCount}/${batchCount} messages in ${processingTime.toFixed(1)}ms`);
              
              // Send client stats periodically (every 10th batch)
              if (Math.random() < 0.1) {
                this.send({
                  event: 'client_stats',
                  payload: {
                    message_count: batchCount,
                    processing_time_ms: processingTime,
                    batch_size: batchCount,
                    compressed: data.compressed === true,
                    decompression_time_ms: data.decompression_time || 0
                  }
                });
              }
              
              return;
            }
            
            // Process individual message (check for acknowledgment requests)
            const processedData = data.payload ? 
              { ...data, payload: this._processAcknowledgmentRequests(data.payload) } : 
              this._processAcknowledgmentRequests(data);
            
            // Dispatch the message event to any listeners
            this._dispatchEvent('message', processedData);
            
            // Dispatch event-specific listeners
            if (processedData.event) {
              this._dispatchEvent(processedData.event, processedData.payload || processedData);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
            
            // Still dispatch the raw message
            this._dispatchEvent('message', event.data);
          }
        };
      } catch (error) {
        this.isConnecting = false;
        console.error('Error creating WebSocket:', error);
        reject(error);
      }
    });
  }
  
  /**
   * Send data over the WebSocket connection
   * @param {Object|string} data - Data to send
   * @returns {boolean} - Whether the send was successful
   */
  send(data) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('Cannot send message: WebSocket is not connected');
      return false;
    }
    
    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(message);
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }
  
  /**
   * Register an event listener
   * @param {string} event - Event name
   * @param {Function} callback - Event callback
   */
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    
    this.eventListeners.get(event).push(callback);
  }
  
  /**
   * Remove an event listener
   * @param {string} event - Event name
   * @param {Function} callback - Event callback to remove
   */
  off(event, callback) {
    if (!this.eventListeners.has(event)) {
      return;
    }
    
    const listeners = this.eventListeners.get(event);
    const index = listeners.indexOf(callback);
    
    if (index !== -1) {
      listeners.splice(index, 1);
    }
    
    if (listeners.length === 0) {
      this.eventListeners.delete(event);
    }
  }
  
  /**
   * Close the WebSocket connection
   * @param {number} code - Close code
   * @param {string} reason - Close reason
   */
  disconnect(code = 1000, reason = 'Normal closure') {
    if (!this.socket) {
      return;
    }
    
    // Cancel any reconnect attempts
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    // Clear heartbeat
    this._stopHeartbeat();
    
    // Close the connection
    if (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING) {
      this.socket.close(code, reason);
    }
    
    this.socket = null;
  }
  
  /**
   * Get the current connection state
   * @returns {string} - Connection state description
   */
  getState() {
    if (!this.socket) {
      return 'DISCONNECTED';
    }
    
    switch (this.socket.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'CONNECTED';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'DISCONNECTED';
      default:
        return 'UNKNOWN';
    }
  }
  
  /**
   * Dispatch an event to registered listeners
   * @param {string} event - Event name
   * @param {*} data - Event data
   * @private
   */
  _dispatchEvent(event, data) {
    if (!this.eventListeners.has(event)) {
      return;
    }
    
    for (const callback of this.eventListeners.get(event)) {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in ${event} event handler:`, error);
      }
    }
  }
  
  /**
   * Attempt to reconnect to the WebSocket
   * @param {string} url - WebSocket URL
   * @private
   */
  _attemptReconnect(url) {
    // Clear any existing reconnect timer
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    // Check if we've exceeded max reconnect attempts
    if (this.reconnectAttempt >= this.options.reconnectAttempts) {
      console.error(`Failed to reconnect after ${this.options.reconnectAttempts} attempts. Giving up.`);
      this._dispatchEvent('reconnect_failed', {
        attempts: this.reconnectAttempt
      });
      return;
    }
    
    // Increment reconnect attempt counter
    this.reconnectAttempt++;
    
    // Emit reconnecting event
    this._dispatchEvent('reconnecting', {
      attempt: this.reconnectAttempt,
      max: this.options.reconnectAttempts
    });
    
    // Set timeout for next attempt
    const delay = this.options.reconnectInterval * Math.pow(1.5, this.reconnectAttempt - 1);
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempt}/${this.options.reconnectAttempts})`);
    
    this.reconnectTimer = setTimeout(() => {
      this.connect(url).catch(() => {
        // Connection failed, try again
        this._attemptReconnect(url);
      });
    }, delay);
  }
  
  /**
   * Start the WebSocket heartbeat
   * @private
   */
  _startHeartbeat() {
    // Clear any existing heartbeat
    this._stopHeartbeat();
    
    // Start ping interval
    this.pingTimer = setInterval(() => {
      if (this.socket.readyState === WebSocket.OPEN) {
        // Send ping message
        this.send({ type: 'ping', timestamp: Date.now() });
        
        // Set pong timeout
        this.pongTimer = setTimeout(() => {
          console.warn('WebSocket ping timeout - no pong received');
          
          // Check if we've received any messages recently
          const now = Date.now();
          if (now - this.lastMessageTime > this.options.pingInterval * 2) {
            console.error('WebSocket connection appears dead - closing and reconnecting');
            this.socket.close(4000, 'Ping timeout');
          }
        }, this.options.pongTimeout);
      }
    }, this.options.pingInterval);
  }
  
  /**
   * Stop the WebSocket heartbeat
   * @private
   */
  _stopHeartbeat() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
    
    if (this.pongTimer) {
      clearTimeout(this.pongTimer);
      this.pongTimer = null;
    }
  }
  
  /**
   * Handle pong response from server
   * @private
   */
  _handlePong() {
    // Clear pong timeout
    if (this.pongTimer) {
      clearTimeout(this.pongTimer);
      this.pongTimer = null;
    }
  }
  
  /**
   * Request acknowledgment for a critical message
   * @param {string} eventName - Name of event to acknowledge
   * @param {Object} data - Event data
   * @returns {Promise<boolean>} - Promise resolving to acknowledgment status
   */
  requestAcknowledgment(eventName, data) {
    if (!this.options.enableAcknowledgments || !this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return Promise.resolve(false);
    }
    
    // Create unique acknowledgment ID
    const ackId = this.acknowledgmentId++;
    
    // Add acknowledgment metadata to message
    const messageWithAck = {
      ...data,
      _ack: {
        id: ackId,
        event: eventName
      }
    };
    
    // Create Promise for acknowledgment
    return new Promise((resolve) => {
      // Set timeout for acknowledgment
      const timeoutId = setTimeout(() => {
        // Remove from pending acknowledgments if timeout
        if (this.pendingAcknowledgments.has(ackId)) {
          this.pendingAcknowledgments.delete(ackId);
          console.warn(`Acknowledgment timeout for ${eventName} (ID: ${ackId})`);
          resolve(false);
        }
      }, this.options.acknowledgmentTimeout);
      
      // Store acknowledgment callback
      this.pendingAcknowledgments.set(ackId, {
        timeoutId,
        callback: () => {
          clearTimeout(timeoutId);
          this.pendingAcknowledgments.delete(ackId);
          resolve(true);
        }
      });
      
      // Send message with acknowledgment request
      this.send({
        event: eventName,
        payload: messageWithAck
      });
    });
  }
  
  /**
   * Acknowledge receipt of a message
   * @param {number} ackId - Acknowledgment ID
   */
  sendAcknowledgment(ackId) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return;
    }
    
    this.send({
      event: 'acknowledge',
      payload: {
        id: ackId
      }
    });
  }
  
  /**
   * Handle incoming acknowledgment
   * @param {number} ackId - Acknowledgment ID
   * @private
   */
  _handleAcknowledgment(ackId) {
    if (this.pendingAcknowledgments.has(ackId)) {
      const { callback } = this.pendingAcknowledgments.get(ackId);
      callback();
    }
  }
  
  /**
   * Process an incoming message to check for acknowledgment requests
   * @param {Object} data - Message data
   * @private
   */
  _processAcknowledgmentRequests(data) {
    // Check if message contains acknowledgment request
    if (data && data._ack && data._ack.id) {
      // Send acknowledgment back to server
      this.sendAcknowledgment(data._ack.id);
      
      // Remove acknowledgment metadata before dispatching to listeners
      const cleanData = { ...data };
      delete cleanData._ack;
      return cleanData;
    }
    
    return data;
  }
}

// Create a singleton instance
const websocketService = new WebSocketService();

export { websocketService };