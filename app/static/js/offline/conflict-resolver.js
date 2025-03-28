/**
 * MagnetoCursor - Conflict Resolver
 * 
 * Handles automatic and interactive resolution of conflicts between
 * local offline changes and remote server data.
 */

/**
 * Conflict Resolution Types
 */
export const ResolutionType = {
  LOCAL: 'local', // Use local changes (client wins)
  SERVER: 'server', // Use server data (server wins)
  MERGE: 'merged', // Use merged data from both sides
  MANUAL: 'manual' // User must decide manually
};

/**
 * Conflict Resolver
 */
export class ConflictResolver {
  /**
   * Create a new ConflictResolver
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = {
      defaultResolution: ResolutionType.SERVER, // Default resolution strategy
      fieldResolutions: {}, // Specific resolution strategies for certain fields
      entityTypeResolutions: {}, // Specific resolution strategies for entity types
      autoresolveThreshold: 120000, // Auto-resolve if changes are more than 2 minutes apart
      manualResolutionCallback: null, // Callback for manual resolution
      fieldMergeFunctions: {}, // Custom merge functions for specific fields
      ...options
    };
  }
  
  /**
   * Resolve a conflict between local and server data
   * @param {Object} change - The local change object
   * @param {Object} serverData - The server's current data
   * @returns {Promise<Object>} - Resolution result
   */
  async resolve(change, serverData) {
    // If there's no server data, use local changes
    if (!serverData) {
      return {
        resolved: true,
        action: ResolutionType.LOCAL
      };
    }
    
    try {
      // Check if we have a specific resolution strategy for this entity type
      const entityTypeStrategy = this.options.entityTypeResolutions[change.entityType];
      if (entityTypeStrategy) {
        if (typeof entityTypeStrategy === 'function') {
          // Use custom function for this entity type
          const result = await entityTypeStrategy(change, serverData);
          if (result && result.resolved) {
            return result;
          }
        } else if (Object.values(ResolutionType).includes(entityTypeStrategy)) {
          // Use predefined resolution type
          return this._resolveWithStrategy(entityTypeStrategy, change, serverData);
        }
      }
      
      // Check the timestamps to decide if we can auto-resolve
      if (this._canAutoResolve(change, serverData)) {
        return this._autoResolve(change, serverData);
      }
      
      // Fields with dedicated resolution strategies
      const fieldResolutionResult = await this._resolveByFields(change, serverData);
      if (fieldResolutionResult && fieldResolutionResult.resolved) {
        return fieldResolutionResult;
      }
      
      // If we have a manual resolution callback, use it
      if (typeof this.options.manualResolutionCallback === 'function') {
        return await this.options.manualResolutionCallback(change, serverData);
      }
      
      // Default resolution strategy
      return this._resolveWithStrategy(this.options.defaultResolution, change, serverData);
    } catch (error) {
      console.error('Error resolving conflict:', error);
      
      // If resolution fails, default to server data
      return {
        resolved: true,
        action: ResolutionType.SERVER,
        error: error.message
      };
    }
  }
  
  /**
   * Check if a conflict can be automatically resolved based on timestamps
   * @param {Object} change - The local change
   * @param {Object} serverData - The server data
   * @returns {boolean} - Whether the conflict can be auto-resolved
   * @private
   */
  _canAutoResolve(change, serverData) {
    // Get the timestamps
    const localTimestamp = change.timestamp;
    const serverTimestamp = serverData.updatedAt ? new Date(serverData.updatedAt).getTime() : null;
    
    // If server has no timestamp, we can't auto-resolve
    if (!serverTimestamp) {
      return false;
    }
    
    // Calculate the time difference
    const timeDiff = Math.abs(localTimestamp - serverTimestamp);
    
    // If the changes are far apart, we can auto-resolve
    return timeDiff > this.options.autoresolveThreshold;
  }
  
  /**
   * Auto-resolve a conflict based on timestamps
   * @param {Object} change - The local change
   * @param {Object} serverData - The server data
   * @returns {Object} - Resolution result
   * @private
   */
  _autoResolve(change, serverData) {
    const localTimestamp = change.timestamp;
    const serverTimestamp = serverData.updatedAt ? new Date(serverData.updatedAt).getTime() : 0;
    
    // Newest change wins
    if (localTimestamp > serverTimestamp) {
      return {
        resolved: true,
        action: ResolutionType.LOCAL,
        reason: 'auto-timestamp'
      };
    } else {
      return {
        resolved: true,
        action: ResolutionType.SERVER,
        reason: 'auto-timestamp'
      };
    }
  }
  
