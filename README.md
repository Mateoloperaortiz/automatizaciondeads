# AdsMaster - Automatización de Ads

## Overview

AdsMaster is a modern web application designed to automate the process of publishing job vacancy advertisements across multiple social media platforms. This tool streamlines the previously manual and time-consuming process of creating, deploying, and analyzing ad campaigns, allowing for more efficient and targeted recruitment advertising.

## Features

### Campaign Management

- **Campaign Creation**: Intuitive three-step workflow for creating job ad campaigns
  - Job details (title, description, requirements, salary, etc.)
  - Platform selection (Meta, LinkedIn, X/Twitter, Google, TikTok, Snapchat)
  - Audience targeting options
- **Multi-platform Publishing**: Simultaneous publishing to multiple social media platforms
- **Campaign Status Tracking**: Monitor active, scheduled, ended, and draft campaigns
- **Campaign Editing**: Update existing campaigns with new information or targeting

### Audience Targeting

- **Advanced Segmentation**: Target specific demographics based on job titles, skills, education, and location
- **Custom Audience Creation**: Create and save audience profiles for reuse
- **Intelligent Targeting**: Define specific targeting parameters for each platform 
- **Geographic Targeting**: Filter candidates by specific locations or regions
- **Job Title Targeting**: Target by current job titles or experience level
- **Skill-based Targeting**: Specify required or desired skills for candidates
- **Education Targeting**: Filter by educational level or specific institutions

### Platform Integration

- **API Connections**: Connect to platform APIs through secure authentication
- **Connection Management**: View and manage connected platform accounts
- **Platform-specific Optimizations**: Tailor content for each platform's requirements
- **API Health Monitoring**: Check API status, quota usage, and connection health
- **Multi-platform Support**: Integrated with Meta, LinkedIn, X/Twitter, Google Ads, TikTok, and Snapchat

### Analytics & Reporting

- **Performance Metrics**: Track views, clicks, and applications for each campaign
- **Platform Comparison**: Compare performance across different advertising platforms
- **Cost Analysis**: Monitor cost per click, cost per application, and total spend
- **Visual Dashboards**: Interactive charts and graphs for data visualization
- **Daily Trends**: Track campaign performance over time with daily metrics
- **Export Capabilities**: Download reports in various formats
- **Custom Date Ranges**: Filter analytics by specific time periods

### User Interface

- **Responsive Design**: Optimized for both desktop and mobile use
- **Dark/Light Mode**: Support for user theme preferences
- **Card-based Layout**: Organized information in easy-to-read card components
- **Animated Transitions**: Smooth transitions between pages and components
- **Intuitive Navigation**: User-friendly dashboard and workflow
- **Toast Notifications**: Non-intrusive feedback system for user actions
- **Advanced Filtering**: Filter campaigns by status, date, platform, and performance

## Technology Stack

### Frontend

- **React**: JavaScript library for building the user interface
- **TypeScript**: Static typing for improved code quality and developer experience
- **Vite**: Next-generation frontend tooling for faster development
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **shadcn/ui**: Component library built with Radix UI and Tailwind CSS
- **Recharts**: Composable charting library for data visualization
- **React Router**: Declarative routing for React applications
- **React Query**: Data fetching and state management library
- **React Hook Form**: Form validation and handling
- **React Context API**: State management for global application state
- **Framer Motion**: Animation library for smooth transitions

### Development Tools

- **ESLint**: JavaScript linting utility
- **TypeScript-ESLint**: TypeScript integration for ESLint
- **PostCSS**: Tool for transforming CSS with JavaScript plugins
- **Autoprefixer**: Plugin to parse CSS and add vendor prefixes
- **SWC**: Speedy Web Compiler for faster builds and transpilation

## Project Structure

