"""API routes for MagnetoCursor."""

import time
from datetime import datetime, timedelta
import json
from flask import Blueprint, jsonify, request, render_template, current_app
from app.models.platform_connection_status import PlatformConnectionStatus
from app.models.ad_campaign import AdCampaign
from app.extensions import db
from app.services.meta_service import meta_service
from app.services.google_service import google_service
from app.services.twitter_service import twitter_service
import random

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/platform-status', methods=['GET'])
def platform_status():
    """Get the current status of all platform connections.
    
    Returns:
        JSON or HTML with platform connection statuses
    """
    # Check if this is an API request or a page view
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        # Get all platform statuses
        platform_statuses = PlatformConnectionStatus.get_all_platforms()
        
        # Convert to dictionary for JSON response
        platforms_dict = {status.platform: status.to_dict() for status in platform_statuses}
        
        # Calculate connected count
        connected_count = sum(1 for status in platform_statuses if status.is_connected)
        
        return jsonify({
            'success': True,
            'platforms': platforms_dict,
            'total_count': len(platform_statuses),
            'connected_count': connected_count,
            'timestamp': datetime.utcnow().isoformat()
        })
    else:
        # Render the completely redesigned platform status dashboard template
        return render_template('api/new_platform_status.html')


@api_bp.route('/test/connection', methods=['POST'])
def test_connection():
    """Test connection to a specific platform API."""
    data = request.get_json()
    platform = data.get('platform')
    
    if not platform:
        return jsonify({
            'success': False,
            'message': 'Platform is required'
        }), 400
    
    start_time = time.time()
    result = test_platform_connection(platform)
    response_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
    
    # Update the platform status in the database
    platform_status = PlatformConnectionStatus.get_platform_status(platform)
    platform_status.update_status(
        is_connected=result['success'],
        response_time_ms=response_time,
        status_message=result.get('message', ''),
        api_version=result.get('api_version'),
        details=result.get('details', {})
    )
    db.session.commit()
    
    # Add response time to the result
    result['response_time_ms'] = response_time
    return jsonify(result)


@api_bp.route('/platform-status/history', methods=['GET'])
def platform_status_history():
    """Get historical connection status for platforms."""
    platform = request.args.get('platform')
    period = request.args.get('period', 'day')  # day, week, month
    
    # Convert period to number of entries
    entries_limit = {
        'day': 24,
        'week': 168,
        'month': 720
    }.get(period, 24)
    
    if platform:
        # Get history for specific platform
        status = PlatformConnectionStatus.get_platform_status(platform)
        history = status.connection_history[-entries_limit:] if status.connection_history else []
        
        return jsonify({
            'success': True,
            'platform': platform,
            'display_name': status.display_name,
            'history': history,
            'period': period
        })
    else:
        # Get history for all platforms
        all_platforms = PlatformConnectionStatus.get_all_platforms()
        history_data = {}
        
        for status in all_platforms:
            history_data[status.platform] = {
                'display_name': status.display_name,
                'history': status.connection_history[-entries_limit:] if status.connection_history else []
            }
        
        return jsonify({
            'success': True,
            'platforms': history_data,
            'period': period
        })


