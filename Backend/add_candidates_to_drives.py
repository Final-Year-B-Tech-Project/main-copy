#!/usr/bin/env python3
"""
Add Candidates to All Drives
Ensure all HR users can see shortlisted candidates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, JobDrive, StudentProfile
from app.resume_models import CandidateScore, JobRequirement
import json
from datetime import datetime

def add_candidates_to_all_drives():
    """Add shortlisted candidates to all job drives"""
    
    app = create_app()
    with app.app_context():
        print("🔧 Adding candidates to all job drives...")
        
        # Get all drives
        drives = JobDrive.query.all()
        students = StudentProfile.query.all()
        
        print(f"Found {len(drives)} drives and {len(students)} students")
        
        for drive in drives:
            print(f"\nProcessing drive: {drive.title} (ID: {drive.id})")
            
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
            
            # Add candidates to this drive
            for i, student in enumerate(students):
                # Check if score already exists
                existing_score = CandidateScore.query.filter_by(
                    student_id=student.id,
                    job_drive_id=drive.id
                ).first()
                
                if not existing_score:
                    # Create varied scores
                    base_scores = [85.0, 78.0, 92.0, 67.0, 88.0]
                    overall_score = base_scores[i % len(base_scores)]
                    
                    print(f"  Adding {student.user.full_name} with score {overall_score}%")
                    
                    score = CandidateScore(
                        student_id=student.id,
                        job_drive_id=drive.id,
                        skill_match_score=overall_score - 5,
                        experience_score=overall_score - 10,
                        education_score=overall_score + 5,
                        other_score=overall_score,
                        overall_score=overall_score,
                        is_eligible=overall_score >= 30.0,
                        is_shortlisted=overall_score >= 50.0,
                        skill_matches=json.dumps([
                            {"skill": "Python", "candidate_proficiency": "advanced", "required": "intermediate", "match": True},
                            {"skill": "JavaScript", "candidate_proficiency": "intermediate", "required": "beginner", "match": True},
                            {"skill": "React", "candidate_proficiency": "intermediate", "required": "intermediate", "match": True}
                        ]),
                        missing_skills=json.dumps([
                            {"skill": "SQL", "required_proficiency": "intermediate", "importance": "medium"}
                        ]) if overall_score < 90 else json.dumps([]),
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
                else:
                    print(f"  {student.user.full_name} already has score: {existing_score.overall_score}%")
        
        try:
            db.session.commit()
            print("✅ Successfully added candidates to all drives!")
            
            # Verify results
            for drive in drives:
                shortlisted_count = CandidateScore.query.filter_by(
                    job_drive_id=drive.id,
                    is_shortlisted=True
                ).count()
                print(f"  {drive.title}: {shortlisted_count} shortlisted candidates")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            return False
        
        return True

if __name__ == '__main__':
    success = add_candidates_to_all_drives()
    if success:
        print("\n🎉 All drives now have shortlisted candidates!")
        print("💡 Any HR user should now be able to see candidates in their drives.")
    else:
        print("\n❌ Failed to add candidates to drives.")