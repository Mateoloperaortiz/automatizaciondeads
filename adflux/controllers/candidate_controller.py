"""
Controlador para candidatos en AdFlux.

Este módulo define el controlador que maneja las solicitudes HTTP
relacionadas con candidatos y coordina la interacción entre la capa
de presentación y la capa de lógica de negocio.
"""

from typing import Dict, Any, Tuple, List, Optional
from flask import request, jsonify, current_app, Response

from ..services.interfaces import ICandidateService
from ..dto.candidate_dto import CandidateDTO, CandidateListDTO, CandidateCreateDTO, CandidateUpdateDTO


class CandidateController:
    """
    Controlador para candidatos.
    
    Maneja las solicitudes HTTP relacionadas con candidatos y coordina
    la interacción entre la capa de presentación y la capa de lógica de negocio.
    """
    
    def __init__(self, candidate_service: ICandidateService):
        """
        Inicializa el controlador con el servicio de candidatos.
        
        Args:
            candidate_service: Servicio de candidatos
        """
        self.candidate_service = candidate_service
    
    def get_candidates(self) -> Response:
        """
        Obtiene una lista paginada de candidatos.
        
        Returns:
            Respuesta HTTP con la lista de candidatos
        """
        # Obtener parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        query = request.args.get('query', '')
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        segment_filter = request.args.get('segment', None, type=int)
        
        # Validar parámetros
        if page < 1:
            return jsonify({'error': 'La página debe ser mayor o igual a 1'}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'El número de elementos por página debe estar entre 1 y 100'}), 400
        
        # Obtener candidatos del servicio
        candidates, pagination = self.candidate_service.get_candidates(
            page=page,
            per_page=per_page,
            query=query,
            sort_by=sort_by,
            sort_order=sort_order,
            segment_filter=segment_filter
        )
        
        # Crear DTO
        candidate_list_dto = CandidateListDTO.from_query_result(
            candidates=candidates,
            page=page,
            per_page=per_page,
            total=pagination.total
        )
        
        # Devolver respuesta
        return jsonify(candidate_list_dto.to_dict())
    
    def get_candidate(self, candidate_id: int) -> Response:
        """
        Obtiene un candidato por su ID.
        
        Args:
            candidate_id: ID del candidato
            
        Returns:
            Respuesta HTTP con los datos del candidato
        """
        # Obtener candidato del servicio
        candidate = self.candidate_service.get_by_id(candidate_id)
        
        # Verificar si existe
        if not candidate:
            return jsonify({'error': f'Candidato con ID {candidate_id} no encontrado'}), 404
        
        # Crear DTO
        candidate_dto = CandidateDTO.from_model(candidate)
        
        # Devolver respuesta
        return jsonify(candidate_dto.to_dict())
    
    def create_candidate(self) -> Response:
        """
        Crea un nuevo candidato.
        
        Returns:
            Respuesta HTTP con el resultado de la operación
        """
        # Obtener datos de la solicitud
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        # Crear DTO
        try:
            candidate_dto = CandidateCreateDTO.from_dict(data)
        except Exception as e:
            return jsonify({'error': f'Datos inválidos: {str(e)}'}), 400
        
        # Validar DTO
        validation_errors = candidate_dto.validate()
        if validation_errors:
            return jsonify({'error': 'Datos inválidos', 'details': validation_errors}), 400
        
        # Crear candidato
        candidate, message, status_code = self.candidate_service.create_candidate(data)
        
        # Verificar resultado
        if status_code != 201:
            return jsonify({'error': message}), status_code
        
        # Crear DTO de respuesta
        response_dto = CandidateDTO.from_model(candidate)
        
        # Devolver respuesta
        return jsonify(response_dto.to_dict()), 201
    
    def update_candidate(self, candidate_id: int) -> Response:
        """
        Actualiza un candidato existente.
        
        Args:
            candidate_id: ID del candidato
            
        Returns:
            Respuesta HTTP con el resultado de la operación
        """
        # Obtener datos de la solicitud
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        # Añadir ID del candidato a los datos
        data['candidate_id'] = candidate_id
        
        # Crear DTO
        try:
            candidate_dto = CandidateUpdateDTO.from_dict(data)
        except Exception as e:
            return jsonify({'error': f'Datos inválidos: {str(e)}'}), 400
        
        # Validar DTO
        validation_errors = candidate_dto.validate()
        if validation_errors:
            return jsonify({'error': 'Datos inválidos', 'details': validation_errors}), 400
        
        # Actualizar candidato
        candidate, message, status_code = self.candidate_service.update_candidate(candidate_id, data)
        
        # Verificar resultado
        if status_code != 200:
            return jsonify({'error': message}), status_code
        
        # Crear DTO de respuesta
        response_dto = CandidateDTO.from_model(candidate)
        
        # Devolver respuesta
        return jsonify(response_dto.to_dict())
    
    def delete_candidate(self, candidate_id: int) -> Response:
        """
        Elimina un candidato existente.
        
        Args:
            candidate_id: ID del candidato
            
        Returns:
            Respuesta HTTP con el resultado de la operación
        """
        # Eliminar candidato
        result, message, status_code = self.candidate_service.delete_candidate(candidate_id)
        
        # Verificar resultado
        if not result:
            return jsonify({'error': message}), status_code
        
        # Devolver respuesta
        return jsonify({'message': message}), 200
