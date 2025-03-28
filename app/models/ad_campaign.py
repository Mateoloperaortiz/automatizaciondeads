from app import db
from datetime import datetime

class SocialMediaPlatform(db.Model):
    """Model representing a social media platform."""
    __tablename__ = 'social_media_platforms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    api_key = db.Column(db.String(255), nullable=True)
    api_secret = db.Column(db.String(255), nullable=True)
    access_token = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    campaigns = db.relationship('AdCampaign', backref='platform', lazy=True)
    
    def __repr__(self):
        return f'<SocialMediaPlatform {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'active': self.active
        }


class AdCampaign(db.Model):
    """Model representing an ad campaign for a job opening."""
    __tablename__ = 'ad_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('social_media_platforms.id'), nullable=False)
    job_opening_id = db.Column(db.Integer, db.ForeignKey('job_openings.id'), nullable=False)
    segment_id = db.Column(db.Integer, nullable=True)  # Target audience segment
    budget = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='draft')  # draft, active, paused, completed, etc.
    ad_content = db.Column(db.Text, nullable=True)  # Legacy field, kept for backward compatibility
    ad_headline = db.Column(db.String(100), nullable=True)
    ad_text = db.Column(db.Text, nullable=True)
    ad_cta = db.Column(db.String(50), nullable=True)
    ad_image_url = db.Column(db.String(255), nullable=True)
    platform_specific_content = db.Column(db.Text, nullable=True)  # JSON field for platform-specific content
    platform_ad_id = db.Column(db.String(100), nullable=True)  # ID returned by the platform API
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    owner = db.relationship('User', backref='owned_campaigns', foreign_keys=[user_id])
    collaborators = db.relationship('CampaignCollaborator', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AdCampaign {self.title} on {self.platform.name}>'
    
    def add_collaborator(self, user, role='viewer'):
        """Add a collaborator to the campaign."""
        from app.models.collaboration import CampaignCollaborator, CollaborationRole
        
        if role not in [r.value for r in CollaborationRole]:
            role = CollaborationRole.VIEWER.value
            
        # Check if user is already a collaborator
        existing = CampaignCollaborator.query.filter_by(
            campaign_id=self.id, user_id=user.id
        ).first()
        
        if existing:
            existing.role = role
            db.session.commit()
            return existing
        
        # Add new collaborator
        collab = CampaignCollaborator(
            campaign_id=self.id,
            user_id=user.id,
            role=role
        )
        db.session.add(collab)
        db.session.commit()
        return collab
    
    def remove_collaborator(self, user):
        """Remove a collaborator from the campaign."""
        collab = CampaignCollaborator.query.filter_by(
            campaign_id=self.id, user_id=user.id
        ).first()
        
        if collab:
            db.session.delete(collab)
            db.session.commit()
            return True
        return False
    
    def get_collaborators(self):
        """Get all campaign collaborators with user data."""
        return db.session.query(
            CampaignCollaborator, 'User'
        ).join(
            'User'
        ).filter(
            CampaignCollaborator.campaign_id == self.id
        ).all()
    
    def to_dict(self, include_collaborators=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'platform_id': self.platform_id,
            'job_opening_id': self.job_opening_id,
            'segment_id': self.segment_id,
            'budget': self.budget,
            'status': self.status,
            'ad_content': self.ad_content,
            'ad_headline': self.ad_headline,
            'ad_text': self.ad_text,
            'ad_cta': self.ad_cta,
            'ad_image_url': self.ad_image_url,
            'platform_specific_content': self.platform_specific_content,
            'platform_ad_id': self.platform_ad_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
        
        # Add owner information if available
        if self.owner:
            data['owner'] = {
                'id': self.owner.id,
                'username': self.owner.username,
                'full_name': f"{self.owner.first_name} {self.owner.last_name}" if self.owner.first_name and self.owner.last_name else self.owner.username
            }
        
        # Add collaborators if requested
        if include_collaborators:
            data['collaborators'] = [
                {
                    'id': collab.id,
                    'user_id': collab.user_id,
                    'username': collab.user.username if collab.user else None,
                    'full_name': f"{collab.user.first_name} {collab.user.last_name}" if collab.user and collab.user.first_name and collab.user.last_name else (collab.user.username if collab.user else None),
                    'role': collab.role,
                    'last_viewed': collab.last_viewed.isoformat() if collab.last_viewed else None
                }
                for collab in self.collaborators.all()
            ]
            data['collaborator_count'] = len(data['collaborators'])
        
        return data
        
    @classmethod
    def serialize_ad_content(cls, ad_data):
        """
        Serialize ad content data into a JSON string for storage in platform_specific_content
        
        Args:
            ad_data (dict): Dictionary containing platform-specific ad content
            
        Returns:
            str: JSON string representation of ad content
        """
        import json
        return json.dumps(ad_data)
    
    @classmethod
    def deserialize_ad_content(cls, json_content):
        """
        Deserialize JSON string from platform_specific_content into a dict
        
        Args:
            json_content (str): JSON string representation of ad content
            
        Returns:
            dict: Dictionary containing platform-specific ad content
        """
        import json
        try:
            return json.loads(json_content) if json_content else {}
        except:
            return {} 