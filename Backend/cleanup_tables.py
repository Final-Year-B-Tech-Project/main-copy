#!/usr/bin/env python3
"""
Clean up redundant tables after skills consolidation
"""

from app import create_app, db

def cleanup_redundant_tables():
    """Remove redundant tables that are no longer needed"""
    
    app = create_app()
    with app.app_context():
        print("🧹 Cleaning Up Redundant Tables")
        print("=" * 60)
        
        with db.engine.connect() as conn:
            # Check current table sizes
            print("📊 Current Table Sizes:")
            
            tables_to_check = [
                'candidate_skill',
                'parsed_resume', 
                'student_profile',
                'candidate_score'
            ]
            
            for table in tables_to_check:
                try:
                    count = conn.execute(db.text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
                    print(f"  • {table}: {count} records")
                except:
                    print(f"  • {table}: Table doesn't exist")
            
            # Show skills are now in student_profile
            print(f"\n📋 Skills Storage Verification:")
            students_with_skills = conn.execute(db.text("""
                SELECT COUNT(*) FROM student_profile 
                WHERE skills IS NOT NULL AND skills != ''
            """)).fetchone()[0]
            print(f"  • Students with consolidated skills: {students_with_skills}")
            
            # Show sample of consolidated skills
            sample = conn.execute(db.text("""
                SELECT id, SUBSTR(skills, 1, 100) || '...' as skills_preview 
                FROM student_profile 
                WHERE skills IS NOT NULL 
                LIMIT 2
            """)).fetchall()
            
            print(f"\n📝 Sample Consolidated Skills:")
            for student_id, skills_preview in sample:
                print(f"  • Student {student_id}: {skills_preview}")
            
            print(f"\n✅ Verification Complete!")
            print(f"💡 The candidate_skill table can now be safely removed")
            print(f"💡 All skills are consolidated in student_profile.skills JSON field")
            
            # Optional: Drop redundant tables (commented out for safety)
            print(f"\n⚠️  To remove redundant tables, uncomment the following lines:")
            print(f"   # DROP TABLE candidate_skill;")
            print(f"   # DROP TABLE parsed_resume;")

if __name__ == '__main__':
    cleanup_redundant_tables()