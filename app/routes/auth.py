from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, UserRole
from app.forms.auth_forms import LoginForm, RegistrationForm, ProfileForm, PasswordChangeForm
from app.utils.realtime import broadcast_entity_change, entity_changed
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType, NotificationCategory
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route for users."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            logger.warning(f"Failed login attempt for user: {form.username.data}")
            return render_template('auth/login.html', form=form)
        
        # Check if user is active
        if not user.is_active:
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            logger.warning(f"Inactive user attempted to login: {user.username}")
            return render_template('auth/login.html', form=form)
        
        # Login user
        login_user(user, remember=form.remember_me.data)
        
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        db.session.commit()
        logger.info(f"User logged in: {user.username}")
        
        # Broadcast user status change via real-time
        try:
            # Sanitize user data for broadcasting (remove sensitive fields)
            user_data = user.to_dict()
            user_data['status'] = 'online'
            user_data['last_login'] = user.last_login.isoformat() if user.last_login else None
            
            entity_changed(
                entity_type='user',
                entity_id=user.id,
                update_type='status_change',
                entity_data=user_data
            )
            
            # If user is a team member, notify team members about user login
            from app.models.collaboration import TeamMember
            team_memberships = TeamMember.query.filter_by(user_id=user.id).all()
            for membership in team_memberships:
                entity_changed(
                    entity_type='team',
                    entity_id=membership.team_id,
                    update_type='member_online',
                    entity_data={
                        'team_id': membership.team_id,
                        'user_id': user.id,
                        'username': user.username,
                        'status': 'online'
                    }
                )
        except Exception as e:
            logger.error(f"Error broadcasting user status change: {str(e)}")
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route for users."""
    user_id = current_user.id
    username = current_user.username
    
    # Store team memberships before logout
    from app.models.collaboration import TeamMember
    team_memberships = [tm.team_id for tm in TeamMember.query.filter_by(user_id=user_id).all()]
    
    logger.info(f"User logged out: {username}")
    
    # Logout user
    logout_user()
    
    # Broadcast user status change via real-time
    try:
        entity_changed(
            entity_type='user',
            entity_id=user_id,
            update_type='status_change',
            entity_data={
                'id': user_id,
                'username': username,
                'status': 'offline'
            }
        )
        
        # Notify team members about user logout
        for team_id in team_memberships:
            entity_changed(
                entity_type='team',
                entity_id=team_id,
                update_type='member_offline',
                entity_data={
                    'team_id': team_id,
                    'user_id': user_id,
                    'username': username,
                    'status': 'offline'
                }
            )
    except Exception as e:
        logger.error(f"Error broadcasting user logout status change: {str(e)}")
    
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route for new users."""
    # Check if registration is enabled
    if not current_app.config.get('ALLOW_REGISTRATION', False):
        flash('Registration is currently disabled.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already in use.', 'danger')
            return render_template('auth/register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=UserRole.VIEWER.value,  # Default role for new users
            is_active=True
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        logger.info(f"New user registered: {user.username}")
        
        # Broadcast new user registration
        try:
            # Notify administrators about new user
            admin_users = User.query.filter_by(role=UserRole.ADMIN.value).all()
            for admin in admin_users:
                NotificationService.create_notification(
                    title="New User Registration",
                    message=f"A new user has registered: {user.username}",
                    type=NotificationType.INFO,
                    category=NotificationCategory.SYSTEM,
                    related_entity_type="user",
                    related_entity_id=user.id,
                    user_id=admin.id
                )
            
            # Broadcast the new user event
            entity_changed(
                entity_type='user',
                entity_id=user.id,
                update_type='created',
                entity_data=user.to_dict()
            )
        except Exception as e:
            logger.error(f"Error broadcasting new user registration: {str(e)}")
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile route."""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Update user profile
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        
        db.session.commit()
        logger.info(f"User updated profile: {current_user.username}")
        
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form, user=current_user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route."""
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html', form=form)
        
        # Update password
        current_user.set_password(form.new_password.data)
        db.session.commit()
        logger.info(f"User changed password: {current_user.username}")
        
        flash('Your password has been updated.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """User preferences route."""
    if request.method == 'POST':
        preferences_data = request.json or {}
        current_user.set_preferences(preferences_data)
        db.session.commit()
        logger.info(f"User updated preferences: {current_user.username}")
        return {'success': True, 'message': 'Preferences updated successfully'}
    
    # GET request
    user_preferences = current_user.get_preferences()
    return render_template(
        'auth/preferences.html', 
        preferences=user_preferences,
        user=current_user
    )

# Admin routes for user management
@auth_bp.route('/users')
@login_required
def user_list():
    """List all users (admin only)."""
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('auth/user_list.html', users=users)

@auth_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit user (admin only)."""
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent editing own user through this route
    if user.id == current_user.id:
        flash('Please use the profile page to edit your own account.', 'warning')
        return redirect(url_for('auth.profile'))
    
    from app.forms.auth_forms import UserEditForm
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        # Store original role and status for comparison
        original_role = user.role
        original_status = user.is_active
                
        # Update user
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        
        # Update password if provided
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        logger.info(f"Admin {current_user.username} updated user: {user.username}")
        
        # Check for important changes that should trigger real-time updates
        try:
            # Role change notification
            if original_role != user.role:
                NotificationService.create_notification(
                    title="Role Updated",
                    message=f"Your role has been changed from {original_role} to {user.role}.",
                    type=NotificationType.INFO,
                    category=NotificationCategory.SYSTEM,
                    related_entity_type="user",
                    related_entity_id=user.id
                )
                
                entity_changed(
                    entity_type='user',
                    entity_id=user.id,
                    update_type='role_change',
                    entity_data={
                        'id': user.id,
                        'username': user.username,
                        'role': user.role,
                        'previous_role': original_role
                    }
                )
            
            # Status change notification
            if original_status != user.is_active:
                status_msg = "activated" if user.is_active else "deactivated"
                NotificationService.create_notification(
                    title="Account Status Updated",
                    message=f"Your account has been {status_msg}.",
                    type=NotificationType.INFO if user.is_active else NotificationType.WARNING,
                    category=NotificationCategory.SYSTEM,
                    related_entity_type="user",
                    related_entity_id=user.id
                )
                
                entity_changed(
                    entity_type='user',
                    entity_id=user.id,
                    update_type='status_change',
                    entity_data={
                        'id': user.id,
                        'username': user.username,
                        'is_active': user.is_active,
                        'status': 'active' if user.is_active else 'inactive'
                    }
                )
            
            # General update notification
            entity_changed(
                entity_type='user',
                entity_id=user.id,
                update_type='updated',
                entity_data=user.to_dict()
            )
        except Exception as e:
            logger.error(f"Error broadcasting user update: {str(e)}")
        
        flash(f'User {user.username} has been updated.', 'success')
        return redirect(url_for('auth.user_list'))
    
    return render_template('auth/edit_user.html', form=form, user=user)

@auth_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete user (admin only)."""
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting own user
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('auth.user_list'))
    
    username = user.username
    user_id = user.id
    
    # Store team memberships before deletion
    from app.models.collaboration import TeamMember
    team_memberships = [tm.team_id for tm in TeamMember.query.filter_by(user_id=user_id).all()]
    
    # Store user data for broadcasting
    user_data = user.to_dict()
    
    db.session.delete(user)
    db.session.commit()
    logger.info(f"Admin {current_user.username} deleted user: {username}")
    
    # Broadcast user deletion and notify teams
    try:
        # Broadcast user deletion
        entity_changed(
            entity_type='user',
            entity_id=user_id,
            update_type='deleted',
            entity_data={
                'id': user_id,
                'username': username,
                'deleted_by': current_user.username
            }
        )
        
        # Notify teams about member removal
        for team_id in team_memberships:
            entity_changed(
                entity_type='team',
                entity_id=team_id,
                update_type='member_removed',
                entity_data={
                    'team_id': team_id,
                    'user_id': user_id,
                    'username': username,
                    'removed_by': current_user.username
                }
            )
            
            # Create team notification
            NotificationService.create_notification(
                title="Team Member Removed",
                message=f"User {username} has been removed from your team.",
                type=NotificationType.INFO,
                category=NotificationCategory.SYSTEM,
                related_entity_type="team",
                related_entity_id=team_id
            )
    except Exception as e:
        logger.error(f"Error broadcasting user deletion: {str(e)}")
    
    flash(f'User {username} has been deleted.', 'success')
    return redirect(url_for('auth.user_list'))