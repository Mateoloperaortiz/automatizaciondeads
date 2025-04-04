import time
import traceback
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from typing import Tuple
import os # Añadir importación de os

from .extensions import db, scheduler, celery # Importar instancia de celery
from .models import Candidate, Campaign, JobOpening, Segment
from .ml_model import (
    load_candidate_data, 
    train_segmentation_model, 
    predict_candidate_segments, 
    load_segmentation_model,
    DEFAULT_N_CLUSTERS
)
import logging
import pandas as pd # Necesario para la verificación de DataFrame

from .api_clients import (
    initialize_meta_api, create_meta_campaign, create_meta_ad_set, 
    upload_meta_image, create_meta_ad_creative, create_meta_ad,
    create_meta_custom_audience,
    # Añadir funciones del cliente de Google Ads
    get_google_ads_client, publish_google_campaign_api 
)

# Obtener instancia del logger
log = logging.getLogger(__name__)

# --- Tarea Programada para Segmentación de Candidatos ---

@scheduler.task('cron', id='train_and_predict_segments', hour=2, minute=30) # Ejemplo: Ejecutar diariamente a las 2:30 AM
def scheduled_train_and_predict():
    """
    Tarea programada para reentrenar periódicamente el modelo K-means 
    y actualizar los segmentos de candidatos en la base de datos.
    Se ejecuta dentro del contexto de la aplicación proporcionado por Flask-APScheduler.
    """
    app = current_app._get_current_object() # Obtener la instancia real de la aplicación Flask
    app.logger.info("Iniciando tarea programada de segmentación de candidatos...")
    
    start_time = time.time()
    
    try:
        # 1. Cargar todos los candidatos de la BD
        app.logger.info("Cargando datos de candidatos desde la base de datos...")
        all_candidates = Candidate.query.all()
        if not all_candidates:
            app.logger.info("No se encontraron candidatos en la base de datos. Omitiendo segmentación.")
            return

        candidate_df = load_candidate_data(candidates=all_candidates)
        if candidate_df.empty:
             app.logger.info("El DataFrame de candidatos está vacío después de la carga. Omitiendo segmentación.")
             return
             
        app.logger.info(f"Cargados {len(candidate_df)} candidatos.")

        # 2. Entrenar (o reentrenar) el modelo
        # Usando las rutas predeterminadas definidas en ml_model.py
        app.logger.info("Entrenando/reentrenando modelo de segmentación...")
        model, preprocessor = train_segmentation_model(
            candidate_df, 
            n_clusters=app.config.get('ML_N_CLUSTERS', DEFAULT_N_CLUSTERS) # Permitir sobrescribir mediante configuración
        )
        app.logger.info("Entrenamiento del modelo completo.")

        # 3. Predecir segmentos para los candidatos cargados
        app.logger.info("Prediciendo segmentos para todos los candidatos...")
        # Hacer una copia para evitar modificar el df usado para entrenamiento si se necesita en otro lugar
        predict_df = candidate_df.copy() 
        df_with_segments = predict_candidate_segments(predict_df, model, preprocessor)
        app.logger.info("Predicción de segmentos completa.")

        # 4. Actualizar candidatos en la base de datos
        app.logger.info("Actualizando segmentos de candidatos en la base de datos...")
        update_count = 0
        error_count = 0
        
        # Crear un diccionario para búsqueda rápida: candidate_id -> segment
        segment_map = df_with_segments.set_index(candidate_df.index)['segment'].to_dict()

        # Iterar a través de los objetos Candidate originales
        for candidate in all_candidates:
            try:
                predicted_segment = segment_map.get(candidate.candidate_id)
                # Comprobar si el segmento cambió o era previamente nulo
                if predicted_segment is not None and candidate.segment != int(predicted_segment):
                    candidate.segment = int(predicted_segment)
                    # db.session.add(candidate) # Marcar para actualización (a menudo automático con query)
                    update_count += 1
            except Exception as e:
                app.logger.error(f"Error procesando segmento para el candidato {candidate.candidate_id}: {e}")
                error_count += 1
                # Opcionalmente, hacer rollback de errores individuales si es necesario, pero el commit masivo es más rápido
        
        if update_count > 0:
            try:
                db.session.commit()
                app.logger.info(f"Segmentos actualizados exitosamente para {update_count} candidatos.")
            except SQLAlchemyError as e:
                db.session.rollback()
                app.logger.error(f"Error de base de datos durante la actualización masiva de segmentos: {e}")
                app.logger.error(traceback.format_exc())
                # Levantar o manejar según sea apropiado
        else:
             app.logger.info("No fue necesario actualizar ningún segmento de candidato.")

        if error_count > 0:
            app.logger.warning(f"Se encontraron errores al procesar segmentos para {error_count} candidatos.")

    except Exception as e:
        # Registrar cualquier otro error inesperado durante la tarea
        db.session.rollback() # Revertir cualquier cambio parcial potencial
        app.logger.error(f"Error durante la tarea de segmentación programada: {e}")
        app.logger.error(traceback.format_exc())
        
    finally:
        end_time = time.time()
        app.logger.info(f"Tarea programada de segmentación de candidatos finalizada. Duración: {end_time - start_time:.2f} segundos")

