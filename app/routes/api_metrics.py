"""
API metrics routes for the MagnetoCursor application.

These routes provide access to API usage metrics collected by the API Framework.
"""

from flask import Blueprint, render_template, jsonify, current_app, request
from datetime import datetime

api_metrics_bp = Blueprint('api_metrics', __name__, url_prefix='/api/metrics')

@api_metrics_bp.route('/')
def metrics_dashboard():
    """View API metrics dashboard."""
    if not current_app.config.get('USE_API_FRAMEWORK', False):
        return jsonify({
            'error': 'API Framework is not enabled'
        }), 400
           
    metrics = {}
    if hasattr(current_app, 'api_metrics'):
        for platform, metrics_collector in current_app.api_metrics.items():
            if metrics_collector:
                # Get basic metrics summary
                metrics[platform] = {
                    'summary': metrics_collector.get_summary(),
                    'request_rate': metrics_collector.get_request_rate(window=300),  # Last 5 minutes
                    'error_rate': metrics_collector.get_error_rate(window=3600),  # Last hour
                    'latency_trends': metrics_collector.get_latency_trends(platform, window=86400, buckets=24)  # Last 24h
                }
                
    return render_template(
        'api/metrics.html',
        metrics=metrics,
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@api_metrics_bp.route('/data')
def metrics_data():
    """API endpoint to get metrics data."""
    if not current_app.config.get('USE_API_FRAMEWORK', False):
        return jsonify({
            'error': 'API Framework is not enabled'
        }), 400
           
    metrics = {}
    if hasattr(current_app, 'api_metrics'):
        for platform, metrics_collector in current_app.api_metrics.items():
            if metrics_collector:
                # Get basic metrics summary
                metrics[platform] = {
                    'summary': metrics_collector.get_summary(),
                    'request_rate': metrics_collector.get_request_rate(window=300),  # Last 5 minutes
                    'error_rate': metrics_collector.get_error_rate(window=3600),  # Last hour
                    'latency_trends': metrics_collector.get_latency_trends(platform, window=86400, buckets=24)  # Last 24h
                }
                
    return jsonify({
        'metrics': metrics,
        'timestamp': datetime.now().isoformat()
    })

@api_metrics_bp.route('/clear')
def clear_metrics():
    """Clear API metrics."""
    if not current_app.config.get('USE_API_FRAMEWORK', False):
        return jsonify({
            'error': 'API Framework is not enabled'
        }), 400
           
    if hasattr(current_app, 'api_metrics'):
        for platform, metrics_collector in current_app.api_metrics.items():
            if metrics_collector:
                metrics_collector.clear()
                
    return jsonify({
        'success': True,
        'message': 'Metrics cleared'
    })

@api_metrics_bp.route('/platform/<platform>')
def platform_metrics(platform):
    """Get metrics for a specific platform."""
    if not current_app.config.get('USE_API_FRAMEWORK', False):
        return jsonify({
            'error': 'API Framework is not enabled'
        }), 400
           
    if hasattr(current_app, 'api_metrics'):
        platform = platform.upper()
        if platform in current_app.api_metrics:
            metrics_collector = current_app.api_metrics[platform]
            if metrics_collector:
                metrics = {
                    'summary': metrics_collector.get_summary(),
                    'request_rate': metrics_collector.get_request_rate(window=300),  # Last 5 minutes
                    'error_rate': metrics_collector.get_error_rate(window=3600),  # Last hour
                    'latency_trends': metrics_collector.get_latency_trends(platform, window=86400, buckets=24)  # Last 24h
                }
                
                return jsonify({
                    'platform': platform,
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                })
                
    return jsonify({
        'error': f'No metrics found for platform: {platform}'
    }), 404