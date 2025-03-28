/**
 * MagnetoCursor - WebSocket Filter Builder
 * 
 * A visual interface for building complex WebSocket subscription filters
 * with support for nested conditions, multiple operators, and various data types.
 */

export class FilterBuilder {
  /**
   * Initialize the filter builder component
   * @param {HTMLElement} container - The container element
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      darkMode: false,
      availableFields: [],
      filterableEntityTypes: [],
      initialFilter: null,
      onChange: null,
      onSave: null,
      onTest: null,
      maxDepth: 5, // Maximum nesting depth for conditions
      showPreview: true, // Show JSON preview
      ...options
    };
    
    // State
    this.filter = this.options.initialFilter || this._createEmptyFilter();
    this.validationErrors = [];
    this.lastGeneratedId = 0;
    
    // Supported operators by data type
    this.operators = {
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
    
    // Logic operators for groups
    this.logicOperators = [
      { id: 'and', label: 'AND', description: 'All conditions must match' },
      { id: 'or', label: 'OR', description: 'Any condition can match' },
      { id: 'not', label: 'NOT', description: 'Negate the contained conditions' }
    ];
    
    // Initialize the component
    this.initialize();
  }
  
  /**
   * Initialize the component
   */
  initialize() {
    // Add styles
    this._addStyles();
    
    // Render the filter builder
    this._renderFilterBuilder();
    
    // Set up event listeners
    this._setupGlobalEventListeners();
  }
  
