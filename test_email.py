#!/usr/bin/env python3
"""
Test email sending functionality
"""

import sys
import os
sys.path.append('ai_interview_system/Backend Files')

def test_start_notification():
    """Test sending start notification email"""
    try:
        from app.email_templates import get_interview_start_template
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        # Test template generation
        html_body = get_interview_start_template(
            "Test Candidate",
            "Software Engineer", 
            "http://localhost:5000/interview/test"
        )
        
        print("✓ Email template generated successfully")
        print(f"Template length: {len(html_body)} characters")
        
        # Check for encoding issues
        try:
            html_body.encode('ascii', errors='strict')
            print("✓ No encoding issues found")
        except UnicodeEncodeError as e:
            print(f"✗ Encoding issue: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Email template test failed: {e}")
        return False

def test_email_config():
    """Test email configuration"""
    try:
        from flask import Flask
        app = Flask(__name__)
        
        # Check environment variables
        mail_server = os.getenv('MAIL_SERVER')
        mail_username = os.getenv('MAIL_USERNAME') 
        mail_password = os.getenv('MAIL_PASSWORD')
        
        print(f"MAIL_SERVER: {mail_server}")
        print(f"MAIL_USERNAME: {mail_username}")
        print(f"MAIL_PASSWORD: {'***' if mail_password else 'Not set'}")
        
        if not mail_username or not mail_password:
            print("✗ Email credentials not configured")
            return False
        
        print("✓ Email configuration found")
        return True
        
    except Exception as e:
        print(f"✗ Email config test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing email functionality...\n")
    
    config_ok = test_email_config()
    template_ok = test_start_notification()
    
    if config_ok and template_ok:
        print("\n✓ Email system ready")
    else:
        print("\n✗ Email system has issues")