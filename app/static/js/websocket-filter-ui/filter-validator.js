/**
 * WebSocket Filter Validator
 * 
 * Validates filter definitions and provides error information
 */

export class FilterValidator {
  /**
   * Initialize a new filter validator
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = {
      fields: [],
      entityTypes: [],
      ...options
    };
  }
  
  /**
   * Validate a filter object
   * @param {Object} filter - Filter to validate
   * @returns {Object} Validation result { valid: boolean, errors: string[] }
   */
  validateFilter(filter) {
    const errors = [];
    
    // Check required properties
    if (!filter) {
      errors.push('Filter object is required');
      return { valid: false, errors };
    }
    
    if (!filter.name || filter.name.trim() === '') {
      errors.push('Filter name is required');
    }
    
    if (!filter.category) {
      errors.push('Filter category is required');
    }
    
    // Validate definition
    if (!filter.definition) {
      errors.push('Filter definition is required');
      return { valid: false, errors };
    }
    
    // Validate entity type
    if (!filter.definition.entityType) {
      errors.push('Entity type is required');
    } else {
      const validEntityType = this.options.entityTypes.some(type => type.id === filter.definition.entityType);
      if (!validEntityType) {
        errors.push(`Unknown entity type: ${filter.definition.entityType}`);
      }
    }
    
    // Validate conditions
    this._validateConditions(filter.definition, errors);
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  /**
   * Validate conditions object
   * @param {Object} definition - Filter definition
   * @param {string[]} errors - Array to collect errors
   * @private
   */
  _validateConditions(definition, errors) {
    if (!definition.conditions) {
      errors.push('Conditions are required');
      return;
    }
    
    // Validate operator
    if (!definition.conditions.operator) {
      errors.push('Condition group operator is required');
    } else if (!['AND', 'OR'].includes(definition.conditions.operator)) {
      errors.push(`Invalid condition group operator: ${definition.conditions.operator}`);
    }
    
    // Validate individual conditions
    if (!Array.isArray(definition.conditions.conditions) || definition.conditions.conditions.length === 0) {
      errors.push('At least one condition is required');
      return;
    }
    
    definition.conditions.conditions.forEach((condition, index) => {
      this._validateCondition(condition, definition.entityType, index, errors);
    });
  }
  
  /**
   * Validate individual condition
   * @param {Object} condition - Condition to validate
   * @param {string} entityType - Entity type
   * @param {number} index - Condition index
   * @param {string[]} errors - Array to collect errors
   * @private
   */
  _validateCondition(condition, entityType, index, errors) {
    // Check for required fields
    if (!condition.field) {
      errors.push(`Condition ${index + 1}: Field is required`);
    }
    
    if (!condition.operator) {
      errors.push(`Condition ${index + 1}: Operator is required`);
    }
    
    // If both field and operator are missing, no need for further validation
    if (!condition.field || !condition.operator) {
      return;
    }
    
    // Get field definition
    const field = this.options.fields.find(f => 
      f.entityType === entityType && f.id === condition.field
    );
    
    if (!field) {
      errors.push(`Condition ${index + 1}: Unknown field: ${condition.field}`);
      return;
    }
    
    // Validate operator for field type
    const validOperators = this._getValidOperatorsForType(field.type);
    if (!validOperators.includes(condition.operator)) {
      errors.push(`Condition ${index + 1}: Invalid operator ${condition.operator} for field type ${field.type}`);
    }
    
    // Validate value based on operator and field type
    this._validateConditionValue(condition, field, index, errors);
  }
  
  /**
   * Validate condition value
   * @param {Object} condition - Condition to validate
   * @param {Object} field - Field definition
   * @param {number} index - Condition index
   * @param {string[]} errors - Array to collect errors
   * @private
   */
  _validateConditionValue(condition, field, index, errors) {
    // Skip validation for operators that don't need values
    if (['is_true', 'is_false', 'is_null', 'is_not_null'].includes(condition.operator)) {
      return;
    }
    
    // Check if value is present
    if (condition.value === undefined || condition.value === null || condition.value === '') {
      errors.push(`Condition ${index + 1}: Value is required for operator: ${condition.operator}`);
      return;
    }
    
    // Type-specific validation
    switch (field.type) {
      case 'number':
        this._validateNumberValue(condition, index, errors);
        break;
      case 'date':
        this._validateDateValue(condition, index, errors);
        break;
      case 'array':
        this._validateArrayValue(condition, index, errors);
        break;
    }
  }
  
  /**
   * Validate number value
   * @param {Object} condition - Condition to validate
   * @param {number} index - Condition index
   * @param {string[]} errors - Array to collect errors
   * @private
   */
  _validateNumberValue(condition, index, errors) {
    if (condition.operator === 'between') {
      // For between, we need an array of two numbers
      if (!Array.isArray(condition.value) || condition.value.length !== 2) {
        errors.push(`Condition ${index + 1}: Between operator requires an array of two numbers`);
      } else {
        const [min, max] = condition.value;
        if (isNaN(parseFloat(min)) || isNaN(parseFloat(max))) {
          errors.push(`Condition ${index + 1}: Both values must be numbers`);
        } else if (parseFloat(min) >= parseFloat(max)) {
          errors.push(`Condition ${index + 1}: First value must be less than second value`);
        }
      }
    } else {
      // For other operators, we need a single number
      if (isNaN(parseFloat(condition.value))) {
        errors.push(`Condition ${index + 1}: Value must be a number`);
      }
    }
  }
  
  /**
   * Validate date value
   * @param {Object} condition - Condition to validate
   * @param {number} index - Condition index
   * @param {string[]} errors - Array to collect errors
   * @private
   */
  _validateDateValue(condition, index, errors) {
    if (condition.operator === 'between') {
      // For between, we need an array of two dates
      if (!Array.isArray(condition.value) || condition.value.length !== 2) {
        errors.push(`Condition ${index + 1}: Between operator requires an array of two dates`);
      } else {
        const [start, end] = condition.value;
        const startDate = new Date(start);
        const endDate = new Date(end);
        
        if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
          errors.push(`Condition ${index + 1}: Both values must be valid dates`);
        } else if (startDate >= endDate) {
          errors.push(`Condition ${index + 1}: Start date must be before end date`);
        }
      }
    } else {
      // For other operators, we need a single date
      const date = new Date(condition.value);
      if (isNaN(date.getTime())) {
        errors.push(`Condition ${index + 1}: Value must be a valid date`);
      }
    }
  }
  
