"""
Ejemplo de uso de los modelos de validación.

Este módulo muestra cómo utilizar los modelos de validación en AdFlux.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from flask import request, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError

from ..models import db, Campaign
from .campaign import CampaignCreate, CampaignUpdate, CampaignResponse, ValidationError


def create_campaign_example():
    """
    Ejemplo de creación de una campaña con validación.
    
    Returns:
        Respuesta HTTP con la campaña creada o errores de validación
    """
    # Obtener datos de la solicitud
    data = request.get_json()
    
    try:
        # Validar datos con Pydantic
        campaign_data = CampaignCreate.validate_data(data)
        
        # Crear campaña en la base de datos
        campaign = Campaign()
        
        # Copiar datos validados a la campaña
        for field, value in campaign_data.to_dict().items():
            if hasattr(campaign, field):
                setattr(campaign, field, value)
        
        # Guardar campaña en la base de datos
        db.session.add(campaign)
        db.session.commit()
        
        # Crear respuesta
        response = CampaignResponse.from_orm(campaign)
        
        return jsonify(response.to_dict()), 201
    
    except ValidationError as e:
        # Manejar errores de validación
        return jsonify({
            "error": "Datos de campaña inválidos",
            "details": e.get_error_messages()
        }), 400
    
    except SQLAlchemyError as e:
        # Manejar errores de base de datos
        db.session.rollback()
        current_app.logger.error(f"Error al crear campaña: {str(e)}")
        return jsonify({
            "error": "Error al crear campaña",
            "message": "Se produjo un error al guardar la campaña en la base de datos"
        }), 500


def update_campaign_example(campaign_id: int):
    """
    Ejemplo de actualización de una campaña con validación.
    
    Args:
        campaign_id: ID de la campaña a actualizar
        
    Returns:
        Respuesta HTTP con la campaña actualizada o errores de validación
    """
    # Obtener datos de la solicitud
    data = request.get_json()
    
    try:
        # Validar datos con Pydantic
        campaign_data = CampaignUpdate.validate_data(data)
        
        # Obtener campaña de la base de datos
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({
                "error": "Campaña no encontrada",
                "message": f"No se encontró una campaña con ID {campaign_id}"
            }), 404
        
        # Actualizar campaña con datos validados
        for field, value in campaign_data.to_dict().items():
            if hasattr(campaign, field) and value is not None:
                setattr(campaign, field, value)
        
        # Guardar campaña en la base de datos
        db.session.commit()
        
        # Crear respuesta
        response = CampaignResponse.from_orm(campaign)
        
        return jsonify(response.to_dict())
    
    except ValidationError as e:
        # Manejar errores de validación
        return jsonify({
            "error": "Datos de campaña inválidos",
            "details": e.get_error_messages()
        }), 400
    
    except SQLAlchemyError as e:
        # Manejar errores de base de datos
        db.session.rollback()
        current_app.logger.error(f"Error al actualizar campaña: {str(e)}")
        return jsonify({
            "error": "Error al actualizar campaña",
            "message": "Se produjo un error al guardar la campaña en la base de datos"
        }), 500


def get_campaign_example(campaign_id: int):
    """
    Ejemplo de obtención de una campaña con validación.
    
    Args:
        campaign_id: ID de la campaña a obtener
        
    Returns:
        Respuesta HTTP con la campaña o error si no existe
    """
    try:
        # Obtener campaña de la base de datos
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({
                "error": "Campaña no encontrada",
                "message": f"No se encontró una campaña con ID {campaign_id}"
            }), 404
        
        # Crear respuesta
        response = CampaignResponse.from_orm(campaign)
        
        return jsonify(response.to_dict())
    
    except Exception as e:
        # Manejar errores
        current_app.logger.error(f"Error al obtener campaña: {str(e)}")
        return jsonify({
            "error": "Error al obtener campaña",
            "message": "Se produjo un error al obtener la campaña de la base de datos"
        }), 500
