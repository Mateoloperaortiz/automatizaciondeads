# Project: Ads Automation Platform

## 1. Overview

This document outlines the plan for building an Ads Automation platform. The primary goal is to automate the process of posting job advertisements across various social media channels, initially targeting candidates for an organization referred to as "Magneto." This will save time and money compared to manual posting and enable targeted advertising to expand the visibility of critical vacancies.

*   **Problem:** Manual, slow, and costly process of posting job ads across multiple social media platforms.
*   **Goal:** Implement an automated workflow for creating, targeting, and posting job ads.
*   **Initial Target User:** "Magneto" (representing businesses needing to advertise jobs).

## 2. Core Features & Scope (MVP)

### 2.1. Target Social Media Platforms (MVP)

The initial version will focus on integration with three primary advertising platforms:

1.  **Meta (Facebook/Instagram)**
2.  **X (formerly Twitter)**
3.  **Google Ads**

### 2.2. MVP Job Ad Definition

The core entity will be a "Job Ad," with the following attributes for the Minimum Viable Product:

| Attribute                     | Purpose in v1                                       | Notes / Validation Rule                        |
| ----------------------------- | --------------------------------------------------- | ---------------------------------------------- |
| `job_id` (UUID/Serial)        | Internal primary key                                | Auto-generated                                 |
| `team_id`                     | Links ad to a specific team/client (Magneto)        | FK to `teams` table                            |
| `title`                       | Display headline across platforms                   | ≤ 100 chars (fits Meta/X)                      |
| `description_short`           | Universal body copy                                 | ≤ 280 chars (single tweet / Google headline)   |
| `description_long`            | Richer text for platforms that allow it             | Optional; defaults to `description_short`      |
| `target_url`                  | Landing page for applicants                         | Must be HTTPS & ideally owned by the client    |
| `creative_asset_url`          | URL for one image or vertical video                 | Optional; fallback to platform default/none    |
| `platforms[]`                 | Channels to post (`meta`, `x`, `google`)            | Array-like storage (e.g., boolean flags)       |
| `budget_daily`                | Flat daily spend in local currency                  | ≥ $1 (or platform minimum); enforced by adapters |
| `schedule_start` / `end`      | Date range (ISO 8601)                               | `end` optional ⇒ open-ended                    |
| `status`                      | Simplest life-cycle (`draft`, `scheduled`, `live`, `paused`, `archived`) | Default: `draft`                               |
| `created_by_user_id`          | Tracks which user created the ad                    | FK to `users` table                            |
| `created_at` / `updated_at`   | Audit & analytics                                   | Auto-generated timestamps                      |

### 2.3. MVP Audience Targeting Pipeline

A sophisticated, unsupervised approach to audience segmentation is planned:

| Stage                        | Minimal Feature                                                                                             | Implementation Choice                                    | Notes                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------- |
| **1. Input**                 | Accept job-ad text (+ optional CSV/JSON résumé dump)                                                        | Next.js REST endpoint (e.g., `/api/segment`)             |                                                     |
| **2. Vectorizer**            | Sentence-BERT MiniLM embeddings                                                                             | Python Microservice (`all-MiniLM-L6-v2`)                 | ≈ 80 ms / text on CPU                               |
| **3. Dim-Reduction**         | UMAP → 50 dims                                                                                              | Python Microservice                                      | Faster clustering, keeps local structure            |
| **4. Clustering**            | K-means++ with auto-k (silhouette, k ∈ [2,6])                                                              | Python Microservice                                      | Pure unsupervised, no labels needed                 |
| **5. Cluster Profiling**     | Top n-grams + zero-shot industry labels                                                                     | Python Microservice (HuggingFace `facebook/bart-large-mnli`) | Makes clusters interpretable                        |
| **6. Taxonomy Mapping**      | Static YAML maps → **audience primitives**: `industries[]`, `skills_keywords[]`, `locations[]`, `seniority` | Next.js Backend                                          | Small hand-maintained file covers Meta/Google/X     |
| **7. Platform Translators**  | Generate per-network JSON ad payloads                                                                       | Next.js Backend                                          | One worker/module per platform; retries & rate-limit aware |
| **8. Confidence Fallback**   | If cluster silhouette < 0.25 ⇒ use default "broad" template                                                 | Next.js Backend                                          | Guarantees campaign health even with noisy input    |
| **9. Logging**               | Store (cluster_id, ad_id, spend, clicks, applies)                                                         | Next.js Backend (Database)                               | Foundation for V2 supervised fine-tuning            |

## 3. Technical Architecture & Implementation Plan

The project will be built upon an existing SaaS boilerplate/template which provides a solid foundation.

### 3.1. Leveraging the Existing Template

The following components of the template will be utilized:

*   **User Management & Authentication:** User accounts, team structures, roles, and JWT-based session management.
*   **Subscription Management (Stripe):** Existing Stripe integration for handling team subscriptions to the service.
*   **Dashboard Layout:** Reusable sidebar navigation and main content area for new features.
*   **UI Components:** Pre-built UI components (shadcn/ui) for constructing new interfaces.
*   **Database ORM (Drizzle):** Drizzle ORM for defining schema and interacting with the PostgreSQL database.

### 3.2. Database Schema Modifications

New tables will be added to `lib/db/schema.ts`:

#### 3.2.1. `job_ads` Table
Stores all information related to individual job advertisements as defined in the MVP Job Ad Definition.
*   **Key fields:** `id`, `team_id`, `title`, `description_short`, `description_long`, `target_url`, `creative_asset_url`, platform booleans (`platforms_meta_enabled`, etc.), `budget_daily`, `schedule_start`, `schedule_end`, `status`, `created_by_user_id`, `created_at`, `updated_at`.

