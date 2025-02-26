# Magneto Ads Booster - Magneto Ads Automation

## Project Overview
Magneto Ads Booster is a platform designed to automate the process of publishing job vacancy advertisements across multiple social media platforms. This proof of concept (POC) demonstrates the core functionality for Sprint 1, focusing on platform connections, ATS integration, and user management.

## Sprint 1 POC Scope
- **OAuth Integration**: Connection with Meta and Google Ads APIs
- **ATS Data Import**: Basic import functionality from Magneto's ATS
- **User Management**: Basic admin/user creation with role-based access

## Target Platforms
- Meta (Facebook, Instagram)
- Google Ads
- X (Twitter)
- TikTok
- Snapchat (future implementation)

## Technical Stack
- **Frontend**: Next.js with TypeScript and TailwindCSS
- **Backend**: Next.js API routes
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: NextAuth.js for user auth and OAuth

## Project Structure
```
magnetoadsbooster/
├── prisma/               # Database schema and migrations
├── public/               # Static assets
├── src/                  # Source code
│   ├── app/              # Next.js App Router
│   ├── components/       # React components
│   ├── lib/              # Utility functions and shared code
│   ├── pages/            # Next.js Pages Router (if used)
│   └── types/            # TypeScript type definitions
├── docs/                 # Documentation
├── package.json          # Dependencies and scripts
└── README.md             # Project documentation
```

## Getting Started
1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables: Copy `.env.example` to `.env.local` and fill in values
4. Set up the database: `npm run prisma:migrate`
5. Run the development server: `npm run dev`

## Key Features
- OAuth-based connection to advertising platforms
- Secure token storage and management
- User role management (Admin, Manager, Creator)
- ATS vacancy data import and transformation
- Basic dashboard for connection status monitoring

## Success Criteria
1. Admin can create and manage user accounts with different roles
2. System can connect to Meta and Google Ads via OAuth
3. Basic vacancy data can be imported from the ATS
4. System securely stores and manages access tokens