# --- Función de Disparo Manual (Opcional) ---

def trigger_train_and_predict():
    """Disparar manualmente la tarea de segmentación (ej., vía CLI)."""
    # Esto necesita el contexto de la aplicación para ejecutarse
    app = current_app._get_current_object()
    with app.app_context():
        app.logger.info("Disparando manualmente la tarea de segmentación de candidatos...")
        # Nota: La función scheduled_train_and_predict espera ser ejecutada
        # por el scheduler que proporciona el contexto implícitamente.
        # Llamarla directamente requiere el envoltorio de contexto.
        scheduled_train_and_predict() 
        app.logger.info("Disparo manual de la tarea de segmentación finalizado.")
        
        # Devolver estado de éxito y mensaje
        return True, "Tarea de segmentación disparada exitosamente."

# --- Tarea Asíncrona de Publicación de Anuncios (Celery) --- #
@celery.task(bind=True, name='tasks.async_publish_adflux_campaign_to_meta')
def async_publish_adflux_campaign_to_meta(self, campaign_id: int, simulate: bool = False):
    """
    Tarea Celery para publicar asíncronamente una campaña de AdFlux en Meta.
    Maneja el proceso de publicación de una campaña de AdFlux en Meta.
    Obtiene detalles de la campaña, determina parámetros y llama a funciones de la API de Meta.
    Puede ejecutarse en modo de simulación.

    Args:
        campaign_id: El ID del objeto Campaign de AdFlux a publicar.
        simulate: Si es True, registra acciones y genera IDs falsos en lugar de llamar a la API de Meta.

    Returns:
        dict: Resultados que contienen mensaje e IDs (o mensaje de error).
    """
    # Las tareas Celery no tienen automáticamente contexto de aplicación, pero nuestra configuración debería proporcionarlo.
    # Obtener la instancia de la aplicación Flask asociada con la tarea Celery
    app = current_app._get_current_object()
    
    # Usar un logger asociado con la aplicación o Celery
    logger = app.logger or log # Usar logger de la app si está disponible, fallback al logger del módulo
    logger.info(f"[Tarea {self.request.id}] Iniciando proceso de publicación para Campaña AdFlux ID: {campaign_id} (Simular: {simulate})")

    # Inicializar diccionario de resultados
    results = {
        "message": "",
        "success": False,
        "external_campaign_id": None,
        "external_ad_set_id": None,
        "external_ad_id": None,
        "external_audience_id": None
    }

    try:
        # 1. Obtener Campaña AdFlux y Trabajo vinculado
        campaign = Campaign.query.options(db.joinedload(Campaign.job_opening)) \
            .filter_by(id=campaign_id).first()
        if not campaign:
            msg = f"[Tarea {self.request.id}] Campaña AdFlux ID {campaign_id} no encontrada."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results

        job = campaign.job_opening
        if not job:
            msg = f"[Tarea {self.request.id}] Campaña AdFlux ID {campaign_id} no está vinculada a un JobOpening."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results

        logger.info(f"[Tarea {self.request.id}] Encontrada Campaña '{campaign.name}' vinculada a Trabajo '{job.title}' ({job.job_id})")
        # Opcionalmente actualizar estado de campaña a 'publicando'
        campaign.status = 'publishing'
        db.session.add(campaign) # Añadir a la sesión antes de un posible commit
        db.session.commit()

        # 2. Recopilar Parámetros
        ad_account_id = os.environ.get('META_AD_ACCOUNT_ID')
        page_id = os.environ.get('META_PAGE_ID')
        if not ad_account_id or not page_id:
            msg = "META_AD_ACCOUNT_ID y META_PAGE_ID deben estar configurados."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            campaign.status = 'failed' # Actualizar estado
            results["message"] = msg
            db.session.commit()
            return results

        # Detalles de la campaña
        meta_campaign_name = f"{campaign.name} - {job.job_id}" # Ejemplo de nomenclatura
        campaign_objective = 'LINK_CLICKS' # Predeterminado por ahora

        # Detalles del conjunto de anuncios
        ad_set_name = f"{meta_campaign_name} AdSet"
        daily_budget_cents = campaign.daily_budget or 500 # Predeterminado $5.00
        targeting_country = 'CO' # Predeterminado a Colombia

        # Detalles del creativo
        ad_creative_name = f"{meta_campaign_name} Creative"
        ad_message = campaign.primary_text or job.description or "¡Postula a esta emocionante oportunidad!"
        link_title = campaign.headline or job.title
        ad_link_description = campaign.link_description or "Aprende más y postula"
        # URL DE EJEMPLO - NECESITA VERIFICACIÓN
        ad_link_url = f"https://www.magneto365.com/empleos/{job.job_id}" 

        # Manejo de imagen
        image_hash = None
        image_local_path = None
        if campaign.creative_image_filename:
            upload_folder_relative = app.config.get('UPLOAD_FOLDER', 'adflux/static/uploads')
            image_local_path = os.path.join(app.root_path, '..', upload_folder_relative, campaign.creative_image_filename)
            logger.info(f"[Tarea {self.request.id}] Encontrado nombre de archivo de imagen: {campaign.creative_image_filename}. Ruta: {image_local_path}")
            # Comprobar si el archivo existe antes de intentar subirlo
            if not os.path.exists(image_local_path):
                logger.warning(f"[Tarea {self.request.id}] Archivo de imagen no encontrado en la ruta: {image_local_path}. Procediendo sin imagen.")
                image_local_path = None # Restablecer ruta si no se encuentra

        # Detalles del anuncio
        ad_name = f"{meta_campaign_name} Ad"
        initial_status = 'PAUSED' # Siempre publicar pausado primero
        special_ad_categories = ['EMPLOYMENT']

        # 3. Obtener Audiencia Objetivo (IDs de Candidatos)
        target_segment_ids = campaign.target_segment_ids
        candidate_ids = []
        if target_segment_ids:
            try:
                candidate_query = db.session.query(Candidate.candidate_id).filter(
                    Candidate.segment_id.in_(target_segment_ids)
                )
                candidate_results = candidate_query.all()
                candidate_ids = [result[0] for result in candidate_results]
                logger.info(f"[Tarea {self.request.id}] Encontrados {len(candidate_ids)} IDs de candidatos para los segmentos {target_segment_ids}.")
            except Exception as e:
                logger.error(f"[Tarea {self.request.id}] Error consultando IDs de candidatos para los segmentos {target_segment_ids}: {e}")
                candidate_ids = [] # Continuar sin audiencia en caso de error
        else:
            logger.info(f"[Tarea {self.request.id}] No se especificaron segmentos objetivo para esta campaña.")

        # 4. Realizar Acciones de API (Simuladas o Reales)
        # Importar funciones de API dentro de la tarea
        from .api_clients import (
            create_meta_campaign, create_meta_ad_set,
            create_meta_ad_creative, create_meta_ad,
            create_meta_custom_audience, upload_meta_image
        )
        
        ext_campaign_id = None
        ext_ad_set_id = None
        ext_ad_id = None
        ext_audience_id = None

        # --- Audiencia Personalizada --- #
        if candidate_ids:
            audience_name = f"Job {job.job_id} Segmentos {target_segment_ids} ({len(candidate_ids)})"
            if simulate:
                ext_audience_id = f"FAKE-AUD-{campaign.id}-{int(time.time())}"
                logger.info(f"[SIMULAR] [Tarea {self.request.id}] Se crearía audiencia personalizada '{audience_name}' ID: {ext_audience_id}")
            else:
                ext_audience_id = create_meta_custom_audience(
                    ad_account_id=ad_account_id, name=audience_name,
                    description=f"Segmentos de candidatos {target_segment_ids} para trabajo {job.job_id}",
                    customer_file_source="USER_PROVIDED_ONLY", subtype="CUSTOM",
                    user_identifiers=candidate_ids, identifier_type="EXTERN_ID"
                )
                if ext_audience_id:
                    logger.info(f"[Tarea {self.request.id}] Creada audiencia personalizada real ID: {ext_audience_id}")
                else:
                    logger.warning(f"[Tarea {self.request.id}] Fallo al crear Audiencia Personalizada de Meta, procediendo sin ella.")
            results["external_audience_id"] = ext_audience_id

        # --- Subir Imagen --- #
        if image_local_path:
            if simulate:
                image_hash = f"FAKE-HASH-{campaign.id}-{int(time.time())}"
                logger.info(f"[SIMULAR] [Tarea {self.request.id}] Se subiría imagen {image_local_path}. Hash: {image_hash}")
            else:
                image_hash = upload_meta_image(ad_account_id, image_local_path)
                if image_hash:
                    logger.info(f"[Tarea {self.request.id}] Imagen subida, hash: {image_hash}")
                else:
                    logger.warning(f"[Tarea {self.request.id}] Fallo al subir imagen, procediendo sin ella.")

        # --- Crear Campaña --- #
        if simulate:
            ext_campaign_id = f"FAKE-CAMP-{campaign.id}-{int(time.time())}"
            logger.info(f"[SIMULAR] [Tarea {self.request.id}] Se crearía campaña '{meta_campaign_name}' ID: {ext_campaign_id}")
        else:
            ext_campaign_id = create_meta_campaign(
                ad_account_id=ad_account_id, name=meta_campaign_name,
                objective=campaign_objective, status=initial_status,
                special_ad_categories=special_ad_categories
            )
            if ext_campaign_id:
                logger.info(f"[Tarea {self.request.id}] Creada campaña real ID: {ext_campaign_id}")
            else:
                msg = f"Fallo al crear Campaña de Meta."
                logger.error(f"[Tarea {self.request.id}] {msg}")
                campaign.status = 'failed'
                results["message"] = msg
                db.session.commit()
                return results # Detener procesamiento si falla la campaña
        results["external_campaign_id"] = ext_campaign_id

        # --- Crear Conjunto de Anuncios --- #
        targeting_spec = {'geo_locations': {'countries': [targeting_country]}}
        if ext_audience_id:
            targeting_spec['custom_audiences'] = [{'id': ext_audience_id}]
        
        if simulate:
            ext_ad_set_id = f"FAKE-ADSET-{campaign.id}-{int(time.time())}"
            logger.info(f"[SIMULAR] [Tarea {self.request.id}] Se crearía conjunto de anuncios '{ad_set_name}' ID: {ext_ad_set_id}")
        else:
            ext_ad_set_id = create_meta_ad_set(
                ad_account_id=ad_account_id, name=ad_set_name,
                campaign_id=ext_campaign_id, status=initial_status,
                daily_budget_cents=daily_budget_cents, optimization_goal='LINK_CLICKS',
                billing_event='IMPRESSIONS', targeting=targeting_spec # Pasar especificación de segmentación aquí
            )
            if ext_ad_set_id:
                logger.info(f"[Tarea {self.request.id}] Creado conjunto de anuncios real ID: {ext_ad_set_id}")
            else:
                msg = f"Fallo al crear Conjunto de Anuncios de Meta."
                logger.error(f"[Tarea {self.request.id}] {msg}")
                campaign.status = 'failed'
                results["message"] = msg
                db.session.commit()
                # TODO: ¿Quizás eliminar la campaña creada anteriormente?
                return results # Detener procesamiento
        results["external_ad_set_id"] = ext_ad_set_id

        # --- Crear Creativo de Anuncio --- #
        creative_id = None
        if simulate:
            creative_id = f"FAKE-CREATIVE-{campaign.id}-{int(time.time())}"
            logger.info(f"[SIMULAR] [Tarea {self.request.id}] Se crearía creativo de anuncio '{ad_creative_name}' ID: {creative_id}")
        else:
            creative_id = create_meta_ad_creative(
                ad_account_id=ad_account_id, name=ad_creative_name,
                page_id=page_id, message=ad_message, link=ad_link_url,
                link_title=link_title, link_description=ad_link_description,
                image_hash=image_hash # Pasar hash de imagen si está disponible
            )
            if creative_id:
                logger.info(f"[Tarea {self.request.id}] Creado creativo de anuncio real ID: {creative_id}")
            else:
                msg = f"Fallo al crear Creativo de Anuncio de Meta."
                logger.error(f"[Tarea {self.request.id}] {msg}")
                campaign.status = 'failed'
                results["message"] = msg
                db.session.commit()
                # TODO: ¿Quizás eliminar campaña/conjunto de anuncios?
                return results # Detener procesamiento

        # --- Crear Anuncio --- #
        if simulate:
            ext_ad_id = f"FAKE-AD-{campaign.id}-{int(time.time())}"
            logger.info(f"[SIMULAR] [Tarea {self.request.id}] Se crearía anuncio '{ad_name}' ID: {ext_ad_id}")
        else:
            ext_ad_id = create_meta_ad(
                ad_account_id=ad_account_id, name=ad_name,
                ad_set_id=ext_ad_set_id, creative_id=creative_id,
                status=initial_status
            )
            if ext_ad_id:
                logger.info(f"[Tarea {self.request.id}] Creado anuncio real ID: {ext_ad_id}")
            else:
                msg = f"Fallo al crear Anuncio de Meta."
                logger.error(f"[Tarea {self.request.id}] {msg}")
                campaign.status = 'failed'
                results["message"] = msg
                db.session.commit()
                # TODO: ¿Quizás eliminar campaña/conjunto de anuncios/creativo?
                return results # Detener procesamiento
        results["external_ad_id"] = ext_ad_id

        # 5. Actualizar Campaña AdFlux con IDs externos y establecer estado a 'active' (o quizás 'paused')
        campaign.external_campaign_id = ext_campaign_id
        campaign.external_ad_set_id = ext_ad_set_id
        campaign.external_ad_id = ext_ad_id
        campaign.external_audience_id = ext_audience_id
        campaign.status = 'active' # O 'paused' ya que los creamos pausados?
        db.session.commit()

        logger.info(f"[Tarea {self.request.id}] Publicada exitosamente Campaña AdFlux {campaign_id} en Meta. IDs Externos: {results}")
        results["success"] = True
        results["message"] = f"Campaña '{campaign.name}' publicada exitosamente ({'simulada' if simulate else 'real'})."
        return results

    except Exception as e:
        db.session.rollback() # Revertir cualquier cambio parcial en BD
        # Actualizar estado de campaña a failed
        try:
            # Obtener campaña de nuevo en caso de que la sesión haya sido revertida
            campaign_to_fail = Campaign.query.get(campaign_id)
            if campaign_to_fail:
                campaign_to_fail.status = 'failed'
                db.session.commit()
        except Exception as db_err:
             logger.error(f"[Tarea {self.request.id}] Fallo al actualizar estado de campaña a 'failed' después de error: {db_err}")
             
        msg = f"Error durante tarea de publicación asíncrona para campaña {campaign_id}: {e}"
        logger.error(f"[Tarea {self.request.id}] {msg}", exc_info=True)
        results["message"] = msg
        results["success"] = False
        return results # Devolver detalles del error

