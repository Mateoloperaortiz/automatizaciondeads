from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_login import LoginManager
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
api = Api()
login = LoginManager()

# WebSocket will be initialized later to avoid circular imports
socketio = None

def create_app(config=None):
    """Create and configure the Flask application."""
    # Initialize credential system before creating app
    from app.utils.credentials import credential_manager
    from app.utils.config import config_manager

    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Apply any provided configuration
    if config is not None:
        app.config.update(config)
        
        # Fix database path to avoid instance/instance/... issues
        if 'SQLALCHEMY_DATABASE_URI' in config and 'sqlite:///' in config['SQLALCHEMY_DATABASE_URI']:
            # Correct the path to avoid instance duplication
            # If the path has instance/ in it but not absolute, make it absolute
            # The URI should be like 'sqlite:///path/to/file.db' not 'sqlite:///instance/instance/...'
            db_path = config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if db_path.startswith('instance/'):
                app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
            else:
                app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.instance_path}/{db_path}'
    
    # Configure the app with our custom configuration manager
    config_manager.init_app(app)
    
    # Register extensions
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    
    # Configure Flask-Login
    login.init_app(app)
    login.login_view = 'auth.login'
    login.login_message = 'Please log in to access this page.'
    login.login_message_category = 'info'
    
    # Initialize API Framework if enabled
    if app.config.get('USE_API_FRAMEWORK', False):
        app.logger.info("API Framework is enabled")
        
        # Import API Framework components
        from app.api_framework import (
            MetaAPIClient, TwitterAPIClient, GoogleAPIClient, 
            APIFrameworkCampaignManager
        )
        
        # Initialize API clients
        app.meta_client = MetaAPIClient(
            credential_manager.get_credentials('META'),
            enable_cache=app.config.get('COLLECT_API_METRICS', True)
        )
        
        app.twitter_client = TwitterAPIClient(
            credential_manager.get_credentials('TWITTER'),
            enable_cache=app.config.get('COLLECT_API_METRICS', True)
        )
        
        app.google_client = GoogleAPIClient(
            credential_manager.get_credentials('GOOGLE'),
            enable_cache=app.config.get('COLLECT_API_METRICS', True)
        )
        
        # Register metrics collectors if enabled
        if app.config.get('COLLECT_API_METRICS', True):
            app.api_metrics = {
                'META': app.meta_client.metrics,
                'TWITTER': app.twitter_client.metrics,
                'GOOGLE': app.google_client.metrics
            }
            app.logger.info("API Metrics collection is enabled")
        
        # Create framework campaign manager if all platforms are enabled
        platforms = app.config.get('API_FRAMEWORK_PLATFORMS', [])
        app.logger.info(f"API Framework enabled for platforms: {platforms}")
        
        # Register the campaign manager if all platforms are enabled
        if set(platforms) >= {'meta', 'twitter', 'google'}:
            app.framework_campaign_manager = APIFrameworkCampaignManager()
            app.logger.info("Framework Campaign Manager initialized")
    else:
        app.logger.info("API Framework is disabled")
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.job_openings import job_openings_bp
    from app.routes.candidates import candidates_bp
    from app.routes.campaigns import campaigns_bp
    from app.routes.segments import segments_bp, segments_api_bp
    from app.routes.analytics import analytics_bp
    from app.routes.ads import ads_bp
    from app.routes.segmentation import segmentation_bp
    from app.routes.credentials import credentials_bp, credentials_api_bp
    from app.routes.notifications import notifications_bp
    from app.routes.alerts import alerts_bp
    from app.routes.auth import auth_bp
    from app.routes.teams import teams_bp
    from app.routes.docs import docs_bp
    from app.routes.websocket import websocket_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(job_openings_bp)
    app.register_blueprint(candidates_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(segments_bp)
    app.register_blueprint(segments_api_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(ads_bp)
    app.register_blueprint(segmentation_bp)
    app.register_blueprint(credentials_bp)
    app.register_blueprint(credentials_api_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(websocket_bp)
    
    # Register API Framework routes if enabled
    if app.config.get('USE_API_FRAMEWORK', False):
        from app.routes.publish_api_framework import publish_api_framework_bp
        from app.routes.api_metrics import api_metrics_bp
        
        app.register_blueprint(publish_api_framework_bp)
        app.register_blueprint(api_metrics_bp)
        app.logger.info("Registered API Framework routes")
    
    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    # Create tables in context (new way instead of before_first_request)
    with app.app_context():
        db.create_all()
    
    # Import models to ensure they're loaded
    from app.models import job_opening, ad_campaign, candidate, segment, notification, alert, user, documentation
    
    # Configure user loader for Flask-Login
    @login.user_loader
    def load_user(user_id):
        return user.User.query.get(int(user_id))
    
    # Configure logging
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Set up file handler
        file_handler = RotatingFileHandler('logs/ad_automation.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        
        # Add handler to app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Ad Automation startup')
    
    # Add a template filter for number formatting
    @app.template_filter('number_format')
    def number_format_filter(value, precision=0):
        """Format a number with thousands separators."""
        if value is None:
            return '0'
        if precision:
            return f"{value:,.{precision}f}"
        return f"{value:,}"
    
    # Add a context processor to make configuration available in templates
    @app.context_processor
    def inject_configuration():
        """Make configuration available in templates."""
        return {
            'env': app.config.get('ENVIRONMENT', 'development'),
            'is_development': app.config.get('IS_DEVELOPMENT', True),
            'is_testing': app.config.get('IS_TESTING', False),
            'is_staging': app.config.get('IS_STAGING', False),
            'is_production': app.config.get('IS_PRODUCTION', False),
        }
    
    # Register our custom context processors
    from app.context_processors import register_context_processors
    register_context_processors(app)
    
    # Register credential and API health route
    @app.route('/api/health/credentials')
    def api_credentials_health():
        """API endpoint to check credential health status."""
        from app.utils.key_rotation import check_credentials_validity
        from app.utils.credentials import credential_manager
        from flask import jsonify
        
        # Check if request has API key for security
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != app.config.get('API_HEALTH_KEY', 'dev-health-key'):
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get credential health
        credential_health = check_credentials_validity()
        
        # Mask sensitive values
        for platform in credential_health:
            if isinstance(credential_health[platform], dict) and 'token' in credential_health[platform]:
                credential_health[platform]['token'] = credential_manager.mask_value(
                    credential_health[platform]['token']
                )
        
        return jsonify({
            'status': 'ok',
            'credential_health': credential_health
        })
    
    # Initialize SocketIO
    from app.routes.websocket import initialize_socketio, socketio as app_socketio
    global socketio
    socketio = initialize_socketio(app)
    app.logger.info("WebSocket server initialized")
    
    # Register Celery tasks
    with app.app_context():
        import app.tasks
    
    return app