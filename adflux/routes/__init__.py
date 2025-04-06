# This file makes the 'routes' directory a Python package

# Import namespaces to make them available via `from adflux.routes import ...`
from .job_routes import jobs_ns
from .candidate_routes import candidates_ns
from .application_routes import applications_ns
from .meta_routes import meta_ns

# Import blueprints
from .dashboard_routes import dashboard_bp
from .campaign_routes import campaign_bp
from .segmentation_routes import segmentation_bp
from .settings_routes import settings_bp
from .report_routes import report_bp
from .job_routes_web import job_bp
from .candidate_routes_web import candidate_bp
from .application_routes_web import application_bp
from .api_routes import api_bp

# Create a test namespace for API verification
from flask_restx import Namespace, Resource, fields, Api

# Create a root namespace for API information
root_ns = Namespace('', description='API Information')

api_info_model = root_ns.model('ApiInfo', {
    'name': fields.String(required=True, description='API name'),
    'version': fields.String(required=True, description='API version'),
    'description': fields.String(required=True, description='API description'),
    'documentation': fields.String(required=True, description='API documentation URL')
})

@root_ns.route('/')
class ApiInfoResource(Resource):
    @root_ns.doc('api_info')
    @root_ns.marshal_with(api_info_model)
    def get(self):
        """Get API information"""
        return {
            'name': 'AdFlux API',
            'version': '1.0',
            'description': 'API for managing job openings and candidates',
            'documentation': '/api/docs/'
        }

# Create a test namespace for API verification
test_ns = Namespace('test', description='Test API operations')

test_model = test_ns.model('Test', {
    'message': fields.String(required=True, description='Test message')
})

@test_ns.route('/')
class TestResource(Resource):
    @test_ns.doc('test_get')
    @test_ns.marshal_with(test_model)
    def get(self):
        """Test API endpoint"""
        return {'message': 'API is working!'}

# Define __all__ for wildcard imports
__all__ = [
    # Namespaces
    'jobs_ns',
    'candidates_ns',
    'applications_ns',
    'meta_ns',
    'root_ns',
    'test_ns',

    # Blueprints
    'dashboard_bp',
    'campaign_bp',
    'segmentation_bp',
    'settings_bp',
    'report_bp',
    'job_bp',
    'candidate_bp',
    'application_bp',
    'api_bp'
]
