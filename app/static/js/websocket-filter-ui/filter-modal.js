/**
 * WebSocket Filter Modal Component
 * 
 * Provides modal dialog functionality for creating, editing, and duplicating filters
 */

export class FilterModal {
  /**
   * Initialize a new filter modal
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = {
      onSave: null,
      categories: ['General', 'Campaigns', 'Notifications', 'Alerts', 'Custom'],
      fields: [],
      entityTypes: [],
      ...options
    };
    
    this.modalElement = null;
    this.isVisible = false;
    this.editMode = false;
    this.currentFilter = null;
    
    this._createModal();
    this._setupEvents();
  }
  
  /**
   * Show the modal for creating a new filter
   * @param {Object} initialData - Initial data for the filter (optional)
   */
  showCreateModal(initialData = {}) {
    this.editMode = false;
    this.currentFilter = initialData;
    
    const titleElement = this.modalElement.querySelector('.filter-modal-title');
    if (titleElement) {
      titleElement.textContent = 'Create New Filter';
    }
    
    this._populateForm(initialData);
    this._show();
  }
  
  /**
   * Show the modal for editing an existing filter
   * @param {Object} filter - Filter to edit
   */
  showEditModal(filter) {
    if (!filter || !filter.id) {
      console.error('Invalid filter object provided for editing');
      return;
    }
    
    this.editMode = true;
    this.currentFilter = filter;
    
    const titleElement = this.modalElement.querySelector('.filter-modal-title');
    if (titleElement) {
      titleElement.textContent = 'Edit Filter';
    }
    
    this._populateForm(filter);
    this._show();
  }
  
  /**
   * Show the modal for duplicating a filter
   * @param {Object} filter - Filter to duplicate
   */
  showDuplicateModal(filter) {
    if (!filter) {
      console.error('Invalid filter object provided for duplication');
      return;
    }
    
    // Create a copy with a different name
    const duplicatedFilter = {
      ...filter,
      id: null, // Will be generated on save
      name: `${filter.name} (Copy)`,
    };
    
    this.editMode = false;
    this.currentFilter = duplicatedFilter;
    
    const titleElement = this.modalElement.querySelector('.filter-modal-title');
    if (titleElement) {
      titleElement.textContent = 'Duplicate Filter';
    }
    
    this._populateForm(duplicatedFilter);
    this._show();
  }
  
  /**
   * Hide the modal
   */
  hide() {
    if (this.modalElement) {
      this.modalElement.classList.remove('active');
      document.body.classList.remove('modal-open');
      this.isVisible = false;
    }
  }
  
  /**
   * Create the modal element
   * @private
   */
  _createModal() {
    // Create modal container if it doesn't exist
    if (!this.modalElement) {
      this.modalElement = document.createElement('div');
      this.modalElement.className = 'filter-modal';
      this.modalElement.innerHTML = `
        <div class="filter-modal-backdrop"></div>
        <div class="filter-modal-container">
          <div class="filter-modal-header">
            <h3 class="filter-modal-title">Create New Filter</h3>
            <button class="filter-modal-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="filter-modal-body">
            <form id="filterForm">
              <div class="form-group">
                <label for="filterName">Filter Name</label>
                <input type="text" id="filterName" name="name" class="form-control" required placeholder="Enter a descriptive name">
              </div>
              
              <div class="form-group">
                <label for="filterCategory">Category</label>
                <select id="filterCategory" name="category" class="form-control">
                  ${this.options.categories.map(category => 
                    `<option value="${category.toLowerCase()}">${category}</option>`
                  ).join('')}
                </select>
              </div>
              
              <div class="form-group">
                <label for="filterDescription">Description</label>
                <textarea id="filterDescription" name="description" class="form-control" placeholder="Describe the purpose of this filter"></textarea>
              </div>
              
              <div class="filter-definition-section">
                <h4>Filter Definition</h4>
                <div class="filter-definition-container">
                  <div class="entity-type-selector">
                    <label for="entityType">Entity Type</label>
                    <select id="entityType" name="entityType" class="form-control">
                      <option value="">Select entity type...</option>
                      ${this.options.entityTypes.map(type => 
                        `<option value="${type.id}">${type.name}</option>`
                      ).join('')}
                    </select>
                  </div>
                  
                  <div class="condition-builder">
                    <!-- Condition builder content will be rendered here dynamically -->
                    <div class="condition-placeholder">
                      <p>Select an entity type to start building filter conditions</p>
                    </div>
                  </div>
                </div>
              </div>
            </form>
          </div>
          
          <div class="filter-modal-footer">
            <button class="btn-cancel">Cancel</button>
            <button class="btn-primary" id="saveFilterBtn">Save Filter</button>
          </div>
        </div>
      `;
      
      // Add the modal to the document body
      document.body.appendChild(this.modalElement);
      
      // Add necessary styles
      this._addStyles();
    }
  }
  
