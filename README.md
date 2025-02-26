# Magneto Ads Booster - Proof of Concept

## 📋 Project Overview

Magneto Ads Booster is a comprehensive platform designed to automate the creation, management, and optimization of job recruitment advertisements across multiple social media platforms. This proof of concept (POC) demonstrates the core functionality for Sprint 1, providing a foundation for the complete solution.

### 🎯 Business Problem

- Social media platforms are essential for marketing job vacancies and reaching potential candidates
- The current process of creating and publishing job ads is manual, time-consuming, and inefficient
- Each platform requires different creative formats and targeting parameters
- HR teams spend excessive time on repetitive tasks that could be automated
- Critical vacancies often don't receive adequate visibility due to the manual effort required

### 💡 Solution

Magneto Ads Booster solves these challenges by:
- Centralizing the management of job advertising across multiple platforms
- Automating the creation and adaptation of ad creatives for different platforms
- Providing a unified interface for monitoring performance
- Integrating with existing ATS (Applicant Tracking System) to import job data
- Implementing role-based access control for team collaboration

## 🌟 Key Features Implemented in POC

### 1️⃣ User Authentication & Authorization
- Secure login system using NextAuth.js
- Role-based access control with three distinct user roles:
  - **Admin**: Full system access, user management, platform settings
  - **Manager**: Campaign creation and monitoring, performance analytics
  - **Creator**: Ad creative design and platform-specific adaptation
- Session management and secure cookie-based authentication

### 2️⃣ Platform Connections
- OAuth integration framework for social media platforms
- Connection management for:
  - Meta (Facebook, Instagram)
  - Google Ads
  - X (Twitter)
  - TikTok
- Token storage and refresh mechanism
- Connection status monitoring

### 3️⃣ Vacancy Management
- Import interface for ATS integration
- Vacancy listing and details view
- Filtering and search functionality
- Assignment to campaigns

### 4️⃣ Campaign Management
- Campaign creation wizard with multi-step form
- Campaign details view with performance metrics
- Campaign listing with status indicators
- Creative assignment to campaigns

### 5️⃣ Creative Management
- Creative upload and storage
- Platform-specific adaptation
- Preview functionality
- Version tracking

### 6️⃣ Admin Tools
- User management interface
- System settings configuration
- Platform settings management
- Role assignment

## 🛠️ Technical Architecture

### 💻 Frontend
- **Framework**: Next.js 14 with React 18
- **Language**: TypeScript for type safety
- **Styling**: TailwindCSS for responsive design
- **State Management**: React Context API
- **Form Handling**: React Hook Form

### 🔧 Backend
- **API Routes**: Next.js API routes
- **Authentication**: NextAuth.js with JWT
- **Database Access**: Prisma ORM
- **Platform Integration**: Custom API clients

### 🗄️ Database
- **Database**: PostgreSQL (hosted on Supabase)
- **ORM**: Prisma for type-safe database access
- **Schema**: Normalized relational structure

## 📊 Database Schema

The database schema includes the following main entities:

### User
- Authentication credentials
- Profile information
- Role assignment

### PlatformConnection
- OAuth tokens
- Platform-specific details
- Connection status

### Vacancy
- Job details from ATS
- Status and visibility settings
- Associated campaigns

### Campaign
- Goals and targeting parameters
- Budget and timeline
- Performance metrics

### Creative
- Original creative assets
- Metadata and usage information
- Version history

### CreativeAdaptation
- Platform-specific versions
- Format specifications
- Publishing status

### PlatformFormat
- Requirements by platform
- Dimension specifications
- Content guidelines

## 🚀 Installation & Setup

### Prerequisites
- Node.js 18.x or higher
- PostgreSQL database
- Developer accounts for platform APIs (Meta, Google, etc.)

### Installation Steps
1. Clone the repository:
   ```
   git clone https://github.com/Mateoloperaortiz/automatizaciondeads.git
   cd automatizaciondeads
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env.local`
   - Update the values for database connection, API keys, and OAuth credentials

4. Set up the database:
   ```
   npx prisma migrate dev
   npx prisma db seed
   ```

5. Start the development server:
   ```
   npm run dev
   ```

6. Access the application at `http://localhost:3000`

### Test Credentials
- **Admin**: `admin@example.com` / `password`
- **User**: `user@example.com` / `password`

## 👥 User Roles & Permissions

### Admin
- Create and manage user accounts
- Configure system settings
- Manage platform connections
- Access all system features
- View analytics and reports

### Manager
- Create and manage campaigns
- Assign vacancies to campaigns
- Monitor campaign performance
- Approve creatives

### Creator
- Design ad creatives
- Adapt creatives for different platforms
- Upload and manage creative assets

