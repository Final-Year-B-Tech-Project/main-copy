#!/usr/bin/env python3
"""
Database Migration Script
Fix missing columns in student_profile table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
import sqlite3

def migrate_database():
    """Fix database schema issues"""
    
    app = create_app()
    with app.app_context():
        print("🔧 Migrating database schema...")
        
        # Get database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(f"Database path: {db_path}")
        
        # Connect directly to SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check existing columns
            cursor.execute("PRAGMA table_info(student_profile)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            print(f"Existing columns: {existing_columns}")
            
            # Add missing columns if they don't exist
            missing_columns = [
                ('technical_skills', 'TEXT'),
                ('soft_skills', 'TEXT'),
                ('resume_file', 'VARCHAR(255)'),
                ('resume_text', 'TEXT'),
                ('parsed_contact', 'TEXT'),
                ('parsed_education', 'TEXT'),
                ('parsed_experience', 'TEXT'),
                ('parsed_projects', 'TEXT'),
                ('experience_level', 'VARCHAR(20)'),
                ('total_experience_years', 'FLOAT'),
                ('preferred_roles', 'TEXT'),
                ('skills_count', 'INTEGER DEFAULT 0'),
                ('parsing_confidence', 'FLOAT'),
                ('last_parsed_at', 'DATETIME')
            ]
            
            for column_name, column_type in missing_columns:
                if column_name not in existing_columns:
                    print(f"Adding column: {column_name}")
                    cursor.execute(f"ALTER TABLE student_profile ADD COLUMN {column_name} {column_type}")
            
            # Create missing tables
            print("Creating missing tables...")
            
            # CandidateSkill table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS candidate_skill (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    skill_name VARCHAR(100) NOT NULL,
                    skill_category VARCHAR(50),
                    skill_type VARCHAR(50),
                    proficiency_level VARCHAR(20),
                    years_experience FLOAT,
                    extracted_from VARCHAR(20),
                    confidence_score FLOAT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES student_profile(id)
                )
            ''')
            
            # ParsedResume table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parsed_resume (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    email VARCHAR(120),
                    phone VARCHAR(20),
                    linkedin_url VARCHAR(255),
                    location VARCHAR(100),
                    education_data TEXT,
                    experience_data TEXT,
                    total_experience_years FLOAT,
                    projects_data TEXT,
                    parsing_confidence FLOAT,
                    parsing_errors TEXT,
                    parsed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES student_profile(id)
                )
            ''')
            
            # JobRequirement table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_requirement (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_drive_id INTEGER NOT NULL,
                    required_skills TEXT,
                    preferred_skills TEXT,
                    min_experience_years FLOAT,
                    max_experience_years FLOAT,
                    experience_level VARCHAR(20),
                    min_degree_level VARCHAR(50),
                    preferred_degrees TEXT,
                    min_gpa FLOAT,
                    location_type VARCHAR(20),
                    max_notice_period INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_drive_id) REFERENCES job_drive(id)
                )
            ''')
            
            # CandidateScore table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS candidate_score (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    job_drive_id INTEGER NOT NULL,
                    skill_match_score FLOAT,
                    experience_score FLOAT,
                    education_score FLOAT,
                    other_score FLOAT,
                    overall_score FLOAT,
                    is_eligible BOOLEAN DEFAULT 0,
                    is_shortlisted BOOLEAN DEFAULT 0,
                    skill_matches TEXT,
                    missing_skills TEXT,
                    score_breakdown TEXT,
                    shortlist_reason TEXT,
                    shortlisted_at DATETIME,
                    scored_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES student_profile(id),
                    FOREIGN KEY (job_drive_id) REFERENCES job_drive(id)
                )
            ''')
            
            # ResumeParsingLog table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resume_parsing_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    file_name VARCHAR(255),
                    file_size INTEGER,
                    file_type VARCHAR(20),
                    parsing_status VARCHAR(20),
                    skills_extracted INTEGER DEFAULT 0,
                    sections_parsed TEXT,
                    processing_time FLOAT,
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES student_profile(id)
                )
            ''')
            
            conn.commit()
            print("✅ Database migration completed successfully!")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Migration error: {e}")
            return False
        finally:
            conn.close()
        
        return True

if __name__ == '__main__':
    success = migrate_database()
    if success:
        print("\n🎉 Database migration completed!")
    else:
        print("\n❌ Migration failed.")