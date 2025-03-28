from flask import Blueprint, render_template, jsonify
from app.models.job_opening import JobOpening
from app.models.ad_campaign import AdCampaign
from app.models.candidate import Candidate
from app.models.segment import Segment
from sqlalchemy import func
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage route."""
    return render_template('index.html', title='Ad Automation P-01')

@main_bp.route('/dashboard')
def dashboard():
    """Main dashboard route."""
    # Get counts for dashboard stats
    job_count = db.session.query(func.count(JobOpening.id)).scalar() or 0
    campaign_count = db.session.query(func.count(AdCampaign.id)).scalar() or 0
    candidate_count = db.session.query(func.count(Candidate.id)).scalar() or 0
    segment_count = db.session.query(func.count(Segment.id)).scalar() or 0
    
    # Get recent campaigns
    recent_campaigns = AdCampaign.query.order_by(AdCampaign.created_at.desc()).limit(5).all()
    
    # Get recent jobs
    recent_jobs = JobOpening.query.order_by(JobOpening.created_at.desc()).limit(5).all()
    
    # Mock data for chart (in a real app, this would come from the database)
    platform_names = ['Meta', 'X', 'Google', 'TikTok', 'Snapchat']
    impressions_data = [12500, 8700, 15200, 6300, 4800]
    clicks_data = [350, 420, 280, 190, 120]
    applications_data = [25, 18, 32, 12, 8]
    
    return render_template(
        'dashboard/dashboard.html',
        job_count=job_count,
        campaign_count=campaign_count,
        candidate_count=candidate_count,
        segment_count=segment_count,
        recent_campaigns=recent_campaigns,
        recent_jobs=recent_jobs,
        platform_names=platform_names,
        impressions_data=impressions_data,
        clicks_data=clicks_data,
        applications_data=applications_data
    )

@main_bp.route('/health')
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Ad Automation P-01',
        'version': '0.1.0'
    }) 