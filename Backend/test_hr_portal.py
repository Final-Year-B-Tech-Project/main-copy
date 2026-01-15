#!/usr/bin/env python3
"""
Test HR Portal Candidate Display
"""

from app import create_app, db
from app.models import JobDrive, User, StudentProfile
from app.resume_models import CandidateScore, JobRequirement
import json

def test_hr_portal():
    """Test what HR portal should show"""
    
    app = create_app()
    with app.app_context():
        print("🔍 Testing HR Portal Candidate Display")
        print("=" * 60)
        
        # Get all job drives
        job_drives = JobDrive.query.all()
        
        for drive in job_drives:
            print(f"\n💼 Job Drive: {drive.title} (ID: {drive.id})")
            
            # Get eligible candidates for this drive
            eligible_candidates = db.session.query(
                CandidateScore, User, StudentProfile
            ).join(
                StudentProfile, CandidateScore.student_id == StudentProfile.id
            ).join(
                User, StudentProfile.user_id == User.id
            ).filter(
                CandidateScore.job_drive_id == drive.id,
                CandidateScore.is_eligible == True
            ).order_by(CandidateScore.overall_score.desc()).all()
            
            print(f"📊 Found {len(eligible_candidates)} eligible candidates:")
            
            for score, user, profile in eligible_candidates:
                print(f"  ✅ {user.full_name} ({user.email})")
                print(f"     Score: {score.overall_score:.1f}%")
                print(f"     Skills: {score.skill_match_score:.1f}%")
                print(f"     Experience: {score.experience_score:.1f}%")
                print(f"     Shortlisted: {'Yes' if score.is_shortlisted else 'No'}")
                
                # Show skill matches
                if score.skill_matches:
                    matches = json.loads(score.skill_matches)
                    print(f"     Matched Skills: {len(matches)}")
                    for match in matches[:3]:
                        print(f"       • {match.get('skill', 'Unknown')}")
                print()
            
            # Get job requirements
            job_req = JobRequirement.query.filter_by(job_drive_id=drive.id).first()
            if job_req:
                required_skills = json.loads(job_req.required_skills or '[]')
                print(f"📋 Job Requirements: {len(required_skills)} required skills")
                for skill in required_skills[:3]:
                    print(f"  • {skill.get('skill', 'Unknown')} ({skill.get('min_proficiency', 'beginner')})")
            else:
                print("⚠️  No job requirements found")
        
        print(f"\n🌐 HR Portal URLs:")
        for drive in job_drives:
            print(f"  • {drive.title}: http://127.0.0.1:5002/hr/drive/{drive.id}/candidates")

if __name__ == '__main__':
    test_hr_portal()