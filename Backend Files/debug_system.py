#!/usr/bin/env python3
"""
Comprehensive System Debug Script for AI Interview System
Identifies all issues and provides detailed analysis
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
import requests
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_environment():
    print_header("ENVIRONMENT CONFIGURATION")
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✓ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'OPENROUTER_API_KEY' in content:
                print("✓ OpenRouter API key configured")
            else:
                print("✗ OpenRouter API key missing")
    else:
        print("✗ .env file missing")
    
    # Check required environment variables
    required_vars = [
        'FLASK_ENV', 'SECRET_KEY', 'DATABASE_URL', 
        'OPENROUTER_API_KEY', 'MAIL_SERVER', 'MAIL_USERNAME'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'PASSWORD' in var:
                print(f"✓ {var}: {'*' * 10}")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: Not set")

def check_database():
    print_header("DATABASE STATUS")
    
    db_path = 'instance/interview_agent.db'
    if os.path.exists(db_path):
        print(f"✓ Database file exists: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"✓ Found {len(tables)} tables:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"  - {table[0]}: {count} records")
            
            # Check for admin users
            cursor.execute("SELECT COUNT(*) FROM user WHERE role IN ('admin', 'master_admin')")
            admin_count = cursor.fetchone()[0]
            print(f"✓ Admin users: {admin_count}")
            
            # Check for students
            cursor.execute("SELECT COUNT(*) FROM user WHERE user_type = 'student'")
            student_count = cursor.fetchone()[0]
            print(f"✓ Student users: {student_count}")
            
            # Check for HR users
            cursor.execute("SELECT COUNT(*) FROM user WHERE user_type = 'hr'")
            hr_count = cursor.fetchone()[0]
            print(f"✓ HR users: {hr_count}")
            
            # Check interview sessions
            cursor.execute("SELECT COUNT(*) FROM interview_session")
            session_count = cursor.fetchone()[0]
            print(f"✓ Interview sessions: {session_count}")
            
            conn.close()
            
        except Exception as e:
            print(f"✗ Database error: {e}")
    else:
        print(f"✗ Database file not found: {db_path}")

def check_ai_service():
    print_header("AI SERVICE STATUS")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    
    if not api_key or api_key == 'your-actual-api-key-here':
        print("✗ Invalid API key")
        return
    
    print(f"✓ API Key: {api_key[:20]}...")
    print(f"✓ Base URL: {base_url}")
    
    # Test API connection
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "AI Interview Agent Debug"
        }
        
        data = {
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": [{"role": "user", "content": "Hello, this is a test."}],
            "max_tokens": 50
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✓ AI API connection successful")
            result = response.json()
            if 'choices' in result:
                print(f"✓ AI response: {result['choices'][0]['message']['content'][:50]}...")
        else:
            print(f"✗ AI API error: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ AI API connection failed: {e}")

def check_file_structure():
    print_header("FILE STRUCTURE")
    
    required_files = [
        'app.py', 'config.py', 'requirements.txt',
        'app/__init__.py', 'app/models.py', 'app/main.py',
        'app/auth.py', 'app/ai_service.py',
        'templates/base.html', 'templates/index.html',
        'templates/interview/pro_interface.html',
        'static/css/main.css', 'static/js/main.js'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")

def check_dependencies():
    print_header("DEPENDENCIES")
    
    try:
        import flask
        print(f"✓ Flask: {flask.__version__}")
    except ImportError:
        print("✗ Flask not installed")
    
    try:
        import flask_sqlalchemy
        print(f"✓ Flask-SQLAlchemy: {flask_sqlalchemy.__version__}")
    except ImportError:
        print("✗ Flask-SQLAlchemy not installed")
    
    try:
        import flask_login
        print(f"✓ Flask-Login: {flask_login.__version__}")
    except ImportError:
        print("✗ Flask-Login not installed")
    
    try:
        import requests
        print(f"✓ Requests: {requests.__version__}")
    except ImportError:
        print("✗ Requests not installed")
    
    try:
        import dotenv
        print(f"✓ Python-dotenv: {dotenv.__version__}")
    except ImportError:
        print("✗ Python-dotenv not installed")

def check_interview_functionality():
    print_header("INTERVIEW FUNCTIONALITY ANALYSIS")
    
    # Check AI service files
    ai_files = ['app/ai_service.py', 'app/ai_service_simple.py']
    for ai_file in ai_files:
        if os.path.exists(ai_file):
            print(f"✓ {ai_file} exists")
            with open(ai_file, 'r') as f:
                content = f.read()
                if 'generate_interview_questions' in content:
                    print(f"  ✓ Question generation function found")
                if 'generate_feedback' in content:
                    print(f"  ✓ Feedback generation function found")
        else:
            print(f"✗ {ai_file} missing")
    
    # Check interview templates
    interview_templates = [
        'templates/interview/pro_interface.html',
        'templates/interview/interface.html',
        'templates/interview/adaptive_interface.html'
    ]
    
    for template in interview_templates:
        if os.path.exists(template):
            print(f"✓ {template} exists")
        else:
            print(f"✗ {template} missing")

def identify_critical_issues():
    print_header("CRITICAL ISSUES IDENTIFIED")
    
    issues = []
    
    # Check for common issues
    if not os.path.exists('.env'):
        issues.append("CRITICAL: .env file missing - Application won't start")
    
    if not os.path.exists('instance/interview_agent.db'):
        issues.append("CRITICAL: Database missing - No data persistence")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key or api_key == 'your-actual-api-key-here':
        issues.append("CRITICAL: Invalid AI API key - Interview questions won't generate")
    
    if not os.path.exists('app/models.py'):
        issues.append("CRITICAL: Database models missing - Application won't function")
    
    if not os.path.exists('templates/interview/pro_interface.html'):
        issues.append("HIGH: Interview interface missing - Interviews won't work")
    
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("✓ No critical issues found")

def provide_solutions():
    print_header("RECOMMENDED SOLUTIONS")
    
    solutions = [
        "1. Verify .env file has correct API keys and configuration",
        "2. Initialize database: python -c \"from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()\"",
        "3. Create admin user: python create_admin.py",
        "4. Test AI service connection with valid OpenRouter API key",
        "5. Check all required dependencies are installed: pip install -r requirements.txt",
        "6. Verify file permissions for uploads directory",
        "7. Test interview flow end-to-end",
        "8. Check browser console for JavaScript errors",
        "9. Verify email configuration for notifications",
        "10. Test voice recognition in supported browsers (Chrome/Edge)"
    ]
    
    for solution in solutions:
        print(solution)

def main():
    print("AI Interview System - Comprehensive Debug Analysis")
    print(f"Timestamp: {datetime.now()}")
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    try:
        check_environment()
        check_dependencies()
        check_file_structure()
        check_database()
        check_ai_service()
        check_interview_functionality()
        identify_critical_issues()
        provide_solutions()
        
        print_header("DEBUG COMPLETE")
        print("✓ System analysis completed successfully")
        
    except Exception as e:
        print(f"\n✗ Debug script error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()