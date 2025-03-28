"""Testing utilities for the Ad Automation P-01 project."""
import sys
from unittest.mock import MagicMock
from flask_restful import Api
from flask import jsonify, request, abort
import json

def mock_api_module():
    """Mock the app.api module for testing."""
    mock_api = MagicMock()
    mock_api.init_app = lambda app: None
    
    # Add to sys.modules to ensure it's used during import
    sys.modules['app.api'] = mock_api
    
    return mock_api

def setup_mock_routes(app, db):
    """Set up mock routes for testing."""
    from app.models.job_opening import JobOpening
    from app.models.candidate import Candidate
    from app.models.ad_campaign import AdCampaign
    from app.models.segment import Segment
    
    # API health endpoint
    @app.route('/api/health')
    def api_health():
        return jsonify({
            'status': 'healthy',
            'service': 'Ad Automation P-01 API'
        })
        
    # API test interface
    @app.route('/api/test')
    def api_test_interface():
        return jsonify({'message': 'API Endpoint Testing'})
        
    # API test endpoints
    @app.route('/api/test/endpoints')
    def api_test_endpoints():
        return jsonify({
            'success': True,
            'count': 3,
            'data': [
                {'name': 'Meta API', 'status': 'available'},
                {'name': 'Twitter API', 'status': 'available'},
                {'name': 'Google Ads API', 'status': 'available'}
            ]
        })
        
    # Platform status endpoint
    @app.route('/api/test/platform-status')
    def platform_status():
        return jsonify({
            'success': True,
            'count': 3,
            'data': [
                {'platform': 'meta', 'status': 'connected', 'features': ['ads', 'insights']},
                {'platform': 'twitter', 'status': 'connected', 'features': ['ads', 'analytics']},
                {'platform': 'google', 'status': 'connected', 'features': ['ads', 'keywords']}
            ]
        })
        
    # Test platform connection
    @app.route('/api/test/connection', methods=['POST'])
    def test_connection():
        data = request.json
        platform = data.get('platform', '').lower() if data else 'unknown'
        
        if platform not in ['meta', 'twitter', 'google']:
            return jsonify({
                'success': False,
                'platform': platform,
                'error': 'Invalid platform'
            }), 400
            
        return jsonify({
            'success': True,
            'platform': platform,
            'connection_status': 'connected',
            'api_version': '2.0'
        })
        
    # Execute API request
    @app.route('/api/test/execute', methods=['POST'])
    def execute_api_request():
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'Missing request data'}), 400
            
        platform = data.get('platform', '')
        endpoint = data.get('endpoint', '')
        method = data.get('method', 'GET')
        
        return jsonify({
            'success': True,
            'data': {
                'id': '12345',
                'status': 'success',
                'created_at': '2023-05-10T12:00:00Z'
            },
            'meta': {
                'platform': platform,
                'endpoint': endpoint,
                'method': method,
                'execution_time': 0.25
            }
        })
        
    # API test save config
    @app.route('/api/test/save-config', methods=['POST'])
    def save_test_config():
        data = request.json
        if not data or not data.get('name') or not data.get('config'):
            return jsonify({'success': False, 'error': 'Invalid configuration'}), 400
            
        return jsonify({
            'success': True,
            'config_id': '67890',
            'message': 'Configuration saved successfully'
        })
        
    # API test configs
    @app.route('/api/test/configs', methods=['GET'])
    def get_test_configs():
        return jsonify({
            'success': True,
            'count': 2,
            'data': [
                {
                    'id': '67890',
                    'name': 'Test Config',
                    'platform': 'meta',
                    'created_at': '2023-05-09T10:30:00Z'
                },
                {
                    'id': '67891',
                    'name': 'Another Test',
                    'platform': 'twitter',
                    'created_at': '2023-05-08T14:20:00Z'
                }
            ]
        })
        
    # API test history
    @app.route('/api/test/history', methods=['GET'])
    def get_test_history():
        return jsonify({
            'success': True,
            'count': 2,
            'data': [
                {
                    'id': '12345',
                    'platform': 'meta',
                    'endpoint': 'create_campaign',
                    'status': 'success',
                    'executed_at': '2023-05-10T12:00:00Z'
                },
                {
                    'id': '12346',
                    'platform': 'twitter',
                    'endpoint': 'create_ad',
                    'status': 'success',
                    'executed_at': '2023-05-10T11:45:00Z'
                }
            ]
        })
    
    # API Framework campaign create
    @app.route('/api/campaigns', methods=['POST'])
    def api_create_campaign():
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'Missing campaign data'}), 400
            
        job_id = data.get('job_opening_id')
        if not job_id:
            return jsonify({'success': False, 'error': 'Missing job opening ID'}), 400
            
        # Would normally create the campaign in database
        return jsonify({
            'success': True,
            'data': {
                'id': '98765',
                'title': data.get('title', 'New Campaign'),
                'description': data.get('description', ''),
                'job_opening_id': job_id,
                'platforms': data.get('platforms', []),
                'budget': data.get('budget', 0),
                'status': 'pending',
                'created_at': '2023-05-10T14:30:00Z'
            }
        }), 201
        
    # Segmentation endpoints
    @app.route('/api/segmentation/segments/create', methods=['POST'])
    def create_segments():
        # Would normally segment candidates using ML
        return jsonify({
            'success': True,
            'segments_count': 3,
            'segments': [
                {'id': 1, 'name': 'Junior Engineers', 'size': 25, 'attributes': ['entry-level', 'tech']},
                {'id': 2, 'name': 'Mid-level Professionals', 'size': 42, 'attributes': ['experienced', 'diverse-fields']},
                {'id': 3, 'name': 'Senior Specialists', 'size': 18, 'attributes': ['senior', 'specialized']}
            ]
        })
        
    @app.route('/api/segmentation/segments', methods=['GET'])
    def get_api_segments():
        return jsonify({
            'success': True,
            'segments': [
                {'id': 1, 'name': 'Junior Engineers', 'size': 25, 'attributes': ['entry-level', 'tech']},
                {'id': 2, 'name': 'Mid-level Professionals', 'size': 42, 'attributes': ['experienced', 'diverse-fields']},
                {'id': 3, 'name': 'Senior Specialists', 'size': 18, 'attributes': ['senior', 'specialized']}
            ]
        })
        
    # API publish endpoint
    @app.route('/api/publish', methods=['POST'])
    def publish_ad():
        data = request.json
        if not data or not data.get('job_opening_id'):
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
            
        # Would normally publish to platforms
        return jsonify({
            'success': True,
            'campaign_id': '54321',
            'platforms': data.get('platforms', []),
            'job_opening_id': data.get('job_opening_id'),
            'status': 'published',
            'platform_responses': {
                'meta': {'ad_id': 'meta_12345', 'status': 'active'},
                'twitter': {'ad_id': 'tw_67890', 'status': 'active'},
                'google': {'ad_id': 'g_24680', 'status': 'active'}
            }
        })
    
    # Job Openings routes
    @app.route('/job_openings', methods=['GET'])
    def get_job_openings():
        jobs = JobOpening.query.all()
        return jsonify([job.to_dict() for job in jobs])
    
    @app.route('/job_openings/<int:job_id>', methods=['GET'])
    def get_job_opening(job_id):
        # Using Session.get() instead of Query.get() to avoid SQLAlchemy deprecation warning
        job = db.session.get(JobOpening, job_id)
        if not job:
            abort(404)
        return jsonify(job.to_dict())
    
    @app.route('/job_openings', methods=['POST'])
    def create_job_opening():
        data = request.json
        if not data:
            abort(400)
        
        try:
            job = JobOpening(
                title=data['title'],
                description=data['description'],
                location=data['location'],
                company=data['company'],
                salary_range=data.get('salary_range'),
                requirements=data.get('requirements'),
                job_type=data['job_type'],
                experience_level=data.get('experience_level')
            )
            db.session.add(job)
            db.session.commit()
            return jsonify(job.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
    
    @app.route('/job_openings/<int:job_id>', methods=['PUT'])
    def update_job_opening(job_id):
        # Using Session.get() instead of Query.get() to avoid SQLAlchemy deprecation warning
        job = db.session.get(JobOpening, job_id)
        if not job:
            abort(404)
        
        data = request.json
        for key, value in data.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        db.session.commit()
        return jsonify(job.to_dict())
    
    @app.route('/job_openings/<int:job_id>', methods=['DELETE'])
    def delete_job_opening(job_id):
        # Using Session.get() instead of Query.get() to avoid SQLAlchemy deprecation warning
        job = db.session.get(JobOpening, job_id)
        if not job:
            abort(404)
        
        db.session.delete(job)
        db.session.commit()
        return '', 204
    
    # Candidates routes
    @app.route('/candidates', methods=['GET'])
    def get_candidates():
        candidates = Candidate.query.all()
        return jsonify([c.to_dict() for c in candidates])
    
    # Campaigns routes
    @app.route('/campaigns', methods=['POST'])
    def create_campaign():
        data = request.json
        if not data:
            abort(400)
        
        job = JobOpening.query.get(data['job_opening_id'])
        if not job:
            abort(404)
        
        campaign = AdCampaign(
            job_opening_id=data['job_opening_id'],
            name=data['name'],
            platforms=data['platforms'],
            budget=data['budget'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            target_audience=data['target_audience']
        )
        
        db.session.add(campaign)
        db.session.commit()
        return jsonify(campaign.to_dict()), 201
    
    @app.route('/campaigns/<int:campaign_id>/status', methods=['GET'])
    def get_campaign_status(campaign_id):
        # Mock status response
        return jsonify({
            "campaign_id": campaign_id,
            "status": "active",
            "platforms_status": {
                "meta": {"published": True, "status": "active"},
                "twitter": {"published": True, "status": "active"},
                "google": {"published": False, "status": "pending"}
            }
        })
    
    @app.route('/campaigns/<int:campaign_id>/performance', methods=['GET'])
    def get_campaign_performance(campaign_id):
        # Mock performance response
        return jsonify({
            "campaign_id": campaign_id,
            "overall_performance": {
                "impressions": 2500,
                "clicks": 150,
                "ctr": 0.06,
                "spend": 250.0
            },
            "platforms": {
                "meta": {
                    "impressions": 1250,
                    "clicks": 75,
                    "ctr": 0.06,
                    "spend": 125.50,
                    "cost_per_click": 1.67,
                    "conversions": 8,
                    "cost_per_conversion": 15.69
                },
                "twitter": {
                    "impressions": 1250,
                    "clicks": 75,
                    "ctr": 0.06,
                    "spend": 124.50,
                    "cost_per_click": 1.66,
                    "conversions": 7,
                    "cost_per_conversion": 17.79
                }
            }
        })
    
    # Segments routes
    @app.route('/segments', methods=['GET'])
    def get_segments():
        segments = Segment.query.all()
        return jsonify([s.to_dict() for s in segments])
    
    @app.route('/segments/<int:segment_id>', methods=['GET'])
    def get_segment(segment_id):
        segment = Segment.query.get(segment_id)
        if not segment:
            abort(404)
        return jsonify(segment.to_dict())
    
    @app.route('/segments', methods=['POST'])
    def create_segment():
        data = request.json
        if not data:
            abort(400)
        
        segment = Segment(
            name=data['name'],
            description=data['description'],
            criteria=data['criteria'],
            clusters=[{"id": 0, "candidates": [1, 2, 3]}, {"id": 1, "candidates": [4, 5, 6]}]
        )
        
        db.session.add(segment)
        db.session.commit()
        
        # Return with clusters for testing
        response = segment.to_dict()
        response['clusters'] = segment.clusters
        return jsonify(response), 201
    
    # Publish routes
    @app.route('/publish', methods=['POST'])
    def publish():
        data = request.json
        if not data:
            abort(400)
        
        campaign_id = data.get('campaign_id')
        if not campaign_id:
            abort(400)
        
        campaign = AdCampaign.query.get(campaign_id)
        if not campaign:
            abort(404)
        
        platforms = data.get('platforms', [])
        
        # Make sure all platforms are valid
        for platform in platforms:
            if platform not in campaign.platforms:
                return jsonify({"error": f"Platform {platform} not in campaign"}), 400
        
        # Mock successful publishing
        results = {}
        for platform in platforms:
            results[platform] = {"id": f"{platform}-123", "success": True}
        
        return jsonify({
            "success": True,
            "campaign_id": campaign_id,
            "published_at": "2023-04-01T12:00:00Z",
            "results": results
        }) 