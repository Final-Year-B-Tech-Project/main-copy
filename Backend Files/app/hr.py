"""
Enhanced HR Blueprint
Comprehensive HR management system with advanced features
"""

import json
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, desc, and_, or_
from app import db
from app.models import User, JobDrive, InterviewSession, HRProfile
from app.utils import generate_interview_link
from app.logger import log_user_action, log_interview_action
from app.email_service import send_shortlist_notification, send_registration_invitation

hr = Blueprint('hr', __name__, url_prefix='/hr')

def hr_required(f):
    """Decorator to ensure user is HR"""
    from functools import wraps
    @wraps(f)
    def hr_decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'hr':
            flash('Access denied. HR access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return hr_decorated_function

@hr.route('/dashboard')
@login_required
@hr_required
def enhanced_dashboard():
    """Enhanced HR dashboard with comprehensive analytics"""
    
    # Get HR's job drives
    job_drives = JobDrive.query.join(HRProfile).filter_by(user_id=current_user.id).all()
    drive_ids = [drive.id for drive in job_drives]
    
    # Get interview statistics
    recent_interviews = InterviewSession.query.filter(
        InterviewSession.job_drive_id.in_(drive_ids) if drive_ids else False
    ).order_by(InterviewSession.created_at.desc()).limit(20).all()
    
    # Calculate statistics
    total_drives = len(job_drives)
    total_interviews = len(recent_interviews)
    completed_interviews = len([i for i in recent_interviews if i.status == 'completed'])
    
    # Get performance metrics
    performance_data = get_hr_performance_metrics(current_user.id)
    
    # Get recent activity
    recent_activity = get_recent_hr_activity(current_user.id)
    
    return render_template('hr/enhanced_dashboard.html',
                         job_drives=job_drives,
                         recent_interviews=recent_interviews,
                         total_drives=total_drives,
                         total_interviews=total_interviews,
                         completed_interviews=completed_interviews,
                         performance_data=performance_data,
                         recent_activity=recent_activity)

@hr.route('/analytics')
@login_required
@hr_required
def analytics_dashboard():
    """Comprehensive HR analytics dashboard"""
    
    # Get time-based analytics
    analytics_data = get_comprehensive_analytics(current_user.id)
    
    return render_template('hr/analytics_dashboard.html', 
                         analytics=analytics_data)

@hr.route('/candidate-management')
@login_required
@hr_required
def candidate_management():
    """Advanced candidate management interface"""
    
    # Get all candidates who have interviewed for HR's drives
    hr_drives = JobDrive.query.join(HRProfile).filter_by(user_id=current_user.id).all()
    drive_ids = [drive.id for drive in hr_drives]
    
    candidates_query = db.session.query(User, InterviewSession).join(
        InterviewSession, User.id == InterviewSession.candidate_id
    ).filter(
        InterviewSession.job_drive_id.in_(drive_ids) if drive_ids else False
    ).distinct(User.id)
    
    candidates = candidates_query.all()
    
    # Get candidate statistics
    candidate_stats = get_candidate_statistics(drive_ids)
    
    return render_template('hr/candidate_management.html',
                         candidates=candidates,
                         candidate_stats=candidate_stats)

@hr.route('/bulk-operations')
@login_required
@hr_required
def bulk_operations():
    """Bulk operations interface for HR"""
    
    # Get available job drives
    job_drives = JobDrive.query.join(HRProfile).filter_by(user_id=current_user.id).all()
    
    return render_template('hr/bulk_operations.html', job_drives=job_drives)

@hr.route('/interview-templates')
@login_required
@hr_required
def interview_templates():
    """Manage interview question templates"""
    
    # Get saved templates (this would be stored in database in production)
    templates = get_interview_templates(current_user.id)
    
    return render_template('hr/interview_templates.html', templates=templates)

@hr.route('/reports')
@login_required
@hr_required
def reports_dashboard():
    """Generate and view various HR reports"""
    
    # Get report data
    report_data = generate_hr_reports(current_user.id)
    
    return render_template('hr/reports_dashboard.html', reports=report_data)

@hr.route('/api/candidate-search')
@login_required
@hr_required
def candidate_search():
    """API endpoint for candidate search"""
    
    query = request.args.get('q', '').strip()
    skills = request.args.get('skills', '').split(',')
    experience = request.args.get('experience', '')
    
    # Build search query
    search_results = search_candidates(query, skills, experience, current_user.id)
    
    return jsonify({
        'success': True,
        'candidates': search_results
    })

@hr.route('/api/schedule-bulk-interviews', methods=['POST'])
@login_required
@hr_required
def schedule_bulk_interviews():
    """API endpoint for bulk interview scheduling"""
    
    try:
        data = request.get_json()
        drive_id = data.get('drive_id')
        candidate_emails = data.get('candidate_emails', [])
        interview_date = data.get('interview_date')
        
        # Validate drive ownership
        drive = JobDrive.query.join(HRProfile).filter_by(
            user_id=current_user.id
        ).filter(JobDrive.id == drive_id).first()
        
        if not drive:
            return jsonify({'success': False, 'message': 'Job drive not found'}), 404
        
        results = []
        
        for email in candidate_emails:
            try:
                result = schedule_single_interview(email, drive, interview_date)
                results.append(result)
            except Exception as e:
                results.append({
                    'email': email,
                    'success': False,
                    'message': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@hr.route('/api/export-data')
@login_required
@hr_required
def export_hr_data():
    """Export HR data in various formats"""
    
    export_type = request.args.get('type', 'interviews')
    format_type = request.args.get('format', 'csv')
    
    try:
        export_data = generate_export_data(current_user.id, export_type)
        
        if format_type == 'csv':
            return generate_csv_response(export_data, export_type)
        elif format_type == 'json':
            return jsonify(export_data)
        else:
            return jsonify({'success': False, 'message': 'Unsupported format'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@hr.route('/api/interview-feedback/<int:session_id>')
@login_required
@hr_required
def get_interview_feedback(session_id):
    """Get detailed interview feedback"""
    
    # Verify session belongs to HR's drive
    session = InterviewSession.query.join(JobDrive).join(HRProfile).filter(
        HRProfile.user_id == current_user.id,
        InterviewSession.id == session_id
    ).first()
    
    if not session:
        return jsonify({'success': False, 'message': 'Interview not found'}), 404
    
    # Parse feedback data
    feedback = json.loads(session.ai_feedback) if session.ai_feedback else {}
    
    return jsonify({
        'success': True,
        'feedback': feedback,
        'session': {
            'id': session.id,
            'candidate_name': session.candidate.full_name,
            'candidate_email': session.candidate.email,
            'status': session.status,
            'overall_score': session.overall_score,
            'created_at': session.created_at.isoformat(),
            'duration': session.duration
        }
    })

# Helper functions

def get_hr_performance_metrics(hr_user_id):
    """Get performance metrics for HR"""
    
    hr_profile = HRProfile.query.filter_by(user_id=hr_user_id).first()
    if not hr_profile:
        return {}
    
    # Get drives and interviews
    drives = JobDrive.query.filter_by(hr_id=hr_profile.id).all()
    drive_ids = [d.id for d in drives]
    
    if not drive_ids:
        return {}
    
    interviews = InterviewSession.query.filter(
        InterviewSession.job_drive_id.in_(drive_ids)
    ).all()
    
    # Calculate metrics
    total_interviews = len(interviews)
    completed = len([i for i in interviews if i.status == 'completed'])
    avg_score = 0
    
    if completed > 0:
        scores = [i.overall_score for i in interviews if i.overall_score]
        avg_score = sum(scores) / len(scores) if scores else 0
    
    return {
        'total_drives': len(drives),
        'total_interviews': total_interviews,
        'completed_interviews': completed,
        'completion_rate': (completed / total_interviews * 100) if total_interviews > 0 else 0,
        'average_score': avg_score,
        'active_drives': len([d for d in drives if d.is_active])
    }

def get_recent_hr_activity(hr_user_id):
    """Get recent activity for HR"""
    
    # This would typically come from an activity log table
    # For now, return sample data
    return [
        {
            'type': 'interview_completed',
            'title': 'Interview completed by John Doe',
            'time': '2 hours ago',
            'icon': 'user-check'
        },
        {
            'type': 'drive_created',
            'title': 'New job drive created: Senior Developer',
            'time': '1 day ago',
            'icon': 'briefcase'
        },
        {
            'type': 'candidate_registered',
            'title': 'New candidate registered: Jane Smith',
            'time': '2 days ago',
            'icon': 'user-plus'
        }
    ]

def get_comprehensive_analytics(hr_user_id):
    """Get comprehensive analytics data"""
    
    # This would include various analytics calculations
    # For now, return sample structure
    return {
        'interview_trends': [],
        'candidate_sources': [],
        'performance_metrics': [],
        'time_analysis': []
    }

def get_candidate_statistics(drive_ids):
    """Get candidate statistics"""
    
    if not drive_ids:
        return {}
    
    total_candidates = db.session.query(func.count(func.distinct(InterviewSession.candidate_id))).filter(
        InterviewSession.job_drive_id.in_(drive_ids)
    ).scalar()
    
    return {
        'total_candidates': total_candidates or 0,
        'interviewed': 0,  # Would calculate from actual data
        'pending': 0,      # Would calculate from actual data
        'hired': 0         # Would calculate from actual data
    }

def get_interview_templates(hr_user_id):
    """Get interview templates for HR"""
    
    # This would come from a templates table
    # For now, return sample templates
    return [
        {
            'id': 1,
            'name': 'Technical Interview - Software Developer',
            'questions': 15,
            'duration': '45 minutes',
            'created_at': '2024-01-15'
        },
        {
            'id': 2,
            'name': 'Behavioral Interview - All Positions',
            'questions': 10,
            'duration': '30 minutes',
            'created_at': '2024-01-10'
        }
    ]

def generate_hr_reports(hr_user_id):
    """Generate various HR reports"""
    
    # This would generate actual reports
    # For now, return sample report structure
    return {
        'monthly_summary': {},
        'candidate_pipeline': {},
        'interview_performance': {},
        'hiring_metrics': {}
    }

def search_candidates(query, skills, experience, hr_user_id):
    """Search candidates based on criteria"""
    
    # This would implement actual candidate search
    # For now, return empty results
    return []

def schedule_single_interview(email, drive, interview_date):
    """Schedule interview for a single candidate"""
    
    try:
        # Find or create candidate
        candidate = User.query.filter_by(email=email, user_type='student').first()
        
        if not candidate:
            # Send registration invitation
            send_registration_invitation(
                candidate_email=email,
                job_title=drive.title,
                company_name=drive.hr.company_name,
                registration_link=f"{request.url_root}register"
            )
            return {
                'email': email,
                'success': True,
                'action': 'registration_invitation_sent'
            }
        
        # Create interview session
        session = InterviewSession(
            candidate_id=candidate.id,
            job_drive_id=drive.id,
            session_type='actual',
            status='scheduled',
            scheduled_time=datetime.fromisoformat(interview_date),
            interview_link=generate_interview_link()
        )
        
        db.session.add(session)
        db.session.flush()
        
        # Send notification
        interview_url = f"{request.url_root}interview/{session.id}?link={session.interview_link}"
        send_shortlist_notification(
            candidate_email=candidate.email,
            candidate_name=candidate.full_name,
            job_title=drive.title,
            company_name=drive.hr.company_name,
            interview_link=interview_url
        )
        
        return {
            'email': email,
            'success': True,
            'action': 'interview_scheduled',
            'session_id': session.id
        }
        
    except Exception as e:
        return {
            'email': email,
            'success': False,
            'message': str(e)
        }

def generate_export_data(hr_user_id, export_type):
    """Generate data for export"""
    
    # This would generate actual export data
    # For now, return sample structure
    return {
        'data': [],
        'metadata': {
            'export_type': export_type,
            'generated_at': datetime.utcnow().isoformat(),
            'hr_id': hr_user_id
        }
    }

def generate_csv_response(data, export_type):
    """Generate CSV response"""
    
    # This would generate actual CSV
    # For now, return JSON
    return jsonify(data)