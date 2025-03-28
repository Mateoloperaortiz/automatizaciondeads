from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models.ad_campaign import AdCampaign, SocialMediaPlatform
from app.models.job_opening import JobOpening
from app.models.user import User
from app.models.collaboration import Team, TeamMember, CollaborationRole, CampaignCollaborator
from app.utils.access_control import analyst_required
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType, NotificationCategory
from app.utils.realtime import broadcast_entity_change, entity_changed
from app import db
import logging
import random

campaigns_bp = Blueprint('campaigns', __name__, url_prefix='/campaigns')
logger = logging.getLogger(__name__)

@campaigns_bp.route('/')
@login_required
def list_campaigns():
    """Get all ad campaigns the user has access to."""
    # Get campaigns owned by the user
    owned_campaigns = AdCampaign.query.filter_by(user_id=current_user.id).all()
    
    # Get campaigns the user is a collaborator on
    collab_campaign_ids = db.session.query(CampaignCollaborator.campaign_id).filter_by(
        user_id=current_user.id
    ).all()
    collab_campaign_ids = [c[0] for c in collab_campaign_ids]
    
    collaborating_campaigns = AdCampaign.query.filter(
        AdCampaign.id.in_(collab_campaign_ids)
    ).all() if collab_campaign_ids else []
    
    # If user is admin, get all campaigns
    if current_user.is_admin():
        all_campaigns = AdCampaign.query.all()
        return render_template(
            'campaigns/list.html', 
            owned_campaigns=owned_campaigns,
            collaborating_campaigns=collaborating_campaigns,
            all_campaigns=all_campaigns,
            is_admin=True
        )
    
    return render_template(
        'campaigns/list.html', 
        owned_campaigns=owned_campaigns,
        collaborating_campaigns=collaborating_campaigns,
        is_admin=False
    )

@campaigns_bp.route('/<int:campaign_id>')
@login_required
def get_campaign(campaign_id):
    """Get a specific ad campaign."""
    campaign = AdCampaign.query.get_or_404(campaign_id)
    
    # Check if user has access to this campaign
    has_access = False
    user_role = None
    
    # User is the owner
    if campaign.owner and campaign.owner.id == current_user.id:
        has_access = True
        user_role = 'owner'
    
    # User is a collaborator
    if not has_access:
        collab = CampaignCollaborator.query.filter_by(
            campaign_id=campaign.id,
            user_id=current_user.id
        ).first()
        
        if collab:
            has_access = True
            user_role = collab.role
            
            # Update last viewed timestamp
            collab.last_viewed = db.func.now()
            db.session.commit()
    
    # User is an admin
    if not has_access and current_user.is_admin():
        has_access = True
        user_role = 'admin'
    
    if not has_access:
        flash('You do not have access to this campaign.', 'danger')
        return redirect(url_for('campaigns.list_campaigns'))
    
    # Get collaborators for the campaign
    collaborators = CampaignCollaborator.query.filter_by(
        campaign_id=campaign.id
    ).all()
    
    # Get other users currently viewing this campaign (viewed in last 5 minutes)
    from datetime import datetime, timedelta
    recent_time = datetime.utcnow() - timedelta(minutes=5)
    
    current_viewers = CampaignCollaborator.query.filter(
        CampaignCollaborator.campaign_id == campaign.id,
        CampaignCollaborator.user_id != current_user.id,
        CampaignCollaborator.last_viewed >= recent_time
    ).all()
    
    return render_template(
        'campaigns/detail.html', 
        campaign=campaign, 
        user_role=user_role,
        collaborators=collaborators,
        current_viewers=current_viewers,
        can_edit=(user_role in ['owner', 'admin', 'editor'])
    )

@campaigns_bp.route('/create')
@login_required
@analyst_required
def create_campaign_form():
    """Show form to create a new ad campaign."""
    jobs = JobOpening.query.filter_by(active=True).all()
    platforms = SocialMediaPlatform.query.filter_by(active=True).all()
    return render_template('campaigns/create.html', jobs=jobs, platforms=platforms)

