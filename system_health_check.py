#!/usr/bin/env python3
"""
Comprehensive System Health Check for AI Interview System
Checks all critical components before making heavy changes
"""

import os
import sys
import sqlite3
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Python Version Check:")
    version = sys.version_info
    print(f"   Current: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Compatible")
        return True
    else:
        print("   ❌ Requires Python 3.8+")
        return False

def check_dependencies():
    """Check required Python packages"""
    print("\n📦 Dependencies Check:")
    
    required_packages = [
        'flask',
        'flask_sqlalchemy', 
        'flask_login',
        'flask_mail',
        'werkzeug',
        'requests',
        'PyPDF2',
        'python-dotenv',
        'PIL',
        'email_validator',
        'reportlab'
    ]
    
    optional_packages = [
        'google.generativeai',
        'gunicorn'
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                importlib.import_module('dotenv')
            elif package == 'PIL':
                importlib.import_module('PIL')
            else:
                importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package} (optional)")
        except ImportError:
            print(f"   ⚠️  {package} (optional - missing)")
            missing_optional.append(package)
    
    return missing_required, missing_optional

def check_project_structure():
    """Check project directory structure"""
    print("\n📁 Project Structure Check:")
    
    base_path = Path("ai_interview_system/Backend Files")
    
    required_dirs = [
        "app",
        "templates", 
        "static",
        "static/css",
        "static/js",
        "static/uploads"
    ]
    
    required_files = [
        "app.py",
        "run.py", 
        "config.py",
        "requirements.txt",
        ".env",
        "app/__init__.py",
        "app/models.py",
        "app/main.py",
        "app/auth.py"
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/")
            missing_dirs.append(dir_path)
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            missing_files.append(file_path)
    
    return missing_dirs, missing_files

def check_database():
    """Check database connectivity and structure"""
    print("\n🗄️  Database Check:")
    
    db_path = "ai_interview_system/Backend Files/interview_agent.db"
    
    if not os.path.exists(db_path):
        print("   ❌ Database file not found")
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
            print(f"   ❌ Missing tables: {missing_tables}")
            conn.close()
            return False
        
        # Check user count
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"   ✅ Database connected - {user_count} users")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("\n🔧 Environment Variables Check:")
    
    env_path = "ai_interview_system/Backend Files/.env"
    
    if not os.path.exists(env_path):
        print("   ❌ .env file not found")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'FLASK_ENV'
    ]
    
    optional_vars = [
        'OPENROUTER_API_KEY',
        'GEMINI_API_KEY', 
        'MAIL_USERNAME',
        'MAIL_PASSWORD'
    ]
    
    missing_required = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}")
        else:
            print(f"   ❌ {var}")
            missing_required.append(var)
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var} (optional)")
        else:
            print(f"   ⚠️  {var} (optional - missing)")
    
    return missing_required

def check_ai_services():
    """Check AI service connectivity"""
    print("\n🤖 AI Services Check:")
    
    from dotenv import load_dotenv
    load_dotenv("ai_interview_system/Backend Files/.env")
    
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    services_available = 0
    
    # Test OpenRouter
    if openrouter_key:
        try:
            import requests
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {openrouter_key}"},
                timeout=5
            )
            if response.status_code == 200:
                print("   ✅ OpenRouter API - Connected")
                services_available += 1
            else:
                print("   ❌ OpenRouter API - Invalid key")
        except Exception as e:
            print(f"   ❌ OpenRouter API - Connection failed: {e}")
    else:
        print("   ⚠️  OpenRouter API - No key configured")
    
    # Test Gemini (if available)
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            print("   ✅ Gemini AI - Connected")
            services_available += 1
        except ImportError:
            print("   ⚠️  Gemini AI - Package not installed")
        except Exception as e:
            print(f"   ❌ Gemini AI - Connection failed: {e}")
    else:
        print("   ⚠️  Gemini AI - No key configured")
    
    if services_available == 0:
        print("   ⚠️  No AI services available - System will use fallback responses")
    
    return services_available > 0

