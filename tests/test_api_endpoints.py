import json
import pytest
from flask import url_for

def test_health_check(client):
    """Test GET /api/health endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'Ad Automation P-01 API'

def test_api_interface(client):
    """Test GET /api/test endpoint."""
    response = client.get('/api/test')
    assert response.status_code == 200
    assert b'API Endpoint Testing' in response.data

def test_get_endpoints(client):
    """Test GET /api/test/endpoints endpoint."""
    response = client.get('/api/test/endpoints')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'count' in data
    assert 'data' in data
    assert isinstance(data['data'], list)

def test_platform_status(client):
    """Test GET /api/test/platform-status endpoint."""
    response = client.get('/api/test/platform-status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'count' in data
    assert 'data' in data
    assert isinstance(data['data'], list)

def test_get_job_openings(client, sample_job_opening):
    """Test GET /job_openings endpoint."""
    response = client.get('/job_openings')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == "Software Engineer"

def test_get_job_opening(client, sample_job_opening):
    """Test GET /job_openings/<id> endpoint."""
    response = client.get(f'/job_openings/{sample_job_opening.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == "Software Engineer"
    assert data['company'] == "Test Company"

def test_create_job_opening(client):
    """Test POST /job_openings endpoint."""
    job_data = {
        "title": "Data Scientist",
        "description": "ML engineer with Python experience",
        "location": "Remote",
        "company": "Another Test Company",
        "salary_range": "$90,000 - $120,000",
        "requirements": "5+ years of Python and ML experience",
        "job_type": "Full-time",
        "experience_level": "Senior"
    }
    
    response = client.post('/job_openings', 
                         data=json.dumps(job_data),
                         content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == "Data Scientist"
    assert data['id'] is not None

def test_update_job_opening(client, sample_job_opening):
    """Test PUT /job_openings/<id> endpoint."""
    update_data = {
        "title": "Senior Software Engineer",
        "salary_range": "$100,000 - $130,000"
    }
    
    response = client.put(f'/job_openings/{sample_job_opening.id}',
                        data=json.dumps(update_data),
                        content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == "Senior Software Engineer"
    assert data['salary_range'] == "$100,000 - $130,000"
    # Original data should remain unchanged
    assert data['description'] == "Python developer with Flask experience"

def test_delete_job_opening(client, sample_job_opening):
    """Test DELETE /job_openings/<id> endpoint."""
    response = client.delete(f'/job_openings/{sample_job_opening.id}')
    assert response.status_code == 204
    
    # Check that the job opening is deleted
    response = client.get(f'/job_openings/{sample_job_opening.id}')
    assert response.status_code == 404

def test_get_candidates(client, sample_candidates):
    """Test GET /candidates endpoint."""
    response = client.get('/candidates')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 10
    # Check using the correct candidate model fields
    assert 'desired_role' in data[0]
    assert data[0]['age'] >= 25

def test_get_platform_connections(client):
    """Test platform connection testing functionality."""
    # This is a POST endpoint that would actually connect to platforms
    # We'll just test that the endpoint exists and returns correctly
    response = client.post('/api/test/connection',
                        data=json.dumps({'platform': 'meta'}),
                        content_type='application/json')
    
    assert response.status_code in [200, 400]  # Either success or properly formed error
    data = json.loads(response.data)
    assert 'success' in data
    assert 'platform' in data

def test_execute_api_request(client):
    """Test execute API request endpoint."""
    # Similar to above, test the endpoint without expecting proper connection
    request_data = {
        'platform': 'meta',
        'endpoint': 'create_campaign',
        'method': 'POST',
        'params': {
            'name': 'Test Campaign',
            'objective': 'REACH',
            'status': 'PAUSED'
        }
    }
    
    response = client.post('/api/test/execute',
                        data=json.dumps(request_data),
                        content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'success' in data
    assert 'data' in data
    assert 'meta' in data
    assert data['meta']['platform'] == 'meta'
    assert data['meta']['endpoint'] == 'create_campaign'

def test_save_config(client):
    """Test saving a test configuration."""
    config_data = {
        'name': 'Test Config',
        'config': {
            'platform': 'meta',
            'endpoint': 'create_campaign',
            'method': 'POST',
            'parameters': {
                'name': 'Test Campaign',
                'objective': 'REACH'
            }
        }
    }
    
    response = client.post('/api/test/save-config',
                        data=json.dumps(config_data),
                        content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'config_id' in data

def test_get_test_configs(client):
    """Test getting saved test configurations."""
    response = client.get('/api/test/configs')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'count' in data
    assert 'data' in data
    assert isinstance(data['data'], list)

def test_get_test_history(client):
    """Test getting test execution history."""
    response = client.get('/api/test/history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'count' in data
    assert 'data' in data
    assert isinstance(data['data'], list)

def test_create_ad_campaign(client, sample_job_opening):
    """Test POST /campaigns endpoint with API Framework."""
    campaign_data = {
        "title": "Test API Framework Campaign",
        "description": "Testing the new API framework",
        "platforms": ["meta", "twitter"],  # Use specific platforms
        "job_opening_id": sample_job_opening.id,
        "budget": 100.00,
        "ad_content": "Join our team as a Software Engineer!"
    }
    
    response = client.post('/api/campaigns', 
                        data=json.dumps(campaign_data),
                        content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['data']['title'] == "Test API Framework Campaign"

def test_segment_candidates(client, sample_candidates):
    """Test POST /segments endpoint."""
    response = client.post('/api/segmentation/segments/create')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'segments_count' in data
    assert isinstance(data['segments'], list)

def test_get_segments(client, sample_candidates):
    """Test GET /segments endpoint."""
    response = client.get('/api/segmentation/segments')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'segments' in data

def test_publish_ad(client, sample_job_opening):
    """Test POST /publish_api_framework endpoint."""
    publish_data = {
        "job_opening_id": sample_job_opening.id,
        "platforms": ["meta", "twitter", "google"],
        "target_segment_id": None,  # No specific segment
        "budget": 200.00,
        "ad_content": "Apply now for our Software Engineer position!"
    }
    
    response = client.post('/api/publish',
                        data=json.dumps(publish_data),
                        content_type='application/json')
    
    assert response.status_code in [200, 201]
    data = json.loads(response.data)
    assert 'success' in data