  /**
   * Resolve conflict by checking field-specific strategies
   * @param {Object} change - The local change
   * @param {Object} serverData - The server data
   * @returns {Object|null} - Resolution result or null if no resolution
   * @private
   */
  async _resolveByFields(change, serverData) {
    // If this is a delete operation, we can't use field-specific resolution
    if (change.operation === 'delete' || !change.data) {
      return null;
    }
    
    // Create a merged copy of the data
    let mergedData = { ...serverData };
    let changedFields = 0;
    let totalFields = 0;
    
    // Check each changed field
    for (const field in change.data) {
      totalFields++;
      
      // Skip special fields
      if (field === 'id' || field === 'clientTimestamp') {
        continue;
      }
      
      // Check if this field has a specific resolution strategy
      const fieldStrategy = this.options.fieldResolutions[field];
      if (fieldStrategy) {
        if (fieldStrategy === ResolutionType.LOCAL) {
          // Use local value
          mergedData[field] = change.data[field];
          changedFields++;
        } else if (fieldStrategy === ResolutionType.SERVER) {
          // Keep server value
          // No need to do anything as mergedData already has server values
        } else if (fieldStrategy === ResolutionType.MERGE) {
          // Use custom merge function if available
          const mergeFunction = this.options.fieldMergeFunctions[field];
          if (typeof mergeFunction === 'function') {
            mergedData[field] = mergeFunction(change.data[field], serverData[field]);
            changedFields++;
          } else {
            // Default merge (use local for primitive values, merge objects)
            if (typeof change.data[field] === 'object' && change.data[field] !== null && 
                typeof serverData[field] === 'object' && serverData[field] !== null) {
              mergedData[field] = { ...serverData[field], ...change.data[field] };
              changedFields++;
            } else {
              // For primitive values, default to local changes
              mergedData[field] = change.data[field];
              changedFields++;
            }
          }
        } else if (typeof fieldStrategy === 'function') {
          // Use custom function
          const result = await fieldStrategy(change.data[field], serverData[field], field);
          if (result !== undefined) {
            mergedData[field] = result;
            changedFields++;
          }
        }
      } else {
        // No specific strategy for this field, use local changes by default
        mergedData[field] = change.data[field];
        changedFields++;
      }
    }
    
    // If we didn't change any fields or if all fields were explicitly resolved to server values,
    // return server-side resolution
    if (changedFields === 0) {
      return {
        resolved: true,
        action: ResolutionType.SERVER,
        reason: 'field-resolution'
      };
    }
    
    // If we changed fields to match local values exactly, return local-side resolution
    if (changedFields === totalFields) {
      return {
        resolved: true,
        action: ResolutionType.LOCAL,
        reason: 'field-resolution'
      };
    }
    
    // Otherwise, we have a merged result
    return {
      resolved: true,
      action: ResolutionType.MERGE,
      mergedData,
      reason: 'field-resolution'
    };
  }
  
  /**
   * Resolve with a specific strategy
   * @param {string} strategy - Resolution strategy
   * @param {Object} change - The local change
   * @param {Object} serverData - The server data
   * @returns {Object} - Resolution result
   * @private
   */
  _resolveWithStrategy(strategy, change, serverData) {
    switch (strategy) {
      case ResolutionType.LOCAL:
        return {
          resolved: true,
          action: ResolutionType.LOCAL,
          reason: 'strategy'
        };
        
      case ResolutionType.SERVER:
        return {
          resolved: true,
          action: ResolutionType.SERVER,
          reason: 'strategy'
        };
        
      case ResolutionType.MERGE:
        // For merge strategy, we need to actually merge the data
        if (change.operation === 'delete' || !change.data) {
          // Can't merge if we're deleting or have no data
          return {
            resolved: true,
            action: ResolutionType.SERVER,
            reason: 'cannot-merge-delete'
          };
        }
        
        // Simple merge: combine server and local data, with local taking precedence
        const mergedData = { ...serverData, ...change.data };
        
        return {
          resolved: true,
          action: ResolutionType.MERGE,
          mergedData,
          reason: 'strategy'
        };
        
      case ResolutionType.MANUAL:
        // For manual resolution, we need the callback
        if (typeof this.options.manualResolutionCallback !== 'function') {
          // If we don't have a callback, default to server
          return {
            resolved: true,
            action: ResolutionType.SERVER,
            reason: 'manual-fallback'
          };
        }
        
        // Should be handled elsewhere, but just in case
        return {
          resolved: false,
          reason: 'manual-required'
        };
        
      default:
        // Unknown strategy, default to server
        return {
          resolved: true,
          action: ResolutionType.SERVER,
          reason: 'unknown-strategy'
        };
    }
  }
  