# --- Tarea Manual de Segmentación ML (Celery) --- #
@celery.task(bind=True, name='tasks.run_candidate_segmentation_task')
def run_candidate_segmentation_task(self):
    """
    Tarea Celery para disparar manualmente el proceso de segmentación de candidatos.
    Replica la lógica de la tarea programada pero se ejecuta bajo demanda.
    """
    # Usar contexto de aplicación proporcionado por la configuración de Celery
    app = current_app._get_current_object()
    logger = app.logger or log
    logger.info(f"[Tarea {self.request.id}] Iniciando tarea de segmentación de candidatos disparada manualmente...")

    start_time = time.time()
    
    try:
        # 1. Cargar todos los candidatos de la BD
        logger.info(f"[Tarea {self.request.id}] Cargando datos de candidatos desde la base de datos...")
        all_candidates = Candidate.query.all()
        if not all_candidates:
            logger.info(f"[Tarea {self.request.id}] No se encontraron candidatos en la base de datos. Omitiendo segmentación.")
            return {"status": "skipped", "message": "No se encontraron candidatos"}

        candidate_df = load_candidate_data(candidates=all_candidates)
        if candidate_df.empty:
            logger.info(f"[Tarea {self.request.id}] El DataFrame de candidatos está vacío después de la carga. Omitiendo segmentación.")
            return {"status": "skipped", "message": "El procesamiento de datos de candidatos resultó en un DataFrame vacío"}

        logger.info(f"[Tarea {self.request.id}] Cargados {len(candidate_df)} candidatos.")

        # 2. Entrenar el modelo
        logger.info(f"[Tarea {self.request.id}] Entrenando modelo de segmentación...")
        model, preprocessor = train_segmentation_model(
            candidate_df,
            n_clusters=app.config.get('ML_N_CLUSTERS', DEFAULT_N_CLUSTERS)
        )
        logger.info(f"[Tarea {self.request.id}] Entrenamiento del modelo completo.")

        # 3. Predecir segmentos
        logger.info(f"[Tarea {self.request.id}] Prediciendo segmentos para todos los candidatos...")
        predict_df = candidate_df.copy()
        df_with_segments = predict_candidate_segments(predict_df, model, preprocessor)
        logger.info(f"[Tarea {self.request.id}] Predicción de segmentos completa.")

        # 4. Actualizar candidatos en la base de datos
        logger.info(f"[Tarea {self.request.id}] Actualizando segmentos de candidatos en la base de datos...")
        update_count = 0
        error_count = 0
        segment_map = df_with_segments.set_index(candidate_df.index)['segment'].to_dict()

        for candidate in all_candidates:
            try:
                predicted_segment = segment_map.get(candidate.candidate_id)
                if predicted_segment is not None and candidate.segment_id != int(predicted_segment):
                    candidate.segment_id = int(predicted_segment)
                    update_count += 1
            except Exception as e:
                logger.error(f"[Tarea {self.request.id}] Error procesando segmento para el candidato {candidate.candidate_id}: {e}")
                error_count += 1

        if update_count > 0:
            try:
                db.session.commit()
                logger.info(f"[Tarea {self.request.id}] Segmentos actualizados exitosamente para {update_count} candidatos.")
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"[Tarea {self.request.id}] Error de base de datos durante la actualización masiva de segmentos: {e}", exc_info=True)
                raise # Volver a lanzar error de BD para marcar la tarea como fallida
        else:
            logger.info(f"[Tarea {self.request.id}] No fue necesario actualizar ningún segmento de candidato.")

        if error_count > 0:
             logger.warning(f"[Tarea {self.request.id}] Se encontraron errores al procesar segmentos para {error_count} candidatos.")
             # Decidir si esto constituye un fallo de la tarea. Por ahora, permitir que tenga éxito.

        status_message = f"Segmentación completa. Actualizados {update_count} candidatos. Encontrados {error_count} errores."
        return {"status": "success", "message": status_message, "updated_count": update_count, "error_count": error_count}

    except Exception as e:
        db.session.rollback()
        logger.error(f"[Tarea {self.request.id}] Error durante tarea de segmentación manual: {e}", exc_info=True)
        # Volver a lanzar la excepción para marcar la tarea Celery como fallida
        raise

    finally:
        end_time = time.time()
        logger.info(f"[Tarea {self.request.id}] Tarea manual de segmentación de candidatos finalizada. Duración: {end_time - start_time:.2f} segundos")
        

