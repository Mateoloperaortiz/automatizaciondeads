/**
 * MagnetoCursor - Cluster Visualization Component
 * 
 * Provides an interactive visualization of ML clusters with both 2D and 3D views.
 * Uses Chart.js for 2D rendering and Three.js for 3D rendering.
 */

export class ClusterVisualization {
  /**
   * Initialize the cluster visualization component
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      transitionDuration: 750,
      pointSize: 6,
      highlightSize: 8,
      colors: [
        '#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f',
        '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab'
      ],
      ...options
    };
    
    // State
    this.data = null;
    this.viewMode = '2d'; // '2d' or '3d'
    this.chart = null;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.pointCloud = null;
    this.highlightedCluster = null;
    this.isLoading = false;
    this.initialized = false;
    
    // Initialize component
    this.initialize();
  }
  
  /**
   * Initialize the visualization
   */
  initialize() {
    // Create container structure
    this.container.innerHTML = `
      <div class="cluster-container">
        <div class="canvas-container">
          <canvas id="cluster-canvas-2d" class="cluster-canvas ${this.viewMode === '2d' ? 'active' : ''}"></canvas>
          <div id="cluster-canvas-3d" class="cluster-canvas-3d ${this.viewMode === '3d' ? 'active' : ''}"></div>
        </div>
        <div class="cluster-loading">
          <div class="spinner"></div>
          <div class="loading-text">Loading visualization...</div>
        </div>
        <div class="cluster-empty">
          <div class="empty-text">No cluster data available</div>
        </div>
      </div>
    `;
    
    // Add styles
    this._addStyles();
    
    // Initialize libraries
    this._initializeLibraries().then(() => {
      this.initialized = true;
      
      // If we have data, update the visualization
      if (this.data) {
        this.updateData(this.data);
      } else {
        this._showEmptyState();
      }
    }).catch(error => {
      console.error('Error initializing visualization libraries:', error);
      this._showErrorState('Failed to initialize visualization libraries');
    });
  }
  
  /**
   * Add component styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('cluster-visualization-styles')) {
      const style = document.createElement('style');
      style.id = 'cluster-visualization-styles';
      style.textContent = `
        .cluster-container {
          position: relative;
          width: 100%;
          height: 100%;
          overflow: hidden;
        }
        
        .canvas-container {
          width: 100%;
          height: 100%;
        }
        
        .cluster-canvas {
          display: none;
          width: 100%;
          height: 100%;
        }
        
        .cluster-canvas.active {
          display: block;
        }
        
        .cluster-canvas-3d {
          display: none;
          width: 100%;
          height: 100%;
        }
        
        .cluster-canvas-3d.active {
          display: block;
        }
        
        .cluster-loading {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.8);
          z-index: 10;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.3s ease-in-out;
        }
        
        .cluster-loading.active {
          opacity: 1;
          pointer-events: auto;
        }
        
        .dark-mode .cluster-loading {
          background: rgba(33, 37, 41, 0.8);
          color: #f8f9fa;
        }
        
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid rgba(0, 0, 0, 0.1);
          border-top: 4px solid var(--highlight-color, #0d6efd);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 1rem;
        }
        
        .dark-mode .spinner {
          border-color: rgba(255, 255, 255, 0.1);
          border-top-color: var(--highlight-color, #0d6efd);
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .loading-text {
          font-size: 0.875rem;
        }
        
        .cluster-empty {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--panel-bg, white);
          z-index: 5;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.3s ease-in-out;
        }
        
        .cluster-empty.active {
          opacity: 1;
          pointer-events: auto;
        }
        
        .empty-text {
          font-size: 1rem;
          color: var(--text-color-secondary, #6c757d);
          font-style: italic;
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Initialize visualization libraries
   * @returns {Promise} - Promise that resolves when libraries are loaded
   * @private
   */
  async _initializeLibraries() {
    try {
      // Show loading state
      this._showLoadingState(true);
      
      // Load Chart.js if not already loaded
      if (!window.Chart) {
        await this._loadScript('https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js');
      }
      
      // Load Three.js if not already loaded
      if (!window.THREE) {
        await this._loadScript('https://cdn.jsdelivr.net/npm/three@0.144.0/build/three.min.js');
        // Load OrbitControls for Three.js
        await this._loadScript('https://cdn.jsdelivr.net/npm/three@0.144.0/examples/js/controls/OrbitControls.js');
      }
      
      // Initialize Chart.js
      this._initializeChart();
      
      // Initialize Three.js
      this._initializeThreeJs();
      
      // Hide loading state
      this._showLoadingState(false);
      
      return true;
    } catch (error) {
      console.error('Error loading visualization libraries:', error);
      this._showLoadingState(false);
      throw error;
    }
  }
  
