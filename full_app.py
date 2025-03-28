import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import logging
from datetime import datetime, timedelta
import json
import secrets
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Flask app
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

# Configure the database with absolute path
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance', 'ad_automation.sqlite'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define User model for authentication
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    
    # Required for Flask-Login
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return str(self.id)
        
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import our fixed Document model
class Document(db.Model):
    """
    Model representing a documentation page/section.
    Each document has multiple versions for tracking history.
    """
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    doc_type = db.Column(db.String(20), nullable=False, default='general')
    parent_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    order = db.Column(db.Integer, default=0)  # For ordering within sections
    status = db.Column(db.String(20), nullable=False, default='draft')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # SEO and metadata as JSON
    document_metadata = db.Column(db.Text, nullable=True)
    
    # Relationships
    creator = db.relationship('User', backref='created_documents')
    children = db.relationship('Document', backref=db.backref('parent', remote_side=[id]))
    
    def __repr__(self):
        return f'<Document {self.title}>'
    
    def get_metadata(self):
        """Get document metadata as a dictionary."""
        if not self.document_metadata:
            return {}
        try:
            return json.loads(self.document_metadata)
        except:
            return {}
    
    def set_metadata(self, metadata_dict):
        """Set document metadata from a dictionary."""
        self.document_metadata = json.dumps(metadata_dict)
    
    def update_metadata(self, key, value):
        """Update a single metadata field."""
        metadata = self.get_metadata()
        metadata[key] = value
        self.set_metadata(metadata)
    
    def to_dict(self, include_content=False):
        """Convert document to dictionary."""
        result = {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'doc_type': self.doc_type,
            'parent_id': self.parent_id,
            'order': self.order,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata': self.get_metadata(),
        }
        
        return result

# Define Campaign model
class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='draft')
    budget = db.Column(db.Float, default=0.0)
    platform = db.Column(db.String(50), default='all')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='created_campaigns')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'budget': self.budget,
            'platform': self.platform,
            'created_by': self.created_by
        }

