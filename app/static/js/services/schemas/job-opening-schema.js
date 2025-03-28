/**
 * Job Opening Schema
 * JSON Schema definition for job opening objects
 */

/**
 * Base schema for job opening objects
 */
export const jobOpeningSchema = {
  type: 'object',
  required: ['title', 'description', 'requirements'],
  properties: {
    title: {
      type: 'string',
      minLength: 3,
      maxLength: 100
    },
    description: {
      type: 'string',
      minLength: 10
    },
    requirements: {
      type: 'string',
      minLength: 10
    },
    location: {
      type: 'string'
    },
    company: {
      type: 'string'
    },
    department: {
      type: 'string'
    },
    employment_type: {
      type: 'string',
      enum: ['full-time', 'part-time', 'contract', 'temporary', 'internship', 'volunteer']
    },
    experience_level: {
      type: 'string',
      enum: ['entry', 'mid', 'senior', 'executive']
    },
    education_level: {
      type: 'string',
      enum: ['high-school', 'associate', 'bachelor', 'master', 'doctorate', 'none']
    },
    salary_min: {
      type: 'number',
      minimum: 0
    },
    salary_max: {
      type: 'number',
      minimum: 0
    },
    salary_currency: {
      type: 'string',
      minLength: 3,
      maxLength: 3
    },
    remote: {
      type: 'boolean'
    },
    active: {
      type: 'boolean'
    },
    application_url: {
      type: 'string',
      format: 'uri'
    },
    closing_date: {
      type: 'string',
      format: 'date'
    },
    tags: {
      type: 'array',
      items: {
        type: 'string'
      }
    }
  }
};

/**
 * Schema for job opening creation
 */
export const createJobOpeningSchema = {
  ...jobOpeningSchema,
  required: ['title', 'description', 'requirements']
};

/**
 * Schema for job opening updates
 */
export const updateJobOpeningSchema = {
  ...jobOpeningSchema,
  required: []  // No required fields for updates
};