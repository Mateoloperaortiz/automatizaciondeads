import dateutil.parser
from flask import current_app
from .extensions import db, celery # Importación de celery añadida
from . import models, api_clients
import logging # Añadir importación de logging

log = logging.getLogger(__name__) # Añadir instancia de logger

def _parse_datetime(value):
    """Analiza de forma segura las cadenas de fecha y hora de la API."""
    if not value:
        return None
    try:
        # Usar dateutil.parser para flexibilidad con formatos (como ISO 8601)
        return dateutil.parser.isoparse(value)
    except (ValueError, TypeError):
        current_app.logger.warning(f"No se pudo analizar la fecha y hora: {value}")
        return None

def _parse_date(value):
    """Analiza de forma segura las cadenas de fecha de la API."""
    if not value:
        return None
    try:
        return dateutil.parser.parse(value).date()
    except (ValueError, TypeError):
        current_app.logger.warning(f"No se pudo analizar la fecha: {value}")
        return None

def _get_float(data, key, default=None):
    """Obtiene de forma segura un valor flotante de un diccionario, convirtiendo si es necesario."""
    val = data.get(key)
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        current_app.logger.warning(f"No se pudo convertir el valor del insight a flotante para la clave '{key}': {val}")
        return default

def _get_int(data, key, default=None):
    """Obtiene de forma segura un valor entero de un diccionario, convirtiendo si es necesario."""
    val = data.get(key)
    if val is None:
        return default
    try:
        return int(float(val)) # Convertir primero a float para manejar "123.0"
    except (ValueError, TypeError):
        current_app.logger.warning(f"No se pudo convertir el valor del insight a entero para la clave '{key}': {val}")
        return default

