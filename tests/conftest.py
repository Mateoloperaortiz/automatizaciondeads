import pytest
import os
import sys
from unittest.mock import MagicMock
from tests.test_utils import mock_api_module, setup_mock_routes
from flask import Flask
from flask_restful import Api

# Mock the api module before importing app
mock_api = mock_api_module()

# Now import app modules
from app import db
from app.models.job_opening import JobOpening
from app.models.candidate import Candidate
from app.models.ad_campaign import AdCampaign
from app.models.segment import Segment

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a Flask app with test configuration
    # Skip the automatic create_all from create_app because it's causing issues
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'USE_API_FRAMEWORK': True,
        'API_FRAMEWORK_PLATFORMS': ['meta', 'twitter', 'google'],
        'META_API_SIMULATE': True,
        'TWITTER_API_SIMULATE': True,
        'GOOGLE_API_SIMULATE': True,
    })
    
    # Initialize extensions
    db.init_app(app)
    
    # Set up mock routes for testing
    setup_mock_routes(app, db)
    
    # Create the database and tables explicitly
    with app.app_context():
        db.create_all()
        
        # Create test data
        yield app
        
        # Clean up after the test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()

@pytest.fixture
def sample_job_opening(db_session):
    """Create a sample job opening for testing."""
    job = JobOpening(
        title="Software Engineer",
        description="Python developer with Flask experience",
        location="Remote",
        company="Test Company",
        salary_range="$80,000 - $100,000",
        requirements="3+ years of Python experience",
        job_type="Full-time",  # Required field
        experience_level="Mid-level"  # Optional field
    )
    db_session.add(job)
    db_session.commit()
    return job

@pytest.fixture
def sample_candidates(db_session):
    """Create sample candidates for testing."""
    candidates = []
    for i in range(10):
        # Use the actual field names from the Candidate model
        candidate = Candidate(
            age=25 + i,
            gender="Male" if i % 2 == 0 else "Female",
            location="Remote" if i % 3 == 0 else "New York" if i % 3 == 1 else "San Francisco",
            education_level="Bachelor's" if i % 2 == 0 else "Master's",
            field_of_study="Computer Science",
            years_of_experience=2 + i,
            desired_job_type="Full-time",
            desired_industry="Technology",
            desired_role="Software Engineer" if i % 2 == 0 else "Data Scientist",
            desired_salary=80000 + (i * 10000)
        )
        db_session.add(candidate)
        candidates.append(candidate)
    
    db_session.commit()
    return candidates 