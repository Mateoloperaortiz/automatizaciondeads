/**
 * Schema Validator
 * Provides utilities for validating objects against JSON schemas
 */

/**
 * Validate an object against a schema
 * @param {Object} data - The data to validate
 * @param {Object} schema - The schema to validate against
 * @returns {Object} Validation result with isValid and errors
 */
export function validate(data, schema) {
  const errors = [];
  
  // Check required fields
  if (schema.required) {
    for (const field of schema.required) {
      if (data[field] === undefined || data[field] === null || data[field] === '') {
        errors.push({
          field,
          message: `${field} is required`
        });
      }
    }
  }
  
  // Validate field types and formats
  if (schema.properties) {
    for (const [field, propSchema] of Object.entries(schema.properties)) {
      if (data[field] !== undefined && data[field] !== null) {
        // Type validation
        if (propSchema.type) {
          const typeErrors = validateType(data[field], propSchema.type, field);
          if (typeErrors) {
            errors.push(typeErrors);
          }
        }
        
        // Format validation
        if (propSchema.format) {
          const formatErrors = validateFormat(data[field], propSchema.format, field);
          if (formatErrors) {
            errors.push(formatErrors);
          }
        }
        
        // Min/max length
        if (propSchema.minLength && typeof data[field] === 'string' && data[field].length < propSchema.minLength) {
          errors.push({
            field,
            message: `${field} must be at least ${propSchema.minLength} characters`
          });
        }
        
        if (propSchema.maxLength && typeof data[field] === 'string' && data[field].length > propSchema.maxLength) {
          errors.push({
            field,
            message: `${field} cannot exceed ${propSchema.maxLength} characters`
          });
        }
        
        // Numeric validations
        if (propSchema.minimum !== undefined && (typeof data[field] === 'number') && data[field] < propSchema.minimum) {
          errors.push({
            field,
            message: `${field} must be at least ${propSchema.minimum}`
          });
        }
        
        if (propSchema.maximum !== undefined && (typeof data[field] === 'number') && data[field] > propSchema.maximum) {
          errors.push({
            field,
            message: `${field} cannot exceed ${propSchema.maximum}`
          });
        }
        
        // Enum validation
        if (propSchema.enum && !propSchema.enum.includes(data[field])) {
          errors.push({
            field,
            message: `${field} must be one of: ${propSchema.enum.join(', ')}`
          });
        }
        
        // Pattern validation
        if (propSchema.pattern && typeof data[field] === 'string') {
          const regex = new RegExp(propSchema.pattern);
          if (!regex.test(data[field])) {
            errors.push({
              field,
              message: propSchema.patternMessage || `${field} format is invalid`
            });
          }
        }
      }
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors: errors
  };
}

/**
 * Validate a value's type
 * @param {*} value - The value to validate
 * @param {string} type - The expected type
 * @param {string} field - Field name for error messages
 * @returns {Object|null} Error object or null if valid
 */
function validateType(value, type, field) {
  switch (type) {
    case 'string':
      if (typeof value !== 'string') {
        return {
          field,
          message: `${field} must be a string`
        };
      }
      break;
      
    case 'number':
      if (typeof value !== 'number' || isNaN(value)) {
        return {
          field,
          message: `${field} must be a number`
        };
      }
      break;
      
    case 'integer':
      if (!Number.isInteger(value)) {
        return {
          field,
          message: `${field} must be an integer`
        };
      }
      break;
      
    case 'boolean':
      if (typeof value !== 'boolean') {
        return {
          field,
          message: `${field} must be a boolean`
        };
      }
      break;
      
    case 'array':
      if (!Array.isArray(value)) {
        return {
          field,
          message: `${field} must be an array`
        };
      }
      break;
      
    case 'object':
      if (typeof value !== 'object' || value === null || Array.isArray(value)) {
        return {
          field,
          message: `${field} must be an object`
        };
      }
      break;
  }
  
  return null;
}

/**
 * Validate a value's format
 * @param {*} value - The value to validate
 * @param {string} format - The expected format
 * @param {string} field - Field name for error messages
 * @returns {Object|null} Error object or null if valid
 */
function validateFormat(value, format, field) {
  switch (format) {
    case 'email':
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (typeof value === 'string' && !emailRegex.test(value)) {
        return {
          field,
          message: `${field} must be a valid email address`
        };
      }
      break;
      
    case 'uri':
    case 'url':
      try {
        new URL(value);
      } catch (e) {
        return {
          field,
          message: `${field} must be a valid URL`
        };
      }
      break;
      
    case 'date':
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      if (typeof value === 'string' && !dateRegex.test(value)) {
        return {
          field,
          message: `${field} must be a valid date in YYYY-MM-DD format`
        };
      }
      break;
      
    case 'date-time':
      // Simple ISO date-time check
      const dateTimeRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$/;
      if (typeof value === 'string' && !dateTimeRegex.test(value)) {
        return {
          field,
          message: `${field} must be a valid ISO date-time`
        };
      }
      break;
  }
  
  return null;
}