## 📱 Key Interfaces

### Dashboard
The main dashboard provides an overview of:
- Platform connection status
- Campaign performance metrics
- Recent activities
- Quick access to common tasks

### Campaign Management
- **Campaign List**: Overview of all campaigns with status and key metrics
- **Campaign Details**: In-depth view of campaign performance, associated vacancies, and creatives
- **Campaign Creation**: Multi-step wizard for creating new campaigns

### Vacancy Management
- **Vacancy List**: Searchable and filterable list of all job vacancies
- **Vacancy Details**: Complete information about a specific vacancy
- **Vacancy Import**: Interface for importing vacancies from ATS

### Ad Creative Management
- **Creative List**: Gallery view of all creative assets
- **Creative Adaptation**: Tools for adapting creatives to different platform requirements
- **Creative Preview**: Visual preview of how creatives will appear on various platforms

### Platform Connection
- Connection status for each platform
- OAuth authorization flow
- Token management

### Admin Section
- **User Management**: Interface for creating and managing users
- **System Settings**: Configuration options for the application
- **Platform Settings**: Platform-specific configuration

## 🧪 Testing

### Authentication Testing
- Test accounts for each role (Admin, Manager, Creator)
- Token expiration and refresh functionality
- Protected route access control

### Platform Integration Testing
- Mock API responses for development
- OAuth flow verification
- Token storage and security

### Performance Testing
- Loading time optimization
- Database query performance
- Network request efficiency

## ⚠️ Current Limitations

This proof of concept has the following limitations:

1. **Mock Data**: Uses mock data instead of real database queries for some features
2. **Platform Integration**: Simulated OAuth flows without actual API calls
3. **Analytics**: Placeholder metrics instead of real-time data
4. **Error Handling**: Basic error handling without comprehensive recovery mechanisms
5. **User Registration**: Limited to admin-created accounts, no self-registration
6. **Security**: Basic implementation without advanced security features

## 🛣️ Future Roadmap

### Sprint 2: Platform Integration
- Complete OAuth integration with Meta and Google Ads
- Implement actual API calls for ad creation
- Develop platform-specific ad templates

### Sprint 3: Analytics & Optimization
- Real-time performance tracking
- Budget management
- A/B testing framework

### Sprint 4: Advanced Features
- AI-powered creative suggestions
- Automated budget allocation
- Advanced targeting options

### Sprint 5: Production Readiness
- Comprehensive security audit
- Performance optimization
- Documentation and training materials

## 🔒 Security Considerations

- **Authentication**: JWT-based authentication with secure storage
- **Authorization**: Role-based access control for all routes and operations
- **Data Protection**: Environment-specific configuration for sensitive information
- **API Security**: Rate limiting and request validation
- **Token Management**: Secure storage and refresh of OAuth tokens

## 📚 Technical Documentation

Additional technical documentation is available in the `/docs` directory:

- [POC Implementation Guide](./docs/poc-implementation.md)
- [API Documentation](./docs/api-documentation.md) (placeholder)
- [Database Schema](./docs/database-schema.md) (placeholder)

## 🔄 Development Process

The development process followed these steps:

1. **Requirements Analysis**: Understanding the business needs and technical constraints
2. **Architecture Design**: Designing the system architecture and component interactions
3. **Database Schema**: Defining the data model and relationships
4. **UI/UX Design**: Creating wireframes and UI components
5. **Implementation**: Developing the core functionality
6. **Testing**: Validating the functionality against requirements
7. **Documentation**: Creating comprehensive documentation

## 👨‍💻 Development Team

This proof of concept was developed by:
- Mateo Lopera Ortiz

## 📅 Project Timeline

- **Sprint 1 (POC)**: February 2025 - Current stage
- **Planned Full Implementation**: March-June 2025

## 🙏 Acknowledgments

- NextAuth.js for authentication framework
- TailwindCSS for UI components
- Prisma team for the excellent ORM
- Supabase for database hosting

## 📝 Evaluation Criteria

This proof of concept addresses the following evaluation criteria:

1. **Functionality**: Demonstrates core features and user flows
2. **Architecture**: Shows a scalable and maintainable system design
3. **Code Quality**: Implements clean, typed, and documented code
4. **User Experience**: Provides an intuitive and responsive interface
5. **Documentation**: Includes comprehensive technical and user documentation
6. **Problem Solving**: Addresses the business challenges effectively

## 📞 Contact

For any questions or further information, please contact:
- Email: mloperao1@eafit.edu.co, ehernandem@eafit.edu.co, myriverac@eafit.edu.co, mfalvarezm@eafit.edu.co
- GitHub: [Mateoloperaortiz](https://github.com/Mateoloperaortiz)
