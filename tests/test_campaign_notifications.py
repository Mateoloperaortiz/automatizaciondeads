"""
Tests for campaign notifications integration.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models.ad_campaign import AdCampaign, SocialMediaPlatform
from app.models.job_opening import JobOpening
from app.models.notification import Notification, NotificationType, NotificationCategory
from app.api_framework.campaign_manager import APIFrameworkCampaignManager
from app.services.notification_service import NotificationService


class TestCampaignNotifications(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test data
        self.platform = SocialMediaPlatform(name='meta', active=True)
        db.session.add(self.platform)
        
        self.job = JobOpening(
            title="Test Job",
            description="Test description",
            company="Test Company",
            location="Test Location",
            active=True
        )
        db.session.add(self.job)
        
        self.campaign = AdCampaign(
            title="Test Campaign",
            platform_id=1,
            job_opening_id=1,
            status='draft'
        )
        db.session.add(self.campaign)
        db.session.commit()
    
    def tearDown(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    @patch('app.api_framework.campaign_manager.APIFrameworkCampaignManager.update_campaign_status')
    def test_campaign_status_change_creates_notification(self, mock_update):
        """Test that changing campaign status creates a notification."""
        # Configure mock to return success
        mock_update.return_value = {
            'success': True,
            'campaign_id': 1,
            'status': 'ACTIVE',
            'platform': 'meta'
        }
        
        # Create a modified campaign status
        with self.app.test_client() as client:
            response = client.put('/campaigns/api/campaigns/1', json={
                'status': 'active'
            })
            data = response.get_json()
            
            # Check response
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            
            # Check notification
            notification = Notification.query.first()
            self.assertIsNotNone(notification)
            self.assertEqual(notification.title, "Campaign Activated")
            self.assertEqual(notification.type, NotificationType.SUCCESS.value)
            self.assertEqual(notification.category, NotificationCategory.CAMPAIGN.value)
    
    @patch('app.api_framework.meta_client.MetaAPIClient.execute_request')
    @patch('app.api_framework.meta_client.MetaAPIClient.create_status_update_request')
    def test_api_framework_campaign_status_change_creates_notification(self, mock_create_request, mock_execute):
        """Test that API framework campaign status update creates a notification."""
        # Configure mocks
        mock_request = MagicMock()
        mock_create_request.return_value = mock_request
        
        mock_response = MagicMock()
        mock_response.success = True
        mock_execute.return_value = mock_response
        
        # Create campaign manager
        manager = APIFrameworkCampaignManager()
        
        # Override platform client's execute_request method
        platform_client_mock = MagicMock()
        platform_client_mock.execute_request.return_value = mock_response
        manager.platform_clients = {'meta': platform_client_mock}
        
        # Update campaign status
        result = manager.update_campaign_status(1, 'ACTIVE')
        
        # Check result
        self.assertTrue(result['success'])
        
        # Check notification
        notification = Notification.query.first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.title, "Campaign Activated")
        self.assertEqual(notification.type, NotificationType.SUCCESS.value)
        self.assertEqual(notification.category, NotificationCategory.CAMPAIGN.value)
        self.assertEqual(notification.related_entity_type, "campaign")
        self.assertEqual(notification.related_entity_id, 1)


if __name__ == '__main__':
    unittest.main()