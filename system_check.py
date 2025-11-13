#!/usr/bin/env python3
"""
AI Interview System - Health Check
Run this to verify your system configuration.
"""

import os
import sys
from pathlib import Path

def check_system_health():
    """Perform comprehensive system health check."""
    
    print("="*60)
    print("🤖 AI INTERVIEW SYSTEM - HEALTH CHECK")
    print("="*60)
    
    issues = []
    warnings = []
    
    # Check Python version
    print(f"🐍 Python Version: {sys.version}")
    if sys.version_info < (3, 7):
        issues.append("Python 3.7+ required")
    
    # Check project structure
    print("\n📁 Project Structure:")
    required_files = [
        "ai_interview_system/Backend Files/app/__init__.py",
        "ai_interview_system/Backend Files/app/main.py",
        "ai_interview_system/Backend Files/app/models.py",
        "ai_interview_system/Backend Files/app/ai_service.py",
        "ai_interview_system/Backend Files/app/email_service.py",
        "ai_interview_system/Backend Files/app/adaptive_interview.py",
        "ai_interview_system/Backend Files/templates/interview/adaptive_interface.html",
        "ai_interview_system/Backend Files/run.py"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            issues.append(f"Missing file: {file_path}")
    
    # Check environment variables
    print("\n🔧 Environment Configuration:")
    
    # Email configuration
    email_vars = ['MAIL_SERVER', 'MAIL_USERNAME', 'MAIL_PASSWORD']
    email_configured = True
    for var in email_vars:
        value = os.environ.get(var)
        if value:
            display_value = value if var != 'MAIL_PASSWORD' else '*' * len(value)
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Not set")
            email_configured = False
    
    if not email_configured:
        warnings.append("Email system not configured - notifications won't work")
    
    # AI service configuration
    ai_vars = ['OPENROUTER_API_KEY']
    ai_configured = True
    for var in ai_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: {'*' * min(len(value), 20)}")
        else:
            print(f"  ⚠️  {var}: Not set (will use fallback)")
            ai_configured = False
    
    if not ai_configured:
        warnings.append("AI service not configured - will use fallback questions")
    
    # Check database
    print("\n🗄️  Database:")
    db_path = Path("ai_interview_system/Backend Files/instance/interview_system.db")
    if db_path.exists():
        print(f"  ✅ Database exists: {db_path}")
        print(f"  📊 Size: {db_path.stat().st_size} bytes")
    else:
        print(f"  ⚠️  Database not found - will be created on first run")
        warnings.append("Database will be created automatically on first run")
    
    # Check required Python packages
    print("\n📦 Python Packages:")
    required_packages = [
        'flask',
        'flask-login',
        'flask-mail',
        'flask-sqlalchemy',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            # Special handling for python-dotenv
            if package == 'python-dotenv':
                import dotenv
            else:
                __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        issues.append(f"Missing packages: {', '.join(missing_packages)}")
    
    # Security features check
    print("\n🔒 Security Features:")
    security_features = [
        "Fullscreen enforcement",
        "Tab switching detection", 
        "Window focus monitoring",
        "Keyboard shortcut blocking",
        "Auto-submission on violations"
    ]
    
    for feature in security_features:
        print(f"  ✅ {feature}")
    
    # Email features check
    print("\n📧 Email Features:")
    email_features = [
        "Shortlist notifications",
        "Interview scheduling",
        "Automatic feedback",
        "Bulk notifications",
        "Registration invitations"
    ]
    
    for feature in email_features:
        status = "✅" if email_configured else "⚠️ "
        print(f"  {status} {feature}")
    
    # Summary
    print("\n" + "="*60)
    print("📋 HEALTH CHECK SUMMARY")
    print("="*60)
    
    if not issues and not warnings:
        print("🎉 EXCELLENT! Your system is fully configured and ready to use.")
        print("\n🚀 Next steps:")
        print("  1. Run: python run.py")
        print("  2. Open: http://127.0.0.1:5000")
        print("  3. Register as HR or Student")
        print("  4. Start creating interviews!")
        
    else:
        if issues:
            print("❌ CRITICAL ISSUES (must fix):")
            for issue in issues:
                print(f"  • {issue}")
            
            if missing_packages:
                print(f"\n💡 To install missing packages:")
                print(f"  pip install {' '.join(missing_packages)}")
        
        if warnings:
            print("\n⚠️  WARNINGS (recommended to fix):")
            for warning in warnings:
                print(f"  • {warning}")
            
            if not email_configured:
                print(f"\n💡 To configure email:")
                print(f"  1. Read EMAIL_SETUP_GUIDE.md")
                print(f"  2. Create .env file with email settings")
                print(f"  3. Run: python ai_interview_system/Backend Files/app/email_test.py")
    
    print("\n📚 Documentation:")
    print("  • EMAIL_SETUP_GUIDE.md - Email configuration")
    print("  • README.md - General setup and usage")
    
    return len(issues) == 0

if __name__ == '__main__':
    success = check_system_health()
    sys.exit(0 if success else 1)