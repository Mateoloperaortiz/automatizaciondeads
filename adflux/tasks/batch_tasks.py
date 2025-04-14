"""
Tareas Celery para procesamiento por lotes.

Este módulo define tareas Celery para el procesamiento por lotes de operaciones
que requieren mucho tiempo o recursos.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta

from celery import shared_task, chain, group, chord
from celery.result import AsyncResult
from sqlalchemy import func, text

from ..models import db, Campaign, MetaCampaign, MetaInsight, JobOpening, Candidate, Application
from ..exceptions import DatabaseError


# Configurar logger
logger = logging.getLogger(__name__)


@shared_task(
    name="adflux.tasks.batch_tasks.process_batch",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutos
    soft_time_limit=3600,  # 1 hora
    time_limit=3600 * 2,  # 2 horas
    rate_limit="2/h"
)
def process_batch(
    self,
    batch_id: str,
    task_name: str,
    items: List[Any],
    chunk_size: int = 100,
    **kwargs
) -> Dict[str, Any]:
    """
    Procesa un lote de elementos dividiéndolos en chunks.
    
    Args:
        batch_id: ID único del lote
        task_name: Nombre de la tarea a ejecutar para cada chunk
        items: Lista de elementos a procesar
        chunk_size: Tamaño de cada chunk
        **kwargs: Argumentos adicionales para la tarea
        
    Returns:
        Resultados del procesamiento por lotes
    """
    logger.info(f"Iniciando procesamiento por lotes {batch_id} con {len(items)} elementos")
    
    # Dividir elementos en chunks
    chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    logger.info(f"Dividido en {len(chunks)} chunks de tamaño {chunk_size}")
    
    # Crear tareas para cada chunk
    tasks = []
    for i, chunk in enumerate(chunks):
        task = process_chunk.s(
            batch_id=batch_id,
            chunk_id=i,
            task_name=task_name,
            items=chunk,
            **kwargs
        )
        tasks.append(task)
    
    # Ejecutar tareas en paralelo y recopilar resultados
    callback = collect_batch_results.s(batch_id=batch_id)
    result = chord(tasks)(callback)
    
    return {
        "batch_id": batch_id,
        "task_id": result.id,
        "num_chunks": len(chunks),
        "total_items": len(items),
        "status": "PROCESSING"
    }


@shared_task(
    name="adflux.tasks.batch_tasks.process_chunk",
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minuto
    soft_time_limit=600,  # 10 minutos
    time_limit=1200  # 20 minutos
)
def process_chunk(
    self,
    batch_id: str,
    chunk_id: int,
    task_name: str,
    items: List[Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Procesa un chunk de elementos.
    
    Args:
        batch_id: ID único del lote
        chunk_id: ID del chunk
        task_name: Nombre de la tarea a ejecutar para cada elemento
        items: Lista de elementos a procesar
        **kwargs: Argumentos adicionales para la tarea
        
    Returns:
        Resultados del procesamiento del chunk
    """
    logger.info(f"Procesando chunk {chunk_id} del lote {batch_id} con {len(items)} elementos")
    
    # Obtener tarea
    task = self.app.tasks[task_name]
    
    # Procesar elementos
    results = []
    errors = []
    
    for i, item in enumerate(items):
        try:
            # Ejecutar tarea para el elemento
            result = task.apply(args=[item], kwargs=kwargs)
            
            # Esperar resultado
            item_result = result.get(timeout=300)  # 5 minutos
            
            results.append({
                "item": item,
                "result": item_result,
                "status": "SUCCESS"
            })
            
        except Exception as e:
            logger.error(f"Error al procesar elemento {i} del chunk {chunk_id}: {str(e)}")
            
            errors.append({
                "item": item,
                "error": str(e),
                "status": "ERROR"
            })
    
    return {
        "batch_id": batch_id,
        "chunk_id": chunk_id,
        "total": len(items),
        "success": len(results),
        "errors": len(errors),
        "results": results,
        "error_details": errors
    }


@shared_task(
    name="adflux.tasks.batch_tasks.collect_batch_results",
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minuto
    soft_time_limit=300,  # 5 minutos
    time_limit=600  # 10 minutos
)
def collect_batch_results(self, results: List[Dict[str, Any]], batch_id: str) -> Dict[str, Any]:
    """
    Recopila los resultados de todos los chunks de un lote.
    
    Args:
        results: Lista de resultados de los chunks
        batch_id: ID único del lote
        
    Returns:
        Resultados consolidados del lote
    """
    logger.info(f"Recopilando resultados del lote {batch_id}")
    
    # Consolidar resultados
    total_items = 0
    total_success = 0
    total_errors = 0
    all_results = []
    all_errors = []
    
    for chunk_result in results:
        total_items += chunk_result["total"]
        total_success += chunk_result["success"]
        total_errors += chunk_result["errors"]
        all_results.extend(chunk_result["results"])
        all_errors.extend(chunk_result["error_details"])
    
    # Crear resultado consolidado
    consolidated_result = {
        "batch_id": batch_id,
        "total_items": total_items,
        "total_success": total_success,
        "total_errors": total_errors,
        "success_rate": (total_success / total_items) * 100 if total_items > 0 else 0,
        "status": "COMPLETED",
        "completed_at": datetime.utcnow().isoformat(),
        "results": all_results,
        "errors": all_errors
    }
    
    logger.info(
        f"Lote {batch_id} completado: {total_success}/{total_items} exitosos "
        f"({consolidated_result['success_rate']:.2f}%)"
    )
    
    return consolidated_result


