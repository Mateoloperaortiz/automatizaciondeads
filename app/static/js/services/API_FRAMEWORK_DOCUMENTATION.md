# API Framework Client Library Documentation

## Overview

The API Framework Client Library provides a standardized interface for interacting with various social media advertising platforms (Meta, Twitter, Google) from the frontend. This client-side implementation mirrors the backend API Framework, ensuring consistent behavior and error handling across the entire application.

## Architecture

The API Framework is built around several key design patterns:

1. **Request/Response Pattern**: All API interactions follow a standardized request and response format.
2. **Adapter Pattern**: Platform-specific implementations share a common interface via the `BaseAPIClient`.
3. **Facade Pattern**: The `APIFrameworkCampaignManager` provides a simplified interface for cross-platform operations.
4. **Caching Strategy**: Transparent TTL-based caching improves performance for read operations.
5. **Factory Method**: Various platform-specific request creation methods generate properly formatted requests.

## Key Components

### 1. APIRequest

Represents a standardized request to any platform API. Encapsulates all request details and provides metadata for caching and analytics.

```javascript
const request = new APIRequest({
  method: 'POST',
  endpoint: '/api-framework/meta/campaigns',
  data: { name: 'Test Campaign' },
  platform: 'META',
  operation: 'create_campaign'
});
```

### 2. APIResponse

Standardizes API responses across all platforms, providing consistent error handling and success/failure status.

```javascript
// Success response
const successResponse = APIResponse.success(requestId, responseData, 200);

// Error response
const errorResponse = APIResponse.error(requestId, 'Not found', 404);
```

### 3. TTLCache

Caches API responses to reduce network requests for frequently accessed data.

```javascript
const cache = new TTLCache(300000); // 5-minute TTL
cache.set('key', value);
const cachedValue = cache.get('key');
```

### 4. BaseAPIClient

Abstract base class that defines the common interface for all platform-specific clients.

```javascript
const baseClient = new BaseAPIClient('PLATFORM_NAME', credentials);
await baseClient.initialize();
const response = await baseClient.executeRequest(request);
```

### 5. Platform-Specific Clients

Implementations of the `BaseAPIClient` for specific social media platforms:

- `MetaAPIClient`: For Facebook and Instagram
- `TwitterAPIClient`: For Twitter/X
- `GoogleAPIClient`: For Google Ads

### 6. APIFrameworkCampaignManager

Unified interface for managing campaigns across multiple platforms simultaneously.

```javascript
const manager = new APIFrameworkCampaignManager({
  metaClient,
  twitterClient,
  googleClient
});

const result = await manager.createCampaign(
  jobOpeningId,
  ['meta', 'twitter', 'google'],
  segmentId,
  budget,
  'PAUSED'
);
```

## Integration Guide

### Step 1: Import Required Components

```javascript
import { 
  APIRequest, 
  APIResponse, 
  MetaAPIClient, 
  TwitterAPIClient, 
  GoogleAPIClient,
  APIFrameworkCampaignManager
} from '../services/api-framework.js';

import { ENDPOINTS } from '../services/api-config.js';
```

### Step 2: Initialize Platform Clients

```javascript
// Meta (Facebook & Instagram) credentials
const metaCredentials = {
  META_APP_ID: '...',
  META_APP_SECRET: '...',
  META_ACCESS_TOKEN: '...'
};

// Create and initialize client
const metaClient = new MetaAPIClient(metaCredentials);
await metaClient.initialize();
```

### Step 3: Create and Execute Requests

```javascript
// Create request using factory method
const campaignRequest = metaClient.createCampaignRequest(
  'Summer Promotion Campaign',
  'REACH',
  'PAUSED'
);

// Execute request
const response = await metaClient.executeRequest(campaignRequest);

// Handle response
if (response.success) {
  const campaignId = response.data.campaign_id;
  console.log('Campaign created:', campaignId);
} else {
  console.error('Failed to create campaign:', response.error);
}
```

### Step 4: Using the Campaign Manager (Optional)

For operations across multiple platforms:

