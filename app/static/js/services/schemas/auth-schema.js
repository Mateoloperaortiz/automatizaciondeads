/**
 * Auth Schema
 * JSON Schema definition for authentication-related objects
 */

/**
 * Schema for login requests
 */
export const loginSchema = {
  type: 'object',
  required: ['username', 'password'],
  properties: {
    username: {
      type: 'string',
      minLength: 3
    },
    password: {
      type: 'string',
      minLength: 8
    },
    remember_me: {
      type: 'boolean'
    }
  }
};

/**
 * Schema for registration requests
 */
export const registrationSchema = {
  type: 'object',
  required: ['username', 'email', 'password', 'confirm_password'],
  properties: {
    username: {
      type: 'string',
      minLength: 3,
      maxLength: 50,
      pattern: '^[a-zA-Z0-9_-]+$',
      patternMessage: 'Username can only contain letters, numbers, underscores and hyphens'
    },
    email: {
      type: 'string',
      format: 'email'
    },
    password: {
      type: 'string',
      minLength: 8,
      pattern: '(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^a-zA-Z0-9])',
      patternMessage: 'Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character'
    },
    confirm_password: {
      type: 'string',
      minLength: 8
    },
    first_name: {
      type: 'string'
    },
    last_name: {
      type: 'string'
    }
  }
};

/**
 * Schema for password reset requests
 */
export const passwordResetRequestSchema = {
  type: 'object',
  required: ['email'],
  properties: {
    email: {
      type: 'string',
      format: 'email'
    }
  }
};

/**
 * Schema for password reset confirmation
 */
export const passwordResetConfirmSchema = {
  type: 'object',
  required: ['token', 'password', 'confirm_password'],
  properties: {
    token: {
      type: 'string'
    },
    password: {
      type: 'string',
      minLength: 8,
      pattern: '(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^a-zA-Z0-9])',
      patternMessage: 'Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character'
    },
    confirm_password: {
      type: 'string',
      minLength: 8
    }
  }
};

/**
 * Schema for user profile updates
 */
export const userProfileSchema = {
  type: 'object',
  properties: {
    email: {
      type: 'string',
      format: 'email'
    },
    first_name: {
      type: 'string',
      maxLength: 100
    },
    last_name: {
      type: 'string',
      maxLength: 100
    },
    profile_image_url: {
      type: 'string',
      format: 'uri'
    },
    bio: {
      type: 'string',
      maxLength: 500
    },
    job_title: {
      type: 'string',
      maxLength: 100
    },
    department: {
      type: 'string',
      maxLength: 100
    }
  }
};