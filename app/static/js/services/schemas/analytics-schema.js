/**
 * Analytics Schema
 * JSON Schema definition for analytics-related objects
 */

/**
 * Schema for analytics timeframe parameters
 */
export const timeframeSchema = {
  type: 'object',
  required: ['period'],
  properties: {
    period: {
      type: 'string',
      enum: ['day', 'week', 'month', 'quarter', 'year', 'custom']
    },
    start_date: {
      type: 'string',
      format: 'date'
    },
    end_date: {
      type: 'string',
      format: 'date'
    }
  }
};

/**
 * Schema for campaign analytics request
 */
export const campaignAnalyticsRequestSchema = {
  type: 'object',
  required: ['campaign_id'],
  properties: {
    campaign_id: {
      type: 'integer'
    },
    period: {
      type: 'string',
      enum: ['day', 'week', 'month', 'quarter', 'year', 'custom']
    },
    start_date: {
      type: 'string',
      format: 'date'
    },
    end_date: {
      type: 'string',
      format: 'date'
    },
    metrics: {
      type: 'array',
      items: {
        type: 'string',
        enum: ['impressions', 'clicks', 'ctr', 'conversions', 'cost', 'cpc', 'cpa']
      }
    }
  }
};

/**
 * Schema for segment analytics request
 */
export const segmentAnalyticsRequestSchema = {
  type: 'object',
  required: ['segment_id'],
  properties: {
    segment_id: {
      type: 'integer'
    },
    period: {
      type: 'string',
      enum: ['day', 'week', 'month', 'quarter', 'year', 'custom']
    },
    start_date: {
      type: 'string',
      format: 'date'
    },
    end_date: {
      type: 'string',
      format: 'date'
    },
    metrics: {
      type: 'array',
      items: {
        type: 'string',
        enum: ['campaign_count', 'impression_share', 'click_share', 'conversion_share', 'cost_share']
      }
    }
  }
};

/**
 * Schema for analytics report generation
 */
export const reportGenerationSchema = {
  type: 'object',
  required: ['report_type', 'period'],
  properties: {
    report_type: {
      type: 'string',
      enum: ['campaign_performance', 'segment_performance', 'platform_comparison', 'job_performance', 'roi_analysis']
    },
    entity_ids: {
      type: 'array',
      items: {
        type: 'integer'
      }
    },
    period: {
      type: 'string',
      enum: ['day', 'week', 'month', 'quarter', 'year', 'custom']
    },
    start_date: {
      type: 'string',
      format: 'date'
    },
    end_date: {
      type: 'string',
      format: 'date'
    },
    format: {
      type: 'string',
      enum: ['csv', 'pdf', 'excel', 'json']
    },
    metrics: {
      type: 'array',
      items: {
        type: 'string'
      }
    }
  }
};