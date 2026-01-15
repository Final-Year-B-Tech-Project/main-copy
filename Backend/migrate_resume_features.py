#!/usr/bin/env python3
"""
Migration script to add resume parsing and candidate scoring tables
"""

from app import create_app, db
from app.resume_models import CandidateSkill, ParsedResume, JobRequirement, CandidateScore, ResumeParsingLog

def migrate_database():
    """Add new tables for resume parsing features"""
    app = create_app()
    with app.app_context():
        print("🔄 Starting database migration...")
        
        try:
            # Create all new tables
            db.create_all()
            print("✅ New tables created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            new_tables = [
                'candidate_skill',
                'parsed_resume', 
                'job_requirement',
                'candidate_score',
                'resume_parsing_log'
            ]
            
            print("\n📊 Table Status:")
            for table in new_tables:
                if table in existing_tables:
                    print(f"✅ {table} - Created")
                else:
                    print(f"❌ {table} - Failed")
            
            print(f"\n📈 Total tables in database: {len(existing_tables)}")
            
            # Add sample job requirements for existing job drives
            from app.models import JobDrive
            job_drives = JobDrive.query.all()
            
            for job in job_drives:
                existing_req = JobRequirement.query.filter_by(job_drive_id=job.id).first()
                if not existing_req:
                    # Create sample requirements
                    sample_req = JobRequirement(
                        job_drive_id=job.id,
                        required_skills='[{"skill": "Python", "importance": "required", "min_proficiency": "intermediate"}]',
                        preferred_skills='[{"skill": "Django", "importance": "preferred", "min_proficiency": "beginner"}]',
                        min_experience_years=1.0,
                        max_experience_years=5.0,
                        experience_level='mid',
                        min_degree_level='bachelor',
                        location_type='hybrid'
                    )
                    db.session.add(sample_req)
            
            db.session.commit()
            print("✅ Sample job requirements added!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_database()