  /**
   * Add modal styles to document
   * @private
   */
  _addStyles() {
    if (!document.getElementById('filter-modal-styles')) {
      const style = document.createElement('style');
      style.id = 'filter-modal-styles';
      style.textContent = `
        .filter-modal {
          display: none;
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          z-index: 9999;
        }
        
        .filter-modal.active {
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .filter-modal-backdrop {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-color: rgba(0, 0, 0, 0.5);
        }
        
        .filter-modal-container {
          position: relative;
          width: 90%;
          max-width: 700px;
          max-height: 90vh;
          background-color: var(--bg-color, #fff);
          border-radius: 0.25rem;
          box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }
        
        .filter-modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid var(--border-color, #dee2e6);
        }
        
        .filter-modal-title {
          margin: 0;
          font-size: 1.25rem;
          font-weight: 600;
        }
        
        .filter-modal-close {
          background: none;
          border: none;
          font-size: 1.25rem;
          cursor: pointer;
          opacity: 0.5;
          transition: opacity 0.2s;
        }
        
        .filter-modal-close:hover {
          opacity: 1;
        }
        
        .filter-modal-body {
          padding: 1rem;
          overflow-y: auto;
          flex-grow: 1;
        }
        
        .filter-modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 0.5rem;
          padding: 1rem;
          border-top: 1px solid var(--border-color, #dee2e6);
        }
        
        .filter-definition-section {
          margin-top: 1.5rem;
        }
        
        .filter-definition-container {
          border: 1px solid var(--border-color, #dee2e6);
          border-radius: 0.25rem;
          padding: 1rem;
        }
        
        .entity-type-selector {
          margin-bottom: 1rem;
        }
        
        .condition-placeholder {
          padding: 2rem;
          text-align: center;
          color: var(--text-color-secondary, #6c757d);
          background-color: var(--neutral-50, #f8f9fa);
          border-radius: 0.25rem;
        }
        
        .form-group {
          margin-bottom: 1rem;
        }
        
        .form-group label {
          display: block;
          margin-bottom: 0.25rem;
          font-weight: 500;
        }
        
        .form-control {
          display: block;
          width: 100%;
          padding: 0.375rem 0.75rem;
          font-size: 0.875rem;
          line-height: 1.5;
          color: var(--input-text, #333);
          background-color: var(--input-bg, #fff);
          background-clip: padding-box;
          border: 1px solid var(--input-border, #ced4da);
          border-radius: 0.25rem;
          transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }
        
        .form-control:focus {
          border-color: var(--primary-500, #0d6efd);
          outline: 0;
          box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
        }
        
        .condition-builder {
          min-height: 200px;
        }
        
        body.modal-open {
          overflow: hidden;
        }
        
        .btn-cancel {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--border-color, #dee2e6);
          background-color: var(--bg-color, #fff);
          color: var(--text-color, #333);
          border-radius: 0.25rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .btn-cancel:hover {
          background-color: var(--neutral-100, #f2f2f2);
        }
      `;
      
      document.head.appendChild(style);
    }
  }
  
