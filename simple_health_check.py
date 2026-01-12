#!/usr/bin/env python3
"""
Simple System Health Check for AI Interview System
"""

import os
import sys
import sqlite3
import importlib
from pathlib import Path

def check_dependencies():
    """Check required Python packages"""
    print("\n[DEPENDENCIES CHECK]")
    
    required_packages = [
        ('flask', 'flask'),
        ('flask_sqlalchemy', 'flask_sqlalchemy'), 
        ('flask_login', 'flask_login'),
        ('flask_mail', 'flask_mail'),
        ('werkzeug', 'werkzeug'),
        ('requests', 'requests'),
        ('PyPDF2', 'PyPDF2'),
        ('dotenv', 'python-dotenv'),
        ('PIL', 'Pillow'),
        ('reportlab', 'reportlab')
    ]
    
    missing_required = []
    
    for import_name, package_name in required_packages:
        try:
            importlib.import_module(import_name)
            print(f"   OK: {package_name}")
        except ImportError:
            print(f"   MISSING: {package_name}")
            missing_required.append(package_name)
    
    # Check optional packages
    try:
        importlib.import_module('google.generativeai')
        print("   OK: google-generativeai (optional)")
    except ImportError:
        print("   MISSING: google-generativeai (optional)")
    
    return missing_required

def check_database():
    """Check database connectivity and structure"""
    print("\n[DATABASE CHECK]")
    
    db_path = "ai_interview_system/Backend Files/interview_agent.db"
    
    if not os.path.exists(db_path):
        print("   ERROR: Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        required_tables = ['user', 'student_profile', 'hr_profile', 'job_drive', 'interview_session']
        
        print(f"   Found tables: {tables}")
        
        missing_tables = [table for table in required_tables if table not in tables]
        if missing_tables:
            print(f"   ERROR: Missing tables: {missing_tables}")
            conn.close()
            return False
        
        # Check user count
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"   OK: Database connected - {user_count} users")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ERROR: Database error: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("\n[ENVIRONMENT CHECK]")
    
    env_path = "ai_interview_system/Backend Files/.env"
    
    if not os.path.exists(env_path):
        print("   ERROR: .env file not found")
        return []
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        print("   ERROR: python-dotenv not installed")
        return ['python-dotenv']
    
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'FLASK_ENV'
    ]
    
    missing_required = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   OK: {var}")
        else:
            print(f"   MISSING: {var}")
            missing_required.append(var)
    
    # Check optional AI keys
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if openrouter_key:
        print("   OK: OPENROUTER_API_KEY (optional)")
    else:
        print("   MISSING: OPENROUTER_API_KEY (optional)")
    
    if gemini_key:
        print("   OK: GEMINI_API_KEY (optional)")
    else:
        print("   MISSING: GEMINI_API_KEY (optional)")
    
    return missing_required

def test_flask_import():
    """Test Flask app import"""
    print("\n[FLASK APP CHECK]")
    
    try:
        # Change to the correct directory
        original_cwd = os.getcwd()
        os.chdir("ai_interview_system/Backend Files")
        
        # Try to import app
        sys.path.insert(0, os.getcwd())
        
        # Test basic imports first
        try:
            from app import db
            print("   OK: Database module imported")
        except Exception as e:
            print(f"   ERROR: Database import failed: {e}")
            os.chdir(original_cwd)
            return False
        
        try:
            from app.models import User
            print("   OK: Models imported")
        except Exception as e:
            print(f"   ERROR: Models import failed: {e}")
            os.chdir(original_cwd)
            return False
        
        # Try to create app (this might fail due to missing dependencies)
        try:
            from app import create_app
            app = create_app()
            print("   OK: Flask app created successfully")
            os.chdir(original_cwd)
            return True
        except Exception as e:
            print(f"   ERROR: Flask app creation failed: {e}")
            os.chdir(original_cwd)
            return False
        
    except Exception as e:
        print(f"   ERROR: Flask test failed: {e}")
        os.chdir(original_cwd)
        return False

def main():
    """Run system check"""
    print("=" * 50)
    print("AI INTERVIEW SYSTEM - HEALTH CHECK")
    print("=" * 50)
    
    # Check Python version
    print(f"\n[PYTHON VERSION]")
    version = sys.version_info
    print(f"   Current: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("   OK: Compatible")
    else:
        print("   ERROR: Requires Python 3.8+")
        return False
    
    # Run checks
    missing_packages = check_dependencies()
    database_ok = check_database()
    missing_env_vars = check_environment()
    flask_ok = test_flask_import()
    
    # Summary
    print("\n" + "=" * 50)
    print("SYSTEM HEALTH SUMMARY")
    print("=" * 50)
    
    total_issues = len(missing_packages) + len(missing_env_vars)
    if not database_ok:
        total_issues += 1
    if not flask_ok:
        total_issues += 1
    
    if total_issues == 0:
        print("STATUS: HEALTHY - Ready for heavy changes")
    else:
        print(f"STATUS: {total_issues} ISSUES FOUND")
        
        if missing_packages:
            print(f"\nFIX: Install missing packages:")
            print(f"     pip install {' '.join(missing_packages)}")
        
        if missing_env_vars:
            print(f"\nFIX: Add to .env file:")
            for var in missing_env_vars:
                print(f"     {var}=your_value_here")
        
        if not database_ok:
            print(f"\nFIX: Initialize database:")
            print(f"     cd 'ai_interview_system/Backend Files'")
            print(f"     python -c \"from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()\"")
    
    print("\n" + "=" * 50)
    return total_issues == 0

if __name__ == "__main__":
    main()