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
        try:
            db.engine.execute("""
                ALTER TABLE student_profile ADD COLUMN technical_skills TEXT;
            """)
            print("✅ Added technical_skills column")
        except:
            print("ℹ️  technical_skills column already exists")
        
        try:
            db.engine.execute("""
                ALTER TABLE student_profile ADD COLUMN soft_skills TEXT;
            """)
            print("✅ Added soft_skills column")
        except:
            print("ℹ️  soft_skills column already exists")
        
        try:
            db.engine.execute("""
                ALTER TABLE student_profile ADD COLUMN parsed_contact TEXT;
            """)
            print("✅ Added parsed_contact column")
        except:
            print("ℹ️  parsed_contact column already exists")
        
        try:
            db.engine.execute("""
                ALTER TABLE student_profile ADD COLUMN parsed_education TEXT;
            """)
            print("✅ Added parsed_education column")
        except:
            print("ℹ️  parsed_education column already exists")
        
        try:
            db.engine.execute("""
                ALTER TABLE student_profile ADD COLUMN parsed_experience TEXT;
            """)
            print("✅ Added parsed_experience column")
        except:
            print("ℹ️  parsed_experience column already exists")
        
        try:
            db.engine.execute("""
                ALTER TABLE student_profile ADD COLUMN parsed_projects TEXT;
            """)
            print("✅ Added parsed_projects column")
        except:
            print("ℹ️  parsed_projects column already exists")
        
        try:
            db.engine.execute("""
                ALTER TABLE student_profile ADD COLUMN total_experience_years FLOAT;
            """)
            print("✅ Added total_experience_years column")
        except:
            print("ℹ️  total_experience_years column already exists")
        
        try:
            db.engine.execute("""
                ALTER TABLE student_profile ADD COLUMN skills_count INTEGER DEFAULT 0;
            """)
            print("✅ Added skills_count column")
        except:
            print("ℹ️  skills_count column already exists")
        
        try:
            db.engine.execute("""
                ALTER TABLE student_profile ADD COLUMN parsing_confidence FLOAT;
            """)
            print("✅ Added parsing_confidence column")
        except:
            print("ℹ️  parsing_confidence column already exists")
        
        try:
            db.engine.execute("""
                ALTER TABLE student_profile ADD COLUMN last_parsed_at DATETIME;
            """)
            print("✅ Added last_parsed_at column")
        except:
            print("ℹ️  last_parsed_at column already exists")
        
        # Migrate existing skills data
        print("\\n📊 Migrating Existing Skills Data...")
        
        students = StudentProfile.query.all()
        migrated_count = 0
        
        for student in students:\n            print(f\"\\n👤 Processing student {student.id}...\")\n            \n            # Get existing skills from CandidateSkill table\n            existing_skills = CandidateSkill.query.filter_by(student_id=student.id).all()\n            \n            if existing_skills:\n                # Convert to consolidated format\n                skills_data = []\n                technical_skills = []\n                soft_skills = []\n                \n                for skill in existing_skills:\n                    skill_dict = {\n                        'skill_name': skill.skill_name,\n                        'skill_category': skill.skill_category or 'technical',\n                        'skill_type': skill.skill_type or 'general',\n                        'proficiency_level': skill.proficiency_level or 'beginner',\n                        'years_experience': skill.years_experience or 0,\n                        'confidence_score': skill.confidence_score or 0.8,\n                        'extracted_from': skill.extracted_from or 'resume'\n                    }\n                    \n                    skills_data.append(skill_dict)\n                    \n                    if skill.skill_category == 'technical':\n                        technical_skills.append(skill_dict)\n                    else:\n                        soft_skills.append(skill_dict)\n                \n                # Update student profile\n                student.skills = json.dumps(skills_data)\n                student.technical_skills = json.dumps(technical_skills)\n                student.soft_skills = json.dumps(soft_skills)\n                student.skills_count = len(skills_data)\n                student.parsing_confidence = 0.85\n                student.last_parsed_at = datetime.utcnow()\n                \n                print(f\"  ✅ Migrated {len(skills_data)} skills ({len(technical_skills)} technical, {len(soft_skills)} soft)\")\n                migrated_count += 1\n            \n            # Migrate parsed resume data if exists\n            parsed_resume = ParsedResume.query.filter_by(student_id=student.id).first()\n            if parsed_resume:\n                student.parsed_contact = json.dumps({\n                    'email': parsed_resume.email,\n                    'phone': parsed_resume.phone,\n                    'linkedin_url': parsed_resume.linkedin_url\n                })\n                student.parsed_education = parsed_resume.education_data\n                student.parsed_experience = parsed_resume.experience_data\n                student.parsed_projects = parsed_resume.projects_data\n                student.total_experience_years = parsed_resume.total_experience_years\n                \n                print(f\"  ✅ Migrated resume data (experience: {parsed_resume.total_experience_years} years)\")\n        \n        db.session.commit()\n        \n        print(f\"\\n🎉 Migration Complete!\")\n        print(f\"📊 Students migrated: {migrated_count}\")\n        print(f\"📋 Total students: {len(students)}\")\n        \n        # Show sample of migrated data\n        print(f\"\\n📋 Sample Migrated Data:\")\n        for student in students[:2]:\n            user = User.query.get(student.user_id)\n            if student.skills:\n                skills_data = json.loads(student.skills)\n                print(f\"  • {user.username}: {len(skills_data)} skills consolidated\")\n                for skill in skills_data[:3]:\n                    print(f\"    - {skill['skill_name']} ({skill['proficiency_level']})\")\n\nif __name__ == '__main__':\n    migrate_to_consolidated_skills()