  /**
   * Set up event listeners
   * @private
   */
  _setupEvents() {
    if (!this.modalElement) return;
    
    // Close button
    const closeButton = this.modalElement.querySelector('.filter-modal-close');
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        this.hide();
      });
    }
    
    // Cancel button
    const cancelButton = this.modalElement.querySelector('.btn-cancel');
    if (cancelButton) {
      cancelButton.addEventListener('click', () => {
        this.hide();
      });
    }
    
    // Backdrop click
    const backdrop = this.modalElement.querySelector('.filter-modal-backdrop');
    if (backdrop) {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) {
          this.hide();
        }
      });
    }
    
    // Save button
    const saveButton = this.modalElement.querySelector('#saveFilterBtn');
    if (saveButton) {
      saveButton.addEventListener('click', () => {
        this._saveFilter();
      });
    }
    
    // Entity type change
    const entityTypeSelect = this.modalElement.querySelector('#entityType');
    if (entityTypeSelect) {
      entityTypeSelect.addEventListener('change', (e) => {
        this._updateConditionBuilder(e.target.value);
      });
    }
  }
  
  /**
   * Populate the form with filter data
   * @param {Object} filter - Filter data
   * @private
   */
  _populateForm(filter) {
    if (!this.modalElement) return;
    
    const nameInput = this.modalElement.querySelector('#filterName');
    const categorySelect = this.modalElement.querySelector('#filterCategory');
    const descriptionTextarea = this.modalElement.querySelector('#filterDescription');
    const entityTypeSelect = this.modalElement.querySelector('#entityType');
    
    if (nameInput) nameInput.value = filter.name || '';
    if (descriptionTextarea) descriptionTextarea.value = filter.description || '';
    
    if (categorySelect && filter.category) {
      [...categorySelect.options].forEach(option => {
        if (option.value === filter.category.toLowerCase()) {
          option.selected = true;
        }
      });
    }
    
    if (entityTypeSelect && filter.definition && filter.definition.entityType) {
      [...entityTypeSelect.options].forEach(option => {
        if (option.value === filter.definition.entityType) {
          option.selected = true;
        }
      });
      
      this._updateConditionBuilder(filter.definition.entityType);
    }
  }
  
  /**
   * Update the condition builder based on selected entity type
   * @param {string} entityType - Selected entity type
   * @private
   */
  _updateConditionBuilder(entityType) {
    if (!this.modalElement) return;
    
    const conditionBuilder = this.modalElement.querySelector('.condition-builder');
    if (!conditionBuilder) return;
    
    if (!entityType) {
      conditionBuilder.innerHTML = `
        <div class="condition-placeholder">
          <p>Select an entity type to start building filter conditions</p>
        </div>
      `;
      return;
    }
    
    // Find the entity type in the options
    const entityTypeObj = this.options.entityTypes.find(type => type.id === entityType);
    if (!entityTypeObj) {
      console.error(`Entity type "${entityType}" not found in options`);
      return;
    }
    
    // Generate fields for the selected entity type
    const entityFields = this.options.fields.filter(field => field.entityType === entityType);
    
    if (entityFields.length === 0) {
      conditionBuilder.innerHTML = `
        <div class="condition-placeholder">
          <p>No fields available for this entity type</p>
        </div>
      `;
      return;
    }
    
    // Render condition builder interface
    conditionBuilder.innerHTML = `
      <div class="condition-group">
        <div class="condition-group-header">
          <select class="condition-group-operator">
            <option value="AND">AND</option>
            <option value="OR">OR</option>
          </select>
          <button class="add-condition-btn">
            <i class="fas fa-plus"></i> Add Condition
          </button>
        </div>
        <div class="condition-list">
          <!-- Initial empty condition -->
          <div class="condition-item">
            <select class="condition-field">
              <option value="">Select field...</option>
              ${entityFields.map(field => 
                `<option value="${field.id}">${field.name}</option>`
              ).join('')}
            </select>
            <select class="condition-operator">
              <option value="">--</option>
            </select>
            <input type="text" class="condition-value" placeholder="Value" disabled>
            <button class="remove-condition-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>
    `;
    
    // Set up event listeners for the condition builder
    this._setupConditionBuilderEvents(conditionBuilder);
    
    // If we're editing, populate with existing conditions
    if (this.currentFilter && this.currentFilter.definition && this.currentFilter.definition.conditions) {
      this._populateConditions(conditionBuilder, this.currentFilter.definition.conditions);
    }
  }
  
  /**
   * Set up event listeners for the condition builder
   * @param {HTMLElement} conditionBuilder - Condition builder element
   * @private
   */
  _setupConditionBuilderEvents(conditionBuilder) {
    if (!conditionBuilder) return;
    
    // Add condition button
    const addBtn = conditionBuilder.querySelector('.add-condition-btn');
    if (addBtn) {
      addBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this._addNewCondition(conditionBuilder);
      });
    }
    
    // Initial condition field change
    const fields = conditionBuilder.querySelectorAll('.condition-field');
    fields.forEach(field => {
      field.addEventListener('change', (e) => {
        this._updateOperators(e.target);
      });
    });
    
    // Initial remove button
    const removeButtons = conditionBuilder.querySelectorAll('.remove-condition-btn');
    removeButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const conditionItem = e.target.closest('.condition-item');
        if (conditionItem) {
          conditionItem.remove();
        }
      });
    });
  }
  
  /**
   * Populate conditions from existing filter definition
   * @param {HTMLElement} conditionBuilder - Condition builder element
   * @param {Object} conditions - Filter conditions
   * @private
   */
  _populateConditions(conditionBuilder, conditions) {
    if (!conditionBuilder || !conditions) return;
    
    // Set group operator
    const groupOperator = conditionBuilder.querySelector('.condition-group-operator');
    if (groupOperator && conditions.operator) {
      groupOperator.value = conditions.operator;
    }
    
    // Clear initial empty condition
    const conditionList = conditionBuilder.querySelector('.condition-list');
    if (conditionList) {
      conditionList.innerHTML = '';
      
      // Add each condition
      if (conditions.conditions && Array.isArray(conditions.conditions)) {
        conditions.conditions.forEach(condition => {
          const conditionItem = document.createElement('div');
          conditionItem.className = 'condition-item';
          
          const entityType = this.modalElement.querySelector('#entityType').value;
          const entityFields = this.options.fields.filter(field => field.entityType === entityType);
          
          conditionItem.innerHTML = `
            <select class="condition-field">
              <option value="">Select field...</option>
              ${entityFields.map(field => 
                `<option value="${field.id}" ${field.id === condition.field ? 'selected' : ''}>${field.name}</option>`
              ).join('')}
            </select>
            <select class="condition-operator">
              <option value="">--</option>
            </select>
            <input type="text" class="condition-value" placeholder="Value" value="${condition.value || ''}">
            <button class="remove-condition-btn">
              <i class="fas fa-times"></i>
            </button>
          `;
          
          conditionList.appendChild(conditionItem);
          
          // Set up the operator dropdown
          const fieldSelect = conditionItem.querySelector('.condition-field');
          this._updateOperators(fieldSelect, condition.operator);
          
          // Add event listeners
          fieldSelect.addEventListener('change', (e) => {
            this._updateOperators(e.target);
          });
          
          const removeButton = conditionItem.querySelector('.remove-condition-btn');
          removeButton.addEventListener('click', (e) => {
            e.preventDefault();
            conditionItem.remove();
          });
        });
      }
    }
  }
  
  /**
   * Add a new condition to the builder
   * @param {HTMLElement} conditionBuilder - Condition builder element
   * @private
   */
  _addNewCondition(conditionBuilder) {
    if (!conditionBuilder) return;
    
    const conditionList = conditionBuilder.querySelector('.condition-list');
    if (!conditionList) return;
    
    const conditionItem = document.createElement('div');
    conditionItem.className = 'condition-item';
    
    const entityType = this.modalElement.querySelector('#entityType').value;
    const entityFields = this.options.fields.filter(field => field.entityType === entityType);
    
    conditionItem.innerHTML = `
      <select class="condition-field">
        <option value="">Select field...</option>
        ${entityFields.map(field => 
          `<option value="${field.id}">${field.name}</option>`
        ).join('')}
      </select>
      <select class="condition-operator">
        <option value="">--</option>
      </select>
      <input type="text" class="condition-value" placeholder="Value" disabled>
      <button class="remove-condition-btn">
        <i class="fas fa-times"></i>
      </button>
    `;
    
    conditionList.appendChild(conditionItem);
    
    // Add event listeners
    const fieldSelect = conditionItem.querySelector('.condition-field');
    fieldSelect.addEventListener('change', (e) => {
      this._updateOperators(e.target);
    });
    
    const removeButton = conditionItem.querySelector('.remove-condition-btn');
    removeButton.addEventListener('click', (e) => {
      e.preventDefault();
      conditionItem.remove();
    });
  }
  
  /**
   * Update operators based on selected field
   * @param {HTMLElement} fieldSelect - Field select element
   * @param {string} selectedOperator - Selected operator (for populating existing data)
   * @private
   */
  _updateOperators(fieldSelect, selectedOperator = null) {
    if (!fieldSelect) return;
    
    const fieldId = fieldSelect.value;
    if (!fieldId) return;
    
    const entityType = this.modalElement.querySelector('#entityType').value;
    const field = this.options.fields.find(f => f.entityType === entityType && f.id === fieldId);
    
    if (!field) {
      console.error(`Field "${fieldId}" not found for entity type "${entityType}"`);
      return;
    }
    
    const conditionItem = fieldSelect.closest('.condition-item');
    if (!conditionItem) return;
    
    const operatorSelect = conditionItem.querySelector('.condition-operator');
    const valueInput = conditionItem.querySelector('.condition-value');
    
    if (!operatorSelect || !valueInput) return;
    
    // Clear existing options
    operatorSelect.innerHTML = '<option value="">Select operator...</option>';
    
    // Add type-specific operators
    switch (field.type) {
      case 'string':
        operatorSelect.innerHTML += `
          <option value="equals" ${selectedOperator === 'equals' ? 'selected' : ''}>equals</option>
          <option value="contains" ${selectedOperator === 'contains' ? 'selected' : ''}>contains</option>
          <option value="starts_with" ${selectedOperator === 'starts_with' ? 'selected' : ''}>starts with</option>
          <option value="ends_with" ${selectedOperator === 'ends_with' ? 'selected' : ''}>ends with</option>
        `;
        break;
      case 'number':
        operatorSelect.innerHTML += `
          <option value="equals" ${selectedOperator === 'equals' ? 'selected' : ''}>equals</option>
          <option value="greater_than" ${selectedOperator === 'greater_than' ? 'selected' : ''}>greater than</option>
          <option value="less_than" ${selectedOperator === 'less_than' ? 'selected' : ''}>less than</option>
          <option value="between" ${selectedOperator === 'between' ? 'selected' : ''}>between</option>
        `;
        break;
      case 'boolean':
        operatorSelect.innerHTML += `
          <option value="is_true" ${selectedOperator === 'is_true' ? 'selected' : ''}>is true</option>
          <option value="is_false" ${selectedOperator === 'is_false' ? 'selected' : ''}>is false</option>
        `;
        break;
      case 'date':
        operatorSelect.innerHTML += `
          <option value="equals" ${selectedOperator === 'equals' ? 'selected' : ''}>equals</option>
          <option value="before" ${selectedOperator === 'before' ? 'selected' : ''}>before</option>
          <option value="after" ${selectedOperator === 'after' ? 'selected' : ''}>after</option>
          <option value="between" ${selectedOperator === 'between' ? 'selected' : ''}>between</option>
        `;
        break;
      case 'array':
        operatorSelect.innerHTML += `
          <option value="contains" ${selectedOperator === 'contains' ? 'selected' : ''}>contains</option>
          <option value="contains_any" ${selectedOperator === 'contains_any' ? 'selected' : ''}>contains any</option>
          <option value="contains_all" ${selectedOperator === 'contains_all' ? 'selected' : ''}>contains all</option>
        `;
        break;
    }
    
    // Enable/disable value input based on operator
    operatorSelect.addEventListener('change', () => {
      const operator = operatorSelect.value;
      
      if (operator === 'is_true' || operator === 'is_false') {
        valueInput.disabled = true;
        valueInput.value = '';
      } else {
        valueInput.disabled = false;
      }
    });
    
    // Trigger change event to set initial state
    const event = new Event('change');
    operatorSelect.dispatchEvent(event);
  }
  
  /**
   * Save the filter
   * @private
   */
  _saveFilter() {
    if (!this.modalElement) return;
    
    // Get form values
    const nameInput = this.modalElement.querySelector('#filterName');
    const categorySelect = this.modalElement.querySelector('#filterCategory');
    const descriptionTextarea = this.modalElement.querySelector('#filterDescription');
    const entityTypeSelect = this.modalElement.querySelector('#entityType');
    
    if (!nameInput || !nameInput.value.trim()) {
      this._showValidationError(nameInput, 'Filter name is required');
      return;
    }
    
    if (!entityTypeSelect || !entityTypeSelect.value) {
      this._showValidationError(entityTypeSelect, 'Entity type selection is required');
      return;
    }
    
    // Build filter definition
    const definition = {
      entityType: entityTypeSelect.value,
      conditions: this._buildConditions()
    };
    
    if (!definition.conditions) {
      this._showValidationError(
        this.modalElement.querySelector('.condition-list'),
        'At least one valid condition is required'
      );
      return;
    }
    
    // Create filter object
    const filter = {
      ...this.currentFilter,
      id: this.editMode ? this.currentFilter.id : `new-${Date.now()}`, // Temporary ID until saved to backend
      name: nameInput.value.trim(),
      category: categorySelect.value,
      description: descriptionTextarea.value.trim(),
      definition: definition,
      updatedAt: new Date().toISOString()
    };
    
    if (!this.editMode && !filter.createdAt) {
      filter.createdAt = new Date().toISOString();
    }
    
    // Call the save callback
    if (this.options.onSave) {
      this.options.onSave(filter, this.editMode);
    }
    
    // Hide the modal
    this.hide();
  }
  
  /**
   * Build conditions object from UI
   * @returns {Object|null} Conditions object or null if invalid
   * @private
   */
  _buildConditions() {
    if (!this.modalElement) return null;
    
    const conditionGroupOperator = this.modalElement.querySelector('.condition-group-operator');
    if (!conditionGroupOperator) return null;
    
    const operator = conditionGroupOperator.value;
    const conditionItems = this.modalElement.querySelectorAll('.condition-item');
    
    if (!conditionItems || conditionItems.length === 0) return null;
    
    const conditions = [];
    
    for (const item of conditionItems) {
      const fieldSelect = item.querySelector('.condition-field');
      const operatorSelect = item.querySelector('.condition-operator');
      const valueInput = item.querySelector('.condition-value');
      
      if (!fieldSelect || !fieldSelect.value || !operatorSelect || !operatorSelect.value) {
        continue; // Skip invalid conditions
      }
      
      let value = null;
      
      // Special handling for operators that don't need values
      if (operatorSelect.value === 'is_true') {
        value = true;
      } else if (operatorSelect.value === 'is_false') {
        value = false;
      } else if (!valueInput.disabled) {
        value = valueInput.value;
      }
      
      conditions.push({
        field: fieldSelect.value,
        operator: operatorSelect.value,
        value: value
      });
    }
    
    if (conditions.length === 0) {
      return null;
    }
    
    return {
      operator: operator,
      conditions: conditions
    };
  }
  
  /**
   * Show validation error
   * @param {HTMLElement} element - Element with error
   * @param {string} message - Error message
   * @private
   */
  _showValidationError(element, message) {
    if (!element) return;
    
    // Remove any existing error messages
    const existingError = element.parentNode.querySelector('.validation-error');
    if (existingError) {
      existingError.remove();
    }
    
    // Add error class to element
    element.classList.add('validation-error-input');
    
    // Create error message
    const errorElement = document.createElement('div');
    errorElement.className = 'validation-error';
    errorElement.textContent = message;
    
    // Add error message after element
    element.parentNode.insertBefore(errorElement, element.nextSibling);
    
    // Focus the element
    element.focus();
    
    // Remove error on input
    element.addEventListener('input', function onInput() {
      element.classList.remove('validation-error-input');
      const error = element.parentNode.querySelector('.validation-error');
      if (error) {
        error.remove();
      }
      element.removeEventListener('input', onInput);
    });
  }
  
  /**
   * Show the modal
   * @private
   */
  _show() {
    if (this.modalElement) {
      this.modalElement.classList.add('active');
      document.body.classList.add('modal-open');
      this.isVisible = true;
      
      // Focus the name input
      const nameInput = this.modalElement.querySelector('#filterName');
      if (nameInput) {
        nameInput.focus();
      }
    }
  }
}

export default FilterModal;