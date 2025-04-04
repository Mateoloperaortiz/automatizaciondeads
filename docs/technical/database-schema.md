# AdFlux Database Schema

This document describes the database schema used by the AdFlux system. The schema is implemented using SQLAlchemy ORM and is compatible with PostgreSQL and SQLite (for development).

## Entity Relationship Diagram

```
+----------------+       +----------------+       +----------------+
| JobOpening     |       | Application    |       | Candidate      |
+----------------+       +----------------+       +----------------+
| job_id (PK)    |<----->| application_id |<----->| candidate_id   |
| title          |       | job_id (FK)    |       | name           |
| description    |       | candidate_id   |       | location       |
| location       |       | status         |       | years_exp      |
| company        |       | date           |       | education      |
| required_skills|       |                |       | skills         |
| salary_min     |       |                |       | primary_skill  |
| salary_max     |       |                |       | desired_salary |
| posted_date    |       |                |       | segment_id (FK)|
| status         |       |                |       |                |
| target_segments|       |                |       |                |
+----------------+       +----------------+       +----------------+
        |                                                 |
        |                                                 |
        v                                                 v
+----------------+                               +----------------+
| Campaign       |                               | Segment        |
+----------------+                               +----------------+
| id (PK)        |                               | id (PK)        |
| name           |                               | name           |
| description    |                               | description    |
| platform       |                               |                |
| status         |                               |                |
| daily_budget   |                               |                |
| job_opening_id |                               |                |
| target_segments|                               |                |
| primary_text   |                               |                |
| headline       |                               |                |
| link_desc      |                               |                |
| image_filename |                               |                |
| external_ids   |                               |                |
| created_at     |                               |                |
| updated_at     |                               |                |
+----------------+                               +----------------+
        |
        |
        v
+----------------+       +----------------+       +----------------+
| MetaCampaign   |       | MetaAdSet      |       | MetaAd         |
+----------------+       +----------------+       +----------------+
| id (PK)        |<----->| id (PK)        |<----->| id (PK)        |
| name           |       | name           |       | name           |
| status         |       | status         |       | status         |
| objective      |       | effective_stat |       | effective_stat |
| effective_stat |       | daily_budget   |       | created_time   |
| created_time   |       | lifetime_budget|       | creative_id    |
| start_time     |       | budget_remain  |       | creative_detail|
| stop_time      |       | optimization   |       | ad_set_id (FK) |
| daily_budget   |       | billing_event  |       | last_updated   |
| lifetime_budget|       | bid_amount     |       |                |
| budget_remain  |       | created_time   |       |                |
| account_id     |       | start_time     |       |                |
| last_updated   |       | end_time       |       |                |
|                |       | campaign_id(FK)|       |                |
+----------------+       +----------------+       +----------------+
        |                        |                        |
        |                        |                        |
        v                        v                        v
+----------------+       +----------------+       +----------------+
| MetaInsight    |       | MetaInsight    |       | MetaInsight    |
+----------------+       +----------------+       +----------------+
| object_id (PK) |       | object_id (PK) |       | object_id (PK) |
| level (PK)     |       | level (PK)     |       | level (PK)     |
| date_start (PK)|       | date_start (PK)|       | date_start (PK)|
| date_stop      |       | date_stop      |       | date_stop      |
| impressions    |       | impressions    |       | impressions    |
| clicks         |       | clicks         |       | clicks         |
| spend          |       | spend          |       | spend          |
| cpc            |       | cpc            |       | cpc            |
| cpm            |       | cpm            |       | cpm            |
| ctr            |       | ctr            |       | ctr            |
| ...            |       | ...            |       | ...            |
+----------------+       +----------------+       +----------------+
```

## Table Descriptions

### JobOpening

Represents a job opening that can be advertised.

| Column | Type | Description |
|--------|------|-------------|
| job_id | String | Primary key, unique identifier for the job (e.g., JOB-0001) |
| title | String | Job title |
| description | Text | Detailed job description |
| location | String | Job location |
| company | String | Company offering the job |
| required_skills | JSON | List of required skills |
| salary_min | Integer | Minimum salary offered |
| salary_max | Integer | Maximum salary offered |
| posted_date | Date | Date when the job was posted |
| status | String | Status of the job (e.g., open, closed) |
| target_segments | JSON | List of candidate segment IDs for targeting |

### Candidate

Represents a job seeker.

| Column | Type | Description |
|--------|------|-------------|
| candidate_id | String | Primary key, unique identifier for the candidate (e.g., CAND-00001) |
| name | String | Candidate's name |
| location | String | Candidate's location |
| years_experience | Integer | Years of professional experience |
| education_level | String | Highest education level |
| skills | JSON | List of skills |
| primary_skill | String | Primary skill or specialization |
| desired_salary | Integer | Desired salary |
| segment_id | Integer | Foreign key to Segment table |

### Segment

Represents a segment of candidates created by the ML model.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key, unique identifier for the segment |
| name | String | Segment name |
| description | Text | Segment description |

### Application

Represents a candidate's application for a job opening.

| Column | Type | Description |
|--------|------|-------------|
| application_id | Integer | Primary key, unique identifier for the application |
| job_id | String | Foreign key to JobOpening table |
| candidate_id | String | Foreign key to Candidate table |
| application_date | Date | Date of application |
| status | String | Status of the application (e.g., Submitted, Under Review, Rejected, Hired) |

### Campaign

