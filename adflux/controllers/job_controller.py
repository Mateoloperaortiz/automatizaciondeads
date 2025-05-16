"""
Controlador para trabajos en AdFlux.

Este módulo define el controlador que maneja las solicitudes HTTP
relacionadas con trabajos y coordina la interacción entre la capa
de presentación y la capa de lógica de negocio.
"""

from typing import Dict, Any, Tuple, List, Optional
from flask import request, jsonify, current_app, Response

from ..services.interfaces import IJobService
from ..dto.job_dto import JobDTO, JobListDTO, JobCreateDTO, JobUpdateDTO


class JobController:
    """
    Controlador para trabajos.
    
    Maneja las solicitudes HTTP relacionadas con trabajos y coordina
    la interacción entre la capa de presentación y la capa de lógica de negocio.
    """
    
    def __init__(self, job_service: IJobService):
        """
        Inicializa el controlador con el servicio de trabajos.
        
        Args:
            job_service: Servicio de trabajos
        """
        self.job_service = job_service
    
    def get_jobs(self) -> Response:
        """
        Obtiene una lista paginada de trabajos.
        
        Returns:
            Respuesta HTTP con la lista de trabajos
        """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        query = request.args.get('query', '')
        sort_by = request.args.get('sort_by', 'title')
        sort_order = request.args.get('sort_order', 'asc')
        
        if page < 1:
            return jsonify({'error': 'La página debe ser mayor o igual a 1'}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'El número de elementos por página debe estar entre 1 y 100'}), 400
        
        jobs, pagination = self.job_service.get_jobs(
            page=page,
            per_page=per_page,
            query=query,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        job_list_dto = JobListDTO.from_query_result(
            jobs=jobs,
            page=page,
            per_page=per_page,
            total=pagination.total
        )
        
        return jsonify(job_list_dto.to_dict())
    
    def get_job(self, job_id: int) -> Response:
        """
        Obtiene un trabajo por su ID.
        
        Args:
            job_id: ID del trabajo
            
        Returns:
            Respuesta HTTP con los datos del trabajo
        """
        job = self.job_service.get_job_by_id(job_id)
        
        if not job:
            return jsonify({'error': f'Trabajo con ID {job_id} no encontrado'}), 404
        
        job_dto = JobDTO.from_model(job)
        
        return jsonify(job_dto.to_dict())
    
    def create_job(self) -> Response:
        """
        Crea un nuevo trabajo.
        
        Returns:
            Respuesta HTTP con el resultado de la operación
        """
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        try:
            job_dto = JobCreateDTO.from_dict(data)
        except Exception as e:
            return jsonify({'error': f'Datos inválidos: {str(e)}'}), 400
        
        validation_errors = job_dto.validate()
        if validation_errors:
            return jsonify({'error': 'Datos inválidos', 'details': validation_errors}), 400
        
        job, message, status_code = self.job_service.create_job(data)
        
        if status_code != 201:
            return jsonify({'error': message}), status_code
        
        response_dto = JobDTO.from_model(job)
        
        return jsonify(response_dto.to_dict()), 201
    
    def update_job(self, job_id: int) -> Response:
        """
        Actualiza un trabajo existente.
        
        Args:
            job_id: ID del trabajo
            
        Returns:
            Respuesta HTTP con el resultado de la operación
        """
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        data['job_id'] = job_id
        
        try:
            job_dto = JobUpdateDTO.from_dict(data)
        except Exception as e:
            return jsonify({'error': f'Datos inválidos: {str(e)}'}), 400
        
        validation_errors = job_dto.validate()
        if validation_errors:
            return jsonify({'error': 'Datos inválidos', 'details': validation_errors}), 400
        
        job, message, status_code = self.job_service.update_job(job_id, data)
        
        if status_code != 200:
            return jsonify({'error': message}), status_code
        
        response_dto = JobDTO.from_model(job)
        
        return jsonify(response_dto.to_dict())
    
    def delete_job(self, job_id: int) -> Response:
        """
        Elimina un trabajo existente.
        
        Args:
            job_id: ID del trabajo
            
        Returns:
            Respuesta HTTP con el resultado de la operación
        """
        result, message, status_code = self.job_service.delete_job(job_id)
        
        if not result:
            return jsonify({'error': message}), status_code
        
        return jsonify({'message': message}), 200