  /**
   * Validate array value
   * @param {Object} condition - Condition to validate
   * @param {number} index - Condition index
   * @param {string[]} errors - Array to collect errors
   * @private
   */
  _validateArrayValue(condition, index, errors) {
    if (['contains_any', 'contains_all'].includes(condition.operator)) {
      // These operators need an array of values
      if (!Array.isArray(condition.value) || condition.value.length === 0) {
        errors.push(`Condition ${index + 1}: ${condition.operator} operator requires a non-empty array`);
      }
    }
  }
  
  /**
   * Get valid operators for field type
   * @param {string} fieldType - Field type
   * @returns {string[]} Array of valid operators
   * @private
   */
  _getValidOperatorsForType(fieldType) {
    switch (fieldType) {
      case 'string':
        return ['equals', 'contains', 'starts_with', 'ends_with', 'is_null', 'is_not_null'];
      case 'number':
        return ['equals', 'greater_than', 'less_than', 'between', 'is_null', 'is_not_null'];
      case 'boolean':
        return ['is_true', 'is_false'];
      case 'date':
        return ['equals', 'before', 'after', 'between', 'is_null', 'is_not_null'];
      case 'array':
        return ['contains', 'contains_any', 'contains_all', 'is_null', 'is_not_null'];
      default:
        return [];
    }
  }
}

export default FilterValidator;