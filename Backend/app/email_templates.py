"""
Attractive HTML email templates for TalentSync
"""

def get_interview_start_template(candidate_name, job_role, interview_link):
    """HTML template for interview start notification"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview Starting - TalentSync</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; color: #1e293b;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #3b82f6, #06b6d4); padding: 30px; text-align: center;">
            <div style="background: #ffffff; width: 60px; height: 60px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #3b82f6;">TS</div>
            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">TalentSync Pro</h1>
            <p style="margin: 10px 0 0; color: #e0f2fe; font-size: 16px;">Your Interview is Starting!</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #1e293b; margin: 0 0 20px; font-size: 24px;">Hello {candidate_name}!</h2>
            
            <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 0 0 25px;">
                Your interview for the <strong style="color: #3b82f6;">{job_role}</strong> position is about to begin! 
                We're excited to learn more about your skills and experience.
            </p>
            
            <!-- Interview Details Box -->
            <div style="background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-left: 4px solid #3b82f6; padding: 20px; margin: 25px 0; border-radius: 8px;">
                <h3 style="margin: 0 0 15px; color: #1e293b; font-size: 18px;">Interview Details</h3>
                <ul style="margin: 0; padding-left: 20px; color: #475569;">
                    <li style="margin-bottom: 8px;"><strong>Position:</strong> {job_role}</li>
                    <li style="margin-bottom: 8px;"><strong>Duration:</strong> 20 minutes</li>
                    <li style="margin-bottom: 8px;"><strong>Format:</strong> AI-powered interview</li>
                    <li style="margin-bottom: 8px;"><strong>Features:</strong> Voice recognition, screen sharing, coding environment</li>
                </ul>
            </div>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="{interview_link}" style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #06b6d4); color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 25px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);">
                    Start Interview Now
                </a>
            </div>
            
            <!-- Tips -->
            <div style="background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 20px; margin: 25px 0;">
                <h4 style="margin: 0 0 15px; color: #92400e; font-size: 16px;">Quick Tips for Success</h4>
                <ul style="margin: 0; padding-left: 20px; color: #92400e; font-size: 14px;">
                    <li>Ensure stable internet connection</li>
                    <li>Use Chrome or Edge browser for best experience</li>
                    <li>Allow camera and microphone access</li>
                    <li>Find a quiet, well-lit environment</li>
                </ul>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #f8fafc; padding: 20px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
            <p style="margin: 0; color: #64748b; font-size: 14px;">
                Good luck! We're looking forward to meeting you.
            </p>
            <p style="margin: 10px 0 0; color: #94a3b8; font-size: 12px;">
                © 2024 TalentSync Pro - Revolutionizing Interviews with AI
            </p>
        </div>
    </div>
</body>
</html>
"""

