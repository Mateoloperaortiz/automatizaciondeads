/**
 * MagnetoCursor - Candidate Profile Map
 * 
 * Visualizes the geographic distribution of candidates on a map
 * with filtering by segment and heatmap visualization.
 */

export class CandidateProfileMap {
  /**
   * Initialize the candidate profile map
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      initialZoom: 3,
      maxZoom: 10,
      tileStyle: 'light', // 'light', 'dark', 'streets', 'satellite'
      heatmapRadius: 25,
      heatmapIntensity: 0.7,
      dotSize: 7,
      dotOpacity: 0.75,
      ...options
    };
    
    // Override tile style based on dark mode
    if (this.options.darkMode && this.options.tileStyle === 'light') {
      this.options.tileStyle = 'dark';
    }
    
    // State
    this.map = null;
    this.markers = [];
    this.heatmap = null;
    this.data = null;
    this.segment = null;
    this.initialized = false;
    this.colorScale = null;
    
    // Initialize map
    this.initialize();
  }
  
  /**
   * Initialize the map
   */
  async initialize() {
    // Add placeholder
    this.container.innerHTML = `
      <div class="map-placeholder">
        <div class="spinner"></div>
        <div class="placeholder-text">Loading map...</div>
      </div>
    `;
    
    // Add styles
    this._addStyles();
    
    // Load Mapbox GL JS and dependencies
    await this._loadDependencies();
    
    // Create map container
    this.container.innerHTML = `
      <div id="candidate-map-container" class="map-container"></div>
      <div class="map-overlay" id="map-legend">
        <div class="legend-title">Candidate Density</div>
        <div class="legend-scale">
          <div class="legend-labels"></div>
        </div>
      </div>
    `;
    
    // Initialize Mapbox map
    this._initializeMap();
    
    this.initialized = true;
    
    // Render data if available
    if (this.data) {
      this.updateData(this.data, this.segment);
    }
  }
  
  /**
   * Add component styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('candidate-profile-map-styles')) {
      const style = document.createElement('style');
      style.id = 'candidate-profile-map-styles';
      style.textContent = `
        .map-placeholder {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          width: 100%;
        }
        
        .placeholder-text {
          margin-top: 1rem;
          font-size: 0.875rem;
          color: var(--text-color-secondary, #6c757d);
        }
        
        .spinner {
          width: 30px;
          height: 30px;
          border: 3px solid rgba(0, 0, 0, 0.1);
          border-top: 3px solid var(--highlight-color, #0d6efd);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        .dark-mode .spinner {
          border-color: rgba(255, 255, 255, 0.1);
          border-top-color: var(--highlight-color, #0d6efd);
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .map-container {
          width: 100%;
          height: 100%;
          border-radius: 0.25rem;
          overflow: hidden;
        }
        
        .map-overlay {
          position: absolute;
          bottom: 10px;
          right: 10px;
          background: rgba(255, 255, 255, 0.9);
          border-radius: 4px;
          padding: 6px 10px;
          font-size: 11px;
          line-height: 1.4;
          z-index: 100;
          box-shadow: 0 1px 5px rgba(0, 0, 0, 0.15);
        }
        
        .dark-mode .map-overlay {
          background: rgba(33, 37, 41, 0.9);
          color: #f8f9fa;
        }
        
        .legend-title {
          font-weight: bold;
          margin-bottom: 5px;
          font-size: 10px;
          text-transform: uppercase;
        }
        
        .legend-scale {
          display: flex;
          flex-direction: column;
        }
        
        .legend-labels {
          display: flex;
          height: 10px;
          width: 100px;
        }
        
        .legend-label {
          flex: 1;
          height: 10px;
        }
        
        .mapboxgl-popup {
          max-width: 200px;
        }
        
        .mapboxgl-popup-content {
          padding: 10px;
          font-size: 12px;
        }
        
        .dark-mode .mapboxgl-popup-content {
          background: #343a40;
          color: #f8f9fa;
        }
        
        .popup-title {
          font-weight: bold;
          margin-bottom: 5px;
        }
        
        .popup-content {
          line-height: 1.4;
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Load map dependencies
   * @returns {Promise} - Promise that resolves when dependencies are loaded
   * @private
   */
  async _loadDependencies() {
    const loadMapboxGL = async () => {
      // Load Mapbox GL CSS
      if (!document.getElementById('mapbox-gl-css')) {
        const link = document.createElement('link');
        link.id = 'mapbox-gl-css';
        link.rel = 'stylesheet';
        link.href = 'https://api.mapbox.com/mapbox-gl-js/v2.12.0/mapbox-gl.css';
        document.head.appendChild(link);
      }
      
      // Load Mapbox GL JS
      if (!window.mapboxgl) {
        await this._loadScript('https://api.mapbox.com/mapbox-gl-js/v2.12.0/mapbox-gl.js');
      }
      
      // Set access token
      if (window.mapboxgl) {
        // Note: In a real implementation, this should be stored securely
        // This is just a placeholder public token for demonstration
        window.mapboxgl.accessToken = 'pk.eyJ1IjoibWFnbmV0b2N1cnNvciIsImEiOiJjazQ5eTB4Y2UwZTJwM2RvM2NhbjFpZ2pkIn0.8X1CyqSM4h5NQjf9jVSZKw';
      }
    };
    
    const loadD3 = async () => {
      // Load D3.js for color scales
      if (!window.d3) {
        await this._loadScript('https://d3js.org/d3.v7.min.js');
      }
    };
    
    // Load dependencies in parallel
    await Promise.all([
      loadMapboxGL(),
      loadD3()
    ]);
  }
  