# API routes
@campaigns_bp.route('/api/campaigns', methods=['GET'])
@login_required
def api_list_campaigns():
    """API endpoint to get all ad campaigns the user has access to."""
    # Get campaigns owned by the user
    owned_campaigns = AdCampaign.query.filter_by(user_id=current_user.id).all()
    
    # Get campaigns the user is a collaborator on
    collab_campaign_ids = db.session.query(CampaignCollaborator.campaign_id).filter_by(
        user_id=current_user.id
    ).all()
    collab_campaign_ids = [c[0] for c in collab_campaign_ids]
    
    collaborating_campaigns = AdCampaign.query.filter(
        AdCampaign.id.in_(collab_campaign_ids)
    ).all() if collab_campaign_ids else []
    
    # Combine both sets of campaigns
    campaign_list = owned_campaigns + collaborating_campaigns
    
    # If user is admin, get all campaigns
    if current_user.is_admin():
        campaign_list = AdCampaign.query.all()
    
    return jsonify({
        'success': True,
        'data': [campaign.to_dict(include_collaborators=True) for campaign in campaign_list]
    })

@campaigns_bp.route('/api/campaigns/<int:campaign_id>', methods=['GET'])
@login_required
def api_get_campaign(campaign_id):
    """API endpoint to get a specific ad campaign."""
    campaign = AdCampaign.query.get_or_404(campaign_id)
    
    # Check if user has access to this campaign
    has_access = False
    
    # User is the owner
    if campaign.owner and campaign.owner.id == current_user.id:
        has_access = True
    
    # User is a collaborator
    if not has_access:
        collab = CampaignCollaborator.query.filter_by(
            campaign_id=campaign.id,
            user_id=current_user.id
        ).first()
        
        if collab:
            has_access = True
            
            # Update last viewed timestamp
            collab.last_viewed = db.func.now()
            db.session.commit()
    
    # User is an admin
    if not has_access and current_user.is_admin():
        has_access = True
    
    if not has_access:
        return jsonify({
            'success': False,
            'message': 'You do not have access to this campaign.'
        }), 403
    
    return jsonify({
        'success': True,
        'data': campaign.to_dict(include_collaborators=True)
    })

@campaigns_bp.route('/api/campaigns', methods=['POST'])
@login_required
@analyst_required
@broadcast_entity_change('campaign', 
    get_entity_id=lambda resp: resp.get('data', {}).get('id'),
    get_entity_data=lambda resp: resp.get('data', {}))
def api_create_campaign():
    """API endpoint to create a new ad campaign."""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('title') or not data.get('platform_id') or not data.get('job_opening_id'):
        return jsonify({
            'success': False,
            'message': 'Missing required fields'
        }), 400
    
    # Check if job opening exists
    job = JobOpening.query.get(data.get('job_opening_id'))
    if not job:
        return jsonify({
            'success': False,
            'message': 'Job opening not found'
        }), 404
    
    # Check if platform exists
    platform = SocialMediaPlatform.query.get(data.get('platform_id'))
    if not platform:
        return jsonify({
            'success': False,
            'message': 'Social media platform not found'
        }), 404
    
    # Process platform-specific content if available
    platform_specific = {}
    if data.get('platform_specific'):
        platform_specific = data.get('platform_specific')
        
    # Create new campaign with enhanced ad content fields
    new_campaign = AdCampaign(
        title=data.get('title'),
        description=data.get('description'),
        platform_id=data.get('platform_id'),
        job_opening_id=data.get('job_opening_id'),
        segment_id=data.get('segment_id'),
        budget=data.get('budget'),
        status='draft',
        # Legacy field, kept for backward compatibility
        ad_content=data.get('ad_content'),
        # New enhanced fields
        ad_headline=data.get('ad_headline'),
        ad_text=data.get('ad_text'),
        ad_cta=data.get('ad_cta'),
        ad_image_url=data.get('ad_image_url'),
        platform_specific_content=AdCampaign.serialize_ad_content(platform_specific),
        user_id=current_user.id  # Set the current user as the campaign owner
    )
    
    db.session.add(new_campaign)
    db.session.commit()
    
    # Create notification for campaign creation
    NotificationService.create_notification(
        title="Campaign Created",
        message=f"You've successfully created a new campaign: '{new_campaign.title}'.",
        type=NotificationType.SUCCESS,
        category=NotificationCategory.CAMPAIGN,
        related_entity_type="campaign",
        related_entity_id=new_campaign.id,
        user_id=current_user.id
    )
    
    logger.info(f"User {current_user.username} created new campaign: {new_campaign.title} (ID: {new_campaign.id})")
    return jsonify({
        'success': True,
        'message': 'Ad campaign created successfully',
        'data': new_campaign.to_dict(include_collaborators=True)
    }), 201

