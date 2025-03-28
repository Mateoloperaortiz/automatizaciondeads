# Service Layer Architecture

## What is it?

The service layer is an architectural pattern that sits between your UI components and the backend API. It provides a consistent interface for all API operations and handles cross-cutting concerns like error handling, caching, and authentication.

```
┌───────────────┐       ┌─────────────┐       ┌────────────┐
│ UI Components │ ──▶── │ Service     │ ──▶── │            │
│ (HTML/JS)     │ ◀──── │ Layer       │ ◀──── │ Backend API│
└───────────────┘       └─────────────┘       └────────────┘
```

## Why Do We Need It?

The MagnetoCursor codebase currently has several issues with frontend-backend integration:

1. **Hardcoded API Endpoints** scattered throughout JavaScript files
2. **Inconsistent Error Handling** with different approaches in each file
3. **Duplicated Request Logic** for common operations
4. **Tightly Coupled Components** that assume specific response formats
5. **Lack of Error Recovery** mechanisms

## Benefits

✅ **Increased Maintainability**
- All API endpoints defined in a single file
- Common request/response handling logic in one place
- Consistent patterns across the application

✅ **Improved Developer Experience**
- Intelligent code completion for API methods
- Better documentation through typed interfaces
- Reusable patterns and less boilerplate

✅ **Enhanced User Experience**
- Consistent error handling and messages
- Better recovery from network failures
- Smoother loading states

✅ **Testability**
- Services can be easily mocked for unit tests
- API behavior can be simulated without backend
- Error scenarios can be tested consistently

## Core Components

### 1. API Configuration

Centralizes all endpoint definitions and URL building:

```javascript
// Before
fetch('/api/campaigns/123/publish');

// After
import { ENDPOINTS, buildUrl } from './services/api-config.js';
fetch(buildUrl(ENDPOINTS.CAMPAIGNS.PUBLISH, { id: 123 }));
```

### 2. Base API Service

Provides standardized HTTP methods:

```javascript
// Before
const response = await fetch('/api/campaigns', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(campaignData)
});
const data = await response.json();
if (!response.ok) {
  // Handle error
}

// After
import { BaseApiService } from './services/base-api-service.js';
const service = new BaseApiService();
const data = await service.post(ENDPOINTS.CAMPAIGNS.CREATE, campaignData);
```

### 3. Error Handler

Provides consistent error processing:

```javascript
// Before
try {
  // API call
} catch (error) {
  console.error('Error:', error);
  alert('An error occurred');
}

// After
import { ErrorHandler } from './services/error-handler.js';
const errorHandler = new ErrorHandler();
try {
  // API call
} catch (error) {
  errorHandler.handleError(error); // Logs, shows toast, tracks analytics
}
```

### 4. Feature Services

Domain-specific APIs with business logic:

```javascript
// Before
const response = await fetch('/api/campaigns?platform=facebook&active=true');
const campaigns = await response.json();

// After
import { campaignService } from './services/index.js';
const campaigns = await campaignService.getCampaigns({ 
  platform: 'facebook', 
  active: true 
});
```

## Getting Started

See the `README.md` file in the services directory for detailed documentation and examples. The `campaign-wizard-refactored.js` file shows a real-world example of migrating from direct API calls to the service layer.

## Implementation Timeline

We are following a phased approach to implementation:

1. **Phase 1: Foundation** (Complete)
   - Core architecture and CampaignService

2. **Phase 2: Main Implementation** (2-3 weeks)
   - Additional services and first migrations

3. **Phase 3: Advanced Features** (2 weeks)
   - Caching, offline support, WebSockets

4. **Phase 4: Finalization** (1 week)
   - Complete migration and optimization

See `IMPLEMENTATION_PLAN.md` for the detailed roadmap.