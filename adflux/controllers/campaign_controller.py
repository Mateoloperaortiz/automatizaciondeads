"""
Controlador para campañas en AdFlux.

Este módulo define el controlador que maneja las solicitudes HTTP
relacionadas con campañas y coordina la interacción entre la capa
de presentación y la capa de lógica de negocio.
"""

from typing import Dict, Any, Tuple, List, Optional
from flask import request, jsonify, current_app, Response

from ..services.interfaces import ICampaignService
from ..dto.campaign_dto import CampaignDTO, CampaignListDTO, CampaignCreateDTO, CampaignUpdateDTO


class CampaignController:
    """
    Controlador para campañas.
    
    Maneja las solicitudes HTTP relacionadas con campañas y coordina
    la interacción entre la capa de presentación y la capa de lógica de negocio.
    """
    
    def __init__(self, campaign_service: ICampaignService):
        """
        Inicializa el controlador con el servicio de campañas.
        
        Args:
            campaign_service: Servicio de campañas
        """
        self.campaign_service = campaign_service
    
    def get_campaigns(self) -> Response:
        """
        Obtiene una lista paginada de campañas.
        
        Returns:
            Respuesta HTTP con la lista de campañas
        """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        query = request.args.get('query', '')
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        platform = request.args.get('platform', None)
        job_id = request.args.get('job_id', None, type=int)
        
        if page < 1:
            return jsonify({'error': 'La página debe ser mayor o igual a 1'}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'El número de elementos por página debe estar entre 1 y 100'}), 400
        
        campaigns, pagination = self.campaign_service.get_campaigns(
            page=page,
            per_page=per_page,
            query=query,
            sort_by=sort_by,
            sort_order=sort_order,
            platform=platform,
            job_id=job_id
        )
        
        campaign_list_dto = CampaignListDTO.from_query_result(
            campaigns=campaigns,
            page=page,
            per_page=per_page,
            total=pagination.total
        )
        
        return jsonify(campaign_list_dto.to_dict())
    
    def get_campaign(self, campaign_id: int) -> Response:
        """
        Obtiene una campaña por su ID.
        
        Args:
            campaign_id: ID de la campaña
            
        Returns:
            Respuesta HTTP con los datos de la campaña
        """
        campaign = self.campaign_service.get_campaign_by_id(campaign_id)
        
        if not campaign:
            return jsonify({'error': f'Campaña con ID {campaign_id} no encontrada'}), 404
        
        campaign_dto = CampaignDTO.from_model(campaign)
        
        return jsonify(campaign_dto.to_dict())
    
    def create_campaign(self) -> Response:
        """
        Crea una nueva campaña.
        
        Returns:
            Respuesta HTTP con el resultado de la operación
        """
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        try:
            campaign_dto = CampaignCreateDTO.from_dict(data)
        except Exception as e:
            return jsonify({'error': f'Datos inválidos: {str(e)}'}), 400
        
        validation_errors = campaign_dto.validate()
        if validation_errors:
            return jsonify({'error': 'Datos inválidos', 'details': validation_errors}), 400
        
        campaign, message, status_code = self.campaign_service.create_campaign(data)
        
        if status_code != 201:
            return jsonify({'error': message}), status_code
        
        response_dto = CampaignDTO.from_model(campaign)
        
        return jsonify(response_dto.to_dict()), 201
    
    def update_campaign(self, campaign_id: int) -> Response:
        """
        Actualiza una campaña existente.
        
        Args:
            campaign_id: ID de la campaña
            
        Returns:
            Respuesta HTTP con el resultado de la operación
        """
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        data['campaign_id'] = campaign_id
        
        try:
            campaign_dto = CampaignUpdateDTO.from_dict(data)
        except Exception as e:
            return jsonify({'error': f'Datos inválidos: {str(e)}'}), 400
        
        validation_errors = campaign_dto.validate()
        if validation_errors:
            return jsonify({'error': 'Datos inválidos', 'details': validation_errors}), 400
        
        campaign, message, status_code = self.campaign_service.update_campaign(campaign_id, data)
        
        if status_code != 200:
            return jsonify({'error': message}), status_code
        
        response_dto = CampaignDTO.from_model(campaign)
        
        return jsonify(response_dto.to_dict())
    
    def delete_campaign(self, campaign_id: int) -> Response:
        """
        Elimina una campaña existente.
        
        Args:
            campaign_id: ID de la campaña
            
        Returns:
            Respuesta HTTP con el resultado de la operación
        """
        result, message, status_code = self.campaign_service.delete_campaign(campaign_id)
        
        if not result:
            return jsonify({'error': message}), status_code
        
        return jsonify({'message': message}), 200