```bash
automatizaciondeads/
├── public/                  # Static assets
├── src/                     # Source code
│   ├── components/          # Reusable UI components
│   │   ├── analytics/       # Analytics and reporting components
│   │   ├── audience/        # Audience targeting components
│   │   ├── campaign/        # Campaign management components
│   │   ├── dashboard/       # Dashboard UI components
│   │   ├── job/             # Job details components
│   │   ├── layout/          # Layout components (Header, Footer)
│   │   ├── notifications/   # Notification components
│   │   ├── platform/        # Platform integration components
│   │   └── ui/              # Base UI components from shadcn/ui
│   ├── contexts/            # React context providers
│   ├── data/                # Static data and constants
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions and helpers
│   ├── pages/               # Page components
│   │   ├── Dashboard.tsx          # Main dashboard
│   │   ├── CreateCampaign.tsx     # Campaign creation flow
│   │   ├── Platforms.tsx          # Platform management
│   │   ├── Analytics.tsx          # Overall analytics
│   │   ├── CampaignAnalytics.tsx  # Campaign-specific analytics
│   │   └── EditCampaign.tsx       # Campaign editing
│   ├── providers/           # Provider components
│   ├── services/            # API and data services
│   │   ├── campaignService.ts     # Campaign CRUD operations
│   │   ├── metricsService.ts      # Analytics data
│   │   ├── eventsService.ts       # Event handling
│   │   ├── platformHealthService.ts # API connection status
│   │   └── mockDatabase.ts        # Simulated backend
│   ├── types/               # TypeScript type definitions
│   ├── App.tsx              # Main application component
│   └── main.tsx             # Application entry point
├── .gitignore               # Git ignore file
├── components.json          # shadcn/ui configuration
├── eslint.config.js         # ESLint configuration
├── index.html               # HTML entry point
├── package.json             # Project dependencies and scripts
├── postcss.config.js        # PostCSS configuration
├── tailwind.config.ts       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── vite.config.ts           # Vite configuration
```

## Key Workflows

### Campaign Creation Flow
1. **Job Details**: Enter job title, description, requirements, salary, and more
2. **Platform Selection**: Choose which platforms to publish the job advertisement on
3. **Audience Targeting**: Define targeting criteria for the campaign audience
4. **Review and Publish**: Review campaign details and schedule or publish immediately

### Analytics Workflow
1. **Overview Dashboard**: View key metrics across all campaigns
2. **Campaign Selection**: Navigate to specific campaign for detailed analysis
3. **Platform Comparison**: Compare performance across different platforms
4. **Date Range Selection**: Filter data by specific time periods
5. **Export Reports**: Download analytics data in various formats

### Platform Connection Flow
1. **Platform Selection**: Choose platform to connect
2. **API Configuration**: Enter API keys and authentication details
3. **Connection Verification**: Test and verify connection to platform API
4. **Health Monitoring**: View connection health and quota usage

## Installation

Follow these steps to set up the project locally:

```sh
# Step 1: Clone the repository
git clone https://github.com/Mateoloperaortiz/automatizaciondeads.git

# Step 2: Navigate to the project directory
cd automatizaciondeads

# Step 3: Install dependencies
npm install

# Step 4: Start the development server
npm run dev
```

## Available Scripts

- `npm run dev`: Start the development server (port 8080)
- `npm run build`: Build the application for production
- `npm run build:dev`: Build the application with development settings
- `npm run lint`: Run ESLint to check code quality
- `npm run preview`: Preview the production build locally

## Platform Support

AdsMaster currently supports integration with the following advertising platforms:

- **Meta** (Facebook/Instagram): Advanced targeting with demographic options
- **LinkedIn**: Professional audience targeting based on job titles and skills
- **X (Twitter)**: Real-time engagement with job seekers
- **Google Ads**: Wide reach through the Google Display Network
- **TikTok**: Target younger candidates with video-based advertisements
- **Snapchat**: Reach Gen Z audience with interactive ad formats

## State Management

The application utilizes several approaches for state management:

- **React Context API**: Used for global application state (notifications, themes)
- **React Query**: For data fetching, caching, and server state
- **Form State**: Managed through React Hook Form
- **Local Component State**: useState for component-specific state
- **URL Parameters**: Used for route-specific state (campaign IDs, filters)

## UI/UX Patterns

- **Multi-step Forms**: Guided workflows with progress indicators
- **Card-based Layout**: Information displayed in digestible card components
- **Tabs Interface**: Organized content access through tab navigation
- **Toast Notifications**: Non-intrusive user feedback system
- **Data Visualization**: Interactive charts and graphs for analytics
- **Responsive Design**: Mobile and desktop compatible layouts
- **Theme Support**: Light/dark mode via ThemeProvider
- **Animated Transitions**: Smooth UI interactions between views

## Future Enhancements

Planned features for future releases:

- **AI-powered Ad Optimization**: Automatic optimization of ad copy and targeting
- **Campaign Templates**: Save and reuse successful campaign configurations
- **Advanced Budget Management**: Set and track campaign budgets across platforms
- **Integration with ATS**: Connect with Applicant Tracking Systems
- **A/B Testing Tools**: Test different ad variations for optimal performance
- **Advanced Analytics**: More detailed performance metrics and insights
- **Custom Reporting**: Build and save custom report configurations