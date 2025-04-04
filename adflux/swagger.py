"""
Configuración de Swagger UI para la API de AdFlux
"""

from flask import Blueprint, render_template, send_from_directory, jsonify
import os
import json

# Crear un blueprint para Swagger UI
swagger_bp = Blueprint('swagger', __name__, url_prefix='/api')

# Definir la especificación JSON de Swagger
SWAGGER_SPEC = {
    "swagger": "2.0",
    "info": {
        "title": "AdFlux API",
        "description": "API for managing job openings and candidates",
        "version": "1.0"
    },
    "basePath": "/api",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "paths": {
        "/jobs": {
            "get": {
                "summary": "Get all job openings",
                "description": "Returns a list of all job openings",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/JobOpening"
                            }
                        }
                    }
                }
            },
            "post": {
                "summary": "Create a new job opening",
                "description": "Creates a new job opening",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "description": "Job opening object",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/JobOpening"
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Job opening created",
                        "schema": {
                            "$ref": "#/definitions/JobOpening"
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    }
                }
            }
        },
        "/jobs/{job_id}": {
            "get": {
                "summary": "Get job opening by ID",
                "description": "Returns a single job opening",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "job_id",
                        "in": "path",
                        "description": "ID of job opening to return",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "$ref": "#/definitions/JobOpening"
                        }
                    },
                    "404": {
                        "description": "Job opening not found"
                    }
                }
            },
            "put": {
                "summary": "Update job opening",
                "description": "Updates a job opening",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "job_id",
                        "in": "path",
                        "description": "ID of job opening to update",
                        "required": True,
                        "type": "string"
                    },
                    {
                        "in": "body",
                        "name": "body",
                        "description": "Job opening object",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/JobOpening"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Job opening updated",
                        "schema": {
                            "$ref": "#/definitions/JobOpening"
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    },
                    "404": {
                        "description": "Job opening not found"
                    }
                }
            },
            "delete": {
                "summary": "Delete job opening",
                "description": "Deletes a job opening",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "job_id",
                        "in": "path",
                        "description": "ID of job opening to delete",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Job opening deleted"
                    },
                    "404": {
                        "description": "Job opening not found"
                    }
                }
            }
        },
        "/candidates": {
            "get": {
                "summary": "Get all candidates",
                "description": "Returns a list of all candidates",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/Candidate"
                            }
                        }
                    }
                }
            },
            "post": {
                "summary": "Create a new candidate",
                "description": "Creates a new candidate",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "description": "Candidate object",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/Candidate"
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Candidate created",
                        "schema": {
                            "$ref": "#/definitions/Candidate"
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    }
                }
            }
        },
        "/candidates/{candidate_id}": {
            "get": {
                "summary": "Fetch a candidate given its identifier",
                "description": "Returns a single candidate",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "candidate_id",
                        "in": "path",
                        "description": "ID of candidate to return",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "$ref": "#/definitions/Candidate"
                        }
                    },
                    "404": {
                        "description": "Candidate not found"
                    }
                }
            },
            "put": {
                "summary": "Update a candidate",
                "description": "Updates a candidate",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "candidate_id",
                        "in": "path",
                        "description": "ID of candidate to update",
                        "required": True,
                        "type": "string"
                    },
                    {
                        "in": "body",
                        "name": "body",
                        "description": "Candidate object",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/Candidate"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Candidate updated",
                        "schema": {
                            "$ref": "#/definitions/Candidate"
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    },
                    "404": {
                        "description": "Candidate not found"
                    }
                }
            },
            "delete": {
                "summary": "Delete a candidate",
                "description": "Deletes a candidate",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "candidate_id",
                        "in": "path",
                        "description": "ID of candidate to delete",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Candidate deleted"
                    },
                    "404": {
                        "description": "Candidate not found"
                    }
                }
            }
        },
        "/applications": {
            "get": {
                "summary": "List all applications",
                "description": "Returns a list of all applications",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/Application"
                            }
                        }
                    }
                }
            },
            "post": {
                "summary": "Create a new application",
                "description": "Creates a new application",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "description": "Application object",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/Application"
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Application created",
                        "schema": {
                            "$ref": "#/definitions/Application"
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    }
                }
            }
        },
        "/applications/{application_id}": {
            "get": {
                "summary": "Fetch an application given its identifier",
                "description": "Returns a single application",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "application_id",
                        "in": "path",
                        "description": "ID of application to return",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "$ref": "#/definitions/Application"
                        }
                    },
                    "404": {
                        "description": "Application not found"
                    }
                }
            },
            "put": {
                "summary": "Update an application",
                "description": "Updates an application",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "application_id",
                        "in": "path",
                        "description": "ID of application to update",
                        "required": True,
                        "type": "string"
                    },
                    {
                        "in": "body",
                        "name": "body",
                        "description": "Application object",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/Application"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Application updated",
                        "schema": {
                            "$ref": "#/definitions/Application"
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    },
                    "404": {
                        "description": "Application not found"
                    }
                }
            },
            "delete": {
                "summary": "Delete an application",
                "description": "Deletes an application",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "application_id",
                        "in": "path",
                        "description": "ID of application to delete",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Application deleted"
                    },
                    "404": {
                        "description": "Application not found"
                    }
                }
            }
        },
        "/meta/campaigns": {
            "get": {
                "summary": "List all synced Meta Campaigns",
                "description": "Returns a list of all Meta campaigns that have been synced",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/MetaCampaign"
                            }
                        }
                    }
                }
            }
        },
        "/meta/campaigns/{campaign_id}": {
            "get": {
                "summary": "Fetch a single Meta Campaign by ID",
                "description": "Returns a single Meta campaign",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "campaign_id",
                        "in": "path",
                        "description": "ID of Meta campaign to return",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "$ref": "#/definitions/MetaCampaign"
                        }
                    },
                    "404": {
                        "description": "Campaign not found"
                    }
                }
            }
        },
        "/meta/adsets": {
            "get": {
                "summary": "List all synced Meta Ad Sets",
                "description": "Returns a list of all Meta ad sets that have been synced",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/MetaAdSet"
                            }
                        }
                    }
                }
            }
        },
        "/meta/adsets/{ad_set_id}": {
            "get": {
                "summary": "Fetch a single Meta Ad Set by ID",
                "description": "Returns a single Meta ad set",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "ad_set_id",
                        "in": "path",
                        "description": "ID of Meta ad set to return",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "$ref": "#/definitions/MetaAdSet"
                        }
                    },
                    "404": {
                        "description": "Ad set not found"
                    }
                }
            }
        },
        "/meta/ads": {
            "get": {
                "summary": "List all synced Meta Ads",
                "description": "Returns a list of all Meta ads that have been synced",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/MetaAd"
                            }
                        }
                    }
                }
            }
        },
        "/meta/ads/{ad_id}": {
            "get": {
                "summary": "Fetch a single Meta Ad by ID",
                "description": "Returns a single Meta ad",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "ad_id",
                        "in": "path",
                        "description": "ID of Meta ad to return",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "$ref": "#/definitions/MetaAd"
                        }
                    },
                    "404": {
                        "description": "Ad not found"
                    }
                }
            }
        },
        "/meta/insights": {
            "get": {
                "summary": "List synced Meta Insights with filtering",
                "description": "Returns a list of Meta insights with optional filtering",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            }
                        }
                    }
                }
            }
        },
        "/google/campaigns": {
            "get": {
                "summary": "List all synced Google Campaigns",
                "description": "Returns a list of all Google campaigns that have been synced",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            }
                        }
                    }
                }
            }
        },
        "/google/campaigns/{campaign_id}": {
            "get": {
                "summary": "Fetch a single Google Campaign by ID",
                "description": "Returns a single Google campaign",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "campaign_id",
                        "in": "path",
                        "description": "ID of Google campaign to return",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "object"
                        }
                    },
                    "404": {
                        "description": "Campaign not found"
                    }
                }
            }
        },
        "/google/adgroups": {
            "get": {
                "summary": "List all synced Google Ad Groups",
                "description": "Returns a list of all Google ad groups that have been synced",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            }
                        }
                    }
                }
            }
        },
        "/google/adgroups/{ad_group_id}": {
            "get": {
                "summary": "Fetch a single Google Ad Group by ID",
                "description": "Returns a single Google ad group",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "ad_group_id",
                        "in": "path",
                        "description": "ID of Google ad group to return",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "object"
                        }
                    },
                    "404": {
                        "description": "Ad group not found"
                    }
                }
            }
        },
        "/google/ads": {
            "get": {
                "summary": "List all synced Google Ads",
                "description": "Returns a list of all Google ads that have been synced",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            }
                        }
                    }
                }
            }
        },
        "/google/ads/{ad_id}": {
            "get": {
                "summary": "Fetch a single Google Ad by ID",
                "description": "Returns a single Google ad",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "ad_id",
                        "in": "path",
                        "description": "ID of Google ad to return",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "object"
                        }
                    },
                    "404": {
                        "description": "Ad not found"
                    }
                }
            }
        },
        "/google/metrics": {
            "get": {
                "summary": "List Google Ads metrics with filtering",
                "description": "Returns a list of Google Ads metrics with optional filtering",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            }
                        }
                    }
                }
            }
        },
        "/jobs/{job_id}/publish-google-ad": {
            "post": {
                "summary": "Triggers an asynchronous task to create Google campaign structure for a specific job opening",
                "description": "Creates a Google campaign, ad group, and ad for a job opening",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "job_id",
                        "in": "path",
                        "description": "ID of job opening to create Google campaign for",
                        "required": True,
                        "type": "string"
                    },
                    {
                        "in": "body",
                        "name": "body",
                        "description": "Google ad publishing parameters",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/PublishGoogleAdRequest"
                        }
                    }
                ],
                "responses": {
                    "202": {
                        "description": "Task accepted",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "ID of the created task"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "Status of the task"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    },
                    "404": {
                        "description": "Job opening not found"
                    }
                }
            }
        },
        "/jobs/{job_id}/publish-meta-ad": {
            "post": {
                "summary": "Triggers an asynchronous task to create Meta campaign structure for a specific job opening",
                "description": "Creates a Meta campaign, ad set, and ad for a job opening",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "job_id",
                        "in": "path",
                        "description": "ID of job opening to create Meta campaign for",
                        "required": True,
                        "type": "string"
                    },
                    {
                        "in": "body",
                        "name": "body",
                        "description": "Meta ad publishing parameters",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/PublishMetaAdRequest"
                        }
                    }
                ],
                "responses": {
                    "202": {
                        "description": "Task accepted",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "ID of the created task"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "Status of the task"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    },
                    "404": {
                        "description": "Job opening not found"
                    }
                }
            }
        },
        "/tasks/status/{task_id}": {
            "get": {
                "summary": "Check the status of a Celery task",
                "description": "Returns the status and result of a Celery task",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "task_id",
                        "in": "path",
                        "description": "ID of the task to check",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "ID of the task"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "Status of the task"
                                },
                                "result": {
                                    "type": "object",
                                    "description": "Result of the task if completed"
                                },
                                "error": {
                                    "type": "string",
                                    "description": "Error message if task failed"
                                }
                            }
                        }
                    },
                    "404": {
                        "description": "Task not found"
                    }
                }
            }
        },
        "/test": {
            "get": {
                "summary": "Test API endpoint",
                "description": "Returns a test message",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "definitions": {
        "JobOpening": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "Unique identifier for the job"
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
                "company": {
                    "type": "string",
                    "description": "Company name"
                },
                "required_skills": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of required skills"
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
                    "description": "Date the job was posted"
                },
                "status": {
                    "type": "string",
                    "description": "Job status (e.g., open, closed)"
                }
            }
        },
        "PublishMetaAdRequest": {
            "type": "object",
            "properties": {
                "daily_budget": {
                    "type": "integer",
                    "description": "Daily budget in cents (e.g., 500 for $5.00)"
                },
                "target_segments": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "description": "List of segment IDs to target"
                },
                "primary_text": {
                    "type": "string",
                    "description": "Primary text for the ad"
                },
                "headline": {
                    "type": "string",
                    "description": "Headline for the ad"
                },
                "link_description": {
                    "type": "string",
                    "description": "Description for the ad link"
                },
                "image_filename": {
                    "type": "string",
                    "description": "Filename of the image to use for the ad"
                }
            }
        },
        "PublishGoogleAdRequest": {
            "type": "object",
            "properties": {
                "daily_budget": {
                    "type": "integer",
                    "description": "Daily budget in cents (e.g., 500 for $5.00)"
                },
                "target_segments": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "description": "List of segment IDs to target"
                },
                "headline_1": {
                    "type": "string",
                    "description": "First headline for the ad"
                },
                "headline_2": {
                    "type": "string",
                    "description": "Second headline for the ad"
                },
                "headline_3": {
                    "type": "string",
                    "description": "Third headline for the ad"
                },
                "description_1": {
                    "type": "string",
                    "description": "First description line for the ad"
                },
                "description_2": {
                    "type": "string",
                    "description": "Second description line for the ad"
                },
                "image_filename": {
                    "type": "string",
                    "description": "Filename of the image to use for the ad"
                }
            }
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
                "location": {
                    "type": "string",
                    "description": "Candidate location"
                },
                "years_experience": {
                    "type": "integer",
                    "description": "Years of professional experience"
                },
                "education_level": {
                    "type": "string",
                    "description": "Highest education level"
                },
                "skills": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of skills"
                },
                "primary_skill": {
                    "type": "string",
                    "description": "Primary skill or specialization"
                },
                "desired_salary": {
                    "type": "integer",
                    "description": "Desired salary"
                }
            }
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
                    "description": "ID of the job applied for"
                },
                "candidate_id": {
                    "type": "string",
                    "description": "ID of the candidate applying"
                },
                "application_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Date the application was submitted"
                },
                "status": {
                    "type": "string",
                    "description": "Application status (e.g., Submitted, Under Review, Rejected, Hired)"
                }
            }
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
                "daily_budget": {
                    "type": "string",
                    "description": "Daily budget"
                },
                "lifetime_budget": {
                    "type": "string",
                    "description": "Lifetime budget"
                },
                "created_time": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Creation timestamp"
                },
                "start_time": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Start timestamp"
                },
                "stop_time": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Stop timestamp"
                }
            }
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
                "optimization_goal": {
                    "type": "string",
                    "description": "Optimization goal"
                },
                "billing_event": {
                    "type": "string",
                    "description": "Billing event"
                },
                "campaign_id": {
                    "type": "string",
                    "description": "Parent campaign ID"
                }
            }
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
                    "description": "Creation timestamp"
                },
                "creative_id": {
                    "type": "string",
                    "description": "Creative ID"
                },
                "ad_set_id": {
                    "type": "string",
                    "description": "Parent ad set ID"
                }
            }
        },
        "ApiInfo": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "API name"
                },
                "version": {
                    "type": "string",
                    "description": "API version"
                },
                "description": {
                    "type": "string",
                    "description": "API description"
                },
                "documentation": {
                    "type": "string",
                    "description": "API documentation URL"
                }
            }
        },
        "Test": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Test message"
                }
            }
        }
    }
}

