"""
Ejemplo de uso de la capa de abstracción para APIs externas.

Este módulo muestra cómo utilizar la capa de abstracción para APIs externas.
"""

import os
from datetime import datetime, timedelta

from .abstract.api_factory import AdAPIFactory
from .abstract.ad_api import AdCampaign, AdSet, Ad, AdCreative, AdInsight
from .adapters.register import register_adapters


def create_meta_api():
    """
    Crea una instancia de la API de Meta Ads.
    
    Returns:
        Instancia de la API de Meta Ads
    """
    # Obtener credenciales de variables de entorno
    app_id = os.environ.get('META_APP_ID')
    app_secret = os.environ.get('META_APP_SECRET')
    access_token = os.environ.get('META_ACCESS_TOKEN')
    ad_account_id = os.environ.get('META_AD_ACCOUNT_ID')
    
    # Crear instancia de la API
    config = {
        'app_id': app_id,
        'app_secret': app_secret,
        'access_token': access_token,
        'ad_account_id': ad_account_id,
    }
    
    return AdAPIFactory.create('meta', config)


def create_google_api():
    """
    Crea una instancia de la API de Google Ads.
    
    Returns:
        Instancia de la API de Google Ads
    """
    # Obtener credenciales de variables de entorno
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
    developer_token = os.environ.get('GOOGLE_DEVELOPER_TOKEN')
    customer_id = os.environ.get('GOOGLE_CUSTOMER_ID')
    
    # Crear instancia de la API
    config = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'developer_token': developer_token,
        'customer_id': customer_id,
    }
    
    return AdAPIFactory.create('google', config)


def create_campaign_on_all_platforms(name, objective, daily_budget):
    """
    Crea una campaña en todas las plataformas soportadas.
    
    Args:
        name: Nombre de la campaña
        objective: Objetivo de la campaña
        daily_budget: Presupuesto diario
        
    Returns:
        Diccionario con las campañas creadas en cada plataforma
    """
    # Obtener plataformas soportadas
    platforms = AdAPIFactory.get_supported_platforms()
    
    # Crear campañas en cada plataforma
    campaigns = {}
    for platform in platforms:
        try:
            # Crear instancia de la API
            if platform == 'meta':
                api = create_meta_api()
            elif platform == 'google':
                api = create_google_api()
            else:
                continue
            
            # Crear campaña
            campaign = api.create_campaign(
                name=f"{name} - {platform.title()}",
                objective=objective,
                status='PAUSED',
                daily_budget=daily_budget,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=30)
            )
            
            campaigns[platform] = campaign
            
        except Exception as e:
            print(f"Error al crear campaña en {platform}: {str(e)}")
    
    return campaigns


def get_insights_from_all_platforms(campaign_ids, start_date, end_date):
    """
    Obtiene insights de todas las plataformas soportadas.
    
    Args:
        campaign_ids: Diccionario con IDs de campañas por plataforma
        start_date: Fecha de inicio
        end_date: Fecha de fin
        
    Returns:
        Diccionario con insights por plataforma
    """
    # Obtener plataformas soportadas
    platforms = AdAPIFactory.get_supported_platforms()
    
    # Obtener insights de cada plataforma
    insights = {}
    for platform in platforms:
        try:
            # Crear instancia de la API
            if platform == 'meta':
                api = create_meta_api()
            elif platform == 'google':
                api = create_google_api()
            else:
                continue
            
            # Verificar si hay campañas para esta plataforma
            if platform not in campaign_ids:
                continue
            
            # Obtener insights
            platform_insights = api.get_insights(
                object_ids=[campaign_ids[platform]],
                level='campaign',
                fields=['impressions', 'clicks', 'spend', 'reach', 'ctr', 'cpc'],
                time_range={
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                limit=100
            )
            
            insights[platform] = platform_insights
            
        except Exception as e:
            print(f"Error al obtener insights en {platform}: {str(e)}")
    
    return insights


def main():
    """Función principal para demostrar el uso de la capa de abstracción."""
    # Asegurarse de que los adaptadores estén registrados
    register_adapters()
    
    # Mostrar plataformas soportadas
    platforms = AdAPIFactory.get_supported_platforms()
    print(f"Plataformas soportadas: {', '.join(platforms)}")
    
    # Crear una campaña en Meta Ads
    try:
        meta_api = create_meta_api()
        campaign = meta_api.create_campaign(
            name="Campaña de prueba",
            objective="LINK_CLICKS",
            status="PAUSED",
            daily_budget=10.0
        )
        print(f"Campaña creada en Meta Ads: {campaign.id} - {campaign.name}")
    except Exception as e:
        print(f"Error al crear campaña en Meta Ads: {str(e)}")
    
    # Obtener campañas de Meta Ads
    try:
        meta_api = create_meta_api()
        campaigns = meta_api.get_campaigns(limit=5)
        print(f"Campañas en Meta Ads ({len(campaigns)}):")
        for campaign in campaigns:
            print(f"  - {campaign.id}: {campaign.name} ({campaign.status})")
    except Exception as e:
        print(f"Error al obtener campañas de Meta Ads: {str(e)}")


if __name__ == "__main__":
    main()
