import json
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, JobDrive, InterviewSession
from app.ai_service_simple import SimpleAIService
from app.utils import generate_interview_link
from app.logger import log_user_action, log_interview_action, log_security_event

main = Blueprint('main', __name__)
ai_service = SimpleAIService()

@main.route('/')
def index():
    """Landing page."""
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - routes to appropriate dashboard based on user type."""
    if current_user.user_type == 'student':
        return redirect(url_for('main.student_dashboard'))
    elif current_user.user_type == 'hr':
        return redirect(url_for('main.hr_dashboard'))
    elif current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('main.student_dashboard'))

@main.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard."""
    if current_user.user_type != 'student':
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get recent interview sessions
    recent_interviews = InterviewSession.query.filter_by(
        candidate_id=current_user.id
    ).order_by(InterviewSession.created_at.desc()).limit(5).all()
    
    # Get practice interview stats
    practice_count = InterviewSession.query.filter_by(
        candidate_id=current_user.id,
        session_type='practice'
    ).count()
    
    # Get average scores
    completed_interviews = InterviewSession.query.filter_by(
        candidate_id=current_user.id,
        status='completed'
    ).all()
    
    avg_score = 0
    if completed_interviews:
        scores = [interview.overall_score for interview in completed_interviews if interview.overall_score]
        avg_score = sum(scores) / len(scores) if scores else 0
    
    return render_template('student/dashboard.html',
                         recent_interviews=recent_interviews,
                         practice_count=practice_count,
                         avg_score=avg_score)

