import json
import pytest
from datetime import datetime, timedelta
from flask import Blueprint
from app.models.ad_campaign import AdCampaign, SocialMediaPlatform
from app.models.segment import Segment
from app import db
import unittest.mock as mock

@pytest.fixture
def app(app):
    """Register the analytics blueprint on the test app."""
    # Import and register the analytics blueprint
    from app.routes.analytics import analytics_bp
    app.register_blueprint(analytics_bp)
    
    # Mock render_template to avoid template not found errors
    with mock.patch('app.routes.analytics.render_template', return_value='Mocked template'):
        yield app

@pytest.fixture
def sample_platforms(db_session):
    """Create sample social media platforms for testing."""
    platforms = []
    for platform_name in ['Meta', 'Twitter', 'Google']:
        platform = SocialMediaPlatform(
            name=platform_name.lower(),
            active=True
        )
        db_session.add(platform)
        platforms.append(platform)
    
    db_session.commit()
    return platforms

@pytest.fixture
def sample_segments(db_session):
    """Create sample segments for testing."""
    segments = []
    for i in range(3):
        segment = Segment(
            name=f"Test Segment {i+1}",
            description=f"Description for test segment {i+1}",
            segment_code=f"SEGMENT_{i+1}",
            criteria={"age_range": [25, 35], "interests": ["technology"]},
            _candidate_ids=[i*5 + j for j in range(5)]  # 5 candidates per segment
        )
        db_session.add(segment)
        segments.append(segment)
    
    db_session.commit()
    return segments

@pytest.fixture
def sample_campaigns_with_metrics(db_session, sample_job_opening, sample_platforms, sample_segments):
    """Create sample ad campaigns with metrics data for testing analytics."""
    campaigns = []
    
    # Create 9 campaigns, 3 for each platform, with each campaign targeting a different segment
    for i, platform in enumerate(sample_platforms):
        for j, segment in enumerate(sample_segments):
            # Create base campaign
            campaign = AdCampaign(
                title=f"Test Campaign {i+1}-{j+1}",
                description=f"Description for campaign {i+1}-{j+1}",
                platform_id=platform.id,
                job_opening_id=sample_job_opening.id,
                segment_id=segment.id,
                budget=100.0 * (i+1),
                status='active',
                ad_headline=f"Test Headline {i+1}-{j+1}",
                ad_text=f"Test ad text for campaign {i+1}-{j+1}",
                ad_cta="Apply Now",
                created_at=datetime.utcnow() - timedelta(days=j*3)  # Vary dates
            )
            
            # Add platform-specific content with metrics
            # Vary metrics to ensure interesting comparison data
            base_impressions = 1000 * (i+1) * (j+1)
            base_clicks = 50 * (i+1) * (j+1)
            base_spend = 50.0 * (i+1)
            base_conversions = 5 * (i+1) * (j+1)
            
            platform_specific_content = {
                "platform_name": platform.name.lower(),  # Make sure platform name is lowercase
                "segment_id": segment.id,
                "platform_campaign_id": f"platform-{platform.name}-{i}-{j}",
                "metrics": {
                    "impressions": base_impressions,
                    "clicks": base_clicks,
                    "spend": base_spend,
                    "conversions": base_conversions,
                    "revenue": base_conversions * 100.0  # Average value of $100 per conversion
                }
            }
            
            campaign.platform_specific_content = json.dumps(platform_specific_content)
            db_session.add(campaign)
            campaigns.append(campaign)
    
    db_session.commit()
    return campaigns

def test_get_performance_data(client, sample_campaigns_with_metrics):
    """Test the performance data API endpoint."""
    response = client.get('/analytics/performance-data')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'meta' in data
    assert 'twitter' in data
    assert 'google' in data
    
    # Verify metrics for Meta
    meta_metrics = data['meta']
    assert 'impressions' in meta_metrics
    assert 'clicks' in meta_metrics
    assert 'spend' in meta_metrics
    assert 'conversions' in meta_metrics
    assert 'ctr' in meta_metrics
    assert 'cpc' in meta_metrics
    
    # Verify data types
    assert isinstance(meta_metrics['impressions'], int)
    assert isinstance(meta_metrics['clicks'], int)
    assert isinstance(meta_metrics['spend'], (int, float))
    assert isinstance(meta_metrics['conversions'], int)
    assert isinstance(meta_metrics['ctr'], (int, float))
    assert isinstance(meta_metrics['cpc'], (int, float))

def test_get_ab_testing_data_with_segments(client, sample_campaigns_with_metrics, sample_segments):
    """Test the A/B testing data API endpoint with segment comparison."""
    # Get IDs of first two segments
    segment_ids = [str(segment.id) for segment in sample_segments[:2]]
    
    response = client.get(f'/analytics/ab-testing-data?segment_ids={segment_ids[0]}&segment_ids={segment_ids[1]}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'metric' in data
    assert 'results' in data
    
    # Verify default metric is 'ctr'
    assert data['metric'] == 'ctr'
    
    # Verify results includes data for both segments
    results = data['results']
    assert len(results) == 2
    
    # Check segment names match expected segments
    segment_names = [segment.name for segment in sample_segments[:2]]
    for segment_name in segment_names:
        assert segment_name in results
    
    # Test with specific platform filter
    response = client.get(f'/analytics/ab-testing-data?segment_ids={segment_ids[0]}&segment_ids={segment_ids[1]}&platform=meta')
    assert response.status_code == 200
    
    # Test with specific metric
    response = client.get(f'/analytics/ab-testing-data?segment_ids={segment_ids[0]}&segment_ids={segment_ids[1]}&metric=cpc')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['metric'] == 'cpc'

def test_ab_testing_data_invalid_input(client, sample_segments):
    """Test A/B testing data API with invalid inputs."""
    # Test with no segments
    response = client.get('/analytics/ab-testing-data')
    assert response.status_code == 400
    
    # Test with only one segment (make sure we have segments)
    assert len(sample_segments) > 0
    segment = sample_segments[0]
    response = client.get(f'/analytics/ab-testing-data?segment_ids={segment.id}')
    assert response.status_code == 400
    
    # Test with nonexistent segment IDs
    response = client.get('/analytics/ab-testing-data?segment_ids=999&segment_ids=1000')
    assert response.status_code == 200  # Should still return, but results might be empty
    
def test_get_roi_data(client, sample_campaigns_with_metrics):
    """Test the ROI data API endpoint."""
    response = client.get('/analytics/roi-data')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'totals' in data
    assert 'time_series' in data
    
    # Verify totals include expected metrics
    totals = data['totals']
    assert 'impressions' in totals
    assert 'clicks' in totals
    assert 'spend' in totals
    assert 'conversions' in totals
    assert 'revenue' in totals
    assert 'roi' in totals
    assert 'ctr' in totals
    assert 'cpc' in totals
    assert 'cpa' in totals
    
    # Verify time series data
    time_series = data['time_series']
    assert isinstance(time_series, list)
    assert len(time_series) > 0
    
    # Test with various filters
    # 1. Platform filter
    response = client.get('/analytics/roi-data?platform=meta')
    assert response.status_code == 200
    
    # 2. Date filter
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
    response = client.get(f'/analytics/roi-data?date_from={yesterday}&date_to={tomorrow}')
    assert response.status_code == 200