import os
from dotenv import load_dotenv
from flask import current_app # Para logging
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError
import json
from typing import Tuple
import google.generativeai as genai
# --- Importaciones de Google Ads ---
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import yaml # Google Ads a menudo usa YAML para la configuración
import time
from google.api_core import protobuf_helpers
import uuid # Para nombres únicos si es necesario
import traceback

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --- Cliente API de Anuncios Meta (Facebook/Instagram) --- #

MY_APP_ID = os.getenv('META_APP_ID')
MY_APP_SECRET = os.getenv('META_APP_SECRET')
MY_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')

# Función para inicializar la API de Meta
def initialize_meta_api():
    """Inicializa la API de Anuncios de Facebook con credenciales de variables de entorno."""
    if not all([MY_APP_ID, MY_APP_SECRET, MY_ACCESS_TOKEN]):
        print("Error: META_APP_ID, META_APP_SECRET y META_ACCESS_TOKEN deben configurarse en variables de entorno o archivo .env.")
        # Opcionalmente lanzar una excepción o devolver None/False
        return None
    try:
        FacebookAdsApi.init(MY_APP_ID, MY_APP_SECRET, MY_ACCESS_TOKEN)
        print("API de Anuncios de Facebook inicializada correctamente.")
        return FacebookAdsApi.get_default_api() # Devolver la instancia de API inicializada
    except FacebookRequestError as e:
        if current_app:
            current_app.logger.error(f"Error inicializando la API de Anuncios de Facebook: {e}")
        else:
            print(f"Error inicializando la API de Anuncios de Facebook: {e}")
        # Manejar el error apropiadamente (registrar, lanzar, etc.)
        return None

# Obtener Cuentas Publicitarias
def get_meta_ad_accounts():
    """Obtiene las cuentas publicitarias asociadas con el token de acceso."""
    api = initialize_meta_api()
    if not api:
        return [] # Devolver lista vacía o manejar error

    try:
        # Importar el objeto User que representa al propietario del token
        from facebook_business.adobjects.user import User

        user = User(fbid='me') 
        ad_accounts = user.get_ad_accounts(fields=['id', 'name', 'account_status'])
        
        accounts_list = [
            {
                'id': account['id'], 
                'name': account['name'], 
                'status': account['account_status']
            } 
            for account in ad_accounts
        ]
        print(f"Se recuperaron {len(accounts_list)} cuentas publicitarias.")
        return accounts_list
    except FacebookRequestError as e:
        print(f"Error al obtener las cuentas publicitarias: {e}")
        return [] # Devolver vacío en caso de error
    except ImportError as e:
         print(f"Error al importar el objeto del SDK de Facebook: {e}")
         return []

# Función para obtener Campañas para una Cuenta Publicitaria específica
def get_meta_campaigns(ad_account_id):
    """Obtiene campañas para un ID de cuenta publicitaria dado."""
    api = initialize_meta_api()
    if not api:
        return []

    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.campaign import Campaign

        # Definir los campos que deseas recuperar para las campañas
        fields = [
            Campaign.Field.id,
            Campaign.Field.name,
            Campaign.Field.status,
            Campaign.Field.objective,
            Campaign.Field.effective_status,
            Campaign.Field.created_time,
            Campaign.Field.start_time,
            Campaign.Field.stop_time,
            Campaign.Field.daily_budget,
            Campaign.Field.lifetime_budget,
            Campaign.Field.budget_remaining, # Útil con presupuestos totales
        ]

        account = AdAccount(ad_account_id)
        # Obtener la primera página
        campaigns_pager = account.get_campaigns(fields=fields, params={'limit': 100}) # Usar un límite razonable por página
        campaigns_list = []

        # Iterar a través de todas las páginas
        while True:
            for campaign in campaigns_pager:
                campaigns_list.append({
                    'id': campaign[Campaign.Field.id],
                    'name': campaign.get(Campaign.Field.name),
                    'status': campaign.get(Campaign.Field.status),
                    'objective': campaign.get(Campaign.Field.objective),
                    'effective_status': campaign.get(Campaign.Field.effective_status),
                    'created_time': campaign.get(Campaign.Field.created_time),
                    'start_time': campaign.get(Campaign.Field.start_time),
                    'stop_time': campaign.get(Campaign.Field.stop_time),
                    'daily_budget': campaign.get(Campaign.Field.daily_budget),
                    'lifetime_budget': campaign.get(Campaign.Field.lifetime_budget),
                    'budget_remaining': campaign.get(Campaign.Field.budget_remaining),
                })
            
            # Intentar cargar la siguiente página
            try:
                next_page = campaigns_pager.load_next_page()
                if next_page:
                    campaigns_pager = next_page
                else:
                    break # No hay más páginas
            except FacebookRequestError as page_error:
                # Registrar error al obtener la siguiente página pero continuar si es posible
                log_msg = f"Error al cargar la siguiente página de campañas para la cuenta {ad_account_id}: {page_error}"
                if current_app: current_app.logger.warning(log_msg)
                else: print(log_msg)
                break # Detener la paginación en caso de error

        print(f"Se recuperaron {len(campaigns_list)} campañas (todas las páginas) para la cuenta {ad_account_id}.")
        return campaigns_list
    except FacebookRequestError as e:
        log_msg = f"Error al obtener campañas para la cuenta {ad_account_id}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return []
    except ImportError as e:
        log_msg = f"Error al importar el objeto del SDK de Facebook: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return []

# Función para obtener Conjuntos de Anuncios para una Campaña específica
def get_meta_ad_sets(campaign_id):
    """Obtiene conjuntos de anuncios para un ID de campaña dado."""
    api = initialize_meta_api()
    if not api:
        return []

    try:
        from facebook_business.adobjects.campaign import Campaign
        from facebook_business.adobjects.adset import AdSet

        fields = [
            AdSet.Field.id,
            AdSet.Field.name,
            AdSet.Field.status,
            AdSet.Field.effective_status,
            AdSet.Field.daily_budget,
            AdSet.Field.lifetime_budget,
            AdSet.Field.budget_remaining,
            AdSet.Field.optimization_goal,
            AdSet.Field.billing_event,
            AdSet.Field.bid_amount, # control de costo
            AdSet.Field.created_time,
            AdSet.Field.start_time,
            AdSet.Field.end_time,
        ]

        campaign = Campaign(campaign_id)
        ad_sets_pager = campaign.get_ad_sets(fields=fields, params={'limit': 100})
        ad_sets_list = []
        
        while True:
            for ad_set in ad_sets_pager:
                ad_sets_list.append({
                    'id': ad_set[AdSet.Field.id],
                    'name': ad_set.get(AdSet.Field.name),
                    'status': ad_set.get(AdSet.Field.status),
                    'effective_status': ad_set.get(AdSet.Field.effective_status),
                    'daily_budget': ad_set.get(AdSet.Field.daily_budget),
                    'lifetime_budget': ad_set.get(AdSet.Field.lifetime_budget),
                    'budget_remaining': ad_set.get(AdSet.Field.budget_remaining),
                    'optimization_goal': ad_set.get(AdSet.Field.optimization_goal),
                    'billing_event': ad_set.get(AdSet.Field.billing_event),
                    'bid_amount': ad_set.get(AdSet.Field.bid_amount),
                    'created_time': ad_set.get(AdSet.Field.created_time),
                    'start_time': ad_set.get(AdSet.Field.start_time),
                    'end_time': ad_set.get(AdSet.Field.end_time),
                })
            
            try:
                next_page = ad_sets_pager.load_next_page()
                if next_page:
                    ad_sets_pager = next_page
                else:
                    break
            except FacebookRequestError as page_error:
                log_msg = f"Error al cargar la siguiente página de conjuntos de anuncios para la campaña {campaign_id}: {page_error}"
                if current_app: current_app.logger.warning(log_msg)
                else: print(log_msg)
                break

        print(f"Se recuperaron {len(ad_sets_list)} conjuntos de anuncios (todas las páginas) para la campaña {campaign_id}.")
        return ad_sets_list
    except FacebookRequestError as e:
        log_msg = f"Error al obtener conjuntos de anuncios para la campaña {campaign_id}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return []
    except ImportError as e:
        log_msg = f"Error al importar el objeto del SDK de Facebook: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return []

