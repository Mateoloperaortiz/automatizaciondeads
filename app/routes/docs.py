from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.utils.access_control import admin_required
from app.models.documentation import Document, DocumentVersion, DocumentApproval, DocumentCollaborator, DocumentStatus, DocumentType
from app.models.user import User
from app import db
from datetime import datetime
import logging
from sqlalchemy import desc

docs_bp = Blueprint('docs', __name__, url_prefix='/docs')
logger = logging.getLogger(__name__)

@docs_bp.route('/')
def index():
    """Display the main documentation page."""
    return render_template('docs/index.html')

@docs_bp.route('/api')
def api_documentation():
    """Display the API documentation page."""
    return render_template('api/documentation.html')

@docs_bp.route('/view/<doc_slug>')
def view_document(doc_slug):
    """View a document by its slug."""
    document = Document.query.filter_by(slug=doc_slug).first_or_404()
    
    # If user is logged in, update last viewed time for collaborators
    if current_user.is_authenticated:
        collaborator = DocumentCollaborator.query.filter_by(
            document_id=document.id, 
            user_id=current_user.id
        ).first()
        
        if collaborator:
            collaborator.last_viewed = datetime.utcnow()
            db.session.commit()
    
    return render_template('docs/view.html', document=document)

@docs_bp.route('/edit', methods=['GET', 'POST'])
@docs_bp.route('/edit/<int:doc_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_documentation(doc_id=None):
    """Edit documentation content (admin only)."""
    # Get the document if doc_id is provided
    document = None
    current_version = None
    approval_request = None
    
    if doc_id:
        document = Document.query.get_or_404(doc_id)
        current_version = document.latest_version
        
        # Check for pending approval request
        approval_request = DocumentApproval.query.filter_by(
            document_id=document.id,
            status='pending'
        ).order_by(DocumentApproval.requested_at.desc()).first()
    
    # Get all documents for sidebar navigation and parent selection
    all_documents = Document.query.all()
    
    # Get all admin users for approval requests
    admins = User.query.filter_by(role='admin').all()
    
    # Organize documents by type for sidebar
    documents_by_type = {}
    for doc in Document.query.filter_by(parent_id=None).all():
        doc_type = doc.doc_type
        if doc_type not in documents_by_type:
            documents_by_type[doc_type] = []
        documents_by_type[doc_type].append(doc)
    
    # Sort each type alphabetically by title
    for doc_type in documents_by_type:
        documents_by_type[doc_type].sort(key=lambda x: x.title)
    
    return render_template(
        'docs/edit.html', 
        document=document,
        current_version=current_version,
        approval_request=approval_request,
        all_documents=all_documents,
        documents_by_type=documents_by_type,
        admins=admins
    )

@docs_bp.route('/create', methods=['POST'])
@login_required
@admin_required
def create_document():
    """Create a new document."""
    title = request.form.get('title')
    slug = request.form.get('slug')
    doc_type = request.form.get('doc_type', DocumentType.GENERAL.value)
    parent_id = request.form.get('parent_id')
    
    # Validate required fields
    if not title or not slug:
        flash('Title and slug are required fields.', 'danger')
        return redirect(url_for('docs.edit_documentation'))
    
    # Check if slug already exists
    if Document.query.filter_by(slug=slug).first():
        flash('A document with this slug already exists.', 'danger')
        return redirect(url_for('docs.edit_documentation'))
    
    # Convert empty parent_id to None
    if parent_id == '':
        parent_id = None
    
    # Create new document
    document = Document(
        title=title,
        slug=slug,
        doc_type=doc_type,
        parent_id=parent_id,
        created_by=current_user.id,
        status=DocumentStatus.DRAFT.value
    )
    
    db.session.add(document)
    db.session.commit()
    
    # Create initial empty version
    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        content='',
        created_by=current_user.id
    )
    
    db.session.add(version)
    db.session.commit()
    
    flash('Document created successfully.', 'success')
    return redirect(url_for('docs.edit_documentation', doc_id=document.id))

