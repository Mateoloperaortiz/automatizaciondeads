"""
Rutas de Meta para Swagger UI.

Este módulo contiene las rutas relacionadas con Meta Ads para Swagger UI.
"""

# Definir las rutas de Meta
META_PATHS = {
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
    "/meta/ad_sets": {
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
    "/meta/ad_sets/{ad_set_id}": {
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
            "summary": "List all synced Meta Insights",
            "description": "Returns a list of all Meta insights that have been synced",
            "produces": ["application/json"],
            "responses": {
                "200": {
                    "description": "Successful operation",
                    "schema": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/MetaInsight"
                        }
                    }
                }
            }
        }
    },
    "/meta/sync": {
        "post": {
            "summary": "Trigger Meta data sync",
            "description": "Triggers a sync of Meta data",
            "produces": ["application/json"],
            "parameters": [
                {
                    "in": "body",
                    "name": "body",
                    "description": "Sync parameters",
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "ad_account_id": {
                                "type": "string",
                                "description": "Meta Ad Account ID"
                            },
                            "date_preset": {
                                "type": "string",
                                "description": "Date preset for insights",
                                "enum": ["today", "yesterday", "this_month", "last_month", "this_quarter", "maximum", "last_3d", "last_7d", "last_14d", "last_28d", "last_30d", "last_90d", "last_week_mon_sun", "last_week_sun_sat", "last_quarter", "last_year", "this_year"]
                            }
                        }
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "Sync triggered",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string"
                            },
                            "task_id": {
                                "type": "string"
                            }
                        }
                    }
                },
                "400": {
                    "description": "Invalid input"
                }
            }
        }
    }
}
