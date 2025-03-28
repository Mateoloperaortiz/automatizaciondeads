from flask import Blueprint, render_template, jsonify, request
from app.models.ad_campaign import AdCampaign
from app.models.segment import Segment
from app import db
from sqlalchemy import func
import json

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
def index():
    """Analytics dashboard index page."""
    # Get platforms with active campaigns
    platforms = db.session.query(
        func.json_extract(AdCampaign.platform_specific_content, '$.platform_name').label('platform')
    ).distinct().all()
    
    platforms = [p.platform for p in platforms if p.platform]
    
    # Get all segments for filtering
    segments = Segment.query.all()
    
    return render_template(
        'analytics/index.html',
        platforms=platforms,
        segments=segments
    )

@analytics_bp.route('/platform-comparison')
def platform_comparison():
    """Cross-platform performance comparison view."""
    # Get platforms with active campaigns
    platforms = db.session.query(
        func.json_extract(AdCampaign.platform_specific_content, '$.platform_name').label('platform')
    ).distinct().all()
    
    platforms = [p.platform for p in platforms if p.platform]
    
    # Get all segments for filtering
    segments = Segment.query.all()
    
    return render_template(
        'analytics/platform_comparison.html',
        platforms=platforms,
        segments=segments
    )

@analytics_bp.route('/performance-data')
def get_performance_data():
    """API endpoint to get cross-platform performance metrics."""
    # Filter parameters
    segment_id = request.args.get('segment_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Get metrics by platform
    platform_metrics = {}
    
    # Base query
    query = AdCampaign.query
    
    # Apply filters
    if segment_id:
        query = query.filter(
            func.json_extract(AdCampaign.platform_specific_content, '$.segment_id') == segment_id
        )
    
    if date_from:
        query = query.filter(AdCampaign.created_at >= date_from)
    
    if date_to:
        query = query.filter(AdCampaign.created_at <= date_to)
    
    # Get campaigns
    campaigns = query.all()
    
    for campaign in campaigns:
        # Extract platform and metrics
        if not campaign.platform_specific_content:
            continue
            
        try:
            content = campaign.platform_specific_content
            if isinstance(content, str):
                content = json.loads(content)
                
            platform = content.get('platform_name')
            if not platform:
                continue
                
            # Initialize platform data if not exists
            if platform not in platform_metrics:
                platform_metrics[platform] = {
                    'impressions': 0,
                    'clicks': 0,
                    'spend': 0,
                    'conversions': 0,
                    'ctr': 0,
                    'cpc': 0,
                    'campaigns': 0
                }
            
            # Add metrics
            metrics = content.get('metrics', {})
            if metrics:
                platform_metrics[platform]['impressions'] += int(metrics.get('impressions', 0))
                platform_metrics[platform]['clicks'] += int(metrics.get('clicks', 0))
                platform_metrics[platform]['spend'] += float(metrics.get('spend', 0))
                platform_metrics[platform]['conversions'] += int(metrics.get('conversions', 0))
                platform_metrics[platform]['campaigns'] += 1
        
        except Exception as e:
            print(f"Error processing campaign {campaign.id}: {str(e)}")
    
    # Calculate derived metrics
    for platform, metrics in platform_metrics.items():
        if metrics['impressions'] > 0:
            metrics['ctr'] = (metrics['clicks'] / metrics['impressions']) * 100
        if metrics['clicks'] > 0:
            metrics['cpc'] = metrics['spend'] / metrics['clicks']
        if metrics['spend'] > 0 and metrics['conversions'] > 0:
            metrics['cpa'] = metrics['spend'] / metrics['conversions']
            metrics['roi'] = ((metrics['conversions'] * 100) - metrics['spend']) / metrics['spend'] * 100
        else:
            metrics['cpa'] = 0
            metrics['roi'] = 0
    
    return jsonify(platform_metrics)

@analytics_bp.route('/ab-testing')
def ab_testing():
    """A/B testing interface for comparing audience segments or ad creatives."""
    # Get all segments
    segments = Segment.query.all()
    
    # Get all platforms
    platforms = db.session.query(
        func.json_extract(AdCampaign.platform_specific_content, '$.platform_name').label('platform')
    ).distinct().all()
    
    platforms = [p.platform for p in platforms if p.platform]
    
    return render_template(
        'analytics/ab_testing.html',
        segments=segments,
        platforms=platforms
    )

@analytics_bp.route('/ab-testing-data')
def get_ab_testing_data():
    """API endpoint for A/B testing comparison data."""
    # Get comparison parameters
    segment_ids = request.args.getlist('segment_ids')
    platform = request.args.get('platform')
    metric = request.args.get('metric', 'ctr')  # Default to CTR
    
    if not segment_ids or len(segment_ids) < 2:
        return jsonify({'error': 'At least two segments must be selected'}), 400
    
    # Results by segment
    results = {}
    
    for segment_id in segment_ids:
        # Get segment
        segment = Segment.query.get(segment_id)
        if not segment:
            continue
        
        # Get campaigns for this segment
        query = AdCampaign.query.filter(
            func.json_extract(AdCampaign.platform_specific_content, '$.segment_id') == segment_id
        )
        
        if platform:
            query = query.filter(
                func.json_extract(AdCampaign.platform_specific_content, '$.platform_name') == platform
            )
        
        campaigns = query.all()
        
        # Initialize metrics
        segment_metrics = {
            'impressions': 0,
            'clicks': 0,
            'spend': 0,
            'conversions': 0,
            'campaigns': 0
        }
        
        # Collect metrics
        for campaign in campaigns:
            if not campaign.platform_specific_content:
                continue
                
            try:
                content = campaign.platform_specific_content
                if isinstance(content, str):
                    content = json.loads(content)
                    
                # Add metrics
                metrics = content.get('metrics', {})
                if metrics:
                    segment_metrics['impressions'] += int(metrics.get('impressions', 0))
                    segment_metrics['clicks'] += int(metrics.get('clicks', 0))
                    segment_metrics['spend'] += float(metrics.get('spend', 0))
                    segment_metrics['conversions'] += int(metrics.get('conversions', 0))
                    segment_metrics['campaigns'] += 1
            
            except Exception as e:
                print(f"Error processing campaign {campaign.id}: {str(e)}")
        
        # Calculate derived metrics
        if segment_metrics['impressions'] > 0:
            segment_metrics['ctr'] = (segment_metrics['clicks'] / segment_metrics['impressions']) * 100
        else:
            segment_metrics['ctr'] = 0
            
        if segment_metrics['clicks'] > 0:
            segment_metrics['cpc'] = segment_metrics['spend'] / segment_metrics['clicks']
        else:
            segment_metrics['cpc'] = 0
            
        if segment_metrics['spend'] > 0 and segment_metrics['conversions'] > 0:
            segment_metrics['cpa'] = segment_metrics['spend'] / segment_metrics['conversions']
            segment_metrics['roi'] = ((segment_metrics['conversions'] * 100) - segment_metrics['spend']) / segment_metrics['spend'] * 100
        else:
            segment_metrics['cpa'] = 0
            segment_metrics['roi'] = 0
        
        # Add to results
        results[segment.name] = segment_metrics
    
    return jsonify({
        'metric': metric,
        'results': results
    })

@analytics_bp.route('/roi-dashboard')
def roi_dashboard():
    """ROI and conversion tracking dashboard."""
    # Get all segments
    segments = Segment.query.all()
    
    # Get all platforms
    platforms = db.session.query(
        func.json_extract(AdCampaign.platform_specific_content, '$.platform_name').label('platform')
    ).distinct().all()
    
    platforms = [p.platform for p in platforms if p.platform]
    
    return render_template(
        'analytics/roi_dashboard.html',
        segments=segments,
        platforms=platforms
    )

@analytics_bp.route('/roi-data')
def get_roi_data():
    """API endpoint for ROI and conversion metrics."""
    # Filter parameters
    segment_id = request.args.get('segment_id')
    platform = request.args.get('platform')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Base query
    query = AdCampaign.query
    
    # Apply filters
    if segment_id:
        query = query.filter(
            func.json_extract(AdCampaign.platform_specific_content, '$.segment_id') == segment_id
        )
    
    if platform:
        query = query.filter(
            func.json_extract(AdCampaign.platform_specific_content, '$.platform_name') == platform
        )
    
    if date_from:
        query = query.filter(AdCampaign.created_at >= date_from)
    
    if date_to:
        query = query.filter(AdCampaign.created_at <= date_to)
    
    # Get campaigns
    campaigns = query.all()
    
    # Total metrics
    totals = {
        'impressions': 0,
        'clicks': 0,
        'spend': 0,
        'conversions': 0,
        'revenue': 0,
        'campaigns': 0
    }
    
    # Data points for time series
    time_series = {}
    
    for campaign in campaigns:
        if not campaign.platform_specific_content:
            continue
            
        try:
            content = campaign.platform_specific_content
            if isinstance(content, str):
                content = json.loads(content)
                
            # Add to totals
            metrics = content.get('metrics', {})
            if metrics:
                totals['impressions'] += int(metrics.get('impressions', 0))
                totals['clicks'] += int(metrics.get('clicks', 0))
                totals['spend'] += float(metrics.get('spend', 0))
                totals['conversions'] += int(metrics.get('conversions', 0))
                totals['revenue'] += float(metrics.get('revenue', 0))
                totals['campaigns'] += 1
                
                # Add to time series
                date = campaign.created_at.strftime('%Y-%m-%d')
                if date not in time_series:
                    time_series[date] = {
                        'impressions': 0,
                        'clicks': 0,
                        'spend': 0,
                        'conversions': 0,
                        'revenue': 0
                    }
                
                time_series[date]['impressions'] += int(metrics.get('impressions', 0))
                time_series[date]['clicks'] += int(metrics.get('clicks', 0))
                time_series[date]['spend'] += float(metrics.get('spend', 0))
                time_series[date]['conversions'] += int(metrics.get('conversions', 0))
                time_series[date]['revenue'] += float(metrics.get('revenue', 0))
        
        except Exception as e:
            print(f"Error processing campaign {campaign.id}: {str(e)}")
    
    # Calculate derived metrics
    if totals['impressions'] > 0:
        totals['ctr'] = (totals['clicks'] / totals['impressions']) * 100
    else:
        totals['ctr'] = 0
        
    if totals['clicks'] > 0:
        totals['cpc'] = totals['spend'] / totals['clicks']
    else:
        totals['cpc'] = 0
        
    if totals['spend'] > 0:
        if totals['conversions'] > 0:
            totals['cpa'] = totals['spend'] / totals['conversions']
        else:
            totals['cpa'] = 0
            
        if totals['revenue'] > 0:
            totals['roi'] = ((totals['revenue'] - totals['spend']) / totals['spend']) * 100
        else:
            totals['roi'] = -100  # 100% loss if no revenue
    else:
        totals['cpa'] = 0
        totals['roi'] = 0
    
    # Convert time series to ordered list
    time_series_list = [
        {'date': date, **metrics}
        for date, metrics in sorted(time_series.items())
    ]
    
    # Calculate daily ROI for time series
    for day in time_series_list:
        if day['spend'] > 0:
            if day['revenue'] > 0:
                day['roi'] = ((day['revenue'] - day['spend']) / day['spend']) * 100
            else:
                day['roi'] = -100  # 100% loss if no revenue
        else:
            day['roi'] = 0
    
    return jsonify({
        'totals': totals,
        'time_series': time_series_list
    })