@campaigns_bp.route('/api/campaigns/<int:campaign_id>', methods=['PUT'])
@login_required
@broadcast_entity_change('campaign')
def api_update_campaign(campaign_id):
    """API endpoint to update an ad campaign."""
    campaign = AdCampaign.query.get_or_404(campaign_id)
    data = request.get_json()
    
    # Check if user has permission to update this campaign
    has_permission = False
    
    # User is the owner
    if campaign.owner and campaign.owner.id == current_user.id:
        has_permission = True
    
    # User is an admin
    if not has_permission and current_user.is_admin():
        has_permission = True
    
    # User is a collaborator with editor role
    if not has_permission:
        collab = CampaignCollaborator.query.filter_by(
            campaign_id=campaign.id,
            user_id=current_user.id,
            role=CollaborationRole.EDITOR.value
        ).first()
        
        if collab:
            has_permission = True
    
    if not has_permission:
        return jsonify({
            'success': False,
            'message': 'You do not have permission to update this campaign.'
        }), 403
    
    # Update basic fields
    if 'title' in data:
        campaign.title = data['title']
    if 'description' in data:
        campaign.description = data['description']
    if 'segment_id' in data:
        campaign.segment_id = data['segment_id']
    if 'budget' in data:
        campaign.budget = data['budget']
    if 'status' in data:
        # Store original status for notification
        original_status = campaign.status
        new_status = data['status']
        
        # Only create notification if status is actually changing
        if original_status != new_status:
            campaign.status = new_status
            
            # Import notification service
            from app.services.notification_service import NotificationService
            from app.models.notification import NotificationType, NotificationCategory
            
            # Get job opening for notification if available
            job_opening = None
            if campaign.job_opening_id:
                from app.models.job_opening import JobOpening
                job_opening = JobOpening.query.get(campaign.job_opening_id)
            
            # Create status change notification with appropriate type/message
            if new_status == 'active':
                NotificationService.create_notification(
                    title="Campaign Activated",
                    message=f"Campaign '{campaign.title}' has been activated.",
                    type=NotificationType.SUCCESS,
                    category=NotificationCategory.CAMPAIGN,
                    related_entity_type="campaign",
                    related_entity_id=campaign.id,
                    extra_data={
                        'previous_status': original_status,
                        'job_title': job_opening.title if job_opening else None
                    }
                )
                
                # Manually trigger real-time status change event
                entity_changed(
                    entity_type='campaign',
                    entity_id=campaign.id,
                    update_type='status_change',
                    entity_data=campaign.to_dict()
                )
                
            elif new_status == 'paused':
                NotificationService.create_notification(
                    title="Campaign Paused",
                    message=f"Campaign '{campaign.title}' has been paused.",
                    type=NotificationType.INFO,
                    category=NotificationCategory.CAMPAIGN,
                    related_entity_type="campaign",
                    related_entity_id=campaign.id,
                    extra_data={
                        'previous_status': original_status,
                        'job_title': job_opening.title if job_opening else None
                    }
                )
                
                # Manually trigger real-time status change event
                entity_changed(
                    entity_type='campaign',
                    entity_id=campaign.id,
                    update_type='status_change',
                    entity_data=campaign.to_dict()
                )
                
            elif new_status == 'completed':
                NotificationService.create_notification(
                    title="Campaign Completed",
                    message=f"Campaign '{campaign.title}' has been marked as completed.",
                    type=NotificationType.SUCCESS,
                    category=NotificationCategory.CAMPAIGN,
                    related_entity_type="campaign",
                    related_entity_id=campaign.id,
                    extra_data={
                        'previous_status': original_status,
                        'job_title': job_opening.title if job_opening else None
                    }
                )
                
                # Manually trigger real-time status change event
                entity_changed(
                    entity_type='campaign',
                    entity_id=campaign.id,
                    update_type='status_change',
                    entity_data=campaign.to_dict()
                )
                
            elif new_status == 'cancelled':
                NotificationService.create_notification(
                    title="Campaign Cancelled",
                    message=f"Campaign '{campaign.title}' has been cancelled.",
                    type=NotificationType.WARNING,
                    category=NotificationCategory.CAMPAIGN,
                    related_entity_type="campaign",
                    related_entity_id=campaign.id,
                    extra_data={
                        'previous_status': original_status,
                        'job_title': job_opening.title if job_opening else None
                    }
                )
                
                # Manually trigger real-time status change event
                entity_changed(
                    entity_type='campaign',
                    entity_id=campaign.id,
                    update_type='status_change',
                    entity_data=campaign.to_dict()
                )
                
            else:
                # Generic status change notification
                NotificationService.create_notification(
                    title="Campaign Status Updated",
                    message=f"Campaign '{campaign.title}' status changed from '{original_status}' to '{new_status}'.",
                    type=NotificationType.INFO,
                    category=NotificationCategory.CAMPAIGN,
                    related_entity_type="campaign",
                    related_entity_id=campaign.id,
                    extra_data={
                        'previous_status': original_status,
                        'new_status': new_status,
                        'job_title': job_opening.title if job_opening else None
                    }
                )
                
                # Manually trigger real-time status change event
                entity_changed(
                    entity_type='campaign',
                    entity_id=campaign.id,
                    update_type='status_change',
                    entity_data=campaign.to_dict()
                )
        else:
            campaign.status = new_status  # Set anyway for consistency
    
    # Update ad content (legacy field)
    if 'ad_content' in data:
        campaign.ad_content = data['ad_content']
    
    # Update enhanced ad content fields
    if 'ad_headline' in data:
        campaign.ad_headline = data['ad_headline']
    if 'ad_text' in data:
        campaign.ad_text = data['ad_text']
    if 'ad_cta' in data:
        campaign.ad_cta = data['ad_cta']
    if 'ad_image_url' in data:
        campaign.ad_image_url = data['ad_image_url']
        
    # Update platform-specific content if available
    if 'platform_specific' in data:
        # Merge with existing content if any
        existing_content = {}
        if campaign.platform_specific_content:
            existing_content = AdCampaign.deserialize_ad_content(campaign.platform_specific_content)
        
        # Update with new data
        platform_name = SocialMediaPlatform.query.get(campaign.platform_id).name.lower()
        if platform_name in data['platform_specific']:
            existing_content[platform_name] = data['platform_specific'][platform_name]
            
        # Save merged content
        campaign.platform_specific_content = AdCampaign.serialize_ad_content(existing_content)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Ad campaign updated successfully',
        'data': campaign.to_dict()
    })

