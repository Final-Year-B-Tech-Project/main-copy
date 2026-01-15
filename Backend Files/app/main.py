import json
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, JobDrive, InterviewSession
import json
from app.ai_service_simple import SimpleAIService
from app.utils import generate_interview_link
from app.logger import log_user_action, log_interview_action, log_security_event
from app.professional_interviewer import ProfessionalInterviewer

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
        return redirect(url_for('hr.dashboard'))
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
    
    return render_template('student/perfect_dashboard.html',
                         recent_interviews=recent_interviews,
                         practice_count=practice_count,
                         avg_score=avg_score)

# Removed - now handled by HR blueprint

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

@main.route('/student/check-resume')
@login_required
def check_resume():
    """Check if student has uploaded resume"""
    if current_user.user_type != 'student':
        return jsonify({'has_resume': False})
    
    has_resume = False
    if current_user.student_profile and current_user.student_profile.resume_file:
        has_resume = True
    
    return jsonify({'has_resume': has_resume})

@main.route('/student/upload-resume', methods=['POST'])
@login_required
def upload_resume():
    """Upload and parse resume"""
    if current_user.user_type != 'student':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'success': False, 'message': 'Only PDF files allowed'}), 400
        
        # Save file
        import os
        from werkzeug.utils import secure_filename
        
        filename = secure_filename(f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        upload_folder = os.path.join('static', 'uploads', 'resumes')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Parse resume
        from app.resume_parser import ResumeParser
        parsed = ResumeParser.parse_resume(filepath)
        
        if not parsed:
            return jsonify({'success': False, 'message': 'Failed to parse resume'}), 500
        
        # Update student profile
        if not current_user.student_profile:
            from app.models import StudentProfile
            profile = StudentProfile(user_id=current_user.id)
            db.session.add(profile)
            db.session.flush()
        
        current_user.student_profile.resume_file = filename
        current_user.student_profile.resume_text = parsed['text']
        current_user.student_profile.skills = json.dumps(parsed['skills'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Resume uploaded successfully',
            'skills': parsed['skills'],
            'experience_years': parsed['experience_years']
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Resume upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/student/start-practice', methods=['POST'])
@login_required
def start_practice():
    """Start a practice interview session."""
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
        
        # Send interview start notification immediately
        try:
            from app.email_templates_fixed import get_interview_start_template
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            import os
            
            # Get job role
            job_role = request.json.get('job_role', 'General')
            
            # Send start notification
            interview_link = f"{request.url_root}adaptive-interview/{session.id}"
            html_body = get_interview_start_template(
                current_user.full_name,
                job_role,
                interview_link
            )
            
            # Email configuration
            smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('MAIL_PORT', 587))
            sender_email = os.getenv('MAIL_USERNAME')
            sender_password = os.getenv('MAIL_PASSWORD')
            
            if sender_email and sender_password:
                print(f"Sending start notification to {current_user.email}...")
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = current_user.email
                msg['Subject'] = f"Interview Starting - {job_role} | TalentSync"
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
                
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, current_user.email, msg.as_string())
                server.quit()
                print(f"✓ Start notification sent to {current_user.email}")
            else:
                print("✗ Email credentials not configured")
                
        except Exception as e:
            print(f"✗ Failed to send start notification: {e}")
            import traceback
            traceback.print_exc()
        
        # Start with predefined first question for instant start
        first_question = "Tell me about yourself and your background."
        session.questions = json.dumps([first_question])
        session.responses = json.dumps({})
        
        # Store job role for adaptive questions later
        session.notes = f"Job Role: {job_role}"
        
        db.session.commit()
        
        log_user_action('PRACTICE_INTERVIEW_STARTED', f'Session ID: {session.id}, Job Role: {job_role}')
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'interview_link': session.interview_link,
            'redirect_url': url_for('main.adaptive_interview_interface', session_id=session.id)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Removed - now handled by HR blueprint

# Removed - now handled by HR blueprint

# Removed - now handled by HR blueprint

@main.route('/hr/drive/<int:drive_id>/toggle', methods=['POST'])
@login_required
def toggle_drive(drive_id):
    """Toggle job drive active status."""
    if current_user.user_type != 'hr':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Verify drive belongs to current HR
        if current_user.hr_profile:
            drive = JobDrive.query.filter_by(id=drive_id, hr_id=current_user.hr_profile.id).first()
        else:
            drive = None
        
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
        if current_user.hr_profile:
            drive = JobDrive.query.filter_by(id=drive_id, hr_id=current_user.hr_profile.id).first()
        else:
            drive = None
        
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
        if current_user.hr_profile:
            drive = JobDrive.query.filter_by(id=drive_id, hr_id=current_user.hr_profile.id).first()
        else:
            drive = None
        
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
    
    return render_template('interview/fullscreen_interview.html', session=session)

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
        
        # Send interview start notification
        try:
            from app.email_templates_fixed import get_interview_start_template
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from flask import current_app
            
            # Get job role
            job_role = "General"
            if session.notes and "Job Role: " in session.notes:
                job_role = session.notes.split("Job Role: ")[1].split("\n")[0]
            
            # Send start notification
            interview_link = f"{request.url_root}adaptive-interview/{session_id}"
            html_body = get_interview_start_template(
                session.candidate.full_name,
                job_role,
                interview_link
            )
            
            # Import os for environment variables
            import os
            
            # Send email directly
            smtp_server = current_app.config.get('MAIL_SERVER') or os.getenv('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT') or int(os.getenv('MAIL_PORT', 587))
            sender_email = current_app.config.get('MAIL_USERNAME') or os.getenv('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD') or os.getenv('MAIL_PASSWORD')
            
            print(f"Email config - Server: {smtp_server}, Username: {sender_email}, Password: {'***' if sender_password else 'None'}")
            
            if sender_email and sender_password:
                print(f"Sending start notification to {session.candidate.email}...")
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = session.candidate.email
                msg['Subject'] = f"Interview Starting - {job_role} | TalentSync"
                
                # Encode HTML body safely
                html_body_safe = html_body.encode('utf-8', errors='ignore').decode('utf-8')
                msg.attach(MIMEText(html_body_safe, 'html', 'utf-8'))
                
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, session.candidate.email, msg.as_string())
                server.quit()
                print(f"✓ Start notification sent to {session.candidate.email}")
            else:
                print(f"✗ Email credentials missing - Username: {sender_email}, Password: {'***' if sender_password else 'None'}")
                print("Please check .env file for MAIL_USERNAME and MAIL_PASSWORD")
            
        except Exception as e:
            print(f"✗ Failed to send start notification: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            'success': True, 
            'message': 'Interview started successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



@main.route('/adaptive-interview/<session_id>/complete', methods=['POST'])
def complete_adaptive_interview(session_id):
    """Complete the adaptive interview session with enhanced evaluation."""
    session = InterviewSession.query.get_or_404(session_id)
    
    try:
        # Get stored responses from frontend
        all_responses = request.json.get('all_responses', [])
        security_data = request.json.get('security_data', {})
        
        # Get job role from session
        job_role = "General"
        if session.notes:
            try:
                job_role = session.notes.split("Job Role: ")[1] if "Job Role: " in session.notes else "General"
            except:
                job_role = "General"
        
        # Only generate feedback if there are actual responses
        if len(all_responses) == 0:
            return jsonify({
                'success': False,
                'message': 'No responses recorded. Please speak or type your answers during the interview.'
            }), 400
        
        # Send all responses to professional feedback system with security data
        from app.professional_feedback import generate_professional_feedback
        evaluation_result = generate_professional_feedback(ai_service, all_responses, job_role, security_data)
        
        print(f"Generated feedback for {len(all_responses)} responses with score: {evaluation_result.get('overall_score', 0)}")
        
        # Debug: Print evaluation result
        print(f"Evaluation result keys: {evaluation_result.keys()}")
        print(f"Technical score: {evaluation_result.get('technical_score', 0)}")
        print(f"Communication score: {evaluation_result.get('communication_score', 0)}")
        
        # Update session with results
        session.status = 'completed'
        session.end_time = datetime.utcnow()
        
        if session.start_time:
            duration = int((session.end_time - session.start_time).total_seconds())
            session.duration = duration
        
        # Store realistic scores
        session.overall_score = evaluation_result['overall_score']
        session.technical_score = evaluation_result['technical_score']
        session.communication_score = evaluation_result['communication_score']
        session.confidence_score = evaluation_result['confidence_score']
        
        # Store responses and questions with enhanced data
        responses = {}
        questions = []
        
        for i, resp in enumerate(all_responses):
            responses[str(i+1)] = {
                'question': resp.get('question', f'Question {i+1}'),
                'answer': resp.get('answer', ''),
                'timestamp': resp.get('timestamp', datetime.utcnow().isoformat()),
                'response_time': resp.get('response_time', 120),
                'word_count': len(resp.get('answer', '').split())
            }
            questions.append({
                'id': i+1,
                'question': resp.get('question', f'Question {i+1}'),
                'type': 'professional',
                'phase': 'adaptive'
            })
        
        session.responses = json.dumps(responses)
        session.questions = json.dumps(questions)
        session.ai_feedback = json.dumps(evaluation_result)
        
        # Store additional metadata
        session.notes = f"Job Role: {job_role}\nTotal Questions: {len(all_responses)}\nInterview Type: Professional"
        
        db.session.commit()
        print(f"Interview completed successfully with {len(all_responses)} responses for {job_role} role")
        
        # Send comprehensive email notifications and PDF
        try:
            from app.interview_completion import InterviewCompletionService
            completion_service = InterviewCompletionService()
            
            # Generate PDF report
            pdf_path, pdf_filename = completion_service.generate_feedback_pdf(
                session, evaluation_result, all_responses
            )
            
            # Send email to candidate
            completion_service.send_candidate_email(
                candidate_email=session.candidate.email,
                candidate_name=session.candidate.full_name,
                job_role=job_role,
                feedback_data=evaluation_result,
                pdf_path=pdf_path
            )
            
            # Send email to HR if this is a scheduled interview
            if session.job_drive and session.session_type == 'actual':
                hr = session.job_drive.hr.user
                completion_service.send_hr_email(
                    hr_email=hr.email,
                    hr_name=hr.full_name,
                    candidate_name=session.candidate.full_name,
                    candidate_email=session.candidate.email,
                    job_role=job_role,
                    feedback_data=evaluation_result
                )
            
            print(f"Interview completed with email notifications sent for {session.candidate.full_name}")
            
        except Exception as e:
            print(f"Email/PDF error: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            'success': True,
            'message': f'Interview completed successfully! Feedback generated for {len(all_responses)} responses.',
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
    
    # Parse feedback and responses
    ai_feedback = json.loads(session.ai_feedback) if session.ai_feedback else {}
    
    # Parse responses for template
    responses_data = {}
    if session.responses:
        try:
            responses_data = json.loads(session.responses) if isinstance(session.responses, str) else session.responses
        except:
            responses_data = {}
    
    # Determine which feedback to show
    if current_user.user_type == 'student':
        return render_template('student/feedback.html', session=session, feedback=ai_feedback, responses=responses_data)
    else:
        return render_template('hr/interview_feedback.html', session=session, feedback=ai_feedback, responses=responses_data)

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
    """Generate adaptive AI response with professional opening and 20-minute timer."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_message = data.get('message', '').strip()
        
        # Get session
        session = InterviewSession.query.get(session_id)
        if not session:
            return jsonify({
                'success': True,
                'response': "Could you tell me about yourself?"
            })
        
        # Load resume data for context ONCE per session
        if not hasattr(ai_service, 'resume_loaded') or not ai_service.resume_loaded:
            if session.candidate.student_profile and session.candidate.student_profile.resume_text:
                from app.resume_parser import ResumeParser
                resume_text = session.candidate.student_profile.resume_text
                skills_json = session.candidate.student_profile.skills
                
                # Parse skills if stored as JSON
                import json
                skills = json.loads(skills_json) if skills_json else []
                
                # Set resume data in AI service
                ai_service.resume_data = {
                    'skills': skills,
                    'experience_years': ResumeParser.extract_experience_years(resume_text),
                    'text': resume_text[:500]  # First 500 chars
                }
                ai_service.resume_loaded = True
                print(f"[OK] Resume loaded: {len(skills)} skills, {ai_service.resume_data['experience_years']} years exp")
        
        # Get job role from session notes with safe handling
        job_role = "General"
        try:
            if hasattr(session, 'notes') and session.notes and "Job Role: " in str(session.notes):
                job_role = str(session.notes).split("Job Role: ")[1].split("\n")[0].strip()
        except Exception as e:
            print(f"Job role extraction error: {e}")
            job_role = "General"
        
        # Get current question count
        try:
            responses_data = session.responses
            if isinstance(responses_data, str):
                responses = json.loads(responses_data) if responses_data else {}
            else:
                responses = responses_data or {}
        except:
            responses = {}
        
        question_count = len(responses)
        
        # Calculate time elapsed
        total_time = 0
        if session.start_time:
            total_time = int((datetime.utcnow() - session.start_time).total_seconds())
        
        # Check for 20-minute limit (1200 seconds)
        if total_time >= 1200:
            return jsonify({
                'success': True,
                'response': "Thank you for completing the 20-minute interview! Please click 'End Interview' to see your feedback.",
                'should_end': True,
                'time_up': True
            })
        
        # Handle first interaction - Skip opening, go to first question
        if question_count == 0 and not user_message:
            # First question directly
            first_question = f"Tell me about yourself and your background in {job_role}."
            
            # Set start time
            if session.start_time is None:
                session.start_time = datetime.utcnow()
                try:
                    db.session.commit()
                except:
                    pass
            
            return jsonify({
                'success': True,
                'response': first_question,
                'question_index': 1,
                'is_first_question': True
            })
        
        # Process the response
        if user_message and len(user_message.strip()) > 1:
            # Store the response with correct indexing
            response_key = str(question_count)
            responses[response_key] = {
                'question_index': question_count,
                'answer': user_message,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            try:
                session.responses = json.dumps(responses)
            except:
                pass
            
            # Use actual response count for continuation check
            current_question_count = len(responses)
            print(f"Current question count: {current_question_count}, Total time: {total_time}")
            
            # Check if should continue - minimum 6 questions, maximum 20 minutes
            elapsed_seconds = total_time
            remaining_time = max(0, 1200 - elapsed_seconds)
            
            # End conditions: ONLY 20 minutes time limit
            if elapsed_seconds >= 1200:
                return jsonify({
                    'success': True,
                    'response': "Thank you for completing the 20-minute interview! Please click 'End Interview' to see your feedback.",
                    'should_end': True,
                    'time_up': True
                })
            elif remaining_time <= 60 and current_question_count >= 5:  # Last minute warning
                return jsonify({
                    'success': True,
                    'response': "We have about one minute remaining. Do you have any final questions?",
                    'should_end': False,
                    'final_minute': True
                })
            
            # Generate next question using AI - PRIORITIZE LLM
            try:
                # Build conversation history for context
                conversation_history = []
                for i, resp in enumerate(responses.values()):
                    if isinstance(resp, dict) and 'answer' in resp:
                        conversation_history.append((
                            f"Question {i+1}",
                            resp['answer']
                        ))
                
                # Use AI service to generate contextual question
                next_question = ai_service.generate_adaptive_question(
                    user_message, job_role, current_question_count, conversation_history
                )
                
                # Validate question quality
                if not next_question or len(next_question.strip()) < 10:
                    raise Exception("Generated question too short")
                
                print(f"AI Generated question: {next_question}")
                
            except Exception as e:
                print(f"AI question generation failed: {e}")
                # Smart fallback based on interview progress
                if current_question_count < 3:
                    next_question = f"Tell me about a challenging {job_role} project you've worked on."
                elif current_question_count < 6:
                    next_question = "How do you approach learning new technologies or skills?"
                else:
                    next_question = "What are your career goals and how does this position fit into them?"
            
            # Store question
            try:
                questions_data = session.questions
                if isinstance(questions_data, str):
                    questions = json.loads(questions_data) if questions_data else []
                else:
                    questions = questions_data or []
                
                questions.append({
                    'id': len(questions) + 1,
                    'question': next_question,
                    'type': 'adaptive',
                    'generated_by': 'ai'
                })
                session.questions = json.dumps(questions)
            except:
                pass
            
            try:
                db.session.commit()
            except:
                pass
            
            return jsonify({
                'success': True,
                'response': next_question,
                'question_index': current_question_count + 1,
                'remaining_time': remaining_time
            })
        else:
            # First question after opening or no meaningful response
            if question_count == 0:
                first_question = f"Let's start with you telling me about yourself and your background in {job_role}."
                
                return jsonify({
                    'success': True,
                    'response': first_question,
                    'question_index': 1
                })
            else:
                # Ask for more detail
                return jsonify({
                    'success': True,
                    'response': "Could you please provide a bit more detail in your response?",
                    'question_index': question_count
                })
        
    except Exception as e:
        print(f"Error in AI response generation: {e}")
        # Always return a valid response
        return jsonify({
            'success': True,
            'response': "Could you tell me more about yourself and your background?"
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

@main.route('/api/detect-faces', methods=['POST'])
def detect_faces():
    """Detect faces in image using DeepSeek vision model."""
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        import requests
        import os
        
        # Use OpenRouter with DeepSeek vision model
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:5000',
                'X-Title': 'TalentSync Interview'
            },
            json={
                'model': 'google/gemini-2.0-flash-exp:free',
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'image_url',
                                'image_url': {'url': image_data}
                            },
                            {
                                'type': 'text',
                                'text': 'Count the number of human faces visible in this image. Respond with ONLY a single number (0, 1, 2, etc). No other text or explanation.'
                            }
                        ]
                    }
                ]
            },
            timeout=10
        )
        
        result = response.json()
        print(f"Face detection API response: {result}")
        
        if 'choices' in result and len(result['choices']) > 0:
            face_count_str = result['choices'][0]['message']['content'].strip()
            
            # Extract number from response
            import re
            numbers = re.findall(r'\d+', face_count_str)
            face_count = int(numbers[0]) if numbers else 1
        else:
            print(f"API error: {result.get('error', 'Unknown error')}")
            face_count = 1
        
        return jsonify({
            'success': True,
            'face_count': face_count
        })
        
    except Exception as e:
        print(f"Face detection error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': True, 'face_count': 1})  # Default to 1 on error