# Ruta para servir la especificación JSON de Swagger
@swagger_bp.route('/swagger.json')
def swagger_json():
    """Servir la especificación JSON de Swagger"""
    return jsonify(SWAGGER_SPEC)

# Ruta para servir la UI de Swagger
@swagger_bp.route('/docs')
def swagger_ui():
    """Servir la UI de Swagger"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AdFlux API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css">
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin: 0; background: #fafafa; }
        #debug-panel { padding: 10px; background: #f0f0f0; border-bottom: 1px solid #ddd; }
        #debug-panel button { margin-right: 10px; }
        #json-display { padding: 10px; background: #f8f8f8; border: 1px solid #ddd; display: none; white-space: pre; overflow: auto; max-height: 300px; }
    </style>
</head>
<body>
    <div id="debug-panel">
        <button onclick="showJson()">Show Swagger JSON</button>
        <button onclick="refreshSwagger()">Refresh Swagger UI</button>
    </div>
    <div id="json-display"></div>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js"></script>
    <script>
        function showJson() {
            const jsonDisplay = document.getElementById('json-display');
            if (jsonDisplay.style.display === 'none' || jsonDisplay.style.display === '') {
                fetch('/api/swagger.json')
                    .then(response => response.json())
                    .then(data => {
                        jsonDisplay.textContent = JSON.stringify(data, null, 2);
                        jsonDisplay.style.display = 'block';
                    })
                    .catch(error => {
                        jsonDisplay.textContent = 'Error fetching Swagger JSON: ' + error;
                        jsonDisplay.style.display = 'block';
                    });
            } else {
                jsonDisplay.style.display = 'none';
            }
        }

        function refreshSwagger() {
            location.reload();
        }

        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: "/api/swagger.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                validatorUrl: null
            });
            window.ui = ui;
        };
    </script>
</body>
</html>
    """

# Ruta para redirigir a la UI de Swagger
@swagger_bp.route('/')
def api_root():
    """Redirigir a la UI de Swagger"""
    return {
        "name": "AdFlux API",
        "version": "1.0",
        "description": "API for managing job openings and candidates",
        "documentation": "/api/docs"
    }
