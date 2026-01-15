#!/usr/bin/env python3
"""
Email configuration test utility.
Run this to test your email settings.
"""

import os
from flask import Flask
from flask_mail import Mail, Message

def test_email_config():
    """Test email configuration and send a test email."""
    
    # Create a minimal Flask app for testing
    app = Flask(__name__)
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    
    print("="*60)
    print("EMAIL CONFIGURATION TEST")
    print("="*60)
    
    # Check configuration
    print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
    print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"MAIL_PASSWORD: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'Not set'}")
    
    if not all([app.config['MAIL_SERVER'], app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']]):
        print("\n❌ ERROR: Email configuration incomplete!")
        print("Please set the following environment variables:")
        if not app.config['MAIL_SERVER']:
            print("  - MAIL_SERVER (e.g., smtp.gmail.com)")
        if not app.config['MAIL_USERNAME']:
            print("  - MAIL_USERNAME (your email address)")
        if not app.config['MAIL_PASSWORD']:
            print("  - MAIL_PASSWORD (your email password or app password)")
        return False
    
    # Initialize mail
    mail = Mail(app)
    
    with app.app_context():
        try:
            print("\n🔄 Testing email connection...")
            
            # Create test message
            msg = Message(
                subject="AI Interview System - Email Test",
                recipients=[app.config['MAIL_USERNAME']],  # Send to self
                sender=app.config['MAIL_USERNAME'],
                html="""
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>✅ Email Test Successful!</h2>
                    <p>Your AI Interview System email configuration is working correctly.</p>
                    <p><strong>Configuration Details:</strong></p>
                    <ul>
                        <li>Server: {}</li>
                        <li>Port: {}</li>
                        <li>TLS: {}</li>
                        <li>Username: {}</li>
                    </ul>
                    <p>You can now send interview notifications and feedback emails.</p>
                </body>
                </html>
                """.format(
                    app.config['MAIL_SERVER'],
                    app.config['MAIL_PORT'],
                    app.config['MAIL_USE_TLS'],
                    app.config['MAIL_USERNAME']
                )
            )
            
            # Send test email
            mail.send(msg)
            
            print("✅ SUCCESS: Test email sent successfully!")
            print(f"📧 Check your inbox at: {app.config['MAIL_USERNAME']}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to send test email")
            print(f"Error details: {e}")
            print(f"Error type: {type(e).__name__}")
            
            # Common error solutions
            print("\n💡 Common solutions:")
            print("1. For Gmail: Use App Password instead of regular password")
            print("2. Enable 2-factor authentication and generate App Password")
            print("3. Check if 'Less secure app access' is enabled (not recommended)")
            print("4. Verify SMTP server and port settings")
            print("5. Check firewall/network restrictions")
            
            return False

if __name__ == '__main__':
    test_email_config()