#!/usr/bin/env python3
"""
Debug the AI Interview System - Check all components
"""

import os
import sys
from pathlib import Path

def debug_system():
    """Debug all system components."""
    
    print("="*60)
    print("AI INTERVIEW SYSTEM - FULL DEBUG")
    print("="*60)
    
    issues = []
    
    # 1. Check Python imports
    print("\n1. CHECKING PYTHON IMPORTS...")
    try:
        sys.path.insert(0, str(Path("ai_interview_system/Backend Files")))
        
        # Test basic imports
        from app import create_app, db
        print("  ✅ Flask app imports working")
        
        from app.models import User, StudentProfile, HRProfile, JobDrive, InterviewSession
        print("  ✅ Model imports working")
        
        from app.auth import auth
        print("  ✅ Auth blueprint working")
        
        from app.main import main
        print("  ✅ Main blueprint working")
        
        from app.admin import admin
        print("  ✅ Admin blueprint working")
        
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        issues.append(f"Import error: {e}")
    
    # 2. Check database
    print("\n2. CHECKING DATABASE...")
    db_path = Path("ai_interview_system/Backend Files/instance/interview_system.db")
    if db_path.exists():
        print(f"  ✅ Database exists: {db_path}")
        
        # Check database tables
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"  📊 Tables found: {len(tables)}")
        for table in tables:
            print(f"    • {table[0]}")
        
        # Check master admin
        cursor.execute("SELECT username, role FROM user WHERE role = 'master_admin'")
        admin_users = cursor.fetchall()
        
        if admin_users:
            print(f"  ✅ Master admin found: {admin_users[0][0]}")
        else:
            print("  ⚠️  No master admin found")
            issues.append("No master admin user")
        
        conn.close()
    else:
        print("  ❌ Database not found")
        issues.append("Database missing")
    
    # 3. Check templates
    print("\n3. CHECKING TEMPLATES...")
    template_dir = Path("ai_interview_system/Backend Files/templates")
    if template_dir.exists():
        print(f"  ✅ Templates directory exists")
        
        required_templates = [
            "base.html",
            "index.html",
            "auth/login.html",
            "auth/register.html",
            "student/dashboard.html",
            "hr/dashboard.html",
            "interview/adaptive_interface.html",
            "admin/dashboard.html"
        ]
        
        for template in required_templates:
            template_path = template_dir / template
            if template_path.exists():
                print(f"    ✅ {template}")
            else:
                print(f"    ❌ {template}")
                issues.append(f"Missing template: {template}")
    else:
        print("  ❌ Templates directory not found")
        issues.append("Templates directory missing")
    
    # 4. Check static files
    print("\n4. CHECKING STATIC FILES...")
    static_dir = Path("ai_interview_system/Backend Files/static")
    if static_dir.exists():
        print(f"  ✅ Static directory exists")
        
        css_file = static_dir / "css" / "clean-theme.css"
        if css_file.exists():
            print("    ✅ CSS theme file")
        else:
            print("    ❌ CSS theme file missing")
            issues.append("CSS theme file missing")
    else:
        print("  ❌ Static directory not found")
        issues.append("Static directory missing")
    
    # 5. Check configuration
    print("\n5. CHECKING CONFIGURATION...")
    env_file = Path("ai_interview_system/Backend Files/.env")
    if env_file.exists():
        print("  ✅ .env file exists")
        
        # Check key environment variables
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        required_vars = ['SECRET_KEY', 'MAIL_USERNAME', 'OPENROUTER_API_KEY']
        for var in required_vars:
            if var in env_content:
                print(f"    ✅ {var} configured")
            else:
                print(f"    ⚠️  {var} not configured")
    else:
        print("  ❌ .env file not found")
        issues.append(".env file missing")
    
    # 6. Test app creation
    print("\n6. TESTING APP CREATION...")
    try:
        app = create_app('development')
        print("  ✅ App creation successful")
        
        with app.app_context():
            # Test database connection
            try:
                user_count = User.query.count()
                print(f"  ✅ Database connection working ({user_count} users)")
            except Exception as e:
                print(f"  ❌ Database connection failed: {e}")
                issues.append(f"Database connection error: {e}")
                
    except Exception as e:
        print(f"  ❌ App creation failed: {e}")
        issues.append(f"App creation error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("DEBUG SUMMARY")
    print("="*60)
    
    if not issues:
        print("🎉 ALL CHECKS PASSED! System is ready.")
        print("\n🚀 To start the system:")
        print("  cd 'ai_interview_system/Backend Files'")
        print("  python run.py")
        print("\n🔑 Master Admin Login:")
        print("  Username: adminsuyash")
        print("  Password: adminsuyash")
        print("  URL: http://127.0.0.1:5000/admin/dashboard")
        
    else:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n💡 RECOMMENDED FIXES:")
        if "Import error" in str(issues):
            print("  • Install missing packages: pip install -r requirements.txt")
        if "Database missing" in str(issues):
            print("  • Run: python create_master_admin.py")
        if "Missing template" in str(issues):
            print("  • Check template files in templates/ directory")
    
    return len(issues) == 0

if __name__ == '__main__':
    success = debug_system()
    sys.exit(0 if success else 1)