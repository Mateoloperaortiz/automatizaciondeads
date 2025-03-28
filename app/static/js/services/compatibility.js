/**
 * Browser Compatibility Service
 * Tests browser support for required features and provides fallbacks where possible
 */

// Features that are required for the application to function
const REQUIRED_FEATURES = [
  { name: 'ES6 Modules', test: () => typeof import === 'function' },
  { name: 'Fetch API', test: () => typeof fetch === 'function' },
  { name: 'Promises', test: () => typeof Promise === 'function' },
  { name: 'Map', test: () => typeof Map === 'function' },
  { name: 'Set', test: () => typeof Set === 'function' },
];

// Features that enhance the application but aren't strictly required
const ENHANCEMENT_FEATURES = [
  { name: 'WebSockets', test: () => typeof WebSocket === 'function' },
  { name: 'Web Notifications', test: () => 'Notification' in window },
  { name: 'localStorage', test: () => {
    try {
      localStorage.setItem('test', 'test');
      localStorage.removeItem('test');
      return true;
    } catch (e) {
      return false;
    }
  }},
  { name: 'sessionStorage', test: () => {
    try {
      sessionStorage.setItem('test', 'test');
      sessionStorage.removeItem('test');
      return true;
    } catch (e) {
      return false;
    }
  }},
  { name: 'Intersection Observer', test: () => typeof IntersectionObserver === 'function' },
];

// CSS features that may need polyfills or alternative styling
const CSS_FEATURES = [
  { name: 'CSS Variables', test: () => {
    try {
      const root = document.querySelector(':root');
      const style = getComputedStyle(root);
      return style.getPropertyValue('--test') !== undefined;
    } catch (e) {
      return false;
    }
  }},
  { name: 'CSS Grid', test: () => {
    try {
      return CSS.supports('display', 'grid');
    } catch (e) {
      return false;
    }
  }},
  { name: 'CSS Flexbox', test: () => {
    try {
      return CSS.supports('display', 'flex');
    } catch (e) {
      return false;
    }
  }},
];

/**
 * Compatibility service to check browser support
 */
class Compatibility {
  constructor() {
    this.tests = {
      required: REQUIRED_FEATURES,
      enhancement: ENHANCEMENT_FEATURES,
      css: CSS_FEATURES
    };
    
    this.results = null;
    this.hasTestedCompatibility = false;
  }
  
  /**
   * Run compatibility tests
   * @returns {Object} - Test results
   */
  testCompatibility() {
    if (this.hasTestedCompatibility) {
      return this.results;
    }
    
    const results = {
      required: {},
      enhancement: {},
      css: {},
      isBrowserCompatible: true,
      missingRequiredFeatures: [],
      missingEnhancementFeatures: [],
      missingCssFeatures: []
    };
    
    // Test required features
    this.tests.required.forEach(feature => {
      const isSupported = feature.test();
      results.required[feature.name] = isSupported;
      
      if (!isSupported) {
        results.isBrowserCompatible = false;
        results.missingRequiredFeatures.push(feature.name);
      }
    });
    
    // Test enhancement features
    this.tests.enhancement.forEach(feature => {
      const isSupported = feature.test();
      results.enhancement[feature.name] = isSupported;
      
      if (!isSupported) {
        results.missingEnhancementFeatures.push(feature.name);
      }
    });
    
    // Test CSS features
    this.tests.css.forEach(feature => {
      const isSupported = feature.test();
      results.css[feature.name] = isSupported;
      
      if (!isSupported) {
        results.missingCssFeatures.push(feature.name);
      }
    });
    
    this.results = results;
    this.hasTestedCompatibility = true;
    
    return results;
  }
  
  /**
   * Check if the browser is compatible with required features
   * @returns {boolean} - Whether the browser is compatible
   */
  isBrowserCompatible() {
    if (!this.hasTestedCompatibility) {
      this.testCompatibility();
    }
    
    return this.results.isBrowserCompatible;
  }
  
  /**
   * Get the compatibility report
   * @returns {Object} - Detailed compatibility report
   */
  getCompatibilityReport() {
    if (!this.hasTestedCompatibility) {
      this.testCompatibility();
    }
    
    return {
      ...this.results,
      browserInfo: this.getBrowserInfo()
    };
  }
  