def get_feedback_template(candidate_name, job_role, feedback_data):
    """HTML template for interview feedback"""
    overall_score = feedback_data.get('overall_score', 70)
    
    # Score color based on performance (no emojis to avoid encoding issues)
    if overall_score >= 80:
        score_color = "#10b981"
        score_icon = "★"
        performance_text = "Excellent"
    elif overall_score >= 70:
        score_color = "#3b82f6"
        score_icon = "✓"
        performance_text = "Good"
    elif overall_score >= 60:
        score_color = "#f59e0b"
        score_icon = "!"
        performance_text = "Fair"
    else:
        score_color = "#ef4444"
        score_icon = "*"
        performance_text = "Needs Improvement"
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview Feedback - TalentSync</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; color: #1e293b;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, {score_color}, #06b6d4); padding: 30px; text-align: center;">
            <div style="background: #ffffff; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 36px; color: {score_color};">{score_icon}</div>
            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">Interview Complete!</h1>
            <p style="margin: 10px 0 0; color: #e0f2fe; font-size: 18px;">{performance_text} Performance</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #1e293b; margin: 0 0 20px; font-size: 24px;">Thank you, {candidate_name}!</h2>
            
            <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 0 0 30px;">
                You've successfully completed your interview for the <strong style="color: #3b82f6;">{job_role}</strong> position. 
                Here's your comprehensive feedback report:
            </p>
            
            <!-- Score Card -->
            <div style="background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-radius: 12px; padding: 25px; margin: 25px 0; text-align: center; border: 2px solid {score_color};">
                <h3 style="margin: 0 0 15px; color: #1e293b; font-size: 20px;">Overall Score</h3>
                <div style="font-size: 48px; font-weight: bold; color: {score_color}; margin: 10px 0;">{overall_score}%</div>
                <p style="margin: 0; color: #64748b; font-size: 16px;">{performance_text} Performance</p>
            </div>
            
            <!-- Detailed Scores -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 25px 0;">
                <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #0ea5e9; font-size: 24px; font-weight: bold;">{feedback_data.get('technical_score', 65)}%</div>
                    <div style="color: #0369a1; font-size: 14px;">Technical Skills</div>
                </div>
                <div style="background: #f0fdf4; border: 1px solid #10b981; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #10b981; font-size: 24px; font-weight: bold;">{feedback_data.get('communication_score', 75)}%</div>
                    <div style="color: #047857; font-size: 14px;">Communication</div>
                </div>
            </div>
            
            <!-- Strengths -->
            <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 20px; margin: 25px 0; border-radius: 8px;">
                <h4 style="margin: 0 0 15px; color: #047857; font-size: 18px;">Key Strengths</h4>
                <ul style="margin: 0; padding-left: 20px; color: #065f46;">
                    {"".join([f"<li style='margin-bottom: 8px;'>{strength}</li>" for strength in feedback_data.get('strengths', ['Completed interview', 'Engaged throughout'])[:3]])}
                </ul>
            </div>
            
            <!-- Areas for Improvement -->
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; margin: 25px 0; border-radius: 8px;">
                <h4 style="margin: 0 0 15px; color: #92400e; font-size: 18px;">Areas for Growth</h4>
                <ul style="margin: 0; padding-left: 20px; color: #92400e;">
                    {"".join([f"<li style='margin-bottom: 8px;'>{weakness}</li>" for weakness in feedback_data.get('weaknesses', ['Provide more detail', 'Include examples'])[:3]])}
                </ul>
            </div>
            
            <!-- Next Steps -->
            <div style="background: linear-gradient(135deg, #ddd6fe, #c7d2fe); border-radius: 8px; padding: 20px; margin: 25px 0;">
                <h4 style="margin: 0 0 15px; color: #5b21b6; font-size: 18px;">Next Steps</h4>
                <p style="margin: 0; color: #5b21b6; font-size: 14px;">
                    Your detailed feedback report is attached as a PDF. We'll be in touch soon regarding the next steps in our hiring process.
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #f8fafc; padding: 20px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
            <p style="margin: 0; color: #64748b; font-size: 14px;">
                Thank you for your interest in joining our team!
            </p>
            <p style="margin: 10px 0 0; color: #94a3b8; font-size: 12px;">
                © 2024 TalentSync Pro - Revolutionizing Interviews with AI
            </p>
        </div>
    </div>