  /**
   * Create a manual resolution callback
   * @param {Function} callback - Function that will handle manual resolution
   */
  setManualResolutionCallback(callback) {
    if (typeof callback === 'function') {
      this.options.manualResolutionCallback = callback;
    }
  }
  
  /**
   * Update resolution options
   * @param {Object} options - New options to apply
   */
  updateOptions(options) {
    this.options = {
      ...this.options,
      ...options
    };
  }
  
  /**
   * Set a resolution strategy for a specific field
   * @param {string} field - Field name
   * @param {string|Function} strategy - Resolution strategy
   */
  setFieldResolution(field, strategy) {
    this.options.fieldResolutions[field] = strategy;
  }
  
  /**
   * Set a resolution strategy for a specific entity type
   * @param {string} entityType - Entity type
   * @param {string|Function} strategy - Resolution strategy
   */
  setEntityTypeResolution(entityType, strategy) {
    this.options.entityTypeResolutions[entityType] = strategy;
  }
  
  /**
   * Set a custom merge function for a specific field
   * @param {string} field - Field name
   * @param {Function} mergeFunction - Function to merge values
   */
  setFieldMergeFunction(field, mergeFunction) {
    if (typeof mergeFunction === 'function') {
      this.options.fieldMergeFunctions[field] = mergeFunction;
    }
  }
}

/**
 * Default instance of conflict resolver
 */
export const defaultConflictResolver = new ConflictResolver();

/**
 * Object deepMerge utility for conflict resolution
 * @param {Object} target - Target object
 * @param {Object} source - Source object
 * @returns {Object} - Merged object
 */
export function deepMerge(target, source) {
  const output = { ...target };
  
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach(key => {
      if (isObject(source[key])) {
        if (!(key in target)) {
          Object.assign(output, { [key]: source[key] });
        } else {
          output[key] = deepMerge(target[key], source[key]);
        }
      } else {
        Object.assign(output, { [key]: source[key] });
      }
    });
  }
  
  return output;
}

/**
 * Check if value is an object
 * @param {any} item - Value to check
 * @returns {boolean} - Whether it's an object
 */
function isObject(item) {
  return item && typeof item === 'object' && !Array.isArray(item);
}

/**
 * Create timestamp-based conflict resolution
 * @param {number} threshold - Time threshold in milliseconds
 * @returns {Function} - Resolution function
 */
export function createTimestampResolver(threshold = 3600000) { // Default: 1 hour
  return function(change, serverData) {
    const localTimestamp = change.timestamp;
    const serverTimestamp = serverData.updatedAt ? new Date(serverData.updatedAt).getTime() : 0;
    
    // If changes are further apart than threshold
    if (Math.abs(localTimestamp - serverTimestamp) > threshold) {
      // Newest change wins
      if (localTimestamp > serverTimestamp) {
        return {
          resolved: true,
          action: ResolutionType.LOCAL,
          reason: 'timestamp-threshold'
        };
      } else {
        return {
          resolved: true,
          action: ResolutionType.SERVER,
          reason: 'timestamp-threshold'
        };
      }
    }
    
    // Otherwise, use default resolution (can't auto-resolve based on time)
    return null;
  };
}

/**
 * Create field-value-based conflict resolution
 * @param {Object} fieldPriorities - Object mapping field names to priorities
 * @returns {Function} - Resolution function
 */
export function createFieldPriorityResolver(fieldPriorities) {
  return function(change, serverData) {
    // Only applicable for updates with data
    if (change.operation === 'delete' || !change.data) {
      return null;
    }
    
    const changedFields = Object.keys(change.data).filter(field => 
      field !== 'id' && field !== 'clientTimestamp');
    
    // Get the highest priority field that was changed
    let highestPriority = -1;
    let highestPriorityField = null;
    
    for (const field of changedFields) {
      const priority = fieldPriorities[field] || 0;
      if (priority > highestPriority) {
        highestPriority = priority;
        highestPriorityField = field;
      }
    }
    
    // If we found a high-priority field, use it to determine resolution
    if (highestPriorityField && highestPriority > 0) {
      const localValue = change.data[highestPriorityField];
      const serverValue = serverData[highestPriorityField];
      
      // If the values are different and we have a high-priority field
      if (JSON.stringify(localValue) !== JSON.stringify(serverValue)) {
        // The resolution is based on which value is "better"
        // In this case, we'll just use the local value since it's a high-priority field
        return {
          resolved: true,
          action: ResolutionType.LOCAL,
          reason: 'field-priority',
          field: highestPriorityField
        };
      }
    }
    
    // No high-priority field found or values are the same
    return null;
  };
}