# Función para obtener Anuncios para un Conjunto de Anuncios específico
def get_meta_ads(ad_set_id):
    """Obtiene anuncios para un ID de conjunto de anuncios dado, incluyendo detalles básicos de Creative Ads."""
    api = initialize_meta_api()
    if not api:
        return []

    try:
        from facebook_business.adobjects.adset import AdSet
        from facebook_business.adobjects.ad import Ad
        from facebook_business.adobjects.adcreative import AdCreative # Para info de creatividad

        fields = [
            Ad.Field.id,
            Ad.Field.name,
            Ad.Field.status,
            Ad.Field.effective_status,
            Ad.Field.creative,
            Ad.Field.created_time,
            # Ad.Field.adset_id,
            # Ad.Field.campaign_id,
        ]

        creative_fields = [
            AdCreative.Field.id,
            AdCreative.Field.name,
            AdCreative.Field.body,
            AdCreative.Field.title,
            AdCreative.Field.thumbnail_url, # Generalmente más rápido/pequeño que image_url
            AdCreative.Field.image_url, # URL completa de la imagen
            AdCreative.Field.object_story_spec, # Contiene datos de enlace, mensaje, etc.
            AdCreative.Field.call_to_action_type,
        ]

        ad_set = AdSet(ad_set_id)
        ads_pager = ad_set.get_ads(fields=fields, params={'limit': 50})
        ads_list = []

        while True:
            current_page_ads = []
            for ad in ads_pager:
                current_page_ads.append(ad)
                ad_data = {
                    'id': ad[Ad.Field.id],
                    'name': ad.get(Ad.Field.name),
                    'status': ad.get(Ad.Field.status),
                    'effective_status': ad.get(Ad.Field.effective_status),
                    'creative_id': ad.get(Ad.Field.creative, {}).get('id') if ad.get(Ad.Field.creative) else None,
                    'created_time': ad.get(Ad.Field.created_time),
                    'creative_details': None # Marcador de posición para info de creatividad
                }
                
                # Obtener detalles de la creatividad si existe creative_id
                if ad_data['creative_id']:
                    try:
                        creative = AdCreative(ad_data['creative_id']).api_get(fields=creative_fields)
                        # Extraer detalles relevantes de la creatividad (manejar posibles campos faltantes)
                        story_spec = creative.get(AdCreative.Field.object_story_spec, {})
                        link_data = story_spec.get('link_data', {})
                        video_data = story_spec.get('video_data', {})
                        
                        ad_data['creative_details'] = {
                            'name': creative.get(AdCreative.Field.name),
                            'body': creative.get(AdCreative.Field.body),
                            'title': creative.get(AdCreative.Field.title),
                            'thumbnail_url': creative.get(AdCreative.Field.thumbnail_url),
                            'image_url': creative.get(AdCreative.Field.image_url),
                            'call_to_action': creative.get(AdCreative.Field.call_to_action_type),
                            'message': link_data.get('message'), # Común para anuncios de feed
                            'link': link_data.get('link'),
                            # Añadir más campos de story_spec o video_data según sea necesario
                        }
                    except FacebookRequestError as creative_e:
                        # Registrar error al obtener creatividad específica pero continuar con otros anuncios
                        log_msg = f"No se pudieron obtener los detalles de la creatividad para {ad_data['creative_id']} (Anuncio: {ad_data['id']}): {creative_e}"
                        if current_app: current_app.logger.warning(log_msg)
                        else: print(log_msg)
                    except ImportError as import_e:
                        log_msg = f"Error de importación al obtener detalles de la creatividad para {ad_data['creative_id']}: {import_e}"
                        if current_app: current_app.logger.error(log_msg)
                        else: print(log_msg)
                        # Dejar de intentar obtener creatividades si falla la importación
                        break 

                ads_list.append(ad_data)
            
            # Comprobar si la página actual estaba vacía antes de intentar cargar la siguiente (evita bucle infinito en resultados vacíos)
            if not current_page_ads:
                break
            
            try:
                next_page = ads_pager.load_next_page()
                if next_page:
                    ads_pager = next_page
                else:
                    break
            except FacebookRequestError as page_error:
                log_msg = f"Error al cargar la siguiente página de anuncios para el conjunto de anuncios {ad_set_id}: {page_error}"
                if current_app: current_app.logger.warning(log_msg)
                else: print(log_msg)
                break

        print(f"Se recuperaron {len(ads_list)} anuncios (todas las páginas) para el conjunto de anuncios {ad_set_id}.")
        return ads_list
    except FacebookRequestError as e:
        log_msg = f"Error al obtener anuncios para el conjunto de anuncios {ad_set_id}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return []
    except ImportError as e:
        log_msg = f"Error al importar el objeto del SDK de Facebook: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return []

