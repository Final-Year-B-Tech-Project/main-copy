#!/usr/bin/env python3
"""
Migrate to consolidated skills storage - one row per student
"""

from app import create_app, db
from app.models import StudentProfile, User
from app.resume_models import CandidateSkill, ParsedResume
import json
from datetime import datetime

def migrate_to_consolidated_skills():
    """Migrate existing skills to consolidated JSON format in student profiles"""
    
    app = create_app()
    with app.app_context():
        print("🔄 Migrating to Consolidated Skills Storage")
        print("=" * 60)
        
        # Add new columns to student_profile table
        columns_to_add = [
            "technical_skills TEXT",
            "soft_skills TEXT", 
            "parsed_contact TEXT",
            "parsed_education TEXT",
            "parsed_experience TEXT",
            "parsed_projects TEXT",
            "total_experience_years FLOAT",
            "skills_count INTEGER DEFAULT 0",
            "parsing_confidence FLOAT",
            "last_parsed_at DATETIME"
        ]
        
        for column in columns_to_add:
            try:
                db.engine.execute(f"ALTER TABLE student_profile ADD COLUMN {column};")
                print(f"✅ Added {column.split()[0]} column")
            except:
                print(f"ℹ️  {column.split()[0]} column already exists")
        
        # Migrate existing skills data
        print("\n📊 Migrating Existing Skills Data...")
        
        students = StudentProfile.query.all()
        migrated_count = 0
        
        for student in students:
            print(f"\n👤 Processing student {student.id}...")
            
            # Get existing skills from CandidateSkill table
            existing_skills = CandidateSkill.query.filter_by(student_id=student.id).all()
            
            if existing_skills:
                # Convert to consolidated format
                skills_data = []
                technical_skills = []
                soft_skills = []
                
                for skill in existing_skills:
                    skill_dict = {
                        'skill_name': skill.skill_name,
                        'skill_category': skill.skill_category or 'technical',
                        'skill_type': skill.skill_type or 'general',
                        'proficiency_level': skill.proficiency_level or 'beginner',
                        'years_experience': skill.years_experience or 0,
                        'confidence_score': skill.confidence_score or 0.8,
                        'extracted_from': skill.extracted_from or 'resume'
                    }
                    
                    skills_data.append(skill_dict)
                    
                    if skill.skill_category == 'technical':
                        technical_skills.append(skill_dict)
                    else:
                        soft_skills.append(skill_dict)
                
                # Update student profile
                student.skills = json.dumps(skills_data)
                student.technical_skills = json.dumps(technical_skills)
                student.soft_skills = json.dumps(soft_skills)
                student.skills_count = len(skills_data)
                student.parsing_confidence = 0.85
                student.last_parsed_at = datetime.utcnow()
                
                print(f"  ✅ Migrated {len(skills_data)} skills")
                migrated_count += 1
            
            # Migrate parsed resume data if exists
            parsed_resume = ParsedResume.query.filter_by(student_id=student.id).first()
            if parsed_resume:
                student.parsed_contact = json.dumps({
                    'email': parsed_resume.email,
                    'phone': parsed_resume.phone,
                    'linkedin_url': parsed_resume.linkedin_url
                })
                student.parsed_education = parsed_resume.education_data
                student.parsed_experience = parsed_resume.experience_data
                student.parsed_projects = parsed_resume.projects_data
                student.total_experience_years = parsed_resume.total_experience_years
                
                print(f"  ✅ Migrated resume data")
        
        db.session.commit()
        
        print(f"\n🎉 Migration Complete!")
        print(f"📊 Students migrated: {migrated_count}")
        print(f"📋 Total students: {len(students)}")

if __name__ == '__main__':
    migrate_to_consolidated_skills()