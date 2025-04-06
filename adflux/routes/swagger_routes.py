"""
Rutas para la documentación de Swagger.

Este módulo contiene las rutas para la documentación de Swagger.
"""

from flask import Blueprint, render_template, jsonify

# Definir el blueprint
swagger_bp = Blueprint('swagger', __name__)


@swagger_bp.route('/api/')
def swagger_ui():
    """Renderiza la interfaz de Swagger UI."""
    return render_template('swagger.html')


@swagger_bp.route('/api/swagger.json')
def swagger_json():
    """Devuelve la especificación OpenAPI en formato JSON."""
    swagger_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "AdFlux API",
            "description": "API para gestión de ofertas de empleo y candidatos",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "/api",
                "description": "API Server"
            }
        ],
        "paths": {
            "/jobs": {
                "get": {
                    "summary": "Obtener todas las ofertas de empleo",
                    "responses": {
                        "200": {
                            "description": "Lista de ofertas de empleo",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/Job"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/candidates": {
                "get": {
                    "summary": "Obtener todos los candidatos",
                    "responses": {
                        "200": {
                            "description": "Lista de candidatos",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/Candidate"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/applications": {
                "get": {
                    "summary": "Obtener todas las aplicaciones",
                    "responses": {
                        "200": {
                            "description": "Lista de aplicaciones",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/Application"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Job": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "ID único de la oferta de empleo"
                        },
                        "title": {
                            "type": "string",
                            "description": "Título de la oferta de empleo"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción de la oferta de empleo"
                        },
                        "company": {
                            "type": "string",
                            "description": "Empresa que ofrece el empleo"
                        },
                        "location": {
                            "type": "string",
                            "description": "Ubicación del empleo"
                        },
                        "salary": {
                            "type": "number",
                            "description": "Salario ofrecido"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Fecha de creación de la oferta"
                        }
                    }
                },
                "Candidate": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string",
                            "description": "ID único del candidato"
                        },
                        "name": {
                            "type": "string",
                            "description": "Nombre del candidato"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email del candidato"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Teléfono del candidato"
                        },
                        "resume": {
                            "type": "string",
                            "description": "Resumen del candidato"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Fecha de creación del candidato"
                        }
                    }
                },
                "Application": {
                    "type": "object",
                    "properties": {
                        "application_id": {
                            "type": "integer",
                            "description": "ID único de la aplicación"
                        },
                        "candidate_id": {
                            "type": "string",
                            "description": "ID del candidato"
                        },
                        "job_opening_id": {
                            "type": "string",
                            "description": "ID de la oferta de empleo"
                        },
                        "status": {
                            "type": "string",
                            "description": "Estado de la aplicación"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Fecha de creación de la aplicación"
                        }
                    }
                }
            }
        }
    }
    return jsonify(swagger_spec)