# Función para obtener Insights (Métricas)
def get_meta_insights(object_id, level, date_preset='last_30d', time_increment=None, fields=None):
    """
    Obtiene insights para un ID de objeto y nivel específicos.

    Args:
        object_id (str): El ID del objeto (cuenta, campaña, conjunto de anuncios, anuncio).
        level (str): El nivel de agregación ('account', 'campaign', 'adset', 'ad').
        date_preset (str, opcional): El preajuste de rango de fechas. Por defecto 'last_30d'.
        time_increment (int, opcional): Periodo de agregación. 1 para diario. Por defecto None (agregado).
        fields (list, opcional): Campos específicos a recuperar. Por defecto un conjunto estándar.

    Returns:
        list: Una lista de diccionarios de datos de insights, o None si ocurre un error.
    """
    api = initialize_meta_api()
    if not api:
        return None

    # Campos por defecto si no se proporcionan
    if fields is None:
        fields = [
            # Añadir IDs de padres para enlazar insights correctamente
            'campaign_id',
            'adset_id',
            'ad_id',
            # Métricas estándar
            'impressions',
            'clicks',
            'spend',
            'ctr', # Tasa de Clics
            'cpc', # Coste Por Clic
            'reach',
            'frequency',
            'inline_link_clicks',
            'cost_per_inline_link_click',
            'actions', # Conversiones, etc. (puede ser complejo, quizás obtener tipos de acción específicos)
            'action_values',
            # Ejemplo de acción específica: 'offsite_conversion.fb_pixel_purchase'
        ]

    params = {
        'level': level,
        'date_preset': date_preset,
        'limit': 500 # Obtener hasta 500 resultados por página
    }
    # Añadir time_increment si se proporciona
    if time_increment is not None:
        params['time_increment'] = time_increment

    try:
        # Determinar dinámicamente la clase del objeto basada en el nivel
        object_instance = None
        if level == 'campaign':
            from facebook_business.adobjects.campaign import Campaign
            object_instance = Campaign(object_id)
        elif level == 'adset':
            from facebook_business.adobjects.adset import AdSet
            object_instance = AdSet(object_id)
        elif level == 'ad':
            from facebook_business.adobjects.ad import Ad
            object_instance = Ad(object_id)
        elif level == 'account':
            from facebook_business.adobjects.adaccount import AdAccount
            object_instance = AdAccount(object_id)
        else:
            log_msg = f"Error: Nivel inválido '{level}'. Debe ser uno de: campaign, adset, ad, account"
            if current_app: current_app.logger.error(log_msg)
            else: print(log_msg)
            return []
        
        insights_pager = object_instance.get_insights(fields=fields, params=params)
        insights_list = []

        while True:
            current_page_insights = []
            for insight in insights_pager:
                current_page_insights.append(insight)
                insights_list.append(dict(insight))

            if not current_page_insights:
                break

            try:
                next_page = insights_pager.load_next_page()
                if next_page:
                    insights_pager = next_page
                else:
                    break
            except FacebookRequestError as page_error:
                log_msg = f"Error al cargar la siguiente página de insights para {level} {object_id}: {page_error}"
                if current_app: current_app.logger.warning(log_msg)
                else: print(log_msg)
                break
            
        print(f"Se recuperaron {len(insights_list)} entradas de insights (todas las páginas) para {level} {object_id} ({date_preset}).")
        return insights_list

    except FacebookRequestError as e:
        log_msg = f"Error al obtener insights para {level} {object_id}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return []
    except ImportError as e:
        log_msg = f"Error al importar el objeto del SDK de Facebook: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return []

# Marcador de posición para el cliente de la API de Google Ads
def google_ads_client():
    pass

# Marcador de posición para el cliente de la API de X Ads (Meta Futura)
def x_ads_client():
    pass

# --- Funciones de Creación de Anuncios Meta --- #

def create_meta_campaign(ad_account_id: str, name: str, objective: str, status: str = 'PAUSED', special_ad_categories: list = None) -> str | None:
    """
    Crea una nueva campaña en la Cuenta Publicitaria de Meta especificada.

    Args:
        ad_account_id: El ID de la cuenta publicitaria (ej., 'act_XXXXXXXX').
        name: El nombre para la nueva campaña.
        objective: El objetivo de la campaña (ej., 'LINK_CLICKS', 'CONVERSIONS', 'REACH').
                   Ver documentación de Meta para objetivos válidos.
        status: Estado inicial ('ACTIVE' o 'PAUSED'). Por defecto 'PAUSED'.
        special_ad_categories: Lista de categorías especiales de anuncios si aplica (ej., ['EMPLOYMENT']). Por defecto None.

    Returns:
        El ID de la campaña recién creada, o None si falló la creación.
    """
    api = initialize_meta_api()
    if not api:
        log_msg = "No se puede crear la campaña: API de Meta no inicializada."
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None

    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.campaign import Campaign

        params = {
            Campaign.Field.name: name,
            Campaign.Field.objective: objective,
            Campaign.Field.status: status,
            Campaign.Field.special_ad_categories: special_ad_categories if special_ad_categories else ['NONE'] # Usar ['NONE'] si no hay categoría específica
        }

        account = AdAccount(ad_account_id)
        new_campaign = account.create_campaign(params=params)
        campaign_id = new_campaign.get(Campaign.Field.id)

        log_msg = f"Se creó correctamente la Campaña Meta ID: {campaign_id} para la cuenta {ad_account_id}"
        if current_app: current_app.logger.info(log_msg)
        else: print(log_msg)
        return campaign_id

    except FacebookRequestError as e:
        log_msg = f"Error al crear la campaña Meta '{name}' para la cuenta {ad_account_id}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        # Opcionalmente analizar e.api_error_message() o e.api_response() para más detalles
        return None
    except ImportError as e:
        log_msg = f"Error al importar el objeto del SDK de Facebook durante la creación de la campaña: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None
    except Exception as e: # Capturar cualquier otro error inesperado
        log_msg = f"Error inesperado al crear la campaña Meta '{name}': {e}"
        if current_app: current_app.logger.error(log_msg, exc_info=True) # Incluir traceback
        else: print(log_msg)
        return None

def create_meta_ad_set(ad_account_id, campaign_id, name, optimization_goal, billing_event, daily_budget_cents, targeting_spec, status, bid_amount=None):
    """Crea un nuevo Conjunto de Anuncios Meta y devuelve su ID."""
    api = initialize_meta_api()
    if not api:
        return None

    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.adset import AdSet

        account = AdAccount(ad_account_id)
        params = {
            AdSet.Field.campaign_id: campaign_id,
            AdSet.Field.name: name,
            AdSet.Field.optimization_goal: optimization_goal,
            AdSet.Field.billing_event: billing_event,
            AdSet.Field.daily_budget: daily_budget_cents,
            AdSet.Field.targeting: targeting_spec, # Pasar el diccionario directamente
            AdSet.Field.status: status,
            # Requerido para algunos objetivos/optimizaciones, el valor por defecto puede funcionar
            # 'promoted_object': {'page_id': <your_page_id>}, # Requerido para el objetivo Page Likes
            # Considerar establecer fechas de inicio/fin si es necesario
        }
        # Añadir bid_amount si se proporciona (requerido para algunas combinaciones de optimización/facturación)
        if bid_amount is not None:
            params[AdSet.Field.bid_amount] = bid_amount
            
        ad_set = account.create_ad_set(params=params)
        ad_set_id = ad_set.get(AdSet.Field.id)
        log_msg = f"Se creó correctamente el conjunto de anuncios '{name}' con ID: {ad_set_id}"

        if current_app: current_app.logger.info(log_msg)
        else: print(log_msg)
        return ad_set_id

    except FacebookRequestError as e:
        log_msg = f"Error al crear el Conjunto de Anuncios Meta '{name}' en la Campaña {campaign_id}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None
    except ImportError as e:
        log_msg = f"Error al importar el objeto del SDK de Facebook durante la creación del conjunto de anuncios: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None
    except Exception as e:
        log_msg = f"Error inesperado al crear el Conjunto de Anuncios Meta '{name}': {e}"
        if current_app: current_app.logger.error(log_msg, exc_info=True)
        else: print(log_msg)
        return None

