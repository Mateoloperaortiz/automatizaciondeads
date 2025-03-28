"""
Models for the documentation system.
"""
from app import db
from datetime import datetime
import enum
import json

class DocumentStatus(enum.Enum):
    """Enum for document status."""
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    PENDING_APPROVAL = 'pending_approval'
    REJECTED = 'rejected'

class DocumentType(enum.Enum):
    """Enum for document types."""
    GENERAL = 'general'
    API = 'api'
    TUTORIAL = 'tutorial'
    FAQ = 'faq'
    GLOSSARY = 'glossary'

class Document(db.Model):
    """
    Model representing a documentation page/section.
    Each document has multiple versions for tracking history.
    """
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    doc_type = db.Column(db.String(20), nullable=False, default=DocumentType.GENERAL.value)
    parent_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    order = db.Column(db.Integer, default=0)  # For ordering within sections
    status = db.Column(db.String(20), nullable=False, default=DocumentStatus.DRAFT.value)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # SEO and metadata as JSON
    document_metadata = db.Column(db.Text, nullable=True)
    
    # Relationships
    creator = db.relationship('User', backref='created_documents')
    children = db.relationship('Document', backref=db.backref('parent', remote_side=[id]))
    versions = db.relationship('DocumentVersion', backref='document', lazy='dynamic', 
                               cascade='all, delete-orphan', order_by='DocumentVersion.version_number.desc()')
    approvals = db.relationship('DocumentApproval', backref='document', lazy='dynamic', 
                                cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Document {self.title}>'
    
    @property
    def latest_version(self):
        """Get the latest version of the document."""
        return self.versions.first()
    
    @property
    def published_version(self):
        """Get the published version of the document."""
        return self.versions.filter_by(is_published=True).first()
    
    @property
    def content(self):
        """Get the content of the latest published version, or the latest version if none is published."""
        version = self.published_version or self.latest_version
        return version.content if version else ""
    
    def create_version(self, content, user_id, is_published=False, change_summary=None):
        """Create a new version of the document."""
        # Get highest version number
        highest_version = self.versions.first()
        new_version_number = (highest_version.version_number + 1) if highest_version else 1
        
        version = DocumentVersion(
            document_id=self.id,
            version_number=new_version_number,
            content=content,
            created_by=user_id,
            is_published=is_published,
            change_summary=change_summary
        )
        
        db.session.add(version)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return version
    
    def publish_version(self, version_number):
        """Publish a specific version of the document."""
        # First unpublish any current published version
        for version in self.versions.filter_by(is_published=True).all():
            version.is_published = False
        
        # Publish the specified version
        version = self.versions.filter_by(version_number=version_number).first()
        if version:
            version.is_published = True
            self.status = DocumentStatus.PUBLISHED.value
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def submit_for_approval(self, version_number, reviewer_id):
        """Submit a document version for approval."""
        version = self.versions.filter_by(version_number=version_number).first()
        if not version:
            return False
        
        # Change status to pending approval
        self.status = DocumentStatus.PENDING_APPROVAL.value
        
        # Create a new approval request
        approval = DocumentApproval(
            document_id=self.id,
            version_number=version_number,
            reviewer_id=reviewer_id,
            requested_by=version.created_by,
            status='pending'
        )
        
        db.session.add(approval)
        db.session.commit()
        return True
    
    def get_metadata(self):
        """Get document metadata as a dictionary."""
        if not self.document_metadata:
            return {}
        try:
            return json.loads(self.document_metadata)
        except:
            return {}
    
    def set_metadata(self, metadata_dict):
        """Set document metadata from a dictionary."""
        self.document_metadata = json.dumps(metadata_dict)
    
    def update_metadata(self, key, value):
        """Update a single metadata field."""
        metadata = self.get_metadata()
        metadata[key] = value
        self.set_metadata(metadata)
    
    def to_dict(self, include_content=False):
        """Convert document to dictionary."""
        result = {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'doc_type': self.doc_type,
            'parent_id': self.parent_id,
            'order': self.order,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'version_count': self.versions.count(),
            'latest_version': self.latest_version.version_number if self.latest_version else None,
            'published_version': self.published_version.version_number if self.published_version else None,
            'metadata': self.get_metadata(),
        }
        
        if include_content:
            result['content'] = self.content
        
        return result

class DocumentVersion(db.Model):
    """Model representing a specific version of a document."""
    __tablename__ = 'document_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)
    change_summary = db.Column(db.String(200), nullable=True)
    
    # Relationships
    creator = db.relationship('User', backref='document_versions')
    
    # Unique constraint to ensure a document can only have one version with a specific number
    __table_args__ = (
        db.UniqueConstraint('document_id', 'version_number', name='uix_document_version'),
    )
    
    def __repr__(self):
        return f'<DocumentVersion {self.document_id}-{self.version_number}>'
    
    def to_dict(self, include_content=True):
        """Convert document version to dictionary."""
        result = {
            'id': self.id,
            'document_id': self.document_id,
            'version_number': self.version_number,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_published': self.is_published,
            'change_summary': self.change_summary,
        }
        
        if include_content:
            result['content'] = self.content
        
        return result

class DocumentApproval(db.Model):
    """Model representing an approval request for a document version."""
    __tablename__ = 'document_approvals'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    
    # Relationships
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='document_reviews')
    requester = db.relationship('User', foreign_keys=[requested_by], backref='document_approval_requests')
    
    def __repr__(self):
        return f'<DocumentApproval {self.document_id}-{self.version_number}>'
    
    def approve(self, feedback=None):
        """Approve the document version."""
        self.status = 'approved'
        self.reviewed_at = datetime.utcnow()
        self.feedback = feedback
        
        # Auto-publish the approved version
        self.document.publish_version(self.version_number)
        
        db.session.commit()
        return True
    
    def reject(self, feedback):
        """Reject the document version."""
        self.status = 'rejected'
        self.reviewed_at = datetime.utcnow()
        self.feedback = feedback
        
        # Update document status
        self.document.status = DocumentStatus.REJECTED.value
        
        db.session.commit()
        return True
    
    def to_dict(self):
        """Convert approval to dictionary."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'version_number': self.version_number,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.username if self.reviewer else None,
            'requested_by': self.requested_by,
            'requester_name': self.requester.username if self.requester else None,
            'status': self.status,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'feedback': self.feedback,
        }

class DocumentCollaborator(db.Model):
    """Model representing a user collaborating on a document."""
    __tablename__ = 'document_collaborators'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')  # owner, editor, viewer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_viewed = db.Column(db.DateTime, nullable=True)
    
    # Unique constraint to ensure a user can only have one role per document
    __table_args__ = (
        db.UniqueConstraint('document_id', 'user_id', name='uix_document_user'),
    )
    
    # Relationships
    user = db.relationship('User', backref=db.backref('document_collaborations', lazy='dynamic'))
    document = db.relationship('Document', backref=db.backref('collaborators', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<DocumentCollaborator: {self.user.username} on document {self.document_id} as {self.role}>'
    
    def to_dict(self):
        """Convert collaborator to dictionary."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'user_id': self.user_id,
            'username': self.user.username,
            'full_name': f"{self.user.first_name} {self.user.last_name}" if self.user.first_name and self.user.last_name else self.user.username,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None
        }