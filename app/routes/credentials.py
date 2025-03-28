"""
API routes for credential management.
"""
from flask import Blueprint, jsonify, request, current_app, render_template
from app.utils.credentials import credential_manager
from app.utils.key_rotation import check_credentials_validity, rotate_meta_token, key_rotation_manager
from app.utils.api_debug import api_diagnostic_tool, test_api_connections, get_api_logs
from app.utils.secure_storage import get_secure_storage

credentials_bp = Blueprint('credentials', __name__, url_prefix='/credentials')
credentials_api_bp = Blueprint('credentials_api', __name__, url_prefix='/api/credentials')

# Create secure storage for credentials
credential_storage = get_secure_storage(storage_type='temp', use_encryption=True)

@credentials_bp.route('/')
def credentials_dashboard():
    """Credentials management dashboard."""
    # Get credential health
    credential_health = check_credentials_validity()
    
    # Get API connection status
    connection_results = test_api_connections()
    
    # Get rotation history
    rotation_history = key_rotation_manager.get_rotation_history()
    
    # Mask sensitive values for display
    meta_creds = credential_manager.get_credentials('META')
    google_creds = credential_manager.get_credentials('GOOGLE')
    twitter_creds = credential_manager.get_credentials('TWITTER')
    
    masked_creds = {
        'META': {
            k: credential_manager.mask_value(v) for k, v in meta_creds.items()
        },
        'GOOGLE': {
            k: credential_manager.mask_value(v) for k, v in google_creds.items()
        },
        'TWITTER': {
            k: credential_manager.mask_value(v) for k, v in twitter_creds.items()
        }
    }
    
    return render_template('credentials/dashboard.html',
                          credentials=masked_creds,
                          health=credential_health,
                          connections=connection_results,
                          rotation_history=rotation_history)

@credentials_bp.route('/rotate/<platform>/<credential_key>', methods=['POST'])
def rotate_credential(platform, credential_key):
    """Rotate a specific credential."""
    # Check for valid rotation request
    if platform == 'META' and credential_key == 'META_ACCESS_TOKEN':
        result = rotate_meta_token()
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Meta access token rotated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 400
    
    return jsonify({
        'success': False,
        'error': f'Rotation not supported for {platform}/{credential_key}'
    }), 400

@credentials_bp.route('/test/<platform>', methods=['POST'])
def test_connection(platform):
    """Test connection to a specific platform."""
    if platform == 'meta':
        result = api_diagnostic_tool.test_meta_api_connection()
    elif platform == 'twitter':
        result = api_diagnostic_tool.test_twitter_api_connection()
    elif platform == 'google':
        result = api_diagnostic_tool.test_google_api_connection()
    else:
        return jsonify({
            'success': False,
            'error': f'Unknown platform: {platform}'
        }), 400
    
    return jsonify(result)

@credentials_bp.route('/logs/<platform>')
def view_logs(platform):
    """View API logs for a specific platform."""
    # Get logs for the platform
    logs = get_api_logs(platform.upper())
    
    return render_template('credentials/logs.html',
                          platform=platform,
                          logs=logs)

# API endpoints for credential management
@credentials_api_bp.route('/health')
def get_credentials_health():
    """API endpoint to get credential health status."""
    # Check API key for security
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != current_app.config.get('API_ADMIN_KEY', 'dev-admin-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get credential health status
    credential_health = check_credentials_validity()
    
    # Mask sensitive values
    for platform in credential_health:
        if isinstance(credential_health[platform], dict) and 'token' in credential_health[platform]:
            credential_health[platform]['token'] = credential_manager.mask_value(
                credential_health[platform]['token']
            )
    
    return jsonify({
        'status': 'success',
        'credential_health': credential_health
    })

@credentials_api_bp.route('/rotate', methods=['POST'])
def api_rotate_credential():
    """API endpoint to rotate credentials."""
    # Check API key for security
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != current_app.config.get('API_ADMIN_KEY', 'dev-admin-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    platform = request.json.get('platform')
    credential_key = request.json.get('credential_key')
    
    if platform == 'META' and credential_key == 'META_ACCESS_TOKEN':
        result = rotate_meta_token()
        return jsonify({
            'status': 'success' if result.get('success') else 'error',
            'message': 'Meta token rotated successfully' if result.get('success') else result.get('error'),
            'result': result
        })
    
    return jsonify({
        'status': 'error',
        'message': f'Rotation not supported for {platform}/{credential_key}'
    }), 400

@credentials_api_bp.route('/test', methods=['POST'])
def api_test_connections():
    """API endpoint to test API connections."""
    # Check API key for security
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != current_app.config.get('API_ADMIN_KEY', 'dev-admin-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    platform = request.json.get('platform')
    
    # Test a specific platform or all platforms
    if platform:
        if platform.upper() in ['META', 'GOOGLE', 'TWITTER']:
            result = getattr(api_diagnostic_tool, f'test_{platform.lower()}_api_connection')()
            return jsonify({
                'status': 'success',
                'result': result
            })
        return jsonify({
            'status': 'error',
            'message': f'Unknown platform: {platform}'
        }), 400
    else:
        # Test all platforms
        test_results = test_api_connections()
        return jsonify({
            'status': 'success',
            'results': test_results
        })

@credentials_api_bp.route('/logs', methods=['GET'])
def api_get_logs():
    """API endpoint to get API logs."""
    # Check API key for security
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != current_app.config.get('API_ADMIN_KEY', 'dev-admin-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    platform = request.args.get('platform')
    limit = int(request.args.get('limit', 20))
    
    # Get API logs
    logs = get_api_logs(platform, limit)
    
    return jsonify({
        'status': 'success',
        'logs': logs
    })

@credentials_api_bp.route('/rotation-history', methods=['GET'])
def api_get_rotation_history():
    """API endpoint to get credential rotation history."""
    # Check API key for security
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != current_app.config.get('API_ADMIN_KEY', 'dev-admin-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get rotation history
    rotation_history = key_rotation_manager.get_rotation_history()
    
    return jsonify({
        'status': 'success',
        'rotation_history': rotation_history
    })

@credentials_api_bp.route('/revert-rotation', methods=['POST'])
def api_revert_rotation():
    """API endpoint to revert a credential rotation."""
    # Check API key for security
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != current_app.config.get('API_ADMIN_KEY', 'dev-admin-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    rotation_key = request.json.get('rotation_key')
    
    if not rotation_key:
        return jsonify({
            'status': 'error',
            'message': 'Rotation key is required'
        }), 400
    
    # Revert the rotation
    result = key_rotation_manager.revert_rotation(rotation_key)
    
    return jsonify({
        'status': 'success' if result.get('success') else 'error',
        'message': f"Rotation reverted successfully for {result.get('platform')}/{result.get('key')}" if result.get('success') else result.get('error'),
        'result': result
    })