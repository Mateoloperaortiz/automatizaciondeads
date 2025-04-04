# AdFlux API Introduction

The AdFlux API provides programmatic access to the AdFlux system, allowing developers to integrate AdFlux functionality into their applications or automate workflows.

## API Overview

The AdFlux API is a RESTful API that uses standard HTTP methods and returns JSON responses. The API is versioned to ensure backward compatibility as new features are added.

### Base URL

```
https://your-adflux-instance.com/api
```

Replace `your-adflux-instance.com` with the actual domain where your AdFlux instance is hosted.

For local development, the base URL is:

```
http://127.0.0.1:5000/api
```

### API Versioning

The API version is included in the URL path (`v1` in the example above). This ensures that your integrations will continue to work even as the API evolves.

### Content Type

All requests and responses use JSON format. Requests should include the header:

```
Content-Type: application/json
```

### Authentication

The API uses token-based authentication. Include your API token in the `Authorization` header:

```
Authorization: Bearer YOUR_API_TOKEN
```

See the [Authentication](authentication.md) page for details on obtaining and managing API tokens.

## Available Resources

The API provides access to the following resources:

- **Job Openings**: Create, read, update, and delete job openings
- **Candidates**: Manage candidate profiles
- **Applications**: Track job applications
- **Segments**: Access candidate segments created by the ML model
- **Campaigns**: Create and manage ad campaigns
- **Meta Ads**: Interact with Meta (Facebook/Instagram) ad campaigns
- **Google Ads**: Interact with Google Ads campaigns
- **Tasks**: Manage and monitor asynchronous tasks

## HTTP Methods

The API uses standard HTTP methods:

- `GET`: Retrieve resources
- `POST`: Create new resources
- `PUT`: Update existing resources (full update)
- `PATCH`: Update existing resources (partial update)
- `DELETE`: Delete resources

## Response Format

All API responses follow a consistent format:

```json
{
  "status": "success",
  "data": {
    // Resource data
  },
  "meta": {
    // Metadata (pagination, etc.)
  }
}
```

For error responses:

```json
{
  "status": "error",
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      // Additional error details
    }
  }
}
```

## Pagination

List endpoints support pagination using the `page` and `per_page` query parameters:

```
GET /api/v1/job-openings?page=2&per_page=10
```

Pagination metadata is included in the `meta` field of the response:

```json
{
  "status": "success",
  "data": [...],
  "meta": {
    "pagination": {
      "page": 2,
      "per_page": 10,
      "total_pages": 5,
      "total_items": 42
    }
  }
}
```

See the [Pagination](pagination.md) page for more details.

## Filtering and Sorting

List endpoints support filtering and sorting using query parameters:

```
GET /api/v1/job-openings?status=open&sort=posted_date:desc
```

See the [Filtering and Sorting](reference/filtering.md) page for more details.

## Rate Limiting

The API implements rate limiting to prevent abuse. Rate limit information is included in the response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1620000000
```

See the [Rate Limiting](rate-limiting.md) page for more details.

## Error Handling

The API uses standard HTTP status codes to indicate success or failure. Error responses include detailed information about the error.

See the [Error Handling](error-handling.md) page for more details.

## API Explorer

The API includes a Swagger UI interface for exploring and testing the API. This is available at:

```
https://your-adflux-instance.com/api/docs/
```

For local development, access the Swagger UI at:

```
http://127.0.0.1:5000/api/docs/
```

## Getting Started

To get started with the AdFlux API:

1. Obtain an API token (see [Authentication](authentication.md))
2. Explore the available endpoints using the API Explorer
3. Make your first API request (see [Examples](examples/create-job.md))

## Support

If you encounter any issues or have questions about the API, please contact your AdFlux administrator or refer to the [Troubleshooting](../user-guides/troubleshooting.md) guide.
