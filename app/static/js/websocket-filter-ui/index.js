/**
 * MagnetoCursor - WebSocket Filter UI Components
 * 
 * This module exports components for building and managing WebSocket subscription filters
 * with a user-friendly UI interface.
 */

// Export main components
export { FilterBuilder } from './filter-builder.js';
export { FilterManager } from './filter-manager.js';

// Filter operators and data types
export const FilterOperators = {
  // String operators
  STRING_EQUALS: 'equals',
  STRING_NOT_EQUALS: 'not_equals',
  STRING_CONTAINS: 'contains',
  STRING_NOT_CONTAINS: 'not_contains',
  STRING_STARTS_WITH: 'starts_with',
  STRING_ENDS_WITH: 'ends_with',
  STRING_IN: 'in',
  STRING_NOT_IN: 'not_in',
  STRING_IS_EMPTY: 'is_empty',
  STRING_IS_NOT_EMPTY: 'is_not_empty',
  
  // Number operators
  NUMBER_EQUALS: 'equals',
  NUMBER_NOT_EQUALS: 'not_equals',
  NUMBER_GREATER_THAN: 'greater_than',
  NUMBER_GREATER_THAN_OR_EQUALS: 'greater_than_or_equals',
  NUMBER_LESS_THAN: 'less_than',
  NUMBER_LESS_THAN_OR_EQUALS: 'less_than_or_equals',
  NUMBER_BETWEEN: 'between',
  NUMBER_NOT_BETWEEN: 'not_between',
  NUMBER_IN: 'in',
  NUMBER_NOT_IN: 'not_in',
  NUMBER_IS_EMPTY: 'is_empty',
  NUMBER_IS_NOT_EMPTY: 'is_not_empty',
  
  // Boolean operators
  BOOLEAN_EQUALS: 'equals',
  BOOLEAN_NOT_EQUALS: 'not_equals',
  
  // Date operators
  DATE_EQUALS: 'equals',
  DATE_NOT_EQUALS: 'not_equals',
  DATE_AFTER: 'after',
  DATE_AFTER_OR_EQUALS: 'after_or_equals',
  DATE_BEFORE: 'before',
  DATE_BEFORE_OR_EQUALS: 'before_or_equals',
  DATE_BETWEEN: 'between',
  DATE_NOT_BETWEEN: 'not_between',
  DATE_IS_EMPTY: 'is_empty',
  DATE_IS_NOT_EMPTY: 'is_not_empty',
  
  // Array operators
  ARRAY_CONTAINS: 'contains',
  ARRAY_NOT_CONTAINS: 'not_contains',
  ARRAY_CONTAINS_ANY: 'contains_any',
  ARRAY_CONTAINS_ALL: 'contains_all',
  ARRAY_IS_EMPTY: 'is_empty',
  ARRAY_IS_NOT_EMPTY: 'is_not_empty'
};

// Filter data types
export const FilterDataTypes = {
  STRING: 'string',
  NUMBER: 'number',
  BOOLEAN: 'boolean',
  DATE: 'date',
  ARRAY: 'array'
};

// Logic operators
export const LogicOperators = {
  AND: 'and',
  OR: 'or',
  NOT: 'not'
};

// Filter condition types
export const ConditionTypes = {
  GROUP: 'group',
  CONDITION: 'condition'
};

/**
 * Create an empty filter with default structure
 * @param {string} entityType - Optional entity type
 * @returns {Object} Empty filter object
 */
export function createEmptyFilter(entityType = '') {
  return {
    id: null,
    name: '',
    description: '',
    category: 'General',
    entityType: entityType,
    conditions: {
      type: 'group',
      operator: 'and',
      id: generateId(),
      conditions: []
    }
  };
}

/**
 * Generate a unique ID for filter conditions
 * @returns {string} Unique ID
 */
