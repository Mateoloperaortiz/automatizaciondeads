# MagnetoCursor Service Layer

## Overview

The service layer is a new architectural component that improves frontend-backend integration by providing:

1. **Centralized API Configuration** - All endpoints in a single location
2. **Standardized HTTP Methods** - Consistent request/response handling
3. **Robust Error Handling** - Unified error processing
4. **Feature-Specific Services** - Organized by business domain

## Directory Structure

```
app/static/js/services/
├── README.md                # This documentation file
├── api-config.js            # API endpoint definitions
├── base-api-service.js      # Base service with HTTP methods
├── campaign-service.js      # Campaign-specific service
├── error-handler.js         # Error handling utilities
└── index.js                 # Service exports
```

## Usage Examples

### Basic Usage

```javascript
// Import the service
import { campaignService } from './services/index.js';

// Get all campaigns
campaignService.getCampaigns()
  .then(campaigns => {
    // Handle successful response
    console.log(campaigns);
  })
  .catch(error => {
    // Error is already handled by the service layer
    // Any additional UI updates can be done here
  });
```

### Creating Resources

```javascript
// Import the service
import { campaignService } from './services/index.js';

// Create new campaign
const newCampaign = {
  title: 'Summer Jobs Campaign',
  description: 'Find opportunities for summer jobs',
  // Other required fields...
};

campaignService.createCampaign(newCampaign)
  .then(response => {
    // Handle successful creation
    console.log('Campaign created:', response);
  })
  .catch(error => {
    // Error already handled by service layer
  });
```

### File Upload with Progress

```javascript
// Get file from input
const fileInput = document.getElementById('ad-image');
const file = fileInput.files[0];

// Upload with progress tracking
campaignService.uploadCampaignImage(file, (percent) => {
  console.log(`Upload progress: ${percent}%`);
  // Update progress bar
  document.querySelector('.progress-bar').style.width = `${percent}%`;
})
.then(result => {
  console.log('Upload complete:', result.url);
})
.catch(error => {
  // Error already handled by service layer
});
```

## Key Features

### 1. API Configuration

The `api-config.js` file centralizes all API endpoints and provides utilities for building URLs:

- Environment-aware configuration (dev/prod/test)
- Organized endpoints by feature
- Path parameter substitution (e.g., `/campaigns/:id` → `/campaigns/123`)
- Query parameter handling

### 2. Base API Service

The `base-api-service.js` provides:

- HTTP methods: GET, POST, PUT, PATCH, DELETE
- File upload handling with progress reporting
- Response processing
- Error delegation

### 3. Error Handling

The `error-handler.js` provides:

- Error categorization (network, validation, authorization, etc.)
- User-friendly messages
- Console logging for debugging
- UI notifications via toast messages
- Optional analytics tracking

### 4. Feature Services

Services like `campaign-service.js` encapsulate business logic:

- Domain-specific methods
- Client-side validation
- Resource manipulation

## Integration

A refactored example using the service layer can be found in:

- `campaign-wizard-refactored.js`

This demonstrates how to migrate from direct fetch calls to the service layer approach.

## Benefits

- **Reduced Code Duplication** - Common HTTP logic in one place
- **Improved Maintainability** - Changes to API URLs only need to be made in one file
- **Better Error Handling** - Consistent error processing across the application
- **Type Safety** - Service methods enforce consistent data structures
- **Testability** - Services can be mocked for frontend unit testing