# --- ELIMINAR FUNCIÓN DE SINCRONIZACIÓN ANTIGUA --- #
# def publish_adflux_campaign_to_meta(campaign_id: int, simulate: bool = False) -> Tuple[bool, dict]:
#    ... (Lógica síncrona antigua eliminada) ...

# --- Tarea Asíncrona para Publicación de Trabajo API --- #
@celery.task(bind=True, name='tasks.async_create_meta_structure_for_job')
def async_create_meta_structure_for_job(self, job_id: str, params: dict):
    """
    Tarea Celery para crear asíncronamente la estructura de campaña de Meta directamente para un Job ID.
    Disparado por el endpoint API /api/v1/jobs/<job_id>/publish-meta-ad.

    Args:
        job_id (str): El ID del JobOpening de AdFlux.
        params (dict): Diccionario que contiene parámetros del payload de la API, ej.,
                       ad_account_id, page_id, campaign_name, daily_budget_cents, 
                       targeting_country_code, ad_message, ad_link_url, etc.
                       Incluye 'image_hash' o 'image_local_path' opcionales.

    Returns:
        dict: Resultados que contienen estado de éxito, mensaje e IDs externos creados.
    """
    app = current_app._get_current_object()
    logger = app.logger or log
    logger.info(f"[Tarea {self.request.id}] Iniciando creación de estructura Meta para Job ID: {job_id}")

    results = {
        "message": "", "success": False, "external_campaign_id": None,
        "external_ad_set_id": None, "external_ad_id": None, "external_audience_id": None
    }

    try:
        # 1. Obtener Trabajo y Extraer Segmentos Objetivo
        job = JobOpening.query.filter_by(job_id=job_id).first()
        if not job:
            msg = f"Trabajo con ID {job_id} no encontrado."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results
            
        # Asegurar que target_segments sea una lista (manejar None u otros tipos)
        target_segments = job.target_segments if isinstance(job.target_segments, list) else []
        logger.info(f"[Tarea {self.request.id}] Trabajo {job_id} encontrado. Segmentos objetivo: {target_segments}")

        # 2. Extraer Parámetros del dict
        ad_account_id = params.get('ad_account_id')
        page_id = params.get('page_id')
        campaign_name = params.get('campaign_name')
        campaign_objective = params.get('campaign_objective', 'LINK_CLICKS')
        ad_set_name = params.get('ad_set_name')
        daily_budget_cents = params.get('daily_budget_cents')
        targeting_country = params.get('targeting_country_code', 'CO')
        ad_creative_name = params.get('ad_creative_name')
        ad_message = params.get('ad_message')
        ad_link_url = params.get('ad_link_url')
        link_title = params.get('link_title', job.title) # Predeterminado desde el trabajo
        ad_link_description = params.get('link_description', 'Aprende más') # Predeterminado
        ad_name = params.get('ad_name')
        image_hash = params.get('image_hash')
        image_local_path = params.get('image_local_path')
        
        # Validar parámetros requeridos
        required_params = [
            'ad_account_id', 'page_id', 'campaign_name', 'ad_set_name', 
            'daily_budget_cents', 'ad_creative_name', 'ad_message', 
            'ad_link_url', 'ad_name'
        ]
        missing_params = [p for p in required_params if not params.get(p)]
        if missing_params:
             msg = f"Faltan parámetros requeridos en la llamada API: {', '.join(missing_params)}"
             logger.error(f"[Tarea {self.request.id}] {msg}")
             results["message"] = msg
             return results

        initial_status = 'PAUSED'
        special_ad_categories = ['EMPLOYMENT']

        # 3. Obtener IDs de Candidatos para Segmentos Objetivo
        candidate_ids = []
        if target_segments:
            try:
                candidate_query = db.session.query(Candidate.candidate_id).filter(
                    Candidate.segment_id.in_(target_segments)
                )
                candidate_results = candidate_query.all()
                candidate_ids = [result[0] for result in candidate_results]
                logger.info(f"[Tarea {self.request.id}] Encontrados {len(candidate_ids)} IDs de candidatos para los segmentos {target_segments}.")
            except Exception as e:
                logger.error(f"[Tarea {self.request.id}] Error consultando IDs de candidatos para los segmentos {target_segments}: {e}")
                # Continuar sin audiencia personalizada si la consulta falla
                candidate_ids = []
        else:
             logger.info(f"[Tarea {self.request.id}] No se especificaron segmentos objetivo para este trabajo.")

        # 4. Realizar Acciones de API (Real - no se necesita bandera de simulación aquí)
        # Importar funciones de API dentro de la tarea
        from .api_clients import (
            create_meta_campaign, create_meta_ad_set,
            create_meta_ad_creative, create_meta_ad,
            create_meta_custom_audience, upload_meta_image
        )

        ext_campaign_id = None
        ext_ad_set_id = None
        ext_ad_id = None
        ext_audience_id = None

        # --- Audiencia Personalizada --- #
        if candidate_ids:
            audience_name = f"API Job {job_id} Segmentos {target_segments} ({len(candidate_ids)})"
            ext_audience_id = create_meta_custom_audience(
                ad_account_id=ad_account_id, name=audience_name,
                description=f"Segmentos de candidatos {target_segments} para trabajo {job_id} (Disparado por API)",
                customer_file_source="USER_PROVIDED_ONLY", subtype="CUSTOM",
                user_identifiers=candidate_ids, identifier_type="EXTERN_ID"
            )
            if ext_audience_id:
                logger.info(f"[Tarea {self.request.id}] Creada audiencia personalizada ID: {ext_audience_id}")
            else:
                logger.warning(f"[Tarea {self.request.id}] Fallo al crear Audiencia Personalizada de Meta, procediendo sin ella.")
        results["external_audience_id"] = ext_audience_id

        # --- Subir Imagen (si se proporciona ruta local) --- #
        # El hash de imagen del payload tiene prioridad
        final_image_hash = image_hash 
        if not final_image_hash and image_local_path:
            # Construir ruta completa relativa a la raíz del proyecto
            # Asume que image_local_path es relativo a la raíz del proyecto, ej. 'static/uploads/image.png'
            img_full_path = os.path.join(app.root_path, '..', image_local_path)
            logger.info(f"[Tarea {self.request.id}] Intentando subir imagen desde la ruta: {img_full_path}")
            if os.path.exists(img_full_path):
                final_image_hash = upload_meta_image(ad_account_id, img_full_path)
                if final_image_hash:
                    logger.info(f"[Tarea {self.request.id}] Imagen subida, hash: {final_image_hash}")
                else:
                    logger.warning(f"[Tarea {self.request.id}] Fallo al subir imagen desde {img_full_path}, procediendo sin ella.")
            else:
                logger.warning(f"[Tarea {self.request.id}] Archivo de imagen local no encontrado en {img_full_path}. Procediendo sin imagen.")

        # --- Crear Campaña --- #
        ext_campaign_id = create_meta_campaign(
            ad_account_id=ad_account_id, name=campaign_name,
            objective=campaign_objective, status=initial_status,
            special_ad_categories=special_ad_categories
        )
        if not ext_campaign_id:
            msg = f"Fallo al crear Campaña de Meta vía tarea API."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            # No hay cambios en BD para revertir aquí todavía
            return results
        logger.info(f"[Tarea {self.request.id}] Creado ID de campaña: {ext_campaign_id}")
        results["external_campaign_id"] = ext_campaign_id

        # --- Crear Conjunto de Anuncios --- #
        targeting_spec = {'geo_locations': {'countries': [targeting_country]}}
        if ext_audience_id:
            targeting_spec['custom_audiences'] = [{'id': ext_audience_id}]
        
        ext_ad_set_id = create_meta_ad_set(
            ad_account_id=ad_account_id, name=ad_set_name,
            campaign_id=ext_campaign_id, status=initial_status,
            daily_budget_cents=daily_budget_cents, optimization_goal=campaign_objective,
            billing_event='IMPRESSIONS', targeting=targeting_spec
        )
        if not ext_ad_set_id:
            msg = f"Fallo al crear Conjunto de Anuncios de Meta vía tarea API."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            # TODO: Limpieza - ¿Eliminar campaña creada?
            return results
        logger.info(f"[Tarea {self.request.id}] Creado ID de conjunto de anuncios: {ext_ad_set_id}")
        results["external_ad_set_id"] = ext_ad_set_id

        # --- Crear Creativo de Anuncio --- #
        creative_id = create_meta_ad_creative(
            ad_account_id=ad_account_id, name=ad_creative_name,
            page_id=page_id, message=ad_message, link=ad_link_url,
            link_title=link_title, link_description=ad_link_description,
            image_hash=final_image_hash # Usar el hash que obtuvimos (si lo hay)
        )
        if not creative_id:
            msg = f"Fallo al crear Creativo de Anuncio de Meta vía tarea API."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            # TODO: Limpieza - ¿Eliminar campaña/conjunto de anuncios creado?
            return results
        logger.info(f"[Tarea {self.request.id}] Creado ID de creativo de anuncio: {creative_id}")

        # --- Crear Anuncio --- #
        ext_ad_id = create_meta_ad(
            ad_account_id=ad_account_id, name=ad_name,
            ad_set_id=ext_ad_set_id, creative_id=creative_id,
            status=initial_status
        )
        if not ext_ad_id:
            msg = f"Fallo al crear Anuncio de Meta vía tarea API."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            # TODO: Limpieza - ¿Eliminar campaña/conjunto de anuncios/creativo?
            return results
        logger.info(f"[Tarea {self.request.id}] Creado ID de anuncio: {ext_ad_id}")
        results["external_ad_id"] = ext_ad_id

        # 5. Éxito
        results["success"] = True
        results["message"] = f"Creada exitosamente estructura Meta para trabajo {job_id} (pausada)."
        logger.info(f"[Tarea {self.request.id}] {results['message']} IDs Externos: {results}")
        return results

    except Exception as e:
        db.session.rollback() # Revertir por si acaso (aunque menos probable aquí)
        msg = f"Error inesperado durante tarea de creación de estructura Meta para trabajo {job_id}: {e}"
        logger.error(f"[Tarea {self.request.id}] {msg}", exc_info=True)
        results["message"] = msg
        results["success"] = False
        return results # Devolver detalles del error