#### 3.2.2. `social_platform_connections` Table
Stores authentication tokens and connection details for each team's linked social media ad accounts.
*   **Key fields:** `id`, `team_id`, `platform_name` (e.g., 'meta', 'x'), `platform_user_id`, `platform_account_id` (ad account ID), `access_token` (encrypted), `refresh_token` (encrypted), `token_expires_at`, `scopes`, `status` ('active', 'needs_reauth'), `created_at`, `updated_at`.

**Relations:**
*   `teams` will have one-to-many relations with `job_ads` and `social_platform_connections`.
*   `users` will have a one-to-many relation with `job_ads` (for `created_by_user_id`).

**Token Encryption:** `access_token` and `refresh_token` in `social_platform_connections` will be encrypted at rest using a symmetric encryption algorithm (e.g., AES-256-GCM) with an encryption key stored securely in environment variables.

### 3.3. Python Microservice for Audience Segmentation

For the computationally intensive parts of the audience targeting pipeline (Stages 2-5: Vectorizer, Dimensionality Reduction, Clustering, Cluster Profiling), a separate Python microservice will be developed.

*   **Rationale:**
    *   Leverages Python's mature Machine Learning ecosystem (Hugging Face Transformers, scikit-learn, UMAP).
    *   Allows independent scaling of ML workloads.
    *   Prevents blocking the Node.js event loop in the main Next.js application.
    *   Clear separation of concerns.
*   **Interaction Flow:**
    1.  Next.js backend receives job ad text (and optional resume data) via an API endpoint.
    2.  Next.js backend makes an HTTP request to the Python microservice.
    3.  Python microservice performs ML tasks and returns structured audience data (e.g., cluster profiles or derived primitives).
    4.  Next.js backend processes these results for taxonomy mapping, platform translation, and ad posting.

### 3.4. Phased Development Approach

#### Phase 1: Core Job Ad Management & Initial Platform Connection (Meta)
*   **Database:** Implement schema changes for `job_ads` and `social_platform_connections`. Run migrations.
*   **Security:** Implement encryption/decryption utilities for tokens. Set up `ENCRYPTION_KEY` environment variable.
*   **UI (Dashboard):**
    *   Add "Job Ads" section to dashboard navigation.
    *   Develop pages/forms for Job Ad CRUD operations (list, create, edit).
    *   Develop UI for managing platform connections (initially Meta), including initiating OAuth and displaying status.
*   **Backend (Next.js):**
    *   Implement server actions for Job Ad CRUD.
    *   Implement OAuth 2.0 flow for Meta (redirect to Meta, callback handling, token storage).
    *   Basic API wrapper for Meta Ads to verify connection (e.g., fetch ad accounts).

#### Phase 2: Audience Targeting MVP & First End-to-End Ad Post (Meta)
*   **Python Microservice:** Develop and deploy the Python service for audience segmentation (Stages 2-5).
*   **Backend (Next.js):**
    *   Implement API endpoint to communicate with the Python microservice.
    *   Implement Taxonomy Mapping (Stage 6) using YAML.
    *   Implement Meta Ads Platform Translator (Stage 7) to create ad payloads.
    *   Implement Confidence Fallback logic (Stage 8).
    *   Implement basic logging for ad posting attempts and results (Stage 9).
*   **Automation:**
    *   Develop a simple scheduler (e.g., `node-cron` or similar) in Next.js to pick up `scheduled` job ads.
    *   Orchestrate the flow: fetch ad -> generate audience (call Python) -> translate -> post to Meta via API wrapper.
    *   Update ad status (`live`, `failed`).
*   **UI (Dashboard):**
    *   Allow users to trigger audience generation for a job ad.
    *   Display derived audience primitives for review.

#### Phase 3: Add X and Google Ads Integrations
*   Repeat relevant tasks from Phase 1 and Phase 2 for X (Twitter) Ads:
    *   Implement OAuth flow for X.
    *   Develop X Ads API wrapper.
    *   Extend Taxonomy Mapping and Platform Translator for X.
*   Repeat relevant tasks from Phase 1 and Phase 2 for Google Ads:
    *   Implement OAuth flow for Google Ads.
    *   Develop Google Ads API wrapper.
    *   Extend Taxonomy Mapping and Platform Translator for Google Ads.

## 4. Key Considerations

*   **Secrets Management:** Securely manage API keys, client secrets, JWT secret, and encryption keys using environment variables and appropriate access controls.
*   **Error Handling & Logging:** Implement robust error handling across the Next.js app, Python microservice, and API interactions. Centralized logging will be important.
*   **Rate Limiting:** Be mindful of and handle API rate limits for all social media platforms. Implement retry mechanisms with backoff.
*   **Scalability:** Design both the Next.js application and the Python microservice with scalability in mind, especially if handling many teams or frequent ad posts.
*   **Data Privacy & Compliance:** If handling candidate résumé data, ensure compliance with relevant data privacy regulations (e.g., GDPR, CCPA).

## 5. Next Steps (Immediate)

1.  **Database Migrations:** Generate and apply database migrations for the new `job_ads` and `social_platform_connections` tables using Drizzle Kit.
    *   `pnpm db:generate` (or `npm run db:generate`)
    *   `pnpm db:migrate` (or `npm run db:migrate`)
2.  **Implement Token Encryption Utilities:** Create helper functions for encrypting and decrypting tokens in `lib/security/crypto.ts` or similar.
3.  **Begin UI for Job Ads CRUD:** Start building the dashboard section for managing job ads.
4.  **Begin OAuth Flow for Meta:** Start implementing the server-side logic and UI triggers for Meta platform connection.
5.  **Setup Python Microservice Project:** Initialize the project structure for the Python microservice.

This plan provides a roadmap for the development of the Ads Automation Platform. It will be refined as development progresses and more insights are gained. 