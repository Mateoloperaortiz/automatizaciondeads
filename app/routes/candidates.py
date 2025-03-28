from flask import Blueprint, jsonify, request, render_template
from app.models.candidate import Candidate
from app import db

candidates_bp = Blueprint('candidates', __name__, url_prefix='/candidates')

@candidates_bp.route('/')
def list_candidates():
    """Get all candidates."""
    candidates = Candidate.query.all()
    return render_template('candidates/list.html', candidates=candidates)

@candidates_bp.route('/<int:candidate_id>')
def get_candidate(candidate_id):
    """Get a specific candidate."""
    candidate = Candidate.query.get_or_404(candidate_id)
    return render_template('candidates/detail.html', candidate=candidate)

# API routes
@candidates_bp.route('/api', methods=['GET'])
def api_list_candidates():
    """API endpoint to get all candidates."""
    candidates = Candidate.query.all()
    return jsonify({
        'success': True,
        'data': [candidate.to_dict() for candidate in candidates]
    })

@candidates_bp.route('/api/<int:candidate_id>', methods=['GET'])
def api_get_candidate(candidate_id):
    """API endpoint to get a specific candidate."""
    candidate = Candidate.query.get_or_404(candidate_id)
    return jsonify({
        'success': True,
        'data': candidate.to_dict()
    })

@candidates_bp.route('/api', methods=['POST'])
def api_create_candidate():
    """API endpoint to create a new candidate."""
    data = request.get_json()
    
    new_candidate = Candidate(
        age=data.get('age'),
        gender=data.get('gender'),
        location=data.get('location'),
        education_level=data.get('education_level'),
        field_of_study=data.get('field_of_study'),
        years_of_experience=data.get('years_of_experience'),
        desired_job_type=data.get('desired_job_type'),
        desired_industry=data.get('desired_industry'),
        desired_role=data.get('desired_role'),
        desired_salary=data.get('desired_salary')
    )
    
    db.session.add(new_candidate)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Candidate created successfully',
        'data': new_candidate.to_dict()
    }), 201 