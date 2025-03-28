/**
 * Performance Monitoring and Optimization Service
 * Monitors application performance metrics and implements optimization techniques
 */

/**
 * Performance monitoring targets
 */
const PERFORMANCE_TARGETS = {
  // Time in milliseconds
  FCP: 1800, // First Contentful Paint
  LCP: 2500, // Largest Contentful Paint
  TTI: 3500, // Time to Interactive
  API_RESPONSE: 500, // API response time
  IDLE_CALLBACK_TIMEOUT: 50, // requestIdleCallback timeout
  // Frames per second
  MIN_FPS: 45, // Minimum acceptable FPS
  TARGET_FPS: 60, // Target FPS
};

/**
 * Performance service for monitoring and optimizing application performance
 */
class Performance {
  constructor() {
    this.metrics = {
      apiCalls: new Map(), // API performance metrics
      resourceLoads: [], // Resource load times
      interactionTimings: [], // User interaction timing
      renderTimings: [], // Render timing
      fpsHistory: [], // FPS history
    };
    
    this.isMonitoring = false;
    this.listeners = new Map();
    this.listenerIdCounter = 0;
    this.fpsInterval = null;
    
    // Debounced functions
    this.debouncers = new Map();
    
    // Web Vitals performance data (if available)
    this.webVitals = {
      lcp: null, // Largest Contentful Paint
      fid: null, // First Input Delay
      cls: null, // Cumulative Layout Shift
      fcp: null, // First Contentful Paint
      ttfb: null, // Time to First Byte
    };
  }
  
  /**
   * Start performance monitoring
   * @param {Object} options - Monitoring options
   */
  startMonitoring(options = {}) {
    if (this.isMonitoring) return;
    
    this.options = {
      monitorApiCalls: true,
      monitorResources: true,
      monitorInteractions: true,
      trackFps: true,
      collectWebVitals: true,
      ...options
    };
    
    // Initialize monitoring
    this._initMonitoring();
    
    this.isMonitoring = true;
    console.log('Performance monitoring started');
  }
  
  /**
   * Stop performance monitoring
   */
  stopMonitoring() {
    if (!this.isMonitoring) return;
    
    // Clear intervals
    if (this.fpsInterval) {
      cancelAnimationFrame(this.fpsInterval);
      this.fpsInterval = null;
    }
    
    // Remove observers
    if (this._resourceObserver) {
      this._resourceObserver.disconnect();
      this._resourceObserver = null;
    }
    
    this.isMonitoring = false;
    console.log('Performance monitoring stopped');
  }
  
  /**
   * Record API call performance
   * @param {string} endpoint - API endpoint
   * @param {number} startTime - Call start time
   * @param {number} endTime - Call end time
   * @param {boolean} success - Whether the call was successful
   */
  recordApiCall(endpoint, startTime, endTime, success = true) {
    if (!this.isMonitoring || !this.options.monitorApiCalls) return;
    
    const duration = endTime - startTime;
    
    // Get or create entry for this endpoint
    if (!this.metrics.apiCalls.has(endpoint)) {
      this.metrics.apiCalls.set(endpoint, {
        totalCalls: 0,
        totalTime: 0,
        successCalls: 0,
        failedCalls: 0,
        minTime: Infinity,
        maxTime: 0,
        timestamps: []
      });
    }
    
    const endpointStats = this.metrics.apiCalls.get(endpoint);
    
    // Update stats
    endpointStats.totalCalls++;
    endpointStats.totalTime += duration;
    
    if (success) {
      endpointStats.successCalls++;
    } else {
      endpointStats.failedCalls++;
    }
    
    endpointStats.minTime = Math.min(endpointStats.minTime, duration);
    endpointStats.maxTime = Math.max(endpointStats.maxTime, duration);
    
    // Add timestamp (keeping only the most recent 100)
    endpointStats.timestamps.push({
      time: Date.now(),
      duration,
      success,
    });
    
    if (endpointStats.timestamps.length > 100) {
      endpointStats.timestamps.shift();
    }
    
    // Emit event for slow API calls
    if (duration > PERFORMANCE_TARGETS.API_RESPONSE) {
      this._emitEvent('slowApiCall', {
        endpoint,
        duration,
        threshold: PERFORMANCE_TARGETS.API_RESPONSE,
      });
    }
  }
  
