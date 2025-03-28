"""
Models for handling user collaboration in the application.
"""
from app import db
from datetime import datetime
import enum

class CollaborationRole(enum.Enum):
    """Enum for collaboration roles."""
    OWNER = 'owner'
    EDITOR = 'editor'
    VIEWER = 'viewer'

class TeamMember(db.Model):
    """Model representing a user team membership."""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=CollaborationRole.VIEWER.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('team_memberships', lazy='dynamic'))
    
    def __repr__(self):
        return f'<TeamMember: {self.user.username} in team {self.team_id} as {self.role}>'

class Team(db.Model):
    """Model representing a team of users that can collaborate on projects."""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    members = db.relationship('TeamMember', backref='team', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_teams')
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def add_member(self, user, role=CollaborationRole.VIEWER.value):
        """Add a member to the team."""
        if TeamMember.query.filter_by(team_id=self.id, user_id=user.id).first():
            # User is already a member
            return False
        
        member = TeamMember(team_id=self.id, user_id=user.id, role=role)
        db.session.add(member)
        db.session.commit()
        return True
    
    def remove_member(self, user):
        """Remove a member from the team."""
        member = TeamMember.query.filter_by(team_id=self.id, user_id=user.id).first()
        if not member:
            # User is not a member
            return False
        
        db.session.delete(member)
        db.session.commit()
        return True
    
    def get_members(self):
        """Get all team members with user data."""
        return db.session.query(
            TeamMember, 'User'
        ).join(
            'User'
        ).filter(
            TeamMember.team_id == self.id
        ).all()
    
    def to_dict(self):
        """Convert team to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'active': self.active,
            'member_count': self.members.count()
        }

class CampaignCollaborator(db.Model):
    """Model representing a user collaborating on a campaign."""
    __tablename__ = 'campaign_collaborators'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('ad_campaigns.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=CollaborationRole.VIEWER.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_viewed = db.Column(db.DateTime, nullable=True)
    
    # Unique constraint to ensure a user can only have one role per campaign
    __table_args__ = (
        db.UniqueConstraint('campaign_id', 'user_id', name='uix_campaign_user'),
    )
    
    # Relationships
    user = db.relationship('User', backref=db.backref('campaign_collaborations', lazy='dynamic'))
    
    def __repr__(self):
        return f'<CampaignCollaborator: {self.user.username} on campaign {self.campaign_id} as {self.role}>'
    
    def to_dict(self):
        """Convert collaborator to dictionary."""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'user_id': self.user_id,
            'username': self.user.username,
            'full_name': f"{self.user.first_name} {self.user.last_name}" if self.user.first_name and self.user.last_name else self.user.username,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None
        }