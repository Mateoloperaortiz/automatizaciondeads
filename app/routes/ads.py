from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models.ad_campaign import AdCampaign
from app.models.job_opening import JobOpening
from app import db
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime

ads_bp = Blueprint('ads', __name__, url_prefix='/ads')

@ads_bp.route('/gallery')
def gallery():
    """Ad gallery page with filtering options."""
    # Get filter parameters
    platform = request.args.get('platform', 'all')
    status = request.args.get('status', 'all')
    
    # Base query
    query = db.session.query(AdCampaign)
    
    # Apply filters
    if platform != 'all':
        query = query.filter(AdCampaign.platform_id == platform)
    
    if status != 'all':
        query = query.filter(AdCampaign.status == status)
    
    # Get campaigns with ad content
    campaigns = query.filter(
        (AdCampaign.ad_headline.isnot(None)) | 
        (AdCampaign.ad_content.isnot(None))
    ).order_by(AdCampaign.updated_at.desc()).all()
    
    # Get job openings for these campaigns
    job_ids = [campaign.job_opening_id for campaign in campaigns]
    jobs = JobOpening.query.filter(JobOpening.id.in_(job_ids)).all()
    jobs_dict = {job.id: job for job in jobs}
    
    # Extract platform stats
    platform_stats = db.session.query(
        AdCampaign.platform_id, 
        db.func.count(AdCampaign.id)
    ).group_by(AdCampaign.platform_id).all()
    
    platform_counts = {platform_id: count for platform_id, count in platform_stats}
    
    return render_template(
        'ads/gallery.html', 
        campaigns=campaigns,
        jobs=jobs_dict,
        platform_counts=platform_counts,
        selected_platform=platform,
        selected_status=status
    )

@ads_bp.route('/api/creatives', methods=['GET'])
def list_creatives():
    """API endpoint to get ad creatives."""
    platform = request.args.get('platform', 'all')
    status = request.args.get('status', 'all')
    
    # Base query
    query = db.session.query(AdCampaign)
    
    # Apply filters
    if platform != 'all':
        query = query.filter(AdCampaign.platform_id == platform)
    
    if status != 'all':
        query = query.filter(AdCampaign.status == status)
    
    # Get campaigns with ad content
    campaigns = query.filter(
        (AdCampaign.ad_headline.isnot(None)) | 
        (AdCampaign.ad_content.isnot(None))
    ).order_by(AdCampaign.updated_at.desc()).all()
    
    # Format response
    result = []
    for campaign in campaigns:
        # Get job details
        job = JobOpening.query.get(campaign.job_opening_id)
        job_title = job.title if job else "Unknown Job"
        
        # Get platform-specific content if available
        platform_content = {}
        if campaign.platform_specific_content:
            try:
                platform_content = json.loads(campaign.platform_specific_content)
            except:
                platform_content = {}
        
        # Create creative object
        creative = {
            'id': campaign.id,
            'title': campaign.title,
            'platform_id': campaign.platform_id,
            'job_title': job_title,
            'headline': campaign.ad_headline or '',
            'text': campaign.ad_text or '',
            'cta': campaign.ad_cta or 'apply_now',
            'image_url': campaign.ad_image_url or '',
            'status': campaign.status,
            'platform_content': platform_content,
            'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
            'updated_at': campaign.updated_at.isoformat() if campaign.updated_at else None
        }
        
        result.append(creative)
    
    return jsonify({
        'success': True,
        'data': result
    })

@ads_bp.route('/api/uploads/image', methods=['POST'])
def upload_image():
    """API endpoint to upload ad images."""
    if 'image' not in request.files:
        return jsonify({
            'success': False,
            'message': 'No image file provided'
        }), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'message': 'No image selected'
        }), 400
    
    # Check file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({
            'success': False,
            'message': 'Invalid file type. Allowed types: png, jpg, jpeg, gif'
        }), 400
    
    # Create uploads directory if it doesn't exist
    upload_folder = os.path.join('app', 'static', 'uploads', 'ads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = secure_filename(f"{timestamp}_{file.filename}")
    file_path = os.path.join(upload_folder, filename)
    
    # Save file
    file.save(file_path)
    
    # Create URL path
    url_path = f"/static/uploads/ads/{filename}"
    
    return jsonify({
        'success': True,
        'url': url_path,
        'message': 'Image uploaded successfully'
    })

@ads_bp.route('/templates')
def templates():
    """Ad templates page."""
    return render_template('ads/templates.html')

@ads_bp.route('/creative/<int:campaign_id>')
def creative_detail(campaign_id):
    """View a specific ad creative."""
    campaign = AdCampaign.query.get_or_404(campaign_id)
    job = JobOpening.query.get_or_404(campaign.job_opening_id)
    
    return render_template('ads/creative_detail.html', campaign=campaign, job=job)

@ads_bp.route('/visual-editor', methods=['GET'])
def visual_editor():
    """Visual editor for creating ad content."""
    campaign_id = request.args.get('campaign_id', None)
    template_id = request.args.get('template', None)
    
    # If campaign_id is provided, load existing campaign data
    campaign = None
    if campaign_id:
        campaign = AdCampaign.query.get_or_404(campaign_id)
    
    return render_template('ads/visual_editor.html', campaign=campaign, campaign_id=campaign_id, template_id=template_id)

@ads_bp.route('/save-ad', methods=['POST'])
def save_ad():
    """Save ad content from visual editor."""
    campaign_id = request.form.get('campaign_id')
    ad_headline = request.form.get('ad_headline')
    ad_text = request.form.get('ad_text')
    ad_cta = request.form.get('ad_cta')
    ad_image_url = request.form.get('ad_image_url')
    platform_specific = request.form.get('platform_specific')
    
    # Validate required fields
    if not ad_headline or not ad_text:
        flash('Ad headline and text are required', 'error')
        return redirect(url_for('ads.visual_editor', campaign_id=campaign_id))
    
    # Update existing campaign or create new one
    if campaign_id:
        campaign = AdCampaign.query.get_or_404(campaign_id)
        campaign.ad_headline = ad_headline
        campaign.ad_text = ad_text
        campaign.ad_cta = ad_cta
        campaign.ad_image_url = ad_image_url
        campaign.platform_specific_content = platform_specific
        
        db.session.commit()
        flash('Ad content updated successfully', 'success')
        return redirect(url_for('ads.creative_detail', campaign_id=campaign.id))
    else:
        # If no campaign_id, create a new campaign
        # This would typically be redirected to the campaign creation form with ad data
        flash('Please create a campaign first', 'warning')
        return redirect(url_for('campaigns.create_campaign_form', 
                                ad_headline=ad_headline, 
                                ad_text=ad_text,
                                ad_cta=ad_cta,
                                ad_image_url=ad_image_url,
                                platform_specific=platform_specific))

@ads_bp.route('/editor-open-button')
def editor_open_button():
    """Render a button to open the visual editor directly from other pages."""
    return render_template('ads/editor_button.html')