  /**
   * Instrument API call with performance monitoring
   * @param {Function} apiCallFn - API call function to instrument
   * @param {string} endpoint - API endpoint name
   * @returns {Function} - Instrumented function
   */
  instrumentApiCall(apiCallFn, endpoint) {
    return async (...args) => {
      const startTime = performance.now();
      let success = true;
      
      try {
        const result = await apiCallFn(...args);
        return result;
      } catch (error) {
        success = false;
        throw error;
      } finally {
        const endTime = performance.now();
        this.recordApiCall(endpoint, startTime, endTime, success);
      }
    };
  }
  
  /**
   * Create a debounced function
   * @param {Function} fn - Function to debounce
   * @param {number} delay - Debounce delay in ms
   * @param {string} key - Optional key to identify this debounce
   * @returns {Function} - Debounced function
   */
  debounce(fn, delay, key = null) {
    const id = key || `debounce_${Date.now()}_${Math.random()}`;
    
    return (...args) => {
      // Clear existing timeout
      if (this.debouncers.has(id)) {
        clearTimeout(this.debouncers.get(id));
      }
      
      // Set new timeout
      const timeoutId = setTimeout(() => {
        fn(...args);
        this.debouncers.delete(id);
      }, delay);
      
      this.debouncers.set(id, timeoutId);
    };
  }
  
  /**
   * Create a throttled function
   * @param {Function} fn - Function to throttle
   * @param {number} limit - Throttle limit in ms
   * @returns {Function} - Throttled function
   */
  throttle(fn, limit) {
    let lastCall = 0;
    let timeoutId = null;
    
    return function throttled(...args) {
      const now = Date.now();
      const context = this;
      
      if (now - lastCall < limit) {
        // If we're within the limit, clear any existing timeout
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        
        // Schedule the function to run when the limit has passed
        timeoutId = setTimeout(() => {
          lastCall = Date.now();
          timeoutId = null;
          fn.apply(context, args);
        }, limit - (now - lastCall));
      } else {
        // If we've passed the limit, execute immediately
        lastCall = now;
        timeoutId = null;
        fn.apply(context, args);
      }
    };
  }
  
