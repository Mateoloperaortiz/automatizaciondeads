"""
Rutas de trabajo para Swagger UI.

Este módulo contiene las rutas relacionadas con ofertas de trabajo para Swagger UI.
"""

# Definir las rutas de trabajo
JOB_PATHS = {
    "/jobs": {
        "get": {
            "summary": "Get all job openings",
            "description": "Returns a list of all job openings",
            "produces": ["application/json"],
            "responses": {
                "200": {
                    "description": "Successful operation",
                    "schema": {"type": "array", "items": {"$ref": "#/definitions/JobOpening"}},
                }
            },
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
                    "schema": {"$ref": "#/definitions/JobOpening"},
                }
            ],
            "responses": {
                "201": {
                    "description": "Job opening created",
                    "schema": {"$ref": "#/definitions/JobOpening"},
                },
                "400": {"description": "Invalid input"},
            },
        },
    },
    "/jobs/{job_id}": {
        "get": {
            "summary": "Find job opening by ID",
            "description": "Returns a single job opening",
            "produces": ["application/json"],
            "parameters": [
                {
                    "name": "job_id",
                    "in": "path",
                    "description": "ID of job opening to return",
                    "required": True,
                    "type": "string",
                }
            ],
            "responses": {
                "200": {
                    "description": "Successful operation",
                    "schema": {"$ref": "#/definitions/JobOpening"},
                },
                "404": {"description": "Job opening not found"},
            },
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
                    "type": "string",
                },
                {
                    "in": "body",
                    "name": "body",
                    "description": "Job opening object",
                    "required": True,
                    "schema": {"$ref": "#/definitions/JobOpening"},
                },
            ],
            "responses": {
                "200": {
                    "description": "Job opening updated",
                    "schema": {"$ref": "#/definitions/JobOpening"},
                },
                "400": {"description": "Invalid input"},
                "404": {"description": "Job opening not found"},
            },
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
                    "type": "string",
                }
            ],
            "responses": {
                "200": {"description": "Job opening deleted"},
                "404": {"description": "Job opening not found"},
            },
        },
    },
}