  /**
   * Get browser information
   * @returns {Object} - Browser name, version, and user agent
   */
  getBrowserInfo() {
    const ua = navigator.userAgent;
    let browserName = 'Unknown';
    let browserVersion = 'Unknown';
    
    // Detect common browsers
    if (ua.indexOf('Firefox') > -1) {
      browserName = 'Firefox';
      browserVersion = ua.match(/Firefox\/([0-9.]+)/)[1];
    } else if (ua.indexOf('Chrome') > -1 && ua.indexOf('Edg') === -1 && ua.indexOf('OPR') === -1) {
      browserName = 'Chrome';
      browserVersion = ua.match(/Chrome\/([0-9.]+)/)[1];
    } else if (ua.indexOf('Safari') > -1 && ua.indexOf('Chrome') === -1) {
      browserName = 'Safari';
      browserVersion = ua.match(/Version\/([0-9.]+)/)[1];
    } else if (ua.indexOf('Edg') > -1) {
      browserName = 'Edge';
      browserVersion = ua.match(/Edg\/([0-9.]+)/)[1];
    } else if (ua.indexOf('OPR') > -1 || ua.indexOf('Opera') > -1) {
      browserName = 'Opera';
      browserVersion = ua.match(/(?:OPR|Opera)\/([0-9.]+)/)[1];
    } else if (ua.indexOf('Trident') > -1) {
      browserName = 'Internet Explorer';
      browserVersion = ua.match(/rv:([0-9.]+)/)[1];
    }
    
    return {
      name: browserName,
      version: browserVersion,
      userAgent: ua,
      isMobile: /Mobi|Android/i.test(ua),
      isTablet: /Tablet|iPad/i.test(ua)
    };
  }
  
  /**
   * Show compatibility warning if browser is not compatible
   * @param {HTMLElement} container - Container element to show warning in
   */
  showCompatibilityWarning(container) {
    if (!this.hasTestedCompatibility) {
      this.testCompatibility();
    }
    
    if (!this.results.isBrowserCompatible) {
      const warning = document.createElement('div');
      warning.className = 'compatibility-warning';
      warning.innerHTML = `
        <div class="compatibility-warning-header">
          <i class="fas fa-exclamation-triangle"></i>
          <h3>Browser Compatibility Issue</h3>
          <button class="compatibility-warning-close">&times;</button>
        </div>
        <div class="compatibility-warning-content">
          <p>Your browser is missing some required features:</p>
          <ul>
            ${this.results.missingRequiredFeatures.map(feature => `<li>${feature}</li>`).join('')}
          </ul>
          <p>Please use a modern browser like Chrome, Firefox, Edge, or Safari.</p>
        </div>
      `;
      
      // Add styling
      const style = document.createElement('style');
      style.textContent = `
        .compatibility-warning {
          position: fixed;
          top: 20px;
          right: 20px;
          width: 350px;
          background-color: #fff3cd;
          border: 1px solid #ffeeba;
          border-radius: 5px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
          z-index: 9999;
          animation: slide-in 0.3s ease;
        }
        
        .compatibility-warning-header {
          display: flex;
          align-items: center;
          padding: 10px 15px;
          background-color: #ffecb5;
          border-bottom: 1px solid #ffeeba;
          border-top-left-radius: 5px;
          border-top-right-radius: 5px;
        }
        
        .compatibility-warning-header i {
          color: #856404;
          margin-right: 10px;
          font-size: 1.2em;
        }
        
        .compatibility-warning-header h3 {
          margin: 0;
          flex: 1;
          font-size: 1rem;
          color: #856404;
        }
        
        .compatibility-warning-close {
          background: none;
          border: none;
          font-size: 1.2em;
          cursor: pointer;
          color: #856404;
        }
        
        .compatibility-warning-content {
          padding: 15px;
          color: #856404;
        }
        
        .compatibility-warning-content ul {
          margin-top: 5px;
          margin-bottom: 10px;
          padding-left: 20px;
        }
        
        @keyframes slide-in {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `;
      
      document.head.appendChild(style);
      
      // Add to container or body
      if (container) {
        container.appendChild(warning);
      } else {
        document.body.appendChild(warning);
      }
      
      // Add close button functionality
      const closeButton = warning.querySelector('.compatibility-warning-close');
      closeButton.addEventListener('click', () => {
        warning.style.display = 'none';
      });
    }
  }
  
  /**
   * Load polyfills for unsupported features
   * @returns {Promise} - Promise that resolves when polyfills are loaded
   */
  async loadPolyfills() {
    if (!this.hasTestedCompatibility) {
      this.testCompatibility();
    }
    
    const polyfillsToLoad = [];
    
    // Check for fetch polyfill need
    if (!this.results.required['Fetch API']) {
      polyfillsToLoad.push('https://cdn.jsdelivr.net/npm/whatwg-fetch@3.6.2/dist/fetch.umd.min.js');
    }
    
    // Check for Promise polyfill need
    if (!this.results.required['Promises']) {
      polyfillsToLoad.push('https://cdn.jsdelivr.net/npm/promise-polyfill@8.2.3/dist/polyfill.min.js');
    }
    
    // Load polyfills if needed
    if (polyfillsToLoad.length > 0) {
      for (const polyfillUrl of polyfillsToLoad) {
        await new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = polyfillUrl;
          script.onload = resolve;
          script.onerror = reject;
          document.head.appendChild(script);
        });
      }
      
      // Re-test compatibility after loading polyfills
      this.hasTestedCompatibility = false;
      this.testCompatibility();
    }
    
    return this.results;
  }
}

// Create singleton instance
const compatibility = new Compatibility();

export { compatibility };