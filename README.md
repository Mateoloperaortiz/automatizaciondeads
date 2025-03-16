# AdsMaster - Automatización de Ads

## Overview

AdsMaster is a modern web application designed to automate the process of publishing job vacancy advertisements across multiple social media platforms. This tool streamlines the previously manual and time-consuming process of creating, deploying, and analyzing ad campaigns, allowing for more efficient and targeted recruitment advertising.

## Features

### Campaign Management

- **Campaign Creation**: Intuitive workflow for creating job ad campaigns
- **Multi-platform Publishing**: Simultaneous publishing to Meta (Facebook/Instagram), X (Twitter), Google, TikTok, and Snapchat
- **Campaign Scheduling**: Schedule campaigns to run at optimal times
- **Campaign Status Tracking**: Monitor active, scheduled, ended, and draft campaigns

### Audience Targeting

- **Advanced Segmentation**: Target specific demographics based on job titles, skills, education, and location
- **Custom Audience Creation**: Create and save audience profiles for reuse
- **Intelligent Targeting**: Leverage non-supervised classification methods to optimize audience targeting

### Platform Integration

- **API Connections**: Seamless integration with social media advertising APIs
- **Authentication Management**: Secure API key storage and management
- **Platform-specific Optimizations**: Tailor content for each platform's requirements

### Analytics & Reporting

- **Performance Metrics**: Track views, clicks, and applications for each campaign
- **Visual Dashboards**: Interactive charts and graphs for data visualization
- **Platform Comparison**: Compare performance across different advertising platforms
- **Export Capabilities**: Download reports in various formats

### User Interface

- **Responsive Design**: Optimized for both desktop and mobile use
- **Magneto365 Brand Integration**: Consistent with Magneto365's visual identity
- **Dark/Light Mode**: Support for user theme preferences
- **Intuitive Navigation**: User-friendly dashboard and workflow

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

### Development Tools

- **ESLint**: JavaScript linting utility
- **TypeScript-ESLint**: TypeScript integration for ESLint
- **PostCSS**: Tool for transforming CSS with JavaScript plugins
- **Autoprefixer**: Plugin to parse CSS and add vendor prefixes

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
│   ├── providers/           # Provider components
│   ├── services/            # API and data services
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

- `npm run dev`: Start the development server
- `npm run build`: Build the application for production
- `npm run build:dev`: Build the application with development settings
- `npm run lint`: Run ESLint to check code quality
- `npm run preview`: Preview the production build locally

## Color Palette

The application follows Magneto365's brand guidelines with the following primary colors:

- Purple (#5D3B90) - Primary brand color
- Orange (#FF6B00) - Secondary accent color
- White (#FFFFFF) - Background and text on dark backgrounds
- Dark Gray (#333333) - Text and secondary UI elements

## Platform Support

AdsMaster currently supports integration with the following advertising platforms:

- Meta (Facebook/Instagram)
- X (Twitter)
- Google
- TikTok
- Snapchat

## Future Development

Planned enhancements include:

- AI-powered ad copy generation
- Enhanced audience targeting algorithms
- Additional platform integrations
- Advanced performance analytics
- A/B testing capabilities
