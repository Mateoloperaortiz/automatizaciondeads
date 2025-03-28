from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.collaboration import Team, TeamMember, CollaborationRole
from app.models.user import User
from app.utils.access_control import manager_required
from app.utils.realtime import broadcast_entity_change, entity_changed
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType, NotificationCategory
import logging

teams_bp = Blueprint('teams', __name__, url_prefix='/teams')
logger = logging.getLogger(__name__)

@teams_bp.route('/')
@login_required
def list_teams():
    """List teams the current user is a member of."""
    # Get teams created by the user
    owned_teams = Team.query.filter_by(created_by=current_user.id).all()
    
    # Get teams the user is a member of (but didn't create)
    member_teams = db.session.query(Team).join(
        TeamMember, Team.id == TeamMember.team_id
    ).filter(
        TeamMember.user_id == current_user.id,
        Team.created_by != current_user.id
    ).all()
    
    return render_template(
        'teams/list.html',
        owned_teams=owned_teams,
        member_teams=member_teams
    )

@teams_bp.route('/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_team():
    """Create a new team."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Team name is required.', 'danger')
            return render_template('teams/create.html')
        
        # Create new team
        team = Team(
            name=name,
            description=description,
            created_by=current_user.id,
            active=True
        )
        db.session.add(team)
        db.session.commit()
        
        # Add creator as owner
        team.add_member(current_user, role=CollaborationRole.OWNER.value)
        
        logger.info(f"User {current_user.username} created team: {name}")
        
        # Broadcast team creation via real-time
        try:
            # Create notification
            NotificationService.create_notification(
                title="Team Created",
                message=f"You have created a new team: '{team.name}'",
                type=NotificationType.SUCCESS,
                category=NotificationCategory.SYSTEM,
                related_entity_type="team",
                related_entity_id=team.id,
                user_id=current_user.id
            )
            
            # Broadcast team creation event
            entity_changed(
                entity_type='team',
                entity_id=team.id,
                update_type='created',
                entity_data=team.to_dict()
            )
        except Exception as e:
            logger.error(f"Error broadcasting team creation: {str(e)}")
        
        flash(f'Team "{name}" created successfully.', 'success')
        return redirect(url_for('teams.detail', team_id=team.id))
    
    return render_template('teams/create.html')

@teams_bp.route('/<int:team_id>')
@login_required
def detail(team_id):
    """Show team details."""
    team = Team.query.get_or_404(team_id)
    
    # Check if user is a member of the team
    is_member = TeamMember.query.filter_by(
        team_id=team.id, user_id=current_user.id
    ).first() is not None
    
    if not is_member and team.created_by != current_user.id:
        flash('You do not have permission to view this team.', 'danger')
        return redirect(url_for('teams.list_teams'))
    
    # Get team members with roles
    members = db.session.query(
        TeamMember, User
    ).join(
        User, TeamMember.user_id == User.id
    ).filter(
        TeamMember.team_id == team.id
    ).all()
    
    return render_template(
        'teams/detail.html',
        team=team,
        members=members,
        is_owner=team.created_by == current_user.id,
        current_user_role=TeamMember.query.filter_by(
            team_id=team.id, user_id=current_user.id
        ).first().role if is_member else None
    )

@teams_bp.route('/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    """Edit team details."""
    team = Team.query.get_or_404(team_id)
    
    # Check if user is the team owner
    if team.created_by != current_user.id:
        flash('Only the team owner can edit team details.', 'danger')
        return redirect(url_for('teams.detail', team_id=team.id))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        active = 'active' in request.form
        
        if not name:
            flash('Team name is required.', 'danger')
            return render_template('teams/edit.html', team=team)
        
        # Store original values for comparison
        original_name = team.name
        original_active = team.active
        
        # Update team
        team.name = name
        team.description = description
        team.active = active
        db.session.commit()
        
        logger.info(f"User {current_user.username} updated team: {name}")
        
        # Broadcast team update via real-time
        try:
            # Create notification for team members
            update_details = []
            if original_name != name:
                update_details.append(f"name changed from '{original_name}' to '{name}'")
            
            if original_active != active:
                status_change = "activated" if active else "deactivated"
                update_details.append(f"team was {status_change}")
                
                # If status changed, send a special notification
                if original_active != active:
                    # Get all team members
                    team_members = TeamMember.query.filter_by(team_id=team.id).all()
                    for member in team_members:
                        NotificationService.create_notification(
                            title=f"Team {status_change.capitalize()}",
                            message=f"Team '{name}' has been {status_change} by {current_user.username}.",
                            type=NotificationType.INFO if active else NotificationType.WARNING,
                            category=NotificationCategory.SYSTEM,
                            related_entity_type="team",
                            related_entity_id=team.id,
                            user_id=member.user_id
                        )
            
            # Notify team members about general update
            if update_details:
                # Get all team members except current user
                team_members = TeamMember.query.filter(
                    TeamMember.team_id == team.id,
                    TeamMember.user_id != current_user.id
                ).all()
                
                update_msg = f"Team '{name}' has been updated: " + ", ".join(update_details)
                for member in team_members:
                    NotificationService.create_notification(
                        title="Team Updated",
                        message=update_msg,
                        type=NotificationType.INFO,
                        category=NotificationCategory.SYSTEM,
                        related_entity_type="team",
                        related_entity_id=team.id,
                        user_id=member.user_id
                    )
            
            # Broadcast general team update
            entity_changed(
                entity_type='team',
                entity_id=team.id,
                update_type='updated',
                entity_data=team.to_dict()
            )
            
            # If status changed, broadcast specific status change event
            if original_active != active:
                entity_changed(
                    entity_type='team',
                    entity_id=team.id,
                    update_type='status_change',
                    entity_data={
                        'id': team.id,
                        'name': team.name,
                        'active': team.active,
                        'status': 'active' if team.active else 'inactive',
                        'changed_by': current_user.username
                    }
                )
        except Exception as e:
            logger.error(f"Error broadcasting team update: {str(e)}")
        
        flash(f'Team "{name}" updated successfully.', 'success')
        return redirect(url_for('teams.detail', team_id=team.id))
    
    return render_template('teams/edit.html', team=team)

@teams_bp.route('/<int:team_id>/members/add', methods=['GET', 'POST'])
@login_required
def add_member(team_id):
    """Add a member to the team."""
    team = Team.query.get_or_404(team_id)
    
    # Check if user is the team owner
    is_owner = TeamMember.query.filter_by(
        team_id=team.id, user_id=current_user.id, role=CollaborationRole.OWNER.value
    ).first() is not None
    
    if not is_owner and team.created_by != current_user.id:
        flash('Only team owners can add members.', 'danger')
        return redirect(url_for('teams.detail', team_id=team.id))
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        role = request.form.get('role')
        
        if not user_id or not role:
            flash('User and role are required.', 'danger')
            return redirect(url_for('teams.add_member', team_id=team.id))
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('teams.add_member', team_id=team.id))
        
        # Add user to team
        team.add_member(user, role=role)
        
        logger.info(f"User {current_user.username} added {user.username} to team {team.name} as {role}")
        
        # Broadcast team member addition via real-time
        try:
            # Notify the added user
            NotificationService.create_notification(
                title="Added to Team",
                message=f"You have been added to team '{team.name}' as {role} by {current_user.username}.",
                type=NotificationType.INFO,
                category=NotificationCategory.SYSTEM,
                related_entity_type="team",
                related_entity_id=team.id,
                user_id=user.id
            )
            
            # Notify other team members
            team_members = TeamMember.query.filter(
                TeamMember.team_id == team.id,
                TeamMember.user_id != user.id,
                TeamMember.user_id != current_user.id
            ).all()
            
            for member in team_members:
                NotificationService.create_notification(
                    title="New Team Member",
                    message=f"{user.username} has been added to team '{team.name}' as {role}.",
                    type=NotificationType.INFO,
                    category=NotificationCategory.SYSTEM,
                    related_entity_type="team",
                    related_entity_id=team.id,
                    user_id=member.user_id
                )
            
            # Broadcast member added event
            entity_changed(
                entity_type='team',
                entity_id=team.id,
                update_type='member_added',
                entity_data={
                    'team_id': team.id,
                    'team_name': team.name,
                    'user_id': user.id,
                    'username': user.username,
                    'role': role,
                    'added_by': current_user.username
                }
            )
        except Exception as e:
            logger.error(f"Error broadcasting team member addition: {str(e)}")
        
        flash(f'User {user.username} added to team as {role}.', 'success')
        return redirect(url_for('teams.detail', team_id=team.id))
    
    # Get users not already in the team
    existing_member_ids = [m.user_id for m in TeamMember.query.filter_by(team_id=team.id).all()]
    available_users = User.query.filter(User.id.notin_(existing_member_ids)).all()
    
    return render_template(
        'teams/add_member.html',
        team=team,
        available_users=available_users,
        roles=[r.value for r in CollaborationRole]
    )

@teams_bp.route('/<int:team_id>/members/<int:user_id>/remove', methods=['POST'])
@login_required
def remove_member(team_id, user_id):
    """Remove a member from the team."""
    team = Team.query.get_or_404(team_id)
    
    # Check if user is the team owner
    is_owner = TeamMember.query.filter_by(
        team_id=team.id, user_id=current_user.id, role=CollaborationRole.OWNER.value
    ).first() is not None
    
    if not is_owner and team.created_by != current_user.id:
        flash('Only team owners can remove members.', 'danger')
        return redirect(url_for('teams.detail', team_id=team.id))
    
    # Cannot remove team creator
    if user_id == team.created_by:
        flash('Cannot remove the team creator.', 'danger')
        return redirect(url_for('teams.detail', team_id=team.id))
    
    # Get user
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('teams.detail', team_id=team.id))
    
    # Remove user from team
    team.remove_member(user)
    
    logger.info(f"User {current_user.username} removed {user.username} from team {team.name}")
    
    # Broadcast team member removal via real-time
    try:
        # Notify the removed user
        NotificationService.create_notification(
            title="Removed from Team",
            message=f"You have been removed from team '{team.name}' by {current_user.username}.",
            type=NotificationType.INFO,
            category=NotificationCategory.SYSTEM,
            related_entity_type="team",
            related_entity_id=team.id,
            user_id=user.id
        )
        
        # Notify other team members
        team_members = TeamMember.query.filter(
            TeamMember.team_id == team.id,
            TeamMember.user_id != current_user.id
        ).all()
        
        for member in team_members:
            NotificationService.create_notification(
                title="Team Member Removed",
                message=f"{user.username} has been removed from team '{team.name}'.",
                type=NotificationType.INFO,
                category=NotificationCategory.SYSTEM,
                related_entity_type="team",
                related_entity_id=team.id,
                user_id=member.user_id
            )
        
        # Broadcast member removed event
        entity_changed(
            entity_type='team',
            entity_id=team.id,
            update_type='member_removed',
            entity_data={
                'team_id': team.id,
                'team_name': team.name,
                'user_id': user.id,
                'username': user.username,
                'removed_by': current_user.username
            }
        )
    except Exception as e:
        logger.error(f"Error broadcasting team member removal: {str(e)}")
    
    flash(f'User {user.username} removed from team.', 'success')
    return redirect(url_for('teams.detail', team_id=team.id))

# API routes
@teams_bp.route('/api/teams', methods=['GET'])
@login_required
def api_list_teams():
    """API endpoint to get all teams the current user is a member of."""
    # Get teams the user is a member of
    team_members = TeamMember.query.filter_by(user_id=current_user.id).all()
    team_ids = [tm.team_id for tm in team_members]
    
    teams = Team.query.filter(Team.id.in_(team_ids)).all()
    
    return jsonify({
        'success': True,
        'data': [team.to_dict() for team in teams]
    })

@teams_bp.route('/api/teams/<int:team_id>/members', methods=['GET'])
@login_required
def api_get_team_members(team_id):
    """API endpoint to get all members of a team."""
    team = Team.query.get_or_404(team_id)
    
    # Check if user is a member of the team
    is_member = TeamMember.query.filter_by(
        team_id=team.id, user_id=current_user.id
    ).first() is not None
    
    if not is_member and team.created_by != current_user.id:
        return jsonify({
            'success': False,
            'message': 'Not authorized to view team members'
        }), 403
    
    # Get team members with user data
    members = []
    for member, user in team.get_members():
        members.append({
            'id': member.id,
            'user_id': user.id,
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username,
            'role': member.role,
            'created_at': member.created_at.isoformat() if member.created_at else None
        })
    
    return jsonify({
        'success': True,
        'data': members
    })