import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask import current_app, render_template
from flask_mail import Mail, Message
from datetime import datetime
import ssl
from app.pdf_generator import generate_interview_pdf

def send_email_safely(to_email, subject, html_body, attachments=None):
    """Safely send email with proper error handling and SSL configuration.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of email
        attachments: List of tuples (filename, file_data) for attachments
    """
    try:
        mail_username = os.environ.get('MAIL_USERNAME')
        mail_password = os.environ.get('MAIL_PASSWORD')
        
        if not mail_username or not mail_password:
            print("Email credentials not configured")
            return False
        
        # Remove ALL non-ASCII characters to prevent encoding errors
        import re
        # Remove emojis and special Unicode characters
        html_body = html_body.encode('ascii', 'ignore').decode('ascii')
        
        # Create message
        msg = MIMEMultipart('mixed')
        msg['From'] = mail_username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add HTML content with ASCII-safe encoding
        html_part = MIMEText(html_body, 'html', 'ascii')
        msg.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for filename, file_data in attachments:
                attachment = MIMEApplication(file_data, _subtype='pdf')
                attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(attachment)
        
        # Gmail SMTP configuration with proper SSL handling
        context = ssl.create_default_context()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(mail_username, mail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(mail_username, to_email, text)
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

def send_admin_notification_email(recipient_email, recipient_name, action, details):
    """Send admin action notification emails to affected users."""
    try:
        # Email templates for different actions
        action_templates = {
            'account_suspended': {
                'subject': 'Account Suspended - TalentSync',
                'template': 'emails/admin_notifications/account_suspended.html'
            },
            'account_reactivated': {
                'subject': 'Account Reactivated - TalentSync',
                'template': 'emails/admin_notifications/account_reactivated.html'
            },
            'data_exported': {
                'subject': 'Data Export Complete - TalentSync',
                'template': 'emails/admin_notifications/data_exported.html'
            }
        }
        
        action_config = action_templates.get(action, {
            'subject': f'Account Update - {action}',
            'template': 'emails/admin_notifications/generic_admin_action.html'
        })
        
        subject = action_config['subject']
        
        # Render HTML template
        html_body = render_template(action_config['template'],
                                  recipient_name=recipient_name,
                                  action=action,
                                  details=details,
                                  current_year=datetime.now().year)
        
        return send_email_safely(recipient_email, subject, html_body)
        
    except Exception as e:
        print(f"Failed to send admin notification email: {e}")
        return False

def send_shortlist_notification(candidate_email, candidate_name, job_title, company_name, interview_link):
    """Send interview invitation email to shortlisted candidates."""
    try:
        subject = f"Interview Invitation - {job_title} at {company_name}"
        
        # Render HTML template
        html_body = render_template('emails/interview_invitation.html',
                                  candidate_name=candidate_name,
                                  job_title=job_title,
                                  company_name=company_name,
                                  interview_link=interview_link,
                                  current_year=datetime.now().year)
        
        return send_email_safely(candidate_email, subject, html_body)
        
    except Exception as e:
        print(f"Failed to send shortlist notification: {e}")
        return False

def send_registration_invitation(candidate_email, job_title, company_name, registration_link):
    """Send registration invitation to unregistered candidates."""
    try:
        subject = f"Welcome to TalentSync - {job_title} at {company_name}"
        
        # Render HTML template
        html_body = render_template('emails/registration_invitation.html',
                                  job_title=job_title,
                                  company_name=company_name,
                                  registration_link=registration_link,
                                  current_year=datetime.now().year)
        
        return send_email_safely(candidate_email, subject, html_body)
        
    except Exception as e:
        print(f"Failed to send registration invitation: {e}")
        return False

def send_interview_feedback_to_candidate(candidate_email, candidate_name, job_title, company_name, feedback):
    """Send interview feedback email to candidate with improvement focus and PDF attachment."""
    try:
        subject = f"Your Interview Results - {job_title}"
        
        # Extract and enhance feedback data
        overall_score = feedback.get('overall_score', 0)
        technical_score = feedback.get('technical_score', 0)
        communication_score = feedback.get('communication_score', 0)
        confidence_score = feedback.get('confidence_score', 0)
        problem_solving_score = feedback.get('problem_solving_score', 0)
        
        # Ensure we have proper feedback data
        strengths = feedback.get('strengths', [
            "Good communication skills",
            "Professional demeanor",
            "Willingness to learn and improve"
        ])
        
        weaknesses = feedback.get('weaknesses', [
            "Continue practicing technical concepts",
            "Work on providing more specific examples",
            "Build confidence in presenting ideas"
        ])
        
        summary = feedback.get('summary', 
            f"Overall performance score of {overall_score}/100. The candidate demonstrated good participation in the interview process with room for improvement in specific areas.")
        
        recommendations = feedback.get('recommendations', [
            "Practice articulating thoughts clearly and concisely",
            "Prepare specific examples that demonstrate skills and experience",
            "Research the company and role thoroughly before interviews",
            "Practice common interview questions in your field",
            "Maintain confidence and enthusiasm throughout the process"
        ])
        
        # Render HTML template
        html_body = render_template('emails/interview_feedback.html',
                                  candidate_name=candidate_name,
                                  job_title=job_title,
                                  company_name=company_name,
                                  overall_score=overall_score,
                                  technical_score=technical_score,
                                  communication_score=communication_score,
                                  confidence_score=confidence_score,
                                  problem_solving_score=problem_solving_score,
                                  strengths=strengths,
                                  weaknesses=weaknesses,
                                  summary=summary,
                                  recommendations=recommendations,
                                  next_steps="Continue practicing and improving your interview skills. Consider taking additional practice interviews to build confidence.",
                                  dashboard_link='#',
                                  current_year=datetime.now().year)
        
        # Generate PDF report
        try:
            candidate_data = {
                'name': candidate_name,
                'email': candidate_email,
                'job_title': job_title,
                'company_name': company_name
            }
            
            feedback_data = {
                'overall_score': overall_score,
                'technical_score': technical_score,
                'communication_score': communication_score,
                'confidence_score': confidence_score,
                'problem_solving_score': problem_solving_score,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'summary': summary,
                'recommendations': recommendations
            }
            
            pdf_buffer = generate_interview_pdf(candidate_data, feedback_data)
            pdf_data = pdf_buffer.read()
            
            # Create filename
            safe_name = candidate_name.replace(' ', '_')
            filename = f"Interview_Report_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            attachments = [(filename, pdf_data)]
            
            return send_email_safely(candidate_email, subject, html_body, attachments)
        except Exception as pdf_error:
            print(f"Failed to generate PDF: {pdf_error}")
            # Send email without PDF if generation fails
            return send_email_safely(candidate_email, subject, html_body)
        
    except Exception as e:
        print(f"Failed to send candidate feedback: {e}")
        return False

def send_interview_feedback_to_hr(hr_email, hr_name, candidate_name, candidate_email, job_title, feedback):
    """Send interview feedback email to HR with hiring decision focus."""
    try:
        subject = f"Interview Assessment Complete - {candidate_name}"
        
        # Extract and enhance feedback data
        overall_score = feedback.get('overall_score', 0)
        technical_score = feedback.get('technical_score', 0)
        communication_score = feedback.get('communication_score', 0)
        confidence_score = feedback.get('confidence_score', 0)
        problem_solving_score = feedback.get('problem_solving_score', 0)
        
        # Determine recommendation based on score
        if overall_score >= 80:
            recommendation = "Strongly Recommend - Excellent Candidate"
        elif overall_score >= 65:
            recommendation = "Consider - Good Candidate"
        elif overall_score >= 50:
            recommendation = "Consider with Reservations - Average Candidate"
        else:
            recommendation = "Not Recommended - Below Expectations"
        
        # Ensure we have proper feedback data
        strengths = feedback.get('strengths', [
            "Demonstrated good communication skills",
            "Showed professional demeanor",
            "Participated actively in the interview"
        ])
        
        weaknesses = feedback.get('weaknesses', [
            "Technical knowledge could be stronger",
            "Limited specific examples provided",
            "Confidence level could be improved"
        ])
        
        summary = feedback.get('summary', 
            f"Candidate {candidate_name} achieved an overall score of {overall_score}/100. The interview revealed both strengths and areas for development. Technical skills scored {technical_score}/100, communication {communication_score}/100, and confidence {confidence_score}/100.")
        
        security_note = feedback.get('security_note', '')
        
        # Render HTML template
        html_body = render_template('emails/hr_interview_feedback.html',
                                  hr_name=hr_name,
                                  candidate_name=candidate_name,
                                  candidate_email=candidate_email,
                                  job_title=job_title,
                                  interview_date=datetime.now().strftime('%B %d, %Y'),
                                  duration='30-45 minutes',
                                  overall_score=overall_score,
                                  technical_score=technical_score,
                                  communication_score=communication_score,
                                  confidence_score=confidence_score,
                                  problem_solving_score=problem_solving_score,
                                  recommendation=recommendation,
                                  strengths=strengths,
                                  weaknesses=weaknesses,
                                  summary=summary,
                                  security_note=security_note,
                                  dashboard_link='#',
                                  current_year=datetime.now().year)
        
        return send_email_safely(hr_email, subject, html_body)
        
    except Exception as e:
        print(f"Failed to send HR feedback: {e}")
        return False

def send_profile_update_notification(user_email, user_name):
    """Send profile update confirmation email."""
    try:
        subject = "Profile Updated Successfully - TalentSync"
        
        # Render HTML template
        html_body = render_template('emails/profile_update_notification.html',
                                  user_name=user_name,
                                  current_year=datetime.now().year)
        
        return send_email_safely(user_email, subject, html_body)
        
    except Exception as e:
        print(f"Failed to send profile update notification: {e}")
        return False

def send_job_drive_notification(hr_email, hr_name, job_title, action):
    """Send job drive action notifications."""
    try:
        subject = f"Job Drive {action.title()} - {job_title}"
        
        # Render HTML template
        html_body = render_template('emails/job_drive_notification.html',
                                  hr_name=hr_name,
                                  job_title=job_title,
                                  action=action,
                                  current_year=datetime.now().year)
        
        return send_email_safely(hr_email, subject, html_body)
        
    except Exception as e:
        print(f"Failed to send job drive notification: {e}")
        return False

def send_practice_interview_notification(user_email, user_name, job_role):
    """Send practice interview start notification."""
    try:
        subject = f"Practice Interview Started - {job_role}"
        
        # Render HTML template
        html_body = render_template('emails/practice_interview_started.html',
                                  user_name=user_name,
                                  job_role=job_role,
                                  start_time=datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                                  interview_link='#',
                                  current_year=datetime.now().year)
        
        return send_email_safely(user_email, subject, html_body)
        
    except Exception as e:
        print(f"Failed to send practice interview notification: {e}")
        return False

def send_welcome_email(user_email, user_name, user_type):
    """Send welcome email to new users."""
    try:
        subject = f"Welcome to TalentSync - {user_name}!"
        
        # Render HTML template
        html_body = render_template('emails/welcome_email.html',
                                  user_name=user_name,
                                  user_type=user_type,
                                  current_year=datetime.now().year)
        
        return send_email_safely(user_email, subject, html_body)
        
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        return False

def send_password_reset_email(user_email, user_name, reset_link):
    """Send password reset email."""
    try:
        subject = "Password Reset Request - TalentSync"
        
        # Render HTML template
        html_body = render_template('emails/password_reset.html',
                                  user_name=user_name,
                                  reset_link=reset_link,
                                  current_year=datetime.now().year)
        
        return send_email_safely(user_email, subject, html_body)
        
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
        return False