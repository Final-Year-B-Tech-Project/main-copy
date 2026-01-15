from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import StudentProfile, JobDrive
from app.resume_models import ParsedResume, CandidateScore, JobRequirement
from app.resume_parser import EnhancedResumeParser
from app.candidate_scoring import CandidateScoringEngine

resume_api = Blueprint('resume_api', __name__, url_prefix='/api/resume')

@resume_api.route('/parse', methods=['POST'])
@login_required
def parse_resume():
    """Parse uploaded resume and extract information"""
    if current_user.user_type != 'student':
        return jsonify({'success': False, 'error': 'Only students can upload resumes'}), 403
    
    if 'resume' not in request.files:
        return jsonify({'success': False, 'error': 'No resume file provided'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(f"resume_{current_user.id}_{file.filename}")
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes', filename)
        file.save(file_path)
        
        # Parse resume
        parser = EnhancedResumeParser()
        result = parser.parse_resume(file_path, current_user.student_profile.id)
        
        if result['success']:
            # Update student profile with parsed data
            student_profile = current_user.student_profile
            student_profile.resume_file = f"uploads/resumes/{filename}"
            
            # Get parsed resume data
            parsed_resume = ParsedResume.query.get(result['parsed_resume_id'])
            if parsed_resume and parsed_resume.email:
                # Update contact info if found
                if not current_user.email or '@' not in current_user.email:
                    current_user.email = parsed_resume.email
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Resume parsed successfully!',
                'data': {
                    'skills_extracted': result['skills_extracted'],
                    'total_experience': result['total_experience'],
                    'contact_info': result.get('contact_info', {}),
                    'processing_time': result['processing_time']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@resume_api.route('/skills/<int:student_id>')
@login_required
def get_candidate_skills(student_id):
    """Get extracted skills for a candidate"""
    from app.resume_models import CandidateSkill
    
    skills = CandidateSkill.query.filter_by(student_id=student_id).all()
    
    skills_data = []
    for skill in skills:
        skills_data.append({
            'id': skill.id,
            'name': skill.skill_name,
            'category': skill.skill_category,
            'type': skill.skill_type,
            'proficiency': skill.proficiency_level,
            'years_experience': skill.years_experience,
            'confidence': skill.confidence_score,
            'source': skill.extracted_from
        })
    
    return jsonify({
        'success': True,
        'skills': skills_data,
        'total_skills': len(skills_data)
    })

@resume_api.route('/score-candidate', methods=['POST'])
@login_required
def score_candidate():
    """Score a candidate for a specific job"""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'error': 'Only HR can score candidates'}), 403
    
    data = request.get_json()
    student_id = data.get('student_id')
    job_drive_id = data.get('job_drive_id')
    
    if not all([student_id, job_drive_id]):
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
    
    try:
        scoring_engine = CandidateScoringEngine()
        result = scoring_engine.score_candidate_for_job(student_id, job_drive_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@resume_api.route('/bulk-score/<int:job_drive_id>', methods=['POST'])
@login_required
def bulk_score_candidates(job_drive_id):
    """Score all candidates for a job"""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'error': 'Only HR can score candidates'}), 403
    
    try:
        scoring_engine = CandidateScoringEngine()
        results = scoring_engine.bulk_score_candidates(job_drive_id)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@resume_api.route('/shortlisted/<int:job_drive_id>')
@login_required
def get_shortlisted_candidates(job_drive_id):
    """Get shortlisted candidates for a job"""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'error': 'Only HR can view shortlisted candidates'}), 403
    
    try:
        scoring_engine = CandidateScoringEngine()
        candidates = scoring_engine.get_shortlisted_candidates(job_drive_id)
        
        return jsonify({
            'success': True,
            'candidates': candidates,
            'total_shortlisted': len(candidates)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@resume_api.route('/job-requirements/<int:job_drive_id>')
@login_required
def get_job_requirements(job_drive_id):
    """Get detailed job requirements"""
    job_req = JobRequirement.query.filter_by(job_drive_id=job_drive_id).first()
    
    if not job_req:
        return jsonify({'success': False, 'error': 'Job requirements not found'}), 404
    
    return jsonify({
        'success': True,
        'requirements': {
            'required_skills': job_req.required_skills,
            'preferred_skills': job_req.preferred_skills,
            'min_experience': job_req.min_experience_years,
            'max_experience': job_req.max_experience_years,
            'experience_level': job_req.experience_level,
            'min_degree': job_req.min_degree_level,
            'location_type': job_req.location_type
        }
    })

@resume_api.route('/create-job-requirements', methods=['POST'])
@login_required
def create_job_requirements():
    """Create detailed job requirements"""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'error': 'Only HR can create job requirements'}), 403
    
    data = request.get_json()
    
    try:
        job_req = JobRequirement(
            job_drive_id=data['job_drive_id'],
            required_skills=data.get('required_skills', '[]'),
            preferred_skills=data.get('preferred_skills', '[]'),
            min_experience_years=data.get('min_experience_years', 0),
            max_experience_years=data.get('max_experience_years', 10),
            experience_level=data.get('experience_level', 'entry'),
            min_degree_level=data.get('min_degree_level', 'bachelor'),
            location_type=data.get('location_type', 'hybrid')
        )
        
        db.session.add(job_req)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job requirements created successfully',
            'job_requirement_id': job_req.id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@resume_api.route('/candidate-dashboard')
@login_required
def candidate_dashboard():
    """Get candidate's resume parsing and scoring dashboard"""
    if current_user.user_type != 'student':
        return jsonify({'success': False, 'error': 'Only students can access this'}), 403
    
    try:
        student_id = current_user.student_profile.id
        
        # Get parsed resume data
        parsed_resume = ParsedResume.query.filter_by(student_id=student_id).first()
        
        # Get candidate skills
        from app.resume_models import CandidateSkill
        skills = CandidateSkill.query.filter_by(student_id=student_id).all()
        
        # Get candidate scores
        scores = CandidateScore.query.filter_by(student_id=student_id).all()
        
        dashboard_data = {
            'resume_parsed': parsed_resume is not None,
            'total_skills': len(skills),
            'total_applications': len(scores),
            'shortlisted_count': len([s for s in scores if s.is_shortlisted]),
            'average_score': sum([s.overall_score for s in scores]) / len(scores) if scores else 0,
            'skills_by_category': {},
            'recent_scores': []
        }
        
        # Group skills by category
        for skill in skills:
            category = skill.skill_category or 'other'
            if category not in dashboard_data['skills_by_category']:
                dashboard_data['skills_by_category'][category] = []
            dashboard_data['skills_by_category'][category].append({
                'name': skill.skill_name,
                'proficiency': skill.proficiency_level
            })
        
        # Recent scores
        for score in scores[-5:]:  # Last 5 scores
            job = JobDrive.query.get(score.job_drive_id)
            dashboard_data['recent_scores'].append({
                'job_title': job.title if job else 'Unknown',
                'overall_score': score.overall_score,
                'is_shortlisted': score.is_shortlisted,
                'scored_at': score.scored_at.isoformat() if score.scored_at else None
            })
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500