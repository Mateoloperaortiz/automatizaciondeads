# Frontend Service Layer Migration Guide

## Overview

This guide provides step-by-step instructions for migrating existing JavaScript code to use the new service layer architecture. The service layer centralizes API calls, adds schema validation, and provides consistent error handling.

## Migration Steps

### 1. Update Script Imports

Add imports for the necessary services at the top of your JavaScript file:

```javascript
// Before: No imports, direct API calls using fetch
const response = await fetch('/api/campaigns');

// After: Import service(s) 
import { campaignService } from './services/index.js';
```

If your HTML is not using ES modules, you'll need to update your script tags:

```html
<!-- Before -->
<script src="/static/js/your-script.js"></script>

<!-- After -->
<script type="module" src="/static/js/your-script.js"></script>
```

### 2. Replace Direct API Calls

Replace direct fetch calls with service layer methods:

```javascript
// Before
async function getCampaigns() {
  try {
    const response = await fetch('/api/campaigns');
    if (!response.ok) {
      throw new Error('API request failed');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching campaigns:', error);
    showErrorMessage('Failed to load campaigns');
    return null;
  }
}

// After
async function getCampaigns() {
  try {
    return await campaignService.getCampaigns();
  } catch (error) {
    // Error already handled by service layer
    // Any UI-specific error handling can go here
    return null;
  }
}
```

### 3. Replace Custom Validation

Replace manual validation with schema validation:

```javascript
// Before
function validateCampaignData(campaignData) {
  const errors = [];
  if (!campaignData.title) {
    errors.push('Title is required');
  }
  if (!campaignData.platform_id) {
    errors.push('Platform is required');
  }
  return errors;
}

// After
// Validation is now handled automatically by the service layer
// No need for manual validation in most cases
await campaignService.createCampaign(campaignData);
```

### 4. Replace Error Handling

The service layer now handles common error cases consistently:

```javascript
// Before
try {
  const response = await fetch('/api/campaigns', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(campaignData)
  });
  const data = await response.json();
  if (!response.ok) {
    showErrorMessage(data.message || 'Failed to create campaign');
    return;
  }
  showSuccessMessage('Campaign created successfully');
} catch (error) {
  console.error('Error creating campaign:', error);
  showErrorMessage('An unexpected error occurred');
}

// After
try {
  await campaignService.createCampaign(campaignData);
  showSuccessMessage('Campaign created successfully');
} catch (error) {
  // The service layer has already logged the error and shown a notification
  // You can add component-specific error handling if needed
}
```

### 5. File Upload Handling

Replace manual FormData handling with the service's upload methods:

```javascript
// Before
const formData = new FormData();
formData.append('image', fileInput.files[0]);

try {
  const response = await fetch('/api/uploads/image', {
    method: 'POST',
    body: formData
  });
  // ... handle response
} catch (error) {
  // ... handle error
}

// After
try {
  const imageData = await campaignService.uploadCampaignImage(
    fileInput.files[0], 
    (progress) => {
      // Update progress bar
      progressBar.style.width = `${progress}%`;
    }
  );
  // Use the returned image URL
  imagePreview.src = imageData.url;
} catch (error) {
  // Error already handled by service layer
}
```

### 6. Update Real-time Features

Replace WebSocket handling with the WebSocket service:

```javascript
// Before
const socket = new WebSocket('ws://example.com/socket');
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle message
};

// After
import { websocketService } from './services/index.js';

// Connect to WebSocket
await websocketService.connect('/api/notifications/ws');

// Register event handlers
websocketService.on('notification', (data) => {
  // Handle notification
});
```

## Example: Platform Status Visualization

See the refactored `platform-status-visualization-refactored.js` file for a complete example of migrating a component to use the service layer.

Key changes:
1. Added import for the platform service
2. Removed hardcoded API URLs
3. Replaced direct fetch calls with service methods
4. Simplified error handling
5. Improved code organization

## Testing Your Migration

After migrating a component:

1. Test the main success paths (loading data, creating/updating resources)
2. Test error handling (server errors, validation errors, network errors)
3. Verify that notifications appear correctly for errors
4. Check console for any unexpected errors
5. Verify that the component works offline if offline support is implemented

## Benefits of Migration

- **Reduced Code Duplication**: Common HTTP logic in one place
- **Improved Maintainability**: Changes to API URLs only need to be made in one file
- **Better Error Handling**: Consistent error processing across the application
- **Input Validation**: Schema-based validation prevents bad data
- **Testability**: Services can be mocked for frontend unit testing