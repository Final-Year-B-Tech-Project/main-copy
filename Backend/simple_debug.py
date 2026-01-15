#!/usr/bin/env python3
"""
Simple debug for HR candidates view
"""

from app import create_app, db

def simple_debug():
    """Simple debug of HR candidates"""
    
    app = create_app()
    with app.app_context():
        print("🔍 HR Candidates Debug")
        print("=" * 40)
        
        with db.engine.connect() as conn:
            # Check HR users and their job drives
            print("1. HR Users:")
            hr_data = conn.execute(db.text("""
                SELECT u.id, u.username, hp.id as hr_profile_id
                FROM user u
                JOIN hr_profile hp ON u.id = hp.user_id
                WHERE u.user_type = 'hr'
            """)).fetchall()
            
            for user_id, username, hr_profile_id in hr_data:
                print(f"  • {username} (User ID: {user_id}, HR Profile: {hr_profile_id})")
                
                # Get job drives for this HR
                jobs = conn.execute(db.text("""
                    SELECT id, title, is_active
                    FROM job_drive
                    WHERE hr_id = :hr_id
                """), {'hr_id': hr_profile_id}).fetchall()
                
                for job_id, title, is_active in jobs:
                    print(f"    Job {job_id}: {title} (Active: {is_active})")
                    
                    # Get shortlisted candidates
                    candidates = conn.execute(db.text("""
                        SELECT u2.username, cs.overall_score, cs.skill_match_score
                        FROM candidate_score cs
                        JOIN student_profile sp ON cs.student_id = sp.id
                        JOIN user u2 ON sp.user_id = u2.id
                        WHERE cs.job_drive_id = :job_id AND cs.is_shortlisted = 1
                        ORDER BY cs.overall_score DESC
                    """), {'job_id': job_id}).fetchall()
                    
                    print(f"      Shortlisted: {len(candidates)}")
                    for candidate_name, overall_score, skill_score in candidates:
                        print(f"        - {candidate_name}: {overall_score:.1f}% (Skills: {skill_score:.1f}%)")
            
            print(f"\n2. 🌐 Access URLs:")
            print(f"  Login as 'arin' (password: hr123 or admin123)")
            print(f"  Then go to: http://127.0.0.1:5002/hr/drives")
            print(f"  Click 'View Candidates' on any job drive")

if __name__ == '__main__':
    simple_debug()