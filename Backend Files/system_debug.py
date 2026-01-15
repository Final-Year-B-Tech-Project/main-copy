#!/usr/bin/env python3
"""
System Debug Script - ASCII Compatible
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
        print("[OK] .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'OPENROUTER_API_KEY' in content:
                print("[OK] OpenRouter API key configured")
            else:
                print("[ERROR] OpenRouter API key missing")
    else:
        print("[ERROR] .env file missing")
    
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
                print(f"[OK] {var}: {'*' * 10}")
            else:
                print(f"[OK] {var}: {value}")
        else:
            print(f"[ERROR] {var}: Not set")

def check_database():
    print_header("DATABASE STATUS")
    
    db_path = 'instance/interview_agent.db'
    if os.path.exists(db_path):
        print(f"[OK] Database file exists: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"[OK] Found {len(tables)} tables:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"  - {table[0]}: {count} records")
            
            # Check for admin users
            cursor.execute("SELECT COUNT(*) FROM user WHERE role IN ('admin', 'master_admin')")
            admin_count = cursor.fetchone()[0]
            print(f"[OK] Admin users: {admin_count}")
            
            # Check for students
            cursor.execute("SELECT COUNT(*) FROM user WHERE user_type = 'student'")
            student_count = cursor.fetchone()[0]
            print(f"[OK] Student users: {student_count}")
            
            # Check for HR users
            cursor.execute("SELECT COUNT(*) FROM user WHERE user_type = 'hr'")
            hr_count = cursor.fetchone()[0]
            print(f"[OK] HR users: {hr_count}")
            
            # Check interview sessions
            cursor.execute("SELECT COUNT(*) FROM interview_session")
            session_count = cursor.fetchone()[0]
            print(f"[OK] Interview sessions: {session_count}")
            
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Database error: {e}")
    else:
        print(f"[ERROR] Database file not found: {db_path}")

def check_ai_service():
    print_header("AI SERVICE STATUS")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    
    if not api_key or api_key == 'your-actual-api-key-here':
        print("[ERROR] Invalid API key")
        return
    
    print(f"[OK] API Key: {api_key[:20]}...")
    print(f"[OK] Base URL: {base_url}")
    
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
            print("[OK] AI API connection successful")
            result = response.json()
            if 'choices' in result:
                print(f"[OK] AI response: {result['choices'][0]['message']['content'][:50]}...")
        else:
            print(f"[ERROR] AI API error: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"[ERROR] AI API connection failed: {e}")

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
            print(f"[OK] {file_path}")
        else:
            print(f"[ERROR] {file_path} - MISSING")

def check_dependencies():
    print_header("DEPENDENCIES")
    
    try:
        import flask
        print(f"[OK] Flask: {flask.__version__}")
    except ImportError:
        print("[ERROR] Flask not installed")
    
    try:
        import flask_sqlalchemy
        print(f"[OK] Flask-SQLAlchemy: {flask_sqlalchemy.__version__}")
    except ImportError:
        print("[ERROR] Flask-SQLAlchemy not installed")
    
    try:
        import flask_login
        print(f"[OK] Flask-Login: {flask_login.__version__}")
    except ImportError:
        print("[ERROR] Flask-Login not installed")
    
    try:
        import requests
        print(f"[OK] Requests: {requests.__version__}")
    except ImportError:
        print("[ERROR] Requests not installed")
    
    try:
        import dotenv
        print("[OK] Python-dotenv: installed")
    except ImportError:
        print("[ERROR] Python-dotenv not installed")

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
        print("[OK] No critical issues found")

def main():
    print("AI Interview System - Debug Analysis")
    print(f"Timestamp: {datetime.now()}")
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    try:
        check_environment()
        check_dependencies()
        check_file_structure()
        check_database()
        check_ai_service()
        identify_critical_issues()
        
        print_header("DEBUG COMPLETE")
        print("[OK] System analysis completed")
        
    except Exception as e:
        print(f"\n[ERROR] Debug script error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()