@campaigns_bp.route('/api/platforms', methods=['GET'])
def api_list_platforms():
    """API endpoint to get all social media platforms."""
    platforms = SocialMediaPlatform.query.all()
    return jsonify({
        'success': True,
        'data': [platform.to_dict() for platform in platforms]
    })

# Campaign sharing routes
@campaigns_bp.route('/<int:campaign_id>/share')
@login_required
def share_campaign_form(campaign_id):
    """Show form to share a campaign with users or teams."""
    campaign = AdCampaign.query.get_or_404(campaign_id)
    
    # Check if user is the owner or has editor access
    if not campaign.owner or campaign.owner.id != current_user.id:
        # Check if user is a collaborator with editor role
        collab = CampaignCollaborator.query.filter_by(
            campaign_id=campaign.id, 
            user_id=current_user.id, 
            role=CollaborationRole.EDITOR.value
        ).first()
        
        if not collab and not current_user.is_admin():
            flash('You do not have permission to share this campaign.', 'danger')
            return redirect(url_for('campaigns.get_campaign', campaign_id=campaign.id))
    
    # Get all users that are not already collaborators or the owner
    existing_user_ids = [collab.user_id for collab in campaign.collaborators.all()]
    if campaign.owner:
        existing_user_ids.append(campaign.owner.id)
    
    available_users = User.query.filter(
        User.id.notin_(existing_user_ids), 
        User.is_active == True
    ).all()
    
    # Get all teams the current user is a member of
    user_teams = db.session.query(Team).join(
        TeamMember, Team.id == TeamMember.team_id
    ).filter(
        TeamMember.user_id == current_user.id,
        Team.active == True
    ).all()
    
    # Get existing collaborators
    collaborators = CampaignCollaborator.query.filter_by(campaign_id=campaign.id).all()
    
    return render_template(
        'campaigns/share.html',
        campaign=campaign,
        available_users=available_users,
        available_teams=user_teams,
        collaborators=collaborators
    )

