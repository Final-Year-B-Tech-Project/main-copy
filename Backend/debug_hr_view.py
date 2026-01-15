#!/usr/bin/env python3
"""
Debug HR candidates view issue
"""

from app import create_app, db
from app.models import User, JobDrive, HRProfile
from app.resume_models import CandidateScore

def debug_hr_candidates():
    """Debug why candidates are not showing in HR view"""
    
    app = create_app()
    with app.app_context():
        print("🔍 Debugging HR Candidates View")
        print("=" * 60)
        
        # Check HR users and their job drives
        print("1. 👤 HR Users and Job Drives:")
        hr_users = User.query.filter_by(user_type='hr').all()
        
        for hr_user in hr_users:
            print(f"\n  HR User: {hr_user.username} (ID: {hr_user.id})")
            if hr_user.hr_profile:
                print(f"  HR Profile ID: {hr_user.hr_profile.id}")
                
                # Get job drives for this HR
                job_drives = JobDrive.query.filter_by(hr_id=hr_user.hr_profile.id).all()
                print(f"  Job Drives: {len(job_drives)}")
                
                for drive in job_drives:
                    print(f"    • {drive.title} (ID: {drive.id}) - Active: {drive.is_active}")
                    
                    # Check shortlisted candidates for this drive
                    shortlisted = CandidateScore.query.filter_by(
                        job_drive_id=drive.id,
                        is_shortlisted=True
                    ).all()
                    
                    print(f"      Shortlisted candidates: {len(shortlisted)}")
                    for candidate in shortlisted:
                        student = db.session.get(db.session.query(User).join(
                            db.session.query(User.id).join(
                                db.session.query(User.id).filter(User.id.in_(
                                    db.session.query(db.session.query(User.id).join(
                                        db.session.query(User.id).filter(User.user_type == 'student')
                                    ).subquery()).subquery()
                                )).subquery()
                            ).subquery()
                        ).first(), candidate.student_id)
                        if student:
                            print(f"        - Student ID {candidate.student_id}: {candidate.overall_score:.1f}%")
        
        # Check all shortlisted candidates
        print(f"\n2. 📊 All Shortlisted Candidates:")
        with db.engine.connect() as conn:
            shortlisted_data = conn.execute(db.text("""
                SELECT jd.id as job_id, jd.title, jd.hr_id, u.username, cs.overall_score
                FROM candidate_score cs
                JOIN job_drive jd ON cs.job_drive_id = jd.id
                JOIN student_profile sp ON cs.student_id = sp.id
                JOIN user u ON sp.user_id = u.id
                WHERE cs.is_shortlisted = 1
                ORDER BY jd.id, cs.overall_score DESC
            """)).fetchall()
            
            for job_id, job_title, hr_id, username, score in shortlisted_data:
                print(f"  • Job {job_id} ({job_title}) - HR {hr_id}: {username} ({score:.1f}%)")
        
        # Show URLs to access
        print(f"\n3. 🌐 URLs to Access Candidates:")
        for hr_user in hr_users:
            if hr_user.hr_profile:
                job_drives = JobDrive.query.filter_by(hr_id=hr_user.hr_profile.id).all()
                for drive in job_drives:
                    print(f"  • {hr_user.username} - {drive.title}:")
                    print(f"    http://127.0.0.1:5002/hr/drive/{drive.id}/candidates")

if __name__ == '__main__':
    debug_hr_candidates()