"""
DTOs para reportes en AdFlux.

Este módulo define los DTOs utilizados para transferir datos
de reportes entre la capa de presentación y la capa de lógica de negocio.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, ClassVar
from datetime import datetime, date

from .base_dto import BaseDTO


@dataclass
class ReportRequestDTO(BaseDTO):
    """DTO para solicitar un reporte."""
    
    report_type: str
    start_date: date
    end_date: date
    platform: Optional[str] = None
    campaign_ids: Optional[List[int]] = None
    job_ids: Optional[List[int]] = None
    segment_ids: Optional[List[int]] = None
    group_by: Optional[str] = None
    format: str = "json"
    
    _validators: ClassVar[Dict[str, Any]] = {
        'report_type': lambda x: None if x in ['performance', 'budget', 'segmentation', 'conversion'] else ValueError('Tipo de reporte no válido'),
        'format': lambda x: None if x in ['json', 'csv', 'pdf', 'excel'] else ValueError('Formato no válido'),
    }
    
    def validate(self) -> List[str]:
        """
        Valida los datos del DTO.
        
        Returns:
            Lista de errores de validación (vacía si no hay errores)
        """
        errors = super().validate()
        
        if self.start_date > self.end_date:
            errors.append("La fecha de inicio debe ser anterior a la fecha de fin")
        
        if self.end_date > date.today():
            errors.append("La fecha de fin no puede ser futura")
        
        return errors


@dataclass
class ReportResponseDTO(BaseDTO):
    """DTO para responder con un reporte."""
    
    report_id: str
    report_type: str
    start_date: date
    end_date: date
    generated_at: datetime
    data: Dict[str, Any]
    format: str
    download_url: Optional[str] = None
    
    @classmethod
    def from_request(cls, request: ReportRequestDTO, report_id: str, data: Dict[str, Any], download_url: Optional[str] = None) -> 'ReportResponseDTO':
        """
        Crea un DTO de respuesta a partir de un DTO de solicitud.
        
        Args:
            request: DTO de solicitud
            report_id: ID del reporte generado
            data: Datos del reporte
            download_url: URL para descargar el reporte
            
        Returns:
            Instancia del DTO de respuesta
        """
        return cls(
            report_id=report_id,
            report_type=request.report_type,
            start_date=request.start_date,
            end_date=request.end_date,
            generated_at=datetime.now(),
            data=data,
            format=request.format,
            download_url=download_url
        )