export function generateId() {
  return `f_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Convert a filter to a backend-compatible format
 * @param {Object} filter - Filter to convert
 * @returns {Object} Backend-compatible filter
 */
export function convertFilterToBackendFormat(filter) {
  if (!filter) return null;
  
  // Clone to avoid modifying original
  const converted = JSON.parse(JSON.stringify(filter));
  
  // Recurse through conditions to format them properly
  if (converted.conditions) {
    converted.conditions = convertConditionGroup(converted.conditions);
  }
  
  return converted;
  
  // Helper function to recursively convert condition groups
  function convertConditionGroup(group) {
    if (!group) return null;
    
    const result = {
      type: group.type,
      operator: group.operator
    };
    
    // Convert child conditions recursively
    if (group.conditions && Array.isArray(group.conditions)) {
      result.conditions = group.conditions.map(condition => {
        if (condition.type === 'group') {
          return convertConditionGroup(condition);
        } else {
          // Format leaf condition
          const convertedCondition = {
            type: 'condition',
            field: condition.field,
            operator: condition.operator
          };
          
          // Handle value based on operator
          if (!['is_empty', 'is_not_empty'].includes(condition.operator)) {
            convertedCondition.value = condition.value;
          }
          
          return convertedCondition;
        }
      });
    }
    
    return result;
  }
}

/**
 * Extract field names used in a filter
 * @param {Object} filter - Filter to analyze
 * @returns {string[]} Array of field names
 */
export function extractFieldsFromFilter(filter) {
  if (!filter || !filter.conditions) return [];
  
  const fields = new Set();
  
  // Recursive function to extract fields
  function extractFields(node) {
    if (node.type === 'condition') {
      if (node.field) {
        fields.add(node.field);
      }
    } else if (node.type === 'group' && node.conditions) {
      node.conditions.forEach(extractFields);
    }
  }
  
  extractFields(filter.conditions);
  return Array.from(fields);
}

/**
 * Get operators available for a specific data type
 * @param {string} dataType - Data type
 * @returns {Object[]} Array of operator objects with id, label, and symbol
 */
export function getOperatorsForDataType(dataType) {
  const operators = {
    string: [
      { id: 'equals', label: 'Equals', symbol: '=' },
      { id: 'not_equals', label: 'Not Equals', symbol: '≠' },
      { id: 'contains', label: 'Contains', symbol: 'contains' },
      { id: 'not_contains', label: 'Not Contains', symbol: 'not contains' },
      { id: 'starts_with', label: 'Starts With', symbol: 'starts with' },
      { id: 'ends_with', label: 'Ends With', symbol: 'ends with' },
      { id: 'in', label: 'In List', symbol: 'in' },
      { id: 'not_in', label: 'Not In List', symbol: 'not in' },
      { id: 'is_empty', label: 'Is Empty', symbol: 'is empty' },
      { id: 'is_not_empty', label: 'Is Not Empty', symbol: 'is not empty' }
    ],
    number: [
      { id: 'equals', label: 'Equals', symbol: '=' },
      { id: 'not_equals', label: 'Not Equals', symbol: '≠' },
      { id: 'greater_than', label: 'Greater Than', symbol: '>' },
      { id: 'greater_than_or_equals', label: 'Greater Than or Equals', symbol: '≥' },
      { id: 'less_than', label: 'Less Than', symbol: '<' },
      { id: 'less_than_or_equals', label: 'Less Than or Equals', symbol: '≤' },
      { id: 'between', label: 'Between', symbol: 'between' },
      { id: 'not_between', label: 'Not Between', symbol: 'not between' },
      { id: 'in', label: 'In List', symbol: 'in' },
      { id: 'not_in', label: 'Not In List', symbol: 'not in' },
      { id: 'is_empty', label: 'Is Empty', symbol: 'is empty' },
      { id: 'is_not_empty', label: 'Is Not Empty', symbol: 'is not empty' }
    ],
    boolean: [
      { id: 'equals', label: 'Equals', symbol: '=' },
      { id: 'not_equals', label: 'Not Equals', symbol: '≠' }
    ],
    date: [
      { id: 'equals', label: 'Equals', symbol: '=' },
      { id: 'not_equals', label: 'Not Equals', symbol: '≠' },
      { id: 'after', label: 'After', symbol: '>' },
      { id: 'after_or_equals', label: 'After or Equals', symbol: '≥' },
      { id: 'before', label: 'Before', symbol: '<' },
      { id: 'before_or_equals', label: 'Before or Equals', symbol: '≤' },
      { id: 'between', label: 'Between', symbol: 'between' },
      { id: 'not_between', label: 'Not Between', symbol: 'not between' },
      { id: 'is_empty', label: 'Is Empty', symbol: 'is empty' },
      { id: 'is_not_empty', label: 'Is Not Empty', symbol: 'is not empty' }
    ],
    array: [
      { id: 'contains', label: 'Contains', symbol: 'contains' },
      { id: 'not_contains', label: 'Not Contains', symbol: 'not contains' },
      { id: 'contains_any', label: 'Contains Any', symbol: 'contains any' },
      { id: 'contains_all', label: 'Contains All', symbol: 'contains all' },
      { id: 'is_empty', label: 'Is Empty', symbol: 'is empty' },
      { id: 'is_not_empty', label: 'Is Not Empty', symbol: 'is not empty' }
    ]
  };
  
  return operators[dataType] || [];
}

/**
 * Validate a filter for completeness and correctness
 * @param {Object} filter - Filter to validate
 * @returns {Object} Validation result with isValid flag and errors array
 */
export function validateFilter(filter) {
  const errors = [];
  
  // Check required metadata
  if (!filter.name || filter.name.trim() === '') {
    errors.push('Filter name is required');
  }
  
  if (!filter.entityType) {
    errors.push('Entity type is required');
  }
  
  // Validate conditions structure
  if (!filter.conditions) {
    errors.push('Filter must have conditions');
  } else {
    // Recursive validation of condition tree
    validateConditionNode(filter.conditions, errors);
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
  
  // Helper function to recursively validate condition nodes
  function validateConditionNode(node, errors) {
    if (!node) {
      errors.push('Empty condition node');
      return;
    }
    
    if (!node.type) {
      errors.push('Condition node missing type');
      return;
    }
    
    if (node.type === 'group') {
      if (!node.operator) {
        errors.push('Group missing operator');
      }
      
      if (!node.conditions || !Array.isArray(node.conditions)) {
        errors.push('Group missing conditions array');
      } else {
        // Validate each child condition
        node.conditions.forEach(child => validateConditionNode(child, errors));
      }
    } else if (node.type === 'condition') {
      if (!node.field) {
        errors.push('Condition missing field');
      }
      
      if (!node.operator) {
        errors.push('Condition missing operator');
      }
      
      // Check if value is required but missing
      if (!['is_empty', 'is_not_empty'].includes(node.operator) && node.value === undefined) {
        errors.push(`Condition for field "${node.field}" with operator "${node.operator}" is missing a value`);
      }
    } else {
      errors.push(`Unknown node type: ${node.type}`);
    }
  }
}
