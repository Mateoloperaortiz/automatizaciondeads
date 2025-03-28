# MagnetoCursor

Ad Automation System for targeted job opening ads on social media platforms.

## Overview

MagnetoCursor is an ad automation system designed to publish job opening ads on social media platforms and segment audiences for targeted advertising. The project integrates with Meta (Facebook), X (Twitter), and Google APIs to automate ad publishing for job openings.

## Key Features

- **Audience Segmentation**: Uses K-means clustering to segment candidates based on demographics and preferences.
- **Multi-Platform Integration**: Publishes job ads to Meta (Facebook/Instagram), X (Twitter), and Google.
- **Campaign Management**: Create, monitor, and optimize ad campaigns across platforms.
- **Analytics**: Track campaign performance and audience engagement.
- **Secure Credential Management**: Secure handling of API keys and access tokens.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/magnetocursor.git
cd magnetocursor
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env-example` to `.env` and add your API credentials:
```bash
cp .env-example .env
```

5. Initialize the database:
```bash
flask db setup
```

6. Run the application:
```bash
flask run
```

## Development

### Directory Structure

```
magnetocursor/
├── app/                  # Main application code
│   ├── models/           # Database models
│   ├── routes/           # API and web routes
│   ├── services/         # API integrations and business logic
│   ├── templates/        # HTML templates
│   ├── utils/            # Utility functions and helpers
│   └── static/           # Static files (CSS, JS, images)
├── ml/                   # Machine learning code
│   ├── data/             # Training and test data
│   ├── models/           # Trained models
│   └── visualizations/   # Data visualizations
├── tests/                # Test suite
├── instance/             # Instance-specific data (database)
├── migrations/           # Database migrations
└── docs/                 # Documentation
```

### CLI Commands

The application provides several CLI commands to manage the system:

```bash
# Generate simulated data
flask data generate --candidates 100 --jobs 20

# Train segmentation model
flask data segment --clusters 5 --visualize

# Manage credentials
flask credentials list
flask credentials health
flask credentials rotate META META_ACCESS_TOKEN
flask credentials export .env.backup

# View configuration
flask config show
```

### API Response Format

All API endpoints follow a standardized response format:

#### Success Response

```json
{
  "success": true,
  "data": [
    // Response data here
  ],
  "message": "Optional success message"
}
```

#### Error Response

```json
{
  "success": false,
  "message": "Error message",
  "errors": [
    // Optional detailed error information
  ]
}
```

#### Paginated Response

```json
{
  "success": true,
  "data": [
    // Data for current page
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  },
  "message": "Optional success message"
}
```

#### Utility Functions

For implementing this format in new API endpoints, use the utility functions in `app/utils/api_responses.py`:

```python
from app.utils.api_responses import api_success, api_error, paginated_response

# For success responses
return api_success(data=my_data, message="Optional message")

# For error responses
return api_error(message="Error message", errors=error_details, status_code=400)

# For paginated responses
return paginated_response(
    data=page_items,
    total=total_count,
    page=current_page,
    per_page=items_per_page
)
```

### Credential Management

MagnetoCursor includes a comprehensive credential management system:

- **Web Interface**: `/credentials` for managing API credentials
- **API Endpoints**: `/api/credentials/*` for credential management via API
- **CLI Commands**: `flask credentials` for command-line management
- **Documentation**: See `/docs/credential_management.md` for details

### Testing

Run the test suite with:

```bash
python tests/run_tests.py --verbose
```

Or run specific test types:

```bash
python tests/run_tests.py --type [unit|integration|e2e|security]
```

## Production Deployment

For production deployment:

1. Set up environment variables:
   - `FLASK_ENV=production`
   - Configure database connection string
   - Set up API credentials securely

2. Use a production WSGI server:
```bash
gunicorn app:app
```

3. Set up a reverse proxy (Nginx/Apache) in front of the application.

4. Configure proper security measures:
   - HTTPS
   - Rate limiting
   - API key security

See `docs/deployment.md` for detailed deployment instructions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

Developed by Magneto365 for internal job opening ad automation.