#!/usr/bin/env python3
"""
Consolidate existing skills into single JSON field per student
"""

from app import create_app, db
import json

def consolidate_skills():
    """Consolidate existing skills into student profile skills field"""
    
    app = create_app()
    with app.app_context():
        print("🔄 Consolidating Skills into Single Row per Student")
        print("=" * 60)
        
        # Use raw SQL to avoid model conflicts
        with db.engine.connect() as conn:
            students = conn.execute(db.text("SELECT id, user_id FROM student_profile")).fetchall()
            print(f"📊 Found {len(students)} students")
            
            for student_id, user_id in students:
                print(f"\n👤 Processing student {student_id}...")
                
                # Get existing skills
                skills_query = db.text("""
                    SELECT skill_name, skill_category, skill_type, proficiency_level, 
                           years_experience, confidence_score, extracted_from
                    FROM candidate_skill 
                    WHERE student_id = :student_id
                """)
                existing_skills = conn.execute(skills_query, {'student_id': student_id}).fetchall()
                
                if existing_skills:
                    # Convert to consolidated format
                    skills_data = []
                    technical_count = 0
                    soft_count = 0
                    
                    for skill in existing_skills:
                        skill_dict = {
                            'skill_name': skill[0],
                            'skill_category': skill[1] or 'technical',
                            'skill_type': skill[2] or 'general',
                            'proficiency_level': skill[3] or 'beginner',
                            'years_experience': skill[4] or 0,
                            'confidence_score': skill[5] or 0.8,
                            'extracted_from': skill[6] or 'resume'
                        }
                        
                        skills_data.append(skill_dict)
                        
                        if skill[1] == 'technical':
                            technical_count += 1
                        else:
                            soft_count += 1
                    
                    # Update student profile with consolidated skills
                    skills_json = json.dumps(skills_data)
                    update_query = db.text("""
                        UPDATE student_profile 
                        SET skills = :skills_json 
                        WHERE id = :student_id
                    """)
                    conn.execute(update_query, {'skills_json': skills_json, 'student_id': student_id})
                    conn.commit()
                    
                    print(f"  ✅ Consolidated {len(skills_data)} skills ({technical_count} technical, {soft_count} soft)")
                else:
                    print(f"  ℹ️  No skills found for student {student_id}")
            
            # Verify consolidation
            print(f"\n📊 Verification:")
            verification = conn.execute(db.text("""
                SELECT COUNT(*) as students_with_skills 
                FROM student_profile 
                WHERE skills IS NOT NULL AND skills != ''
            """)).fetchone()
            
            print(f"  • Students with consolidated skills: {verification[0]}")
        
        print(f"\n🎉 Consolidation Complete!")
        print(f"📋 All skills are now stored as JSON in student_profile.skills field")

if __name__ == '__main__':
    consolidate_skills()