def create_meta_ad_creative(ad_account_id: str, name: str, page_id: str, 
                                message: str, link_url: str, 
                                link_title: str = None, 
                                link_description: str = None, # Añadir link_description
                                image_hash: str = None) -> str | None:
    """
    Crea una Creatividad de Anuncio de Enlace simple.

    Args:
        ad_account_id: El ID de la cuenta publicitaria.
        name: Nombre para la creatividad del anuncio.
        page_id: El ID de la Página de Facebook a asociar con el anuncio.
        message: El cuerpo de texto principal del anuncio.
        link_url: La URL de destino (ej., enlace a la oferta de trabajo).
        link_title: Título opcional mostrado con el enlace (titular).
        link_description: Descripción opcional mostrada con el enlace.
        image_hash: Hash opcional de una imagen previamente subida.

    Returns:
        El ID de la creatividad del anuncio recién creada, o None si falló la creación.
    """
    api = initialize_meta_api()
    if not api:
        log_msg = "No se puede crear la creatividad del anuncio: API de Meta no inicializada."
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None
    
    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.adcreative import AdCreative
        from facebook_business.adobjects.adcreativelinkdata import AdCreativeLinkData
        from facebook_business.adobjects.adcreativeobjectstoryspec import AdCreativeObjectStorySpec

        # Definir los datos del enlace
        link_data = AdCreativeLinkData()
        link_data[AdCreativeLinkData.Field.message] = message
        link_data[AdCreativeLinkData.Field.link] = link_url
        if link_title:
             link_data[AdCreativeLinkData.Field.name] = link_title # Usar 'name' para el titular/título del enlace
        if link_description:
             link_data[AdCreativeLinkData.Field.description] = link_description # Usar 'description' para la descripción del enlace
        if image_hash:
             link_data[AdCreativeLinkData.Field.image_hash] = image_hash
        # Establecer call_to_action (Ejemplo: APPLY_NOW)
        link_data[AdCreativeLinkData.Field.call_to_action] = {
            'type': 'APPLY_NOW', 
            'value': {
                'link': link_url
            }
        }

        # Definir la especificación de la historia del objeto (asocia datos de enlace con la página)
        object_story_spec = AdCreativeObjectStorySpec()
        object_story_spec[AdCreativeObjectStorySpec.Field.page_id] = page_id
        object_story_spec[AdCreativeObjectStorySpec.Field.link_data] = link_data

        # Definir los parámetros de AdCreative
        params = {
            AdCreative.Field.name: name,
            AdCreative.Field.object_story_spec: object_story_spec,
            # Añadir otros campos como 'call_to_action_type' si es necesario
        }

        account = AdAccount(ad_account_id)
        new_creative = account.create_ad_creative(params=params)
        creative_id = new_creative.get(AdCreative.Field.id)

        log_msg = f"Se creó correctamente la Creatividad de Anuncio Meta ID: {creative_id}"
        if current_app: current_app.logger.info(log_msg)
        else: print(log_msg)
        return creative_id

    except FacebookRequestError as e:
        log_msg = f"Error al crear la Creatividad de Anuncio Meta '{name}': {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None
    except ImportError as e:
        log_msg = f"Error al importar el objeto del SDK de Facebook durante la creación de la creatividad del anuncio: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None
    except Exception as e:
        log_msg = f"Error inesperado al crear la Creatividad de Anuncio Meta '{name}': {e}"
        if current_app: current_app.logger.error(log_msg, exc_info=True)
        else: print(log_msg)
        return None

def create_meta_ad(ad_account_id: str, name: str, ad_set_id: str, creative_id: str, status: str = 'PAUSED') -> str | None:
    """
    Crea un Anuncio enlazando un Conjunto de Anuncios y una Creatividad de Anuncio.

    Args:
        ad_account_id: El ID de la cuenta publicitaria.
        name: El nombre para el nuevo anuncio.
        ad_set_id: El ID del conjunto de anuncios padre.
        creative_id: El ID de la creatividad del anuncio a usar.
        status: Estado inicial ('ACTIVE' o 'PAUSED'). Por defecto 'PAUSED'.

    Returns:
        El ID del anuncio recién creado, o None si falló la creación.
    """
    api = initialize_meta_api()
    if not api:
        log_msg = "No se puede crear el anuncio: API de Meta no inicializada."
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None

    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.ad import Ad

        params = {
            Ad.Field.name: name,
            Ad.Field.adset_id: ad_set_id,
            Ad.Field.creative: {'creative_id': creative_id},
            Ad.Field.status: status,
        }

        account = AdAccount(ad_account_id)
        new_ad = account.create_ad(params=params)
        ad_id = new_ad.get(Ad.Field.id)

        log_msg = f"Se creó correctamente el Anuncio Meta ID: {ad_id} en el Conjunto de Anuncios {ad_set_id}"
        if current_app: current_app.logger.info(log_msg)
        else: print(log_msg)
        return ad_id

    except FacebookRequestError as e:
        log_msg = f"Error al crear el Anuncio Meta '{name}' en el Conjunto de Anuncios {ad_set_id}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        # Registrar error detallado si está disponible
        # print("Código de Error API:", e.api_error_code())
        # print("Subcódigo de Error API:", e.api_error_subcode())
        # print("Mensaje de Error API:", e.api_error_message())
        # print("Tipo de Error API:", e.api_error_type())
        # print("Respuesta API:", e.api_response())
        return None
    except ImportError as e:
        log_msg = f"Error al importar el objeto del SDK de Facebook durante la creación del anuncio: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None
    except Exception as e:
        log_msg = f"Error inesperado al crear el Anuncio Meta '{name}': {e}"
        if current_app: current_app.logger.error(log_msg, exc_info=True)
        else: print(log_msg)
        return None

