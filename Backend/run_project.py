#!/usr/bin/env python3
"""
Quick start script for TalentSync with proctoring integration
"""

import os
import sys
from app import create_app, db

def setup_environment():
    """Setup environment variables"""
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    os.environ.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Set GEMINI_API_KEY if not already set
    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠️  GEMINI_API_KEY not set. AI features may not work.")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")

def main():
    """Run the application"""
    print("🚀 Starting TalentSync with Proctoring Integration...")
    
    # Setup environment
    setup_environment()
    
    # Create Flask app
    app = create_app('development')
    
    # Create database tables
    with app.app_context():
        print("📊 Creating database tables...")
        db.create_all()
        print("✅ Database ready")
    
    print("\n🎯 Testing URLs:")
    print("   Main App: http://127.0.0.1:5000")
    print("   Student Dashboard: http://127.0.0.1:5000/student/dashboard")
    print("   Practice Interview: http://127.0.0.1:5000/student/practice-interview")
    print("   Proctoring Test: http://127.0.0.1:5000/api/proctoring/test")
    
    print("\n🔒 Proctoring Features:")
    print("   ✓ Real-time face detection")
    print("   ✓ Object detection (phones, etc.)")
    print("   ✓ Violation alerts")
    print("   ✓ Session tracking")
    
    print("\n📝 To test proctoring:")
    print("   1. Register as student")
    print("   2. Start practice interview")
    print("   3. Allow camera access")
    print("   4. Watch for proctoring status indicator")
    print("   5. Try holding a phone to test detection")
    
    # Run the app
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)

if __name__ == '__main__':
    main()