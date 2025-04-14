"""
Interfaces para los servicios de AdFlux.

Este módulo define interfaces explícitas para los servicios de AdFlux,
facilitando la implementación de patrones como Dependency Injection,
mejorando la testabilidad y permitiendo implementaciones alternativas.
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Protocol, TypeVar, Generic
from datetime import datetime

# Definir tipos genéricos para las entidades
T = TypeVar('T')
JobOpeningType = TypeVar('JobOpeningType')
CandidateType = TypeVar('CandidateType')
CampaignType = TypeVar('CampaignType')
ApplicationType = TypeVar('ApplicationType')


class IBaseService(Protocol, Generic[T]):
    """
    Interfaz base para servicios que proporcionan operaciones CRUD estándar.
    
    Esta interfaz define los métodos comunes que deben implementar todos los servicios
    que realizan operaciones CRUD sobre entidades.
    """
    
    @classmethod
    def get_by_id(cls, entity_id: Any) -> Optional[T]:
        """
        Obtiene una entidad por su ID.
        
        Args:
            entity_id: ID único de la entidad
                
        Returns:
            Objeto de la entidad o None si no se encuentra
        """
        ...
    
    @classmethod
    def get_list(
        cls,
        page: int = 1, 
        per_page: int = 10,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        **filters
    ) -> Tuple[List[T], Any]:
        """
        Obtiene una lista paginada de entidades con opciones de filtrado y ordenación.
        
        Args:
            page: Número de página para paginación
            per_page: Número de elementos por página
            sort_by: Campo por el cual ordenar los resultados
            sort_order: Orden de clasificación ('asc' o 'desc')
            **filters: Filtros adicionales a aplicar
                
        Returns:
            Tupla con la lista de entidades y el objeto de paginación
        """
        ...
    
    @classmethod
    def create(cls, data: Dict[str, Any]) -> Tuple[Union[T, None], str, int]:
        """
        Crea una nueva entidad.
        
        Args:
            data: Diccionario con datos de la entidad
                
        Returns:
            Tupla con (entidad creada, mensaje, código de estado)
        """
        ...
    
    @classmethod
    def update(cls, entity_id: Any, data: Dict[str, Any]) -> Tuple[Union[T, None], str, int]:
        """
        Actualiza una entidad existente.
        
        Args:
            entity_id: ID único de la entidad
            data: Diccionario con datos actualizados
                
        Returns:
            Tupla con (entidad actualizada, mensaje, código de estado)
        """
        ...
    
    @classmethod
    def delete(cls, entity_id: Any) -> Tuple[bool, str, int]:
        """
        Elimina una entidad.
        
        Args:
            entity_id: ID único de la entidad
                
        Returns:
            Tupla con (éxito, mensaje, código de estado)
        """
        ...


class IJobService(IBaseService[JobOpeningType], Protocol):
    """
    Interfaz para el servicio de gestión de trabajos.
    
    Define los métodos específicos para la gestión de ofertas de trabajo,
    además de los métodos CRUD estándar heredados de IBaseService.
    """
    
    @classmethod
    def create_job(cls, job_data: Dict[str, Any]) -> Tuple[Union[JobOpeningType, None], str, int]:
        """
        Crea una nueva oferta de trabajo con un ID único generado.
        
        Args:
            job_data: Diccionario con datos del trabajo
                
        Returns:
            Tupla con (trabajo creado, mensaje, código de estado)
        """
        ...
    
    @classmethod
    def get_active_jobs(cls) -> List[JobOpeningType]:
        """
        Obtiene todas las ofertas de trabajo activas.
        
        Returns:
            Lista de ofertas de trabajo activas
        """
        ...
    
    @classmethod
    def get_jobs_by_status(cls, status: str) -> List[JobOpeningType]:
        """
        Obtiene ofertas de trabajo filtradas por estado.
        
        Args:
            status: Estado de las ofertas a filtrar
                
        Returns:
            Lista de ofertas de trabajo con el estado especificado
        """
        ...


class ICandidateService(Protocol):
    """
    Interfaz para el servicio de gestión de candidatos.
    
    Define los métodos para la gestión de candidatos, incluyendo
    operaciones CRUD y funcionalidades específicas.
    """
    
    @staticmethod
    def get_candidates(
        page: int = 1, 
        per_page: int = 10, 
        query: str = "", 
        sort_by: str = "name",
        sort_order: str = "asc",
        segment_filter: Optional[str] = None
    ) -> Tuple[List[CandidateType], Any]:
        """
        Obtiene una lista paginada de candidatos con opciones de filtrado y ordenación.
        
        Args:
            page: Número de página para paginación
            per_page: Número de elementos por página
            query: Término de búsqueda para filtrar candidatos
            sort_by: Campo por el cual ordenar los resultados
            sort_order: Orden de clasificación ('asc' o 'desc')
            segment_filter: Filtro opcional por ID de segmento
            
        Returns:
            Tupla con la lista de candidatos y el objeto de paginación
        """
        ...
    
    @staticmethod
    def get_candidate_by_id(candidate_id: str) -> Optional[CandidateType]:
        """
        Obtiene un candidato por su ID.
        
        Args:
            candidate_id: ID único del candidato
            
        Returns:
            Objeto Candidate o None si no se encuentra
        """
        ...
    
    @staticmethod
    def create_candidate(candidate_data: Dict[str, Any]) -> Tuple[Union[CandidateType, None], str, int]:
        """
        Crea un nuevo candidato.
        
        Args:
            candidate_data: Diccionario con datos del candidato
            
        Returns:
            Tupla con (candidato creado, mensaje, código de estado)
        """
        ...
    
    @staticmethod
    def update_candidate(candidate_id: str, candidate_data: Dict[str, Any]) -> Tuple[Union[CandidateType, None], str, int]:
        """
        Actualiza un candidato existente.
        
        Args:
            candidate_id: ID único del candidato
            candidate_data: Diccionario con datos actualizados
            
        Returns:
            Tupla con (candidato actualizado, mensaje, código de estado)
        """
        ...
    
    @staticmethod
    def delete_candidate(candidate_id: str) -> Tuple[bool, str, int]:
        """
        Elimina un candidato.
        
        Args:
            candidate_id: ID único del candidato
            
        Returns:
            Tupla con (éxito, mensaje, código de estado)
        """
        ...
    
    @staticmethod
    def get_candidates_by_segment(segment_id: int) -> List[CandidateType]:
        """
        Obtiene candidatos filtrados por segmento.
        
        Args:
            segment_id: ID del segmento
            
        Returns:
            Lista de candidatos en el segmento especificado
        """
        ...


class ICampaignService(Protocol):
    """
    Interfaz para el servicio de gestión de campañas.
    
    Define los métodos para la gestión de campañas publicitarias,
    incluyendo operaciones CRUD y funcionalidades específicas.
    """
    
    def get_campaign_by_id(self, campaign_id: int) -> Optional[CampaignType]:
        """
        Obtiene una campaña por su ID.
        
        Args:
            campaign_id: ID único de la campaña
            
        Returns:
            Objeto Campaign o None si no se encuentra
        """
        ...
    
    def get_campaigns_paginated(
        self, 
        page: int, 
        per_page: int, 
        platform_filter: Optional[str] = None, 
        status_filter: Optional[str] = None, 
        sort_by: str = "created_at", 
        sort_order: str = "desc"
    ):
        """
        Obtiene una lista paginada de campañas con filtros y ordenación.
        
        Args:
            page: Número de página
            per_page: Elementos por página
            platform_filter: Filtro opcional por plataforma
            status_filter: Filtro opcional por estado
            sort_by: Campo para ordenar
            sort_order: Dirección de ordenación
            
        Returns:
            Objeto de paginación con campañas
        """
        ...
    
    def get_campaign_details_data(self, campaign_id: int) -> Tuple[CampaignType, Any]:
        """
        Prepara los datos necesarios para la vista de detalles de campaña.
        
        Args:
            campaign_id: ID único de la campaña
            
        Returns:
            Tupla con la campaña y el trabajo asociado
        """
        ...
    
    def create_campaign(self, form_data: Dict[str, Any], image_file: Any) -> Tuple[Optional[CampaignType], bool, str]:
        """
        Crea una nueva campaña.
        
        Args:
            form_data: Datos del formulario
            image_file: Archivo de imagen para la campaña
            
        Returns:
            Tupla con (campaña creada, éxito, mensaje)
        """
        ...
    
    def update_campaign(self, campaign_id: int, form_data: Dict[str, Any], image_file: Any) -> Tuple[CampaignType, bool, str]:
        """
        Actualiza una campaña existente.
        
        Args:
            campaign_id: ID único de la campaña
            form_data: Datos del formulario
            image_file: Archivo de imagen para la campaña
            
        Returns:
            Tupla con (campaña actualizada, éxito, mensaje)
        """
        ...
    
    def trigger_publish_campaign(self, campaign_id: int, simulate: bool = False) -> Tuple[CampaignType, bool, str]:
        """
        Dispara la tarea asíncrona para publicar una campaña.
        
        Args:
            campaign_id: ID único de la campaña
            simulate: Si es True, simula la publicación sin hacerla efectiva
            
        Returns:
            Tupla con (campaña, éxito, mensaje)
        """
        ...


class IDashboardService(Protocol):
    """
    Interfaz para el servicio del dashboard.
    
    Define los métodos para obtener y procesar datos para el dashboard.
    """
    
    def get_dashboard_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Recopila y procesa todos los datos necesarios para el dashboard.
        
        Args:
            start_date: Fecha de inicio para filtrar datos
            end_date: Fecha de fin para filtrar datos
            
        Returns:
            Diccionario con todos los datos procesados para el dashboard
        """
        ...


