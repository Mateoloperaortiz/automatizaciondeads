# Magneto Ads Booster POC Implementation Guide

This document outlines the implementation details of the Magneto Ads Booster Sprint 1 Proof of Concept.

## Overview

The POC focuses on three key user stories:

1. **HU-001: User account management with different roles**
2. **HU-005: Connection to social media ad platforms**
3. **HU-009: Importing vacancies from the ATS system**

## Technical Implementation

### 1. Project Structure

The project is built using:
- Next.js with TypeScript
- PostgreSQL with Prisma ORM
- TailwindCSS for styling
- NextAuth.js for authentication

The application follows a standard Next.js App Router structure:

```
/src
  /app               # Next.js App Router
    /api             # API routes
    /auth            # Authentication pages
    /dashboard       # Dashboard page
    /platforms       # Platform management
    /vacancies       # Vacancy management
  /components        # Reusable React components
  /lib               # Utility functions and service clients
  /types             # TypeScript type definitions
/prisma              # Database schema
/docs                # Documentation
```

### 2. User Authentication (HU-001)

#### Implementation Details

- **NextAuth.js** is used for user authentication
- Users can register and log in with email/password
- OAuth integration with Google and Facebook is provided
- User roles (ADMIN, MANAGER, CREATOR) are implemented
- JWT strategy is used for session management

#### User Flows

1. **Registration**: Users can create an account with name, email, and password
2. **Login**: Users can log in with email/password or OAuth providers
3. **Role-based access**: Different users see different features based on role

### 3. Platform Connections (HU-005)

#### Implementation Details

- OAuth 2.0 integration with social media platforms
- Secure token storage in the database
- Token refresh handling when applicable
- Clear UI for connection status

#### Supported Platforms

- **Meta (Facebook & Instagram)** - Full implementation
- **Google Ads** - Full implementation
- **X (Twitter)** - UI prepared, OAuth framework in place
- **TikTok** - UI prepared, OAuth framework in place
- **Snapchat** - UI prepared, OAuth framework in place

#### Connection Flow

1. User clicks "Connect" for a platform
2. User is redirected to platform OAuth authorization
3. After authorization, user is redirected back to Magneto Ads Booster
4. Tokens are securely stored in the database
5. Connection status is updated in the UI

### 4. ATS Integration (HU-009)

#### Implementation Details

- RESTful API client for ATS communication
- Data transformation between ATS and Magneto Ads Booster formats
- Vacancy import UI with search and filtering
- Validation of imported data

#### Import Flow

1. User goes to the vacancy import page
2. System fetches available vacancies from ATS
3. User can search and filter the list
4. User selects vacancies to import
5. System transforms and stores the selected vacancies
6. Imported vacancies are available for campaign creation

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/api/auth/[...nextauth]` | GET/POST | NextAuth.js authentication endpoints |
| `/api/auth/register` | POST | User registration |
| `/api/auth/platform/[platform]` | GET | Initiate OAuth flow for platform connection |
| `/api/auth/platform/callback` | GET | OAuth callback handling |
| `/api/vacancies/import` | POST | Import vacancies from ATS |

## Database Schema

The database schema includes:

- **User**: User accounts with roles
- **PlatformConnection**: OAuth tokens for ad platforms
- **Vacancy**: Imported job vacancies
- **Campaign**: Ad campaigns for vacancies

## Security Considerations

- **Authentication**: JWT-based with secure cookie storage
- **OAuth**: State parameter used to prevent CSRF attacks
- **API Tokens**: Encrypted in database
- **API Routes**: Protected with session validation

## POC Limitations

- For demonstration purposes, actual API calls are mocked
- Success scenarios are simulated rather than making real API requests
- Database operations are commented out with explanations
- A hardcoded admin user is provided for testing

## Getting Started

1. **Environment Setup**:
   - Copy `.env.example` to `.env.local`
   - Fill in required environment variables

2. **Database Setup**:
   - Run `npm run prisma:migrate` to set up the database

3. **Start the Application**:
   - Run `npm run dev` to start the development server
   - Access the application at `http://localhost:3000`

4. **Test User Credentials**:
   - Email: `admin@example.com`
   - Password: `password`
