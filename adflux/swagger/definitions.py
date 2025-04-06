"""
Definiciones de modelos para Swagger UI.

Este módulo contiene las definiciones de modelos para Swagger UI.
"""

# Definir las definiciones de modelos
DEFINITIONS = {
    "JobOpening": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "description": "Unique identifier for the job opening"
            },
            "title": {
                "type": "string",
                "description": "Job title"
            },
            "description": {
                "type": "string",
                "description": "Job description"
            },
            "location": {
                "type": "string",
                "description": "Job location"
            },
            "company_name": {
                "type": "string",
                "description": "Company name"
            },
            "required_skills": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Required skills for the job"
            },
            "salary_min": {
                "type": "integer",
                "description": "Minimum salary"
            },
            "salary_max": {
                "type": "integer",
                "description": "Maximum salary"
            },
            "posted_date": {
                "type": "string",
                "format": "date",
                "description": "Date when the job was posted"
            },
            "status": {
                "type": "string",
                "description": "Job status",
                "enum": ["open", "closed", "draft"]
            },
            "employment_type": {
                "type": "string",
                "description": "Employment type",
                "enum": ["Full-time", "Part-time", "Contract", "Temporary", "Internship"]
            },
            "experience_level": {
                "type": "string",
                "description": "Experience level",
                "enum": ["Entry-level", "Mid-level", "Senior", "Executive"]
            },
            "education_level": {
                "type": "string",
                "description": "Education level",
                "enum": ["High School", "Technical", "Bachelor's", "Master's", "PhD"]
            },
            "department": {
                "type": "string",
                "description": "Department"
            },
            "remote": {
                "type": "boolean",
                "description": "Whether the job is remote"
            },
            "application_url": {
                "type": "string",
                "description": "URL to apply for the job"
            },
            "closing_date": {
                "type": "string",
                "format": "date",
                "description": "Date when the job closes"
            },
            "short_description": {
                "type": "string",
                "description": "Short description for ads"
            },
            "benefits": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Benefits offered"
            },
            "target_segments": {
                "type": "array",
                "items": {
                    "type": "integer"
                },
                "description": "Target segment IDs"
            }
        },
        "required": ["job_id", "title"]
    },
    "Candidate": {
        "type": "object",
        "properties": {
            "candidate_id": {
                "type": "string",
                "description": "Unique identifier for the candidate"
            },
            "name": {
                "type": "string",
                "description": "Candidate name"
            },
            "email": {
                "type": "string",
                "description": "Candidate email"
            },
            "phone": {
                "type": "string",
                "description": "Candidate phone"
            },
            "location": {
                "type": "string",
                "description": "Candidate location"
            },
            "years_experience": {
                "type": "integer",
                "description": "Years of experience"
            },
            "education_level": {
                "type": "string",
                "description": "Education level",
                "enum": ["High School", "Technical", "Bachelor's", "Master's", "PhD"]
            },
            "skills": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Candidate skills"
            },
            "primary_skill": {
                "type": "string",
                "description": "Primary skill"
            },
            "desired_salary": {
                "type": "integer",
                "description": "Desired salary"
            },
            "desired_position": {
                "type": "string",
                "description": "Desired position"
            },
            "summary": {
                "type": "string",
                "description": "Candidate summary"
            },
            "availability": {
                "type": "string",
                "description": "Availability"
            },
            "languages": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Languages spoken"
            },
            "job_id": {
                "type": "string",
                "description": "Job ID the candidate is associated with"
            },
            "segment_id": {
                "type": "integer",
                "description": "Segment ID the candidate belongs to"
            }
        },
        "required": ["candidate_id", "name"]
    },
    "Application": {
        "type": "object",
        "properties": {
            "application_id": {
                "type": "integer",
                "description": "Unique identifier for the application"
            },
            "job_id": {
                "type": "string",
                "description": "Job ID"
            },
            "candidate_id": {
                "type": "string",
                "description": "Candidate ID"
            },
            "application_date": {
                "type": "string",
                "format": "date",
                "description": "Date of application"
            },
            "status": {
                "type": "string",
                "description": "Application status",
                "enum": ["Submitted", "In Review", "Rejected", "Hired"]
            },
            "source_platform": {
                "type": "string",
                "description": "Source platform",
                "enum": ["Meta", "Google", "LinkedIn", "Direct"]
            },
            "notes": {
                "type": "string",
                "description": "Notes"
            },
            "resume_path": {
                "type": "string",
                "description": "Path to resume"
            },
            "cover_letter_path": {
                "type": "string",
                "description": "Path to cover letter"
            }
        },
        "required": ["job_id", "candidate_id"]
    },
    "MetaCampaign": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Meta campaign ID"
            },
            "name": {
                "type": "string",
                "description": "Campaign name"
            },
            "status": {
                "type": "string",
                "description": "Campaign status"
            },
            "objective": {
                "type": "string",
                "description": "Campaign objective"
            },
            "effective_status": {
                "type": "string",
                "description": "Effective status"
            },
            "created_time": {
                "type": "string",
                "format": "date-time",
                "description": "Creation time"
            },
            "start_time": {
                "type": "string",
                "format": "date-time",
                "description": "Start time"
            },
            "stop_time": {
                "type": "string",
                "format": "date-time",
                "description": "Stop time"
            },
            "daily_budget": {
                "type": "string",
                "description": "Daily budget"
            },
            "lifetime_budget": {
                "type": "string",
                "description": "Lifetime budget"
            },
            "budget_remaining": {
                "type": "string",
                "description": "Budget remaining"
            },
            "account_id": {
                "type": "string",
                "description": "Ad account ID"
            }
        },
        "required": ["id"]
    },
    "MetaAdSet": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Meta ad set ID"
            },
            "name": {
                "type": "string",
                "description": "Ad set name"
            },
            "status": {
                "type": "string",
                "description": "Ad set status"
            },
            "effective_status": {
                "type": "string",
                "description": "Effective status"
            },
            "daily_budget": {
                "type": "string",
                "description": "Daily budget"
            },
            "lifetime_budget": {
                "type": "string",
                "description": "Lifetime budget"
            },
            "budget_remaining": {
                "type": "string",
                "description": "Budget remaining"
            },
            "optimization_goal": {
                "type": "string",
                "description": "Optimization goal"
            },
            "billing_event": {
                "type": "string",
                "description": "Billing event"
            },
            "bid_amount": {
                "type": "string",
                "description": "Bid amount"
            },
            "created_time": {
                "type": "string",
                "format": "date-time",
                "description": "Creation time"
            },
            "start_time": {
                "type": "string",
                "format": "date-time",
                "description": "Start time"
            },
            "end_time": {
                "type": "string",
                "format": "date-time",
                "description": "End time"
            },
            "campaign_id": {
                "type": "string",
                "description": "Campaign ID"
            },
            "targeting": {
                "type": "object",
                "description": "Targeting specifications"
            }
        },
        "required": ["id", "campaign_id"]
    },
    "MetaAd": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Meta ad ID"
            },
            "name": {
                "type": "string",
                "description": "Ad name"
            },
            "status": {
                "type": "string",
                "description": "Ad status"
            },
            "effective_status": {
                "type": "string",
                "description": "Effective status"
            },
            "created_time": {
                "type": "string",
                "format": "date-time",
                "description": "Creation time"
            },
            "creative_id": {
                "type": "string",
                "description": "Creative ID"
            },
            "creative_details": {
                "type": "object",
                "description": "Creative details"
            },
            "ad_set_id": {
                "type": "string",
                "description": "Ad set ID"
            },
            "preview_url": {
                "type": "string",
                "description": "Preview URL"
            }
        },
        "required": ["id", "ad_set_id"]
    },
    "MetaInsight": {
        "type": "object",
        "properties": {
            "object_id": {
                "type": "string",
                "description": "Object ID"
            },
            "level": {
                "type": "string",
                "description": "Level",
                "enum": ["campaign", "adset", "ad", "account"]
            },
            "date_start": {
                "type": "string",
                "format": "date",
                "description": "Start date"
            },
            "date_stop": {
                "type": "string",
                "format": "date",
                "description": "End date"
            },
            "impressions": {
                "type": "integer",
                "description": "Impressions"
            },
            "clicks": {
                "type": "integer",
                "description": "Clicks"
            },
            "spend": {
                "type": "number",
                "format": "float",
                "description": "Spend"
            },
            "cpc": {
                "type": "number",
                "format": "float",
                "description": "Cost per click"
            },
            "cpm": {
                "type": "number",
                "format": "float",
                "description": "Cost per 1000 impressions"
            },
            "ctr": {
                "type": "number",
                "format": "float",
                "description": "Click-through rate"
            },
            "cpp": {
                "type": "number",
                "format": "float",
                "description": "Cost per result"
            },
            "frequency": {
                "type": "number",
                "format": "float",
                "description": "Frequency"
            },
            "reach": {
                "type": "integer",
                "description": "Reach"
            },
            "unique_clicks": {
                "type": "integer",
                "description": "Unique clicks"
            },
            "unique_ctr": {
                "type": "number",
                "format": "float",
                "description": "Unique click-through rate"
            },
            "actions": {
                "type": "object",
                "description": "Actions"
            },
            "action_values": {
                "type": "object",
                "description": "Action values"
            },
            "submit_applications": {
                "type": "integer",
                "description": "Submit applications"
            },
            "submit_applications_value": {
                "type": "number",
                "format": "float",
                "description": "Submit applications value"
            },
            "leads": {
                "type": "integer",
                "description": "Leads"
            },
            "leads_value": {
                "type": "number",
                "format": "float",
                "description": "Leads value"
            },
            "view_content": {
                "type": "integer",
                "description": "View content"
            },
            "view_content_value": {
                "type": "number",
                "format": "float",
                "description": "View content value"
            }
        },
        "required": ["object_id", "level", "date_start", "date_stop"]
    },
    "Campaign": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Campaign ID"
            },
            "name": {
                "type": "string",
                "description": "Campaign name"
            },
            "description": {
                "type": "string",
                "description": "Campaign description"
            },
            "platform": {
                "type": "string",
                "description": "Platform",
                "enum": ["meta", "google"]
            },
            "status": {
                "type": "string",
                "description": "Campaign status",
                "enum": ["draft", "active", "paused", "archived"]
            },
            "daily_budget": {
                "type": "integer",
                "description": "Daily budget in cents"
            },
            "start_date": {
                "type": "string",
                "format": "date-time",
                "description": "Start date"
            },
            "end_date": {
                "type": "string",
                "format": "date-time",
                "description": "End date"
            },
            "job_opening_id": {
                "type": "string",
                "description": "Job opening ID"
            },
            "target_segment_ids": {
                "type": "array",
                "items": {
                    "type": "integer"
                },
                "description": "Target segment IDs"
            },
            "primary_text": {
                "type": "string",
                "description": "Primary text"
            },
            "headline": {
                "type": "string",
                "description": "Headline"
            },
            "link_description": {
                "type": "string",
                "description": "Link description"
            },
            "creative_image_filename": {
                "type": "string",
                "description": "Creative image filename"
            },
            "landing_page_url": {
                "type": "string",
                "description": "Landing page URL"
            },
            "external_id": {
                "type": "string",
                "description": "External ID"
            },
            "external_ids": {
                "type": "object",
                "description": "External IDs"
            },
            "created_at": {
                "type": "string",
                "format": "date-time",
                "description": "Creation time"
            },
            "updated_at": {
                "type": "string",
                "format": "date-time",
                "description": "Update time"
            }
        },
        "required": ["name", "platform", "status"]
    }
}