  /**
   * Execute function when browser is idle
   * @param {Function} fn - Function to execute
   * @param {Object} options - Options for requestIdleCallback
   */
  runWhenIdle(fn, options = {}) {
    const defaultOptions = {
      timeout: PERFORMANCE_TARGETS.IDLE_CALLBACK_TIMEOUT
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    if ('requestIdleCallback' in window) {
      requestIdleCallback(fn, finalOptions);
    } else {
      // Fallback to setTimeout
      setTimeout(fn, 1);
    }
  }
  
  /**
   * Run a function in chunks to avoid blocking the main thread
   * @param {Array} items - Items to process
   * @param {Function} processFn - Function to process each item
   * @param {number} chunkSize - Size of chunks to process
   * @param {number} delay - Delay between chunks in ms
   * @returns {Promise} - Promise that resolves when all items are processed
   */
  async processInChunks(items, processFn, chunkSize = 5, delay = 10) {
    const chunks = [];
    
    // Split items into chunks
    for (let i = 0; i < items.length; i += chunkSize) {
      chunks.push(items.slice(i, i + chunkSize));
    }
    
    // Process chunks with delay between them
    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i];
      
      // Process current chunk
      for (const item of chunk) {
        processFn(item);
      }
      
      // Wait before processing next chunk
      if (i < chunks.length - 1) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  /**
   * Get performance metrics for all endpoints
   * @returns {Object} - Performance metrics
   */
  getApiPerformanceReport() {
    const report = {
      endpoints: {},
      summary: {
        totalEndpoints: this.metrics.apiCalls.size,
        totalCalls: 0,
        totalSuccess: 0,
        totalFailures: 0,
        averageResponseTime: 0,
        slowEndpoints: []
      }
    };
    
    // Calculate total calls
    let totalTime = 0;
    
    // Process each endpoint
    for (const [endpoint, stats] of this.metrics.apiCalls.entries()) {
      const averageTime = stats.totalCalls > 0 ? stats.totalTime / stats.totalCalls : 0;
      
      report.endpoints[endpoint] = {
        totalCalls: stats.totalCalls,
        successRate: stats.totalCalls > 0 ? (stats.successCalls / stats.totalCalls) * 100 : 0,
        averageTime,
        minTime: stats.minTime === Infinity ? 0 : stats.minTime,
        maxTime: stats.maxTime,
      };
      
      // Add to summary
      report.summary.totalCalls += stats.totalCalls;
      report.summary.totalSuccess += stats.successCalls;
      report.summary.totalFailures += stats.failedCalls;
      totalTime += stats.totalTime;
      
      // Track slow endpoints
      if (averageTime > PERFORMANCE_TARGETS.API_RESPONSE) {
        report.summary.slowEndpoints.push({
          endpoint,
          averageTime,
          threshold: PERFORMANCE_TARGETS.API_RESPONSE,
        });
      }
    }
    
    // Calculate overall average response time
    if (report.summary.totalCalls > 0) {
      report.summary.averageResponseTime = totalTime / report.summary.totalCalls;
    }
    
    return report;
  }
  
  /**
   * Get current FPS (frames per second)
   * @returns {number} - Current FPS
   */
  getCurrentFps() {
    if (this.metrics.fpsHistory.length === 0) {
      return 0;
    }
    
    return this.metrics.fpsHistory[this.metrics.fpsHistory.length - 1];
  }
  
  /**
   * Get average FPS over the last n frames
   * @param {number} frames - Number of frames to average
   * @returns {number} - Average FPS
   */
  getAverageFps(frames = 10) {
    if (this.metrics.fpsHistory.length === 0) {
      return 0;
    }
    
    const recentFrames = this.metrics.fpsHistory.slice(-frames);
    const sum = recentFrames.reduce((acc, fps) => acc + fps, 0);
    
    return sum / recentFrames.length;
  }
  
  /**
   * Get Web Vitals metrics
   * @returns {Object} - Web Vitals metrics
   */
  getWebVitals() {
    return { ...this.webVitals };
  }
  
  /**
   * Add listener for performance events
   * @param {string} event - Event name
   * @param {Function} callback - Event callback
   * @returns {number} - Listener ID for removal
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Map());
    }
    
    const id = ++this.listenerIdCounter;
    this.listeners.get(event).set(id, callback);
    
    return id;
  }
  
  /**
   * Remove listener for performance events
   * @param {string} event - Event name
   * @param {number} id - Listener ID
   * @returns {boolean} - Whether listener was removed
   */
  off(event, id) {
    if (!this.listeners.has(event)) {
      return false;
    }
    
    return this.listeners.get(event).delete(id);
  }
  
  /**
   * Initialize performance monitoring
   * @private
   */
  _initMonitoring() {
    // Start FPS monitoring
    if (this.options.trackFps) {
      this._startFpsTracking();
    }
    
    // Start resource monitoring
    if (this.options.monitorResources) {
      this._startResourceMonitoring();
    }
    
    // Track Web Vitals if available and enabled
    if (this.options.collectWebVitals) {
      this._collectWebVitals();
    }
    
    // Track interactions if enabled
    if (this.options.monitorInteractions) {
      this._trackInteractions();
    }
  }
  
  /**
   * Start FPS tracking
   * @private
   */
  _startFpsTracking() {
    let lastFrameTime = performance.now();
    let frameCount = 0;
    let lastFpsUpdateTime = lastFrameTime;
    
    const trackFrame = (timestamp) => {
      // Calculate time since last frame
      const delta = timestamp - lastFrameTime;
      lastFrameTime = timestamp;
      
      // Increment frame counter
      frameCount++;
      
      // Update FPS every second
      if (timestamp - lastFpsUpdateTime >= 1000) {
        const fps = Math.round(frameCount * 1000 / (timestamp - lastFpsUpdateTime));
        
        // Add to history, keeping max 60 entries
        this.metrics.fpsHistory.push(fps);
        if (this.metrics.fpsHistory.length > 60) {
          this.metrics.fpsHistory.shift();
        }
        
        // Check if FPS is below target
        if (fps < PERFORMANCE_TARGETS.MIN_FPS) {
          this._emitEvent('lowFps', {
            fps,
            threshold: PERFORMANCE_TARGETS.MIN_FPS,
            target: PERFORMANCE_TARGETS.TARGET_FPS,
          });
        }
        
        // Reset counters
        frameCount = 0;
        lastFpsUpdateTime = timestamp;
      }
      
      // Continue tracking
      this.fpsInterval = requestAnimationFrame(trackFrame);
    };
    
    this.fpsInterval = requestAnimationFrame(trackFrame);
  }
  
  /**
   * Start resource load monitoring
   * @private
   */
  _startResourceMonitoring() {
    // Use Performance Observer if available
    if ('PerformanceObserver' in window) {
      this._resourceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'resource') {
            this.metrics.resourceLoads.push({
              name: entry.name,
              startTime: entry.startTime,
              duration: entry.duration,
              size: entry.transferSize || 0,
              type: this._getResourceType(entry.name),
              timestamp: Date.now(),
            });
            
            // Keep only the most recent 100 resource loads
            if (this.metrics.resourceLoads.length > 100) {
              this.metrics.resourceLoads.shift();
            }
            
            // Check for slow-loading resources
            if (entry.duration > 1000) { // Over 1 second
              this._emitEvent('slowResource', {
                resource: entry.name,
                duration: entry.duration,
                type: this._getResourceType(entry.name),
              });
            }
          }
        }
      });
      
      this._resourceObserver.observe({ entryTypes: ['resource'] });
    }
  }
  
  /**
   * Collect Web Vitals metrics
   * @private
   */
  _collectWebVitals() {
    // Only run if the Web Vitals library is available
    if (typeof webVitals === 'undefined') {
      console.warn('Web Vitals library not available');
      return;
    }
    
    const handleVitals = (metric) => {
      this.webVitals[metric.name.toLowerCase()] = metric.value;
      
      // Emit event for each collected vital
      this._emitEvent('webVital', {
        name: metric.name,
        value: metric.value,
        id: metric.id,
      });
    };
    
    // Collect each vital
    webVitals.getLCP(handleVitals);
    webVitals.getFID(handleVitals);
    webVitals.getCLS(handleVitals);
    webVitals.getFCP(handleVitals);
    webVitals.getTTFB(handleVitals);
  }
  
  /**
   * Track user interactions
   * @private
   */
  _trackInteractions() {
    // Track clicks
    document.addEventListener('click', (event) => {
      const target = event.target.tagName.toLowerCase();
      const isButton = target === 'button' || 
                       (target === 'a' && event.target.role === 'button');
      
      this.metrics.interactionTimings.push({
        type: 'click',
        target,
        isButton,
        timestamp: Date.now(),
      });
      
      // Keep only the most recent 100 interactions
      if (this.metrics.interactionTimings.length > 100) {
        this.metrics.interactionTimings.shift();
      }
    });
    
    // Track key presses in inputs
    document.addEventListener('keydown', (event) => {
      if (event.target.tagName.toLowerCase() === 'input' || 
          event.target.tagName.toLowerCase() === 'textarea') {
        
        this.metrics.interactionTimings.push({
          type: 'keydown',
          target: event.target.tagName.toLowerCase(),
          inputType: event.target.type || 'text',
          timestamp: Date.now(),
        });
        
        // Keep only the most recent 100 interactions
        if (this.metrics.interactionTimings.length > 100) {
          this.metrics.interactionTimings.shift();
        }
      }
    });
  }
  
  /**
   * Get resource type from URL
   * @param {string} url - Resource URL
   * @returns {string} - Resource type
   * @private
   */
  _getResourceType(url) {
    const extension = url.split('.').pop().toLowerCase().split('?')[0];
    
    // Categorize by file extension
    if (['js'].includes(extension)) return 'script';
    if (['css'].includes(extension)) return 'style';
    if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(extension)) return 'image';
    if (['woff', 'woff2', 'ttf', 'otf', 'eot'].includes(extension)) return 'font';
    if (['mp4', 'webm', 'ogg'].includes(extension)) return 'video';
    if (['mp3', 'wav'].includes(extension)) return 'audio';
    if (['json'].includes(extension)) return 'data';
    
    // Check URL patterns
    if (url.includes('/api/')) return 'api';
    if (url.includes('/fonts/')) return 'font';
    if (url.includes('/images/')) return 'image';
    
    return 'other';
  }
  
  /**
   * Emit event to listeners
   * @param {string} event - Event name
   * @param {Object} data - Event data
   * @private
   */
  _emitEvent(event, data) {
    if (!this.listeners.has(event)) {
      return;
    }
    
    for (const callback of this.listeners.get(event).values()) {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in performance event listener for ${event}:`, error);
      }
    }
  }
}

// Create singleton instance
const performance = new Performance();

export { performance, PERFORMANCE_TARGETS };