def _sync_insights_for_object(object_id, level, date_preset):
    """Obtiene y actualiza los insights diarios para un preset de fecha dado para un objeto dado."""
    current_app.logger.debug(f"Obteniendo insights para {level} ID: {object_id} con preset: {date_preset}")
    # Obtener insights diarios para el preset dado
    insights_data = api_clients.get_meta_insights(
        object_id=object_id,
        level=level,
        date_preset=date_preset, # Usar el preset pasado
        time_increment=1 # Obtener datos diarios
    )

    if insights_data is None:
        current_app.logger.warning(f"Fallo al obtener insights para {level} {object_id}")
        return

    # Determinar IDs padres basado en el objeto que se está sincronizando
    parent_campaign_id = None
    parent_ad_set_id = None
    parent_ad_id = None

    if level == 'campaign':
        parent_campaign_id = object_id
    elif level == 'adset':
        ad_set = db.session.get(models.MetaAdSet, object_id)
        if ad_set:
            parent_ad_set_id = object_id
            parent_campaign_id = ad_set.campaign_id
        else:
            current_app.logger.warning(f"No se pudo encontrar el AdSet padre {object_id} al sincronizar sus insights.")
            # Opcionalmente retornar o continuar sin el ID de campaña
    elif level == 'ad':
        ad = db.session.get(models.MetaAd, object_id)
        if ad:
            parent_ad_id = object_id
            parent_ad_set_id = ad.ad_set_id
            # Obtener el ad set para conseguir el ID de campaña
            ad_set = db.session.get(models.MetaAdSet, parent_ad_set_id)
            if ad_set:
                parent_campaign_id = ad_set.campaign_id
            else:
                 current_app.logger.warning(f"No se pudo encontrar el AdSet padre {parent_ad_set_id} para el Ad {object_id} al sincronizar insights.")
        else:
            current_app.logger.warning(f"No se pudo encontrar el Ad padre {object_id} al sincronizar sus insights.")
            # Opcionalmente retornar o continuar sin IDs padres

    processed_count = 0
    for data in insights_data:
        date_start = _parse_date(data.get('date_start'))
        if not date_start:
            current_app.logger.warning(f"Registro de insight sin date_start para {level} {object_id}, omitiendo: {data}")
            continue

        # Clave Primaria: (object_id, level, date_start)
        pk_object_id = object_id # Usar el ID del objeto que estamos sincronizando para la PK
        pk = (pk_object_id, level, date_start)

        insight = db.session.get(models.MetaInsight, pk)

        if insight is None:
            # Usar el pk_object_id para la columna principal object_id
            insight = models.MetaInsight(object_id=pk_object_id, level=level, date_start=date_start)
            db.session.add(insight)
            current_app.logger.debug(f"Creando Insight: {level} {pk_object_id} en {date_start}")
        else:
            current_app.logger.debug(f"Actualizando Insight: {level} {pk_object_id} en {date_start}")

        # Mapear campos - usar funciones auxiliares para conversión segura de tipos
        insight.date_stop = _parse_date(data.get('date_stop'))

        # Asignar IDs padres determinados *antes* del bucle
        insight.meta_campaign_id = parent_campaign_id
        insight.meta_ad_set_id = parent_ad_set_id
        insight.meta_ad_id = parent_ad_id

        # Mapear métricas (estas vienen de los datos de la API para esta entrada específica de insight)
        insight.impressions = _get_int(data, 'impressions', 0)
        insight.clicks = _get_int(data, 'clicks', 0)
        insight.spend = _get_float(data, 'spend', 0.0)
        insight.reach = _get_int(data, 'reach', 0)
        insight.frequency = _get_float(data, 'frequency')
        insight.cpc = _get_float(data, 'cpc')
        insight.cpm = _get_float(data, 'cpm')
        insight.cpp = _get_float(data, 'cpp')
        insight.ctr = _get_float(data, 'ctr')
        insight.conversions = _get_int(data, 'conversions') # Puede necesitar refinamiento basado en acciones de conversión específicas
        insight.cost_per_conversion = _get_float(data, 'cost_per_conversion') # Puede necesitar refinamiento
        insight.actions = data.get('actions') # Almacenar como JSON
        insight.action_values = data.get('action_values') # Almacenar como JSON

        # --- Analizar acciones específicas ---
        # Resetear campos de acciones específicas
        insight.submit_applications = None
        insight.submit_applications_value = None
        insight.leads = None
        insight.leads_value = None
        insight.view_content = None
        insight.view_content_value = None

        # Auxiliar para encontrar valor de acción
        def _get_action_value(action_type, actions_list):
            if not actions_list:
                return None
            for action in actions_list:
                if action.get('action_type') == action_type:
                    return _get_float(action, 'value')
            return None

        # Analizar desde la lista 'actions' (conteos)
        actions_list = data.get('actions')
        if actions_list:
            for action in actions_list:
                action_type = action.get('action_type')
                action_count = _get_int(action, 'value')
                if action_type == 'offsite_conversion.fb_pixel_submit_application':
                    insight.submit_applications = action_count
                elif action_type == 'offsite_conversion.fb_pixel_lead':
                    insight.leads = action_count
                elif action_type == 'offsite_conversion.fb_pixel_view_content':
                    insight.view_content = action_count
        
        # Analizar desde la lista 'action_values' (valores)
        action_values_list = data.get('action_values')
        insight.submit_applications_value = _get_action_value('offsite_conversion.fb_pixel_purchase', action_values_list) # Nota: SubmitApp a menudo no tiene valor, podría usar Purchase aquí si es relevante
        insight.leads_value = _get_action_value('offsite_conversion.fb_pixel_lead', action_values_list)
        insight.view_content_value = _get_action_value('offsite_conversion.fb_pixel_view_content', action_values_list)
        # --- Fin Análisis de acciones específicas ---

        processed_count += 1

    current_app.logger.debug(f"Procesados {processed_count} registros de insight para {level} {object_id}")