@campaigns_bp.route('/<int:campaign_id>/share/user', methods=['POST'])
@login_required
def share_with_user(campaign_id):
    """Share a campaign with a user."""
    campaign = AdCampaign.query.get_or_404(campaign_id)
    
    # Check if user is the owner or has editor access
    if not campaign.owner or campaign.owner.id != current_user.id:
        collab = CampaignCollaborator.query.filter_by(
            campaign_id=campaign.id, 
            user_id=current_user.id, 
            role=CollaborationRole.EDITOR.value
        ).first()
        
        if not collab and not current_user.is_admin():
            flash('You do not have permission to share this campaign.', 'danger')
            return redirect(url_for('campaigns.get_campaign', campaign_id=campaign.id))
    
    user_id = request.form.get('user_id')
    role = request.form.get('role')
    
    if not user_id or not role:
        flash('User and role are required.', 'danger')
        return redirect(url_for('campaigns.share_campaign_form', campaign_id=campaign.id))
    
    # Validate role
    if role not in [r.value for r in CollaborationRole]:
        role = CollaborationRole.VIEWER.value
    
    # Prevent adding owner as collaborator
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('campaigns.share_campaign_form', campaign_id=campaign.id))
    
    if campaign.owner and user.id == campaign.owner.id:
        flash('Cannot add the campaign owner as a collaborator.', 'danger')
        return redirect(url_for('campaigns.share_campaign_form', campaign_id=campaign.id))
    
    # Add user as collaborator
    campaign.add_collaborator(user, role=role)
    
    # Create notification for the user
    NotificationService.create_notification(
        title="Campaign Shared",
        message=f"{current_user.username} has shared '{campaign.title}' with you.",
        type=NotificationType.INFO,
        category=NotificationCategory.COLLABORATION,
        related_entity_type="campaign",
        related_entity_id=campaign.id,
        user_id=user.id,
        extra_data={
            'shared_by': current_user.username,
            'role': role
        }
    )
    
    logger.info(f"User {current_user.username} shared campaign {campaign.id} with user {user.username} as {role}")
    flash(f'Campaign shared with {user.username} as {role}.', 'success')
    return redirect(url_for('campaigns.share_campaign_form', campaign_id=campaign.id))

@campaigns_bp.route('/<int:campaign_id>/share/team', methods=['POST'])
@login_required
def share_with_team(campaign_id):
    """Share a campaign with all members of a team."""
    campaign = AdCampaign.query.get_or_404(campaign_id)
    
    # Check if user is the owner or has editor access
    if not campaign.owner or campaign.owner.id != current_user.id:
        collab = CampaignCollaborator.query.filter_by(
            campaign_id=campaign.id, 
            user_id=current_user.id, 
            role=CollaborationRole.EDITOR.value
        ).first()
        
        if not collab and not current_user.is_admin():
            flash('You do not have permission to share this campaign.', 'danger')
            return redirect(url_for('campaigns.get_campaign', campaign_id=campaign.id))
    
    team_id = request.form.get('team_id')
    role = request.form.get('role')
    
    if not team_id or not role:
        flash('Team and role are required.', 'danger')
        return redirect(url_for('campaigns.share_campaign_form', campaign_id=campaign.id))
    
    # Validate role
    if role not in [r.value for r in CollaborationRole]:
        role = CollaborationRole.VIEWER.value
    
    # Get team
    team = Team.query.get(team_id)
    if not team:
        flash('Team not found.', 'danger')
        return redirect(url_for('campaigns.share_campaign_form', campaign_id=campaign.id))
    
    # Verify user is a member of the team
    is_member = TeamMember.query.filter_by(
        team_id=team.id, user_id=current_user.id
    ).first() is not None
    
    if not is_member and not current_user.is_admin():
        flash('You must be a member of the team to share with it.', 'danger')
        return redirect(url_for('campaigns.share_campaign_form', campaign_id=campaign.id))
    
    # Get all team members
    members = TeamMember.query.filter_by(team_id=team.id).all()
    added_count = 0
    
    for member in members:
        # Skip if user is the campaign owner
        if campaign.owner and member.user_id == campaign.owner.id:
            continue
        
        # Add user as collaborator
        user = User.query.get(member.user_id)
        if user and user.is_active:
            campaign.add_collaborator(user, role=role)
            added_count += 1
            
            # Create notification for the user
            NotificationService.create_notification(
                title="Campaign Shared with Team",
                message=f"{current_user.username} has shared '{campaign.title}' with your team '{team.name}'.",
                type=NotificationType.INFO,
                category=NotificationCategory.COLLABORATION,
                related_entity_type="campaign",
                related_entity_id=campaign.id,
                user_id=user.id,
                extra_data={
                    'shared_by': current_user.username,
                    'team_name': team.name,
                    'role': role
                }
            )
    
    logger.info(f"User {current_user.username} shared campaign {campaign.id} with team {team.name} ({added_count} members)")
    flash(f'Campaign shared with {added_count} members of team {team.name}.', 'success')
    return redirect(url_for('campaigns.share_campaign_form', campaign_id=campaign.id))

