"""
Pruebas funcionales para el flujo de campañas en AdFlux.

Este módulo contiene pruebas para verificar el flujo completo de creación,
publicación y seguimiento de campañas publicitarias en AdFlux.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from adflux.models import db, Campaign, MetaCampaign, MetaAdSet, MetaAd, MetaInsight
from adflux.services.campaign_service import (
    create_campaign, get_campaign, update_campaign, delete_campaign,
    publish_campaign, pause_campaign, resume_campaign
)
from adflux.services.metrics_service import get_campaign_metrics, get_platform_metrics


@pytest.mark.functional
class TestCampaignFlow:
    """Pruebas para el flujo completo de campañas."""
    
    @patch('adflux.services.campaign_service.create_meta_campaign')
    def test_campaign_creation_flow(self, mock_create_meta_campaign, db, admin_user):
        """Prueba el flujo de creación de una campaña."""
        # Configurar mock
        mock_create_meta_campaign.return_value = {'id': '123456789'}
        
        # Crear campaña
        campaign_data = {
            'name': 'Test Campaign Flow',
            'objective': 'AWARENESS',
            'platform': 'META',
            'status': 'DRAFT',
            'daily_budget': 100.0,
            'start_date': datetime.utcnow().strftime('%Y-%m-%d'),
            'end_date': (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'targeting': {
                'age_min': 18,
                'age_max': 65,
                'genders': [1, 2],
                'locations': [{'id': '2421', 'name': 'New York, United States'}]
            },
            'ad_creative': {
                'headline': 'Join Our Team Today!',
                'description': 'We\'re looking for talented individuals to join our growing company.',
                'image_url': 'https://example.com/image.jpg',
                'call_to_action': 'APPLY_NOW',
                'website_url': 'https://example.com/careers'
            }
        }
        
        campaign = create_campaign(campaign_data, admin_user.id)
        
        # Verificar que la campaña se creó correctamente
        assert campaign.id is not None
        assert campaign.name == 'Test Campaign Flow'
        assert campaign.objective == 'AWARENESS'
        assert campaign.platform == 'META'
        assert campaign.status == 'DRAFT'
        assert campaign.daily_budget == 100.0
        assert campaign.created_by == admin_user.id
        
        # Verificar que se guardó en la base de datos
        saved_campaign = Campaign.query.filter_by(name='Test Campaign Flow').first()
        assert saved_campaign is not None
        assert saved_campaign.id == campaign.id
        
        # Verificar que no se llamó a la API de Meta (porque está en borrador)
        mock_create_meta_campaign.assert_not_called()
    
    @patch('adflux.services.campaign_service.create_meta_campaign')
    @patch('adflux.services.campaign_service.create_meta_ad_set')
    @patch('adflux.services.campaign_service.create_meta_ad')
    def test_campaign_publish_flow(self, mock_create_meta_ad, mock_create_meta_ad_set, 
                                 mock_create_meta_campaign, db, admin_user):
        """Prueba el flujo de publicación de una campaña."""
        # Configurar mocks
        mock_create_meta_campaign.return_value = {'id': '123456789'}
        mock_create_meta_ad_set.return_value = {'id': '987654321'}
        mock_create_meta_ad.return_value = {'id': '555555555'}
        
        # Crear campaña en estado borrador
        campaign_data = {
            'name': 'Test Publish Flow',
            'objective': 'AWARENESS',
            'platform': 'META',
            'status': 'DRAFT',
            'daily_budget': 100.0,
            'start_date': datetime.utcnow().strftime('%Y-%m-%d'),
            'end_date': (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'targeting': {
                'age_min': 18,
                'age_max': 65,
                'genders': [1, 2],
                'locations': [{'id': '2421', 'name': 'New York, United States'}]
            },
            'ad_creative': {
                'headline': 'Join Our Team Today!',
                'description': 'We\'re looking for talented individuals to join our growing company.',
                'image_url': 'https://example.com/image.jpg',
                'call_to_action': 'APPLY_NOW',
                'website_url': 'https://example.com/careers'
            }
        }
        
        campaign = create_campaign(campaign_data, admin_user.id)
        
        # Publicar campaña
        published_campaign = publish_campaign(campaign.id, admin_user.id)
        
        # Verificar que la campaña se publicó correctamente
        assert published_campaign.status == 'ACTIVE'
        
        # Verificar que se llamó a las APIs de Meta
        mock_create_meta_campaign.assert_called_once()
        mock_create_meta_ad_set.assert_called_once()
        mock_create_meta_ad.assert_called_once()
        
        # Verificar que se crearon los registros en la base de datos
        meta_campaign = MetaCampaign.query.filter_by(campaign_id=campaign.id).first()
        assert meta_campaign is not None
        assert meta_campaign.external_id == '123456789'
        assert meta_campaign.status == 'ACTIVE'
        
        meta_ad_set = MetaAdSet.query.filter_by(meta_campaign_id=meta_campaign.id).first()
        assert meta_ad_set is not None
        assert meta_ad_set.external_id == '987654321'
        
        meta_ad = MetaAd.query.filter_by(meta_ad_set_id=meta_ad_set.id).first()
        assert meta_ad is not None
        assert meta_ad.external_id == '555555555'
    
    @patch('adflux.services.campaign_service.update_meta_campaign')
    def test_campaign_update_flow(self, mock_update_meta_campaign, db, admin_user, sample_campaign):
        """Prueba el flujo de actualización de una campaña."""
        # Configurar mock
        mock_update_meta_campaign.return_value = {'success': True}
        
        # Actualizar campaña
        updated_data = {
            'name': 'Updated Campaign Name',
            'daily_budget': 200.0
        }
        
        updated_campaign = update_campaign(sample_campaign.id, updated_data, admin_user.id)
        
        # Verificar que la campaña se actualizó correctamente
        assert updated_campaign.name == 'Updated Campaign Name'
        assert updated_campaign.daily_budget == 200.0
        
        # Verificar que se guardó en la base de datos
        saved_campaign = Campaign.query.get(sample_campaign.id)
        assert saved_campaign.name == 'Updated Campaign Name'
        assert saved_campaign.daily_budget == 200.0
        
        # Verificar que se llamó a la API de Meta
        mock_update_meta_campaign.assert_called_once()
    
    @patch('adflux.services.campaign_service.pause_meta_campaign')
    def test_campaign_pause_flow(self, mock_pause_meta_campaign, db, admin_user, sample_campaign):
        """Prueba el flujo de pausa de una campaña."""
        # Configurar mock
        mock_pause_meta_campaign.return_value = {'success': True}
        
        # Pausar campaña
        paused_campaign = pause_campaign(sample_campaign.id, admin_user.id)
        
        # Verificar que la campaña se pausó correctamente
        assert paused_campaign.status == 'PAUSED'
        
        # Verificar que se guardó en la base de datos
        saved_campaign = Campaign.query.get(sample_campaign.id)
        assert saved_campaign.status == 'PAUSED'
        
        # Verificar que se llamó a la API de Meta
        mock_pause_meta_campaign.assert_called_once()
    
    @patch('adflux.services.campaign_service.resume_meta_campaign')
    def test_campaign_resume_flow(self, mock_resume_meta_campaign, db, admin_user, sample_campaign):
        """Prueba el flujo de reanudación de una campaña."""
        # Configurar campaña pausada
        sample_campaign.status = 'PAUSED'
        db.session.commit()
        
        # Configurar mock
        mock_resume_meta_campaign.return_value = {'success': True}
        
        # Reanudar campaña
        resumed_campaign = resume_campaign(sample_campaign.id, admin_user.id)
        
        # Verificar que la campaña se reanudó correctamente
        assert resumed_campaign.status == 'ACTIVE'
        
        # Verificar que se guardó en la base de datos
        saved_campaign = Campaign.query.get(sample_campaign.id)
        assert saved_campaign.status == 'ACTIVE'
        
        # Verificar que se llamó a la API de Meta
        mock_resume_meta_campaign.assert_called_once()
    
    @patch('adflux.services.campaign_service.delete_meta_campaign')
    def test_campaign_delete_flow(self, mock_delete_meta_campaign, db, admin_user, sample_campaign):
        """Prueba el flujo de eliminación de una campaña."""
        # Configurar mock
        mock_delete_meta_campaign.return_value = {'success': True}
        
        # Eliminar campaña
        result = delete_campaign(sample_campaign.id, admin_user.id)
        
        # Verificar que la campaña se eliminó correctamente
        assert result is True
        
        # Verificar que se eliminó de la base de datos
        deleted_campaign = Campaign.query.get(sample_campaign.id)
        assert deleted_campaign is None
        
        # Verificar que se llamó a la API de Meta
        mock_delete_meta_campaign.assert_called_once()
    
    @patch('adflux.services.metrics_service.get_meta_campaign_insights')
    def test_campaign_metrics_flow(self, mock_get_meta_insights, db, admin_user, sample_campaign):
        """Prueba el flujo de obtención de métricas de una campaña."""
        # Configurar mock
        mock_get_meta_insights.return_value = {
            'data': [
                {
                    'date_start': '2023-01-01',
                    'date_stop': '2023-01-07',
                    'impressions': '1000',
                    'clicks': '50',
                    'spend': '100.00',
                    'reach': '800',
                    'cpm': '100.00',
                    'ctr': '5.00'
                }
            ]
        }
        
        # Crear insight en la base de datos
        insight = MetaInsight(
            meta_campaign_id=sample_campaign.meta_campaign.id,
            date_start='2023-01-01',
            date_stop='2023-01-07',
            impressions=1000,
            clicks=50,
            spend=100.00,
            reach=800,
            cpm=100.00,
            ctr=5.00
        )
        db.session.add(insight)
        db.session.commit()
        
        # Obtener métricas
        metrics = get_campaign_metrics(
            campaign_id=sample_campaign.id,
            start_date='2023-01-01',
            end_date='2023-01-07'
        )
        
        # Verificar métricas
        assert metrics['impressions'] == 1000
        assert metrics['clicks'] == 50
        assert metrics['spend'] == 100.00
        assert metrics['reach'] == 800
        assert metrics['cpm'] == 100.00
        assert metrics['ctr'] == 5.00
        
        # Verificar que no se llamó a la API de Meta (porque ya hay datos en la base de datos)
        mock_get_meta_insights.assert_not_called()
        
        # Obtener métricas para un período diferente (debería llamar a la API)
        metrics = get_campaign_metrics(
            campaign_id=sample_campaign.id,
            start_date='2023-01-08',
            end_date='2023-01-14',
            force_refresh=True
        )
        
        # Verificar que se llamó a la API de Meta
        mock_get_meta_insights.assert_called_once()
