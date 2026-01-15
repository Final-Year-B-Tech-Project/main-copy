#!/usr/bin/env python3
"""
Debug HR Shortlisting Data
Check what data exists in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, JobDrive, StudentProfile, HRProfile
from app.resume_models import CandidateScore, JobRequirement

def debug_shortlisting():
    """Debug the shortlisting data"""
    
    app = create_app()
    with app.app_context():
        print("🔍 Debugging HR Shortlisting Data...")
        
        # Check HR users
        hr_users = User.query.filter_by(user_type='hr').all()
        print(f"\n📊 HR Users: {len(hr_users)}")
        for hr in hr_users:
            print(f"  - {hr.full_name} ({hr.email})")
            if hr.hr_profile:
                drives = JobDrive.query.filter_by(hr_id=hr.hr_profile.id).all()
                print(f"    Drives: {len(drives)}")
                for drive in drives:
                    print(f"      - {drive.title} (ID: {drive.id})")
        
        # Check students
        students = User.query.filter_by(user_type='student').all()
        print(f"\n👥 Students: {len(students)}")
        for student in students:
            print(f"  - {student.full_name} ({student.email})")
            if student.student_profile:
                print(f"    Profile ID: {student.student_profile.id}")
        
        # Check job drives
        drives = JobDrive.query.all()
        print(f"\n💼 Job Drives: {len(drives)}")
        for drive in drives:
            print(f"  - {drive.title} (ID: {drive.id}, HR ID: {drive.hr_id})")
        
        # Check job requirements
        job_reqs = JobRequirement.query.all()
        print(f"\n📋 Job Requirements: {len(job_reqs)}")
        for req in job_reqs:
            print(f"  - Drive {req.job_drive_id}: {req.experience_level} level")
        
        # Check candidate scores
        scores = CandidateScore.query.all()
        print(f"\n⭐ Candidate Scores: {len(scores)}")
        for score in scores:
            print(f"  - Student {score.student_id}, Drive {score.job_drive_id}: {score.overall_score}% (Shortlisted: {score.is_shortlisted})")
        
        # Check shortlisted candidates specifically
        shortlisted = CandidateScore.query.filter_by(is_shortlisted=True).all()
        print(f"\n🎯 Shortlisted Candidates: {len(shortlisted)}")
        for score in shortlisted:
            try:
                student_profile = StudentProfile.query.get(score.student_id)
                if student_profile:
                    user = User.query.get(student_profile.user_id)
                    drive = JobDrive.query.get(score.job_drive_id)
                    print(f"  - {user.full_name} for {drive.title}: {score.overall_score}%")
                else:
                    print(f"  - Student profile {score.student_id} not found")
            except Exception as e:
                print(f"  - Error loading candidate {score.student_id}: {e}")
        
        # Test the specific query used in the route
        print(f"\n🔍 Testing Route Query...")
        try:
            for drive in drives:
                print(f"\nTesting drive: {drive.title} (ID: {drive.id})")
                
                shortlisted_candidates = db.session.query(
                    CandidateScore, User, StudentProfile
                ).join(
                    StudentProfile, CandidateScore.student_id == StudentProfile.id
                ).join(
                    User, StudentProfile.user_id == User.id
                ).filter(
                    CandidateScore.job_drive_id == drive.id,
                    CandidateScore.is_shortlisted == True
                ).order_by(CandidateScore.overall_score.desc()).all()
                
                print(f"  Query result: {len(shortlisted_candidates)} candidates")
                for score, user, profile in shortlisted_candidates:
                    print(f"    - {user.full_name}: {score.overall_score}%")
                    
        except Exception as e:
            print(f"Query error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_shortlisting()