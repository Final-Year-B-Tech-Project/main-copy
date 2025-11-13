#!/usr/bin/env python3
"""
Create minimal database
"""

import sqlite3

def create_db():
    """Create minimal database with required tables"""
    
    conn = sqlite3.connect('interview_agent.db')
    cursor = conn.cursor()
    
    # Create user table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            email VARCHAR(120) NOT NULL,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            user_type VARCHAR(20) NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            permissions TEXT,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            phone VARCHAR(20),
            date_of_birth DATE,
            profile_photo VARCHAR(255),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')
    
    # Create student_profile table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_profile (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE,
            university VARCHAR(100),
            degree VARCHAR(100),
            graduation_year INTEGER,
            gpa REAL,
            skills TEXT,
            resume_file VARCHAR(255),
            resume_text TEXT,
            experience_level VARCHAR(20),
            preferred_roles TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    
    # Create hr_profile table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hr_profile (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE,
            company_name VARCHAR(100) NOT NULL,
            company_website VARCHAR(255),
            company_description TEXT,
            department VARCHAR(100),
            position VARCHAR(100),
            employee_id VARCHAR(50),
            hr_code VARCHAR(20) UNIQUE,
            years_experience INTEGER,
            specializations TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    
    # Create job_drive table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_drive (
            id INTEGER PRIMARY KEY,
            hr_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            job_role VARCHAR(100) NOT NULL,
            experience_required VARCHAR(50),
            skills_required TEXT,
            number_of_positions INTEGER DEFAULT 1,
            location VARCHAR(100),
            salary_range VARCHAR(100),
            deadline DATETIME,
            is_active BOOLEAN DEFAULT 1,
            interview_questions TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hr_id) REFERENCES hr_profile (id)
        )
    ''')
    
    # Create interview_session table with notes column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interview_session (
            id INTEGER PRIMARY KEY,
            candidate_id INTEGER NOT NULL,
            job_drive_id INTEGER,
            session_type VARCHAR(20) NOT NULL,
            status VARCHAR(20) DEFAULT 'scheduled',
            scheduled_time DATETIME,
            start_time DATETIME,
            end_time DATETIME,
            duration INTEGER,
            questions TEXT,
            responses TEXT,
            ai_feedback TEXT,
            hr_feedback TEXT,
            overall_score REAL,
            technical_score REAL,
            communication_score REAL,
            confidence_score REAL,
            coding_score REAL,
            interview_link VARCHAR(255),
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES user (id),
            FOREIGN KEY (job_drive_id) REFERENCES job_drive (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created successfully with all tables including notes column")

if __name__ == "__main__":
    create_db()