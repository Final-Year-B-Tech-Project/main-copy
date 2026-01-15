from flask import Blueprint, jsonify
from app.models import User, StudentProfile, JobDrive
from app.resume_models import CandidateScore
from app import db
import json

test_bp = Blueprint('test', __name__, url_prefix='/test')

@test_bp.route('/candidates/<int:job_id>')
def test_candidates(job_id):
    """Test route to show candidates data"""
    
    # Get shortlisted candidates
    shortlisted_candidates = db.session.query(
        CandidateScore, User, StudentProfile
    ).join(
        StudentProfile, CandidateScore.student_id == StudentProfile.id
    ).join(
        User, StudentProfile.user_id == User.id
    ).filter(
        CandidateScore.job_drive_id == job_id,
        CandidateScore.is_shortlisted == True
    ).order_by(CandidateScore.overall_score.desc()).all()
    
    candidates_data = []
    for score, user, profile in shortlisted_candidates:
        candidates_data.append({
            'name': user.full_name,
            'email': user.email,
            'overall_score': score.overall_score,
            'skill_match_score': score.skill_match_score,
            'is_shortlisted': score.is_shortlisted
        })
    
    return jsonify({
        'job_id': job_id,
        'total_shortlisted': len(candidates_data),
        'candidates': candidates_data
    })