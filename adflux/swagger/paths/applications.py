"""
Rutas de aplicación para Swagger UI.

Este módulo contiene las rutas relacionadas con aplicaciones a ofertas de trabajo para Swagger UI.
"""

# Definir las rutas de aplicación
APPLICATION_PATHS = {
    "/applications": {
        "get": {
            "summary": "Get all applications",
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
            "summary": "Find application by ID",
            "description": "Returns a single application",
            "produces": ["application/json"],
            "parameters": [
                {
                    "name": "application_id",
                    "in": "path",
                    "description": "ID of application to return",
                    "required": True,
                    "type": "integer"
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
            "summary": "Update application",
            "description": "Updates an application",
            "produces": ["application/json"],
            "parameters": [
                {
                    "name": "application_id",
                    "in": "path",
                    "description": "ID of application to update",
                    "required": True,
                    "type": "integer"
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
            "summary": "Delete application",
            "description": "Deletes an application",
            "produces": ["application/json"],
            "parameters": [
                {
                    "name": "application_id",
                    "in": "path",
                    "description": "ID of application to delete",
                    "required": True,
                    "type": "integer"
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
    }
}