@celery.task(bind=True, name='tasks.async_publish_adflux_campaign_to_google')
def async_publish_adflux_campaign_to_google(self, campaign_id: int, simulate: bool = True):
    """
    Tarea Celery para publicar asíncronamente una campaña de AdFlux en Google Ads.
    Obtiene detalles de la campaña, determina parámetros y llama a funciones de la API de Google Ads.
    Actualmente se ejecuta en modo de simulación por defecto.

    Args:
        campaign_id: El ID del objeto Campaign de AdFlux a publicar.
        simulate: Si es True (predeterminado), usa la llamada API simulada. Si es False, intentaría una llamada API real (aún no implementado).

    Returns:
        dict: Resultados que contienen mensaje e IDs externos (o mensaje de error).
    """
    app = current_app._get_current_object()
    logger = app.logger or log
    logger.info(f"[Tarea {self.request.id}] Iniciando proceso de publicación en Google Ads para Campaña AdFlux ID: {campaign_id} (Simular: {simulate})")

    results = {
        "message": "",
        "success": False,
        "external_campaign_id": None,
        "external_ids": None # Diccionario para IDs de Google
    }

    try:
        # 1. Obtener Campaña AdFlux y Trabajo vinculado
        campaign = Campaign.query.options(db.joinedload(Campaign.job_opening)) \
            .filter_by(id=campaign_id).first()
            
        if not campaign:
            msg = f"[Tarea {self.request.id}] Campaña AdFlux ID {campaign_id} no encontrada."
            logger.error(msg)
            results["message"] = msg
            return results
            
        if campaign.platform.lower() != 'google':
             msg = f"[Tarea {self.request.id}] Campaña {campaign_id} no es una campaña de Google Ads (plataforma: {campaign.platform}). Abortando."
             logger.error(msg)
             results["message"] = msg
             return results

        logger.info(f"[Tarea {self.request.id}] Encontrada Campaña Google '{campaign.name}'")

        # Actualizar estado a 'publicando'
        campaign.status = 'publishing'
        db.session.commit()

        # 2. Preparar datos para la llamada API
        # Extraer campos relevantes del modelo de campaña AdFlux
        campaign_data_for_api = {
            "name": campaign.name,
            "daily_budget": campaign.daily_budget, # Asumiendo que el presupuesto está en centavos o la unidad monetaria más pequeña
            "headline": campaign.headline,
            "primary_text": campaign.primary_text, # A menudo llamado 'description' en Google Ads
            "job_id": campaign.job_opening_id,
            # Añadir cualquier otro campo relevante necesario para la creación de la campaña de Google Ads
            # ej., URL de landing page, palabras clave (¿podría necesitar otro campo de modelo?)
        }
        
        # 3. Llamar a la función cliente de API (simulada por ahora)
        if simulate:
            logger.info(f"[Tarea {self.request.id}] Llamando a función SIMULADA de publicación de Google Ads.")
            api_result = publish_google_campaign_api(campaign.id, campaign_data_for_api)
        else:
            # Placeholder para llamada API real
            logger.warning(f"[Tarea {self.request.id}] Publicación real en Google Ads aún no implementada. Ejecutando simulación en su lugar.")
            api_result = publish_google_campaign_api(campaign.id, campaign_data_for_api)
            # En el futuro:
            # api_result = real_publish_google_campaign_api(campaign.id, campaign_data_for_api)
            
        logger.info(f"[Tarea {self.request.id}] Resultado de llamada API: {api_result}")

        # 4. Procesar resultados y actualizar Campaña AdFlux
        if api_result and api_result.get('success'):
            external_ids_dict = api_result.get('external_ids')
            if external_ids_dict:
                campaign.external_campaign_id = external_ids_dict.get('campaign_id') # Almacenar ID de nivel superior
                campaign.external_ids = external_ids_dict # Almacenar todo el dict
            campaign.status = 'published' # O 'active' / 'pending_review' dependiendo de la respuesta API
            results["message"] = api_result.get('message', "Publicado exitosamente.")
            results["success"] = True
            results["external_campaign_id"] = campaign.external_campaign_id
            results["external_ids"] = campaign.external_ids
            logger.info(f"[Tarea {self.request.id}] Publicada exitosamente Campaña {campaign_id} en Google Ads (Simulada). IDs Externos: {campaign.external_ids}")
        else:
            campaign.status = 'failed'
            results["message"] = api_result.get('message', "Fallo la publicación.")
            results["success"] = False
            logger.error(f"[Tarea {self.request.id}] Fallo al publicar Campaña {campaign_id} en Google Ads. Razón: {results['message']}")

        db.session.commit() # Confirmar actualizaciones de estado e ID

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"[Tarea {self.request.id}] Error de base de datos durante publicación en Google para campaña {campaign_id}: {e}")
        logger.error(traceback.format_exc())
        results["message"] = f"Error de base de datos: {e}"
        # Intentar actualizar estado a failed si es posible
        try:
            campaign = Campaign.query.get(campaign_id)
            if campaign:
                campaign.status = 'failed'
                db.session.commit()
        except Exception as inner_e:
             logger.error(f"[Tarea {self.request.id}] Fallo al actualizar estado de campaña a failed después de error de BD: {inner_e}")
             
    except Exception as e:
        db.session.rollback()
        logger.error(f"[Tarea {self.request.id}] Error inesperado durante publicación en Google para campaña {campaign_id}: {e}")
        logger.error(traceback.format_exc())
        results["message"] = f"Error inesperado: {e}"
        # Intentar actualizar estado a failed
        try:
            campaign = Campaign.query.get(campaign_id)
            if campaign:
                campaign.status = 'failed'
                db.session.commit()
        except Exception as inner_e:
             logger.error(f"[Tarea {self.request.id}] Fallo al actualizar estado de campaña a failed después de error inesperado: {inner_e}")
             
    return results

