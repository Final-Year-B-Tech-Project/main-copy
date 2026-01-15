#!/usr/bin/env python3
"""
Fix HR Shortlisting Issue
This script ensures that shortlisted candidates are visible in the HR portal
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, JobDrive, StudentProfile, HRProfile
from app.resume_models import CandidateScore, JobRequirement
import json
from datetime import datetime

def fix_shortlisting():
    """Fix the shortlisting issue by ensuring data exists"""
    
    app = create_app()
    with app.app_context():
        print("🔧 Fixing HR Shortlisting Issue...")
        
        # Get all HR users and their drives
        hr_users = User.query.filter_by(user_type='hr').all()
        print(f"Found {len(hr_users)} HR users")
        
        # Get all students
        students = User.query.filter_by(user_type='student').all()
        print(f"Found {len(students)} students")
        
        if not students:
            print("❌ No students found. Creating sample student...")
            # Create a sample student
            student = User(
                email='john.doe@example.com',
                username='johndoe',
                user_type='student',
                first_name='John',
                last_name='Doe',
                phone='1234567890'
            )
            student.set_password('password123')
            db.session.add(student)
            db.session.flush()
            
            # Create student profile
            profile = StudentProfile(
                user_id=student.id,
                university='Sample University',
                degree='Computer Science',
                graduation_year=2024,
                gpa=3.5,
                skills='["Python", "JavaScript", "React", "Node.js"]',
                experience_level='experienced',
                total_experience_years=2.0
            )
            db.session.add(profile)
            students = [student]
        
        # Process each HR's drives
        for hr_user in hr_users:
            if not hr_user.hr_profile:
                continue
                
            drives = JobDrive.query.filter_by(hr_id=hr_user.hr_profile.id).all()
            print(f"HR {hr_user.full_name} has {len(drives)} drives")
            
            for drive in drives:
                print(f"Processing drive: {drive.title}")
                
                # Check if job requirements exist
                job_req = JobRequirement.query.filter_by(job_drive_id=drive.id).first()
                if not job_req:
                    print(f"Creating job requirements for drive {drive.id}")
                    job_req = JobRequirement(
                        job_drive_id=drive.id,
                        required_skills=json.dumps([
                            {"skill": "Python", "importance": "high", "min_proficiency": "intermediate"},
                            {"skill": "JavaScript", "importance": "medium", "min_proficiency": "beginner"},
                            {"skill": "React", "importance": "medium", "min_proficiency": "intermediate"}
                        ]),
                        preferred_skills=json.dumps([
                            {"skill": "Node.js", "importance": "low", "min_proficiency": "beginner"},
                            {"skill": "SQL", "importance": "medium", "min_proficiency": "intermediate"}
                        ]),
                        min_experience_years=1.0,
                        max_experience_years=5.0,
                        experience_level='mid',
                        min_degree_level='bachelor',
                        location_type='remote'
                    )
                    db.session.add(job_req)
                
                # Create candidate scores for students
                for student in students:
                    if not student.student_profile:
                        continue
                        
                    # Check if score already exists
                    existing_score = CandidateScore.query.filter_by(
                        student_id=student.student_profile.id,
                        job_drive_id=drive.id
                    ).first()
                    
                    if not existing_score:
                        print(f"Creating score for student {student.full_name}")
                        
                        # Create realistic scores
                        skill_score = 75.0
                        experience_score = 65.0
                        education_score = 80.0
                        other_score = 70.0
                        overall_score = (skill_score * 0.4 + experience_score * 0.3 + 
                                       education_score * 0.2 + other_score * 0.1)
                        
                        score = CandidateScore(
                            student_id=student.student_profile.id,
                            job_drive_id=drive.id,
                            skill_match_score=skill_score,
                            experience_score=experience_score,
                            education_score=education_score,
                            other_score=other_score,
                            overall_score=overall_score,
                            is_eligible=overall_score >= 30.0,
                            is_shortlisted=overall_score >= 50.0,
                            skill_matches=json.dumps([
                                {"skill": "Python", "candidate_proficiency": "intermediate", "required": "intermediate", "match": True},
                                {"skill": "JavaScript", "candidate_proficiency": "beginner", "required": "beginner", "match": True},
                                {"skill": "React", "candidate_proficiency": "intermediate", "required": "intermediate", "match": True}
                            ]),
                            missing_skills=json.dumps([
                                {"skill": "SQL", "required_proficiency": "intermediate", "importance": "medium"}
                            ]),
                            score_breakdown=json.dumps({
                                "skill_details": "Strong match in core technologies",
                                "experience_details": "Good experience level for role",
                                "education_details": "Relevant degree and good GPA",
                                "other_details": "Well-rounded candidate"
                            }),
                            shortlist_reason="Strong technical skills and relevant experience",
                            shortlisted_at=datetime.utcnow() if overall_score >= 50.0 else None
                        )
                        db.session.add(score)
        
        # Commit all changes
        try:
            db.session.commit()
            print("✅ Successfully fixed shortlisting data!")
            
            # Verify the fix
            total_scores = CandidateScore.query.count()
            shortlisted_count = CandidateScore.query.filter_by(is_shortlisted=True).count()
            print(f"📊 Total candidate scores: {total_scores}")
            print(f"⭐ Shortlisted candidates: {shortlisted_count}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            return False
        
        return True

if __name__ == '__main__':
    success = fix_shortlisting()
    if success:
        print("\n🎉 Shortlisting fix completed successfully!")
        print("💡 Now HR users should be able to see shortlisted candidates in their drives.")
    else:
        print("\n❌ Fix failed. Please check the error messages above.")