  /**
   * Add component styles
   * @private
   */
  _addStyles() {
    if (!document.getElementById('filter-builder-styles')) {
      const style = document.createElement('style');
      style.id = 'filter-builder-styles';
      style.textContent = `
        .ws-filter-builder {
          font-family: var(--font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif);
          color: var(--text-color, #333);
          background: var(--bg-color, #f8f9fa);
          border-radius: 0.25rem;
          border: 1px solid var(--border-color, #dee2e6);
          overflow: hidden;
        }
        
        .ws-filter-builder.dark-mode {
          --bg-color: #212529;
          --text-color: #f8f9fa;
          --border-color: #495057;
          --input-bg: #343a40;
          --input-border: #495057;
          --input-text: #f8f9fa;
          --btn-default-bg: #343a40;
          --btn-default-border: #495057;
          --btn-default-text: #f8f9fa;
          --btn-primary-bg: #0d6efd;
          --btn-primary-border: #0d6efd;
          --btn-primary-text: #fff;
          --btn-danger-bg: #dc3545;
          --btn-danger-border: #dc3545;
          --btn-danger-text: #fff;
          --group-bg: #2c3034;
          --condition-bg: #343a40;
        }
        
        .filter-toolbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          background-color: var(--bg-color, #f8f9fa);
          border-bottom: 1px solid var(--border-color, #dee2e6);
        }
        
        .filter-entity-selector {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .filter-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .filter-content {
          padding: 1rem;
        }
        
        .filter-group {
          border: 1px solid var(--border-color, #dee2e6);
          border-radius: 0.25rem;
          margin-bottom: 1rem;
          background-color: var(--group-bg, #fff);
        }
        
        .filter-group-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem 1rem;
          background-color: var(--bg-color, #f8f9fa);
          border-bottom: 1px solid var(--border-color, #dee2e6);
        }
        
        .filter-group-operator {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .filter-group-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .filter-group-content {
          padding: 1rem;
        }
        
        .filter-condition {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.75rem;
          padding: 0.75rem;
          border-radius: 0.25rem;
          background-color: var(--condition-bg, #f8f9fa);
          border: 1px solid var(--border-color, #dee2e6);
        }
        
        .filter-field-selector {
          flex: 0 0 200px;
        }
        
        .filter-operator-selector {
          flex: 0 0 150px;
        }
        
        .filter-value-input {
          flex: 1;
          min-width: 180px;
        }
        
        .filter-multi-value-container {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          width: 100%;
        }
        
        .filter-multi-value-row {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .filter-value-item {
          flex: 1;
        }
        
        .filter-condition-actions {
          display: flex;
          gap: 0.25rem;
        }
        
        .filter-add-buttons {
          display: flex;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }
        
        .filter-preview {
          margin-top: 1rem;
          border-top: 1px solid var(--border-color, #dee2e6);
          padding-top: 1rem;
        }
        
        .filter-preview-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }
        
        .filter-preview-content {
          padding: 0.75rem;
          border-radius: 0.25rem;
          background-color: var(--input-bg, #f8f9fa);
          border: 1px solid var(--input-border, #dee2e6);
          font-family: monospace;
          font-size: 0.875rem;
          white-space: pre-wrap;
          overflow-x: auto;
          color: var(--input-text, #333);
          max-height: 200px;
          overflow-y: auto;
        }
        
        .filter-validation-errors {
          margin-top: 1rem;
          color: var(--btn-danger-text, #dc3545);
        }
        
        /* Form controls */
        select, input, button {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--input-border, #ced4da);
          border-radius: 0.25rem;
          background-color: var(--input-bg, #fff);
          color: var(--input-text, #333);
          font-size: 0.875rem;
        }
        
        button {
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 0.25rem;
          white-space: nowrap;
          user-select: none;
        }
        
        button:hover {
          opacity: 0.9;
        }
        
        button:active {
          opacity: 0.8;
        }
        
        button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .btn-default {
          background-color: var(--btn-default-bg, #f8f9fa);
          border-color: var(--btn-default-border, #ced4da);
          color: var(--btn-default-text, #333);
        }
        
        .btn-primary {
          background-color: var(--btn-primary-bg, #0d6efd);
          border-color: var(--btn-primary-border, #0d6efd);
          color: var(--btn-primary-text, #fff);
        }
        
        .btn-danger {
          background-color: var(--btn-danger-bg, #dc3545);
          border-color: var(--btn-danger-border, #dc3545);
          color: var(--btn-danger-text, #fff);
        }
        
        .btn-sm {
          padding: 0.25rem 0.5rem;
          font-size: 0.75rem;
        }
        
        .btn-icon {
          width: 28px;
          height: 28px;
          padding: 0;
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }
        
        .filter-help-tooltip {
          position: relative;
          display: inline-block;
        }
        
        .filter-help-tooltip .tooltip-text {
          visibility: hidden;
          width: 200px;
          background-color: #333;
          color: #fff;
          text-align: center;
          border-radius: 6px;
          padding: 5px;
          position: absolute;
          z-index: 1;
          bottom: 125%;
          left: 50%;
          transform: translateX(-50%);
          opacity: 0;
          transition: opacity 0.3s;
          font-size: 0.75rem;
        }
        
        .filter-help-tooltip:hover .tooltip-text {
          visibility: visible;
          opacity: 1;
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Render the filter builder
   * @private
   */
  _renderFilterBuilder() {
    // Create main container
    const builderElement = document.createElement('div');
    builderElement.className = 'ws-filter-builder';
    
    if (this.options.darkMode) {
      builderElement.classList.add('dark-mode');
    }
    
    // Create toolbar
    const toolbar = this._createToolbar();
    builderElement.appendChild(toolbar);
    
    // Create content container
    const content = document.createElement('div');
    content.className = 'filter-content';
    
    // Render root group
    content.appendChild(this._renderFilterGroup(this.filter, 0));
    
    // Add content to builder
    builderElement.appendChild(content);
    
    // Add preview if enabled
    if (this.options.showPreview) {
      const preview = this._createFilterPreview();
      builderElement.appendChild(preview);
    }
    
    // Add validation errors
    const validationErrors = document.createElement('div');
    validationErrors.className = 'filter-validation-errors';
    builderElement.appendChild(validationErrors);
    
    // Clear container and append builder
    this.container.innerHTML = '';
    this.container.appendChild(builderElement);
    
    // Update validation errors
    this._updateValidationErrors();
    
    // Update filter preview
    this._updateFilterPreview();
  }
  
  /**
   * Create toolbar
   * @returns {HTMLElement} Toolbar element
   * @private
   */
  _createToolbar() {
    const toolbar = document.createElement('div');
    toolbar.className = 'filter-toolbar';
    
    // Entity selector
    const entitySelector = document.createElement('div');
    entitySelector.className = 'filter-entity-selector';
    
    const entityLabel = document.createElement('label');
    entityLabel.textContent = 'Entity Type:';
    entitySelector.appendChild(entityLabel);
    
    const entitySelect = document.createElement('select');
    entitySelect.id = 'filter-entity-type';
    
    // Add entity types
    this.options.filterableEntityTypes.forEach(entityType => {
      const option = document.createElement('option');
      option.value = entityType.id;
      option.textContent = entityType.label;
      entitySelect.appendChild(option);
    });
    
    // Set current entity type
    if (this.filter.entityType) {
      entitySelect.value = this.filter.entityType;
    }
    
    entitySelect.addEventListener('change', (e) => {
      this.filter.entityType = e.target.value;
      this._notifyChange();
    });
    
    entitySelector.appendChild(entitySelect);
    toolbar.appendChild(entitySelector);
    
    // Action buttons
    const actions = document.createElement('div');
    actions.className = 'filter-actions';
    
    // Save button
    const saveButton = document.createElement('button');
    saveButton.className = 'btn-primary';
    saveButton.innerHTML = '<i class="fas fa-save"></i> Save Filter';
    saveButton.addEventListener('click', () => {
      this._saveFilter();
    });
    actions.appendChild(saveButton);
    
    // Test button
    const testButton = document.createElement('button');
    testButton.className = 'btn-default';
    testButton.innerHTML = '<i class="fas fa-vial"></i> Test Filter';
    testButton.addEventListener('click', () => {
      this._testFilter();
    });
    actions.appendChild(testButton);
    
    // Clear button
    const clearButton = document.createElement('button');
    clearButton.className = 'btn-danger';
    clearButton.innerHTML = '<i class="fas fa-trash"></i> Clear';
    clearButton.addEventListener('click', () => {
      this._clearFilter();
    });
    actions.appendChild(clearButton);
    
    toolbar.appendChild(actions);
    
    return toolbar;
  }
  
  /**
   * Create filter preview section
   * @returns {HTMLElement} Preview element
   * @private
   */
  _createFilterPreview() {
    const preview = document.createElement('div');
    preview.className = 'filter-preview';
    
    // Preview header
    const header = document.createElement('div');
    header.className = 'filter-preview-header';
    
    const title = document.createElement('h4');
    title.textContent = 'Filter JSON Preview';
    title.style.margin = '0';
    title.style.fontSize = '1rem';
    header.appendChild(title);
    
    const copyButton = document.createElement('button');
    copyButton.className = 'btn-default btn-sm';
    copyButton.innerHTML = '<i class="fas fa-copy"></i> Copy';
    copyButton.addEventListener('click', () => {
      const previewContent = document.querySelector('.filter-preview-content');
      if (previewContent) {
        navigator.clipboard.writeText(previewContent.textContent)
          .then(() => {
            // Temporarily change button text
            const originalText = copyButton.innerHTML;
            copyButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
              copyButton.innerHTML = originalText;
            }, 2000);
          })
          .catch(err => {
            console.error('Failed to copy text: ', err);
          });
      }
    });
    header.appendChild(copyButton);
    
    preview.appendChild(header);
    
    // Preview content
    const content = document.createElement('pre');
    content.className = 'filter-preview-content';
    preview.appendChild(content);
    
    return preview;
  }
  
  /**
   * Render a filter group
   * @param {Object} group - Group to render
   * @param {number} depth - Current nesting depth
   * @returns {HTMLElement} Group element
   * @private
   */
  _renderFilterGroup(group, depth) {
    const groupElement = document.createElement('div');
    groupElement.className = 'filter-group';
    groupElement.dataset.id = group.id;
    
    // Group header
    const header = document.createElement('div');
    header.className = 'filter-group-header';
    
    // Logic operator selector
    const operatorContainer = document.createElement('div');
    operatorContainer.className = 'filter-group-operator';
    
    const operatorLabel = document.createElement('label');
    operatorLabel.textContent = depth === 0 ? 'Root Group:' : 'Logic:';
    operatorContainer.appendChild(operatorLabel);
    
    const operatorSelect = document.createElement('select');
    operatorSelect.dataset.groupId = group.id;
    
    this.logicOperators.forEach(operator => {
      const option = document.createElement('option');
      option.value = operator.id;
      option.textContent = operator.label;
      option.title = operator.description;
      operatorSelect.appendChild(option);
    });
    
    // Set current operator
    operatorSelect.value = group.operator || 'and';
    
    operatorSelect.addEventListener('change', (e) => {
      this._updateGroupOperator(group.id, e.target.value);
    });
    
    operatorContainer.appendChild(operatorSelect);
    
    // Help tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'filter-help-tooltip';
    tooltip.innerHTML = '<i class="fas fa-question-circle"></i>';
    
    const tooltipText = document.createElement('span');
    tooltipText.className = 'tooltip-text';
    
    // Get current operator description
    const currentOperator = this.logicOperators.find(op => op.id === (group.operator || 'and'));
    tooltipText.textContent = currentOperator ? currentOperator.description : '';
    
    // Update tooltip text when operator changes
    operatorSelect.addEventListener('change', (e) => {
      const newOperator = this.logicOperators.find(op => op.id === e.target.value);
      if (newOperator) {
        tooltipText.textContent = newOperator.description;
      }
    });
    
    tooltip.appendChild(tooltipText);
    operatorContainer.appendChild(tooltip);
    
    header.appendChild(operatorContainer);
    
    // Group actions
    const actionsContainer = document.createElement('div');
    actionsContainer.className = 'filter-group-actions';
    
    // Only show remove button if not root group
    if (depth > 0) {
      const removeButton = document.createElement('button');
      removeButton.className = 'btn-danger btn-sm';
      removeButton.innerHTML = '<i class="fas fa-times"></i> Remove Group';
      removeButton.addEventListener('click', () => {
        this._removeGroup(group.id);
      });
      actionsContainer.appendChild(removeButton);
    }
    
    header.appendChild(actionsContainer);
    groupElement.appendChild(header);
    
    // Group content
    const content = document.createElement('div');
    content.className = 'filter-group-content';
    
    // Render conditions
    if (group.conditions && group.conditions.length > 0) {
      group.conditions.forEach(condition => {
        if (condition.type === 'group') {
          // Render nested group if depth allows
          if (depth < this.options.maxDepth) {
            content.appendChild(this._renderFilterGroup(condition, depth + 1));
          } else {
            console.warn('Maximum nesting depth reached, not rendering nested group');
          }
        } else {
          // Render condition
          content.appendChild(this._renderFilterCondition(condition));
        }
      });
    } else {
      // Empty message
      const emptyMessage = document.createElement('div');
      emptyMessage.className = 'filter-empty-message';
      emptyMessage.textContent = 'No conditions added yet. Use the buttons below to add conditions.';
      emptyMessage.style.opacity = '0.6';
      emptyMessage.style.fontStyle = 'italic';
      emptyMessage.style.marginBottom = '1rem';
      content.appendChild(emptyMessage);
    }
    
    // Add condition/group buttons
    const addButtons = document.createElement('div');
    addButtons.className = 'filter-add-buttons';
    
    const addConditionButton = document.createElement('button');
    addConditionButton.className = 'btn-default';
    addConditionButton.innerHTML = '<i class="fas fa-plus"></i> Add Condition';
    addConditionButton.addEventListener('click', () => {
      this._addCondition(group.id);
    });
    addButtons.appendChild(addConditionButton);
    
    // Only show add group button if depth allows
    if (depth < this.options.maxDepth) {
      const addGroupButton = document.createElement('button');
      addGroupButton.className = 'btn-default';
      addGroupButton.innerHTML = '<i class="fas fa-object-group"></i> Add Group';
      addGroupButton.addEventListener('click', () => {
        this._addGroup(group.id);
      });
      addButtons.appendChild(addGroupButton);
    }
    
    content.appendChild(addButtons);
    groupElement.appendChild(content);
    
    return groupElement;
  }
  
  /**
   * Render a filter condition
   * @param {Object} condition - Condition to render
   * @returns {HTMLElement} Condition element
   * @private
   */
  _renderFilterCondition(condition) {
    const conditionElement = document.createElement('div');
    conditionElement.className = 'filter-condition';
    conditionElement.dataset.id = condition.id;
    
    // Field selector
    const fieldSelector = document.createElement('select');
    fieldSelector.className = 'filter-field-selector';
    fieldSelector.dataset.conditionId = condition.id;
    
    // Add empty option
    const emptyOption = document.createElement('option');
    emptyOption.value = '';
    emptyOption.textContent = '-- Select Field --';
    fieldSelector.appendChild(emptyOption);
    
    // Add available fields
    this.options.availableFields.forEach(field => {
      const option = document.createElement('option');
      option.value = field.id;
      option.textContent = field.label;
      option.dataset.type = field.type;
      fieldSelector.appendChild(option);
    });
    
    // Set current field
    if (condition.field) {
      fieldSelector.value = condition.field;
    }
    
    fieldSelector.addEventListener('change', (e) => {
      // Get field type from selected option
      const selectedOption = e.target.options[e.target.selectedIndex];
      const fieldType = selectedOption.dataset.type;
      
      this._updateConditionField(condition.id, e.target.value, fieldType);
    });
    
    conditionElement.appendChild(fieldSelector);
    
    // Operator selector
    const operatorSelector = document.createElement('select');
    operatorSelector.className = 'filter-operator-selector';
    operatorSelector.dataset.conditionId = condition.id;
    
    // Add operators based on field type
    const fieldType = this._getFieldType(condition.field);
    
    if (fieldType) {
      // Get operators for this field type
      const fieldOperators = this.operators[fieldType] || [];
      
      fieldOperators.forEach(operator => {
        const option = document.createElement('option');
        option.value = operator.id;
        option.textContent = operator.label;
        operatorSelector.appendChild(option);
      });
      
      // Set current operator if valid for this field type
      if (condition.operator && fieldOperators.some(op => op.id === condition.operator)) {
        operatorSelector.value = condition.operator;
      } else if (fieldOperators.length > 0) {
        // Set first available operator
        operatorSelector.value = fieldOperators[0].id;
        condition.operator = fieldOperators[0].id;
      }
    } else {
      // Add placeholder option
      const placeholderOption = document.createElement('option');
      placeholderOption.value = '';
      placeholderOption.textContent = '-- Select Field First --';
      operatorSelector.appendChild(placeholderOption);
      operatorSelector.disabled = true;
    }
    
    operatorSelector.addEventListener('change', (e) => {
      this._updateConditionOperator(condition.id, e.target.value);
    });
    
    conditionElement.appendChild(operatorSelector);
    
    // Value input(s) based on operator and field type
    const valueContainer = this._createValueInput(condition, fieldType);
    conditionElement.appendChild(valueContainer);
    
    // Condition actions
    const actionsContainer = document.createElement('div');
    actionsContainer.className = 'filter-condition-actions';
    
    const removeButton = document.createElement('button');
    removeButton.className = 'btn-danger btn-sm btn-icon';
    removeButton.innerHTML = '<i class="fas fa-times"></i>';
    removeButton.title = 'Remove Condition';
    removeButton.addEventListener('click', () => {
      this._removeCondition(condition.id);
    });
    actionsContainer.appendChild(removeButton);
    
    conditionElement.appendChild(actionsContainer);
    
    return conditionElement;
  }
  
  /**
   * Create value input(s) based on operator and field type
   * @param {Object} condition - Condition object
   * @param {string} fieldType - Field data type
   * @returns {HTMLElement} Value input container
   * @private
   */
  _createValueInput(condition, fieldType) {
    const container = document.createElement('div');
    container.className = 'filter-value-input';
    
    // Skip value input for operators that don't need values
    const noValueOperators = ['is_empty', 'is_not_empty'];
    
    if (condition.operator && noValueOperators.includes(condition.operator)) {
      container.innerHTML = '<div class="text-muted">(No value needed)</div>';
      return container;
    }
    
    // Special case for between operators
    const betweenOperators = ['between', 'not_between'];
    if (condition.operator && betweenOperators.includes(condition.operator)) {
      const multiValueContainer = document.createElement('div');
      multiValueContainer.className = 'filter-multi-value-container';
      
      // Min value
      const minValueRow = document.createElement('div');
      minValueRow.className = 'filter-multi-value-row';
      
      const minValueLabel = document.createElement('div');
      minValueLabel.textContent = 'Min:';
      minValueLabel.style.width = '50px';
      minValueRow.appendChild(minValueLabel);
      
      const minValueInput = this._createInputForType(fieldType, condition, 'value_min');
      minValueInput.className += ' filter-value-item';
      minValueRow.appendChild(minValueInput);
      
      multiValueContainer.appendChild(minValueRow);
      
      // Max value
      const maxValueRow = document.createElement('div');
      maxValueRow.className = 'filter-multi-value-row';
      
      const maxValueLabel = document.createElement('div');
      maxValueLabel.textContent = 'Max:';
      maxValueLabel.style.width = '50px';
      maxValueRow.appendChild(maxValueLabel);
      
      const maxValueInput = this._createInputForType(fieldType, condition, 'value_max');
      maxValueInput.className += ' filter-value-item';
      maxValueRow.appendChild(maxValueInput);
      
      multiValueContainer.appendChild(maxValueRow);
      
      container.appendChild(multiValueContainer);
      return container;
    }
    
    // Special case for in/not_in operators (list of values)
    const listOperators = ['in', 'not_in', 'contains_any', 'contains_all'];
    if (condition.operator && listOperators.includes(condition.operator)) {
      const multiValueContainer = document.createElement('div');
      multiValueContainer.className = 'filter-multi-value-container';
      
      // Current values
      const values = Array.isArray(condition.value) ? condition.value : 
                    (condition.value ? [condition.value] : []);
      
      // Add at least one value input
      if (values.length === 0) {
        values.push('');
      }
      
      // Create inputs for each value
      values.forEach((value, index) => {
        const valueRow = document.createElement('div');
        valueRow.className = 'filter-multi-value-row';
        
        const valueInput = this._createInputForType(fieldType, { ...condition, value }, 'value');
        valueInput.className += ' filter-value-item';
        valueInput.dataset.index = index;
        
        valueInput.addEventListener('change', (e) => {
          this._updateListValue(condition.id, index, e.target.value, fieldType);
        });
        
        valueRow.appendChild(valueInput);
        
        // Remove button
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn-danger btn-sm btn-icon';
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.title = 'Remove Value';
        removeBtn.dataset.index = index;
        
        removeBtn.addEventListener('click', () => {
          this._removeListValue(condition.id, index);
        });
        
        valueRow.appendChild(removeBtn);
        multiValueContainer.appendChild(valueRow);
      });
      
      // Add value button
      const addValueBtn = document.createElement('button');
      addValueBtn.className = 'btn-default btn-sm';
      addValueBtn.innerHTML = '<i class="fas fa-plus"></i> Add Value';
      addValueBtn.addEventListener('click', () => {
        this._addListValue(condition.id);
      });
      
      multiValueContainer.appendChild(addValueBtn);
      container.appendChild(multiValueContainer);
      return container;
    }
    
    // Standard single value input
    const input = this._createInputForType(fieldType, condition, 'value');
    container.appendChild(input);
    
    return container;
  }
  
  /**
   * Create an input element appropriate for the field type
   * @param {string} fieldType - Field data type
   * @param {Object} condition - Condition object
   * @param {string} valueProp - Property name for value in condition object
   * @returns {HTMLElement} - Input element
   * @private
   */
  _createInputForType(fieldType, condition, valueProp = 'value') {
    let input;
    
    switch (fieldType) {
      case 'boolean':
        // Create a select for boolean values
        input = document.createElement('select');
        input.className = 'form-control';
        
        const trueOption = document.createElement('option');
        trueOption.value = 'true';
        trueOption.textContent = 'True';
        input.appendChild(trueOption);
        
        const falseOption = document.createElement('option');
        falseOption.value = 'false';
        falseOption.textContent = 'False';
        input.appendChild(falseOption);
        
        // Set current value
        input.value = condition[valueProp] === true || condition[valueProp] === 'true' ? 'true' : 'false';
        break;
        
      case 'number':
        // Create number input
        input = document.createElement('input');
        input.type = 'number';
        input.className = 'form-control';
        input.step = 'any'; // Allow any number (including decimals)
        
        // Set current value
        if (condition[valueProp] !== undefined && condition[valueProp] !== null) {
          input.value = condition[valueProp];
        }
        break;
        
      case 'date':
        // Create date input
        input = document.createElement('input');
        input.type = 'date';
        input.className = 'form-control';
        
        // Set current value
        if (condition[valueProp]) {
          // Format date YYYY-MM-DD
          const dateValue = new Date(condition[valueProp]);
          if (!isNaN(dateValue.getTime())) {
            input.value = dateValue.toISOString().split('T')[0];
          }
        }
        break;
        
      default:
        // Default to text input for string and other types
        input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control';
        
        // Set current value
        if (condition[valueProp] !== undefined && condition[valueProp] !== null) {
          input.value = condition[valueProp];
        }
        break;
    }
    
    // Add data attribute for condition ID and property
    input.dataset.conditionId = condition.id;
    input.dataset.valueProp = valueProp;
    
    // Add change event listener
    input.addEventListener('change', (e) => {
      // Convert value based on field type
      let value = e.target.value;
      
      if (fieldType === 'number') {
        value = value !== '' ? Number(value) : null;
      } else if (fieldType === 'boolean') {
        value = value === 'true';
      }
      
      // Update condition
      this._updateConditionValue(condition.id, value, valueProp);
    });
    
    return input;
  }
  
  /**
   * Update a condition's value
   * @param {string} conditionId - Condition ID
   * @param {any} value - New value
   * @param {string} valueProp - Value property name
   * @private
   */
  _updateConditionValue(conditionId, value, valueProp = 'value') {
    // Find condition in filter
    this._findAndUpdateCondition(this.filter, conditionId, (condition) => {
      condition[valueProp] = value;
    });
    
    // Notify of change
    this._notifyChange();
  }
  
  /**
   * Update a list value
   * @param {string} conditionId - Condition ID
   * @param {number} index - Value index
   * @param {any} value - New value
   * @param {string} fieldType - Field type for value conversion
   * @private
   */
  _updateListValue(conditionId, index, value, fieldType) {
    // Find condition in filter
    this._findAndUpdateCondition(this.filter, conditionId, (condition) => {
      // Ensure value is an array
      if (!Array.isArray(condition.value)) {
        condition.value = condition.value !== undefined && condition.value !== null ? 
                          [condition.value] : [];
      }
      
      // Convert value based on field type
      if (fieldType === 'number') {
        value = value !== '' ? Number(value) : null;
      } else if (fieldType === 'boolean') {
        value = value === 'true';
      }
      
      // Update value at index
      condition.value[index] = value;
    });
    
    // Notify of change
    this._notifyChange();
  }
  
  /**
   * Add an empty value to a list
   * @param {string} conditionId - Condition ID
   * @private
   */
  _addListValue(conditionId) {
    // Find condition in filter
    this._findAndUpdateCondition(this.filter, conditionId, (condition) => {
      // Ensure value is an array
      if (!Array.isArray(condition.value)) {
        condition.value = condition.value !== undefined && condition.value !== null ? 
                          [condition.value] : [];
      }
      
      // Add empty value
      condition.value.push('');
    });
    
    // Rebuild UI
    this._renderFilterBuilder();
  }
  
  /**
   * Remove a value from a list
   * @param {string} conditionId - Condition ID
   * @param {number} index - Value index
   * @private
   */
  _removeListValue(conditionId, index) {
    // Find condition in filter
    this._findAndUpdateCondition(this.filter, conditionId, (condition) => {
      // Ensure value is an array
      if (!Array.isArray(condition.value)) {
        condition.value = [];
        return;
      }
      
      // Remove value at index
      condition.value.splice(index, 1);
      
      // Ensure at least one value for UI
      if (condition.value.length === 0) {
        condition.value.push('');
      }
    });
    
    // Rebuild UI
    this._renderFilterBuilder();
  }
  
  /**
   * Find and update a condition by ID in the filter structure
   * @param {Object} group - Current group to search in
   * @param {string} conditionId - Condition ID to find
   * @param {Function} updateFn - Function to call with found condition
   * @returns {boolean} - Whether condition was found and updated
   * @private
   */
  _findAndUpdateCondition(group, conditionId, updateFn) {
    if (!group || !group.conditions) {
      return false;
    }
    
    for (let i = 0; i < group.conditions.length; i++) {
      const condition = group.conditions[i];
      
      if (condition.id === conditionId) {
        updateFn(condition);
        return true;
      }
      
      // Check nested groups
      if (condition.type === 'group') {
        if (this._findAndUpdateCondition(condition, conditionId, updateFn)) {
          return true;
        }
      }
    }
    
    return false;
  }
  
  /**
   * Find and update a group by ID in the filter structure
   * @param {Object} parent - Current parent group to search in
   * @param {string} groupId - Group ID to find
   * @param {Function} updateFn - Function to call with found group
   * @returns {boolean} - Whether group was found and updated
   * @private
   */
  _findAndUpdateGroup(parent, groupId, updateFn) {
    if (!parent || !parent.conditions) {
      return false;
    }
    
    // Check if this is the group we're looking for
    if (parent.id === groupId) {
      updateFn(parent);
      return true;
    }
    
    // Check children
    for (let i = 0; i < parent.conditions.length; i++) {
      const condition = parent.conditions[i];
      
      if (condition.type === 'group') {
        if (this._findAndUpdateGroup(condition, groupId, updateFn)) {
          return true;
        }
      }
    }
    
    return false;
  }
  
  /**
   * Find the parent group of a condition or group
   * @param {Object} group - Current group to search in
   * @param {string} id - Condition or group ID to find
   * @returns {Object|null} - Parent group or null if not found
   * @private
   */
  _findParent(group, id) {
    if (!group || !group.conditions) {
      return null;
    }
    
    for (let i = 0; i < group.conditions.length; i++) {
      const condition = group.conditions[i];
      
      if (condition.id === id) {
        return group;
      }
      
      if (condition.type === 'group') {
        const parent = this._findParent(condition, id);
        if (parent) {
          return parent;
        }
      }
    }
    
    return null;
  }
  
  /**
   * Update the operator of a group
   * @param {string} groupId - Group ID
   * @param {string} operator - New operator
   * @private
   */
  _updateGroupOperator(groupId, operator) {
    this._findAndUpdateGroup(this.filter, groupId, (group) => {
      group.operator = operator;
    });
    
    this._notifyChange();
  }
  
  /**
   * Update the field of a condition
   * @param {string} conditionId - Condition ID
   * @param {string} field - New field ID
   * @param {string} fieldType - Field data type
   * @private
   */
  _updateConditionField(conditionId, field, fieldType) {
    this._findAndUpdateCondition(this.filter, conditionId, (condition) => {
      // Update field
      condition.field = field;
      condition.fieldType = fieldType;
      
      // Reset operator and value
      condition.operator = this._getDefaultOperatorForType(fieldType);
      condition.value = this._getDefaultValueForType(fieldType);
    });
    
    // Rebuild UI to update operators and value inputs
    this._renderFilterBuilder();
  }
  
  /**
   * Update the operator of a condition
   * @param {string} conditionId - Condition ID
   * @param {string} operator - New operator
   * @private
   */
  _updateConditionOperator(conditionId, operator) {
    this._findAndUpdateCondition(this.filter, conditionId, (condition) => {
      // Update operator
      condition.operator = operator;
      
      // Reset value based on operator type
      const fieldType = this._getFieldType(condition.field);
      
      // For operators that handle lists, convert value to array
      const listOperators = ['in', 'not_in', 'contains_any', 'contains_all'];
      if (listOperators.includes(operator)) {
        condition.value = Array.isArray(condition.value) ? condition.value : 
                       (condition.value !== undefined && condition.value !== null ? [condition.value] : ['']);
      }
      
      // For between operators, set value_min and value_max
      const betweenOperators = ['between', 'not_between'];
      if (betweenOperators.includes(operator)) {
        condition.value_min = condition.value_min || this._getDefaultValueForType(fieldType);
        condition.value_max = condition.value_max || this._getDefaultValueForType(fieldType);
      }
      
      // For operators without values, clear value
      const noValueOperators = ['is_empty', 'is_not_empty'];
      if (noValueOperators.includes(operator)) {
        condition.value = undefined;
      }
    });
    
    // Rebuild UI to update value inputs
    this._renderFilterBuilder();
  }
  
  /**
   * Add a new condition to a group
   * @param {string} groupId - Group ID
   * @private
   */
  _addCondition(groupId) {
    this._findAndUpdateGroup(this.filter, groupId, (group) => {
      // Create new condition
      const condition = {
        id: `condition_${++this.lastGeneratedId}`,
        type: 'condition',
        field: '',
        operator: '',
        value: ''
      };
      
      // Add to group
      if (!group.conditions) {
        group.conditions = [];
      }
      
      group.conditions.push(condition);
    });
    
    // Rebuild UI
    this._renderFilterBuilder();
  }
  
  /**
   * Add a new group to a parent group
   * @param {string} parentId - Parent group ID
   * @private
   */
  _addGroup(parentId) {
    this._findAndUpdateGroup(this.filter, parentId, (parent) => {
      // Create new group
      const group = {
        id: `group_${++this.lastGeneratedId}`,
        type: 'group',
        operator: 'and',
        conditions: []
      };
      
      // Add to parent
      if (!parent.conditions) {
        parent.conditions = [];
      }
      
      parent.conditions.push(group);
    });
    
    // Rebuild UI
    this._renderFilterBuilder();
  }
  
  /**
   * Remove a condition
   * @param {string} conditionId - Condition ID
   * @private
   */
  _removeCondition(conditionId) {
    const parent = this._findParent(this.filter, conditionId);
    
    if (parent) {
      parent.conditions = parent.conditions.filter(c => c.id !== conditionId);
      this._renderFilterBuilder();
      this._notifyChange();
    }
  }
  
  /**
   * Remove a group
   * @param {string} groupId - Group ID
   * @private
   */
  _removeGroup(groupId) {
    const parent = this._findParent(this.filter, groupId);
    
    if (parent) {
      parent.conditions = parent.conditions.filter(c => c.id !== groupId);
      this._renderFilterBuilder();
      this._notifyChange();
    }
  }
  
  /**
   * Get the default operator for a field type
   * @param {string} fieldType - Field type
   * @returns {string} - Default operator
   * @private
   */
  _getDefaultOperatorForType(fieldType) {
    if (!fieldType) {
      return '';
    }
    
    const operators = this.operators[fieldType] || [];
    return operators.length > 0 ? operators[0].id : '';
  }
  
  /**
   * Get the default value for a field type
   * @param {string} fieldType - Field type
   * @returns {any} - Default value
   * @private
   */
  _getDefaultValueForType(fieldType) {
    switch (fieldType) {
      case 'number':
        return 0;
      case 'boolean':
        return false;
      case 'date':
        return new Date().toISOString().split('T')[0]; // Today
      default:
        return '';
    }
  }
  
  /**
   * Get the field type for a field ID
   * @param {string} fieldId - Field ID
   * @returns {string|null} - Field type or null if not found
   * @private
   */
  _getFieldType(fieldId) {
    if (!fieldId) {
      return null;
    }
    
    const field = this.options.availableFields.find(f => f.id === fieldId);
    return field ? field.type : null;
  }
  
  /**
   * Create an empty filter
   * @returns {Object} - Empty filter
   * @private
   */
  _createEmptyFilter() {
    return {
      id: `filter_${++this.lastGeneratedId}`,
      type: 'group',
      operator: 'and',
      conditions: [],
      entityType: this.options.filterableEntityTypes.length > 0 ? 
                 this.options.filterableEntityTypes[0].id : null
    };
  }
  
  /**
   * Update filter preview
   * @private
   */
  _updateFilterPreview() {
    if (!this.options.showPreview) {
      return;
    }
    
    const previewContent = document.querySelector('.filter-preview-content');
    if (previewContent) {
      previewContent.textContent = JSON.stringify(this.filter, null, 2);
    }
  }
  
  /**
   * Update validation errors display
   * @private
   */
  _updateValidationErrors() {
    const errorsContainer = document.querySelector('.filter-validation-errors');
    if (!errorsContainer) {
      return;
    }
    
    if (this.validationErrors.length > 0) {
      let errorHtml = '<ul class="mb-0">';
      this.validationErrors.forEach(error => {
        errorHtml += `<li>${error}</li>`;
      });
      errorHtml += '</ul>';
      
      errorsContainer.innerHTML = errorHtml;
      errorsContainer.style.display = 'block';
    } else {
      errorsContainer.innerHTML = '';
      errorsContainer.style.display = 'none';
    }
  }
  
  /**
   * Validate the current filter
   * @returns {boolean} - Whether the filter is valid
   * @private
   */
  _validateFilter() {
    this.validationErrors = [];
    
    // No entity type
    if (!this.filter.entityType) {
      this.validationErrors.push('Please select an entity type.');
    }
    
    // Validate conditions
    const validationResult = this._validateGroup(this.filter);
    if (!validationResult.valid) {
      this.validationErrors.push(...validationResult.errors);
    }
    
    // Update validation errors display
    this._updateValidationErrors();
    
    return this.validationErrors.length === 0;
  }
  
  /**
   * Validate a group and its conditions
   * @param {Object} group - Group to validate
   * @param {number} depth - Current depth level
   * @returns {Object} - Validation result
   * @private
   */
  _validateGroup(group, depth = 0) {
    const errors = [];
    
    // Check if group has conditions
    if (!group.conditions || group.conditions.length === 0) {
      return { valid: true, errors: [] }; // Empty groups are valid
    }
    
    // Check each condition
    for (const condition of group.conditions) {
      if (condition.type === 'condition') {
        // Validate condition
        if (!condition.field) {
          errors.push(`A condition is missing a field.`);
        } else if (!condition.operator) {
          errors.push(`Condition with field "${condition.field}" is missing an operator.`);
        } else {
          const noValueOperators = ['is_empty', 'is_not_empty'];
          const betweenOperators = ['between', 'not_between'];
          const listOperators = ['in', 'not_in', 'contains_any', 'contains_all'];
          
          // Validate value based on operator type
          if (!noValueOperators.includes(condition.operator)) {
            if (betweenOperators.includes(condition.operator)) {
              // Check min and max values
              if (condition.value_min === undefined || condition.value_min === null) {
                errors.push(`Condition with field "${condition.field}" is missing a minimum value.`);
              }
              
              if (condition.value_max === undefined || condition.value_max === null) {
                errors.push(`Condition with field "${condition.field}" is missing a maximum value.`);
              }
            } else if (listOperators.includes(condition.operator)) {
              // Check list value
              if (!Array.isArray(condition.value) || condition.value.length === 0) {
                errors.push(`Condition with field "${condition.field}" requires at least one value.`);
              }
            } else if (condition.value === undefined || condition.value === null || condition.value === '') {
              errors.push(`Condition with field "${condition.field}" is missing a value.`);
            }
          }
        }
      } else if (condition.type === 'group') {
        // Validate nested group
        const result = this._validateGroup(condition, depth + 1);
        if (!result.valid) {
          errors.push(...result.errors);
        }
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  /**
   * Notify of filter changes
   * @private
   */
  _notifyChange() {
    // Update preview
    this._updateFilterPreview();
    
    // Call onChange callback if provided
    if (typeof this.options.onChange === 'function') {
      this.options.onChange(this.filter);
    }
  }
  
  /**
   * Setup global event listeners
   * @private
   */
  _setupGlobalEventListeners() {
    // No global event listeners needed at this time
  }
  
  /**
   * Save the current filter
   * @private
   */
  _saveFilter() {
    // Validate filter
    if (!this._validateFilter()) {
      return;
    }
    
    // Call onSave callback if provided
    if (typeof this.options.onSave === 'function') {
      this.options.onSave(this.filter);
    }
  }
  
  /**
   * Test the current filter
   * @private
   */
  _testFilter() {
    // Validate filter
    if (!this._validateFilter()) {
      return;
    }
    
    // Call onTest callback if provided
    if (typeof this.options.onTest === 'function') {
      this.options.onTest(this.filter);
    }
  }
  
  /**
   * Clear the filter (reset to empty)
   * @private
   */
  _clearFilter() {
    this.filter = this._createEmptyFilter();
    this._renderFilterBuilder();
    this._notifyChange();
  }
  
  /**
   * Get the current filter
   * @returns {Object} - Current filter
   */
  getFilter() {
    return this.filter;
  }
  
  /**
   * Set a new filter
   * @param {Object} filter - New filter
   */
  setFilter(filter) {
    this.filter = filter || this._createEmptyFilter();
    this._renderFilterBuilder();
    this._notifyChange();
  }