  /**
   * Initialize Mapbox map
   * @private
   */
  _initializeMap() {
    if (!window.mapboxgl) {
      console.error('Mapbox GL JS not loaded');
      return;
    }
    
    const mapContainer = document.getElementById('candidate-map-container');
    if (!mapContainer) return;
    
    // Get tile style
    const style = this._getMapStyle();
    
    // Create map
    this.map = new mapboxgl.Map({
      container: mapContainer,
      style: style,
      center: [0, 20], // Center on world
      zoom: this.options.initialZoom,
      maxZoom: this.options.maxZoom
    });
    
    // Add navigation controls
    this.map.addControl(new mapboxgl.NavigationControl({
      showCompass: false,
      showZoom: true
    }), 'top-right');
    
    // Initialize legend
    this._initializeLegend();
    
    // Add map load event handler
    this.map.on('load', () => {
      // Add heatmap source and layer
      this.map.addSource('candidates', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      });
      
      // Add heatmap layer
      this.map.addLayer({
        id: 'candidate-heatmap',
        type: 'heatmap',
        source: 'candidates',
        paint: {
          'heatmap-weight': ['get', 'weight'],
          'heatmap-intensity': this.options.heatmapIntensity,
          'heatmap-radius': this.options.heatmapRadius,
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, 'rgba(0, 0, 255, 0)',
            0.2, 'rgba(65, 105, 225, 0.5)',
            0.4, 'rgba(0, 191, 255, 0.7)',
            0.6, 'rgba(0, 255, 255, 0.8)',
            0.8, 'rgba(0, 255, 0, 0.9)',
            1, 'rgba(255, 99, 71, 1)'
          ]
        }
      });
      
      // Add dot layer
      this.map.addLayer({
        id: 'candidate-points',
        type: 'circle',
        source: 'candidates',
        paint: {
          'circle-radius': this.options.dotSize,
          'circle-color': ['get', 'color'],
          'circle-opacity': this.options.dotOpacity,
          'circle-stroke-width': 1,
          'circle-stroke-color': '#fff'
        }
      });
      
      // Add click behavior
      this.map.on('click', 'candidate-points', (e) => {
        if (!e.features || e.features.length === 0) return;
        
        const feature = e.features[0];
        const props = feature.properties;
        
        // Create popup
        new mapboxgl.Popup()
          .setLngLat(feature.geometry.coordinates)
          .setHTML(`
            <div class="popup-title">${props.name || 'Candidate'}</div>
            <div class="popup-content">
              <div>Location: ${props.location}</div>
              <div>Experience: ${props.experience} years</div>
              <div>Segment: ${props.segment}</div>
            </div>
          `)
          .addTo(this.map);
      });
      
      // Change cursor on hover
      this.map.on('mouseenter', 'candidate-points', () => {
        this.map.getCanvas().style.cursor = 'pointer';
      });
      
      this.map.on('mouseleave', 'candidate-points', () => {
        this.map.getCanvas().style.cursor = '';
      });
      
      // If data is available, update the map
      if (this.data) {
        this._updateMapData(this.data, this.segment);
      }
    });
  }
  
  /**
   * Get map style URL based on options
   * @returns {string} - Mapbox style URL
   * @private
   */
  _getMapStyle() {
    const style = this.options.tileStyle;
    
    switch (style) {
      case 'dark':
        return 'mapbox://styles/mapbox/dark-v10';
      case 'light':
        return 'mapbox://styles/mapbox/light-v10';
      case 'streets':
        return 'mapbox://styles/mapbox/streets-v11';
      case 'satellite':
        return 'mapbox://styles/mapbox/satellite-v9';
      default:
        return 'mapbox://styles/mapbox/light-v10';
    }
  }
  
  /**
   * Initialize legend
   * @private
   */
  _initializeLegend() {
    const legendLabels = document.querySelector('.legend-labels');
    if (!legendLabels) return;
    
    // Create color gradient
    const colors = [
      'rgba(65, 105, 225, 0.5)',
      'rgba(0, 191, 255, 0.7)',
      'rgba(0, 255, 255, 0.8)',
      'rgba(0, 255, 0, 0.9)',
      'rgba(255, 99, 71, 1)'
    ];
    
    // Add color blocks
    colors.forEach(color => {
      const label = document.createElement('div');
      label.className = 'legend-label';
      label.style.backgroundColor = color;
      legendLabels.appendChild(label);
    });
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
   * Convert candidates data to GeoJSON
   * @param {Array} candidates - Array of candidate objects
   * @param {Object} segment - Optional segment filter
   * @returns {Object} - GeoJSON FeatureCollection
   * @private
   */
  _candidatesToGeoJSON(candidates, segment = null) {
    // Initialize color scale
    if (!this.colorScale && window.d3) {
      this.colorScale = d3.scaleOrdinal(d3.schemeCategory10);
    }
    
    // Filter candidates by segment if provided
    let filteredCandidates = candidates;
    if (segment) {
      filteredCandidates = candidates.filter(candidate => {
        return candidate.segments && candidate.segments.includes(segment.id);
      });
    }
    
    // Convert to GeoJSON features
    const features = filteredCandidates.map(candidate => {
      // Extract location if available
      const location = candidate.location || '';
      
      // Skip if no coordinates
      if (!candidate.latitude || !candidate.longitude) {
        return null;
      }
      
      // Create GeoJSON feature
      return {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [candidate.longitude, candidate.latitude]
        },
        properties: {
          id: candidate.id,
          name: candidate.name || `Candidate ${candidate.id}`,
          location: location,
          segment: segment ? segment.name : (candidate.primary_segment || 'Unassigned'),
          segment_id: segment ? segment.id : (candidate.primary_segment_id || 0),
          experience: candidate.years_of_experience || 0,
          age: candidate.age || 0,
          color: this.colorScale ? 
            this.colorScale(segment ? segment.id : (candidate.primary_segment_id || 0)) : 
            '#4e79a7',
          weight: 1.0
        }
      };
    }).filter(Boolean); // Filter out null entries
    
    return {
      type: 'FeatureCollection',
      features: features
    };
  }
  
  /**
   * Update map with new data
   * @param {Array} candidates - Array of candidate objects
   * @param {Object} segment - Optional segment filter
   * @private
   */
  _updateMapData(candidates, segment = null) {
    if (!this.map || !this.map.getSource('candidates')) {
      return;
    }
    
    // Convert to GeoJSON
    const geoJSON = this._candidatesToGeoJSON(candidates, segment);
    
    // Update source data
    this.map.getSource('candidates').setData(geoJSON);
    
    // Fit bounds if we have features
    if (geoJSON.features.length > 0) {
      // Calculate bounds from features
      const bounds = geoJSON.features.reduce((bounds, feature) => {
        return bounds.extend(feature.geometry.coordinates);
      }, new mapboxgl.LngLatBounds(
        geoJSON.features[0].geometry.coordinates,
        geoJSON.features[0].geometry.coordinates
      ));
      
      // Fit map to bounds with padding
      this.map.fitBounds(bounds, {
        padding: 50,
        maxZoom: 8
      });
    }
  }
  
  /**
   * Update map with new data
   * @param {Array} candidates - Array of candidate objects
   * @param {Object} segment - Optional segment filter
   */
  updateData(candidates, segment = null) {
    // Store data
    this.data = candidates;
    this.segment = segment;
    
    // Skip if not initialized
    if (!this.initialized || !this.map) {
      return;
    }
    
    // Wait for map to be fully loaded
    if (this.map.loaded()) {
      this._updateMapData(candidates, segment);
    } else {
      // Wait for map to load
      this.map.once('load', () => {
        this._updateMapData(candidates, segment);
      });
    }
  }
  
  /**
   * Apply segment filter
   * @param {Object} segment - Segment to filter by (null for all)
   */
  filterBySegment(segment) {
    this.segment = segment;
    
    if (this.data) {
      this._updateMapData(this.data, segment);
    }
  }
  
  /**
   * Set map style
   * @param {string} style - Map style ('light', 'dark', 'streets', 'satellite')
   */
  setMapStyle(style) {
    if (!this.map) return;
    
    this.options.tileStyle = style;
    this.map.setStyle(this._getMapStyle());
  }
  
  /**
   * Toggle heatmap view
   * @param {boolean} show - Whether to show heatmap
   */
  toggleHeatmap(show) {
    if (!this.map) return;
    
    const visibility = show ? 'visible' : 'none';
    this.map.setLayoutProperty('candidate-heatmap', 'visibility', visibility);
  }
  
  /**
   * Toggle point view
   * @param {boolean} show - Whether to show points
   */
  togglePoints(show) {
    if (!this.map) return;
    
    const visibility = show ? 'visible' : 'none';
    this.map.setLayoutProperty('candidate-points', 'visibility', visibility);
  }
  
  /**
   * Force map resize
   */
  resize() {
    if (this.map) {
      this.map.resize();
    }
  }
  
  /**
   * Clean up map
   */
  destroy() {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
    
    // Clear container
    this.container.innerHTML = '';
  }
}
