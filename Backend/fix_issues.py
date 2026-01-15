#!/usr/bin/env python3
"""
Fix skill mapping and job drive ownership issues
"""

from app import create_app, db
from app.models import User, StudentProfile, JobDrive, HRProfile
from app.resume_models import CandidateSkill, CandidateScore
from app.candidate_scoring import CandidateScoringEngine

def fix_issues():
    """Fix skill mapping and job ownership issues"""
    
    app = create_app()
    with app.app_context():
        print("🔧 Fixing Database Issues")
        print("=" * 60)
        
        # Issue 1: Fix skill mapping for DEEPAK SHINDE
        print("\n1. 🎯 Fixing Skill Mapping...")
        
        # Find DEEPAK SHINDE's correct student profile
        deepak_user = User.query.filter_by(username='deep_shindzz').first()
        if deepak_user:
            deepak_profile = StudentProfile.query.filter_by(user_id=deepak_user.id).first()
            if deepak_profile:
                print(f"✅ Found DEEPAK SHINDE: user_id={deepak_user.id}, student_id={deepak_profile.id}")
                
                # Check if skills exist for the correct student_id
                existing_skills = CandidateSkill.query.filter_by(student_id=deepak_profile.id).count()
                print(f"📊 Current skills for DEEPAK: {existing_skills}")
                
                if existing_skills == 0:
                    # Copy skills from student_id=1 to DEEPAK's correct student_id
                    skills_to_copy = CandidateSkill.query.filter_by(student_id=1).all()
                    print(f"📋 Copying {len(skills_to_copy)} skills to DEEPAK's profile...")
                    
                    for skill in skills_to_copy:
                        new_skill = CandidateSkill(
                            student_id=deepak_profile.id,
                            skill_name=skill.skill_name,
                            skill_category=skill.skill_category,
                            skill_type=skill.skill_type,
                            proficiency_level=skill.proficiency_level,
                            years_experience=skill.years_experience,
                            extracted_from=skill.extracted_from,
                            confidence_score=skill.confidence_score
                        )
                        db.session.add(new_skill)
                    
                    db.session.commit()
                    print("✅ Skills copied successfully!")
                else:
                    print("✅ Skills already exist for DEEPAK")
        
        # Issue 2: Fix job drive ownership - assign all drives to current HR user (arin)
        print("\n2. 🏢 Fixing Job Drive Ownership...")
        
        arin_user = User.query.filter_by(username='arin').first()
        if arin_user and arin_user.hr_profile:
            arin_hr_id = arin_user.hr_profile.id
            print(f"✅ Found ARIN HR profile: hr_id={arin_hr_id}")
            
            # Update all job drives to belong to arin
            job_drives = JobDrive.query.all()
            for drive in job_drives:
                if drive.hr_id != arin_hr_id:
                    print(f"📝 Updating job drive '{drive.title}' to belong to arin")
                    drive.hr_id = arin_hr_id
            
            db.session.commit()
            print("✅ Job drive ownership updated!")
        
        # Issue 3: Re-score all candidates with correct skills
        print("\n3. 🎯 Re-scoring Candidates with Correct Skills...")
        
        # Delete existing scores
        CandidateScore.query.delete()
        db.session.commit()
        print("🗑️ Cleared existing scores")
        
        # Re-score all candidates
        scoring_engine = CandidateScoringEngine()
        scoring_engine.eligibility_threshold = 30.0
        
        job_drives = JobDrive.query.filter_by(is_active=True).all()
        students = StudentProfile.query.all()
        
        total_scored = 0
        for drive in job_drives:
            for student in students:
                try:
                    result = scoring_engine.score_candidate_for_job(student.id, drive.id)
                    if result['success']:
                        total_scored += 1
                        user = User.query.get(student.user_id)
                        print(f"✅ {user.username}: {result['overall_score']:.1f}% for {drive.title}")
                except Exception as e:
                    print(f"❌ Error scoring: {e}")
        
        print(f"\n🎉 Fixed all issues!")
        print(f"📊 Total candidates re-scored: {total_scored}")
        
        # Show final status
        print(f"\n📋 Final Status:")
        for drive in job_drives:
            eligible_count = CandidateScore.query.filter_by(
                job_drive_id=drive.id,
                is_eligible=True
            ).count()
            print(f"  • {drive.title}: {eligible_count} eligible candidates")

if __name__ == '__main__':
    fix_issues()