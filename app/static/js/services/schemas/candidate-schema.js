/**
 * Candidate Schema
 * JSON Schema definition for candidate objects
 */

/**
 * Base schema for candidate objects
 */
export const candidateSchema = {
  type: 'object',
  required: ['name'],
  properties: {
    name: {
      type: 'string',
      minLength: 2,
      maxLength: 100
    },
    email: {
      type: 'string',
      format: 'email'
    },
    age: {
      type: 'integer',
      minimum: 16,
      maximum: 100
    },
    gender: {
      type: 'string',
      enum: ['male', 'female', 'non-binary', 'other', 'prefer_not_to_say']
    },
    location: {
      type: 'string'
    },
    education: {
      type: 'string'
    },
    work_experience: {
      type: 'string'
    },
    job_preferences: {
      type: 'string'
    },
    skills: {
      type: 'array',
      items: {
        type: 'string'
      }
    },
    interests: {
      type: 'array',
      items: {
        type: 'string'
      }
    },
    segment_id: {
      type: 'integer'
    },
    profile_image_url: {
      type: 'string',
      format: 'uri'
    },
    salary_expectation: {
      type: 'number',
      minimum: 0
    },
    years_of_experience: {
      type: 'number',
      minimum: 0
    },
    highest_education_level: {
      type: 'string',
      enum: ['high-school', 'associate', 'bachelor', 'master', 'doctorate', 'none']
    },
    job_search_status: {
      type: 'string',
      enum: ['active', 'passive', 'not-looking']
    },
    remote_preference: {
      type: 'string',
      enum: ['remote', 'hybrid', 'in-office', 'flexible']
    }
  }
};

/**
 * Schema for candidate creation
 */
export const createCandidateSchema = {
  ...candidateSchema,
  required: ['name', 'email']
};

/**
 * Schema for candidate updates
 */
export const updateCandidateSchema = {
  ...candidateSchema,
  required: []  // No required fields for updates
};