@celery.task(bind=True, name='sync_tasks.async_sync_meta_data')
def async_sync_meta_data(self, ad_account_id, date_preset='last_30d'):
    """
    Tarea Celery para obtener asíncronamente Campañas, Conjuntos de Anuncios, Anuncios y sus Insights
    de la API de Meta para un ID de cuenta publicitaria dado y los guarda/actualiza en la base de datos.

    Args:
        ad_account_id (str): El ID de la Cuenta Publicitaria de Meta (ej., act_XXXXXXXX).
        date_preset (str): Preset de fecha de la API de Meta para obtener insights.

    Returns:
        dict: Un diccionario indicando éxito o fracaso y un mensaje.
    """
    # Usar contexto de aplicación proporcionado por la configuración de Celery
    app = current_app._get_current_object()
    logger = app.logger or log
    logger.info(f"[Tarea {self.request.id}] Iniciando sincronización asíncrona de Meta para la cuenta: {ad_account_id}, preset: {date_preset}")
    
    total_campaigns_processed = 0
    total_ad_sets_processed = 0
    total_ads_processed = 0
    
    # Mantener registro de errores encontrados
    errors_found = False
    error_messages = []

    try:
        logger.info(f"[Tarea {self.request.id}] Obteniendo campañas para la cuenta: {ad_account_id}")
        campaigns_data = api_clients.get_meta_campaigns(ad_account_id)
        if campaigns_data is None:
            msg = f"Fallo al obtener campañas para la cuenta {ad_account_id}. Abortando sincronización."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            error_messages.append(msg)
            errors_found = True
            # No se puede proceder sin campañas
            db.session.rollback() # Asegurar que no haya commits parciales de operaciones anteriores potenciales
            return {"success": False, "message": msg}

        # --- Manejar Campañas Eliminadas/Archivadas --- #
        existing_campaign_ids_in_db = {
            c.id for c in models.MetaCampaign.query.with_entities(models.MetaCampaign.id).filter_by(account_id=ad_account_id).all()
        }
        api_campaign_ids = {camp_data['id'] for camp_data in campaigns_data if 'id' in camp_data}

        campaign_ids_to_mark_deleted = existing_campaign_ids_in_db - api_campaign_ids
        if campaign_ids_to_mark_deleted:
            logger.info(f"[Tarea {self.request.id}] Marcando {len(campaign_ids_to_mark_deleted)} campañas como ELIMINADAS: {campaign_ids_to_mark_deleted}")
            campaigns_to_update = models.MetaCampaign.query.filter(models.MetaCampaign.id.in_(campaign_ids_to_mark_deleted)).all()
            for camp in campaigns_to_update:
                if camp.status not in ('DELETED', 'ARCHIVED'):
                    camp.status = 'DELETED'
                    camp.effective_status = 'DELETED'
                    db.session.add(camp)

        # --- Procesar Campañas desde la API --- #
        for camp_data in campaigns_data:
            campaign_id = camp_data.get('id')
            if not campaign_id:
                logger.warning(f"[Tarea {self.request.id}] Se encontraron datos de campaña sin ID. Omitiendo.")
                continue
            
            total_campaigns_processed += 1
            logger.debug(f"[Tarea {self.request.id}] Procesando ID de Campaña: {campaign_id}")
            campaign = db.session.get(models.MetaCampaign, campaign_id)
            if campaign is None:
                campaign = models.MetaCampaign(id=campaign_id, account_id=ad_account_id)
                db.session.add(campaign)
                logger.debug(f"[Tarea {self.request.id}] Creando Campaña: {campaign_id}")
            else:
                logger.debug(f"[Tarea {self.request.id}] Actualizando Campaña: {campaign_id}")

            # Actualizar campos
            campaign.name = camp_data.get('name')
            campaign.status = camp_data.get('status')
            campaign.objective = camp_data.get('objective')
            campaign.effective_status = camp_data.get('effective_status')
            campaign.created_time = _parse_datetime(camp_data.get('created_time'))
            campaign.start_time = _parse_datetime(camp_data.get('start_time'))
            campaign.stop_time = _parse_datetime(camp_data.get('stop_time'))
            campaign.daily_budget = camp_data.get('daily_budget')
            campaign.lifetime_budget = camp_data.get('lifetime_budget')
            campaign.budget_remaining = camp_data.get('budget_remaining')

            # --- Sincronizar Insights para esta Campaña --- #
            try:
                _sync_insights_for_object(campaign_id, 'campaign', date_preset)
            except Exception as insight_err:
                msg = f"Error sincronizando insights para la campaña {campaign_id}: {insight_err}"
                logger.error(f"[Tarea {self.request.id}] {msg}", exc_info=True)
                error_messages.append(msg)
                errors_found = True
                # ¿Continuar procesando otras campañas/conjuntos de anuncios/anuncios?

            # --- Sincronizar Conjuntos de Anuncios para esta Campaña --- #
            logger.debug(f"[Tarea {self.request.id}] Obteniendo conjuntos de anuncios para el ID de campaña: {campaign_id}")
            ad_sets_data = api_clients.get_meta_ad_sets(campaign_id)
            if ad_sets_data is None:
                 msg = f"Fallo al obtener conjuntos de anuncios para la campaña {campaign_id}. Omitiendo conjuntos de anuncios y anuncios para esta campaña."
                 logger.warning(f"[Tarea {self.request.id}] {msg}")
                 error_messages.append(msg)
                 errors_found = True
                 continue # Saltar a la siguiente campaña si fallan los conjuntos de anuncios

            # Manejar Conjuntos de Anuncios Eliminados/Archivados para esta Campaña
            existing_ad_set_ids_in_db = {
                 adset.id for adset in models.MetaAdSet.query.with_entities(models.MetaAdSet.id).filter_by(campaign_id=campaign_id).all()
            }
            api_ad_set_ids = {ad_set_data['id'] for ad_set_data in ad_sets_data if 'id' in ad_set_data}
            ad_set_ids_to_mark_deleted = existing_ad_set_ids_in_db - api_ad_set_ids
            if ad_set_ids_to_mark_deleted:
                logger.info(f"[Tarea {self.request.id}] Marcando {len(ad_set_ids_to_mark_deleted)} conjuntos de anuncios como ELIMINADOS: {ad_set_ids_to_mark_deleted}")
                ad_sets_to_update = models.MetaAdSet.query.filter(models.MetaAdSet.id.in_(ad_set_ids_to_mark_deleted)).all()
                for adset in ad_sets_to_update:
                    if adset.status not in ('DELETED', 'ARCHIVED'):
                        adset.status = 'DELETED'
                        adset.effective_status = 'DELETED'
                        db.session.add(adset)
            
            # Procesar Conjuntos de Anuncios desde la API
            for ad_set_data in ad_sets_data:
                ad_set_id = ad_set_data.get('id')
                if not ad_set_id:
                    logger.warning(f"[Tarea {self.request.id}] Se encontraron datos de conjunto de anuncios sin ID para la campaña {campaign_id}. Omitiendo.")
                    continue
                
                total_ad_sets_processed += 1
                logger.debug(f"[Tarea {self.request.id}] Procesando ID de Conjunto de Anuncios: {ad_set_id}")
                ad_set = db.session.get(models.MetaAdSet, ad_set_id)
                if ad_set is None:
                    ad_set = models.MetaAdSet(id=ad_set_id, campaign_id=campaign_id)
                    db.session.add(ad_set)
                    logger.debug(f"[Tarea {self.request.id}] Creando Conjunto de Anuncios: {ad_set_id}")
                else:
                    logger.debug(f"[Tarea {self.request.id}] Actualizando Conjunto de Anuncios: {ad_set_id}")

                # Actualizar campos
                ad_set.name = ad_set_data.get('name')
                ad_set.status = ad_set_data.get('status')
                ad_set.effective_status = ad_set_data.get('effective_status')
                ad_set.daily_budget = ad_set_data.get('daily_budget')
                ad_set.lifetime_budget = ad_set_data.get('lifetime_budget')
                ad_set.budget_remaining = ad_set_data.get('budget_remaining')
                ad_set.optimization_goal = ad_set_data.get('optimization_goal')
                ad_set.billing_event = ad_set_data.get('billing_event')
                ad_set.bid_amount = ad_set_data.get('bid_amount')
                ad_set.created_time = _parse_datetime(ad_set_data.get('created_time'))
                ad_set.start_time = _parse_datetime(ad_set_data.get('start_time'))
                ad_set.end_time = _parse_datetime(ad_set_data.get('end_time'))

                # --- Sincronizar Insights para este Conjunto de Anuncios --- #
                try:
                    _sync_insights_for_object(ad_set_id, 'adset', date_preset)
                except Exception as insight_err:
                    msg = f"Error sincronizando insights para el conjunto de anuncios {ad_set_id}: {insight_err}"
                    logger.error(f"[Tarea {self.request.id}] {msg}", exc_info=True)
                    error_messages.append(msg)
                    errors_found = True
                    # ¿Continuar procesando otros conjuntos de anuncios/anuncios?

                # --- Sincronizar Anuncios para este Conjunto de Anuncios --- #
                logger.debug(f"[Tarea {self.request.id}] Obteniendo anuncios para el ID de conjunto de anuncios: {ad_set_id}")
                ads_data = api_clients.get_meta_ads(ad_set_id)
                if ads_data is None:
                     msg = f"Fallo al obtener anuncios para el conjunto de anuncios {ad_set_id}. Omitiendo anuncios para este conjunto de anuncios."
                     logger.warning(f"[Tarea {self.request.id}] {msg}")
                     error_messages.append(msg)
                     errors_found = True
                     continue # Saltar al siguiente conjunto de anuncios si fallan los anuncios

                # Manejar Anuncios Eliminados/Archivados para este Conjunto de Anuncios
                existing_ad_ids_in_db = {
                     ad.id for ad in models.MetaAd.query.with_entities(models.MetaAd.id).filter_by(ad_set_id=ad_set_id).all()
                }
                api_ad_ids = {ad_data['id'] for ad_data in ads_data if 'id' in ad_data}
                ad_ids_to_mark_deleted = existing_ad_ids_in_db - api_ad_ids
                if ad_ids_to_mark_deleted:
                    logger.info(f"[Tarea {self.request.id}] Marcando {len(ad_ids_to_mark_deleted)} anuncios como ELIMINADOS: {ad_ids_to_mark_deleted}")
                    ads_to_update = models.MetaAd.query.filter(models.MetaAd.id.in_(ad_ids_to_mark_deleted)).all()
                    for ad in ads_to_update:
                        if ad.status not in ('DELETED', 'ARCHIVED'):
                            ad.status = 'DELETED'
                            ad.effective_status = 'DELETED'
                            db.session.add(ad)
                
                # Procesar Anuncios desde la API
                for ad_data in ads_data:
                    ad_id = ad_data.get('id')
                    if not ad_id:
                        logger.warning(f"[Tarea {self.request.id}] Se encontraron datos de anuncio sin ID para el conjunto de anuncios {ad_set_id}. Omitiendo.")
                        continue
                    
                    total_ads_processed += 1
                    logger.debug(f"[Tarea {self.request.id}] Procesando ID de Anuncio: {ad_id}")
                    ad = db.session.get(models.MetaAd, ad_id)
                    if ad is None:
                        ad = models.MetaAd(id=ad_id, ad_set_id=ad_set_id)
                        db.session.add(ad)
                        logger.debug(f"[Tarea {self.request.id}] Creando Anuncio: {ad_id}")
                    else:
                        logger.debug(f"[Tarea {self.request.id}] Actualizando Anuncio: {ad_id}")

                    # Actualizar campos
                    ad.name = ad_data.get('name')
                    ad.status = ad_data.get('status')
                    ad.effective_status = ad_data.get('effective_status')
                    ad.created_time = _parse_datetime(ad_data.get('created_time'))
                    ad.creative_id = ad_data.get('creative_id')
                    ad.creative_details = ad_data.get('creative') # Almacenar diccionario completo del creativo

                    # --- Sincronizar Insights para este Anuncio --- #
                    try:
                        _sync_insights_for_object(ad_id, 'ad', date_preset)
                    except Exception as insight_err:
                        msg = f"Error sincronizando insights para el anuncio {ad_id}: {insight_err}"
                        logger.error(f"[Tarea {self.request.id}] {msg}", exc_info=True)
                        error_messages.append(msg)
                        errors_found = True
                        # ¿Continuar procesando otros anuncios?

        # Confirmar todos los cambios realizados durante la sincronización para esta cuenta
        db.session.commit()
        logger.info(f"[Tarea {self.request.id}] Commit de sincronización exitoso para la cuenta {ad_account_id}. Procesados: {total_campaigns_processed} C, {total_ad_sets_processed} AS, {total_ads_processed} A.")
        
        success_message = f"Sincronización completada para la cuenta {ad_account_id}. Procesados: {total_campaigns_processed} campañas, {total_ad_sets_processed} conjuntos de anuncios, {total_ads_processed} anuncios."
        if errors_found:
            success_message += f" Se encontraron errores: {', '.join(error_messages[:3])} ... (revisar logs para detalles)"
        
        return {"success": not errors_found, "message": success_message}

    except Exception as e:
        db.session.rollback() # Rollback en caso de error inesperado
        msg = f"Error inesperado durante la sincronización para la cuenta {ad_account_id}: {e}"
        logger.error(f"[Tarea {self.request.id}] {msg}", exc_info=True)
        # Volver a lanzar la excepción para marcar la tarea Celery como fallida
        # Alternativamente, devolver estado de fallo:
        return {"success": False, "message": msg}

# --- ELIMINAR FUNCIÓN DE SINCRONIZACIÓN ANTIGUA --- #
# def sync_meta_data(ad_account_id, date_preset='last_30d'):
#    ... (Lógica síncrona antigua eliminada) ...