  /**
   * Initialize Chart.js for 2D visualization
   * @private
   */
  _initializeChart() {
    const canvas = document.getElementById('cluster-canvas-2d');
    if (!canvas) return;
    
    // Get context
    const ctx = canvas.getContext('2d');
    
    // Create chart
    this.chart = new Chart(ctx, {
      type: 'scatter',
      data: {
        datasets: []
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: this.options.transitionDuration
        },
        scales: {
          x: {
            ticks: {
              color: this.options.darkMode ? '#adb5bd' : '#666',
              font: {
                size: 10
              }
            },
            grid: {
              color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
            },
            title: {
              display: true,
              text: 'Component 1',
              color: this.options.darkMode ? '#f8f9fa' : '#333'
            }
          },
          y: {
            ticks: {
              color: this.options.darkMode ? '#adb5bd' : '#666',
              font: {
                size: 10
              }
            },
            grid: {
              color: this.options.darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
            },
            title: {
              display: true,
              text: 'Component 2',
              color: this.options.darkMode ? '#f8f9fa' : '#333'
            }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => {
                const point = context.raw;
                return `Cluster: ${point.cluster}, (${point.x.toFixed(2)}, ${point.y.toFixed(2)})`;
              }
            }
          },
          legend: {
            display: false
          }
        }
      }
    });
  }
  
  /**
   * Initialize Three.js for 3D visualization
   * @private
   */
  _initializeThreeJs() {
    const container = document.getElementById('cluster-canvas-3d');
    if (!container) return;
    
    // Get container dimensions
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Create scene
    this.scene = new THREE.Scene();
    if (this.options.darkMode) {
      this.scene.background = new THREE.Color(0x212529);
    } else {
      this.scene.background = new THREE.Color(0xffffff);
    }
    
    // Create camera
    this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    this.camera.position.z = 5;
    
    // Create renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(width, height);
    container.appendChild(this.renderer.domElement);
    
    // Add orbit controls
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.25;
    this.controls.screenSpacePanning = false;
    this.controls.maxDistance = 100;
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0x404040, 1.5);
    this.scene.add(ambientLight);
    
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1).normalize();
    this.scene.add(light);
    
    // Add axes helper
    const axesHelper = new THREE.AxesHelper(3);
    this.scene.add(axesHelper);
    
    // Add resize listener
    window.addEventListener('resize', () => {
      if (this.renderer && this.camera) {
        const newWidth = container.clientWidth;
        const newHeight = container.clientHeight;
        
        this.camera.aspect = newWidth / newHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(newWidth, newHeight);
      }
    });
    
    // Start animation loop
    this._animate();
  }
  
  /**
   * Three.js animation loop
   * @private
   */
  _animate() {
    if (!this.scene || !this.renderer) return;
    
    requestAnimationFrame(() => this._animate());
    
    if (this.controls) {
      this.controls.update();
    }
    
    this.renderer.render(this.scene, this.camera);
  }
  
  /**
   * Load a script dynamically
   * @param {string} url - Script URL
   * @returns {Promise} - Promise that resolves when script is loaded
   * @private
   */
  _loadScript(url) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = url;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }
  
  /**
   * Show/hide loading state
   * @param {boolean} show - Whether to show loading state
   * @private
   */
  _showLoadingState(show) {
    this.isLoading = show;
    const loadingElement = this.container.querySelector('.cluster-loading');
    
    if (loadingElement) {
      if (show) {
        loadingElement.classList.add('active');
      } else {
        loadingElement.classList.remove('active');
      }
    }
  }
  
  /**
   * Show empty state
   * @private
   */
  _showEmptyState() {
    const emptyElement = this.container.querySelector('.cluster-empty');
    
    if (emptyElement) {
      emptyElement.classList.add('active');
    }
  }
  
  /**
   * Hide empty state
   * @private
   */
  _hideEmptyState() {
    const emptyElement = this.container.querySelector('.cluster-empty');
    
    if (emptyElement) {
      emptyElement.classList.remove('active');
    }
  }
  
  /**
   * Show error state
   * @param {string} message - Error message
   * @private
   */
  _showErrorState(message) {
    const emptyElement = this.container.querySelector('.cluster-empty');
    
    if (emptyElement) {
      emptyElement.classList.add('active');
      const textElement = emptyElement.querySelector('.empty-text');
      if (textElement) {
        textElement.textContent = message;
        textElement.classList.add('error');
      }
    }
  }
  
  /**
   * Get color for a cluster
   * @param {number} index - Cluster index
   * @returns {string} - Cluster color
   */
  getColorForCluster(index) {
    return this.options.colors[index % this.options.colors.length];
  }
  
  /**
   * Set visualization view mode (2D/3D)
   * @param {string} mode - View mode ('2d' or '3d')
   */
  setViewMode(mode) {
    if (mode !== '2d' && mode !== '3d') {
      console.error('Invalid view mode:', mode);
      return;
    }
    
    this.viewMode = mode;
    
    // Update canvas visibility
    const canvas2d = document.getElementById('cluster-canvas-2d');
    const canvas3d = document.getElementById('cluster-canvas-3d');
    
    if (canvas2d) {
      if (mode === '2d') {
        canvas2d.classList.add('active');
      } else {
        canvas2d.classList.remove('active');
      }
    }
    
    if (canvas3d) {
      if (mode === '3d') {
        canvas3d.classList.add('active');
      } else {
        canvas3d.classList.remove('active');
      }
    }
    
    // Trigger resize event to ensure proper rendering
    window.dispatchEvent(new Event('resize'));
  }
  
  /**
   * Update visualization with new data
   * @param {Object} data - Cluster data
   */
  updateData(data) {
    // Store data
    this.data = data;
    
    // Show loading state
    this._showLoadingState(true);
    
    // Hide empty state
    this._hideEmptyState();
    
    // Skip visualization if no data
    if (!data || !data.points || data.points.length === 0) {
      this._showEmptyState();
      this._showLoadingState(false);
      return;
    }
    
    // Wait for initialization to complete
    if (!this.initialized) {
      this._showLoadingState(false);
      return;
    }
    
    // Update 2D visualization
    this._update2D(data);
    
    // Update 3D visualization
    this._update3D(data);
    
    // Hide loading state
    this._showLoadingState(false);
  }
  
  /**
   * Update 2D visualization
   * @param {Object} data - Cluster data
   * @private
   */
  _update2D(data) {
    if (!this.chart) return;
    
    // Clear existing datasets
    this.chart.data.datasets = [];
    
    // Process points by cluster
    const clusterData = {};
    
    // Group by cluster
    data.points.forEach(point => {
      const clusterId = point.cluster;
      if (!clusterData[clusterId]) {
        clusterData[clusterId] = [];
      }
      clusterData[clusterId].push({
        x: point.x,
        y: point.y,
        cluster: clusterId
      });
    });
    
    // Create datasets for each cluster
    Object.keys(clusterData).forEach(clusterId => {
      const color = this.getColorForCluster(parseInt(clusterId));
      const isHighlighted = this.highlightedCluster === parseInt(clusterId);
      
      this.chart.data.datasets.push({
        label: `Cluster ${clusterId}`,
        data: clusterData[clusterId],
        backgroundColor: color,
        borderColor: color,
        pointRadius: isHighlighted ? this.options.highlightSize : this.options.pointSize,
        pointHoverRadius: isHighlighted ? this.options.highlightSize + 2 : this.options.pointSize + 2
      });
    });
    
    // Update chart
    this.chart.update();
  }
  
  /**
   * Update 3D visualization
   * @param {Object} data - Cluster data
   * @private
   */
  _update3D(data) {
    if (!this.scene) return;
    
    // Remove existing point cloud
    if (this.pointCloud) {
      this.scene.remove(this.pointCloud);
      this.pointCloud = null;
    }
    
    // Create points geometry
    const geometry = new THREE.BufferGeometry();
    const positions = [];
    const colors = [];
    const sizes = [];
    
    // Process points
    data.points.forEach(point => {
      // Position
      positions.push(point.x, point.y, point.z || 0);
      
      // Color
      const color = new THREE.Color(this.getColorForCluster(point.cluster));
      colors.push(color.r, color.g, color.b);
      
      // Size (larger for highlighted cluster)
      const size = this.highlightedCluster === point.cluster ? 
        this.options.highlightSize : this.options.pointSize;
      sizes.push(size);
    });
    
    // Set attributes
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1));
    
    // Create point cloud material
    const material = new THREE.PointsMaterial({
      size: this.options.pointSize,
      vertexColors: true,
      sizeAttenuation: true
    });
    
    // Create point cloud
    this.pointCloud = new THREE.Points(geometry, material);
    this.scene.add(this.pointCloud);
    
    // Reset camera position
    this.camera.position.set(0, 0, 5);
    this.controls.reset();
  }
  
  /**
   * Highlight a specific cluster
   * @param {number} clusterIndex - Cluster index to highlight
   */
  highlightCluster(clusterIndex) {
    this.highlightedCluster = clusterIndex;
    
    // Update both visualizations
    if (this.data) {
      this._update2D(this.data);
      this._update3D(this.data);
    }
  }
  
  /**
   * Resize the visualization
   */
  resize() {
    // Trigger resize event
    window.dispatchEvent(new Event('resize'));
    
    // Update chart
    if (this.chart) {
      this.chart.resize();
    }
  }
  
  /**
   * Clean up visualization
   */
  destroy() {
    // Destroy Chart.js instance
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
    
    // Clean up Three.js
    if (this.scene) {
      // Remove all objects from scene
      while (this.scene.children.length > 0) {
        this.scene.remove(this.scene.children[0]);
      }
      
      // Dispose of renderer
      if (this.renderer) {
        this.renderer.dispose();
        
        // Remove canvas
        const canvas = this.renderer.domElement;
        if (canvas && canvas.parentNode) {
          canvas.parentNode.removeChild(canvas);
        }
        
        this.renderer = null;
      }
      
      this.scene = null;
      this.camera = null;
      this.controls = null;
    }
    
    // Clear container
    if (this.container) {
      this.container.innerHTML = '';
    }
  }
}