```javascript
const campaignManager = new APIFrameworkCampaignManager({
  metaClient,
  twitterClient,
  googleClient
});

// Create campaigns on all platforms
const result = await campaignManager.createCampaign(
  jobOpeningId,
  ['meta', 'twitter', 'google'],
  segmentId,
  budget,
  'PAUSED'
);
```

## Error Handling

The API Framework provides consistent error handling across all platforms:

```javascript
try {
  const response = await client.executeRequest(request);
  
  if (!response.success) {
    // Handle API error
    console.error('API error:', response.error);
    console.log('Status code:', response.statusCode);
  }
} catch (error) {
  // Handle unexpected errors
  console.error('Unexpected error:', error);
}
```

For more advanced error handling with retries:

```javascript
async function executeWithRetry(client, request, maxRetries = 3) {
  let attempts = 0;
  
  while (attempts < maxRetries) {
    try {
      const response = await client.executeRequest(request);
      
      // Return successful responses immediately
      if (response.success) {
        return response;
      }
      
      // Handle rate limiting with exponential backoff
      if (response.statusCode === 429) {
        const delay = Math.pow(2, attempts) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        attempts++;
        continue;
      }
      
      // Return other error responses
      return response;
    } catch (error) {
      // Only retry on network errors
      if (error.message === 'Failed to fetch') {
        attempts++;
        continue;
      }
      
      // Rethrow other errors
      throw error;
    }
  }
  
  throw new Error('Maximum retry attempts exceeded');
}
```

## Caching Strategy

By default, GET requests can be cached to improve performance:

```javascript
// Create a cacheable request
const statsRequest = metaClient.getCampaignStatsRequest(campaignId);

// This will return the cached response if available
const response1 = await metaClient.executeRequest(statsRequest);

// This will also return the cached response without a network request
const response2 = await metaClient.executeRequest(statsRequest);

// To clear the cache
metaClient.clearCache();
```

## Best Practices

1. **Initialize Early**: Initialize API clients during application startup.
2. **Reuse Clients**: Create clients once and reuse them throughout the application.
3. **Handle Errors Gracefully**: Always check `response.success` before accessing `response.data`.
4. **Use Factory Methods**: Use the provided factory methods to create well-formed requests.
5. **Implement Retries**: Use retry logic for transient errors, especially rate limiting.
6. **Monitor Performance**: Track metrics like response times and cache hit rates.
7. **Secure Credentials**: Never expose API credentials in client-side code; obtain them securely from backend.

## Platform-Specific Considerations

### Meta (Facebook & Instagram)

- Uses a special ad category for job ads: `['EMPLOYMENT']`
- Requires precise targeting parameters for effective ad delivery
- Supports multiple ad formats across Facebook and Instagram platforms

### Twitter/X

- Character limits apply to tweet text
- Media uploads require a separate request before attaching to tweets
- Line items must be created before promoted tweets

### Google Ads

- Supports advanced targeting including keywords, locations, and demographics
- Requires responsive search ads with multiple headlines and descriptions
- Has strict ad policy requirements that may require approval

## Examples

See the `api-framework-usage.js` file for complete working examples, including:

1. Setting up platform clients
2. Creating and executing a Meta campaign
3. Publishing tweets with Twitter API
4. Creating Google Ads campaigns with targeting
5. Using the unified Campaign Manager
6. Handling API errors and implementing retry logic

## Metrics and Monitoring

Each client automatically tracks metrics that can be used for monitoring:

```javascript
// Get metrics from a single client
const metrics = metaClient.getMetrics();
console.log('Meta API metrics:', metrics);

// Get metrics from all platforms via the campaign manager
const allMetrics = campaignManager.getMetrics();
console.log('All platform metrics:', allMetrics);
```

Available metrics include:
- Total requests
- Success rate
- Cache hit rate
- Average response time
- Error count

## Common Issues and Troubleshooting

1. **Authentication Failures**: Ensure credentials are valid and not expired.
2. **Rate Limiting**: Implement retry logic with exponential backoff.
3. **Invalid Requests**: Validate request parameters before sending.
4. **Network Errors**: Handle intermittent network failures with retries.
5. **Cross-Origin Issues**: Ensure proper CORS configuration on backend endpoints.

## API Reference

For a complete reference of all available methods and properties, see the source code documentation in `api-framework.js`.
