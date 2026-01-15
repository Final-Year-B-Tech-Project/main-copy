import json
from datetime import datetime
from flask import current_app
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class InterviewCompletionService:
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    def generate_feedback_pdf(self, session, feedback_data, transcript_data):
        """Generate comprehensive PDF report"""
        try:
            # Create PDF file path
            pdf_filename = f"interview_feedback_{session.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), pdf_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            story = []
            
            # Header with branding
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=28,
                spaceAfter=10,
                textColor=colors.HexColor('#3b82f6'),
                alignment=1,
                fontName='Helvetica-Bold'
            )
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=self.styles['Normal'],
                fontSize=14,
                spaceAfter=30,
                textColor=colors.HexColor('#64748b'),
                alignment=1
            )
            
            story.append(Paragraph("🚀 TalentSync Pro", title_style))
            story.append(Paragraph("AI-Powered Interview Assessment Report", subtitle_style))
            story.append(Spacer(1, 20))
            
            # Candidate Info
            info_data = [
                ['Candidate Name:', session.candidate.full_name],
                ['Email:', session.candidate.email],
                ['Interview Date:', session.created_at.strftime('%B %d, %Y')],
                ['Duration:', f"{session.duration // 60}m {session.duration % 60}s" if session.duration else "N/A"],
                ['Position:', session.notes.split('Job Role: ')[1] if 'Job Role: ' in str(session.notes) else 'General']
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Overall Score
            story.append(Paragraph("Overall Performance", self.styles['Heading2']))
            score = feedback_data.get('overall_score', 70)
            story.append(Paragraph(f"<b>Overall Score: {score}%</b>", self.styles['Normal']))
            story.append(Spacer(1, 15))
            
            # Detailed Scores
            scores_data = [
                ['Technical Skills', f"{feedback_data.get('technical_score', 65)}%"],
                ['Communication', f"{feedback_data.get('communication_score', 75)}%"],
                ['Confidence', f"{feedback_data.get('confidence_score', 70)}%"],
                ['Problem Solving', f"{feedback_data.get('problem_solving_score', 68)}%"]
            ]
            
            scores_table = Table(scores_data, colWidths=[3*inch, 1.5*inch])
            scores_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(scores_table)
            story.append(Spacer(1, 20))
            
            # Strengths
            story.append(Paragraph("Key Strengths", self.styles['Heading2']))
            for strength in feedback_data.get('strengths', ['Completed interview', 'Engaged throughout']):
                story.append(Paragraph(f"• {strength}", self.styles['Normal']))
            story.append(Spacer(1, 15))
            
            # Areas for Improvement
            story.append(Paragraph("Areas for Improvement", self.styles['Heading2']))
            for weakness in feedback_data.get('weaknesses', ['Provide more detail', 'Include examples']):
                story.append(Paragraph(f"• {weakness}", self.styles['Normal']))
            story.append(Spacer(1, 15))
            
            # Recommendations
            story.append(Paragraph("Recommendations", self.styles['Heading2']))
            for rec in feedback_data.get('recommendations', ['Practice STAR method', 'Prepare specific examples']):
                story.append(Paragraph(f"• {rec}", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Summary
            story.append(Paragraph("Summary", self.styles['Heading2']))
            summary = feedback_data.get('summary', 'Interview completed successfully with areas for improvement identified.')
            story.append(Paragraph(summary, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            return pdf_path, pdf_filename
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None, None
    
    def send_candidate_email(self, candidate_email, candidate_name, job_role, feedback_data, pdf_path=None):
        """Send feedback email to candidate"""
        try:
            # Email configuration
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            sender_email = current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                print("Email configuration missing")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = candidate_email
            msg['Subject'] = f"Interview Feedback - {job_role} Position"
            
            # Use attractive HTML template
            from app.email_templates_fixed import get_feedback_template
            html_body = get_feedback_template(candidate_name, job_role, feedback_data)
            
            # Encode safely
            html_body_safe = html_body.encode('utf-8', errors='ignore').decode('utf-8')
            msg.attach(MIMEText(html_body_safe, 'html', 'utf-8'))
            
            # Attach PDF if available
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= interview_feedback.pdf'
                )
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, candidate_email, text)
            server.quit()
            
            print(f"Candidate email sent successfully to {candidate_email}")
            return True
            
        except Exception as e:
            print(f"Error sending candidate email: {e}")
            return False
    
    def send_hr_email(self, hr_email, hr_name, candidate_name, candidate_email, job_role, feedback_data):
        """Send notification email to HR"""
        try:
            # Email configuration
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            sender_email = current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                print("Email configuration missing")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = hr_email
            msg['Subject'] = f"Interview Completed - {candidate_name} ({job_role})"
            
            # Use attractive HTML template
            from app.email_templates_fixed import get_hr_notification_template
            html_body = get_hr_notification_template(hr_name, candidate_name, candidate_email, job_role, feedback_data)
            
            # Encode safely
            html_body_safe = html_body.encode('utf-8', errors='ignore').decode('utf-8')
            msg.attach(MIMEText(html_body_safe, 'html', 'utf-8'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, hr_email, text)
            server.quit()
            
            print(f"HR email sent successfully to {hr_email}")
            return True
            
        except Exception as e:
            print(f"Error sending HR email: {e}")
            return False
    
    def send_start_notification(self, candidate_email, candidate_name, job_role, html_body):
        """Send interview start notification"""
        try:
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            sender_email = current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                print("Email configuration missing")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = candidate_email
            msg['Subject'] = f"Interview Starting - {job_role} Position | TalentSync"
            
            msg.attach(MIMEText(html_body, 'html'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, candidate_email, text)
            server.quit()
            
            print(f"Start notification sent to {candidate_email}")
            return True
            
        except Exception as e:
            print(f"Error sending start notification: {e}")
            return False