# Define Segment model for audience segmentation
class Segment(db.Model):
    __tablename__ = 'segments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    criteria = db.Column(db.Text)  # JSON stored as text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='created_segments')
    
    def get_criteria(self):
        if not self.criteria:
            return {}
        try:
            return json.loads(self.criteria)
        except:
            return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'criteria': self.get_criteria(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        # For demo purposes, allow any login
        if not user:
            user = User(username=username, email=f"{username}@example.com", is_admin=True)
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
        
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # For simplicity, don't require login
    campaigns = Campaign.query.all()
    segments = Segment.query.all()
    
    # Create mock data for dashboard charts
    platform_names = ['Meta', 'Google', 'Twitter']
    impressions_data = [45000, 32000, 28000]
    clicks_data = [2100, 1450, 1200]
    applications_data = [85, 62, 48]
    
    # Add job and segment counts for stats cards
    job_count = 24
    candidate_count = 1250
    
    return render_template('dashboard/simple_dashboard.html', 
                         campaigns=campaigns, 
                         segments=segments,
                         platform_names=platform_names,
                         impressions_data=impressions_data,
                         clicks_data=clicks_data,
                         applications_data=applications_data,
                         job_count=job_count,
                         candidate_count=candidate_count)

@app.route('/analytics')
def analytics():
    # Create a more detailed analytics page
    campaigns = Campaign.query.all()
    segments = Segment.query.all()
    
    # Mock data for platform performance
    platforms = [
        {'name': 'Meta', 'impressions': 450000, 'clicks': 22500, 'conversions': 720, 'ctr': 5.0, 'roi': 142},
        {'name': 'Google', 'impressions': 320000, 'clicks': 12800, 'conversions': 510, 'ctr': 4.0, 'roi': 128},
        {'name': 'X', 'impressions': 280000, 'clicks': 8400, 'conversions': 420, 'ctr': 3.0, 'roi': 115},
        {'name': 'LinkedIn', 'impressions': 210000, 'clicks': 10500, 'conversions': 630, 'ctr': 5.0, 'roi': 168},
        {'name': 'TikTok', 'impressions': 180000, 'clicks': 9000, 'conversions': 380, 'ctr': 5.0, 'roi': 105}
    ]
    
    # Create a custom analytics template on the fly if it doesn't exist
    os.makedirs(os.path.join(app.template_folder, 'analytics'), exist_ok=True)
    analytics_template = os.path.join(app.template_folder, 'analytics', 'index.html')
    
    if not os.path.exists(analytics_template):
        with open(analytics_template, 'w') as f:
            f.write("""{% extends "simple_base.html" %}

{% block title %}Analytics Dashboard | MagnetoCursor{% endblock %}

{% block content %}
<div class="analytics-dashboard mb-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="page-title mb-1">Campaign Analytics</h1>
            <p class="text-muted">Track performance metrics across all platforms and campaigns</p>
        </div>
        <div class="d-flex">
            <div class="date-range me-2">
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-calendar3"></i></span>
                    <select class="form-select">
                        <option>Last 7 days</option>
                        <option selected>Last 30 days</option>
                        <option>Last 90 days</option>
                        <option>Year to date</option>
                        <option>Custom range</option>
                    </select>
                </div>
            </div>
            <div class="btn-group">
                <button class="btn btn-outline-primary"><i class="bi bi-download"></i> Export</button>
                <button class="btn btn-outline-primary"><i class="bi bi-gear"></i></button>
            </div>
        </div>
    </div>
    
    <!-- KPI Summary Cards -->
    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card kpi-card border-0 h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="icon-circle bg-primary-light me-3">
                            <i class="bi bi-eye text-primary"></i>
                        </div>
                        <h6 class="card-subtitle text-muted mb-0">Total Impressions</h6>
                    </div>
                    <h2 class="mb-2 fw-bold">1.54M</h2>
                    <div class="trend up">
                        <i class="bi bi-graph-up-arrow"></i> 12.3% from previous period
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card kpi-card border-0 h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="icon-circle bg-success-light me-3">
                            <i class="bi bi-cursor text-success"></i>
                        </div>
                        <h6 class="card-subtitle text-muted mb-0">Click-Through Rate</h6>
                    </div>
                    <h2 class="mb-2 fw-bold">4.8%</h2>
                    <div class="trend up">
                        <i class="bi bi-graph-up-arrow"></i> 0.5% from previous period
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card kpi-card border-0 h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="icon-circle bg-warning-light me-3">
                            <i class="bi bi-arrow-repeat text-warning"></i>
                        </div>
                        <h6 class="card-subtitle text-muted mb-0">Conversion Rate</h6>
                    </div>
                    <h2 class="mb-2 fw-bold">2.3%</h2>
                    <div class="trend down">
                        <i class="bi bi-graph-down-arrow"></i> 0.2% from previous period
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card kpi-card border-0 h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="icon-circle bg-info-light me-3">
                            <i class="bi bi-currency-dollar text-info"></i>
                        </div>
                        <h6 class="card-subtitle text-muted mb-0">Cost per Conversion</h6>
                    </div>
                    <h2 class="mb-2 fw-bold">$24.82</h2>
                    <div class="trend down positive">
                        <i class="bi bi-graph-down-arrow"></i> $1.47 from previous period
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Performance Over Time -->
    <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
            <h5 class="fw-semibold mb-0">Performance Over Time</h5>
            <div class="chart-actions">
                <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-primary active">Impressions</button>
                    <button type="button" class="btn btn-outline-primary">Clicks</button>
                    <button type="button" class="btn btn-outline-primary">Conversions</button>
                </div>
            </div>
        </div>
        <div class="card-body">
            <canvas id="performanceChart" height="280"></canvas>
        </div>
    </div>
    
    <!-- Platform Comparison -->
    <div class="row g-4 mb-4">
        <div class="col-lg-7">
            <div class="card border-0 shadow-sm h-100">
                <div class="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
                    <h5 class="fw-semibold mb-0">Platform Comparison</h5>
                    <button class="btn btn-sm btn-outline-primary"><i class="bi bi-filter"></i> Filter</button>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle platform-table">
                            <thead class="table-light">
                                <tr>
                                    <th scope="col">Platform</th>
                                    <th scope="col">Budget</th>
                                    <th scope="col">Impressions</th>
                                    <th scope="col">CTR</th>
                                    <th scope="col">Conv. Rate</th>
                                    <th scope="col">ROI</th>
                                    <th scope="col">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for platform in platforms %}
                                <tr>
                                    <td>
                                        <div class="d-flex align-items-center">
                                            <div class="platform-icon me-2">
                                                {% if platform.name == 'Meta' %}
                                                <i class="bi bi-facebook"></i>
                                                {% elif platform.name == 'Google' %}
                                                <i class="bi bi-google"></i>
                                                {% elif platform.name == 'X' %}
                                                <i class="bi bi-twitter-x"></i>
                                                {% elif platform.name == 'LinkedIn' %}
                                                <i class="bi bi-linkedin"></i>
                                                {% elif platform.name == 'TikTok' %}
                                                <i class="bi bi-tiktok"></i>
                                                {% endif %}
                                            </div>
                                            <span>{{ platform.name }}</span>
                                        </div>
                                    </td>
                                    <td>${{ platform.impressions // 100 }}.00</td>
                                    <td>{{ '{:,}'.format(platform.impressions) }}</td>
                                    <td>{{ platform.ctr }}%</td>
                                    <td>{{ (platform.conversions / platform.clicks * 100) | round(1) }}%</td>
                                    <td><span class="text-success fw-semibold">{{ platform.roi }}%</span></td>
                                    <td><span class="badge bg-success">Active</span></td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-lg-5">
            <div class="card border-0 shadow-sm h-100">
                <div class="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
                    <h5 class="fw-semibold mb-0">ROI by Platform</h5>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-outline-primary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            This Month
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="#">This Month</a></li>
                            <li><a class="dropdown-item" href="#">Last Month</a></li>
                            <li><a class="dropdown-item" href="#">This Quarter</a></li>
                            <li><a class="dropdown-item" href="#">Custom Range</a></li>
                        </ul>
                    </div>
                </div>
                <div class="card-body d-flex align-items-center">
                    <canvas id="roiChart"></canvas>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Segment Performance -->
    <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
            <h5 class="fw-semibold mb-0">Audience Segments Performance</h5>
            <div>
                <button class="btn btn-sm btn-outline-primary me-2"><i class="bi bi-filter"></i> Filter</button>
                <button class="btn btn-sm btn-primary"><i class="bi bi-plus-lg"></i> Create Segment</button>
            </div>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>Segment Name</th>
                            <th>Size</th>
                            <th>Impressions</th>
                            <th>CTR</th>
                            <th>Conv. Rate</th>
                            <th>CPC</th>
                            <th>ROI</th>
                            <th class="text-end">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="segment-icon bg-primary-light me-2">TP</div>
                                    <span>Tech Professionals</span>
                                </div>
                            </td>
                            <td>532,450</td>
                            <td>428,120</td>
                            <td>5.2%</td>
                            <td>3.1%</td>
                            <td>$1.82</td>
                            <td><span class="text-success fw-semibold">148%</span></td>
                            <td class="text-end">
                                <button class="btn btn-sm btn-outline-primary me-1"><i class="bi bi-bar-chart"></i></button>
                                <button class="btn btn-sm btn-outline-secondary"><i class="bi bi-three-dots"></i></button>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="segment-icon bg-success-light me-2">RG</div>
                                    <span>Recent Graduates</span>
                                </div>
                            </td>
                            <td>321,780</td>
                            <td>278,540</td>
                            <td>4.7%</td>
                            <td>2.5%</td>
                            <td>$1.62</td>
                            <td><span class="text-success fw-semibold">128%</span></td>
                            <td class="text-end">
                                <button class="btn btn-sm btn-outline-primary me-1"><i class="bi bi-bar-chart"></i></button>
                                <button class="btn btn-sm btn-outline-secondary"><i class="bi bi-three-dots"></i></button>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="segment-icon bg-warning-light me-2">CP</div>
                                    <span>Creative Professionals</span>
                                </div>
                            </td>
                            <td>184,320</td>
                            <td>148,950</td>
                            <td>5.8%</td>
                            <td>2.9%</td>
                            <td>$1.94</td>
                            <td><span class="text-success fw-semibold">142%</span></td>
                            <td class="text-end">
                                <button class="btn btn-sm btn-outline-primary me-1"><i class="bi bi-bar-chart"></i></button>
                                <button class="btn btn-sm btn-outline-secondary"><i class="bi bi-three-dots"></i></button>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="segment-icon bg-info-light me-2">RW</div>
                                    <span>Remote Workers</span>
                                </div>
                            </td>
                            <td>428,760</td>
                            <td>352,480</td>
                            <td>6.1%</td>
                            <td>3.4%</td>
                            <td>$1.76</td>
                            <td><span class="text-success fw-semibold">168%</span></td>
                            <td class="text-end">
                                <button class="btn btn-sm btn-outline-primary me-1"><i class="bi bi-bar-chart"></i></button>
                                <button class="btn btn-sm btn-outline-secondary"><i class="bi bi-three-dots"></i></button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Campaign Performance -->
    <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
            <h5 class="fw-semibold mb-0">Campaign Performance</h5>
            <div>
                <button class="btn btn-sm btn-outline-primary me-2"><i class="bi bi-filter"></i> Filter</button>
                <button class="btn btn-sm btn-primary"><i class="bi bi-plus-lg"></i> New Campaign</button>
            </div>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>Campaign</th>
                            <th>Status</th>
                            <th>Platform</th>
                            <th>Budget</th>
                            <th>Spend</th>
                            <th>Impressions</th>
                            <th>CTR</th>
                            <th>Conv.</th>
                            <th>CPA</th>
                            <th class="text-end">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for campaign in campaigns[:4] %}
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="campaign-icon bg-primary-light me-2">
                                        {% set initials = campaign.name.split(' ')|map('first')|join('')|upper %}
                                        {{ initials[:2] }}
                                    </div>
                                    <div>
                                        <div class="fw-medium">{{ campaign.name }}</div>
                                        <div class="small text-muted">ID: {{ campaign.id }}</div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                {% if campaign.status == 'active' %}
                                <span class="badge bg-success">Active</span>
                                {% elif campaign.status == 'paused' %}
                                <span class="badge bg-warning">Paused</span>
                                {% elif campaign.status == 'draft' %}
                                <span class="badge bg-secondary">Draft</span>
                                {% else %}
                                <span class="badge bg-secondary">{{ campaign.status|capitalize }}</span>
                                {% endif %}
                            </td>
                            <td>{{ campaign.platform }}</td>
                            <td>${{ (campaign.budget|float) }}</td>
                            <td>${{ (campaign.budget|float * 0.7)|round(2) }}</td>
                            <td>{{ (campaign.budget|float * 25000)|int|format_number }}</td>
                            <td>{{ (3 + (loop.index / 10))|round(1) }}%</td>
                            <td>{{ (campaign.budget|float * 5)|int }}</td>
                            <td>${{ (campaign.budget|float * 0.7 / (campaign.budget|float * 5))|round(2) * 100 }}</td>
                            <td class="text-end">
                                <button class="btn btn-sm btn-outline-primary me-1"><i class="bi bi-bar-chart"></i></button>
                                <div class="btn-group">
                                    <button type="button" class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                    <ul class="dropdown-menu dropdown-menu-end">
                                        <li><a class="dropdown-item" href="#"><i class="bi bi-pencil me-2"></i>Edit</a></li>
                                        <li><a class="dropdown-item" href="#"><i class="bi bi-eye me-2"></i>View</a></li>
                                        <li><a class="dropdown-item" href="#"><i class="bi bi-pause me-2"></i>Pause</a></li>
                                        <li><hr class="dropdown-divider"></li>
                                        <li><a class="dropdown-item text-danger" href="#"><i class="bi bi-trash me-2"></i>Delete</a></li>
                                    </ul>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        <div class="card-footer bg-white border-0 text-center py-3">
            <a href="#" class="btn btn-outline-primary">View All Campaigns <i class="bi bi-arrow-right ms-1"></i></a>
        </div>
    </div>
    
    <!-- Insights & Recommendations -->
    <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white border-0 py-3">
            <h5 class="fw-semibold mb-0">AI-Powered Insights & Recommendations</h5>
        </div>
        <div class="card-body">
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="insight-card">
                        <div class="insight-icon bg-primary-light">
                            <i class="bi bi-lightbulb text-primary"></i>
                        </div>
                        <h6 class="insight-title">Performance Insight</h6>
                        <p>Your tech professionals segment shows 24% higher engagement on weekdays between 10 AM and 2 PM.</p>
                        <div class="mt-auto">
                            <button class="btn btn-sm btn-outline-primary">Optimize Schedule</button>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="insight-card">
                        <div class="insight-icon bg-success-light">
                            <i class="bi bi-graph-up-arrow text-success"></i>
                        </div>
                        <h6 class="insight-title">Budget Recommendation</h6>
                        <p>Reallocate 15% of Google budget to LinkedIn for higher ROI based on last 30 days performance.</p>
                        <div class="mt-auto">
                            <button class="btn btn-sm btn-outline-primary">Apply Recommendation</button>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="insight-card">
                        <div class="insight-icon bg-warning-light">
                            <i class="bi bi-bullseye text-warning"></i>
                        </div>
                        <h6 class="insight-title">Audience Insight</h6>
                        <p>Create a new segment targeting mid-career professionals with 5-10 years experience for DevOps roles.</p>
                        <div class="mt-auto">
                            <button class="btn btn-sm btn-outline-primary">Create Segment</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        Chart.defaults.font.family = "'Inter', 'Helvetica', 'Arial', sans-serif";
        Chart.defaults.color = '#6c757d';
        
        // Performance Over Time Chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: ['Mar 1', 'Mar 5', 'Mar 10', 'Mar 15', 'Mar 20', 'Mar 25', 'Mar 30'],
                datasets: [{
                    label: 'Impressions',
                    data: [45000, 52000, 48000, 61000, 58000, 63000, 68000],
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#4361ee',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.7)',
                        padding: 10,
                        titleFont: {
                            size: 14,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13
                        },
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return 'Impressions: ' + context.raw.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            drawBorder: false,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value >= 1000 ? value / 1000 + 'k' : value;
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
        
        // ROI Chart
        const roiCtx = document.getElementById('roiChart').getContext('2d');
        new Chart(roiCtx, {
            type: 'doughnut',
            data: {
                labels: ['Meta', 'Google', 'X', 'LinkedIn', 'TikTok'],
                datasets: [{
                    data: [142, 128, 115, 168, 105],
                    backgroundColor: [
                        '#4361ee',
                        '#3a0ca3',
                        '#4cc9f0',
                        '#4895ef',
                        '#560bad'
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.7)',
                        padding: 10,
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.raw + '% ROI';
                            }
                        }
                    }
                }
            }
        });
    });
</script>
{% endblock %}

{% block styles %}
<style>
    :root {
        --primary: #4361ee;
        --primary-light: rgba(67, 97, 238, 0.1);
        --success: #2ec4b6;
        --success-light: rgba(46, 196, 182, 0.1);
        --warning: #ff9f1c;
        --warning-light: rgba(255, 159, 28, 0.1);
        --danger: #e71d36;
        --danger-light: rgba(231, 29, 54, 0.1);
        --info: #4cc9f0;
        --info-light: rgba(76, 201, 240, 0.1);
        --light-border: rgba(0, 0, 0, 0.08);
        --card-shadow: 0 0.125rem 0.375rem rgba(0, 0, 0, 0.05);
    }

    .page-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #212529;
    }
    
    /* KPI Cards */
    .kpi-card {
        box-shadow: var(--card-shadow);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.08);
    }
    
    .icon-circle {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        font-size: 1.25rem;
    }
    
    .bg-primary-light { background-color: var(--primary-light); }
    .bg-success-light { background-color: var(--success-light); }
    .bg-warning-light { background-color: var(--warning-light); }
    .bg-danger-light { background-color: var(--danger-light); }
    .bg-info-light { background-color: var(--info-light); }
    
    .text-primary { color: var(--primary) !important; }
    .text-success { color: var(--success) !important; }
    .text-warning { color: var(--warning) !important; }
    .text-danger { color: var(--danger) !important; }
    .text-info { color: var(--info) !important; }
    
    .trend {
        font-size: 0.85rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .trend.up {
        color: var(--success);
    }
    
    .trend.down {
        color: var(--danger);
    }
    
    .trend.down.positive {
        color: var(--success);
    }
    
    /* Cards */
    .card {
        box-shadow: var(--card-shadow);
        border-radius: 0.5rem;
        overflow: hidden;
    }
    
    .card-header {
        padding: 1rem 1.25rem;
        font-weight: 600;
    }
    
    /* Tables */
    .table {
        margin-bottom: 0;
    }
    
    .table thead th {
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 0.75rem 1rem;
    }
    
    .table tbody td {
        padding: 0.875rem 1rem;
        vertical-align: middle;
    }
    
    .platform-icon,
    .segment-icon,
    .campaign-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .segment-icon,
    .campaign-icon {
        font-size: 0.875rem;
    }
    
    /* Insight Cards */
    .insight-card {
        background-color: #fff;
        border-radius: 0.5rem;
        padding: 1.5rem;
        height: 100%;
        box-shadow: var(--card-shadow);
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .insight-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 12px;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .insight-title {
        font-weight: 600;
        font-size: 1.1rem;
        margin: 0;
    }
    
    .btn-outline-primary {
        border-color: var(--primary);
        color: var(--primary);
    }
    
    .btn-outline-primary:hover {
        background-color: var(--primary);
        border-color: var(--primary);
        color: white;
    }
    
    .btn-primary {
        background-color: var(--primary);
        border-color: var(--primary);
    }
    
    .btn-primary:hover {
        background-color: #3253e0;
        border-color: #3253e0;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .date-range-selector {
            width: 150px;
        }
        
        .insight-card {
            padding: 1.25rem;
        }
    }
</style>
{% endblock %}
""")
    
    # Mock data for platform performance
    platforms = [
        {'name': 'Meta', 'impressions': 450000, 'clicks': 22500, 'conversions': 720, 'ctr': 5.0, 'roi': 142},
        {'name': 'Google', 'impressions': 320000, 'clicks': 12800, 'conversions': 510, 'ctr': 4.0, 'roi': 128},
        {'name': 'X', 'impressions': 280000, 'clicks': 8400, 'conversions': 420, 'ctr': 3.0, 'roi': 115},
        {'name': 'LinkedIn', 'impressions': 210000, 'clicks': 10500, 'conversions': 630, 'ctr': 5.0, 'roi': 168},
        {'name': 'TikTok', 'impressions': 180000, 'clicks': 9000, 'conversions': 380, 'ctr': 5.0, 'roi': 105}
    ]
    
    return render_template('analytics/index.html', 
                          campaigns=campaigns,
                          segments=segments,
                          platforms=platforms,
                          connected_platforms=3,  # Mock data for connected platforms
                          total_platforms=5)      # Mock data for total platforms

@app.route('/campaigns')
def campaigns():
    # Get all campaigns
    all_campaigns = Campaign.query.all()
    
    # Simulate owned campaigns (in a real app, this would be filtered by user_id)
    owned_campaigns = all_campaigns[:2] if all_campaigns else []
    
    # Simulate shared campaigns (in a real app, this would come from a collaboration table)
    collaborating_campaigns = all_campaigns[2:] if len(all_campaigns) > 2 else []
    
    # Set is_admin for displaying the admin tab
    is_admin = True
    
    # Return the standard template with all required variables
    return render_template('campaigns/list.html',
                          owned_campaigns=owned_campaigns,
                          collaborating_campaigns=collaborating_campaigns,
                          all_campaigns=all_campaigns,
                          is_admin=is_admin,
                          connected_platforms=3,
                          total_platforms=5)

@app.route('/campaign/<int:campaign_id>')
def campaign_detail(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('campaigns/detail.html', campaign=campaign)

@app.route('/segments')
def segments():
    segments = Segment.query.all()
    
    # Add candidate_count attribute to each segment (mock data)
    for i, segment in enumerate(segments):
        # Create some variation in the counts
        segment.candidate_count = (i + 1) * 125 + (hash(segment.name) % 50)
        
        # Add traits from the segment description
        segment.traits = []
        if segment.description:
            traits_desc = segment.description.split(". ")
            for trait_desc in traits_desc[:3]:  # Get at most 3 traits
                if ":" in trait_desc:
                    name, value = trait_desc.split(":", 1)
                    segment.traits.append({"name": name.strip(), "value": value.strip()})
                else:
                    segment.traits.append({"name": "Characteristic", "value": trait_desc.strip()})
    
    # Prepare data for the chart visualization
    segment_names = [segment.name for segment in segments]
    segment_counts = [segment.candidate_count for segment in segments]
    
    # Return the standard template
    return render_template('dashboard/segments.html', 
                          segments=segments,
                          segment_names=segment_names,
                          segment_counts=segment_counts,
                          connected_platforms=3,
                          total_platforms=5)

@app.route('/segment/<int:segment_id>')
def segment_detail(segment_id):
    segment = Segment.query.get_or_404(segment_id)
    return render_template('dashboard/segment_detail.html', segment=segment)

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'database': {
            'path': db_path,
            'uri': app.config['SQLALCHEMY_DATABASE_URI'],
            'connected': True
        },
        'message': 'Application is running with SQLAlchemy fix applied!'
    })

