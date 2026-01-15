#!/usr/bin/env python3
"""
Score all candidates for all job drives
"""

from app import create_app, db
from app.models import JobDrive, StudentProfile, User
from app.resume_models import CandidateScore, JobRequirement
from app.candidate_scoring import CandidateScoringEngine
import json

def score_all_candidates():
    """Score all candidates for all active job drives"""
    
    app = create_app()
    with app.app_context():
        print("🎯 Scoring All Candidates for All Job Drives")
        print("=" * 60)
        
        # Get all active job drives
        job_drives = JobDrive.query.filter_by(is_active=True).all()
        print(f"📋 Found {len(job_drives)} active job drives")
        
        # Get all students with resumes
        students_with_resumes = db.session.query(StudentProfile).join(User).filter(
            User.user_type == 'student'
        ).all()
        print(f"👥 Found {len(students_with_resumes)} students")
        
        scoring_engine = CandidateScoringEngine()
        scoring_engine.eligibility_threshold = 30.0  # 30% threshold
        
        total_scored = 0
        total_eligible = 0
        
        for job_drive in job_drives:
            print(f"\n💼 Processing Job: {job_drive.title} (ID: {job_drive.id})")
            
            # Check if job requirements exist
            job_req = JobRequirement.query.filter_by(job_drive_id=job_drive.id).first()
            if not job_req:
                print(f"⚠️  No requirements found for job {job_drive.id}, creating basic requirements...")
                
                # Create basic requirements from job description
                from app.job_parser import JobDescriptionParser
                parser = JobDescriptionParser()
                parsed_data = parser.parse_job_description(
                    job_drive.description or "General requirements", 
                    job_drive.title, 
                    job_drive.job_role
                )
                
                job_req = JobRequirement(
                    job_drive_id=job_drive.id,
                    required_skills=json.dumps(parsed_data['required_skills']),
                    preferred_skills=json.dumps(parsed_data['preferred_skills']),
                    min_experience_years=parsed_data['experience_requirements']['min_years'],
                    max_experience_years=parsed_data['experience_requirements']['max_years'],
                    experience_level=parsed_data['experience_requirements']['level'],
                    min_degree_level='bachelor',
                    location_type='remote'
                )
                db.session.add(job_req)
                db.session.commit()
                print(f"✅ Created requirements with {len(parsed_data['required_skills'])} skills")
            
            # Score all students for this job
            job_scored = 0
            job_eligible = 0
            
            for student in students_with_resumes:
                try:
                    # Check if already scored
                    existing_score = CandidateScore.query.filter_by(
                        student_id=student.id,
                        job_drive_id=job_drive.id
                    ).first()
                    
                    if existing_score:
                        print(f"  📊 Student {student.id} already scored: {existing_score.overall_score:.1f}%")
                        if existing_score.is_eligible:
                            job_eligible += 1
                        continue
                    
                    # Score the candidate
                    result = scoring_engine.score_candidate_for_job(student.id, job_drive.id)
                    
                    if result['success']:
                        job_scored += 1
                        total_scored += 1
                        
                        if result['is_eligible']:
                            job_eligible += 1
                            total_eligible += 1
                            
                        print(f"  ✅ Student {student.id}: {result['overall_score']:.1f}% {'(Eligible)' if result['is_eligible'] else ''}")
                    else:
                        print(f"  ❌ Failed to score student {student.id}: {result['error']}")
                        
                except Exception as e:
                    print(f"  ❌ Error scoring student {student.id}: {e}")
            
            print(f"  📈 Job Summary: {job_scored} newly scored, {job_eligible} eligible total")
        
        print(f"\n🎉 Scoring Complete!")
        print(f"📊 Total candidates scored: {total_scored}")
        print(f"✅ Total eligible candidates: {total_eligible}")
        
        # Show eligible candidates by job
        print(f"\n📋 Eligible Candidates by Job:")
        for job_drive in job_drives:
            eligible_count = CandidateScore.query.filter_by(
                job_drive_id=job_drive.id,
                is_eligible=True
            ).count()
            print(f"  • {job_drive.title}: {eligible_count} eligible candidates")

if __name__ == '__main__':
    score_all_candidates()