@docs_bp.route('/save/<int:doc_id>', methods=['POST'])
@login_required
@admin_required
def save_document(doc_id):
    """Save changes to a document."""
    document = Document.query.get_or_404(doc_id)
    
    # Update document title and slug
    document.title = request.form.get('title')
    document.slug = request.form.get('slug')
    
    # Update document content (create new version)
    content = request.form.get('content')
    change_summary = request.form.get('change_summary')
    
    # Determine if we should publish directly
    publish = request.form.get('publish') == 'true'
    
    # Create new version
    version = document.create_version(
        content=content,
        user_id=current_user.id,
        is_published=publish,
        change_summary=change_summary
    )
    
    # Update document status if publishing
    if publish:
        document.status = DocumentStatus.PUBLISHED.value
    
    db.session.commit()
    
    flash('Document saved successfully.', 'success')
    return redirect(url_for('docs.edit_documentation', doc_id=document.id))

@docs_bp.route('/settings/<int:doc_id>', methods=['POST'])
@login_required
@admin_required
def update_settings(doc_id):
    """Update document settings."""
    document = Document.query.get_or_404(doc_id)
    
    # Update document type and parent
    document.doc_type = request.form.get('doc_type')
    parent_id = request.form.get('parent_id')
    document.parent_id = None if parent_id == '' else parent_id
    document.order = request.form.get('order', 0)
    
    # Update metadata
    metadata_json = request.form.get('metadata', '{}')
    try:
        import json
        metadata = json.loads(metadata_json)
        document.set_metadata(metadata)
    except Exception as e:
        logger.error(f"Error parsing metadata: {e}")
        flash('Error updating metadata.', 'danger')
        return redirect(url_for('docs.edit_documentation', doc_id=document.id))
    
    db.session.commit()
    
    flash('Document settings updated successfully.', 'success')
    return redirect(url_for('docs.edit_documentation', doc_id=document.id))

@docs_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
@admin_required
def delete_document(doc_id):
    """Delete a document."""
    document = Document.query.get_or_404(doc_id)
    
    # Check if document has children
    if document.children:
        # Either delete children or reassign
        for child in document.children:
            db.session.delete(child)
    
    db.session.delete(document)
    db.session.commit()
    
    flash('Document deleted successfully.', 'success')
    return redirect(url_for('docs.edit_documentation'))

@docs_bp.route('/version/<int:version_id>')
@login_required
@admin_required
def get_version(version_id):
    """Get a specific version of a document."""
    version = DocumentVersion.query.get_or_404(version_id)
    
    return jsonify({
        'success': True,
        'data': {
            'id': version.id,
            'document_id': version.document_id,
            'document_title': version.document.title,
            'version_number': version.version_number,
            'content': version.content,
            'created_by': version.created_by,
            'created_at': version.created_at.isoformat(),
            'is_published': version.is_published
        }
    })

@docs_bp.route('/publish/<int:doc_id>/<int:version_number>', methods=['POST'])
@login_required
@admin_required
def publish_version(doc_id, version_number):
    """Publish a specific version of a document."""
    document = Document.query.get_or_404(doc_id)
    
    success = document.publish_version(version_number)
    
    if success:
        flash('Document published successfully.', 'success')
    else:
        flash('Error publishing document.', 'danger')
    
    return redirect(url_for('docs.edit_documentation', doc_id=document.id))

@docs_bp.route('/unpublish/<int:doc_id>', methods=['POST'])
@login_required
@admin_required
def unpublish_document(doc_id):
    """Unpublish a document."""
    document = Document.query.get_or_404(doc_id)
    
    # Unpublish all versions
    for version in document.versions.filter_by(is_published=True).all():
        version.is_published = False
    
    document.status = DocumentStatus.DRAFT.value
    db.session.commit()
    
    flash('Document unpublished successfully.', 'success')
    return redirect(url_for('docs.edit_documentation', doc_id=document.id))

