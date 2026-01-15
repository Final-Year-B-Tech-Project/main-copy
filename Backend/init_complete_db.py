#!/usr/bin/env python3
"""
Complete Database Initialization
Create all required tables for the HR shortlisting system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, StudentProfile, HRProfile, JobDrive, InterviewSession
from app.resume_models import CandidateSkill, ParsedResume, JobRequirement, CandidateScore, ResumeParsingLog
import json
from datetime import datetime

def initialize_database():
    """Initialize complete database with all tables"""
    
    app = create_app()
    with app.app_context():
        print("🔧 Initializing complete database...")
        
        try:
            # Drop all tables and recreate
            print("Dropping existing tables...")
            db.drop_all()
            
            print("Creating all tables...")
            db.create_all()
            
            print("✅ All tables created successfully!")
            
            # Create sample data
            print("Creating sample data...")
            
            # Create HR user
            hr_user = User(
                email='hr@company.com',
                username='hrmanager',
                user_type='hr',
                first_name='HR',
                last_name='Manager',
                phone='1234567890'
            )
            hr_user.set_password('password123')
            db.session.add(hr_user)
            db.session.flush()
            
            # Create HR profile
            hr_profile = HRProfile(
                user_id=hr_user.id,
                company_name='Tech Company',
                company_website='https://techcompany.com',
                department='Human Resources',
                position='HR Manager',
                hr_code='HR001'
            )
            db.session.add(hr_profile)
            db.session.flush()
            
            # Create job drive
            job_drive = JobDrive(
                hr_id=hr_profile.id,
                title='Senior Software Developer',
                description='We are looking for a senior software developer with experience in Python, JavaScript, and React.',
                job_role='Software Developer',
                experience_required='3-5 years',
                skills_required='Python,JavaScript,React,Node.js',
                number_of_positions=2,
                location='Remote',
                salary_range='$80,000 - $120,000',
                is_active=True
            )
            db.session.add(job_drive)
            db.session.flush()
            
            # Create job requirements
            job_req = JobRequirement(
                job_drive_id=job_drive.id,
                required_skills=json.dumps([
                    {"skill": "Python", "importance": "high", "min_proficiency": "intermediate"},
                    {"skill": "JavaScript", "importance": "high", "min_proficiency": "intermediate"},
                    {"skill": "React", "importance": "medium", "min_proficiency": "intermediate"}
                ]),
                preferred_skills=json.dumps([
                    {"skill": "Node.js", "importance": "low", "min_proficiency": "beginner"},
                    {"skill": "SQL", "importance": "medium", "min_proficiency": "intermediate"}
                ]),
                min_experience_years=3.0,
                max_experience_years=5.0,
                experience_level='senior',
                min_degree_level='bachelor',
                location_type='remote'
            )
            db.session.add(job_req)
            
            # Create sample students
            students_data = [
                {
                    'email': 'john.doe@example.com',
                    'username': 'johndoe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'university': 'MIT',
                    'degree': 'Computer Science',
                    'gpa': 3.8,
                    'skills': ["Python", "JavaScript", "React", "Node.js", "SQL"],
                    'experience_years': 4.0,
                    'score': 85.0
                },
                {
                    'email': 'jane.smith@example.com',
                    'username': 'janesmith',
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'university': 'Stanford',
                    'degree': 'Software Engineering',
                    'gpa': 3.6,
                    'skills': ["Python", "Java", "React", "Angular"],
                    'experience_years': 3.5,
                    'score': 78.0
                },
                {
                    'email': 'mike.johnson@example.com',
                    'username': 'mikejohnson',
                    'first_name': 'Mike',
                    'last_name': 'Johnson',
                    'university': 'UC Berkeley',
                    'degree': 'Computer Science',
                    'gpa': 3.9,
                    'skills': ["Python", "JavaScript", "React", "Node.js", "MongoDB"],
                    'experience_years': 5.0,
                    'score': 92.0
                }
            ]
            
            for student_data in students_data:
                # Create user
                student = User(
                    email=student_data['email'],
                    username=student_data['username'],
                    user_type='student',
                    first_name=student_data['first_name'],
                    last_name=student_data['last_name'],
                    phone='1234567890'
                )
                student.set_password('password123')
                db.session.add(student)
                db.session.flush()
                
                # Create student profile
                profile = StudentProfile(
                    user_id=student.id,
                    university=student_data['university'],
                    degree=student_data['degree'],
                    graduation_year=2024,
                    gpa=student_data['gpa'],
                    skills=json.dumps(student_data['skills']),
                    experience_level='experienced',
                    total_experience_years=student_data['experience_years']
                )
                db.session.add(profile)
                db.session.flush()
                
                # Create candidate score
                overall_score = student_data['score']
                score = CandidateScore(
                    student_id=profile.id,
                    job_drive_id=job_drive.id,
                    skill_match_score=overall_score - 5,
                    experience_score=overall_score - 10,
                    education_score=overall_score + 5,
                    other_score=overall_score,
                    overall_score=overall_score,
                    is_eligible=overall_score >= 30.0,
                    is_shortlisted=overall_score >= 50.0,
                    skill_matches=json.dumps([
                        {"skill": "Python", "candidate_proficiency": "advanced", "required": "intermediate", "match": True},
                        {"skill": "JavaScript", "candidate_proficiency": "intermediate", "required": "intermediate", "match": True},
                        {"skill": "React", "candidate_proficiency": "intermediate", "required": "intermediate", "match": True}
                    ]),
                    missing_skills=json.dumps([
                        {"skill": "SQL", "required_proficiency": "intermediate", "importance": "medium"}
                    ]) if overall_score < 90 else json.dumps([]),
                    score_breakdown=json.dumps({
                        "skill_details": "Strong match in core technologies",
                        "experience_details": "Excellent experience level for role",
                        "education_details": "Top-tier education background",
                        "other_details": "Well-rounded candidate profile"
                    }),
                    shortlist_reason="Excellent technical skills and strong experience",
                    shortlisted_at=datetime.utcnow() if overall_score >= 50.0 else None
                )
                db.session.add(score)
            
            # Commit all changes
            db.session.commit()
            print("✅ Sample data created successfully!")
            
            # Verify data
            total_users = User.query.count()
            total_students = User.query.filter_by(user_type='student').count()
            total_hr = User.query.filter_by(user_type='hr').count()
            total_drives = JobDrive.query.count()
            total_scores = CandidateScore.query.count()
            shortlisted_count = CandidateScore.query.filter_by(is_shortlisted=True).count()
            
            print(f"📊 Database Summary:")
            print(f"   Total Users: {total_users}")
            print(f"   Students: {total_students}")
            print(f"   HR Users: {total_hr}")
            print(f"   Job Drives: {total_drives}")
            print(f"   Candidate Scores: {total_scores}")
            print(f"   Shortlisted Candidates: {shortlisted_count}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = initialize_database()
    if success:
        print("\n🎉 Database initialization completed successfully!")
        print("💡 You can now log in as:")
        print("   HR: hr@company.com / password123")
        print("   Students: john.doe@example.com, jane.smith@example.com, mike.johnson@example.com / password123")
    else:
        print("\n❌ Database initialization failed.")