@campaigns_bp.route('/<int:campaign_id>/collaborator/<int:user_id>/remove', methods=['POST'])
@login_required
def remove_collaborator(campaign_id, user_id):
    """Remove a collaborator from a campaign."""
    campaign = AdCampaign.query.get_or_404(campaign_id)
    
    # Check if user is the owner or has editor access
    if not campaign.owner or campaign.owner.id != current_user.id:
        collab = CampaignCollaborator.query.filter_by(
            campaign_id=campaign.id, 
            user_id=current_user.id, 
            role=CollaborationRole.EDITOR.value
        ).first()
        
        if not collab and not current_user.is_admin():
            flash('You do not have permission to modify campaign collaborators.', 'danger')
            return redirect(url_for('campaigns.get_campaign', campaign_id=campaign.id))
    
    # Get user to remove
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('campaigns.share_campaign_form', campaign_id=campaign.id))
    
    # Remove collaborator
    success = campaign.remove_collaborator(user)
    
    if success:
        logger.info(f"User {current_user.username} removed {user.username} as collaborator from campaign {campaign.id}")
        flash(f'Removed {user.username} from campaign collaborators.', 'success')
        
        # Notify the removed user
        NotificationService.create_notification(
            title="Removed from Campaign",
            message=f"You were removed as a collaborator from '{campaign.title}'.",
            type=NotificationType.INFO,
            category=NotificationCategory.COLLABORATION,
            related_entity_type="campaign",
            related_entity_id=campaign.id,
            user_id=user.id,
            extra_data={
                'removed_by': current_user.username
            }
        )
    else:
        flash(f'User {user.username} is not a collaborator.', 'warning')
    
    return redirect(url_for('campaigns.share_campaign_form', campaign_id=campaign.id))


@campaigns_bp.route('/dashboard')
@login_required
def campaign_dashboard():
    """Display the campaign analytics dashboard."""
    # Get specific campaign if ID is provided
    campaign_id = request.args.get('campaign_id')
    
    # Get all campaigns
    if current_user.is_admin():
        campaigns = AdCampaign.query.all()
    else:
        # Get owned campaigns and collaborations
        owned_campaigns = AdCampaign.query.filter_by(user_id=current_user.id).all()
        
        # Get campaigns the user is a collaborator on
        collab_campaign_ids = db.session.query(CampaignCollaborator.campaign_id).filter_by(
            user_id=current_user.id
        ).all()
        collab_campaign_ids = [c[0] for c in collab_campaign_ids]
        
        collaborating_campaigns = AdCampaign.query.filter(
            AdCampaign.id.in_(collab_campaign_ids)
        ).all() if collab_campaign_ids else []
        
        campaigns = owned_campaigns + collaborating_campaigns
    
    # Get platforms
    platforms = SocialMediaPlatform.query.filter_by(active=True).all()
    platform_names = [p.name for p in platforms] if platforms else ['Meta', 'Google', 'Twitter']
    
    # Generate mock data for simple chart
    impressions_data = [random.randint(5000, 50000) for _ in range(len(platform_names))]
    clicks_data = [random.randint(100, 2000) for _ in range(len(platform_names))]
    applications_data = [random.randint(10, 200) for _ in range(len(platform_names))]
    
    # If campaign_id is provided, set it as the initial campaign
    context = {
        'campaigns': campaigns,
        'segments': [],  # We'll implement segments later
        'platform_names': platform_names,
        'impressions_data': impressions_data,
        'clicks_data': clicks_data,
        'applications_data': applications_data
    }
    
    # Add campaign_id to template context if provided
    if campaign_id:
        context['initial_campaign_id'] = campaign_id
    
    return render_template('dashboard/campaign_analytics.html', **context) 