def check_flask_app():
    """Test Flask app initialization"""
    print("\n🌐 Flask Application Check:")
    
    try:
        # Change to the correct directory
        original_cwd = os.getcwd()
        os.chdir("ai_interview_system/Backend Files")
        
        # Try to import and create app
        sys.path.insert(0, os.getcwd())
        from app import create_app
        
        app = create_app()
        print("   ✅ Flask app created successfully")
        
        # Test configuration
        if app.config.get('SECRET_KEY'):
            print("   ✅ Configuration loaded")
        else:
            print("   ❌ Configuration missing")
            return False
        
        # Test database connection
        with app.app_context():
            from app import db
            db.create_all()
            print("   ✅ Database tables created/verified")
        
        os.chdir(original_cwd)
        return True
        
    except Exception as e:
        print(f"   ❌ Flask app failed: {e}")
        os.chdir(original_cwd)
        return False

def generate_fix_recommendations(issues):
    """Generate recommendations to fix identified issues"""
    print("\n🔧 Fix Recommendations:")
    
    if issues['missing_packages']:
        print("\n   📦 Install missing packages:")
        print(f"      pip install {' '.join(issues['missing_packages'])}")
    
    if issues['missing_dirs']:
        print("\n   📁 Create missing directories:")
        for dir_path in issues['missing_dirs']:
            print(f"      mkdir -p 'ai_interview_system/Backend Files/{dir_path}'")
    
    if issues['missing_env_vars']:
        print("\n   🔧 Add missing environment variables to .env:")
        for var in issues['missing_env_vars']:
            print(f"      {var}=your_value_here")
    
    if not issues['database_ok']:
        print("\n   🗄️  Initialize database:")
        print("      cd 'ai_interview_system/Backend Files'")
        print("      python -c \"from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()\"")
    
    if not issues['ai_services_ok']:
        print("\n   🤖 Configure AI services:")
        print("      Add OPENROUTER_API_KEY to .env file")
        print("      Or install: pip install google-generativeai")

def main():
    """Run comprehensive system check"""
    print("=" * 60)
    print("🔍 AI INTERVIEW SYSTEM - HEALTH CHECK")
    print("=" * 60)
    
    issues = {
        'missing_packages': [],
        'missing_dirs': [],
        'missing_files': [],
        'missing_env_vars': [],
        'database_ok': True,
        'ai_services_ok': True,
        'flask_ok': True
    }
    
    # Run all checks
    python_ok = check_python_version()
    missing_required, missing_optional = check_dependencies()
    missing_dirs, missing_files = check_project_structure()
    missing_env_vars = check_environment()
    database_ok = check_database()
    ai_services_ok = check_ai_services()
    flask_ok = check_flask_app()
    
    # Collect issues
    issues['missing_packages'] = missing_required
    issues['missing_dirs'] = missing_dirs
    issues['missing_files'] = missing_files
    issues['missing_env_vars'] = missing_env_vars
    issues['database_ok'] = database_ok
    issues['ai_services_ok'] = ai_services_ok
    issues['flask_ok'] = flask_ok
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SYSTEM HEALTH SUMMARY")
    print("=" * 60)
    
    total_issues = len(missing_required) + len(missing_dirs) + len(missing_files) + len(missing_env_vars)
    if not database_ok:
        total_issues += 1
    if not flask_ok:
        total_issues += 1
    
    if total_issues == 0:
        print("🎉 SYSTEM STATUS: HEALTHY")
        print("✅ All critical components are working properly")
        print("✅ Ready for heavy changes and development")
    else:
        print(f"⚠️  SYSTEM STATUS: {total_issues} ISSUES FOUND")
        print("❌ Fix these issues before making heavy changes")
        generate_fix_recommendations(issues)
    
    print("\n" + "=" * 60)
    
    return total_issues == 0

if __name__ == "__main__":
    main()