"""
Simplified HR Blueprint - No complex dependencies
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
from app import db
from app.models import User, JobDrive, InterviewSession, HRProfile
from app.utils import generate_interview_link

hr = Blueprint('hr', __name__, url_prefix='/hr')

@hr.route('/dashboard')
@login_required
def dashboard():
    """HR Dashboard - Simplified"""
    if current_user.user_type != 'hr':
        flash('Access denied. HR only.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Get job drives safely
        job_drives = []
        recent_interviews = []
        
        if hasattr(current_user, 'hr_profile') and current_user.hr_profile:
            job_drives = JobDrive.query.filter_by(hr_id=current_user.hr_profile.id).all()
            
            if job_drives:
                drive_ids = [drive.id for drive in job_drives]
                recent_interviews = InterviewSession.query.filter(
                    InterviewSession.job_drive_id.in_(drive_ids)
                ).order_by(InterviewSession.created_at.desc()).limit(10).all()
        
        stats = {
            'total_drives': len(job_drives),
            'total_interviews': len(recent_interviews),
            'completed_interviews': len([i for i in recent_interviews if i.status == 'completed'])
        }
        
        return render_template('hr/perfect_dashboard.html',
                             job_drives=job_drives,
                             recent_interviews=recent_interviews,
                             stats=stats)
    
    except Exception as e:
        print(f"HR Dashboard Error: {e}")
        return render_template('hr/perfect_dashboard.html',
                             job_drives=[],
                             recent_interviews=[],
                             stats={'total_drives': 0, 'total_interviews': 0, 'completed_interviews': 0})

@hr.route('/drives')
@login_required
def drives():
    """Job Drives Management"""
    if current_user.user_type != 'hr':
        flash('Access denied. HR only.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        drives = []
        if hasattr(current_user, 'hr_profile') and current_user.hr_profile:
            drives = JobDrive.query.filter_by(hr_id=current_user.hr_profile.id).order_by(JobDrive.created_at.desc()).all()
        
        return render_template('hr/perfect_drives.html', drives=drives)
    
    except Exception as e:
        print(f"HR Drives Error: {e}")
        return render_template('hr/perfect_drives.html', drives=[])

@hr.route('/create-drive', methods=['GET', 'POST'])
@login_required
def create_drive():
    """Create Job Drive - Simplified"""
    if current_user.user_type != 'hr':
        flash('Access denied. HR only.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Ensure HR profile exists
            if not hasattr(current_user, 'hr_profile') or not current_user.hr_profile:
                flash('HR profile not found. Please contact admin.', 'error')
                return redirect(url_for('hr.dashboard'))
            
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            job_role = request.form.get('job_role', '').strip()
            experience_required = request.form.get('experience_required', 'Any')
            location = request.form.get('location', 'Remote').strip()
            
            if not title or not job_role:
                flash('Title and Job Role are required.', 'error')
                return render_template('hr/perfect_create_drive.html')
            
            # Create job drive
            drive = JobDrive(
                hr_id=current_user.hr_profile.id,
                title=title,
                description=description,
                job_role=job_role,
                experience_required=experience_required,
                location=location,
                skills_required=json.dumps([]),
                number_of_positions=1,
                is_active=True
            )
            
            db.session.add(drive)
            db.session.commit()
            
            flash('Job drive created successfully!', 'success')
            return redirect(url_for('hr.drives'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Create Drive Error: {e}")
            flash('Failed to create job drive. Please try again.', 'error')
    
    return render_template('hr/perfect_create_drive.html')

@hr.route('/drive/<int:drive_id>/candidates')
@login_required
def drive_candidates(drive_id):
    """View Candidates for Drive"""
    if current_user.user_type != 'hr':
        flash('Access denied. HR only.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Verify drive ownership
        drive = None
        if hasattr(current_user, 'hr_profile') and current_user.hr_profile:
            drive = JobDrive.query.filter_by(id=drive_id, hr_id=current_user.hr_profile.id).first()
        
        if not drive:
            flash('Drive not found or access denied.', 'error')
            return redirect(url_for('hr.drives'))
        
        # Get interviews for this drive
        interviews = InterviewSession.query.filter_by(job_drive_id=drive_id).all()
        
        return render_template('hr/fixed_candidates.html', drive=drive, interviews=interviews)
    
    except Exception as e:
        print(f"Drive Candidates Error: {e}")
        flash('Error loading candidates.', 'error')
        return redirect(url_for('hr.drives'))

@hr.route('/schedule-interview', methods=['POST'])
@login_required
def schedule_interview():
    """Schedule Interview - Simplified"""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        drive_id = data.get('drive_id')
        candidate_email = data.get('candidate_email')
        
        # Find candidate
        candidate = User.query.filter_by(email=candidate_email, user_type='student').first()
        if not candidate:
            return jsonify({'success': False, 'message': 'Candidate not found'}), 404
        
        # Verify drive ownership
        drive = None
        if hasattr(current_user, 'hr_profile') and current_user.hr_profile:
            drive = JobDrive.query.filter_by(id=drive_id, hr_id=current_user.hr_profile.id).first()
        
        if not drive:
            return jsonify({'success': False, 'message': 'Drive not found'}), 404
        
        # Create interview session
        session = InterviewSession(
            candidate_id=candidate.id,
            job_drive_id=drive_id,
            session_type='actual',
            status='scheduled',
            scheduled_time=datetime.utcnow() + timedelta(hours=1),
            interview_link=generate_interview_link()
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Interview scheduled successfully',
            'session_id': session.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Schedule Interview Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@hr.route('/drive/<int:drive_id>/toggle', methods=['POST'])
@login_required
def toggle_drive(drive_id):
    """Toggle Drive Status"""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Verify drive ownership
        drive = None
        if hasattr(current_user, 'hr_profile') and current_user.hr_profile:
            drive = JobDrive.query.filter_by(id=drive_id, hr_id=current_user.hr_profile.id).first()
        
        if not drive:
            return jsonify({'success': False, 'message': 'Drive not found'}), 404
        
        # Toggle status
        drive.is_active = not drive.is_active
        db.session.commit()
        
        status = 'activated' if drive.is_active else 'deactivated'
        return jsonify({
            'success': True,
            'message': f'Job drive {status} successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@hr.route('/drive/<int:drive_id>/delete', methods=['DELETE'])
@login_required
def delete_drive(drive_id):
    """Delete Job Drive"""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Verify drive ownership
        drive = None
        if hasattr(current_user, 'hr_profile') and current_user.hr_profile:
            drive = JobDrive.query.filter_by(id=drive_id, hr_id=current_user.hr_profile.id).first()
        
        if not drive:
            return jsonify({'success': False, 'message': 'Drive not found'}), 404
        
        # Delete associated interview sessions first
        InterviewSession.query.filter_by(job_drive_id=drive_id).delete()
        
        # Delete the drive
        db.session.delete(drive)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job drive deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@hr.route('/bulk-schedule-interview', methods=['POST'])
@login_required
def bulk_schedule_interview():
    """Bulk Schedule Interviews"""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        drive_id = data.get('drive_id')
        candidate_emails = data.get('candidate_emails', [])
        
        if not candidate_emails:
            return jsonify({'success': False, 'message': 'No candidates provided'}), 400
        
        # Verify drive ownership
        drive = None
        if hasattr(current_user, 'hr_profile') and current_user.hr_profile:
            drive = JobDrive.query.filter_by(id=drive_id, hr_id=current_user.hr_profile.id).first()
        
        if not drive:
            return jsonify({'success': False, 'message': 'Drive not found'}), 404
        
        successful = []
        failed = []
        
        for email in candidate_emails:
            try:
                candidate = User.query.filter_by(email=email.strip(), user_type='student').first()
                if not candidate:
                    failed.append({'email': email, 'reason': 'Candidate not found'})
                    continue
                
                session = InterviewSession(
                    candidate_id=candidate.id,
                    job_drive_id=drive_id,
                    session_type='actual',
                    status='scheduled',
                    scheduled_time=datetime.utcnow() + timedelta(hours=1),
                    interview_link=generate_interview_link()
                )
                
                db.session.add(session)
                successful.append({'email': email, 'session_id': session.id})
                
            except Exception as e:
                failed.append({'email': email, 'reason': str(e)})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Scheduled {len(successful)} interviews successfully',
            'successful': successful,
            'failed': failed
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500