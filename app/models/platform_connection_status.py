"""Platform Connection Status model for tracking API connection health."""

from datetime import datetime
import json
from sqlalchemy.dialects.postgresql import JSONB
from app.extensions import db


class PlatformConnectionStatus(db.Model):
    """Tracks the connection status for each integrated platform API."""
    
    __tablename__ = 'platform_connection_status'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False, index=True)
    is_connected = db.Column(db.Boolean, nullable=False, default=False)
    last_checked = db.Column(db.DateTime, nullable=True)
    last_successful_connection = db.Column(db.DateTime, nullable=True)
    connection_details = db.Column(JSONB, nullable=True)
    status_message = db.Column(db.String(255), nullable=True)
    response_time_ms = db.Column(db.Integer, nullable=True)
    api_version = db.Column(db.String(50), nullable=True)
    performance_score = db.Column(db.Integer, nullable=True)
    failure_count = db.Column(db.Integer, nullable=True, default=0)
    health_status = db.Column(db.String(50), nullable=True)
    connection_history = db.Column(JSONB, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, 
                           onupdate=datetime.utcnow)
    
    # Platform-specific icons and display names
    PLATFORM_ICONS = {
        'meta': 'fab fa-facebook',
        'google': 'fab fa-google',
        'twitter': 'fab fa-twitter',
        'tiktok': 'fab fa-tiktok',
        'snapchat': 'fab fa-snapchat'
    }
    
    PLATFORM_NAMES = {
        'meta': 'Meta (Facebook)',
        'google': 'Google Ads',
        'twitter': 'X (Twitter)',
        'tiktok': 'TikTok',
        'snapchat': 'Snapchat'
    }
    
    HEALTH_STATUSES = ['excellent', 'good', 'fair', 'poor', 'critical']
    
    def __init__(self, platform, is_connected=False, status_message=None):
        self.platform = platform
        self.is_connected = is_connected
        self.status_message = status_message
        self.last_checked = datetime.utcnow()
        self.connection_history = []
        self.failure_count = 0
        self.health_status = 'fair'  # Default starting status
    
    def update_status(self, is_connected, response_time_ms=None, 
                     status_message=None, api_version=None, details=None):
        """Update the platform connection status with new information."""
        self.is_connected = is_connected
        self.last_checked = datetime.utcnow()
        self.response_time_ms = response_time_ms
        self.status_message = status_message
        
        if api_version:
            self.api_version = api_version
            
        # Update connection history
        history_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'connected': is_connected,
            'response_time_ms': response_time_ms,
            'message': status_message
        }
        
        if details:
            history_entry['details'] = details
            self.connection_details = details
        
        # Initialize connection history if None
        if not self.connection_history:
            self.connection_history = []
            
        # Add the new entry (keep last 50 entries)
        self.connection_history.append(history_entry)
        if len(self.connection_history) > 50:
            self.connection_history = self.connection_history[-50:]
        
        # Update success/failure tracking
        if is_connected:
            self.last_successful_connection = datetime.utcnow()
            self.failure_count = 0
        else:
            self.failure_count += 1
        
        # Update performance score and health status
        self._update_performance_metrics()
        
    def _update_performance_metrics(self):
        """Calculate performance score and health status based on history."""
        if not self.connection_history:
            self.performance_score = 50  # Neutral starting point
            self.health_status = 'fair'
            return
            
        # Calculate health based on last 10 connections
        recent_history = self.connection_history[-10:]
        success_rate = sum(1 for entry in recent_history if entry.get('connected', False)) / len(recent_history)
        
        # Calculate average response time of successful connections
        successful_connections = [entry for entry in recent_history if entry.get('connected', False)]
        avg_response_time = 0
        if successful_connections:
            response_times = [entry.get('response_time_ms', 0) for entry in successful_connections if entry.get('response_time_ms')]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        # Calculate performance score (0-100)
        # 70% based on success rate, 30% based on response time
        success_score = success_rate * 70
        
        # Response time score (lower is better, max 30 points)
        # Assume response times over 1000ms get 0 points, under 100ms get 30 points
        response_score = 0
        if avg_response_time > 0:
            response_score = max(0, 30 - (avg_response_time / 1000 * 30))
            
        self.performance_score = int(success_score + response_score)
        
        # Set health status based on performance score
        if self.performance_score >= 90:
            self.health_status = 'excellent'
        elif self.performance_score >= 75:
            self.health_status = 'good'
        elif self.performance_score >= 50:
            self.health_status = 'fair'
        elif self.performance_score >= 25:
            self.health_status = 'poor'
        else:
            self.health_status = 'critical'
    
    @property
    def icon(self):
        """Get the appropriate Font Awesome icon for this platform."""
        return self.PLATFORM_ICONS.get(self.platform, 'fas fa-globe')
    
    @property
    def display_name(self):
        """Get the human-readable name for this platform."""
        return self.PLATFORM_NAMES.get(self.platform, self.platform.capitalize())
    
    @property
    def health_icon(self):
        """Get the appropriate health status icon."""
        if self.health_status == 'excellent':
            return 'fas fa-circle-check text-success'
        elif self.health_status == 'good':
            return 'fas fa-circle-check text-success'
        elif self.health_status == 'fair':
            return 'fas fa-triangle-exclamation text-warning'
        elif self.health_status == 'poor':
            return 'fas fa-circle-exclamation text-danger'
        else:  # critical
            return 'fas fa-circle-xmark text-danger'
    
    @property
    def status_badge_class(self):
        """Get the appropriate Bootstrap badge class for the connection status."""
        if self.is_connected:
            return 'bg-success'
        else:
            return 'bg-danger'
    
    @property
    def health_badge_class(self):
        """Get the appropriate Bootstrap badge class for the health status."""
        if self.health_status == 'excellent':
            return 'bg-success'
        elif self.health_status == 'good':
            return 'bg-success'
        elif self.health_status == 'fair':
            return 'bg-warning'
        elif self.health_status == 'poor':
            return 'bg-danger'
        else:  # critical
            return 'bg-danger'
    
    @property
    def last_checked_display(self):
        """Format the last checked time for display."""
        if not self.last_checked:
            return 'Never'
        
        return self.last_checked.strftime('%Y-%m-%d %H:%M:%S')
    
    @property
    def last_successful_connection_display(self):
        """Format the last successful connection time for display."""
        if not self.last_successful_connection:
            return 'Never'
        
        return self.last_successful_connection.strftime('%Y-%m-%d %H:%M:%S')
    
    @classmethod
    def get_all_platforms(cls):
        """Return all platform statuses, creating entries for missing platforms."""
        # Get all existing platform statuses
        existing_statuses = cls.query.all()
        existing_platforms = {status.platform for status in existing_statuses}
        
        # Ensure all supported platforms have entries
        all_platforms = set(cls.PLATFORM_NAMES.keys())
        missing_platforms = all_platforms - existing_platforms
        
        # Create entries for missing platforms
        for platform in missing_platforms:
            new_status = cls(platform=platform)
            db.session.add(new_status)
        
        if missing_platforms:
            db.session.commit()
            # Reload all statuses
            existing_statuses = cls.query.all()
            
        return existing_statuses
    
    @classmethod
    def get_platform_status(cls, platform):
        """Get status for a specific platform, creating if it doesn't exist."""
        status = cls.query.filter_by(platform=platform).first()
        
        if not status:
            status = cls(platform=platform)
            db.session.add(status)
            db.session.commit()
            
        return status
        
    def to_dict(self):
        """Convert the status object to a dictionary for JSON responses."""
        return {
            'id': self.id,
            'platform': self.platform,
            'display_name': self.display_name,
            'is_connected': self.is_connected,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'last_successful_connection': self.last_successful_connection.isoformat() if self.last_successful_connection else None,
            'status_message': self.status_message,
            'response_time_ms': self.response_time_ms,
            'api_version': self.api_version,
            'performance_score': self.performance_score,
            'health_status': self.health_status,
            'failure_count': self.failure_count,
            'icon': self.icon
        }
    
    def __repr__(self):
        return f"<PlatformConnectionStatus(platform='{self.platform}', connected={self.is_connected})>"