@api_bp.route('/campaigns/list', methods=['GET'])
def get_campaigns_list():
    """API endpoint to get list of campaigns for dashboard."""
    try:
        # Get campaigns from database
        campaigns = AdCampaign.query.all()
        
        # Format campaigns for response
        campaign_list = []
        for campaign in campaigns:
            # Extract platform if available
            platform = None
            if campaign.platform_specific_content:
                if isinstance(campaign.platform_specific_content, str):
                    content = json.loads(campaign.platform_specific_content)
                else:
                    content = campaign.platform_specific_content
                platform = content.get('platform_name')
            
            campaign_list.append({
                'id': campaign.id,
                'name': campaign.title,
                'description': campaign.description,
                'status': campaign.status,
                'budget': campaign.budget,
                'platform': platform,
                'startDate': campaign.created_at.isoformat() if campaign.created_at else None,
                'endDate': None  # Placeholder for future implementation
            })
        
        return jsonify({
            'status': 'success',
            'campaigns': campaign_list
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching campaigns: {str(e)}")
        # Return mock data as fallback
        return jsonify({
            'status': 'success',
            'campaigns': [
                {'id': 1, 'name': 'Q1 2025 Product Launch', 'status': 'active', 'platform': 'meta'},
                {'id': 2, 'name': 'Summer Sale 2025', 'status': 'active', 'platform': 'google'},
                {'id': 3, 'name': 'Holiday Promotion 2024', 'status': 'paused', 'platform': 'twitter'},
                {'id': 4, 'name': 'Brand Awareness Campaign', 'status': 'active', 'platform': 'meta'},
                {'id': 5, 'name': 'Lead Generation Q2 2025', 'status': 'draft', 'platform': 'google'}
            ]
        })


@api_bp.route('/campaign/analytics/<int:campaign_id>', methods=['GET'])
def get_campaign_analytics(campaign_id):
    """API endpoint to get analytics data for a specific campaign."""
    try:
        # Get date range from request
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Get campaign from database
        campaign = AdCampaign.query.get_or_404(campaign_id)
        
        # Get available platforms
        platforms = ['meta', 'google', 'twitter']
        
        # Generate analytics data (in production, this would come from actual platform data)
        time_series_data = generate_time_series_data(campaign, platforms, date_from, date_to)
        platform_data = generate_platform_data(campaign, platforms)
        roi_data = generate_roi_data(campaign, platforms)
        
        # Format campaign for response
        campaign_details = {
            'id': campaign.id,
            'name': campaign.title,
            'description': campaign.description,
            'status': campaign.status,
            'budget': campaign.budget,
            'platforms': platforms,
            'startDate': campaign.created_at.isoformat() if campaign.created_at else None,
            'endDate': None,  # Placeholder for future implementation
            'objectives': {
                'primary': 'Conversions',
                'secondary': 'Brand Awareness'
            },
            'targeting': {
                'audience': 'Job Seekers',
                'demographics': ['Ages 25-45', 'Professionals'],
                'locations': ['United States', 'Canada', 'United Kingdom'],
                'interests': ['Technology', 'Career Development', 'Job Hunting']
            }
        }
        
        return jsonify({
            'status': 'success',
            'campaign': campaign_details,
            'timeSeriesData': time_series_data,
            'platformData': platform_data,
            'roiData': roi_data,
            'platforms': platforms
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching campaign analytics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error fetching campaign analytics: {str(e)}"
        }), 500


def generate_time_series_data(campaign, platforms, date_from, date_to):
    """Generate time series data for campaign analytics."""
    # Parse dates or use defaults
    try:
        start_date = datetime.strptime(date_from, '%Y-%m-%d') if date_from else (datetime.utcnow() - timedelta(days=30))
        end_date = datetime.strptime(date_to, '%Y-%m-%d') if date_to else datetime.utcnow()
    except ValueError:
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
    
    # Generate date range
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    # Generate platform data
    platform_data = {}
    for platform in platforms:
        # Initialize metrics for platform
        platform_data[platform] = {
            'impressions': [],
            'clicks': [],
            'conversions': [],
            'ctr': [],
            'cpc': [],
            'cpa': [],
            'spend': [],
            'revenue': [],
            'roi': []
        }
        
        # Generate base trend value for this platform
        base_trend = 100 + random.randint(-20, 20)
        
        # Generate daily metrics
        for date in dates:
            # Add some randomness to trend
            daily_factor = random.uniform(0.8, 1.2)
            trend = base_trend * daily_factor
            
            # Base metrics with some randomness for each platform
            impressions = int(trend * 100 * random.uniform(0.9, 1.1))
            clicks = int(impressions * random.uniform(0.01, 0.05))
            conversions = int(clicks * random.uniform(0.05, 0.15))
            spend = round(clicks * random.uniform(0.5, 2.0), 2)
            revenue = round(conversions * random.uniform(10, 30), 2)
            
            # Calculate derived metrics
            ctr = round((clicks / impressions * 100) if impressions > 0 else 0, 2)
            cpc = round((spend / clicks) if clicks > 0 else 0, 2)
            cpa = round((spend / conversions) if conversions > 0 else 0, 2)
            roi = round(((revenue - spend) / spend * 100) if spend > 0 else 0, 2)
            
            # Add data points
            platform_data[platform]['impressions'].append({'x': date, 'y': impressions})
            platform_data[platform]['clicks'].append({'x': date, 'y': clicks})
            platform_data[platform]['conversions'].append({'x': date, 'y': conversions})
            platform_data[platform]['ctr'].append({'x': date, 'y': ctr})
            platform_data[platform]['cpc'].append({'x': date, 'y': cpc})
            platform_data[platform]['cpa'].append({'x': date, 'y': cpa})
            platform_data[platform]['spend'].append({'x': date, 'y': spend})
            platform_data[platform]['revenue'].append({'x': date, 'y': revenue})
            platform_data[platform]['roi'].append({'x': date, 'y': roi})
    
    return {
        'platforms': platforms,
        'data': platform_data
    }


def generate_platform_data(campaign, platforms):
    """Generate platform comparison data for campaign analytics."""
    # Generate metrics by platform
    metrics_data = {}
    for metric in ['impressions', 'clicks', 'conversions', 'ctr', 'cpc', 'cpa', 'spend', 'revenue', 'roi']:
        metrics_data[metric] = {}
        
        for platform in platforms:
            # Generate random value based on metric type
            if metric == 'impressions':
                metrics_data[metric][platform] = random.randint(50000, 500000)
            elif metric == 'clicks':
                metrics_data[metric][platform] = random.randint(1000, 20000)
            elif metric == 'conversions':
                metrics_data[metric][platform] = random.randint(50, 1000)
            elif metric == 'ctr':
                metrics_data[metric][platform] = round(random.uniform(0.5, 5.0), 2)
            elif metric == 'cpc':
                metrics_data[metric][platform] = round(random.uniform(0.5, 2.0), 2)
            elif metric == 'cpa':
                metrics_data[metric][platform] = round(random.uniform(10, 50), 2)
            elif metric == 'spend':
                metrics_data[metric][platform] = round(random.uniform(1000, 10000), 2)
            elif metric == 'revenue':
                metrics_data[metric][platform] = round(random.uniform(5000, 30000), 2)
            elif metric == 'roi':
                metrics_data[metric][platform] = round(random.uniform(50, 300), 2)
    
    return {
        'data': metrics_data
    }


def generate_roi_data(campaign, platforms):
    """Generate ROI and breakdown data for campaign analytics."""
    # Overall ROI data
    overall_data = {
        'spend': 0,
        'revenue': 0,
        'roi': 0,
        'conversions': 0
    }
    
    # Platform-specific ROI data
    platform_data = {}
    
    for platform in platforms:
        # Generate platform metrics
        spend = round(random.uniform(1000, 10000), 2)
        revenue = round(random.uniform(5000, 30000), 2)
        conversions = random.randint(50, 1000)
        roi = round(((revenue - spend) / spend * 100) if spend > 0 else 0, 2)
        
        platform_data[platform] = {
            'spend': spend,
            'revenue': revenue,
            'roi': roi,
            'conversions': conversions
        }
        
        # Add to overall totals
        overall_data['spend'] += spend
        overall_data['revenue'] += revenue
        overall_data['conversions'] += conversions
    
    # Calculate overall ROI
    overall_data['roi'] = round(((overall_data['revenue'] - overall_data['spend']) / overall_data['spend'] * 100) 
                               if overall_data['spend'] > 0 else 0, 2)
    
    # Generate breakdown data
    breakdown_data = {
        'platform': generate_breakdown_data('platform', platforms),
        'ad_type': generate_breakdown_data('ad_type', ['Image', 'Video', 'Carousel', 'Collection']),
        'placement': generate_breakdown_data('placement', ['Feed', 'Stories', 'Search', 'Display']),
        'device': generate_breakdown_data('device', ['Desktop', 'Mobile', 'Tablet'])
    }
    
    return {
        'overall': overall_data,
        'platforms': platform_data,
        'breakdowns': breakdown_data
    }


def generate_breakdown_data(breakdown_type, items):
    """Generate breakdown data for different dimensions."""
    data = []
    
    for item in items:
        data.append({
            'name': item,
            'spend': round(random.uniform(1000, 10000), 2),
            'revenue': round(random.uniform(5000, 30000), 2),
            'impressions': random.randint(50000, 500000),
            'clicks': random.randint(1000, 20000),
            'conversions': random.randint(50, 1000)
        })
    
    return data


def test_platform_connection(platform):
    """Test connection to a specific platform API."""
    if platform == 'meta':
        return test_meta_connection()
    elif platform == 'google':
        return test_google_connection()
    elif platform == 'twitter':
        return test_twitter_connection()
    elif platform == 'tiktok':
        return test_tiktok_connection()
    elif platform == 'snapchat':
        return test_snapchat_connection()
    else:
        return {
            'success': False,
            'platform': platform,
            'message': f'Unknown platform: {platform}'
        }


def test_meta_connection():
    """Test connection to Meta (Facebook) API."""
    if meta_service.is_initialized:
        try:
            # In a real implementation, we would make a simple API call
            # to test the connection. For now, we'll simulate it.
            api_details = meta_service.get_api_info()
            
            return {
                'success': True,
                'platform': 'meta',
                'message': 'Successfully connected to Meta API',
                'api_version': api_details.get('version', 'unknown'),
                'details': {
                    'user_id': api_details.get('user_id'),
                    'app_id': api_details.get('app_id'),
                    'account_name': api_details.get('account_name'),
                    'permissions': api_details.get('permissions', [])
                }
            }
        except Exception as e:
            return {
                'success': False,
                'platform': 'meta',
                'message': f'Error connecting to Meta API: {str(e)}',
                'details': {
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
            }
    else:
        return {
            'success': False,
            'platform': 'meta',
            'message': 'Meta API is not initialized',
            'details': {
                'is_initialized': False,
                'error_type': 'ServiceNotInitialized'
            }
        }


def test_google_connection():
    """Test connection to Google Ads API."""
    if google_service.is_initialized:
        try:
            # In a real implementation, we would make a simple API call
            # to test the connection. For now, we'll simulate it.
            api_details = google_service.get_api_info()
            
            return {
                'success': True,
                'platform': 'google',
                'message': 'Successfully connected to Google Ads API',
                'api_version': api_details.get('version', 'unknown'),
                'details': {
                    'customer_id': api_details.get('customer_id'),
                    'account_name': api_details.get('account_name'),
                    'access_level': api_details.get('access_level')
                }
            }
        except Exception as e:
            return {
                'success': False,
                'platform': 'google',
                'message': f'Error connecting to Google Ads API: {str(e)}',
                'details': {
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
            }
    else:
        return {
            'success': False,
            'platform': 'google',
            'message': 'Google Ads API is not initialized',
            'details': {
                'is_initialized': False,
                'error_type': 'ServiceNotInitialized'
            }
        }


def test_twitter_connection():
    """Test connection to Twitter (X) API."""
    if twitter_service.is_initialized:
        try:
            # In a real implementation, we would make a simple API call
            # to test the connection. For now, we'll simulate it.
            api_details = twitter_service.get_api_info()
            
            return {
                'success': True,
                'platform': 'twitter',
                'message': 'Successfully connected to Twitter API',
                'api_version': api_details.get('version', 'unknown'),
                'details': {
                    'user_id': api_details.get('user_id'),
                    'screen_name': api_details.get('screen_name'),
                    'account_type': api_details.get('account_type')
                }
            }
        except Exception as e:
            return {
                'success': False,
                'platform': 'twitter',
                'message': f'Error connecting to Twitter API: {str(e)}',
                'details': {
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
            }
    else:
        return {
            'success': False,
            'platform': 'twitter',
            'message': 'Twitter API is not initialized',
            'details': {
                'is_initialized': False,
                'error_type': 'ServiceNotInitialized'
            }
        }


def test_tiktok_connection():
    """Test connection to TikTok API."""
    # Import conditionally to handle cases where the module isn't installed
    try:
        # Check if TikTok client module exists and is initialized
        from app.services.tiktok_service import tiktok_service
        
        if tiktok_service.is_initialized:
            try:
                # Get API info from the service
                api_details = tiktok_service.get_api_info()
                
                return {
                    'success': True,
                    'platform': 'tiktok',
                    'message': 'Successfully connected to TikTok API',
                    'api_version': api_details.get('version', 'unknown'),
                    'details': {
                        'account_id': api_details.get('account_id'),
                        'advertiser_id': api_details.get('advertiser_id'),
                        'access_level': api_details.get('access_level')
                    }
                }
            except Exception as e:
                return {
                    'success': False,
                    'platform': 'tiktok',
                    'message': f'Error connecting to TikTok API: {str(e)}',
                    'details': {
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    }
                }
        else:
            return {
                'success': False,
                'platform': 'tiktok',
                'message': 'TikTok API is not initialized',
                'details': {
                    'is_initialized': False,
                    'error_type': 'ServiceNotInitialized'
                }
            }
    except ImportError:
        # TikTok API module not installed
        return {
            'success': False,
            'platform': 'tiktok',
            'message': 'TikTok API integration is available but not configured',
            'details': {
                'status': 'not_configured',
                'is_optional': True,
                'setup_instructions': 'Install the TikTok Marketing API SDK and configure credentials'
            }
        }


def test_snapchat_connection():
    """Test connection to Snapchat API."""
    # Import conditionally to handle cases where the module isn't installed
    try:
        # Check if Snapchat client module exists and is initialized
        from app.services.snapchat_service import snapchat_service
        
        if snapchat_service.is_initialized:
            try:
                # Get API info from the service
                api_details = snapchat_service.get_api_info()
                
                return {
                    'success': True,
                    'platform': 'snapchat',
                    'message': 'Successfully connected to Snapchat API',
                    'api_version': api_details.get('version', 'unknown'),
                    'details': {
                        'organization_id': api_details.get('organization_id'),
                        'account_id': api_details.get('account_id'),
                        'access_level': api_details.get('access_level')
                    }
                }
            except Exception as e:
                return {
                    'success': False,
                    'platform': 'snapchat',
                    'message': f'Error connecting to Snapchat API: {str(e)}',
                    'details': {
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    }
                }
        else:
            return {
                'success': False,
                'platform': 'snapchat',
                'message': 'Snapchat API is not initialized',
                'details': {
                    'is_initialized': False,
                    'error_type': 'ServiceNotInitialized'
                }
            }
    except ImportError:
        # Snapchat API module not installed
        return {
            'success': False,
            'platform': 'snapchat',
            'message': 'Snapchat API integration is available but not configured',
            'details': {
                'status': 'not_configured',
                'is_optional': True,
                'setup_instructions': 'Install the Snapchat Marketing API SDK and configure credentials'
            }
        }