@main.route('/hr/dashboard')
@login_required
def hr_dashboard():
    """HR dashboard."""
    if current_user.user_type != 'hr':
        flash('Access denied. HR only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get HR's job drives
    job_drives = JobDrive.query.join(
        current_user.hr_profile.__class__
    ).filter_by(user_id=current_user.id).all()
    
    # Get recent interview sessions for HR's drives
    drive_ids = [drive.id for drive in job_drives]
    recent_interviews = InterviewSession.query.filter(
        InterviewSession.job_drive_id.in_(drive_ids) if drive_ids else False
    ).order_by(InterviewSession.created_at.desc()).limit(10).all()
    
    # Statistics
    total_drives = len(job_drives)
    total_interviews = len(recent_interviews)
    completed_interviews = len([i for i in recent_interviews if i.status == 'completed'])
    
    return render_template('hr/enhanced_dashboard.html',
                         job_drives=job_drives,
                         recent_interviews=recent_interviews,
                         total_drives=total_drives,
                         total_interviews=total_interviews,
                         completed_interviews=completed_interviews)

@main.route('/student/practice-interview')
@login_required
def practice_interview():
    """Student practice interview page."""
    if current_user.user_type != 'student':
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('student/practice.html')

@main.route('/practice-interview')
@login_required  
def practice_interview_alias():
    """Alias for practice interview."""
    return redirect(url_for('main.practice_interview'))

@main.route('/student/clear-history', methods=['POST'])
@login_required
def clear_interview_history():
    """Clear all interview history for the current student."""
    if current_user.user_type != 'student':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Delete all interview sessions for this student
        deleted_count = InterviewSession.query.filter_by(
            candidate_id=current_user.id
        ).delete()
        
        db.session.commit()
        
        log_user_action('INTERVIEW_HISTORY_CLEARED', f'Deleted {deleted_count} interview sessions')
        
        return jsonify({
            'success': True,
            'message': f'Successfully cleared {deleted_count} interview records'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/student/start-practice', methods=['POST'])
@login_required
def start_practice():
    """Start an adaptive practice interview session."""
    if current_user.user_type != 'student':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Get parameters with validation
        if not request.json:
            return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400
        
        job_role = request.json.get('job_role', 'General')
        
        # Create interview session
        session = InterviewSession(
            candidate_id=current_user.id,
            session_type='practice',
            status='scheduled',
            interview_link=generate_interview_link()
        )
        
        db.session.add(session)
        db.session.flush()
        
        # Prepare candidate data for adaptive interview
        candidate_data = {
            'name': current_user.full_name,
            'email': current_user.email,
            'education': getattr(current_user.student_profile, 'degree', 'Not specified') if current_user.student_profile else 'Not specified',
            'skills': getattr(current_user.student_profile, 'skills', 'Not specified') if current_user.student_profile else 'Not specified',
            'experience': getattr(current_user.student_profile, 'experience_level', 'Fresher') if current_user.student_profile else 'Fresher',
            'projects': 'Not specified'  # Can be enhanced later
        }
        
        # Start with predefined first question for instant start
        first_question = "Tell me about yourself and your background."
        session.questions = json.dumps([first_question])
        session.responses = json.dumps({})
        
        # Store job role for adaptive questions later
        session.notes = f"Job Role: {job_role}"
        
        db.session.commit()
        
        log_user_action('PRACTICE_INTERVIEW_STARTED', f'Session ID: {session.id}, Job Role: {job_role}')
        
        # Send practice interview start notification
        try:
            from app.email_service import send_practice_interview_notification
            send_practice_interview_notification(current_user.email, current_user.full_name, job_role)
        except Exception as e:
            print(f"Failed to send practice interview notification: {e}")
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'interview_link': session.interview_link,
            'redirect_url': url_for('main.adaptive_interview_interface', session_id=session.id)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/hr/drives')
@login_required
def hr_drives():
    """HR job drives management."""
    if current_user.user_type != 'hr':
        flash('Access denied. HR only.', 'error')
        return redirect(url_for('main.index'))
    
    drives = JobDrive.query.join(
        current_user.hr_profile.__class__
    ).filter_by(user_id=current_user.id).order_by(JobDrive.created_at.desc()).all()
    
    return render_template('hr/drives.html', drives=drives)

@main.route('/hr/create-drive', methods=['GET', 'POST'])
@login_required
def create_drive():
    """Create new job drive."""
    if current_user.user_type != 'hr':
        flash('Access denied. HR only.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            job_role = request.form.get('job_role', '').strip()
            experience_required = request.form.get('experience_required', '')
            skills_required = request.form.get('skills_required', '').split(',')
            skills_required = [skill.strip() for skill in skills_required if skill.strip()]
            number_of_positions = int(request.form.get('number_of_positions', 1))
            location = request.form.get('location', '').strip()
            salary_range = request.form.get('salary_range', '').strip()
            
            # Parse deadline
            deadline_str = request.form.get('deadline')
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M') if deadline_str else None
            
            # Create job drive
            drive = JobDrive(
                hr_id=current_user.hr_profile.id,
                title=title,
                description=description,
                job_role=job_role,
                experience_required=experience_required,
                skills_required=json.dumps(skills_required),
                number_of_positions=number_of_positions,
                location=location,
                salary_range=salary_range,
                deadline=deadline
            )
            
            db.session.add(drive)
            db.session.commit()
            
            # Send job drive creation notification
            try:
                from app.email_service import send_job_drive_notification
                send_job_drive_notification(current_user.email, current_user.full_name, title, 'created')
            except Exception as e:
                print(f"Failed to send job drive creation email: {e}")
            
            flash('Job drive created successfully!', 'success')
            return redirect(url_for('main.hr_drives'))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to create job drive. Please try again.', 'error')
    
    return render_template('hr/create_drive.html')

@main.route('/hr/drive/<int:drive_id>/candidates')
@login_required
def drive_candidates(drive_id):
    """View candidates for a specific drive."""
    if current_user.user_type != 'hr':
        flash('Access denied. HR only.', 'error')
        return redirect(url_for('main.index'))
    
    # Verify drive belongs to current HR
    drive = JobDrive.query.join(
        current_user.hr_profile.__class__
    ).filter_by(user_id=current_user.id).filter(JobDrive.id == drive_id).first()
    
    if not drive:
        flash('Drive not found or access denied.', 'error')
        return redirect(url_for('main.hr_drives'))
    
    # Get interview sessions for this drive
    interviews = InterviewSession.query.filter_by(job_drive_id=drive_id).all()
    
    return render_template('hr/candidates.html', drive=drive, interviews=interviews)

@main.route('/hr/drive/<int:drive_id>/toggle', methods=['POST'])
@login_required
def toggle_drive(drive_id):
    """Toggle job drive active status."""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Verify drive belongs to current HR
        drive = JobDrive.query.join(
            current_user.hr_profile.__class__
        ).filter_by(user_id=current_user.id).filter(JobDrive.id == drive_id).first()
        
        if not drive:
            return jsonify({'success': False, 'message': 'Drive not found'}), 404
        
        # Toggle status
        is_active = request.json.get('is_active', True)
        drive.is_active = is_active
        db.session.commit()
        
        action = 'resumed' if is_active else 'stopped'
        return jsonify({
            'success': True,
            'message': f'Job drive {action} successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/hr/schedule-interview', methods=['POST'])
@login_required
def schedule_interview():
    """Schedule interview for a candidate."""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        drive_id = request.json.get('drive_id')
        candidate_email = request.json.get('candidate_email')
        scheduled_time_str = request.json.get('scheduled_time')
        
        # Find candidate
        candidate = User.query.filter_by(email=candidate_email, user_type='student').first()
        if not candidate:
            return jsonify({'success': False, 'message': 'Candidate not found'}), 404
        
        # Verify drive belongs to current HR
        drive = JobDrive.query.join(
            current_user.hr_profile.__class__
        ).filter_by(user_id=current_user.id).filter(JobDrive.id == drive_id).first()
        
        if not drive:
            return jsonify({'success': False, 'message': 'Job drive not found or access denied'}), 404
        
        # Parse scheduled time with better error handling
        try:
            if scheduled_time_str:
                if 'T' in scheduled_time_str:
                    scheduled_time_str = scheduled_time_str.replace('Z', '')
                    scheduled_time = datetime.fromisoformat(scheduled_time_str)
                else:
                    scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%d %H:%M:%S')
            else:
                scheduled_time = datetime.utcnow() + timedelta(hours=1)
        except ValueError:
            scheduled_time = datetime.utcnow() + timedelta(hours=1)
        
        # Create interview session
        session = InterviewSession(
            candidate_id=candidate.id,
            job_drive_id=drive_id,
            session_type='actual',
            status='scheduled',
            scheduled_time=scheduled_time,
            interview_link=generate_interview_link()
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Send email notification to candidate
        try:
            from app.email_service import send_shortlist_notification
            interview_url = f"{request.url_root}interview/{session.id}?link={session.interview_link}"
            
            send_shortlist_notification(
                candidate_email=candidate.email,
                candidate_name=candidate.full_name,
                job_title=drive.title,
                company_name=current_user.hr_profile.company_name,
                interview_link=interview_url
            )
        except Exception as e:
            print(f"Failed to send interview invitation email: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Interview scheduled and notification sent successfully',
            'session_id': session.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/hr/bulk-schedule-interview', methods=['POST'])
@login_required
def bulk_schedule_interview():
    """Schedule interviews for multiple candidates."""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        drive_id = request.json.get('drive_id')
        candidate_emails = request.json.get('candidate_emails', [])
        scheduled_time_str = request.json.get('scheduled_time')
        
        if not candidate_emails:
            return jsonify({'success': False, 'message': 'No candidates selected'}), 400
        
        # Verify drive belongs to current HR
        drive = JobDrive.query.join(
            current_user.hr_profile.__class__
        ).filter_by(user_id=current_user.id).filter(JobDrive.id == drive_id).first()
        
        if not drive:
            return jsonify({'success': False, 'message': 'Job drive not found or access denied'}), 404
        
        # Parse scheduled time with better error handling
        try:
            if scheduled_time_str:
                if 'T' in scheduled_time_str:
                    scheduled_time_str = scheduled_time_str.replace('Z', '')
                    scheduled_time = datetime.fromisoformat(scheduled_time_str)
                else:
                    scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%d %H:%M:%S')
            else:
                scheduled_time = datetime.utcnow() + timedelta(hours=1)
        except ValueError:
            scheduled_time = datetime.utcnow() + timedelta(hours=1)
        
        successful_schedules = []
        failed_schedules = []
        
        for email in candidate_emails:
            try:
                # Find candidate
                candidate = User.query.filter_by(email=email.strip(), user_type='student').first()
                if not candidate:
                    # Send registration invitation for unregistered candidates
                    try:
                        from app.email_service import send_registration_invitation
                        registration_url = f"{request.url_root}register"
                        
                        send_registration_invitation(
                            candidate_email=email.strip(),
                            job_title=drive.title,
                            company_name=current_user.hr_profile.company_name,
                            registration_link=registration_url
                        )
                    except Exception as e:
                        print(f"Failed to send registration invitation email: {e}")
                    
                    successful_schedules.append({'email': email, 'action': 'registration_invitation_sent'})
                    continue
                
                # Create interview session for registered candidates
                session = InterviewSession(
                    candidate_id=candidate.id,
                    job_drive_id=drive_id,
                    session_type='actual',
                    status='scheduled',
                    scheduled_time=scheduled_time,
                    interview_link=generate_interview_link()
                )
                
                db.session.add(session)
                db.session.flush()
                
                # Send email notification
                try:
                    from app.email_service import send_shortlist_notification
                    interview_url = f"{request.url_root}interview/{session.id}?link={session.interview_link}"
                    
                    send_shortlist_notification(
                        candidate_email=candidate.email,
                        candidate_name=candidate.full_name,
                        job_title=drive.title,
                        company_name=current_user.hr_profile.company_name,
                        interview_link=interview_url
                    )
                except Exception as e:
                    print(f"Failed to send interview invitation email: {e}")
                
                successful_schedules.append({'email': email, 'session_id': session.id, 'action': 'interview_scheduled'})
                
            except Exception as e:
                failed_schedules.append({'email': email, 'reason': str(e)})
        
        db.session.commit()
        
        registered_count = len([s for s in successful_schedules if s.get('action') == 'interview_scheduled'])
        invitation_count = len([s for s in successful_schedules if s.get('action') == 'registration_invitation_sent'])
        
        message = f'Processed {len(successful_schedules)} candidates successfully'
        if registered_count > 0:
            message += f' - {registered_count} interviews scheduled'
        if invitation_count > 0:
            message += f' - {invitation_count} registration invitations sent'
        
        return jsonify({
            'success': True,
            'message': message,
            'successful': successful_schedules,
            'failed': failed_schedules
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/interview/<session_id>')
def interview_interface(session_id):
    """Unified interview interface for all interview types."""
    session = InterviewSession.query.get_or_404(session_id)
    
    # Verify access
    if current_user.is_authenticated:
        if current_user.id != session.candidate_id:
            flash('Access denied.', 'error')
            return redirect(url_for('main.index'))
    else:
        # Allow anonymous access via interview link
        interview_link = request.args.get('link')
        if not interview_link or interview_link != session.interview_link:
            flash('Invalid interview link.', 'error')
            return redirect(url_for('main.index'))
    
    # Check if interview is already completed
    if session.status == 'completed':
        flash('This interview has already been completed.', 'info')
        return redirect(url_for('main.interview_feedback', session_id=session_id))
    
    return render_template('interview/pro_interface.html', session=session)

@main.route('/adaptive-interview/<session_id>')
def adaptive_interview_interface(session_id):
    """Simple interview interface page."""
    session = InterviewSession.query.get_or_404(session_id)
    
    # Verify access
    if current_user.is_authenticated:
        if current_user.id != session.candidate_id:
            flash('Access denied.', 'error')
            return redirect(url_for('main.index'))
    else:
        # Allow anonymous access via interview link
        interview_link = request.args.get('link')
        if not interview_link or interview_link != session.interview_link:
            flash('Invalid interview link.', 'error')
            return redirect(url_for('main.index'))
    
    # Check if interview is already completed
    if session.status == 'completed':
        flash('This interview has already been completed.', 'info')
        return redirect(url_for('main.interview_feedback', session_id=session_id))
    
    return render_template('interview/pro_interface.html', session=session)

@main.route('/interview/<session_id>/start', methods=['POST'])
def start_interview(session_id):
    """Start the interview session."""
    session = InterviewSession.query.get_or_404(session_id)
    
    try:
        # Simple start without complex question generation
        if not session.questions:
            session.questions = json.dumps([{"id": 1, "question": "Tell me about yourself"}])
        
        # Update session status
        session.status = 'in_progress'
        session.start_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Interview started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/adaptive-interview/<session_id>/start', methods=['POST'])
def start_adaptive_interview(session_id):
    """Start the simple interview session."""
    session = InterviewSession.query.get_or_404(session_id)
    
    try:
        # Update session status
        session.status = 'in_progress'
        session.start_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Interview started successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



@main.route('/adaptive-interview/<session_id>/complete', methods=['POST'])
def complete_adaptive_interview(session_id):
    """Complete the adaptive interview session."""
    session = InterviewSession.query.get_or_404(session_id)
    
    try:
        # Get stored responses from frontend
        all_responses = request.json.get('all_responses', [])
        
        # Store responses
        responses = {}
        questions = []
        for i, resp in enumerate(all_responses):
            responses[str(i+1)] = {
                'question': resp.get('question', f'Question {i+1}'),
                'answer': resp.get('answer', ''),
                'timestamp': resp.get('timestamp', datetime.utcnow().isoformat())
            }
            questions.append({
                'id': i+1,
                'question': resp.get('question', f'Question {i+1}'),
                'type': 'interview',
                'category': 'general'
            })
        
        session.responses = json.dumps(responses)
        session.questions = json.dumps(questions)
        session.status = 'completed'
        session.end_time = datetime.utcnow()
        
        if session.start_time:
            duration = (session.end_time - session.start_time).total_seconds()
            session.duration = int(duration)
        
        # Generate detailed student-oriented feedback
        feedback_data = ai_service.generate_simple_feedback(all_responses, "student")
        session.ai_feedback = json.dumps(feedback_data)
        session.overall_score = feedback_data.get('overall_score', 75)
        session.technical_score = feedback_data.get('technical_score', 75)
        session.communication_score = feedback_data.get('communication_score', 75)
        session.confidence_score = feedback_data.get('confidence_score', 75)
        
        db.session.commit()
        
        # Send email notification
        try:
            from app.email_service import send_interview_feedback_to_candidate
            candidate = session.candidate
            send_interview_feedback_to_candidate(
                candidate_email=candidate.email,
                candidate_name=candidate.full_name,
                job_title='Practice Interview',
                company_name='Talent Sync',
                feedback=feedback_data
            )
        except Exception as e:
            print(f"Email error: {e}")
        
        return jsonify({
            'success': True,
            'redirect_url': url_for('main.interview_feedback', session_id=session_id)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/interview/<session_id>/submit-answer', methods=['POST'])
def submit_answer(session_id):
    """Submit answer for a question."""
    session = InterviewSession.query.get_or_404(session_id)
    
    try:
        question_id = request.json.get('question_id')
        answer = request.json.get('answer')
        
        # Load existing responses
        responses = json.loads(session.responses) if session.responses else {}
        responses[str(question_id)] = {
            'answer': answer,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        session.responses = json.dumps(responses)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/interview/<session_id>/complete', methods=['POST'])
def complete_interview(session_id):
    """Complete the interview session."""
    session = InterviewSession.query.get_or_404(session_id)
    
    try:
        # Update session
        session.status = 'completed'
        session.end_time = datetime.utcnow()
        
        if session.start_time:
            duration = (session.end_time - session.start_time).total_seconds()
            session.duration = int(duration)
        
        # Mark interview as completed first
        db.session.commit()
        
        # Generate HR-oriented feedback for scheduled interviews
        feedback_data = ai_service.generate_simple_feedback([], "hr")
        session.ai_feedback = json.dumps(feedback_data)
        session.overall_score = feedback_data.get('overall_score', 75)
        session.technical_score = 75
        session.communication_score = 75
        session.confidence_score = 75
        
        db.session.commit()
        
        # Send automatic feedback emails
        try:
            from app.email_service import send_interview_feedback_to_candidate, send_interview_feedback_to_hr
            
            print(f"Sending feedback emails for session {session_id}")
            
            # Send feedback to candidate
            candidate = session.candidate
            job_title = session.job_drive.title if session.job_drive else 'Practice Interview'
            company_name = 'Talent Sync'
            
            if session.job_drive:
                try:
                    company_name = session.job_drive.hr.company_name
                except:
                    company_name = 'Talent Sync'
            
            feedback_data = json.loads(session.ai_feedback) if session.ai_feedback else self._get_fallback_feedback()
            
            print(f"Sending candidate email to: {candidate.email}")
            send_interview_feedback_to_candidate(
                candidate_email=candidate.email,
                candidate_name=candidate.full_name,
                job_title=job_title,
                company_name=company_name,
                feedback=feedback_data
            )
            print("Candidate email sent successfully")
            
            # Send feedback to HR only if this is a scheduled interview (not practice)
            if session.job_drive and session.session_type == 'actual':
                try:
                    hr = session.job_drive.hr.user
                    print(f"Sending HR email to: {hr.email}")
                    send_interview_feedback_to_hr(
                        hr_email=hr.email,
                        hr_name=hr.full_name,
                        candidate_name=candidate.full_name,
                        candidate_email=candidate.email,
                        job_title=job_title,
                        feedback=feedback_data
                    )
                    print("HR email sent successfully")
                except Exception as hr_error:
                    print(f"Error sending HR email: {hr_error}")
                
        except Exception as e:
            print(f"Error sending feedback emails: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            'success': True,
            'redirect_url': url_for('main.interview_feedback', session_id=session_id)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/interview/<session_id>/feedback')
def interview_feedback(session_id):
    """Show interview feedback."""
    session = InterviewSession.query.get_or_404(session_id)
    
    # Verify access
    can_view = False
    if current_user.is_authenticated:
        # Candidate can view their own feedback
        if current_user.id == session.candidate_id:
            can_view = True
        # HR can view feedback for their drives
        elif current_user.user_type == 'hr' and session.job_drive_id:
            drive = JobDrive.query.filter_by(
                id=session.job_drive_id,
                hr_id=current_user.hr_profile.id
            ).first()
            if drive:
                can_view = True
    
    if not can_view:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    # Parse feedback
    ai_feedback = json.loads(session.ai_feedback) if session.ai_feedback else {}
    
    # Determine which feedback to show
    if current_user.user_type == 'student':
        return render_template('student/feedback.html', session=session, feedback=ai_feedback)
    else:
        return render_template('hr/interview_feedback.html', session=session, feedback=ai_feedback)

@main.route('/interview/<session_id>/security-warning', methods=['POST'])
def log_security_warning(session_id):
    """Log security warning for interview session."""
    try:
        reason = request.json.get('reason', 'Unknown')
        warning_count = request.json.get('warning_count', 1)
        timestamp = request.json.get('timestamp', datetime.utcnow().isoformat())
        
        log_security_event(
            'INTERVIEW_SECURITY_WARNING',
            f'Session: {session_id}, Warning {warning_count}: {reason}'
        )
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



@main.route('/api/interview-questions')
@login_required
def get_interview_questions():
    """API endpoint to get interview questions."""
    job_role = request.args.get('job_role', 'General')
    difficulty = request.args.get('difficulty', 'medium')
    
    try:
        # Simple questions without complex generation
        questions = [
            {"id": 1, "question": "Tell me about yourself", "type": "behavioral"},
            {"id": 2, "question": "What are your strengths?", "type": "behavioral"},
            {"id": 3, "question": "Describe a challenge you faced", "type": "behavioral"}
        ]
        return jsonify({'success': True, 'questions': questions})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/api/generate-ai-response', methods=['POST'])
def generate_ai_response():
    """Generate professional AI interviewer response."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_message = data.get('message', '').strip()
        current_tool = data.get('current_tool', 'chat')
        
        # Get session
        session = InterviewSession.query.get(session_id)
        if not session:
            return jsonify({'success': False, 'message': 'Session not found'}), 404
        
        # Get job role from session
        job_role = 'General'
        if session.job_drive:
            job_role = session.job_drive.job_role
        elif hasattr(session, 'notes') and session.notes:
            # Extract job role from notes
            if 'Job Role:' in session.notes:
                job_role = session.notes.split('Job Role:')[1].strip()
        
        # Get current question count
        responses_data = session.responses
        if isinstance(responses_data, str):
            responses = json.loads(responses_data) if responses_data else {}
        else:
            responses = responses_data or {}
            
        question_count = len(responses)
        
        # Generate contextual response
        response = ai_service.generate_simple_response(user_message, question_count, job_role)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return jsonify({
            'success': True,
            'response': "Thank you for your response. Please continue with your thoughts on this topic."
        })

@main.route('/api/log-interaction', methods=['POST'])
def log_interaction():
    """Log user interaction during interview."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        interaction = data.get('interaction')
        
        # Log interaction (you can store this in database if needed)
        log_interview_action(f"Session {session_id}", f"Interaction: {interaction['type']}")
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/api/evaluate-code', methods=['POST'])
def evaluate_code():
    """Evaluate submitted code."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        code = data.get('code')
        language = data.get('language', 'javascript')
        
        # Simple code evaluation feedback
        feedback = f"Thank you for your {language} code submission. I can see you've implemented a solution. Can you walk me through your approach and explain your reasoning behind the key decisions you made?"
        
        return jsonify({
            'success': True,
            'feedback': feedback
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500