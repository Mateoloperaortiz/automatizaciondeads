/**
 * Toast Notification Service
 * Provides a standardized interface for showing toast notifications
 */

// Default options for toast notifications
const DEFAULT_OPTIONS = {
  position: 'bottom-right',
  duration: 5000,
  maxToasts: 5,
  pauseOnHover: true,
  closeButton: true,
  icons: true,
  animation: true,
  styling: 'modern'
};

/**
 * ToastService Class - Manages toast notifications
 */
export class ToastService {
  /**
   * Create a new ToastService
   * @param {Object} options - Toast configuration options
   */
  constructor(options = {}) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
    this.toastContainer = null;
    this.toasts = [];
    this.toastIdCounter = 1;
    
    // Initialize toast container
    this._initializeContainer();
  }
  
  /**
   * Initialize the toast container
   * @private
   */
  _initializeContainer() {
    // If container already exists, return
    if (this.toastContainer) return;
    
    // Create container element
    this.toastContainer = document.createElement('div');
    this.toastContainer.className = `toast-container position-${this.options.position}`;
    
    // Add position class
    this._applyPositionClass();
    
    // Apply styling
    this._applyContainerStyle();
    
    // Add to document
    document.body.appendChild(this.toastContainer);
  }
  
  /**
   * Apply positioning class to container
   * @private
   */
  _applyPositionClass() {
    // Clear existing position classes
    const positionClasses = ['top-left', 'top-center', 'top-right', 'bottom-left', 'bottom-center', 'bottom-right'];
    positionClasses.forEach(pos => {
      this.toastContainer.classList.remove(pos);
    });
    
    // Add new position class
    this.toastContainer.classList.add(this.options.position);
  }
  
  /**
   * Apply styling to container
   * @private
   */
  _applyContainerStyle() {
    this.toastContainer.style.position = 'fixed';
    this.toastContainer.style.zIndex = '9999';
    this.toastContainer.style.pointerEvents = 'none'; // Don't block clicks on page
    
    // Position-specific styles
    if (this.options.position.includes('top')) {
      this.toastContainer.style.top = '1rem';
    } else {
      this.toastContainer.style.bottom = '1rem';
    }
    
    if (this.options.position.includes('left')) {
      this.toastContainer.style.left = '1rem';
    } else if (this.options.position.includes('right')) {
      this.toastContainer.style.right = '1rem';
    } else {
      // Center
      this.toastContainer.style.left = '50%';
      this.toastContainer.style.transform = 'translateX(-50%)';
    }
    
    // Container layout
    this.toastContainer.style.display = 'flex';
    this.toastContainer.style.flexDirection = 'column';
    this.toastContainer.style.gap = '0.5rem';
    this.toastContainer.style.maxWidth = '100%';
    
    // If using bottom position, reverse order
    if (this.options.position.includes('bottom')) {
      this.toastContainer.style.flexDirection = 'column-reverse';
    }
  }
  
  /**
   * Show a toast notification
   * @param {string} message - The message to display
   * @param {string} type - Type of toast (success, error, warning, info)
   * @param {Object} options - Override default options
   * @returns {number} - Toast ID for later reference
   */
  show(message, type = 'info', options = {}) {
    // Merge options
    const toastOptions = { ...this.options, ...options };
    
    // Ensure container exists
    this._initializeContainer();
    
    // Create toast element
    const toast = this._createToastElement(message, type, toastOptions);
    const toastId = this.toastIdCounter++;
    toast.dataset.id = toastId;
    
    // Add to container
    this.toastContainer.appendChild(toast);
    
    // Add to tracking array
    this.toasts.push({
      id: toastId,
      element: toast,
      timeout: null
    });
    
    // Enforce maximum number of toasts
    this._enforceMaxToasts();
    
    // Show animation
    setTimeout(() => {
      toast.classList.add('show');
    }, 10);
    
    // Set auto-dismiss timeout
    if (toastOptions.duration) {
      const timeout = setTimeout(() => {
        this.dismiss(toastId);
      }, toastOptions.duration);
      
      // Store timeout reference
      const toastInfo = this.toasts.find(t => t.id === toastId);
      if (toastInfo) {
        toastInfo.timeout = timeout;
      }
      
      // Pause timer on hover if enabled
      if (toastOptions.pauseOnHover) {
        toast.addEventListener('mouseenter', () => {
          clearTimeout(timeout);
        });
        
        toast.addEventListener('mouseleave', () => {
          const toastInfo = this.toasts.find(t => t.id === toastId);
          if (toastInfo) {
            toastInfo.timeout = setTimeout(() => {
              this.dismiss(toastId);
            }, toastOptions.duration);
          }
        });
      }
    }
    
    return toastId;
  }
  
  /**
   * Show a success toast
   * @param {string} message - The message to display
   * @param {Object} options - Override default options
   * @returns {number} - Toast ID
   */
  success(message, options = {}) {
    return this.show(message, 'success', options);
  }
  
  /**
   * Show an error toast
   * @param {string} message - The message to display
   * @param {Object} options - Override default options
   * @returns {number} - Toast ID
   */
  error(message, options = {}) {
    return this.show(message, 'error', options);
  }
  
  /**
   * Show a warning toast
   * @param {string} message - The message to display
   * @param {Object} options - Override default options
   * @returns {number} - Toast ID
   */
  warning(message, options = {}) {
    return this.show(message, 'warning', options);
  }
  
  /**
   * Show an info toast
   * @param {string} message - The message to display
   * @param {Object} options - Override default options
   * @returns {number} - Toast ID
   */
  info(message, options = {}) {
    return this.show(message, 'info', options);
  }
  
  /**
   * Dismiss a toast
   * @param {number} id - Toast ID to dismiss
   */
  dismiss(id) {
    const toastInfo = this.toasts.find(t => t.id === id);
    if (!toastInfo) return;
    
    // Clear timeout if exists
    if (toastInfo.timeout) {
      clearTimeout(toastInfo.timeout);
    }
    
    // Remove show class to trigger exit animation
    toastInfo.element.classList.remove('show');
    
    // Remove from DOM after animation
    setTimeout(() => {
      if (toastInfo.element.parentNode === this.toastContainer) {
        this.toastContainer.removeChild(toastInfo.element);
      }
      
      // Remove from tracking array
      this.toasts = this.toasts.filter(t => t.id !== id);
    }, 300);
  }
  
  /**
   * Dismiss all active toasts
   */
  dismissAll() {
    // Copy array to avoid modification during iteration
    const toastsCopy = [...this.toasts];
    
    // Dismiss each toast
    toastsCopy.forEach(toast => {
      this.dismiss(toast.id);
    });
  }
  
  /**
   * Create a toast element
   * @param {string} message - Toast message
   * @param {string} type - Toast type
   * @param {Object} options - Toast options
   * @returns {HTMLElement} - Toast element
   * @private
   */
  _createToastElement(message, type, options) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.style.pointerEvents = 'auto'; // Allow interaction
    
    // Add type class
    toast.classList.add(`toast-${type}`);
    
    // Add animation class if enabled
    if (options.animation) {
      toast.classList.add('animate');
    }
    
    // Add styling
    this._applyToastStyle(toast, type);
    
    // Set icon based on type
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    // Create content
    toast.innerHTML = `
      ${options.icons ? `
        <div class="toast-icon">
          <i class="fas fa-${icon}"></i>
        </div>
      ` : ''}
      <div class="toast-content">
        <p>${message}</p>
      </div>
      ${options.closeButton ? `
        <button class="toast-close" aria-label="Close">
          <i class="fas fa-times"></i>
        </button>
      ` : ''}
    `;
    
    // Add close button event listener
    if (options.closeButton) {
      const closeButton = toast.querySelector('.toast-close');
      closeButton.addEventListener('click', () => {
        const id = parseInt(toast.dataset.id);
        if (id) {
          this.dismiss(id);
        }
      });
    }
    
    return toast;
  }
  
  /**
   * Apply styling to a toast element
   * @param {HTMLElement} toast - Toast element
   * @param {string} type - Toast type
   * @private
   */
  _applyToastStyle(toast, type) {
    // Base styles
    Object.assign(toast.style, {
      display: 'flex',
      alignItems: 'center',
      maxWidth: '350px',
      borderRadius: '4px',
      padding: '0.75rem 1rem',
      marginBottom: '0.5rem',
      boxShadow: '0 2px 10px rgba(0,0,0,0.15)',
      opacity: '0',
      transform: 'translateY(20px)',
      transition: 'all 0.3s ease'
    });
    
    // Type-specific styles
    let borderColor, backgroundColor, textColor;
    
    switch (type) {
      case 'success':
        borderColor = '#10b981';
        backgroundColor = '#f0fdf5';
        textColor = '#065f46';
        break;
      case 'error':
        borderColor = '#ef4444';
        backgroundColor = '#fef2f2';
        textColor = '#991b1b';
        break;
      case 'warning':
        borderColor = '#f59e0b';
        backgroundColor = '#fffbeb';
        textColor = '#92400e';
        break;
      case 'info':
      default:
        borderColor = '#0ea5e9';
        backgroundColor = '#f0f9ff';
        textColor = '#075985';
        break;
    }
    
    // Apply type-specific styles
    toast.style.borderLeft = `4px solid ${borderColor}`;
    toast.style.backgroundColor = backgroundColor;
    toast.style.color = textColor;
    
    // Add show class styles
    const styleEl = document.createElement('style');
    styleEl.textContent = `
      .toast-notification.show {
        opacity: 1;
        transform: translateY(0);
      }
      
      .toast-notification .toast-icon {
        margin-right: 12px;
        font-size: 18px;
      }
      
      .toast-notification .toast-content {
        flex: 1;
      }
      
      .toast-notification .toast-content p {
        margin: 0;
      }
      
      .toast-notification .toast-close {
        background: none;
        border: none;
        cursor: pointer;
        color: currentColor;
        opacity: 0.6;
        font-size: 16px;
        padding: 0;
        margin-left: 12px;
        transition: opacity 0.2s;
      }
      
      .toast-notification .toast-close:hover {
        opacity: 1;
      }
    `;
    
    // Add style element to document head if it doesn't exist already
    if (!document.getElementById('toast-styles')) {
      styleEl.id = 'toast-styles';
      document.head.appendChild(styleEl);
    }
  }
  
  /**
   * Enforce maximum number of toasts
   * @private
   */
  _enforceMaxToasts() {
    if (this.toasts.length > this.options.maxToasts) {
      // Remove oldest toasts
      const toastsToRemove = this.toasts.slice(0, this.toasts.length - this.options.maxToasts);
      toastsToRemove.forEach(toast => {
        this.dismiss(toast.id);
      });
    }
  }
  
  /**
   * Update toast service options
   * @param {Object} options - New options
   */
  updateOptions(options) {
    this.options = { ...this.options, ...options };
    
    // Update container if position changed
    if (options.position) {
      this._applyPositionClass();
      this._applyContainerStyle();
    }
  }
}

// Create singleton instance
const toastService = new ToastService();

// Create legacy function for backward compatibility
window.showToast = (message, type = 'info', duration = 5000) => {
  return toastService.show(message, type, { duration });
};

export { toastService };