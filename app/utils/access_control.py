"""
Access control utilities for the application.
"""

from functools import wraps
from flask import current_app, flash, redirect, url_for
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

def admin_required(func):
    """
    Decorator for views that require admin role.
    Redirects to login page if user is not logged in or not an admin.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to admin-only route: {func.__name__}")
            return redirect(url_for('auth.login', next=current_app.request.url))
        
        if not current_user.is_admin():
            logger.warning(f"Unauthorized access attempt to admin-only route by user {current_user.username}")
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        
        return func(*args, **kwargs)
    
    return decorated_view

def manager_required(func):
    """
    Decorator for views that require manager role or higher.
    Redirects to login page if user is not logged in or doesn't have sufficient permissions.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to manager-only route: {func.__name__}")
            return redirect(url_for('auth.login', next=current_app.request.url))
        
        if not current_user.can_manage():
            logger.warning(f"Unauthorized access attempt to manager-only route by user {current_user.username}")
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        
        return func(*args, **kwargs)
    
    return decorated_view

def analyst_required(func):
    """
    Decorator for views that require analyst role or higher.
    Redirects to login page if user is not logged in or doesn't have sufficient permissions.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to analyst-only route: {func.__name__}")
            return redirect(url_for('auth.login', next=current_app.request.url))
        
        if not current_user.can_edit():
            logger.warning(f"Unauthorized access attempt to analyst-only route by user {current_user.username}")
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        
        return func(*args, **kwargs)
    
    return decorated_view