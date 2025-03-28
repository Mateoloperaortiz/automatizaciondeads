from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum
import json

class UserRole(enum.Enum):
    """Enum for user roles."""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"

class User(UserMixin, db.Model):
    """Model representing a user."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    role = db.Column(db.String(20), nullable=False, default=UserRole.VIEWER.value)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # User preferences as JSON
    preferences = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set the user's password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check the provided password against the hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_preferences(self):
        """Get user preferences as a dictionary."""
        if not self.preferences:
            return {}
        try:
            return json.loads(self.preferences)
        except:
            return {}
    
    def set_preferences(self, preferences_dict):
        """Set user preferences from a dictionary."""
        self.preferences = json.dumps(preferences_dict)
    
    def update_preference(self, key, value):
        """Update a single preference."""
        prefs = self.get_preferences()
        prefs[key] = value
        self.set_preferences(prefs)
    
    def has_role(self, role):
        """Check if user has specific role."""
        if isinstance(role, UserRole):
            role = role.value
        return self.role == role
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN.value
    
    def can_manage(self):
        """Check if user can manage resources."""
        return self.role in [UserRole.ADMIN.value, UserRole.MANAGER.value]
    
    def can_edit(self):
        """Check if user can edit resources."""
        return self.role in [UserRole.ADMIN.value, UserRole.MANAGER.value, UserRole.ANALYST.value]
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }