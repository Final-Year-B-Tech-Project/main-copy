#!/usr/bin/env python3
"""
Reset and recreate the database with all tables.
"""

import os
import sys
from pathlib import Path

# Add the Backend Files directory to Python path
backend_path = Path("ai_interview_system/Backend Files")
sys.path.insert(0, str(backend_path))

from app import create_app, db
from app.models import User, StudentProfile, HRProfile, JobDrive, InterviewSession, Question, InterviewFeedback

def reset_database():
    """Reset and recreate the database."""
    
    print("🔄 Resetting AI Interview System Database...")
    
    # Create app
    app = create_app('development')
    
    with app.app_context():
        try:
            # Drop all tables
            print("🗑️  Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("🏗️  Creating new tables...")
            db.create_all()
            
            # Verify tables were created
            print("✅ Database reset complete!")
            print("\n📋 Tables created:")
            
            # List all tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            for table in tables:
                print(f"  • {table}")
            
            print(f"\n📊 Total tables: {len(tables)}")
            
            # Create a test user to verify everything works
            print("\n👤 Creating test student user...")
            test_user = User(
                email='test@student.com',
                username='teststudent',
                user_type='student',
                first_name='Test',
                last_name='Student'
            )
            test_user.set_password('password123')
            
            db.session.add(test_user)
            db.session.flush()
            
            # Create student profile
            student_profile = StudentProfile(
                user_id=test_user.id,
                university='Test University',
                degree='Computer Science',
                experience_level='fresher'
            )
            db.session.add(student_profile)
            
            # Create test HR user
            print("👔 Creating test HR user...")
            hr_user = User(
                email='test@hr.com',
                username='testhr',
                user_type='hr',
                first_name='Test',
                last_name='HR'
            )
            hr_user.set_password('password123')
            
            db.session.add(hr_user)
            db.session.flush()
            
            # Create HR profile
            from app.utils import generate_hr_code
            hr_profile = HRProfile(
                user_id=hr_user.id,
                hr_code=generate_hr_code(),
                company_name='Test Company',
                department='Engineering'
            )
            db.session.add(hr_profile)
            
            db.session.commit()
            
            print("✅ Test users created successfully!")
            print("\n🔑 Test Login Credentials:")
            print("  Student: test@student.com / password123")
            print("  HR: test@hr.com / password123")
            
            return True
            
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = reset_database()
    if success:
        print("\n🎉 Database reset complete! You can now start the server.")
        print("Run: python run.py")
    else:
        print("\n💥 Database reset failed!")
        sys.exit(1)