"""
Rutas de candidato para Swagger UI.

Este módulo contiene las rutas relacionadas con perfiles de candidatos para Swagger UI.
"""

# Definir las rutas de candidato
CANDIDATE_PATHS = {
    "/candidates": {
        "get": {
            "summary": "Get all candidates",
            "description": "Returns a list of all candidates",
            "produces": ["application/json"],
            "responses": {
                "200": {
                    "description": "Successful operation",
                    "schema": {"type": "array", "items": {"$ref": "#/definitions/Candidate"}},
                }
            },
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
                    "schema": {"$ref": "#/definitions/Candidate"},
                }
            ],
            "responses": {
                "201": {
                    "description": "Candidate created",
                    "schema": {"$ref": "#/definitions/Candidate"},
                },
                "400": {"description": "Invalid input"},
            },
        },
    },
    "/candidates/{candidate_id}": {
        "get": {
            "summary": "Find candidate by ID",
            "description": "Returns a single candidate",
            "produces": ["application/json"],
            "parameters": [
                {
                    "name": "candidate_id",
                    "in": "path",
                    "description": "ID of candidate to return",
                    "required": True,
                    "type": "string",
                }
            ],
            "responses": {
                "200": {
                    "description": "Successful operation",
                    "schema": {"$ref": "#/definitions/Candidate"},
                },
                "404": {"description": "Candidate not found"},
            },
        },
        "put": {
            "summary": "Update candidate",
            "description": "Updates a candidate",
            "produces": ["application/json"],
            "parameters": [
                {
                    "name": "candidate_id",
                    "in": "path",
                    "description": "ID of candidate to update",
                    "required": True,
                    "type": "string",
                },
                {
                    "in": "body",
                    "name": "body",
                    "description": "Candidate object",
                    "required": True,
                    "schema": {"$ref": "#/definitions/Candidate"},
                },
            ],
            "responses": {
                "200": {
                    "description": "Candidate updated",
                    "schema": {"$ref": "#/definitions/Candidate"},
                },
                "400": {"description": "Invalid input"},
                "404": {"description": "Candidate not found"},
            },
        },
        "delete": {
            "summary": "Delete candidate",
            "description": "Deletes a candidate",
            "produces": ["application/json"],
            "parameters": [
                {
                    "name": "candidate_id",
                    "in": "path",
                    "description": "ID of candidate to delete",
                    "required": True,
                    "type": "string",
                }
            ],
            "responses": {
                "200": {"description": "Candidate deleted"},
                "404": {"description": "Candidate not found"},
            },
        },
    },
}