def create_meta_custom_audience(ad_account_id, name, description, customer_file_source, subtype, user_identifiers, identifier_type="EXTERN_ID"):
    """Crea una Audiencia Personalizada Meta a partir de una lista de IDs externos y devuelve su ID."""
    api = initialize_meta_api()
    if not api:
        return None
    
    if not user_identifiers:
        log_msg = "No se puede crear la audiencia personalizada: No se proporcionaron identificadores de usuario."
        if current_app: current_app.logger.warning(log_msg)
        else: print(log_msg)
        return None

    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.customaudience import CustomAudience
        import hashlib # Para hashing (aunque quizás no lo necesitemos para EXTERN_ID)
        import json # Para formatear datos de usuario

        account = AdAccount(ad_account_id)

        # 1. Crear el contenedor de la Audiencia Personalizada
        params = {
            CustomAudience.Field.name: name,
            CustomAudience.Field.description: description,
            CustomAudience.Field.subtype: subtype, # ej., CUSTOM, WEBSITE, APP, LOOKALIKE
            CustomAudience.Field.customer_file_source: customer_file_source, # ej., USER_PROVIDED_ONLY, PARTNER_PROVIDED_ONLY
            # Para anuncios de empleo que usan audiencias personalizadas, se necesita enlace de exclusión
            CustomAudience.Field.is_value_based: False,
            # 'rule': '""' # Para CAs de sitio web/app, no necesario para carga de archivo
        }
        audience = account.create_custom_audience(params=params)
        audience_id = audience.get(CustomAudience.Field.id)
        log_msg = f"Se creó correctamente el contenedor de audiencia personalizada '{name}' con ID: {audience_id}"
        if current_app: current_app.logger.info(log_msg)
        else: print(log_msg)

        # 2. Añadir usuarios a la audiencia
        # Formatear usuarios según las especificaciones de la API
        # Para EXTERN_ID, el esquema es simplemente una lista de strings
        # Meta recomienda hashear PII, pero EXTERN_ID podría no requerirlo si son IDs internos.
        # Asumamos que candidate_id es seguro para subir directamente como EXTERN_ID.
        # Si se necesita hashing: list_of_hashes = [hashlib.sha256(id.encode('utf-8')).hexdigest() for id in user_identifiers]
        
        # Preparar payload para añadir usuarios
        # El esquema depende de identifier_type. Para EXTERN_ID, es solo una lista de strings.
        # Ver: https://developers.facebook.com/docs/marketing-api/audiences/guides/custom-audiences#adding-users
        users_payload = {
            'schema': ['EXTERN_ID'],
            'data': [[ext_id] for ext_id in user_identifiers] # Cada ID necesita estar en su propia lista
        }
        
        # La API espera datos como string JSON para el parámetro 'users'
        # Sin embargo, el SDK de Python podría manejar el objeto directamente vía add_users
        
        target_audience = CustomAudience(audience_id)
        # Usando el método add_users que maneja el formato
        # Añadir is_raw=True para identificadores no PII como EXTERN_ID
        response = target_audience.add_users(schema=users_payload['schema'], users=users_payload['data'], is_raw=True)
        
        log_msg = f"Se enviaron {len(user_identifiers)} usuarios a la audiencia personalizada {audience_id}. Respuesta: {response}"
        # Comprobar si la respuesta indica éxito (manejar formatos de respuesta potenciales)
        response_body = {}
        if hasattr(response, 'json'):
            response_body = response.json() # Forma estándar para muchas respuestas del SDK
        elif hasattr(response, '_content'):
            try:
                response_body = json.loads(response._content) # Menos estándar, pero a veces necesario
            except json.JSONDecodeError:
                current_app.logger.warning("No se pudo decodificar el contenido de la respuesta de la audiencia personalizada.")
        
        current_app.logger.info(f"{log_msg} | Cuerpo Analizado: {response_body}")
        
        # Comprobar respuesta para detalles de éxito/fracaso si es necesario
        # Formato de respuesta: {'audience_id': '...', 'num_received': ..., 'num_invalid_entries': ..., 'session_id': '...'}
        if response_body and response_body.get('num_received', 0) == len(user_identifiers) and response_body.get('num_invalid_entries', 0) == 0:
            current_app.logger.info(f"Todos los {len(user_identifiers)} usuarios aceptados por la audiencia {audience_id}.")
        else:
            received_count = response_body.get('num_received', 'N/A')
            invalid_count = response_body.get('num_invalid_entries', 'N/A')
            current_app.logger.warning(f"Posibles problemas al añadir usuarios a la audiencia {audience_id}. Recibidos: {received_count}, Inválidos: {invalid_count}")

        return audience_id # Devolver el ID incluso si la adición de usuarios tuvo problemas menores

    except FacebookRequestError as e:
        log_msg = f"Error al crear/actualizar la audiencia personalizada '{name}' para la cuenta {ad_account_id}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        # ¿Intentar eliminar el contenedor de audiencia si falló la adición de usuarios?
        # if 'audience_id' in locals():
        #    try: CustomAudience(audience_id).remote_delete() except: pass
        return None
    except ImportError as e:
        log_msg = f"Error al importar el objeto del SDK de Facebook: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None
    except Exception as e:
        # Capturar otros errores potenciales como serialización JSON
        log_msg = f"Ocurrió un error inesperado en create_meta_custom_audience: {e}"
        if current_app: current_app.logger.error(log_msg, exc_info=True)
        else: print(log_msg)
        return None

def upload_meta_image(ad_account_id: str, image_path: str) -> str | None:
    """Sube una imagen a la Biblioteca de Anuncios Meta y devuelve su hash."""
    api = initialize_meta_api()
    if not api or not os.path.exists(image_path):
        log_msg = f"No se puede subir la imagen: API no inicializada o ruta inválida: {image_path}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None

    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.adimage import AdImage

        account = AdAccount(ad_account_id)
        params = {
            AdImage.Field.filename: image_path,
        }
        image = account.create_ad_image(params=params)
        image_hash = image.get(AdImage.Field.hash)

        log_msg = f"Se subió correctamente la imagen {image_path}, hash: {image_hash}"
        if current_app: current_app.logger.info(log_msg)
        else: print(log_msg)
        return image_hash

    except FacebookRequestError as e:
        log_msg = f"Error al subir la imagen {image_path}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None
    except ImportError as e:
        log_msg = f"Error al importar el objeto del SDK de Facebook durante la subida de la imagen: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return None
    except Exception as e:
        log_msg = f"Error inesperado al subir la imagen {image_path}: {e}"
        if current_app: current_app.logger.error(log_msg, exc_info=True)
        else: print(log_msg)
        return None

# --- Funciones de Obtención de Insights ---

# --- Función de Prueba de Conexión ---

