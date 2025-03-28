/**
 * Ad Template Service
 * Provides functionality for managing ad templates
 */

import { BaseApiService } from './services/base-api-service.js';
import { toastService } from './services/toast-service.js';

/**
 * Template Service for managing ad templates
 */
export class AdTemplateService {
  /**
   * Create a new template service instance
   */
  constructor() {
    this.apiService = new BaseApiService();
    this.endpoints = {
      templates: '/api/ad-templates',
      template: (id) => `/api/ad-templates/${id}`
    };
  }

  /**
   * Get all templates
   * @returns {Promise<Array>} - List of templates
   */
  async getTemplates() {
    try {
      const response = await this.apiService.get(this.endpoints.templates);
      return response.data || [];
    } catch (error) {
      this._handleError('Error fetching templates', error);
      
      // Fallback to localStorage if API fails
      return this._getLocalTemplates();
    }
  }

  /**
   * Get a template by ID
   * @param {string|number} templateId - Template ID
   * @returns {Promise<Object>} - Template data
   */
  async getTemplate(templateId) {
    try {
      const response = await this.apiService.get(this.endpoints.template(templateId));
      return response.data;
    } catch (error) {
      this._handleError(`Error fetching template ${templateId}`, error);
      
      // Fallback to localStorage
      const templates = this._getLocalTemplates();
      return templates.find(t => t.id === templateId || t.name === templateId);
    }
  }

  /**
   * Save a new template
   * @param {Object} template - Template to save
   * @returns {Promise<Object>} - Saved template with ID
   */
  async saveTemplate(template) {
    try {
      const response = await this.apiService.post(this.endpoints.templates, template);
      
      // For backward compatibility, also save to localStorage
      this._saveLocalTemplate(template);
      
      return response.data;
    } catch (error) {
      this._handleError('Error saving template', error);
      
      // Fallback to localStorage only
      const savedTemplate = this._saveLocalTemplate(template);
      return savedTemplate;
    }
  }

  /**
   * Update an existing template
   * @param {string|number} templateId - Template ID
   * @param {Object} template - Updated template data
   * @returns {Promise<Object>} - Updated template
   */
  async updateTemplate(templateId, template) {
    try {
      const response = await this.apiService.put(
        this.endpoints.template(templateId), 
        template
      );
      
      // Update in localStorage too
      this._updateLocalTemplate(templateId, template);
      
      return response.data;
    } catch (error) {
      this._handleError(`Error updating template ${templateId}`, error);
      
      // Fallback to localStorage only
      return this._updateLocalTemplate(templateId, template);
    }
  }

  /**
   * Delete a template
   * @param {string|number} templateId - Template ID
   * @returns {Promise<boolean>} - Success status
   */
  async deleteTemplate(templateId) {
    try {
      await this.apiService.delete(this.endpoints.template(templateId));
      
      // Also remove from localStorage
      this._deleteLocalTemplate(templateId);
      
      return true;
    } catch (error) {
      this._handleError(`Error deleting template ${templateId}`, error);
      
      // Fallback to localStorage only
      this._deleteLocalTemplate(templateId);
      return false;
    }
  }

  /**
   * Get templates from localStorage
   * @returns {Array} - List of templates
   * @private
   */
  _getLocalTemplates() {
    try {
      return JSON.parse(localStorage.getItem('adTemplates') || '[]');
    } catch (e) {
      console.error('Error parsing localStorage templates', e);
      return [];
    }
  }

  /**
   * Save template to localStorage
   * @param {Object} template - Template to save
   * @returns {Object} - Saved template with generated ID
   * @private
   */
  _saveLocalTemplate(template) {
    try {
      const templates = this._getLocalTemplates();
      
      // Generate a client-side ID if none exists
      const newTemplate = { 
        ...template,
        id: template.id || `local_${Date.now()}`,
        createdAt: template.createdAt || new Date().toISOString()
      };
      
      templates.push(newTemplate);
      localStorage.setItem('adTemplates', JSON.stringify(templates));
      
      return newTemplate;
    } catch (e) {
      console.error('Error saving template to localStorage', e);
      return template;
    }
  }

  /**
   * Update template in localStorage
   * @param {string|number} templateId - Template ID
   * @param {Object} updatedTemplate - Updated template data
   * @returns {Object} - Updated template
   * @private
   */
  _updateLocalTemplate(templateId, updatedTemplate) {
    try {
      const templates = this._getLocalTemplates();
      const index = templates.findIndex(t => t.id === templateId || t.name === templateId);
      
      if (index >= 0) {
        templates[index] = {
          ...templates[index],
          ...updatedTemplate,
          updatedAt: new Date().toISOString()
        };
        
        localStorage.setItem('adTemplates', JSON.stringify(templates));
        return templates[index];
      }
      
      return null;
    } catch (e) {
      console.error('Error updating template in localStorage', e);
      return updatedTemplate;
    }
  }

  /**
   * Delete template from localStorage
   * @param {string|number} templateId - Template ID
   * @returns {boolean} - Success status
   * @private
   */
  _deleteLocalTemplate(templateId) {
    try {
      const templates = this._getLocalTemplates();
      const newTemplates = templates.filter(t => t.id !== templateId && t.name !== templateId);
      
      localStorage.setItem('adTemplates', JSON.stringify(newTemplates));
      return true;
    } catch (e) {
      console.error('Error deleting template from localStorage', e);
      return false;
    }
  }

  /**
   * Handle API errors
   * @param {string} message - Error message prefix
   * @param {Error} error - Error object
   * @private
   */
  _handleError(message, error) {
    console.error(message, error);
    
    if (toastService) {
      toastService.error(`${message}: ${error.message || 'Unknown error'}`);
    }
  }
}

// Create singleton instance
export const adTemplateService = new AdTemplateService();