</body>
</html>
"""

def get_hr_notification_template(hr_name, candidate_name, candidate_email, job_role, feedback_data):
    """HTML template for HR notification"""
    overall_score = feedback_data.get('overall_score', 70)
    
    if overall_score >= 75:
        recommendation = "Highly Recommended"
        rec_color = "#10b981"
        rec_icon = "✓"
    elif overall_score >= 60:
        recommendation = "Consider for Next Round"
        rec_color = "#f59e0b"
        rec_icon = "!"
    else:
        recommendation = "Not Recommended"
        rec_color = "#ef4444"
        rec_icon = "X"
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview Completed - TalentSync</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; color: #1e293b;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #1e293b, #3b82f6); padding: 30px; text-align: center;">
            <div style="background: #ffffff; width: 60px; height: 60px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #3b82f6;">📊</div>
            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">Interview Completed</h1>
            <p style="margin: 10px 0 0; color: #e0f2fe; font-size: 16px;">Candidate Assessment Report</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #1e293b; margin: 0 0 20px; font-size: 24px;">Hello {hr_name}!</h2>
            
            <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 0 0 25px;">
                A candidate has completed their interview for the <strong style="color: #3b82f6;">{job_role}</strong> position. 
                Here's the AI-generated assessment summary:
            </p>
            
            <!-- Candidate Info -->
            <div style="background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-radius: 12px; padding: 25px; margin: 25px 0;">
                <h3 style="margin: 0 0 20px; color: #1e293b; font-size: 20px;">Candidate Information</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <strong style="color: #475569;">Name:</strong><br>
                        <span style="color: #1e293b; font-size: 16px;">{candidate_name}</span>
                    </div>
                    <div>
                        <strong style="color: #475569;">Email:</strong><br>
                        <span style="color: #1e293b; font-size: 16px;">{candidate_email}</span>
                    </div>
                </div>
            </div>
            
            <!-- Assessment Results -->
            <div style="background: {rec_color}; background: linear-gradient(135deg, {rec_color}20, {rec_color}10); border: 2px solid {rec_color}; border-radius: 12px; padding: 25px; margin: 25px 0; text-align: center;">
                <div style="font-size: 36px; margin-bottom: 10px; color: {rec_color};">{rec_icon}</div>
                <h3 style="margin: 0 0 10px; color: {rec_color}; font-size: 24px;">{recommendation}</h3>
                <div style="font-size: 32px; font-weight: bold; color: {rec_color}; margin: 10px 0;">{overall_score}%</div>
                <p style="margin: 0; color: #64748b;">Overall Performance Score</p>
            </div>
            
            <!-- Performance Breakdown -->
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 25px 0;">
                <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #0ea5e9; font-size: 20px; font-weight: bold;">{feedback_data.get('technical_score', 65)}%</div>
                    <div style="color: #0369a1; font-size: 12px;">Technical</div>
                </div>
                <div style="background: #f0fdf4; border: 1px solid #10b981; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #10b981; font-size: 20px; font-weight: bold;">{feedback_data.get('communication_score', 75)}%</div>
                    <div style="color: #047857; font-size: 12px;">Communication</div>
                </div>
                <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #f59e0b; font-size: 20px; font-weight: bold;">{feedback_data.get('confidence_score', 70)}%</div>
                    <div style="color: #92400e; font-size: 12px;">Confidence</div>
                </div>
            </div>
            
            <!-- Key Insights -->
            <div style="background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 20px; margin: 25px 0; border-radius: 8px;">
                <h4 style="margin: 0 0 15px; color: #1e40af; font-size: 18px;">Key Insights</h4>
                <ul style="margin: 0; padding-left: 20px; color: #1e40af;">
                    {"".join([f"<li style='margin-bottom: 8px;'>{strength}</li>" for strength in feedback_data.get('strengths', ['Completed interview', 'Engaged throughout'])[:3]])}
                </ul>
            </div>
            
            <!-- Action Required -->
            <div style="background: linear-gradient(135deg, #ddd6fe, #c7d2fe); border-radius: 8px; padding: 20px; margin: 25px 0; text-align: center;">
                <h4 style="margin: 0 0 15px; color: #5b21b6; font-size: 18px;">Next Steps</h4>
                <p style="margin: 0 0 15px; color: #5b21b6; font-size: 14px;">
                    Please review the complete assessment and decide on the next steps for this candidate.
                </p>
                <a href="#" style="display: inline-block; background: #5b21b6; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 20px; font-weight: bold; font-size: 14px;">
                    View Full Report
                </a>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #f8fafc; padding: 20px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
            <p style="margin: 0; color: #64748b; font-size: 14px;">
                TalentSync Pro - AI-Powered Recruitment Platform
            </p>
            <p style="margin: 10px 0 0; color: #94a3b8; font-size: 12px;">
                © 2024 TalentSync Pro - Revolutionizing Interviews with AI
            </p>
        </div>
    </div>
</body>
</html>
"""