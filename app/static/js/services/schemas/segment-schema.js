/**
 * Segment Schema
 * JSON Schema definition for segment objects
 */

/**
 * Base schema for segment objects
 */
export const segmentSchema = {
  type: 'object',
  required: ['name'],
  properties: {
    name: {
      type: 'string',
      minLength: 2,
      maxLength: 100
    },
    description: {
      type: 'string'
    },
    criteria: {
      type: 'object'
    },
    characteristics: {
      type: 'object'
    },
    segment_code: {
      type: 'string'
    },
    candidate_ids: {
      type: 'array',
      items: {
        type: 'integer'
      }
    }
  }
};

/**
 * Schema for segment creation
 */
export const createSegmentSchema = {
  ...segmentSchema,
  required: ['name']
};

/**
 * Schema for segment updates
 */
export const updateSegmentSchema = {
  ...segmentSchema,
  required: []  // No required fields for updates
};

/**
 * Schema for segment criteria
 */
export const segmentCriteriaSchema = {
  type: 'object',
  properties: {
    age_min: {
      type: 'integer',
      minimum: 18
    },
    age_max: {
      type: 'integer',
      minimum: 18
    },
    gender: {
      type: 'string',
      enum: ['male', 'female', 'non-binary', 'other', 'all']
    },
    education_level: {
      type: 'string',
      enum: ['high-school', 'associate', 'bachelor', 'master', 'doctorate', 'all']
    },
    experience_years_min: {
      type: 'integer',
      minimum: 0
    },
    experience_years_max: {
      type: 'integer',
      minimum: 0
    },
    locations: {
      type: 'array',
      items: {
        type: 'string'
      }
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
    job_search_status: {
      type: 'string',
      enum: ['active', 'passive', 'all']
    },
    remote_preference: {
      type: 'string',
      enum: ['remote', 'hybrid', 'in-office', 'flexible', 'all']
    }
  }
};