Represents an advertising campaign for a job opening.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key, unique identifier for the campaign |
| name | String | Campaign name |
| description | Text | Campaign description |
| platform | String | Platform for the campaign (e.g., meta, google) |
| status | String | Status of the campaign (e.g., draft, active, paused, archived) |
| daily_budget | Integer | Daily budget in cents (e.g., 500 for $5.00) |
| job_opening_id | String | Foreign key to JobOpening table |
| target_segment_ids | JSON | List of segment IDs to target |
| primary_text | String | Primary text for the ad |
| headline | String | Headline for the ad |
| link_description | String | Description for the ad link |
| creative_image_filename | String | Filename of the uploaded image |
| external_ids | JSON | IDs from external platforms after publishing |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### MetaCampaign

Represents a campaign on Meta (Facebook/Instagram).

| Column | Type | Description |
|--------|------|-------------|
| id | String | Primary key, Meta's campaign ID |
| name | String | Campaign name |
| status | String | Campaign status |
| objective | String | Campaign objective |
| effective_status | String | Effective status |
| created_time | DateTime | Creation timestamp |
| start_time | DateTime | Start timestamp |
| stop_time | DateTime | Stop timestamp |
| daily_budget | String | Daily budget |
| lifetime_budget | String | Lifetime budget |
| budget_remaining | String | Remaining budget |
| account_id | String | Meta Ad Account ID |
| last_updated | DateTime | Last update timestamp |

### MetaAdSet

Represents an ad set on Meta (Facebook/Instagram).

| Column | Type | Description |
|--------|------|-------------|
| id | String | Primary key, Meta's ad set ID |
| name | String | Ad set name |
| status | String | Ad set status |
| effective_status | String | Effective status |
| daily_budget | String | Daily budget |
| lifetime_budget | String | Lifetime budget |
| budget_remaining | String | Remaining budget |
| optimization_goal | String | Optimization goal |
| billing_event | String | Billing event |
| bid_amount | String | Bid amount |
| created_time | DateTime | Creation timestamp |
| start_time | DateTime | Start timestamp |
| end_time | DateTime | End timestamp |
| campaign_id | String | Foreign key to MetaCampaign table |
| last_updated | DateTime | Last update timestamp |

### MetaAd

Represents an ad on Meta (Facebook/Instagram).

| Column | Type | Description |
|--------|------|-------------|
| id | String | Primary key, Meta's ad ID |
| name | String | Ad name |
| status | String | Ad status |
| effective_status | String | Effective status |
| created_time | DateTime | Creation timestamp |
| creative_id | String | Creative ID |
| creative_details | JSON | Creative details |
| ad_set_id | String | Foreign key to MetaAdSet table |
| last_updated | DateTime | Last update timestamp |

### MetaInsight

Represents performance metrics for Meta ads.

| Column | Type | Description |
|--------|------|-------------|
| object_id | String | Part of composite primary key, ID of the object (campaign, ad set, or ad) |
| level | String | Part of composite primary key, level of the insight (campaign, adset, ad, account) |
| date_start | Date | Part of composite primary key, start date of the insight |
| date_stop | Date | End date of the insight |
| impressions | Integer | Number of impressions |
| clicks | Integer | Number of clicks |
| spend | Float | Amount spent |
| cpc | Float | Cost per click |
| cpm | Float | Cost per thousand impressions |
| ctr | Float | Click-through rate |
| cpp | Float | Cost per result |
| frequency | Float | Average frequency |
| reach | Integer | Reach |
| unique_clicks | Integer | Unique clicks |
| unique_ctr | Float | Unique click-through rate |
| actions | JSON | Array of action type breakdowns |
| action_values | JSON | Array of action value breakdowns |
| submit_applications | Integer | Number of application submissions |
| submit_applications_value | Float | Value of application submissions |
| leads | Integer | Number of leads |
| leads_value | Float | Value of leads |
| view_content | Integer | Number of content views |
| view_content_value | Float | Value of content views |
| meta_campaign_id | String | Foreign key to MetaCampaign table |
| meta_ad_set_id | String | Foreign key to MetaAdSet table |
| meta_ad_id | String | Foreign key to MetaAd table |
| created_at | DateTime | Creation timestamp |
| last_updated | DateTime | Last update timestamp |

## Relationships

1. **JobOpening to Application**: One-to-many relationship. A job opening can have multiple applications.
2. **Candidate to Application**: One-to-many relationship. A candidate can have multiple applications.
3. **Segment to Candidate**: One-to-many relationship. A segment can contain multiple candidates.
4. **JobOpening to Campaign**: One-to-many relationship. A job opening can have multiple campaigns.
5. **MetaCampaign to MetaAdSet**: One-to-many relationship. A Meta campaign can have multiple ad sets.
6. **MetaAdSet to MetaAd**: One-to-many relationship. A Meta ad set can have multiple ads.
7. **MetaCampaign/MetaAdSet/MetaAd to MetaInsight**: One-to-many relationship. Each Meta object can have multiple insights.

## Indexes

The following indexes are defined to optimize query performance:

1. **JobOpening**: Index on `status` for filtering active job openings
2. **Candidate**: Index on `segment_id` for filtering candidates by segment
3. **Campaign**: Indexes on `platform` and `status` for filtering campaigns
4. **Application**: Unique constraint on `job_id` and `candidate_id` to prevent duplicate applications
5. **MetaInsight**: Indexes on `object_id`, `level`, and `date_start` for filtering insights

## Data Types

1. **JSON Fields**: Stored as JSON in PostgreSQL and as text in SQLite
2. **Date/DateTime Fields**: Stored as date/timestamp in PostgreSQL and as text in SQLite
3. **Text Fields**: Stored as text in both PostgreSQL and SQLite
4. **Numeric Fields**: Stored as appropriate numeric types in PostgreSQL and as numeric in SQLite

## Migrations

Database migrations are managed using Flask-Migrate (based on Alembic). Migration scripts are stored in the `migrations` directory and can be applied using the `flask db upgrade` command.