@app.route('/api/documents')
def get_documents():
    documents = Document.query.all()
    return jsonify({
        'status': 'success',
        'count': len(documents),
        'documents': [doc.to_dict() for doc in documents]
    })

@app.route('/api/campaigns')
def get_campaigns():
    campaigns = Campaign.query.all()
    return jsonify({
        'status': 'success',
        'count': len(campaigns),
        'campaigns': [campaign.to_dict() for campaign in campaigns]
    })

@app.route('/api/segments')
def get_segments():
    segments = Segment.query.all()
    return jsonify({
        'status': 'success',
        'count': len(segments),
        'segments': [segment.to_dict() for segment in segments]
    })

@app.route('/api/campaign/analytics/<int:campaign_id>')
def get_campaign_analytics(campaign_id):
    """API endpoint to get campaign analytics data."""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Get date range from query parameters with defaults
    date_from = request.args.get('date_from', default=(datetime.utcnow() - timedelta(days=30)).isoformat())
    date_to = request.args.get('date_to', default=datetime.utcnow().isoformat())
    
    # Generate mock platform data (in a real app, this would come from the API clients)
    platforms = ['meta', 'google', 'twitter']
    
    # Simulate time series data
    time_series_data = {}
    for platform in platforms:
        time_series_data[platform] = {
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
        
        # Generate data for each day in range
        current_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Base metrics with random fluctuation
            base = 100 + (hash(platform + date_str) % 100)
            impressions = int(base * (50 + (hash(platform + 'imp' + date_str) % 50)))
            clicks = int(impressions * (0.01 + (hash(platform + 'click' + date_str) % 100) / 10000))
            conversions = int(clicks * (0.05 + (hash(platform + 'conv' + date_str) % 100) / 2000))
            spend = round(clicks * (0.5 + (hash(platform + 'spend' + date_str) % 100) / 100), 2)
            revenue = round(conversions * (10 + (hash(platform + 'rev' + date_str) % 100) / 10), 2)
            
            # Calculated metrics
            ctr = round((clicks / impressions) * 100, 2) if impressions > 0 else 0
            cpc = round(spend / clicks, 2) if clicks > 0 else 0
            cpa = round(spend / conversions, 2) if conversions > 0 else 0
            roi = round(((revenue - spend) / spend) * 100, 2) if spend > 0 else 0
            
            # Add to time series
            time_series_data[platform]['impressions'].append({'x': date_str, 'y': impressions})
            time_series_data[platform]['clicks'].append({'x': date_str, 'y': clicks})
            time_series_data[platform]['conversions'].append({'x': date_str, 'y': conversions})
            time_series_data[platform]['ctr'].append({'x': date_str, 'y': ctr})
            time_series_data[platform]['cpc'].append({'x': date_str, 'y': cpc})
            time_series_data[platform]['cpa'].append({'x': date_str, 'y': cpa})
            time_series_data[platform]['spend'].append({'x': date_str, 'y': spend})
            time_series_data[platform]['revenue'].append({'x': date_str, 'y': revenue})
            time_series_data[platform]['roi'].append({'x': date_str, 'y': roi})
            
            # Next day
            current_date += timedelta(days=1)
    
    # Aggregate platform metrics
    platform_metrics = {}
    for platform in platforms:
        # Generate platform-specific data
        base = 100 + (hash(platform + campaign.name) % 100)
        platform_metrics[platform] = {
            'impressions': int(base * (500 + (hash(platform + 'imp') % 500))),
            'clicks': int(base * (20 + (hash(platform + 'click') % 30))),
            'conversions': int(base * (1 + (hash(platform + 'conv') % 5))),
            'spend': round(base * (10 + (hash(platform + 'spend') % 20)), 2),
            'revenue': round(base * (20 + (hash(platform + 'rev') % 40)), 2)
        }
        
        # Calculate derived metrics
        if platform_metrics[platform]['impressions'] > 0:
            platform_metrics[platform]['ctr'] = round((platform_metrics[platform]['clicks'] / platform_metrics[platform]['impressions']) * 100, 2)
        else:
            platform_metrics[platform]['ctr'] = 0
            
        if platform_metrics[platform]['clicks'] > 0:
            platform_metrics[platform]['cpc'] = round(platform_metrics[platform]['spend'] / platform_metrics[platform]['clicks'], 2)
        else:
            platform_metrics[platform]['cpc'] = 0
            
        if platform_metrics[platform]['conversions'] > 0:
            platform_metrics[platform]['cpa'] = round(platform_metrics[platform]['spend'] / platform_metrics[platform]['conversions'], 2)
        else:
            platform_metrics[platform]['cpa'] = 0
            
        if platform_metrics[platform]['spend'] > 0:
            platform_metrics[platform]['roi'] = round(((platform_metrics[platform]['revenue'] - platform_metrics[platform]['spend']) / platform_metrics[platform]['spend']) * 100, 2)
        else:
            platform_metrics[platform]['roi'] = 0
    
    # Generate ROI data
    roi_data = {
        'overall': {
            'spend': sum(metrics['spend'] for metrics in platform_metrics.values()),
            'revenue': sum(metrics['revenue'] for metrics in platform_metrics.values()),
            'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values())
        },
        'platforms': platform_metrics
    }
    
    # Calculate overall ROI
    if roi_data['overall']['spend'] > 0:
        roi_data['overall']['roi'] = round(((roi_data['overall']['revenue'] - roi_data['overall']['spend']) / roi_data['overall']['spend']) * 100, 2)
    else:
        roi_data['overall']['roi'] = 0
    
    # Generate breakdown data
    roi_data['breakdowns'] = {
        'platform': [
            {
                'name': platform,
                'spend': metrics['spend'],
                'revenue': metrics['revenue'],
                'impressions': metrics['impressions'],
                'clicks': metrics['clicks'],
                'conversions': metrics['conversions']
            } for platform, metrics in platform_metrics.items()
        ],
        'ad_type': [
            {
                'name': 'Image',
                'spend': roi_data['overall']['spend'] * 0.4,
                'revenue': roi_data['overall']['revenue'] * 0.35,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.4,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.35,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.35
            },
            {
                'name': 'Video',
                'spend': roi_data['overall']['spend'] * 0.3,
                'revenue': roi_data['overall']['revenue'] * 0.4,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.3,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.4,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.4
            },
            {
                'name': 'Carousel',
                'spend': roi_data['overall']['spend'] * 0.2,
                'revenue': roi_data['overall']['revenue'] * 0.15,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.2,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.15,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.15
            },
            {
                'name': 'Collection',
                'spend': roi_data['overall']['spend'] * 0.1,
                'revenue': roi_data['overall']['revenue'] * 0.1,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.1,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.1,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.1
            }
        ],
        'placement': [
            {
                'name': 'Feed',
                'spend': roi_data['overall']['spend'] * 0.5,
                'revenue': roi_data['overall']['revenue'] * 0.45,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.5,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.45,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.45
            },
            {
                'name': 'Stories',
                'spend': roi_data['overall']['spend'] * 0.3,
                'revenue': roi_data['overall']['revenue'] * 0.35,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.3,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.35,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.35
            },
            {
                'name': 'Search',
                'spend': roi_data['overall']['spend'] * 0.15,
                'revenue': roi_data['overall']['revenue'] * 0.15,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.15,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.15,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.15
            },
            {
                'name': 'Display',
                'spend': roi_data['overall']['spend'] * 0.05,
                'revenue': roi_data['overall']['revenue'] * 0.05,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.05,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.05,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.05
            }
        ],
        'device': [
            {
                'name': 'Mobile',
                'spend': roi_data['overall']['spend'] * 0.6,
                'revenue': roi_data['overall']['revenue'] * 0.55,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.6,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.55,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.55
            },
            {
                'name': 'Desktop',
                'spend': roi_data['overall']['spend'] * 0.3,
                'revenue': roi_data['overall']['revenue'] * 0.35,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.3,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.35,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.35
            },
            {
                'name': 'Tablet',
                'spend': roi_data['overall']['spend'] * 0.1,
                'revenue': roi_data['overall']['revenue'] * 0.1,
                'impressions': sum(metrics['impressions'] for metrics in platform_metrics.values()) * 0.1,
                'clicks': sum(metrics['clicks'] for metrics in platform_metrics.values()) * 0.1,
                'conversions': sum(metrics['conversions'] for metrics in platform_metrics.values()) * 0.1
            }
        ]
    }
    
    return jsonify({
        'status': 'success',
        'campaign': {
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'startDate': campaign.start_date.isoformat() if campaign.start_date else None,
            'endDate': campaign.end_date.isoformat() if campaign.end_date else None,
            'status': campaign.status,
            'budget': campaign.budget,
            'platform': campaign.platform
        },
        'dateRange': {
            'start': date_from,
            'end': date_to
        },
        'platforms': platforms,
        'timeSeriesData': time_series_data,
        'platformData': platform_metrics,
        'roiData': roi_data
    })

@app.route('/api/campaigns/list')
def get_campaigns_list():
    """API endpoint to get the list of campaigns for the dashboard."""
    campaigns = Campaign.query.all()
    return jsonify({
        'status': 'success',
        'campaigns': [{
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'startDate': campaign.start_date.isoformat() if campaign.start_date else None,
            'endDate': campaign.end_date.isoformat() if campaign.end_date else None,
            'status': campaign.status,
            'budget': campaign.budget,
            'platform': campaign.platform
        } for campaign in campaigns]
    })

# Initialize database with sample data
def init_sample_data():
    # Create admin user
    admin = User(
        username="admin",
        email="admin@example.com",
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    
    # Create sample documents
    doc1 = Document(
        slug='getting-started',
        title='Getting Started with MagnetoCursor',
        doc_type='tutorial',
        status='published',
        created_by=admin.id
    )
    doc1.set_metadata({
        'author': 'Admin',
        'description': 'A tutorial for getting started with MagnetoCursor'
    })
    
    doc2 = Document(
        slug='api-documentation',
        title='API Documentation',
        doc_type='api',
        status='published',
        created_by=admin.id
    )
    doc2.set_metadata({
        'author': 'Admin',
        'description': 'Comprehensive API documentation'
    })
    
    # Create sample campaigns
    campaign1 = Campaign(
        name='Spring Marketing Campaign',
        description='Marketing campaign for spring season',
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status='active',
        budget=5000.0,
        platform='Meta',
        created_by=admin.id
    )
    
    campaign2 = Campaign(
        name='Summer Sale Campaign',
        description='Promotional campaign for summer sale',
        start_date=datetime.now() + timedelta(days=45),
        end_date=datetime.now() + timedelta(days=75),
        status='draft',
        budget=7500.0,
        platform='Google',
        created_by=admin.id
    )
    
    campaign3 = Campaign(
        name='Fall Product Launch',
        description='Campaign for new product launch',
        start_date=datetime.now() + timedelta(days=90),
        end_date=datetime.now() + timedelta(days=120),
        status='planned',
        budget=10000.0,
        platform='X',
        created_by=admin.id
    )
    
    # Create sample segments
    segment1 = Segment(
        name='Young Professionals',
        description='Professionals aged 25-35',
        criteria=json.dumps({
            'age_min': 25,
            'age_max': 35,
            'employment_status': 'employed'
        }),
        created_by=admin.id
    )
    
    segment2 = Segment(
        name='Tech Enthusiasts',
        description='People interested in technology',
        criteria=json.dumps({
            'interests': ['technology', 'gadgets', 'computers']
        }),
        created_by=admin.id
    )
    
    segment3 = Segment(
        name='Recent Graduates',
        description='College graduates from the last 2 years',
        criteria=json.dumps({
            'education_level': 'bachelor',
            'graduation_year_min': datetime.now().year - 2,
            'graduation_year_max': datetime.now().year
        }),
        created_by=admin.id
    )
    
    # Add all objects to session
    db.session.add_all([doc1, doc2, campaign1, campaign2, campaign3, segment1, segment2, segment3])
    db.session.commit()
    
    logger.info("Sample data initialized successfully")

# Context processor to make some data available to all templates
@app.context_processor
def inject_globals():
    return {
        'app_name': 'MagnetoCursor',
        'current_year': datetime.now().year,
        'env': 'development'
    }

# Create a simple API routes directly in the app
@app.route('/api/platform-status')
def api_platform_status():
    """Show platform connection status dashboard."""
    # Get platform statuses and render the template
    platforms = [
        {'name': 'Meta', 'status': 'connected', 'last_checked': datetime.now(), 'response_time': 120},
        {'name': 'Google', 'status': 'connected', 'last_checked': datetime.now(), 'response_time': 150},
        {'name': 'X (Twitter)', 'status': 'connected', 'last_checked': datetime.now(), 'response_time': 200},
        {'name': 'LinkedIn', 'status': 'disconnected', 'last_checked': datetime.now(), 'response_time': 0},
        {'name': 'TikTok', 'status': 'maintenance', 'last_checked': datetime.now(), 'response_time': 350}
    ]
    
    return render_template('dashboard/platform_status.html', 
                         platforms=platforms,
                         connected_count=3,
                         total_platforms=5)

# Create a simple platform status template
os.makedirs(os.path.join(app.template_folder, 'dashboard'), exist_ok=True)
platform_status_template = os.path.join(app.template_folder, 'dashboard', 'platform_status.html')

if not os.path.exists(platform_status_template):
    with open(platform_status_template, 'w') as f:
        f.write("""{% extends "simple_base.html" %}

{% block title %}Platform Status | MagnetoCursor{% endblock %}

{% block content %}
<div class="dashboard-wrapper">
    <!-- Header Section -->
    <div class="dashboard-header">
        <div class="header-left">
            <h1 class="page-title">Platform Connection Status</h1>
            <p class="text-muted">Monitor and manage connections to social media advertising platforms</p>
        </div>
        <div class="header-actions">
            <button class="btn btn-outline-primary" id="refreshAllBtn">
                <i class="fas fa-sync-alt me-2"></i> Refresh All
            </button>
            <button class="btn btn-primary ms-2">
                <i class="fas fa-plus me-2"></i> Add Platform
            </button>
        </div>
    </div>

    <!-- Status Summary -->
    <div class="stats-cards">
        <div class="stats-card">
            <div class="stats-icon bg-success-light">
                <i class="fas fa-check-circle text-success"></i>
            </div>
            <div class="stats-content">
                <div class="stats-title">Connected Platforms</div>
                <div class="stats-value">{{ connected_count }}</div>
                <div class="stats-change positive">
                    <i class="fas fa-arrow-up"></i> Ready to use
                </div>
            </div>
        </div>
        <div class="stats-card">
            <div class="stats-icon bg-warning-light">
                <i class="fas fa-exclamation-triangle text-warning"></i>
            </div>
            <div class="stats-content">
                <div class="stats-title">Platforms in Maintenance</div>
                <div class="stats-value">1</div>
                <div class="stats-change pending">
                    <i class="fas fa-clock"></i> Temporary issues
                </div>
            </div>
        </div>
        <div class="stats-card">
            <div class="stats-icon bg-danger-light">
                <i class="fas fa-times-circle text-danger"></i>
            </div>
            <div class="stats-content">
                <div class="stats-title">Disconnected Platforms</div>
                <div class="stats-value">{{ total_platforms - connected_count - 1 }}</div>
                <div class="stats-change negative">
                    <i class="fas fa-arrow-down"></i> Needs configuration
                </div>
            </div>
        </div>
        <div class="stats-card">
            <div class="stats-icon bg-info-light">
                <i class="fas fa-globe text-info"></i>
            </div>
            <div class="stats-content">
                <div class="stats-title">Total Platforms</div>
                <div class="stats-value">{{ total_platforms }}</div>
                <div class="stats-change positive">
                    <i class="fas fa-plus"></i> All available platforms
                </div>
            </div>
        </div>
    </div>

    <!-- Platform Status Table -->
    <div class="dashboard-card">
        <div class="card-header">
            <h2>Platform Status</h2>
            <div class="header-actions">
                <div class="input-group input-group-sm">
                    <input type="text" class="form-control" placeholder="Search platforms..." id="platformSearchInput">
                    <span class="input-group-text"><i class="fas fa-search"></i></span>
                </div>
            </div>
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover platform-table">
                    <thead>
                        <tr>
                            <th>Platform</th>
                            <th>Status</th>
                            <th>Last Checked</th>
                            <th>Response Time</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for platform in platforms %}
                        <tr>
                            <td>
                                <div class="platform-name">
                                    {% if platform.name == 'Meta' %}
                                    <div class="platform-icon bg-primary-light">
                                        <i class="fab fa-facebook text-primary"></i>
                                    </div>
                                    {% elif platform.name == 'Google' %}
                                    <div class="platform-icon bg-danger-light">
                                        <i class="fab fa-google text-danger"></i>
                                    </div>
                                    {% elif platform.name == 'X (Twitter)' %}
                                    <div class="platform-icon bg-info-light">
                                        <i class="fab fa-twitter text-info"></i>
                                    </div>
                                    {% elif platform.name == 'LinkedIn' %}
                                    <div class="platform-icon bg-primary-light">
                                        <i class="fab fa-linkedin text-primary"></i>
                                    </div>
                                    {% elif platform.name == 'TikTok' %}
                                    <div class="platform-icon bg-dark">
                                        <i class="fab fa-tiktok text-white"></i>
                                    </div>
                                    {% else %}
                                    <div class="platform-icon bg-secondary-light">
                                        <i class="fas fa-ad text-secondary"></i>
                                    </div>
                                    {% endif %}
                                    <span>{{ platform.name }}</span>
                                </div>
                            </td>
                            <td>
                                {% if platform.status == 'connected' %}
                                <span class="status-badge active"><i class="fas fa-circle"></i> Connected</span>
                                {% elif platform.status == 'disconnected' %}
                                <span class="status-badge inactive"><i class="fas fa-circle"></i> Disconnected</span>
                                {% elif platform.status == 'maintenance' %}
                                <span class="status-badge pending"><i class="fas fa-circle"></i> In Maintenance</span>
                                {% else %}
                                <span class="status-badge pending"><i class="fas fa-circle"></i> {{ platform.status }}</span>
                                {% endif %}
                            </td>
                            <td>{{ platform.last_checked.strftime('%b %d, %Y %H:%M') if platform.last_checked else 'N/A' }}</td>
                            <td>
                                {% if platform.status == 'connected' %}
                                <span class="{% if platform.response_time < 150 %}text-success{% elif platform.response_time < 300 %}text-warning{% else %}text-danger{% endif %}">
                                    {{ platform.response_time }} ms
                                </span>
                                {% else %}
                                -
                                {% endif %}
                            </td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn btn-sm btn-outline-primary test-connection-btn" data-platform="{{ platform.name }}">
                                        <i class="fas fa-sync-alt"></i>
                                    </button>
                                    {% if platform.status == 'connected' %}
                                    <button class="btn btn-sm btn-outline-danger">
                                        <i class="fas fa-unlink"></i>
                                    </button>
                                    {% else %}
                                    <button class="btn btn-sm btn-outline-success">
                                        <i class="fas fa-link"></i>
                                    </button>
                                    {% endif %}
                                    <div class="dropdown d-inline-block">
                                        <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                            <i class="fas fa-ellipsis-v"></i>
                                        </button>
                                        <ul class="dropdown-menu dropdown-menu-end">
                                            <li><a class="dropdown-item" href="#"><i class="fas fa-cog me-2"></i>Configure</a></li>
                                            <li><a class="dropdown-item" href="#"><i class="fas fa-history me-2"></i>View History</a></li>
                                            <li><a class="dropdown-item" href="#"><i class="fas fa-info-circle me-2"></i>API Details</a></li>
                                        </ul>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Credentials Manager -->
    <div class="dashboard-card mt-4">
        <div class="card-header">
            <h2>API Credentials Management</h2>
            <div class="header-actions">
                <button class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-key me-2"></i> Add New Credentials
                </button>
            </div>
        </div>
        <div class="card-body">
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i> API credentials are securely stored and rotated automatically. You can manage your credentials and check their validation status below.
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header bg-primary text-white">
                            <div class="d-flex justify-content-between align-items-center">
                                <span><i class="fab fa-facebook me-2"></i> Meta Ads API</span>
                                <span class="badge bg-success">Active</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">API Version</label>
                                <div class="input-group">
                                    <input type="text" class="form-control" value="v17.0" readonly>
                                    <button class="btn btn-outline-secondary" type="button"><i class="fas fa-copy"></i></button>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">App ID</label>
                                <div class="input-group">
                                    <input type="text" class="form-control" value="********2345" readonly>
                                    <button class="btn btn-outline-secondary" type="button"><i class="fas fa-copy"></i></button>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-sm btn-outline-primary"><i class="fas fa-sync-alt me-2"></i>Rotate</button>
                                <button class="btn btn-sm btn-outline-secondary"><i class="fas fa-cog me-2"></i>Configure</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header bg-danger text-white">
                            <div class="d-flex justify-content-between align-items-center">
                                <span><i class="fab fa-google me-2"></i> Google Ads API</span>
                                <span class="badge bg-success">Active</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">API Version</label>
                                <div class="input-group">
                                    <input type="text" class="form-control" value="v14" readonly>
                                    <button class="btn btn-outline-secondary" type="button"><i class="fas fa-copy"></i></button>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Client ID</label>
                                <div class="input-group">
                                    <input type="text" class="form-control" value="********78ab" readonly>
                                    <button class="btn btn-outline-secondary" type="button"><i class="fas fa-copy"></i></button>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-sm btn-outline-primary"><i class="fas fa-sync-alt me-2"></i>Rotate</button>
                                <button class="btn btn-sm btn-outline-secondary"><i class="fas fa-cog me-2"></i>Configure</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Handle refresh all button
        document.getElementById('refreshAllBtn').addEventListener('click', function() {
            alert('Refreshing all platform connections...');
            // In a real implementation, this would make API calls to test connections
            // and update the UI with the results
        });
        
        // Handle individual test connection buttons
        const testButtons = document.querySelectorAll('.test-connection-btn');
        testButtons.forEach(button => {
            button.addEventListener('click', function() {
                const platform = this.getAttribute('data-platform');
                alert(`Testing connection to ${platform}...`);
                // In a real implementation, this would make an API call to test
                // the connection and update the UI with the result
            });
        });
        
        // Search functionality for platforms
        document.getElementById('platformSearchInput').addEventListener('keyup', function() {
            const searchValue = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('.platform-table tbody tr');
            
            tableRows.forEach(row => {
                const platformName = row.querySelector('.platform-name').textContent.toLowerCase();
                if (platformName.includes(searchValue)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
</script>
{% endblock %}""")

# Initialize database tables and sample data
with app.app_context():
    db.create_all()
    logger.info(f"Created database tables in {db_path}")
    
    # Only add sample data if tables are empty
    if User.query.count() == 0:
        init_sample_data()

# Add routes for API and platform pages
@app.route('/api/metrics')
def api_metrics_dashboard():
    """API Metrics Dashboard."""
    # Mock data for API metrics
    api_metrics = {
        'meta': {
            'daily_requests': 5250,
            'error_rate': 0.8,
            'avg_response_time': 145, 
            'quota_usage': 37.5
        },
        'google': {
            'daily_requests': 4120,
            'error_rate': 0.5,
            'avg_response_time': 180,
            'quota_usage': 41.2
        },
        'twitter': {
            'daily_requests': 2830,
            'error_rate': 1.2,
            'avg_response_time': 210,
            'quota_usage': 28.3
        }
    }
    
    # Calculate totals
    total_requests = sum(platform['daily_requests'] for platform in api_metrics.values())
    avg_error_rate = sum(platform['error_rate'] for platform in api_metrics.values()) / len(api_metrics)
    avg_response_time = sum(platform['avg_response_time'] for platform in api_metrics.values()) / len(api_metrics)
    avg_quota_usage = sum(platform['quota_usage'] for platform in api_metrics.values()) / len(api_metrics)
    
    # Generate random time series data for charts
    time_labels = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
    requests_data = [
        {'platform': 'Meta', 'data': [420, 380, 620, 750, 680, 520]},
        {'platform': 'Google', 'data': [350, 310, 580, 680, 590, 430]},
        {'platform': 'Twitter', 'data': [220, 180, 380, 480, 350, 280]}
    ]
    
    response_time_data = [
        {'platform': 'Meta', 'data': [135, 142, 158, 160, 145, 130]},
        {'platform': 'Google', 'data': [165, 178, 195, 210, 185, 172]},
        {'platform': 'Twitter', 'data': [195, 205, 218, 225, 210, 198]}
    ]
    
    return render_template('dashboard/api_metrics.html',
                         api_metrics=api_metrics,
                         total_requests=total_requests,
                         avg_error_rate=avg_error_rate,
                         avg_response_time=avg_response_time,
                         avg_quota_usage=avg_quota_usage,
                         time_labels=time_labels,
                         requests_data=requests_data,
                         response_time_data=response_time_data)

@app.route('/credentials/dashboard')
def credentials_dashboard():
    """API Credentials Dashboard."""
    # Mock data for credentials
    credentials = [
        {
            'platform': 'Meta',
            'app_id': '1234567890',
            'app_secret': '********abcdef',
            'access_token': '********ghijkl',
            'status': 'active',
            'expires_in': '58 days',
            'scopes': ['ads_management', 'business_management', 'pages_read_engagement'],
            'last_rotated': '2025-02-15'
        },
        {
            'platform': 'Google',
            'client_id': '123456789012-abcdef.apps.googleusercontent.com',
            'client_secret': '********GOCSPX',
            'refresh_token': '********1//04dX',
            'status': 'active',
            'expires_in': 'Never',
            'scopes': ['https://www.googleapis.com/auth/adwords', 'https://www.googleapis.com/auth/analytics'],
            'last_rotated': '2025-01-20'
        },
        {
            'platform': 'Twitter',
            'api_key': '********abcXyz123',
            'api_secret': '********789Abc',
            'bearer_token': '********AAAA',
            'status': 'active',
            'expires_in': '90 days',
            'scopes': ['tweet.read', 'users.read', 'tweet.write'],
            'last_rotated': '2025-03-10'
        },
        {
            'platform': 'LinkedIn',
            'client_id': '********12345',
            'client_secret': '********abcDEF',
            'status': 'inactive',
            'expires_in': 'Expired',
            'scopes': ['r_organization_social', 'w_organization_social', 'r_ads'],
            'last_rotated': '2024-11-05'
        }
    ]
    
    # Count active and inactive credentials
    active_count = sum(1 for cred in credentials if cred['status'] == 'active')
    inactive_count = len(credentials) - active_count
    
    # Security status check - mock data
    security_status = {
        'key_rotation': 'Good',
        'encryption': 'Excellent',
        'access_control': 'Good',
        'audit_logging': 'Fair'
    }
    
    # Recent activity log - mock data
    activity_log = [
        {'timestamp': '2025-03-27 09:45', 'action': 'Key rotation', 'platform': 'Twitter', 'user': 'admin@magnetocursor.com'},
        {'timestamp': '2025-03-25 14:32', 'action': 'Access scope modified', 'platform': 'Meta', 'user': 'admin@magnetocursor.com'},
        {'timestamp': '2025-03-22 10:15', 'action': 'New credential added', 'platform': 'TikTok', 'user': 'admin@magnetocursor.com'},
        {'timestamp': '2025-03-20 16:08', 'action': 'Credential deleted', 'platform': 'LinkedIn', 'user': 'admin@magnetocursor.com'},
        {'timestamp': '2025-03-15 11:27', 'action': 'Key rotation', 'platform': 'Google', 'user': 'admin@magnetocursor.com'}
    ]
    
    return render_template('dashboard/credentials.html',
                         credentials=credentials,
                         active_count=active_count,
                         inactive_count=inactive_count,
                         security_status=security_status,
                         activity_log=activity_log)

@app.route('/api/playground')
def api_playground():
    """API testing playground."""
    # Available platforms for testing
    platforms = [
        {'id': 'meta', 'name': 'Meta Ads API', 'version': 'v17.0'},
        {'id': 'google', 'name': 'Google Ads API', 'version': 'v14'},
        {'id': 'twitter', 'name': 'Twitter Ads API', 'version': 'v11'},
        {'id': 'linkedin', 'name': 'LinkedIn Marketing API', 'version': 'v2'}
    ]
    
    # Sample API endpoints for each platform
    endpoints = {
        'meta': [
            {'name': 'Get Ad Accounts', 'endpoint': '/me/adaccounts', 'method': 'GET'},
            {'name': 'Get Campaign Insights', 'endpoint': '/{ad_account_id}/insights', 'method': 'GET'},
            {'name': 'Create Campaign', 'endpoint': '/{ad_account_id}/campaigns', 'method': 'POST'}
        ],
        'google': [
            {'name': 'Get Campaigns', 'endpoint': '/customers/{customer_id}/campaigns', 'method': 'GET'},
            {'name': 'Get Campaign Metrics', 'endpoint': '/customers/{customer_id}/googleAds:search', 'method': 'POST'},
            {'name': 'Create Campaign', 'endpoint': '/customers/{customer_id}/campaigns:mutate', 'method': 'POST'}
        ],
        'twitter': [
            {'name': 'Get Accounts', 'endpoint': '/accounts', 'method': 'GET'},
            {'name': 'Get Campaign Analytics', 'endpoint': '/stats/accounts/{account_id}', 'method': 'GET'},
            {'name': 'Create Campaign', 'endpoint': '/accounts/{account_id}/campaigns', 'method': 'POST'}
        ],
        'linkedin': [
            {'name': 'Get Ad Accounts', 'endpoint': '/adAccountsV2', 'method': 'GET'},
            {'name': 'Get Campaign Analytics', 'endpoint': '/adAnalyticsV2', 'method': 'GET'},
            {'name': 'Create Campaign', 'endpoint': '/adCampaignsV2', 'method': 'POST'}
        ]
    }
    
    # Sample API responses
    sample_responses = {
        'meta_accounts': '''
{
  "data": [
    {
      "id": "act_123456789",
      "name": "Business Account",
      "currency": "USD",
      "account_status": 1
    }
  ]
}''',
        'google_campaigns': '''
{
  "results": [
    {
      "campaign": {
        "resourceName": "customers/1234567890/campaigns/9876543210",
        "id": "9876543210",
        "name": "Spring Promotion 2025",
        "status": "ENABLED"
      },
      "metrics": {
        "impressions": "45000",
        "clicks": "2800",
        "costMicros": "9500000"
      }
    }
  ]
}''',
        'twitter_analytics': '''
{
  "data": [
    {
      "id": "8ve",
      "id_data": [
        {
          "metrics": {
            "billed_charge_local_micro": 12345600,
            "impressions": 36700,
            "clicks": 1250
          }
        }
      ]
    }
  ]
}'''
    }
    
    return render_template('dashboard/api_playground.html',
                         platforms=platforms,
                         endpoints=endpoints,
                         sample_responses=sample_responses)
                         
# Create necessary templates
api_metrics_template = os.path.join(app.template_folder, 'dashboard', 'api_metrics.html')
if not os.path.exists(api_metrics_template):
    with open(api_metrics_template, 'w') as f:
        f.write("""{% extends "simple_base.html" %}

{% block title %}API Metrics | MagnetoCursor{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="mb-1">API Metrics Dashboard</h1>
            <p class="text-muted">Monitor API usage, performance, and quotas across platforms</p>
        </div>
        <div class="d-flex align-items-center">
            <div class="dropdown me-2">
                <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fas fa-calendar me-2"></i> Last 24 Hours
                </button>
                <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#">Last 24 Hours</a></li>
                    <li><a class="dropdown-item" href="#">Last 7 Days</a></li>
                    <li><a class="dropdown-item" href="#">Last 30 Days</a></li>
                    <li><a class="dropdown-item" href="#">Custom Range</a></li>
                </ul>
            </div>
            <button class="btn btn-outline-primary">
                <i class="fas fa-download me-2"></i> Export
            </button>
        </div>
    </div>
    
    <!-- Summary Cards -->
    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="flex-shrink-0">
                            <div class="stats-icon bg-primary-light">
                                <i class="fas fa-exchange-alt text-primary"></i>
                            </div>
                        </div>
                        <div class="flex-grow-1 ms-3">
                            <h6 class="card-subtitle text-muted">Total API Requests</h6>
                        </div>
                    </div>
                    <h2 class="card-title mb-1">{{ "{:,}".format(total_requests) }}</h2>
                    <div class="text-success small">
                        <i class="fas fa-arrow-up me-1"></i> 8.3% from yesterday
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="flex-shrink-0">
                            <div class="stats-icon bg-warning-light">
                                <i class="fas fa-exclamation-triangle text-warning"></i>
                            </div>
                        </div>
                        <div class="flex-grow-1 ms-3">
                            <h6 class="card-subtitle text-muted">Avg. Error Rate</h6>
                        </div>
                    </div>
                    <h2 class="card-title mb-1">{{ "%.1f"|format(avg_error_rate) }}%</h2>
                    <div class="text-danger small">
                        <i class="fas fa-arrow-up me-1"></i> 0.2% from yesterday
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="flex-shrink-0">
                            <div class="stats-icon bg-info-light">
                                <i class="fas fa-clock text-info"></i>
                            </div>
                        </div>
                        <div class="flex-grow-1 ms-3">
                            <h6 class="card-subtitle text-muted">Avg. Response Time</h6>
                        </div>
                    </div>
                    <h2 class="card-title mb-1">{{ "%.0f"|format(avg_response_time) }} ms</h2>
                    <div class="text-success small">
                        <i class="fas fa-arrow-down me-1"></i> 5.3% from yesterday
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="flex-shrink-0">
                            <div class="stats-icon bg-success-light">
                                <i class="fas fa-chart-pie text-success"></i>
                            </div>
                        </div>
                        <div class="flex-grow-1 ms-3">
                            <h6 class="card-subtitle text-muted">Avg. Quota Usage</h6>
                        </div>
                    </div>
                    <h2 class="card-title mb-1">{{ "%.1f"|format(avg_quota_usage) }}%</h2>
                    <div class="text-warning small">
                        <i class="fas fa-arrow-up me-1"></i> 3.1% from yesterday
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Request Volume Chart -->
    <div class="card mb-4">
        <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">API Request Volume</h5>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-secondary active">Hourly</button>
                    <button class="btn btn-outline-secondary">Daily</button>
                    <button class="btn btn-outline-secondary">Weekly</button>
                </div>
            </div>
        </div>
        <div class="card-body">
            <canvas id="requestVolumeChart" height="300"></canvas>
        </div>
    </div>
    
    <!-- Response Time Chart -->
    <div class="card mb-4">
        <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">API Response Time</h5>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-secondary active">Hourly</button>
                    <button class="btn btn-outline-secondary">Daily</button>
                    <button class="btn btn-outline-secondary">Weekly</button>
                </div>
            </div>
        </div>
        <div class="card-body">
            <canvas id="responseTimeChart" height="300"></canvas>
        </div>
    </div>
    
    <!-- Platform-specific metrics table -->
    <div class="card mb-4">
        <div class="card-header bg-white">
            <h5 class="mb-0">Platform-specific Metrics</h5>
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Platform</th>
                            <th>Daily Requests</th>
                            <th>Error Rate</th>
                            <th>Avg Response Time</th>
                            <th>Quota Usage</th>
                            <th>Status</th>
                            <th class="text-end">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="platform-icon bg-primary-light me-2">
                                        <i class="fab fa-facebook text-primary"></i>
                                    </div>
                                    <span>Meta</span>
                                </div>
                            </td>
                            <td>{{ "{:,}".format(api_metrics.meta.daily_requests) }}</td>
                            <td>{{ "%.1f"|format(api_metrics.meta.error_rate) }}%</td>
                            <td>{{ api_metrics.meta.avg_response_time }} ms</td>
                            <td>
                                <div class="progress" style="height: 6px; width: 100px;">
                                    <div class="progress-bar" role="progressbar" style="width: {{ api_metrics.meta.quota_usage }}%;" aria-valuenow="{{ api_metrics.meta.quota_usage }}" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <span class="small">{{ "%.1f"|format(api_metrics.meta.quota_usage) }}%</span>
                            </td>
                            <td><span class="badge bg-success">Healthy</span></td>
                            <td class="text-end">
                                <button class="btn btn-sm btn-outline-primary">Details</button>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="platform-icon bg-danger-light me-2">
                                        <i class="fab fa-google text-danger"></i>
                                    </div>
                                    <span>Google</span>
                                </div>
                            </td>
                            <td>{{ "{:,}".format(api_metrics.google.daily_requests) }}</td>
                            <td>{{ "%.1f"|format(api_metrics.google.error_rate) }}%</td>
                            <td>{{ api_metrics.google.avg_response_time }} ms</td>
                            <td>
                                <div class="progress" style="height: 6px; width: 100px;">
                                    <div class="progress-bar" role="progressbar" style="width: {{ api_metrics.google.quota_usage }}%;" aria-valuenow="{{ api_metrics.google.quota_usage }}" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <span class="small">{{ "%.1f"|format(api_metrics.google.quota_usage) }}%</span>
                            </td>
                            <td><span class="badge bg-success">Healthy</span></td>
                            <td class="text-end">
                                <button class="btn btn-sm btn-outline-primary">Details</button>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="platform-icon bg-info-light me-2">
                                        <i class="fab fa-twitter text-info"></i>
                                    </div>
                                    <span>Twitter</span>
                                </div>
                            </td>
                            <td>{{ "{:,}".format(api_metrics.twitter.daily_requests) }}</td>
                            <td>{{ "%.1f"|format(api_metrics.twitter.error_rate) }}%</td>
                            <td>{{ api_metrics.twitter.avg_response_time }} ms</td>
                            <td>
                                <div class="progress" style="height: 6px; width: 100px;">
                                    <div class="progress-bar" role="progressbar" style="width: {{ api_metrics.twitter.quota_usage }}%;" aria-valuenow="{{ api_metrics.twitter.quota_usage }}" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <span class="small">{{ "%.1f"|format(api_metrics.twitter.quota_usage) }}%</span>
                            </td>
                            <td><span class="badge bg-success">Healthy</span></td>
                            <td class="text-end">
                                <button class="btn btn-sm btn-outline-primary">Details</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Rate Limits & Quotas -->
    <div class="card mb-4">
        <div class="card-header bg-white">
            <h5 class="mb-0">Rate Limits & Quotas</h5>
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Platform</th>
                            <th>Endpoint</th>
                            <th>Daily Limit</th>
                            <th>Used</th>
                            <th>Remaining</th>
                            <th>Reset Time</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Meta</td>
                            <td>/insights</td>
                            <td>5,000</td>
                            <td>1,873</td>
                            <td>3,127</td>
                            <td>Midnight UTC</td>
                            <td><span class="badge bg-success">OK</span></td>
                        </tr>
                        <tr>
                            <td>Meta</td>
                            <td>/adaccounts</td>
                            <td>1,000</td>
                            <td>782</td>
                            <td>218</td>
                            <td>Midnight UTC</td>
                            <td><span class="badge bg-warning">Monitor</span></td>
                        </tr>
                        <tr>
                            <td>Google</td>
                            <td>/customers/*/campaigns</td>
                            <td>10,000</td>
                            <td>3,245</td>
                            <td>6,755</td>
                            <td>Midnight PST</td>
                            <td><span class="badge bg-success">OK</span></td>
                        </tr>
                        <tr>
                            <td>Twitter</td>
                            <td>/stats/accounts</td>
                            <td>3,000</td>
                            <td>2,640</td>
                            <td>360</td>
                            <td>3:45 PM UTC</td>
                            <td><span class="badge bg-danger">Alert</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Request Volume Chart
        const requestVolumeCtx = document.getElementById('requestVolumeChart').getContext('2d');
        new Chart(requestVolumeCtx, {
            type: 'line',
            data: {
                labels: {{ time_labels|tojson }},
                datasets: [
                    {% for platform in requests_data %}
                    {
                        label: '{{ platform.platform }}',
                        data: {{ platform.data|tojson }},
                        borderColor: {% if platform.platform == 'Meta' %}'#4267B2'{% elif platform.platform == 'Google' %}'#DB4437'{% elif platform.platform == 'Twitter' %}'#1DA1F2'{% else %}'#999999'{% endif %},
                        backgroundColor: {% if platform.platform == 'Meta' %}'rgba(66, 103, 178, 0.1)'{% elif platform.platform == 'Google' %}'rgba(219, 68, 55, 0.1)'{% elif platform.platform == 'Twitter' %}'rgba(29, 161, 242, 0.1)'{% else %}'rgba(153, 153, 153, 0.1)'{% endif %},
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }{% if not loop.last %},{% endif %}
                    {% endfor %}
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
        
        // Response Time Chart
        const responseTimeCtx = document.getElementById('responseTimeChart').getContext('2d');
        new Chart(responseTimeCtx, {
            type: 'line',
            data: {
                labels: {{ time_labels|tojson }},
                datasets: [
                    {% for platform in response_time_data %}
                    {
                        label: '{{ platform.platform }}',
                        data: {{ platform.data|tojson }},
                        borderColor: {% if platform.platform == 'Meta' %}'#4267B2'{% elif platform.platform == 'Google' %}'#DB4437'{% elif platform.platform == 'Twitter' %}'#1DA1F2'{% else %}'#999999'{% endif %},
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: false
                    }{% if not loop.last %},{% endif %}
                    {% endfor %}
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            drawBorder: false,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + ' ms';
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    });
</script>
{% endblock %}

{% block styles %}
<style>
    .stats-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
    
    .bg-primary-light {
        background-color: rgba(66, 103, 178, 0.1);
    }
    
    .bg-danger-light {
        background-color: rgba(219, 68, 55, 0.1);
    }
    
    .bg-info-light {
        background-color: rgba(29, 161, 242, 0.1);
    }
    
    .bg-success-light {
        background-color: rgba(46, 196, 182, 0.1);
    }
    
    .bg-warning-light {
        background-color: rgba(255, 159, 28, 0.1);
    }
    
    .text-primary {
        color: #4267B2 !important;
    }
    
    .text-danger {
        color: #DB4437 !important;
    }
    
    .text-info {
        color: #1DA1F2 !important;
    }
    
    .text-success {
        color: #2EC4B6 !important;
    }
    
    .text-warning {
        color: #FF9F1C !important;
    }
    
    .platform-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
</style>
{% endblock %}""")

credentials_template = os.path.join(app.template_folder, 'dashboard', 'credentials.html')
if not os.path.exists(credentials_template):
    with open(credentials_template, 'w') as f:
        f.write("""{% extends "simple_base.html" %}

{% block title %}API Credentials | MagnetoCursor{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="mb-1">API Credentials Management</h1>
            <p class="text-muted">Securely manage your social media platform API credentials</p>
        </div>
        <div>
            <button class="btn btn-primary">
                <i class="fas fa-plus me-2"></i> Add New Credential
            </button>
        </div>
    </div>
    
    <!-- Status Summary Cards -->
    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="flex-shrink-0">
                            <div class="icon-circle bg-success-light">
                                <i class="fas fa-check-circle text-success"></i>
                            </div>
                        </div>
                        <div class="flex-grow-1 ms-3">
                            <h6 class="card-subtitle text-muted">Active Credentials</h6>
                        </div>
                    </div>
                    <h2 class="card-title mb-0">{{ active_count }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="flex-shrink-0">
                            <div class="icon-circle bg-danger-light">
                                <i class="fas fa-times-circle text-danger"></i>
                            </div>
                        </div>
                        <div class="flex-grow-1 ms-3">
                            <h6 class="card-subtitle text-muted">Inactive Credentials</h6>
                        </div>
                    </div>
                    <h2 class="card-title mb-0">{{ inactive_count }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="card-subtitle text-muted mb-3">Security Status</h6>
                    <div class="d-flex flex-wrap">
                        <div class="me-4 mb-2">
                            <div class="d-flex align-items-center">
                                <span class="me-2">Key Rotation:</span>
                                <span class="badge bg-success">{{ security_status.key_rotation }}</span>
                            </div>
                        </div>
                        <div class="me-4 mb-2">
                            <div class="d-flex align-items-center">
                                <span class="me-2">Encryption:</span>
                                <span class="badge bg-success">{{ security_status.encryption }}</span>
                            </div>
                        </div>
                        <div class="me-4 mb-2">
                            <div class="d-flex align-items-center">
                                <span class="me-2">Access Control:</span>
                                <span class="badge bg-success">{{ security_status.access_control }}</span>
                            </div>
                        </div>
                        <div class="mb-2">
                            <div class="d-flex align-items-center">
                                <span class="me-2">Audit Logging:</span>
                                <span class="badge bg-warning">{{ security_status.audit_logging }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Credentials List -->
    <div class="card mb-4">
        <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">API Credentials</h5>
                <div class="input-group" style="width: 250px;">
                    <input type="text" class="form-control" placeholder="Search credentials...">
                    <button class="btn btn-outline-secondary" type="button">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </div>
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Platform</th>
                            <th>Credentials</th>
                            <th>Status</th>
                            <th>Expires</th>
                            <th>Last Rotated</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for credential in credentials %}
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    {% if credential.platform == 'Meta' %}
                                    <div class="platform-icon bg-primary-light me-2">
                                        <i class="fab fa-facebook text-primary"></i>
                                    </div>
                                    {% elif credential.platform == 'Google' %}
                                    <div class="platform-icon bg-danger-light me-2">
                                        <i class="fab fa-google text-danger"></i>
                                    </div>
                                    {% elif credential.platform == 'Twitter' %}
                                    <div class="platform-icon bg-info-light me-2">
                                        <i class="fab fa-twitter text-info"></i>
                                    </div>
                                    {% elif credential.platform == 'LinkedIn' %}
                                    <div class="platform-icon bg-primary-light me-2">
                                        <i class="fab fa-linkedin text-primary"></i>
                                    </div>
                                    {% else %}
                                    <div class="platform-icon bg-secondary-light me-2">
                                        <i class="fas fa-user-lock text-secondary"></i>
                                    </div>
                                    {% endif %}
                                    <span>{{ credential.platform }}</span>
                                </div>
                            </td>
                            <td>
                                <div class="d-flex flex-column">
                                    {% if credential.platform == 'Meta' %}
                                    <div class="d-flex align-items-center mb-1">
                                        <span class="text-muted small me-2 credential-label">App ID:</span>
                                        <span class="credential-value">{{ credential.app_id }}</span>
                                        <button class="btn btn-link btn-sm py-0 ms-1" title="Copy"><i class="fas fa-copy"></i></button>
                                    </div>
                                    <div class="d-flex align-items-center">
                                        <span class="text-muted small me-2 credential-label">App Secret:</span>
                                        <span class="credential-value">{{ credential.app_secret }}</span>
                                        <button class="btn btn-link btn-sm py-0 ms-1" title="Copy"><i class="fas fa-copy"></i></button>
                                    </div>
                                    {% elif credential.platform == 'Google' %}
                                    <div class="d-flex align-items-center mb-1">
                                        <span class="text-muted small me-2 credential-label">Client ID:</span>
                                        <span class="credential-value">{{ credential.client_id }}</span>
                                        <button class="btn btn-link btn-sm py-0 ms-1" title="Copy"><i class="fas fa-copy"></i></button>
                                    </div>
                                    <div class="d-flex align-items-center">
                                        <span class="text-muted small me-2 credential-label">Client Secret:</span>
                                        <span class="credential-value">{{ credential.client_secret }}</span>
                                        <button class="btn btn-link btn-sm py-0 ms-1" title="Copy"><i class="fas fa-copy"></i></button>
                                    </div>
                                    {% elif credential.platform == 'Twitter' %}
                                    <div class="d-flex align-items-center mb-1">
                                        <span class="text-muted small me-2 credential-label">API Key:</span>
                                        <span class="credential-value">{{ credential.api_key }}</span>
                                        <button class="btn btn-link btn-sm py-0 ms-1" title="Copy"><i class="fas fa-copy"></i></button>
                                    </div>
                                    <div class="d-flex align-items-center">
                                        <span class="text-muted small me-2 credential-label">API Secret:</span>
                                        <span class="credential-value">{{ credential.api_secret }}</span>
                                        <button class="btn btn-link btn-sm py-0 ms-1" title="Copy"><i class="fas fa-copy"></i></button>
                                    </div>
                                    {% else %}
                                    <div class="d-flex align-items-center mb-1">
                                        <span class="text-muted small me-2 credential-label">Client ID:</span>
                                        <span class="credential-value">{{ credential.client_id }}</span>
                                        <button class="btn btn-link btn-sm py-0 ms-1" title="Copy"><i class="fas fa-copy"></i></button>
                                    </div>
                                    <div class="d-flex align-items-center">
                                        <span class="text-muted small me-2 credential-label">Client Secret:</span>
                                        <span class="credential-value">{{ credential.client_secret }}</span>
                                        <button class="btn btn-link btn-sm py-0 ms-1" title="Copy"><i class="fas fa-copy"></i></button>
                                    </div>
                                    {% endif %}
                                </div>
                            </td>
                            <td>
                                {% if credential.status == 'active' %}
                                <span class="badge bg-success">Active</span>
                                {% else %}
                                <span class="badge bg-danger">Inactive</span>
                                {% endif %}
                            </td>
                            <td>{{ credential.expires_in }}</td>
                            <td>{{ credential.last_rotated }}</td>
                            <td>
                                <div class="btn-group">
                                    <a href="#" class="btn btn-sm btn-outline-primary" title="Test Connection">
                                        <i class="fas fa-sync-alt"></i>
                                    </a>
                                    <a href="#" class="btn btn-sm btn-outline-secondary" title="Edit">
                                        <i class="fas fa-pencil-alt"></i>
                                    </a>
                                    <div class="btn-group">
                                        <button type="button" class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                                            <i class="fas fa-ellipsis-v"></i>
                                        </button>
                                        <ul class="dropdown-menu dropdown-menu-end">
                                            <li><a class="dropdown-item" href="#"><i class="fas fa-key me-2"></i>Rotate Keys</a></li>
                                            <li><a class="dropdown-item" href="#"><i class="fas fa-shield-alt me-2"></i>View Permissions</a></li>
                                            <li><a class="dropdown-item" href="#"><i class="fas fa-history me-2"></i>View History</a></li>
                                            <li><hr class="dropdown-divider"></li>
                                            <li><a class="dropdown-item text-danger" href="#"><i class="fas fa-trash me-2"></i>Delete</a></li>
                                        </ul>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Recent Activity -->
    <div class="card mb-4">
        <div class="card-header bg-white">
            <h5 class="mb-0">Recent Activity</h5>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-borderless mb-0">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Action</th>
                            <th>Platform</th>
                            <th>User</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for activity in activity_log %}
                        <tr>
                            <td>{{ activity.timestamp }}</td>
                            <td>
                                {% if 'rotation' in activity.action %}
                                <span class="badge bg-info text-dark py-1">{{ activity.action }}</span>
                                {% elif 'added' in activity.action %}
                                <span class="badge bg-success text-white py-1">{{ activity.action }}</span>
                                {% elif 'deleted' in activity.action %}
                                <span class="badge bg-danger text-white py-1">{{ activity.action }}</span>
                                {% else %}
                                <span class="badge bg-secondary text-white py-1">{{ activity.action }}</span>
                                {% endif %}
                            </td>
                            <td>{{ activity.platform }}</td>
                            <td>{{ activity.user }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        <div class="card-footer bg-white text-center">
            <a href="#" class="btn btn-outline-primary btn-sm">View All Activity</a>
        </div>
    </div>
</div>
{% endblock %}

{% block styles %}
<style>
    .icon-circle {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
    
    .platform-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
    
    .bg-primary-light {
        background-color: rgba(66, 103, 178, 0.1);
    }
    
    .bg-danger-light {
        background-color: rgba(219, 68, 55, 0.1);
    }
    
    .bg-info-light {
        background-color: rgba(29, 161, 242, 0.1);
    }
    
    .bg-success-light {
        background-color: rgba(46, 196, 182, 0.1);
    }
    
    .bg-warning-light {
        background-color: rgba(255, 159, 28, 0.1);
    }
    
    .bg-secondary-light {
        background-color: rgba(108, 117, 125, 0.1);
    }
    
    .text-primary {
        color: #4267B2 !important;
    }
    
    .text-danger {
        color: #DB4437 !important;
    }
    
    .text-info {
        color: #1DA1F2 !important;
    }
    
    .text-success {
        color: #2EC4B6 !important;
    }
    
    .text-warning {
        color: #FF9F1C !important;
    }
    
    .credential-label {
        width: 80px;
        display: inline-block;
    }
    
    .credential-value {
        font-family: monospace;
    }
</style>
{% endblock %}""")

api_playground_template = os.path.join(app.template_folder, 'dashboard', 'api_playground.html')
if not os.path.exists(api_playground_template):
    with open(api_playground_template, 'w') as f:
        f.write("""{% extends "simple_base.html" %}

{% block title %}API Playground | MagnetoCursor{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="mb-4">
        <h1 class="mb-1">API Playground</h1>
        <p class="text-muted">Test API endpoints and experiment with different parameters</p>
    </div>
    
    <div class="row">
        <!-- API Request Builder Panel -->
        <div class="col-lg-7">
            <div class="card mb-4">
                <div class="card-header bg-white">
                    <h5 class="mb-0">Request Builder</h5>
                </div>
                <div class="card-body">
                    <form id="apiRequestForm">
                        <div class="mb-3">
                            <label for="platform" class="form-label">Platform</label>
                            <select class="form-select" id="platform">
                                <option value="">Select a platform</option>
                                {% for platform in platforms %}
                                <option value="{{ platform.id }}">{{ platform.name }} ({{ platform.version }})</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label for="endpoint" class="form-label">Endpoint</label>
                            <select class="form-select" id="endpoint" disabled>
                                <option value="">Select an endpoint</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label for="method" class="form-label">Method</label>
                            <div class="method-selector">
                                <div class="btn-group w-100" role="group">
                                    <input type="radio" class="btn-check" name="method" id="method-get" value="GET" checked>
                                    <label class="btn btn-outline-primary" for="method-get">GET</label>
                                    
                                    <input type="radio" class="btn-check" name="method" id="method-post" value="POST">
                                    <label class="btn btn-outline-primary" for="method-post">POST</label>
                                    
                                    <input type="radio" class="btn-check" name="method" id="method-put" value="PUT">
                                    <label class="btn btn-outline-primary" for="method-put">PUT</label>
                                    
                                    <input type="radio" class="btn-check" name="method" id="method-delete" value="DELETE">
                                    <label class="btn btn-outline-primary" for="method-delete">DELETE</label>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="parameters" class="form-label">Parameters</label>
                            <div id="parameters-container">
                                <div class="row mb-2 parameter-row">
                                    <div class="col-5">
                                        <input type="text" class="form-control param-key" placeholder="Key">
                                    </div>
                                    <div class="col-6">
                                        <input type="text" class="form-control param-value" placeholder="Value">
                                    </div>
                                    <div class="col-1">
                                        <button type="button" class="btn btn-outline-danger remove-param">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <button type="button" class="btn btn-outline-secondary btn-sm mt-2" id="add-param">
                                <i class="fas fa-plus me-1"></i> Add Parameter
                            </button>
                        </div>
                        
                        <div class="mb-3">
                            <label for="request-body" class="form-label">Request Body (JSON)</label>
                            <div class="code-editor" id="request-body-editor">
                                <pre><code class="language-json" id="request-body-code">{
  "key": "value"
}</code></pre>
                            </div>
                        </div>
                        
                        <div class="d-flex justify-content-between">
                            <button type="button" class="btn btn-outline-secondary" id="reset-form">
                                <i class="fas fa-undo me-1"></i> Reset
                            </button>
                            <button type="submit" class="btn btn-primary" id="send-request">
                                <i class="fas fa-paper-plane me-1"></i> Send Request
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- Request History -->
            <div class="card">
                <div class="card-header bg-white">
                    <h5 class="mb-0">Request History</h5>
                </div>
                <div class="card-body p-0">
                    <div class="list-group list-group-flush">
                        <a href="#" class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">GET /me/adaccounts</h6>
                                <small class="text-muted">3 mins ago</small>
                            </div>
                            <p class="mb-1 text-muted small">Meta Ads API</p>
                            <span class="badge bg-success">200 OK</span>
                        </a>
                        <a href="#" class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">GET /customers/1234567890/campaigns</h6>
                                <small class="text-muted">10 mins ago</small>
                            </div>
                            <p class="mb-1 text-muted small">Google Ads API</p>
                            <span class="badge bg-success">200 OK</span>
                        </a>
                        <a href="#" class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">POST /{ad_account_id}/campaigns</h6>
                                <small class="text-muted">15 mins ago</small>
                            </div>
                            <p class="mb-1 text-muted small">Meta Ads API</p>
                            <span class="badge bg-danger">400 Bad Request</span>
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Response Panel -->
        <div class="col-lg-5">
            <div class="card mb-4">
                <div class="card-header bg-white">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Response</h5>
                        <div>
                            <span class="badge bg-success response-status">200 OK</span>
                            <span class="text-muted ms-2 response-time">154 ms</span>
                        </div>
                    </div>
                </div>
                <div class="card-body p-0">
                    <ul class="nav nav-tabs" id="responseTabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="response-body-tab" data-bs-toggle="tab" data-bs-target="#response-body" type="button" role="tab">Body</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="response-headers-tab" data-bs-toggle="tab" data-bs-target="#response-headers" type="button" role="tab">Headers</button>
                        </li>
                    </ul>
                    <div class="tab-content">
                        <div class="tab-pane fade show active" id="response-body" role="tabpanel">
                            <div class="code-editor" id="response-body-editor">
                                <pre><code class="language-json" id="response-body-code">{{ sample_responses.meta_accounts }}</code></pre>
                            </div>
                        </div>
                        <div class="tab-pane fade" id="response-headers" role="tabpanel">
                            <div class="p-3">
                                <table class="table table-sm">
                                    <tbody>
                                        <tr>
                                            <th>Content-Type</th>
                                            <td>application/json</td>
                                        </tr>
                                        <tr>
                                            <th>X-App-Usage</th>
                                            <td>{"call_count":28,"total_time":122,"total_cputime":14}</td>
                                        </tr>
                                        <tr>
                                            <th>X-FB-Debug</th>
                                            <td>5dYbw+pg3OcO3OlCm0DMb38PoVJfju66iJN38Me2iJYcVGJRk8HS/NA==</td>
                                        </tr>
                                        <tr>
                                            <th>Date</th>
                                            <td>Mon, 27 Mar 2025 14:58:26 GMT</td>
                                        </tr>
                                        <tr>
                                            <th>Connection</th>
                                            <td>keep-alive</td>
                                        </tr>
                                        <tr>
                                            <th>Cache-Control</th>
                                            <td>no-store</td>
                                        </tr>
                                        <tr>
                                            <th>Pragma</th>
                                            <td>no-cache</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- API Documentation -->
            <div class="card">
                <div class="card-header bg-white">
                    <h5 class="mb-0">API Documentation</h5>
                </div>
                <div class="card-body">
                    <div id="no-api-selected" class="text-center py-5">
                        <div class="api-placeholder">
                            <i class="fas fa-book text-muted"></i>
                        </div>
                        <p class="text-muted mt-3">Select a platform and endpoint to view documentation</p>
                    </div>
                    
                    <div id="api-documentation" class="d-none">
                        <h5 id="doc-endpoint-title">Get Ad Accounts</h5>
                        <p id="doc-endpoint-description" class="text-muted">Returns a list of ad accounts that the current user has access to.</p>
                        
                        <div class="mb-3">
                            <h6>Endpoint</h6>
                            <div class="code-inline">/me/adaccounts</div>
                        </div>
                        
                        <div class="mb-3">
                            <h6>Parameters</h6>
                            <table class="table table-sm">
                                <thead class="table-light">
                                    <tr>
                                        <th>Name</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                        <th>Required</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>fields</td>
                                        <td>string</td>
                                        <td>Comma-separated list of fields to return</td>
                                        <td>No</td>
                                    </tr>
                                    <tr>
                                        <td>limit</td>
                                        <td>integer</td>
                                        <td>Number of results to return</td>
                                        <td>No</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <div>
                            <h6>Response Format</h6>
                            <div class="code-inline">
                                <pre><code class="language-json">{
  "data": [
    {
      "id": "act_123456789",
      "name": "Business Account",
      "currency": "USD",
      "account_status": 1
    }
  ]
}</code></pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block styles %}
<style>
    .method-selector .btn {
        border-radius: 0;
    }
    
    .method-selector .btn:first-child {
        border-top-left-radius: 0.25rem;
        border-bottom-left-radius: 0.25rem;
    }
    
    .method-selector .btn:last-child {
        border-top-right-radius: 0.25rem;
        border-bottom-right-radius: 0.25rem;
    }
    
    .code-editor {
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
        background-color: #f8f9fa;
        max-height: 400px;
        overflow: auto;
    }
    
    .code-editor pre {
        margin: 0;
        padding: 1rem;
    }
    
    .code-inline {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
        padding: 0.5rem;
        font-family: monospace;
        overflow: auto;
    }
    
    .api-placeholder {
        font-size: 3rem;
        opacity: 0.2;
    }
</style>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Populate endpoints when platform changes
        const platformSelect = document.getElementById('platform');
        const endpointSelect = document.getElementById('endpoint');
        
        // Endpoint data by platform
        const endpoints = {
            meta: [
                { value: '/me/adaccounts', name: 'Get Ad Accounts', method: 'GET' },
                { value: '/{ad_account_id}/insights', name: 'Get Campaign Insights', method: 'GET' },
                { value: '/{ad_account_id}/campaigns', name: 'Create Campaign', method: 'POST' }
            ],
            google: [
                { value: '/customers/{customer_id}/campaigns', name: 'Get Campaigns', method: 'GET' },
                { value: '/customers/{customer_id}/googleAds:search', name: 'Get Campaign Metrics', method: 'POST' },
                { value: '/customers/{customer_id}/campaigns:mutate', name: 'Create Campaign', method: 'POST' }
            ],
            twitter: [
                { value: '/accounts', name: 'Get Accounts', method: 'GET' },
                { value: '/stats/accounts/{account_id}', name: 'Get Campaign Analytics', method: 'GET' },
                { value: '/accounts/{account_id}/campaigns', name: 'Create Campaign', method: 'POST' }
            ],
            linkedin: [
                { value: '/adAccountsV2', name: 'Get Ad Accounts', method: 'GET' },
                { value: '/adAnalyticsV2', name: 'Get Campaign Analytics', method: 'GET' },
                { value: '/adCampaignsV2', name: 'Create Campaign', method: 'POST' }
            ]
        };
        
        platformSelect.addEventListener('change', function() {
            // Clear and disable endpoint select if no platform selected
            if (!this.value) {
                endpointSelect.innerHTML = '<option value="">Select an endpoint</option>';
                endpointSelect.disabled = true;
                return;
            }
            
            // Enable endpoint select and populate options
            endpointSelect.disabled = false;
            endpointSelect.innerHTML = '<option value="">Select an endpoint</option>';
            
            // Add endpoints for selected platform
            const platformEndpoints = endpoints[this.value] || [];
            platformEndpoints.forEach(endpoint => {
                const option = document.createElement('option');
                option.value = endpoint.value;
                option.text = endpoint.name;
                option.dataset.method = endpoint.method;
                endpointSelect.appendChild(option);
            });
        });
        
        // Set method when endpoint changes
        endpointSelect.addEventListener('change', function() {
            if (!this.value) return;
            
            const selectedOption = this.options[this.selectedIndex];
            const method = selectedOption.dataset.method || 'GET';
            
            // Select the appropriate method radio button
            document.getElementById(`method-${method.toLowerCase()}`).checked = true;
            
            // Show API documentation
            document.getElementById('no-api-selected').classList.add('d-none');
            document.getElementById('api-documentation').classList.remove('d-none');
            
            // Update documentation content
            document.getElementById('doc-endpoint-title').textContent = selectedOption.text;
            document.getElementById('doc-endpoint-description').textContent = `This endpoint allows you to ${selectedOption.text.toLowerCase()}.`;
        });
        
        // Add parameter button functionality
        document.getElementById('add-param').addEventListener('click', function() {
            const container = document.getElementById('parameters-container');
            const paramRow = document.createElement('div');
            paramRow.className = 'row mb-2 parameter-row';
            paramRow.innerHTML = `
                <div class="col-5">
                    <input type="text" class="form-control param-key" placeholder="Key">
                </div>
                <div class="col-6">
                    <input type="text" class="form-control param-value" placeholder="Value">
                </div>
                <div class="col-1">
                    <button type="button" class="btn btn-outline-danger remove-param">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            container.appendChild(paramRow);
            
            // Add event listener to the new remove button
            paramRow.querySelector('.remove-param').addEventListener('click', function() {
                container.removeChild(paramRow);
            });
        });
        
        // Initial event delegation for remove parameter buttons
        document.getElementById('parameters-container').addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-param') || e.target.parentElement.classList.contains('remove-param')) {
                const button = e.target.classList.contains('remove-param') ? e.target : e.target.parentElement;
                const row = button.closest('.parameter-row');
                row.parentElement.removeChild(row);
            }
        });
        
        // Reset form button
        document.getElementById('reset-form').addEventListener('click', function() {
            document.getElementById('apiRequestForm').reset();
            
            // Clear parameters except the first one
            const container = document.getElementById('parameters-container');
            const paramRows = container.querySelectorAll('.parameter-row');
            for (let i = 1; i < paramRows.length; i++) {
                container.removeChild(paramRows[i]);
            }
            
            // Clear first parameter inputs
            const firstRow = container.querySelector('.parameter-row');
            if (firstRow) {
                firstRow.querySelector('.param-key').value = '';
                firstRow.querySelector('.param-value').value = '';
            }
            
            // Reset request body
            document.getElementById('request-body-code').textContent = '{\n  "key": "value"\n}';
            
            // Reset documentation panel
            document.getElementById('no-api-selected').classList.remove('d-none');
            document.getElementById('api-documentation').classList.add('d-none');
        });
        
        // Send request button
        document.getElementById('apiRequestForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const platform = document.getElementById('platform').value;
            const endpoint = document.getElementById('endpoint').value;
            const method = document.querySelector('input[name="method"]:checked').value;
            
            // For demo purposes, update response based on selections
            const responseStatus = document.querySelector('.response-status');
            const responseCode = document.getElementById('response-body-code');
            
            // Update status to success
            responseStatus.textContent = '200 OK';
            responseStatus.className = 'badge bg-success response-status';
            
            // Update response time
            document.querySelector('.response-time').textContent = `${Math.floor(Math.random() * 100) + 100} ms`;
            
            // Update response body based on platform and endpoint
            if (platform === 'meta') {
                responseCode.textContent = {{ sample_responses.meta_accounts|tojson }};
            } else if (platform === 'google') {
                responseCode.textContent = {{ sample_responses.google_campaigns|tojson }};
            } else if (platform === 'twitter') {
                responseCode.textContent = {{ sample_responses.twitter_analytics|tojson }};
            } else {
                responseCode.textContent = '{\n  "data": {\n    "result": "success"\n  }\n}';
            }
        });
    });
</script>
{% endblock %} """)

# Add routes for job openings
@app.route('/jobs')
def job_openings_list():
    """View list of job openings."""
    # In a real app, this would fetch job openings from the database
    job_openings = [
        {"id": 1, "title": "Senior Software Engineer", "company": "Tech Solutions Inc", "location": "Remote", "posted_date": "2025-03-15"},
        {"id": 2, "title": "Marketing Manager", "company": "Brand Builders", "location": "New York, NY", "posted_date": "2025-03-20"},
        {"id": 3, "title": "UX Designer", "company": "Creative Designs", "location": "San Francisco, CA", "posted_date": "2025-03-22"},
        {"id": 4, "title": "Data Scientist", "company": "Data Analytics Ltd", "location": "Remote", "posted_date": "2025-03-25"},
        {"id": 5, "title": "Product Manager", "company": "Tech Solutions Inc", "location": "Austin, TX", "posted_date": "2025-03-26"}
    ]
    return render_template('dashboard/job_openings.html', job_openings=job_openings)

@app.route('/jobs/create')
def job_openings_create():
    """Create a new job opening."""
    return render_template('dashboard/job_create.html')
    
@app.route('/candidates')
def candidates_list():
    """View list of candidates."""
    # In a real app, this would fetch candidates from the database
    candidates = [
        {"id": 1, "name": "John Smith", "skills": "Python, JavaScript, React", "location": "Remote", "status": "Active"},
        {"id": 2, "name": "Emily Johnson", "skills": "Marketing, Social Media, Content Creation", "location": "New York, NY", "status": "Interviewing"},
        {"id": 3, "name": "Michael Brown", "skills": "UX Design, Figma, Adobe Creative Suite", "location": "San Francisco, CA", "status": "Active"},
        {"id": 4, "name": "David Wilson", "skills": "Data Science, Python, Machine Learning", "location": "Remote", "status": "New"},
        {"id": 5, "name": "Sarah Miller", "skills": "Product Management, Agile, JIRA", "location": "Austin, TX", "status": "Hired"}
    ]
    return render_template('dashboard/candidates.html', candidates=candidates)

# Create simple template files for these new routes
os.makedirs(os.path.join(app.template_folder, 'dashboard'), exist_ok=True)

# Create job_openings.html
job_openings_template = os.path.join(app.template_folder, 'dashboard', 'job_openings.html')
if not os.path.exists(job_openings_template):
    with open(job_openings_template, 'w') as f:
        f.write("""{% extends "simple_base.html" %}

{% block title %}Job Openings | MagnetoCursor{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="mb-1">Job Openings</h1>
            <p class="text-muted">Manage and publish job openings across platforms</p>
        </div>
        <div>
            <a href="{{ url_for('job_openings_create') }}" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i> Create Job Opening
            </a>
        </div>
    </div>

    <div class="card">
        <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">All Job Openings</h5>
                <div class="input-group" style="width: 300px;">
                    <input type="text" class="form-control" placeholder="Search jobs...">
                    <button class="btn btn-outline-secondary" type="button">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </div>
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Location</th>
                            <th>Posted Date</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for job in job_openings %}
                        <tr>
                            <td>{{ job.title }}</td>
                            <td>{{ job.company }}</td>
                            <td>{{ job.location }}</td>
                            <td>{{ job.posted_date }}</td>
                            <td><span class="badge bg-success">Active</span></td>
                            <td>
                                <div class="btn-group">
                                    <a href="#" class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                    <a href="#" class="btn btn-sm btn-outline-secondary">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <div class="btn-group">
                                        <button type="button" class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                                            <i class="fas fa-ellipsis-v"></i>
                                        </button>
                                        <ul class="dropdown-menu dropdown-menu-end">
                                            <li><a class="dropdown-item" href="#"><i class="fas fa-ad me-2"></i>Create Campaign</a></li>
                                            <li><a class="dropdown-item" href="#"><i class="fas fa-share me-2"></i>Share</a></li>
                                            <li><hr class="dropdown-divider"></li>
                                            <li><a class="dropdown-item text-danger" href="#"><i class="fas fa-trash me-2"></i>Delete</a></li>
                                        </ul>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}""")

# Create job_create.html
job_create_template = os.path.join(app.template_folder, 'dashboard', 'job_create.html')
if not os.path.exists(job_create_template):
    with open(job_create_template, 'w') as f:
        f.write("""{% extends "simple_base.html" %}

{% block title %}Create Job Opening | MagnetoCursor{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="mb-4">
        <h1 class="mb-1">Create Job Opening</h1>
        <p class="text-muted">Add a new job opening to your account</p>
    </div>

    <div class="card">
        <div class="card-body">
            <form>
                <div class="mb-3">
                    <label for="job-title" class="form-label">Job Title</label>
                    <input type="text" class="form-control" id="job-title" placeholder="e.g. Senior Software Engineer">
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label for="company" class="form-label">Company</label>
                        <input type="text" class="form-control" id="company" placeholder="e.g. Tech Solutions Inc">
                    </div>
                    <div class="col-md-6">
                        <label for="location" class="form-label">Location</label>
                        <input type="text" class="form-control" id="location" placeholder="e.g. Remote, New York, NY">
                    </div>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label for="job-type" class="form-label">Job Type</label>
                        <select class="form-select" id="job-type">
                            <option>Full-time</option>
                            <option>Part-time</option>
                            <option>Contract</option>
                            <option>Internship</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <label for="salary-range" class="form-label">Salary Range</label>
                        <input type="text" class="form-control" id="salary-range" placeholder="e.g. $100,000 - $130,000">
                    </div>
                </div>
                
                <div class="mb-3">
                    <label for="description" class="form-label">Job Description</label>
                    <textarea class="form-control" id="description" rows="6" placeholder="Enter job description..."></textarea>
                </div>
                
                <div class="mb-3">
                    <label for="requirements" class="form-label">Requirements</label>
                    <textarea class="form-control" id="requirements" rows="4" placeholder="Enter job requirements..."></textarea>
                </div>
                
                <div class="mb-3">
                    <label for="benefits" class="form-label">Benefits</label>
                    <textarea class="form-control" id="benefits" rows="4" placeholder="Enter job benefits..."></textarea>
                </div>
                
                <div class="d-flex justify-content-between mt-4">
                    <a href="{{ url_for('job_openings_list') }}" class="btn btn-outline-secondary">Cancel</a>
                    <button type="submit" class="btn btn-primary">Create Job Opening</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}""")

# Create candidates.html
candidates_template = os.path.join(app.template_folder, 'dashboard', 'candidates.html')
if not os.path.exists(candidates_template):
    with open(candidates_template, 'w') as f:
        f.write("""{% extends "simple_base.html" %}

{% block title %}Candidates | MagnetoCursor{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="mb-1">Candidates</h1>
            <p class="text-muted">Manage and track candidates for your job openings</p>
        </div>
        <div>
            <button class="btn btn-primary">
                <i class="fas fa-plus me-2"></i> Add Candidate
            </button>
        </div>
    </div>

    <div class="card">
        <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">All Candidates</h5>
                <div class="input-group" style="width: 300px;">
                    <input type="text" class="form-control" placeholder="Search candidates...">
                    <button class="btn btn-outline-secondary" type="button">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </div>
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Name</th>
                            <th>Skills</th>
                            <th>Location</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for candidate in candidates %}
                        <tr>
                            <td>{{ candidate.name }}</td>
                            <td>{{ candidate.skills }}</td>
                            <td>{{ candidate.location }}</td>
                            <td>
                                {% if candidate.status == 'Active' %}
                                <span class="badge bg-success">Active</span>
                                {% elif candidate.status == 'Interviewing' %}
                                <span class="badge bg-primary">Interviewing</span>
                                {% elif candidate.status == 'New' %}
                                <span class="badge bg-info">New</span>
                                {% elif candidate.status == 'Hired' %}
                                <span class="badge bg-warning">Hired</span>
                                {% else %}
                                <span class="badge bg-secondary">{{ candidate.status }}</span>
                                {% endif %}
                            </td>
                            <td>
                                <div class="btn-group">
                                    <a href="#" class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                    <a href="#" class="btn btn-sm btn-outline-secondary">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <div class="btn-group">
                                        <button type="button" class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                                            <i class="fas fa-ellipsis-v"></i>
                                        </button>
                                        <ul class="dropdown-menu dropdown-menu-end">
                                            <li><a class="dropdown-item" href="#"><i class="fas fa-paper-plane me-2"></i>Contact</a></li>
                                            <li><a class="dropdown-item" href="#"><i class="fas fa-briefcase me-2"></i>Assign to Job</a></li>
                                            <li><hr class="dropdown-divider"></li>
                                            <li><a class="dropdown-item text-danger" href="#"><i class="fas fa-trash me-2"></i>Delete</a></li>
                                        </ul>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}""")

# Run the app
if __name__ == '__main__':
    logger.info(f"Starting app with database at {db_path}")
    app.run(debug=True, port=5002)