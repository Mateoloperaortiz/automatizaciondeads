# Job Openings API

The Job Openings API allows you to manage job openings in the AdFlux system.

## Endpoints

- [List Job Openings](#list-job-openings)
- [Get Job Opening](#get-job-opening)
- [Create Job Opening](#create-job-opening)
- [Update Job Opening](#update-job-opening)
- [Delete Job Opening](#delete-job-opening)
- [List Applications for Job Opening](#list-applications-for-job-opening)
- [List Campaigns for Job Opening](#list-campaigns-for-job-opening)

## List Job Openings

Retrieves a list of job openings.

```
GET /api/v1/job-openings
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | Page number (default: 1) |
| per_page | integer | Items per page (default: 20, max: 100) |
| status | string | Filter by status (e.g., open, closed) |
| location | string | Filter by location |
| company | string | Filter by company |
| title | string | Filter by title (partial match) |
| skills | string | Filter by required skills (comma-separated) |
| sort | string | Sort field and direction (e.g., posted_date:desc) |

### Response

```json
{
  "status": "success",
  "data": [
    {
      "job_id": "JOB-0001",
      "title": "Senior Software Engineer",
      "description": "We are looking for a senior software engineer...",
      "location": "San Francisco, CA",
      "company": "Tech Corp",
      "required_skills": ["Python", "JavaScript", "AWS"],
      "salary_min": 120000,
      "salary_max": 160000,
      "posted_date": "2025-03-15",
      "status": "open",
      "target_segments": [1, 3],
      "applications_count": 5,
      "campaigns_count": 2
    },
    {
      "job_id": "JOB-0002",
      "title": "Product Manager",
      "description": "Experienced product manager needed...",
      "location": "New York, NY",
      "company": "Product Inc",
      "required_skills": ["Product Management", "Agile", "UX"],
      "salary_min": 110000,
      "salary_max": 150000,
      "posted_date": "2025-03-20",
      "status": "open",
      "target_segments": [2, 4],
      "applications_count": 3,
      "campaigns_count": 1
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_pages": 1,
      "total_items": 2
    }
  }
}
```

## Get Job Opening

Retrieves a specific job opening by ID.

```
GET /api/v1/job-openings/{job_id}
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | Job opening ID |

### Response

```json
{
  "status": "success",
  "data": {
    "job_id": "JOB-0001",
    "title": "Senior Software Engineer",
    "description": "We are looking for a senior software engineer...",
    "location": "San Francisco, CA",
    "company": "Tech Corp",
    "required_skills": ["Python", "JavaScript", "AWS"],
    "salary_min": 120000,
    "salary_max": 160000,
    "posted_date": "2025-03-15",
    "status": "open",
    "target_segments": [1, 3],
    "applications_count": 5,
    "campaigns_count": 2
  }
}
```

## Create Job Opening

Creates a new job opening.

```
POST /api/v1/job-openings
```

### Request Body

```json
{
  "title": "Senior Software Engineer",
  "description": "We are looking for a senior software engineer...",
  "location": "San Francisco, CA",
  "company": "Tech Corp",
  "required_skills": ["Python", "JavaScript", "AWS"],
  "salary_min": 120000,
  "salary_max": 160000,
  "posted_date": "2025-03-15",
  "status": "open",
  "target_segments": [1, 3]
}
```

### Response

```json
{
  "status": "success",
  "data": {
    "job_id": "JOB-0001",
    "title": "Senior Software Engineer",
    "description": "We are looking for a senior software engineer...",
    "location": "San Francisco, CA",
    "company": "Tech Corp",
    "required_skills": ["Python", "JavaScript", "AWS"],
    "salary_min": 120000,
    "salary_max": 160000,
    "posted_date": "2025-03-15",
    "status": "open",
    "target_segments": [1, 3],
    "applications_count": 0,
    "campaigns_count": 0
  }
}
```

## Update Job Opening

Updates an existing job opening.

```
PUT /api/v1/job-openings/{job_id}
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | Job opening ID |

### Request Body

```json
{
  "title": "Senior Software Engineer",
  "description": "We are looking for a senior software engineer...",
  "location": "San Francisco, CA",
  "company": "Tech Corp",
  "required_skills": ["Python", "JavaScript", "AWS", "Docker"],
  "salary_min": 130000,
  "salary_max": 170000,
  "posted_date": "2025-03-15",
  "status": "open",
  "target_segments": [1, 3, 5]
}
```

### Response

```json
{
  "status": "success",
  "data": {
    "job_id": "JOB-0001",
    "title": "Senior Software Engineer",
    "description": "We are looking for a senior software engineer...",
    "location": "San Francisco, CA",
    "company": "Tech Corp",
    "required_skills": ["Python", "JavaScript", "AWS", "Docker"],
    "salary_min": 130000,
    "salary_max": 170000,
    "posted_date": "2025-03-15",
    "status": "open",
    "target_segments": [1, 3, 5],
    "applications_count": 5,
    "campaigns_count": 2
  }
}
```

## Delete Job Opening

Deletes a job opening.

```
DELETE /api/v1/job-openings/{job_id}
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | Job opening ID |

### Response

```json
{
  "status": "success",
  "data": {
    "message": "Job opening deleted successfully"
  }
}
```

## List Applications for Job Opening

Retrieves a list of applications for a specific job opening.

```
GET /api/v1/job-openings/{job_id}/applications
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | Job opening ID |

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | Page number (default: 1) |
| per_page | integer | Items per page (default: 20, max: 100) |
| status | string | Filter by status (e.g., Submitted, Under Review) |
| sort | string | Sort field and direction (e.g., application_date:desc) |

### Response

```json
{
  "status": "success",
  "data": [
    {
      "application_id": 1,
      "job_id": "JOB-0001",
      "candidate_id": "CAND-00001",
      "candidate_name": "John Doe",
      "application_date": "2025-03-20",
      "status": "Under Review"
    },
    {
      "application_id": 2,
      "job_id": "JOB-0001",
      "candidate_id": "CAND-00002",
      "candidate_name": "Jane Smith",
      "application_date": "2025-03-21",
      "status": "Submitted"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_pages": 1,
      "total_items": 2
    }
  }
}
```

## List Campaigns for Job Opening

Retrieves a list of campaigns for a specific job opening.

```
GET /api/v1/job-openings/{job_id}/campaigns
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | Job opening ID |

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | Page number (default: 1) |
| per_page | integer | Items per page (default: 20, max: 100) |
| status | string | Filter by status (e.g., draft, active, paused) |
| platform | string | Filter by platform (e.g., meta, google) |
| sort | string | Sort field and direction (e.g., created_at:desc) |

### Response

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Senior Engineer - Meta Campaign",
      "description": "Campaign for Senior Software Engineer position on Meta",
      "platform": "meta",
      "status": "active",
      "daily_budget": 5000,
      "job_opening_id": "JOB-0001",
      "target_segment_ids": [1, 3],
      "created_at": "2025-03-22T10:30:00Z",
      "updated_at": "2025-03-22T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Senior Engineer - Google Campaign",
      "description": "Campaign for Senior Software Engineer position on Google Ads",
      "platform": "google",
      "status": "active",
      "daily_budget": 4500,
      "job_opening_id": "JOB-0001",
      "target_segment_ids": [1, 3],
      "created_at": "2025-03-22T11:15:00Z",
      "updated_at": "2025-03-22T11:15:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_pages": 1,
      "total_items": 2
    }
  }
}
```

## Error Responses

### Not Found (404)

```json
{
  "status": "error",
  "error": {
    "code": "resource_not_found",
    "message": "Job opening not found",
    "details": {
      "job_id": "JOB-9999"
    }
  }
}
```

### Validation Error (400)

```json
{
  "status": "error",
  "error": {
    "code": "validation_error",
    "message": "Validation failed",
    "details": {
      "title": ["This field is required"],
      "salary_min": ["Must be less than salary_max"]
    }
  }
}
```

### Unauthorized (401)

```json
{
  "status": "error",
  "error": {
    "code": "unauthorized",
    "message": "Authentication required",
    "details": {}
  }
}
```

### Forbidden (403)

```json
{
  "status": "error",
  "error": {
    "code": "forbidden",
    "message": "You do not have permission to perform this action",
    "details": {}
  }
}
```
