/**
 * Campaign Schema
 * JSON Schema definition for campaign objects
 */

/**
 * Base schema for campaign objects
 */
export const campaignSchema = {
  type: 'object',
  required: ['title', 'platform_id', 'job_opening_id', 'ad_headline', 'ad_text'],
  properties: {
    title: {
      type: 'string',
      minLength: 3,
      maxLength: 100
    },
    description: {
      type: 'string',
      maxLength: 500
    },
    platform_id: {
      type: 'integer'
    },
    job_opening_id: {
      type: 'integer'
    },
    segment_id: {
      type: 'integer'
    },
    budget: {
      type: 'number',
      minimum: 0
    },
    start_date: {
      type: 'string',
      format: 'date'
    },
    end_date: {
      type: 'string',
      format: 'date'
    },
    status: {
      type: 'string',
      enum: ['draft', 'active', 'paused', 'completed', 'cancelled']
    },
    ad_headline: {
      type: 'string',
      minLength: 3,
      maxLength: 100
    },
    ad_text: {
      type: 'string',
      minLength: 10,
      maxLength: 2000
    },
    ad_cta: {
      type: 'string',
      enum: ['apply_now', 'learn_more', 'see_jobs', 'sign_up']
    },
    ad_image_url: {
      type: 'string',
      format: 'uri'
    }
  }
};

/**
 * Schema for campaign creation
 */
export const createCampaignSchema = {
  ...campaignSchema,
  required: ['title', 'platform_id', 'job_opening_id', 'ad_headline', 'ad_text']
};

/**
 * Schema for campaign updates
 */
export const updateCampaignSchema = {
  ...campaignSchema,
  required: []  // No required fields for updates
};

/**
 * Schema for platform-specific content for Meta (Facebook)
 */
export const metaAdSchema = {
  type: 'object',
  properties: {
    headline: {
      type: 'string',
      maxLength: 100
    },
    text: {
      type: 'string',
      maxLength: 2000
    },
    cta: {
      type: 'string',
      enum: ['apply_now', 'learn_more', 'see_jobs', 'sign_up']
    },
    image_url: {
      type: 'string',
      format: 'uri'
    }
  }
};

/**
 * Schema for platform-specific content for Google Ads
 */
export const googleAdSchema = {
  type: 'object',
  properties: {
    headline: {
      type: 'string',
      maxLength: 30
    },
    description_line1: {
      type: 'string',
      maxLength: 90
    },
    description_line2: {
      type: 'string',
      maxLength: 90
    },
    final_url: {
      type: 'string',
      format: 'uri'
    }
  }
};

/**
 * Schema for platform-specific content for Twitter (X)
 */
export const twitterAdSchema = {
  type: 'object',
  properties: {
    tweet_text: {
      type: 'string',
      maxLength: 280
    },
    image_url: {
      type: 'string',
      format: 'uri'
    },
    website_url: {
      type: 'string',
      format: 'uri'
    }
  }
};