class ISegmentationService(Protocol):
    """
    Interfaz para el servicio de segmentación.
    
    Define los métodos para la segmentación de candidatos y análisis relacionados.
    """
    
    def get_segmentation_analysis_data(self) -> Dict[str, Any]:
        """
        Recopila y procesa los datos para la página de análisis de segmentación.
        
        Returns:
            Diccionario con datos de análisis de segmentación
        """
        ...
    
    def trigger_segmentation_task(self) -> Tuple[bool, str]:
        """
        Dispara la tarea Celery para ejecutar la segmentación.
        
        Returns:
            Tupla con (éxito, mensaje)
        """
        ...
    
    def get_segment_by_id(self, segment_id: int) -> Any:
        """
        Obtiene un segmento por su ID.
        
        Args:
            segment_id: ID único del segmento
            
        Returns:
            Objeto Segment
        """
        ...


class IApplicationService(Protocol):
    """
    Interfaz para el servicio de gestión de aplicaciones.
    
    Define los métodos para la gestión de aplicaciones de candidatos a trabajos.
    """
    
    @staticmethod
    def get_applications(
        page: int = 1, 
        per_page: int = 10,
        job_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "application_date",
        sort_order: str = "desc"
    ) -> Tuple[List[ApplicationType], Any]:
        """
        Obtiene una lista paginada de aplicaciones con opciones de filtrado y ordenación.
        
        Args:
            page: Número de página para paginación
            per_page: Número de elementos por página
            job_id: Filtro opcional por ID de trabajo
            candidate_id: Filtro opcional por ID de candidato
            status: Filtro opcional por estado de aplicación
            sort_by: Campo por el cual ordenar los resultados
            sort_order: Orden de clasificación ('asc' o 'desc')
            
        Returns:
            Tupla con la lista de aplicaciones y el objeto de paginación
        """
        ...
    
    @staticmethod
    def get_application_by_id(application_id: int) -> Optional[ApplicationType]:
        """
        Obtiene una aplicación por su ID con carga anticipada de relaciones.
        
        Args:
            application_id: ID único de la aplicación
            
        Returns:
            Objeto Application o None si no se encuentra
        """
        ...
    
    @staticmethod
    def create_application(application_data: Dict[str, Any]) -> Tuple[Union[ApplicationType, None], str, int]:
        """
        Crea una nueva aplicación.
        
        Args:
            application_data: Diccionario con datos de la aplicación
            
        Returns:
            Tupla con (aplicación creada, mensaje, código de estado)
        """
        ...
    
    @staticmethod
    def update_application(application_id: int, application_data: Dict[str, Any]) -> Tuple[Union[ApplicationType, None], str, int]:
        """
        Actualiza una aplicación existente.
        
        Args:
            application_id: ID único de la aplicación
            application_data: Diccionario con datos actualizados
            
        Returns:
            Tupla con (aplicación actualizada, mensaje, código de estado)
        """
        ...
    
    @staticmethod
    def delete_application(application_id: int) -> Tuple[bool, str, int]:
        """
        Elimina una aplicación.
        
        Args:
            application_id: ID único de la aplicación
            
        Returns:
            Tupla con (éxito, mensaje, código de estado)
        """
        ...


