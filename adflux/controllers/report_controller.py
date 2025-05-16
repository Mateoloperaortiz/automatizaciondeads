"""
Controlador para reportes en AdFlux.

Este módulo define el controlador que maneja las solicitudes HTTP
relacionadas con reportes y coordina la interacción entre la capa
de presentación y la capa de lógica de negocio.
"""

from typing import Dict, Any, Tuple, List, Optional
from flask import request, jsonify, current_app, Response

from ..services.interfaces import IReportService
from ..dto.report_dto import ReportRequestDTO, ReportResponseDTO


class ReportController:
    """
    Controlador para reportes.
    
    Maneja las solicitudes HTTP relacionadas con reportes y coordina
    la interacción entre la capa de presentación y la capa de lógica de negocio.
    """
    
    def __init__(self, report_service: IReportService):
        """
        Inicializa el controlador con el servicio de reportes.
        
        Args:
            report_service: Servicio de reportes
        """
        self.report_service = report_service
    
    def generate_report(self) -> Response:
        """
        Genera un reporte según los parámetros proporcionados.
        
        Returns:
            Respuesta HTTP con el reporte generado
        """
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        try:
            report_request_dto = ReportRequestDTO.from_dict(data)
        except Exception as e:
            return jsonify({'error': f'Datos inválidos: {str(e)}'}), 400
        
        validation_errors = report_request_dto.validate()
        if validation_errors:
            return jsonify({'error': 'Datos inválidos', 'details': validation_errors}), 400
        
        report_data, report_id, message, status_code = self.report_service.generate_report(
            report_type=report_request_dto.report_type,
            start_date=report_request_dto.start_date,
            end_date=report_request_dto.end_date,
            platform=report_request_dto.platform,
            campaign_ids=report_request_dto.campaign_ids,
            job_ids=report_request_dto.job_ids,
            segment_ids=report_request_dto.segment_ids,
            group_by=report_request_dto.group_by,
            format=report_request_dto.format
        )
        
        if status_code != 200:
            return jsonify({'error': message}), status_code
        
        download_url = None
        if report_request_dto.format != 'json':
            download_url = f"/api/reports/download/{report_id}"
        
        response_dto = ReportResponseDTO.from_request(
            request=report_request_dto,
            report_id=report_id,
            data=report_data,
            download_url=download_url
        )
        
        return jsonify(response_dto.to_dict())
    
    def download_report(self, report_id: str) -> Response:
        """
        Descarga un reporte generado previamente.
        
        Args:
            report_id: ID del reporte
            
        Returns:
            Respuesta HTTP con el archivo del reporte
        """
        file_path, file_name, mime_type, message, status_code = self.report_service.get_report_file(report_id)
        
        if status_code != 200:
            return jsonify({'error': message}), status_code
        
        return current_app.send_file(
            file_path,
            as_attachment=True,
            download_name=file_name,
            mimetype=mime_type
        )
