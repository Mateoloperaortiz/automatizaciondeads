# WebSocket Filter UI

A comprehensive UI toolkit for building, managing, and monitoring WebSocket subscription filters.

## Overview

The WebSocket Filter UI provides a visual interface for creating and managing complex filters for WebSocket subscriptions. These filters allow clients to subscribe to specific subsets of real-time data based on sophisticated filtering conditions. The UI is designed to be user-friendly while supporting advanced filtering capabilities.

![WebSocket Filter UI](https://via.placeholder.com/1200x800?text=WebSocket+Filter+UI)

## Components

### Core Components

1. **FilterBuilder**
   - Visual interface for building complex filter conditions
   - Supports nested condition groups with AND/OR/NOT logic
   - Field selector with data type-specific operators
   - Value inputs customized for different data types
   - Real-time validation and preview
   - Filter testing functionality

2. **FilterManager**
   - Interface for saving, loading, and organizing filters
   - Filter categorization and search
   - Performance statistics for filter evaluation
   - Filter efficiency monitoring
   - Filter duplication and deletion

## Filter Structure

Filters are structured as condition trees with groups and individual conditions:

```javascript
{
  // Filter metadata
  id: "filter123",
  name: "Active Google Campaigns",
  description: "Filter for active campaigns on Google platform",
  category: "campaigns",
  entityType: "campaign",
  createdAt: "2025-02-15T10:30:00",
  updatedAt: "2025-02-20T14:45:00",
  createdBy: "admin",
  
  // Filter condition tree
  conditions: {
    type: "group",
    operator: "and",
    conditions: [
      {
        type: "condition",
        field: "platform",
        operator: "equals",
        value: "google"
      },
      {
        type: "condition",
        field: "is_active",
        operator: "equals",
        value: true
      }
    ]
  }
}
```

## Filter Builder

The FilterBuilder component provides an intuitive interface for creating complex filter conditions. It supports:

### Features

- **Field Selection**: Select fields from a list of available fields with their associated data types
- **Operators**: Choose from a list of operators appropriate for the selected field type
- **Value Input**: Input fields customized for the data type (string, number, boolean, date, array)
- **Nested Groups**: Create complex logic with nested condition groups
- **Logic Operators**: Toggle between AND, OR, and NOT logic for condition groups
- **Real-time Preview**: JSON preview of the filter structure
- **Validation**: Real-time validation with error messages
- **Filter Testing**: Test filter against sample data

### Supported Data Types and Operators

| Data Type | Supported Operators |
|-----------|---------------------|
| string | equals, not_equals, contains, not_contains, starts_with, ends_with, in, not_in, is_empty, is_not_empty |
| number | equals, not_equals, greater_than, greater_than_or_equals, less_than, less_than_or_equals, between, not_between, in, not_in, is_empty, is_not_empty |
| boolean | equals, not_equals |
| date | equals, not_equals, after, after_or_equals, before, before_or_equals, between, not_between, is_empty, is_not_empty |
| array | contains, not_contains, contains_any, contains_all, is_empty, is_not_empty |

## Filter Manager

The FilterManager component provides a comprehensive interface for managing saved filters:

### Features

- **Filter List**: Browse and search saved filters
- **Categories**: Organize filters by category
- **Filter Details**: View detailed information about filters
- **Filter Statistics**: Track filter performance metrics
- **Filter Actions**: Edit, duplicate, and delete filters
- **Filter Preview**: JSON preview of the filter structure

### Performance Metrics

The Filter Manager tracks the following performance metrics for each filter:

- **Messages Received**: Total number of messages processed by the filter
- **Messages Matched**: Number of messages that matched the filter criteria
- **Match Rate**: Percentage of messages that matched the filter
- **Average Processing Time**: Average time in milliseconds to evaluate the filter
- **Efficiency**: Calculated efficiency score based on processing time and complexity
- **Last Matched**: Timestamp of the last message that matched the filter

## Usage

### Basic Setup

```javascript
import { FilterBuilder, FilterManager } from '../websocket-filter-ui/index.js';

// Initialize filter builder
const filterBuilder = new FilterBuilder(
  document.getElementById('filter-builder-container'), 
  {
    availableFields: [
      { id: 'entity_type', label: 'Entity Type', type: 'string' },
      { id: 'platform', label: 'Platform', type: 'string' },
      { id: 'is_active', label: 'Is Active', type: 'boolean' }
    ],
    filterableEntityTypes: [
      { id: 'campaign', label: 'Campaign' },
      { id: 'ad_set', label: 'Ad Set' }
    ],
    onChange: (filter) => console.log('Filter updated:', filter),
    onSave: (filter) => saveFilterToServer(filter),
    onTest: (filter) => testFilterAgainstSampleData(filter)
  }
);

// Initialize filter manager
const filterManager = new FilterManager(
  document.getElementById('filter-manager-container'),
  {
    filterListUrl: '/api/websocket/filters',
    filterStatsUrl: '/api/websocket/filter-stats',
    categories: ['General', 'Campaigns', 'Notifications'],
    onLoadFilter: (filter) => filterBuilder.loadFilter(filter),
    onDeleteFilter: (filterId) => deleteFilterFromServer(filterId),
    onDuplicateFilter: (filter) => duplicateFilter(filter)
  }
);
```

### Creating a New Filter

```javascript
// Create an empty filter
const emptyFilter = filterBuilder.createEmptyFilter();

// Load it into the builder
filterBuilder.loadFilter(emptyFilter);

// Add conditions through the UI
// ... user interactions ...

// Get the current filter
const currentFilter = filterBuilder.getCurrentFilter();

// Save the filter
filterBuilder.saveFilter(currentFilter);
```

### Loading and Editing a Filter

```javascript
// Load a filter from the manager
filterManager.loadFilter(filterId);

// Get the current filter from the builder
const currentFilter = filterBuilder.getCurrentFilter();

// Make changes through the UI
// ... user interactions ...

// Save the updated filter
filterBuilder.saveFilter(currentFilter);
```

## Configuration Options

### FilterBuilder Options

| Option | Type | Description |
|--------|------|-------------|
| darkMode | Boolean | Enable dark theme |
| availableFields | Array | List of fields available for filtering |
| filterableEntityTypes | Array | List of entity types available for filtering |
| initialFilter | Object | Initial filter to load |
| onChange | Function | Callback when filter changes |
| onSave | Function | Callback when filter is saved |
| onTest | Function | Callback when filter is tested |
| maxDepth | Number | Maximum nesting depth for groups |
| showPreview | Boolean | Show JSON preview |

### FilterManager Options

| Option | Type | Description |
|--------|------|-------------|
| darkMode | Boolean | Enable dark theme |
| onLoadFilter | Function | Callback when a filter is loaded |
| onDeleteFilter | Function | Callback when a filter is deleted |
| onDuplicateFilter | Function | Callback when a filter is duplicated |
| initialFilter | Object | Initial filter to select |
| filterListUrl | String | URL to fetch filter list |
| filterStatsUrl | String | URL to fetch filter statistics |
| categories | Array | List of filter categories |

## API Endpoints

The WebSocket Filter UI integrates with the following API endpoints:

- **GET /api/websocket/filters** - List all saved filters
- **POST /api/websocket/filters** - Create a new filter
- **GET /api/websocket/filters/:id** - Get a specific filter
- **PUT /api/websocket/filters/:id** - Update a filter
- **DELETE /api/websocket/filters/:id** - Delete a filter
- **GET /api/websocket/filter-stats** - Get performance statistics for all filters
- **GET /api/websocket/filter-stats/:id** - Get performance statistics for a specific filter
- **POST /api/websocket/test-filter** - Test a filter against sample data

## Backend Integration

The Filter UI components are designed to integrate with the existing WebSocket filter infrastructure:

- **WebSocket Filter Cache** (`app/services/websocket_filter_cache.py`) - Backend service that manages filter subscriptions
- **WebSocket Permissions** (`app/services/websocket_permissions.py`) - Handles authorization for WebSocket subscriptions
- **WebSocket Rate Limiter** (`app/services/websocket_rate_limiter.py`) - Enforces rate limits on WebSocket subscriptions

## Example

See the `examples` directory for a complete working example:

- `filter-builder-demo.html` - Interactive demo showcasing both the filter builder and manager components

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Dependencies

- FontAwesome (for icons)

## Integration with Realtime Architecture

This component integrates with the MagnetoCursor realtime architecture described in:

- `docs/real_time_architecture.md`
- `docs/realtime_entity_implementation.md`
- `docs/realtime_entity_types_integration.md`
- `docs/realtime_implementation_summary.md`
- `docs/realtime_implementation_update.md`
- `docs/realtime_optimization.md`

The WebSocket Filter UI provides the missing frontend interface for creating and managing the subscription filters that power the real-time data streaming capabilities.