@docs_bp.route('/request-approval/<int:doc_id>', methods=['POST'])
@login_required
@admin_required
def request_approval(doc_id):
    """Request approval for a document."""
    document = Document.query.get_or_404(doc_id)
    reviewer_id = request.form.get('reviewer_id')
    
    if not reviewer_id:
        flash('Reviewer is required.', 'danger')
        return redirect(url_for('docs.edit_documentation', doc_id=document.id))
    
    # Get the latest version
    latest_version = document.latest_version
    
    if not latest_version:
        flash('No version to approve.', 'danger')
        return redirect(url_for('docs.edit_documentation', doc_id=document.id))
    
    # Submit for approval
    success = document.submit_for_approval(latest_version.version_number, reviewer_id)
    
    if success:
        flash('Document submitted for approval.', 'success')
    else:
        flash('Error submitting document for approval.', 'danger')
    
    return redirect(url_for('docs.edit_documentation', doc_id=document.id))

@docs_bp.route('/approve/<int:approval_id>', methods=['POST'])
@login_required
@admin_required
def approve_document(approval_id):
    """Approve a document."""
    approval = DocumentApproval.query.get_or_404(approval_id)
    
    # Check if user is the assigned reviewer
    if approval.reviewer_id != current_user.id:
        flash('You are not authorized to approve this document.', 'danger')
        return redirect(url_for('docs.edit_documentation', doc_id=approval.document_id))
    
    feedback = request.form.get('feedback')
    success = approval.approve(feedback)
    
    if success:
        flash('Document approved and published.', 'success')
    else:
        flash('Error approving document.', 'danger')
    
    return redirect(url_for('docs.edit_documentation', doc_id=approval.document_id))

@docs_bp.route('/reject/<int:approval_id>', methods=['POST'])
@login_required
@admin_required
def reject_document(approval_id):
    """Reject a document."""
    approval = DocumentApproval.query.get_or_404(approval_id)
    
    # Check if user is the assigned reviewer
    if approval.reviewer_id != current_user.id:
        flash('You are not authorized to reject this document.', 'danger')
        return redirect(url_for('docs.edit_documentation', doc_id=approval.document_id))
    
    feedback = request.form.get('feedback')
    
    if not feedback:
        flash('Feedback is required when rejecting a document.', 'danger')
        return redirect(url_for('docs.edit_documentation', doc_id=approval.document_id))
    
    success = approval.reject(feedback)
    
    if success:
        flash('Document rejected.', 'success')
    else:
        flash('Error rejecting document.', 'danger')
    
    return redirect(url_for('docs.edit_documentation', doc_id=approval.document_id))

@docs_bp.route('/search')
def search():
    """Search documentation content."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({
            'success': False,
            'message': 'Search query is required'
        }), 400
    
    # Search in document titles and content
    documents = Document.query.filter(
        (Document.title.ilike(f'%{query}%')) |
        (Document.id.in_(
            db.session.query(DocumentVersion.document_id).filter(
                DocumentVersion.content.ilike(f'%{query}%')
            )
        ))
    ).all()
    
    results = []
    for doc in documents:
        # Only include published documents for non-admin users
        if doc.status == DocumentStatus.PUBLISHED.value or (current_user.is_authenticated and current_user.is_admin()):
            # Get matching version
            version = doc.published_version or doc.latest_version
            
            # Simple content snippet extraction
            content = version.content if version else ""
            lower_content = content.lower()
            query_pos = lower_content.find(query.lower())
            
            if query_pos >= 0:
                # Extract snippet around match
                start = max(0, query_pos - 50)
                end = min(len(content), query_pos + len(query) + 50)
                snippet = '...' + content[start:end] + '...'
            else:
                # Use first 100 chars as fallback
                snippet = content[:100] + '...' if content and len(content) > 100 else content
            
            results.append({
                'id': doc.id,
                'title': doc.title,
                'url': url_for('docs.view_document', doc_slug=doc.slug),
                'snippet': snippet,
                'doc_type': doc.doc_type,
                'updated_at': doc.updated_at.isoformat()
            })
    
    return jsonify({
        'success': True,
        'data': {
            'query': query,
            'results': results
        }
    })