class IReportService(Protocol):
    """
    Interfaz para el servicio de informes.
    
    Define los métodos para generar diferentes tipos de informes.
    """
    
    def generate_campaign_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Genera los datos para el informe de campañas.
        
        Args:
            start_date: Fecha de inicio para filtrar datos
            end_date: Fecha de fin para filtrar datos
            
        Returns:
            Diccionario con datos del informe
        """
        ...


class ISettingsService(Protocol):
    """
    Interfaz para el servicio de configuración.
    
    Define los métodos para gestionar la configuración de la aplicación.
    """
    
    def get_api_settings(self) -> Dict[str, Dict[str, str]]:
        """
        Obtiene la configuración actual de las APIs desde las variables de entorno.
        
        Returns:
            Diccionario con configuración de APIs por plataforma
        """
        ...
    
    def save_settings(self, platform: str, settings_data: Dict[str, str]) -> Tuple[bool, str]:
        """
        Guarda la configuración para una plataforma específica.
        
        Args:
            platform: 'meta', 'google', o 'gemini'
            settings_data: Diccionario con las claves y valores a guardar
            
        Returns:
            Tupla con (éxito, mensaje)
        """
        ...
    
    def test_meta_connection(self, settings: Dict[str, str]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Prueba la conexión a la API de Meta con las credenciales proporcionadas.
        
        Args:
            settings: Diccionario con credenciales de Meta
            
        Returns:
            Tupla con (éxito, mensaje, datos adicionales)
        """
        ...
    
    def test_google_connection(self, settings: Dict[str, str]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Prueba la conexión a la API de Google Ads con las credenciales proporcionadas.
        
        Args:
            settings: Diccionario con credenciales de Google Ads
            
        Returns:
            Tupla con (éxito, mensaje, datos adicionales)
        """
        ...
    
    def test_gemini_connection(self, settings: Dict[str, str]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Prueba la conexión a la API de Gemini con la clave proporcionada.
        
        Args:
            settings: Diccionario con clave de API de Gemini
            
        Returns:
            Tupla con (éxito, mensaje, datos adicionales)
        """
        ...
    
    def generate_google_config_file(self, settings: Dict[str, str]) -> Tuple[bool, str]:
        """
        Genera el archivo de configuración para Google Ads.
        
        Args:
            settings: Diccionario con credenciales de Google Ads
            
        Returns:
            Tupla con (éxito, mensaje)
        """
        ...
    
    def get_gemini_models(self, api_key: str) -> Tuple[bool, str, List[str]]:
        """
        Obtiene la lista de modelos disponibles en Gemini.
        
        Args:
            api_key: Clave de API de Gemini
            
        Returns:
            Tupla con (éxito, mensaje, lista de modelos)
        """
        ...