def test_meta_api_connection(ad_account_id: str, access_token: str) -> Tuple[bool, str]:
    """
    Prueba la conexión a la API de Meta usando credenciales específicas.
    Obtiene el nombre de la Cuenta Publicitaria como una prueba simple.

    Args:
        ad_account_id: El ID de la Cuenta Publicitaria (ej., 'act_123456789').
        access_token: El Token de Acceso Meta a usar para la prueba.

    Returns:
        Una tupla: (bool: éxito, str: mensaje/nombre_cuenta/error).
    """
    api = None # Asegurar que api esté definido
    try:
        # Inicializar API con token proporcionado (no depender de variables de entorno globales para la prueba)
        app_id = os.getenv('META_APP_ID')
        app_secret = os.getenv('META_APP_SECRET')
        if not app_id or not app_secret:
            return False, "META_APP_ID o META_APP_SECRET no configurados."
        
        api = FacebookAdsApi.init(app_id, app_secret, access_token, crash_log=False) # Deshabilitar registro de fallos para pruebas
        
        from facebook_business.adobjects.adaccount import AdAccount

        # Obtener solo el campo de nombre
        account = AdAccount(ad_account_id)
        account.api_get(fields=[AdAccount.Field.name]) # Hacer la llamada a la API

        account_name = account.get(AdAccount.Field.name, "Nombre Desconocido")
        msg = f"¡Conexión exitosa! Nombre de la Cuenta: {account_name}"
        if current_app: current_app.logger.info(msg)
        else: print(msg)
        return True, msg

    except FacebookRequestError as e:
        # Manejar códigos de error específicos si es necesario
        error_message = f"Fallo de Conexión API: {e}"
        if e.api_error_code() == 190: # Error común para token inválido/permisos
            error_message = "Fallo de Conexión API: Token de acceso inválido o permisos insuficientes."
        elif e.api_error_code() == 100: # Error común para ID de cuenta inválido
             error_message = f"Fallo de Conexión API: ID de Cuenta Publicitaria '{ad_account_id}' no encontrado o inaccesible."
        
        log_msg = f"Fallo la prueba de conexión API de Meta para la cuenta {ad_account_id}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return False, error_message
    except ImportError as e:
        log_msg = f"Fallo la prueba de conexión API de Meta debido a error de importación: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return False, "Error de Importación del SDK de API."
    except Exception as e:
        # Capturar cualquier otro error inesperado
        log_msg = f"Error inesperado durante la prueba de conexión API de Meta para la cuenta {ad_account_id}: {e}"
        if current_app: current_app.logger.error(log_msg)
        else: print(log_msg)
        return False, f"Error Inesperado: {e}"
    finally:
        # Limpiar instancia de API si se creó
        if api:
             FacebookAdsApi.set_default_api(None) # Limpiar la API por defecto temporal

# --- Fin Prueba de Conexión ---

# --- Funciones API Google Gemini ---

def get_available_gemini_models(api_key: str) -> Tuple[bool, str, list]:
    """Obtiene la lista de modelos Gemini disponibles."""
    if not api_key:
        return False, "Falta la Clave API de Gemini.", []

    try:
        genai.configure(api_key=api_key)
        models = list(genai.list_models())
        
        # Filtrar por modelos que soportan generación de contenido
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                model_info = {
                    'name': model.name,
                    'display_name': model.name.split('/')[-1],  # Extraer nombre amigable
                    'description': getattr(model, 'description', ''),
                    'input_image': False  # Por defecto False
                }
                
                # Comprobar si el modelo soporta entrada de imagen mirando los métodos soportados
                if hasattr(model, 'supported_generation_methods'):
                    model_info['input_image'] = 'countImageTokens' in model.supported_generation_methods
                
                available_models.append(model_info)

        if available_models:
            current_app.logger.info(f"Se encontraron {len(available_models)} modelos Gemini disponibles")
            return True, "Se recuperaron correctamente los modelos Gemini.", available_models
        else:
            current_app.logger.warning("No se encontraron modelos Gemini adecuados")
            return False, "No se encontraron modelos Gemini adecuados.", []

    except Exception as e:
        current_app.logger.error(f"Error al listar modelos Gemini: {e}", exc_info=True)
        return False, f"Error al listar modelos Gemini: {str(e)}", []

def test_gemini_api_connection(api_key: str) -> Tuple[bool, str]:
    """Prueba la conexión a la API Google Gemini usando la clave proporcionada."""
    success, message, models = get_available_gemini_models(api_key)
    if success:
        current_app.logger.info("Conexión API Gemini exitosa (modelos encontrados).")
        return True, f"Conexión API Gemini exitosa. Se encontraron {len(models)} modelos disponibles."
    else:
        current_app.logger.error(f"Fallo la conexión API Gemini: {message}")
        return False, f"Fallo la conexión API Gemini: {message}"

def generate_ad_creative_gemini(job_title: str, job_description: str, target_audience: str = "general job seekers") -> Tuple[bool, str, dict]:
    """Genera texto creativo para anuncios usando Gemini basado en detalles del trabajo.
    
    Args:
        job_title: El título del puesto de trabajo
        job_description: La descripción completa del trabajo
        target_audience: Audiencia objetivo para el anuncio (por defecto: "buscadores de empleo generales")
        
    Returns:
        Tupla conteniendo:
        - bool: Estado de éxito
        - str: Mensaje de error si falló, mensaje de éxito si tuvo éxito
        - dict: Contenido generado con claves:
            - primary_text: Texto principal del anuncio
            - headline: Titular corto y llamativo
            - link_description: Breve descripción para la vista previa del enlace
    """
    try:
        # Obtener clave API y modelo de variables de entorno
        api_key = os.getenv('GEMINI_API_KEY')
        model_name = os.getenv('GEMINI_MODEL')
        
        if not api_key:
            return False, "Clave API de Gemini no configurada", {}
        if not model_name:
            return False, "Modelo Gemini no seleccionado", {}

        # Configurar la API de Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        # Construir el prompt
        prompt = f"""Eres un redactor experto especializado en anuncios de reclutamiento de empleo. Crea un texto publicitario convincente para el siguiente trabajo:

Puesto de Trabajo: {job_title}
Descripción del Trabajo: {job_description}
Audiencia Objetivo: {target_audience}

Por favor, genera tres piezas de texto publicitario:
1. Texto Principal (150-200 caracteres): Texto principal atractivo que resalte los beneficios clave del trabajo y anime a las solicitudes
2. Titular (25-40 caracteres): Titular conciso y llamativo
3. Descripción del Enlace (30-50 caracteres): Descripción breve y convincente

Formatea tu respuesta como JSON con estas claves exactas:
- primary_text
- headline
- link_description

Mantén un tono profesional pero atractivo. Enfócate en lo que hace que este puesto sea único y atractivo para la audiencia objetivo."""

        # Generar contenido
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return False, "No se generó contenido", {}

        try:
            # Analizar la respuesta JSON
            import json
            content = json.loads(response.text)
            
            # Validar claves requeridas
            required_keys = ['primary_text', 'headline', 'link_description']
            if not all(key in content for key in required_keys):
                return False, "Contenido generado falta campos requeridos", {}
                
            return True, "Se generó correctamente el texto creativo del anuncio", content

        except json.JSONDecodeError:
            # Si falla el análisis JSON, intentar extraer contenido usando regex
            import re
            
            # Extraer contenido entre comillas después de cada clave
            content = {}
            patterns = {
                'primary_text': r'primary_text"?\s*:?\s*"([^"]+)"',
                'headline': r'headline"?\s*:?\s*"([^"]+)"',
                'link_description': r'link_description"?\s*:?\s*"([^"]+)"'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, response.text)
                if match:
                    content[key] = match.group(1)
                else:
                    content[key] = ""  # Proporcionar string vacío si no se encuentra
            
            if any(content.values()):  # Si encontramos al menos algo de contenido
                return True, "Se generó correctamente el texto creativo del anuncio (necesitó análisis regex)", content
            else:
                return False, "Failed to parse generated content", {}

    except Exception as e:
        current_app.logger.error(f"Error al generar texto creativo del anuncio: {e}", exc_info=True)
        return False, f"Error al generar texto creativo del anuncio: {str(e)}", {}

# --- Cliente API Google Ads --- #

