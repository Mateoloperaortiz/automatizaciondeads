# Audience Segmentation Feature

## Overview

The InspireAI platform now includes ML-powered audience segmentation that automatically analyzes job advertisements and determines the best target audience for each ad across Meta, X (Twitter), and Google Ads platforms.

## How It Works

### 1. **Automatic Segmentation**
When a job ad is scheduled and processed:
- The job description is sent to the Python ML service
- Text is converted to embeddings using Sentence-BERT
- UMAP reduces dimensions for efficient clustering  
- K-means assigns the ad to one of 3 pre-trained clusters
- Each cluster represents a different audience profile (e.g., Tech Support, Backend Dev, Sales)

### 2. **Confidence-Based Targeting**
- **High Confidence (≥25%)**: Uses specific audience targeting based on the assigned cluster
- **Low Confidence (<25%)**: Falls back to broad targeting to ensure ad delivery
- Confidence is calculated based on distance to cluster centroid

### 3. **Platform-Agnostic Mapping**
Segmentation results are mapped to standardized targeting parameters:
- **Industries**: TECH_SOFTWARE_DEV, BIZ_SALES, etc.
- **Skills**: Specific keywords from the cluster profile
- **Seniority**: SENIORITY_ENTRY, SENIORITY_MID, SENIORITY_SENIOR
- **Locations**: Can be derived from job ad or set to defaults

## User Interface

### Job List View
- Segmentation confidence badges show next to job status
- Green (>50%), Yellow (25-50%), Red (<25%) indicators

### Job Edit View
- **Audience Targeting & Segmentation** section shows:
  - Segmentation status
  - Assigned cluster and profile name
  - Confidence score with color coding
  - Derived audience segments
  - Platform-specific targeting parameters
  - Processing timestamp

### Test Segmentation Feature
- **"Test Segmentation"** button allows previewing targeting without publishing
- Shows real-time analysis results in a modal
- Helps users understand how their job descriptions affect targeting

## Database Schema

New fields added to `job_ads` table:
- `derivedAudiencePrimitives` (jsonb) - Raw segmentation results
- `audienceClusterId` (text) - Assigned cluster ID
- `audienceConfidence` (decimal) - Confidence score (0-1)
- `audienceClusterProfileName` (text) - Human-readable cluster name
- `mappedTargeting` (jsonb) - Platform-agnostic targeting
- `segmentationProcessedAt` (timestamp) - When segmentation was run

## API Endpoints

### Test Segmentation
```typescript
POST /api/jobs/test-segmentation
Body: { jobAdId: number }
Response: {
  segmentationData: {
    derivedAudiencePrimitives: AudiencePrimitive[]
    audienceClusterId: string
    audienceConfidence: number
    audienceClusterProfileName: string
    mappedTargeting: PlatformAgnosticTargeting
  }
}
```

### Python Segmentation Service
```
POST http://localhost:8000/segment
Body: { job_ad_text: string }
Response: {
  derived_audience_primitives: []
  assigned_cluster_id: string
  cluster_assignment_confidence: number
}
```

## Configuration

### Environment Variables
```
PYTHON_SEGMENTATION_SERVICE_URL=http://localhost:8000/segment
```

### Cluster Profiles
Located at `services/audience_segmentation_service/models/cluster_profiles.json`

Example:
```json
{
  "0": {
    "name": "Profile for Cluster 0 (e.g., Tech Support Roles)",
    "industry": "Customer Support",
    "skills": ["troubleshooting", "communication", "CRM"],
    "seniority": "Entry-Level",
    "keywords": ["helpdesk", "tier 1", "customer service"]
  }
}
```

## Training New Models

To train new segmentation models:

1. Update the job ads corpus:
   ```
   services/audience_segmentation_service/data/job_ads_corpus.json
   ```

2. Run the training script:
   ```bash
   cd services/audience_segmentation_service
   python train_models.py
   ```

3. Update cluster profiles based on analysis of the new clusters

## Monitoring & Debugging

- Check segmentation status in job list and edit views
- Low confidence scores indicate the ad doesn't match existing clusters well
- `segmentation_failed` status indicates service connectivity issues
- View Python service logs for detailed debugging

## Future Enhancements

1. **Manual Override**: Allow users to adjust automatic segmentation
2. **A/B Testing**: Compare performance of different segmentation strategies
3. **Feedback Loop**: Use ad performance data to improve clustering
4. **More Clusters**: Expand beyond 3 clusters for finer segmentation
5. **Custom Audiences**: Allow users to define their own audience profiles 