@shared_task(
    name="adflux.tasks.batch_tasks.sync_campaign_insights_batch",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutos
    soft_time_limit=3600,  # 1 hora
    time_limit=3600 * 2  # 2 horas
)
def sync_campaign_insights_batch(
    self,
    start_date: str,
    end_date: str,
    platform: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sincroniza insights de campañas en lotes.
    
    Args:
        start_date: Fecha de inicio (formato ISO)
        end_date: Fecha de fin (formato ISO)
        platform: Plataforma a sincronizar (opcional)
        status: Estado de las campañas a sincronizar (opcional)
        
    Returns:
        Resultado del procesamiento por lotes
    """
    logger.info(f"Iniciando sincronización de insights de campañas en lotes")
    
    try:
        # Convertir fechas
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Construir consulta
        query = db.session.query(MetaCampaign.external_id)
        
        # Aplicar filtros
        if platform or status:
            query = query.join(Campaign, MetaCampaign.campaign_id == Campaign.id)
            
            if platform:
                query = query.filter(Campaign.platform == platform)
            
            if status:
                query = query.filter(Campaign.status == status)
        
        # Obtener IDs de campañas
        campaign_ids = [row[0] for row in query.all()]
        
        if not campaign_ids:
            logger.warning("No se encontraron campañas para sincronizar")
            return {
                "status": "COMPLETED",
                "message": "No se encontraron campañas para sincronizar",
                "total_campaigns": 0
            }
        
        # Crear ID de lote
        batch_id = f"sync_insights_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Iniciar procesamiento por lotes
        return process_batch.delay(
            batch_id=batch_id,
            task_name="adflux.tasks.sync_tasks.sync_campaign_insights",
            items=campaign_ids,
            chunk_size=10,
            start_date=start_date,
            end_date=end_date
        ).get()
    
    except Exception as e:
        logger.error(f"Error al iniciar sincronización de insights en lotes: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    name="adflux.tasks.batch_tasks.process_candidates_batch",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutos
    soft_time_limit=3600,  # 1 hora
    time_limit=3600 * 2  # 2 horas
)
def process_candidates_batch(
    self,
    job_id: int,
    action: str,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Procesa candidatos en lotes.
    
    Args:
        job_id: ID del trabajo
        action: Acción a realizar ('invite', 'reject', 'approve', etc.)
        filters: Filtros para seleccionar candidatos
        
    Returns:
        Resultado del procesamiento por lotes
    """
    logger.info(f"Iniciando procesamiento de candidatos en lotes para trabajo {job_id}")
    
    try:
        # Verificar que el trabajo existe
        job = JobOpening.query.get(job_id)
        if not job:
            raise ValueError(f"Trabajo con ID {job_id} no encontrado")
        
        # Construir consulta
        query = db.session.query(Candidate.id).join(
            Application, Candidate.id == Application.candidate_id
        ).filter(
            Application.job_id == job_id
        )
        
        # Aplicar filtros adicionales
        if filters:
            if 'status' in filters:
                query = query.filter(Application.status == filters['status'])
            
            if 'min_score' in filters:
                query = query.filter(Application.score >= filters['min_score'])
            
            if 'max_score' in filters:
                query = query.filter(Application.score <= filters['max_score'])
            
            if 'applied_after' in filters:
                applied_after = datetime.fromisoformat(filters['applied_after'])
                query = query.filter(Application.created_at >= applied_after)
            
            if 'applied_before' in filters:
                applied_before = datetime.fromisoformat(filters['applied_before'])
                query = query.filter(Application.created_at <= applied_before)
        
        # Obtener IDs de candidatos
        candidate_ids = [row[0] for row in query.all()]
        
        if not candidate_ids:
            logger.warning(f"No se encontraron candidatos para el trabajo {job_id} con los filtros especificados")
            return {
                "status": "COMPLETED",
                "message": "No se encontraron candidatos con los filtros especificados",
                "total_candidates": 0
            }
        
        # Crear ID de lote
        batch_id = f"process_candidates_{job_id}_{action}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Determinar tarea según la acción
        if action == 'invite':
            task_name = "adflux.tasks.candidate_tasks.invite_candidate"
        elif action == 'reject':
            task_name = "adflux.tasks.candidate_tasks.reject_candidate"
        elif action == 'approve':
            task_name = "adflux.tasks.candidate_tasks.approve_candidate"
        else:
            raise ValueError(f"Acción no soportada: {action}")
        
        # Iniciar procesamiento por lotes
        return process_batch.delay(
            batch_id=batch_id,
            task_name=task_name,
            items=candidate_ids,
            chunk_size=50,
            job_id=job_id
        ).get()
    
    except Exception as e:
        logger.error(f"Error al iniciar procesamiento de candidatos en lotes: {str(e)}")
        raise self.retry(exc=e)