def get_google_ads_client():
    """Inicializa y devuelve un cliente API de Google Ads usando credenciales 
       de variables de entorno (vía config de Flask)."""
    
    # Construir el diccionario de configuración esperado por el cliente de Google Ads
    # desde la config de la app Flask que cargó las variables .env
    try:
        googleads_config = {
            "developer_token": current_app.config['GOOGLE_ADS_DEVELOPER_TOKEN'],
            "client_id": current_app.config['GOOGLE_ADS_CLIENT_ID'],
            "client_secret": current_app.config['GOOGLE_ADS_CLIENT_SECRET'],
            "refresh_token": current_app.config['GOOGLE_ADS_REFRESH_TOKEN'],
            "login_customer_id": current_app.config['GOOGLE_ADS_LOGIN_CUSTOMER_ID'],
            "use_proto_plus": current_app.config.get('GOOGLE_ADS_USE_PROTO_PLUS', True) # Por defecto True
        }
        
        # --- LÍNEA DE DEPURACIÓN --- 
        current_app.logger.info(f"Intentando inicializar cliente Google Ads con Login Customer ID: {googleads_config.get('login_customer_id')}")
        # -----------------------

        # Comprobar si todas las claves requeridas están presentes y no son None/vacías
        required_keys = ["developer_token", "client_id", "client_secret", "refresh_token", "login_customer_id"]
        if not all(googleads_config.get(key) for key in required_keys):
            current_app.logger.error("Missing one or more required Google Ads API credentials in configuration.")
            return None
            
        # Convertir dict a string YAML (alternativa a cargar desde archivo)
        # googleads_yaml = yaml.dump(googleads_config)
        # client = GoogleAdsClient.load_from_string(googleads_yaml)
        
        # Cargar directamente desde el diccionario
        client = GoogleAdsClient.load_from_dict(googleads_config)
        current_app.logger.info("Google Ads API client initialized successfully.")
        return client
        
    except KeyError as e:
        current_app.logger.error(f"Missing Google Ads configuration key: {e}")
        return None
    except GoogleAdsException as ex:
        current_app.logger.error(
            f'Request with ID "{ex.request_id}" failed with status "{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            current_app.logger.error(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    current_app.logger.error(f"\t\tOn field: {field_path_element.field_name}")
        return None
    except Exception as e: # Catch other potential errors
        current_app.logger.error(f"An unexpected error occurred initializing Google Ads client: {e}")
        return None

def publish_google_campaign_api(adflux_campaign_id: int, campaign_data: dict) -> dict:
    """Publica una campaña en Google Ads.

    Args:
        adflux_campaign_id: El ID de la campaña AdFlux.
        campaign_data: Diccionario que contiene detalles del modelo de campaña AdFlux.
                       Claves esperadas: 'name', 'daily_budget' (en centavos),
                       'primary_text', 'headline', 'job_id'.

    Returns:
        Un diccionario que contiene el resultado, incluyendo IDs externos.
        Ejemplo: {'success': True, 'message': '...', 'external_ids': {'campaign_id': '...', 'ad_group_id': '...', 'ad_id': '...'}}
    """
    client = get_google_ads_client()
    if not client:
        return {'success': False, 'message': 'Fallo al inicializar el cliente de Google Ads.', 'external_ids': None}
        
    # login_customer_id es el ID del ADMINISTRADOR usado para la cabecera de autenticación
    # target_customer_id es el ID de la cuenta CLIENTE que queremos modificar
    try:
        target_customer_id = current_app.config['GOOGLE_ADS_TARGET_CUSTOMER_ID']
        if not target_customer_id:
            raise KeyError("GOOGLE_ADS_TARGET_CUSTOMER_ID no configurado.")
    except KeyError:
         logger.error("Error de configuración: GOOGLE_ADS_TARGET_CUSTOMER_ID debe configurarse.")
         return {'success': False, 'message': 'Error de configuración del servidor: Falta ID de cliente objetivo.', 'external_ids': None}
         
    logger = current_app.logger
    logger.info(f"Iniciando publicación REAL en Google Ads para la campaña AdFlux ID: {adflux_campaign_id} en el Cliente Objetivo ID: {target_customer_id}")
    logger.info(f"Datos de la Campaña: {campaign_data}")

    # Preparar dict de resultados
    results = {
        'success': False, 
        'message': '', 
        'external_ids': {}
    }

    try:
        # --- Paso 1: Creando Presupuesto de Campaña --- 
        logger.info("Paso 1: Creando Presupuesto de Campaña...")
        campaign_budget_service = client.get_service("CampaignBudgetService")
        budget_operation = client.get_type("CampaignBudgetOperation")
        budget = budget_operation.create
        
        budget.name = f"Presupuesto para AdFlux {adflux_campaign_id} - {uuid.uuid4()}" # Asegurar nombre único
        # La cantidad está en micros (moneda * 1,000,000). El presupuesto de AdFlux está en centavos.
        # Convertir centavos a micros: centavos * 10,000
        daily_budget_micros = (campaign_data.get('daily_budget', 500) or 500) * 10000 # Por defecto $5.00
        budget.amount_micros = daily_budget_micros
        budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        # Indicar explícitamente que no es compartido, si aplica por versión de API
        # budget.explicitly_shared = False # Comprobar si es necesario/válido

        response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=target_customer_id, operations=[budget_operation]
        )
        # --- Registrar la respuesta cruda para depuración --- 
        logger.info(f"Respuesta cruda MutateCampaignBudgetsResponse: {response}")
        # --------------------------------------------
        budget_resource_name = response.results[0].resource_name
        logger.info(f"Nombre de Recurso de Presupuesto Extraído: {budget_resource_name}") # Registrar nombre antes de analizar
        results['external_ids']['budget_id'] = campaign_budget_service.parse_campaign_budget_path(budget_resource_name)["campaign_budget_id"]
        logger.info(f"Se creó correctamente el Presupuesto de Campaña: {budget_resource_name}")

        # --- Paso 2: Crear Campaña --- 
        logger.info("Paso 2: Creando Campaña...")
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        
        campaign.name = f"AdFlux {adflux_campaign_id}: {campaign_data.get('name', 'Campaña sin título')} - {uuid.uuid4()}"
        campaign.status = client.enums.CampaignStatusEnum.PAUSED # Empezar pausado
        campaign.campaign_budget = budget_resource_name # Enlazar al presupuesto creado arriba

        # --- Establecer Estrategia de Puja (Intento 18 - Probar objeto ManualCpc de nuevo) ---
        # Eliminar adjuntar estrategia de portafolio
        # portfolio_strategy_resource_name = "customers/1631306843/biddingStrategies/11508937879"
        # campaign.bidding_strategy = portfolio_strategy_resource_name
        # Probar creando el objeto de estrategia específico usando client.get_type
        campaign.manual_cpc = client.get_type("ManualCpc")

        # Establecer Tipo de Canal Publicitario (Búsqueda)
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH

        # Configuración de Red (Solo Red de Búsqueda, deshabilitar socios inicialmente)
        # Acceder a enums vía instancia de cliente que debería ser consciente de la versión
        campaign.network_settings.target_google_search = True
        campaign.network_settings.target_search_network = False
        campaign.network_settings.target_content_network = False
        campaign.network_settings.target_partner_search_network = False

        # Segmentación Geográfica (Opcional - Ejemplo: USA)
        # geo_target_constant_service = client.get_service("GeoTargetConstantService")
        # gt_criterion = client.get_type("CriterionInfo")
        # gt_criterion.location.geo_target_constant = geo_target_constant_service.geo_target_constant_path(2840) # 2840 = USA
        # campaign.geo_targeting_type = client.enums.GeoTargetingTypeEnum.LOCATION_OF_PRESENCE

        # Segmentación por Idioma (Opcional - Ejemplo: Inglés)
        # language_constant_service = client.get_service("LanguageConstantService")
        # lang_criterion = client.get_type("CriterionInfo")
        # lang_criterion.language.language_constant = language_constant_service.language_constant_path(1000) # 1000 = Inglés
        # campaign.language_targeting.language_constants.append(lang_criterion)

        response = campaign_service.mutate_campaigns(
            customer_id=target_customer_id, operations=[campaign_operation]
        )
        campaign_resource_name = response.results[0].resource_name
        results['external_ids']['campaign_id'] = campaign_service.parse_campaign_path(campaign_resource_name)["campaign_id"]
        logger.info(f"Se creó correctamente la Campaña: {campaign_resource_name}")

        # --- Paso 3: Crear Grupo de Anuncios --- 
        logger.info("Paso 3: Creando Grupo de Anuncios...")
        ad_group_service = client.get_service("AdGroupService")
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.create
        
        ad_group.name = f"Grupo de Anuncios AdFlux para Campaña {results['external_ids']['campaign_id']}"
        ad_group.campaign = campaign_resource_name # Enlazar a campaña
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED # Habilitar grupo de anuncios por defecto
        # Opcional: Establecer pujas a nivel de Grupo de Anuncios si no se usa estrategia a nivel de campaña o se necesitan anulaciones
        # ad_group.cpc_bid_micros = 1000000 # Ejemplo puja CPC $1.00
        
        response = ad_group_service.mutate_ad_groups(
            customer_id=target_customer_id, operations=[ad_group_operation]
        )
        ad_group_resource_name = response.results[0].resource_name
        results['external_ids']['ad_group_id'] = ad_group_service.parse_ad_group_path(ad_group_resource_name)["ad_group_id"]
        logger.info(f"Se creó correctamente el Grupo de Anuncios: {ad_group_resource_name}")

        # --- Paso 4: Crear Anuncio de Grupo de Anuncios (Anuncio de Búsqueda Responsivo) ---
        logger.info("Paso 4: Creando Anuncio de Búsqueda Responsivo...")
        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_group_ad_operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = ad_group_ad_operation.create
        ad_group_ad.ad_group = ad_group_resource_name # Enlazar a grupo de anuncios
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED # Habilitar anuncio

        # Crear la información del anuncio de búsqueda responsivo
        ad_info = ad_group_ad.ad
        ad_info.name = f"Anuncio AdFlux para Campaña {results['external_ids']['campaign_id']}"
        # TODO: Hacer URL final dinámica - usar enlace de trabajo o página de destino por defecto
        ad_info.final_urls.append("https://www.magneto365.com/") # URL de marcador de posición

        rsa_info = ad_info.responsive_search_ad
        # Titulares (Usar datos de campaign_data, proporcionar valores por defecto)
        headline_texts = [campaign_data.get('headline', 'Aplica Ahora'), 
                         campaign_data.get('job_title', 'Oportunidad Emocionante'), # Asumiendo que job_title está disponible
                         'Salario Competitivo Ofrecido'] # Añadir al menos 3
        max_headline_len = 30 # Google Ads headline limit
        for text in headline_texts[:15]: # Máx 15 titulares
            headline = client.get_type("AdTextAsset")
            # Truncate headline if it exceeds the limit
            original_len = len(text)
            if original_len > max_headline_len:
                logger.warning(f"Truncando texto de titular de {original_len} a {max_headline_len} caracteres.")
                text = text[:max_headline_len]
            headline.text = text
            rsa_info.headlines.append(headline)

        # Descripciones (Usar datos de campaign_data, proporcionar valores por defecto)
        description_texts = [campaign_data.get('primary_text', 'Haz clic aquí para saber más y aplicar al trabajo.'),
                             campaign_data.get('link_description', '¡Únete a nuestro creciente equipo hoy!')] # Añadir al menos 2
        max_desc_len = 90
        for text in description_texts[:4]: # Máx 4 descripciones
            # Truncar si es necesario
            original_len = len(text)
            if original_len > max_desc_len:
                logger.warning(f"Truncando texto de descripción de {original_len} a {max_desc_len} caracteres.")
                text = text[:max_desc_len]
                
            logger.info(f"Usando texto de descripción (longitud {len(text)}): \"{text}\"")
            description = client.get_type("AdTextAsset")
            description.text = text
            rsa_info.descriptions.append(description)
            
        # Ruta (Ruta de URL de visualización opcional)
        # rsa_info.path1 = "trabajos"
        # rsa_info.path2 = "aplicar"
        
        response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=target_customer_id, operations=[ad_group_ad_operation]
        )
        ad_group_ad_resource_name = response.results[0].resource_name
        results['external_ids']['ad_id'] = ad_group_ad_service.parse_ad_group_ad_path(ad_group_ad_resource_name)["ad_id"]
        logger.info(f"Se creó correctamente el Anuncio de Grupo de Anuncios: {ad_group_ad_resource_name}")

        # --- Actualizar mensaje final de éxito ---
        results['success'] = True
        results['message'] = f"Campaña, Grupo de Anuncios y Anuncio de Google Ads creados correctamente. ID de Campaña: {results['external_ids'].get('campaign_id', 'N/A')}"

    except GoogleAdsException as ex:
        logger.error(
            f'Fallo la solicitud API de Google Ads para la Campaña {adflux_campaign_id}. ID de Solicitud: "{ex.request_id}". Estado: "{ex.error.code().name}". Errores:'
        )
        error_messages = []
        for error in ex.failure.errors:
            logger.error(f'\tMensaje de error: "{error.message}".')
            error_messages.append(error.message)
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    logger.error(f"\t\tEn campo: {field_path_element.field_name}")
        results['message'] = f"Error API Google Ads: { '; '.join(error_messages)}"
        results['success'] = False
        # Nota: Pudo haber ocurrido creación parcial. Idealmente se necesita lógica de limpieza.
        
    except Exception as e:
        logger.error(f"Error inesperado durante la publicación en Google para la campaña {adflux_campaign_id}: {e}")
        logger.error(traceback.format_exc())
        results['message'] = f"Error inesperado: {e}"
        results['success'] = False

    # Devolver los resultados recopilados
    return results

# --- Cliente Gemini --- #
