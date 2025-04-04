# AdFlux Architecture Overview

## System Architecture

AdFlux follows a modular, layered architecture designed for scalability, maintainability, and extensibility. The system is built using the Flask web framework with a PostgreSQL database, and incorporates machine learning for candidate segmentation.

### High-Level Architecture Diagram

```
+----------------------------------+
|           Web Interface          |
|  (Flask Templates, Tailwind CSS) |
+----------------------------------+
                |
+----------------------------------+
|           API Layer              |
|      (Flask-RESTX, Swagger)      |
+----------------------------------+
                |
+----------------------------------+       +---------------------------+
|         Service Layer            | <---> |   Machine Learning Engine |
| (Business Logic, Validation)     |       |   (Scikit-learn, Pandas)  |
+----------------------------------+       +---------------------------+
                |                                       |
+----------------------------------+       +---------------------------+
|         Data Access Layer        | <---> |      Task Queue           |
|   (SQLAlchemy, Flask-SQLAlchemy) |       |   (Celery, Redis)         |
+----------------------------------+       +---------------------------+
                |                                       |
+----------------------------------+       +---------------------------+
|           Database               |       |   External API Clients    |
|         (PostgreSQL)             |       | (Meta, Google Ads)        |
+----------------------------------+       +---------------------------+
                                                       |
                                           +---------------------------+
                                           |   Social Media Platforms  |
                                           | (Meta, Google Ads)        |
                                           +---------------------------+
```

## Core Components

### Web Interface

The web interface is built using Flask's templating system with Tailwind CSS for styling. It provides a user-friendly dashboard for managing job openings, candidates, and ad campaigns.

**Key Features:**
- Responsive design for desktop and mobile
- Interactive dashboards with real-time data
- Form-based interfaces for data entry
- Data visualization for campaign performance

### API Layer

The API layer is implemented using Flask-RESTX, which provides RESTful API endpoints with automatic Swagger documentation. This layer handles HTTP requests, authentication, and routing.

**Key Features:**
- RESTful API design
- JSON request/response format
- Authentication and authorization
- Rate limiting and request validation
- Swagger documentation

### Service Layer

The service layer contains the core business logic of the application. It handles operations like campaign creation, candidate segmentation, and data validation.

**Key Features:**
- Business rule implementation
- Transaction management
- Cross-cutting concerns (logging, error handling)
- Service composition

### Data Access Layer

The data access layer is implemented using SQLAlchemy with Flask-SQLAlchemy extension. It provides an object-relational mapping (ORM) for database operations.

**Key Features:**
- Object-relational mapping
- Query building and execution
- Transaction management
- Migration support (Flask-Migrate)

### Machine Learning Engine

The machine learning engine is built using Scikit-learn and Pandas. It handles candidate segmentation using K-means clustering.

**Key Features:**
- Data preprocessing and feature engineering
- K-means clustering for segmentation
- Model training and evaluation
- Prediction and segment assignment

### Task Queue

The task queue is implemented using Celery with Redis as the message broker. It handles asynchronous and scheduled tasks like campaign publishing and data synchronization.

**Key Features:**
- Asynchronous task processing
- Task scheduling
- Task monitoring and retry
- Distributed task execution

### External API Clients

The external API clients handle communication with social media advertising platforms like Meta and Google Ads.

**Key Features:**
- Authentication and authorization
- Request formatting and validation
- Response parsing
- Error handling and retry logic

## Data Flow

1. **Job Opening Creation**:
   - User creates a job opening through the web interface
   - Data is validated and stored in the database
   - Job opening becomes available for campaign creation

2. **Candidate Segmentation**:
   - Candidate data is loaded from the database
   - Machine learning engine processes the data
   - Candidates are assigned to segments
   - Segment information is stored in the database

3. **Campaign Creation**:
   - User creates a campaign targeting specific job openings and segments
   - Campaign data is validated and stored in the database
   - Campaign is ready for publishing

4. **Campaign Publishing**:
   - User initiates campaign publishing
   - Task is queued for asynchronous processing
   - External API client formats the request for the target platform
   - Campaign is published to the social media platform
   - External IDs and status are stored in the database

5. **Performance Tracking**:
   - Scheduled task retrieves performance data from social media platforms
   - Data is processed and stored in the database
   - Performance metrics are displayed in the web interface

## Technology Stack

### Backend
- **Framework**: Python 3.9+ with Flask
- **API**: Flask-RESTX with Swagger documentation
- **Database**: PostgreSQL (SQLite for development)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy & Flask-Migrate
- **Task Queue**: Celery with Redis
- **Scheduler**: Flask-APScheduler
- **Forms**: Flask-WTF
- **Serialization**: Marshmallow with Flask-Marshmallow

### Machine Learning
- **Framework**: Scikit-learn
- **Algorithm**: K-means clustering
- **Data Processing**: Pandas, NumPy
- **Model Persistence**: Joblib

### API Integrations
- **Meta Ads**: `facebook-python-business-sdk`
- **Google Ads**: `google-ads-python`
- **Data Generation**: Google Gemini API

### Frontend
- **Templates**: Jinja2
- **CSS Framework**: Tailwind CSS

### Development & Deployment
- **CLI**: Click
- **Environment**: python-dotenv
- **Testing**: Pytest
- **Version Control**: Git & GitHub
- **Deployment Target**: Google Cloud Platform

## Security Considerations

- **Authentication**: Password-based authentication for web interface
- **Authorization**: Role-based access control for different user types
- **API Security**: Token-based authentication for API access
- **Data Protection**: Encryption for sensitive data (API credentials)
- **Input Validation**: Form and API request validation
- **CSRF Protection**: Cross-Site Request Forgery protection for web forms

## Scalability Considerations

- **Horizontal Scaling**: Stateless application design allows for multiple instances
- **Database Scaling**: Connection pooling and query optimization
- **Task Queue Scaling**: Multiple Celery workers can be deployed
- **Caching**: Strategic caching for frequently accessed data
- **Cloud Deployment**: Google Cloud Platform services for scalability

## Monitoring and Logging

- **Application Logging**: Structured logging with different severity levels
- **Performance Monitoring**: Timing metrics for critical operations
- **Task Monitoring**: Status tracking for asynchronous tasks
- **Error Tracking**: Detailed error messages and stack traces
- **Alerting**: Configurable alerts for critical issues
