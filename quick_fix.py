#!/usr/bin/env python3
"""
Quick database fix - run this from the Backend Files directory
"""

import os
import sqlite3
from pathlib import Path

def fix_database():
    """Fix the database by recreating it with proper structure."""
    
    print("Quick Database Fix...")
    
    # Database path
    db_path = Path("ai_interview_system/Backend Files/instance/interview_system.db")
    
    # Create instance directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove old database if exists
    if db_path.exists():
        print("Removing old database...")
        db_path.unlink()
    
    # Create new database with basic structure
    print("Creating new database...")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(120) NOT NULL,
            username VARCHAR(80) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            user_type VARCHAR(20) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            phone VARCHAR(20),
            profile_photo VARCHAR(255),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')
    
    # Create student_profile table
    cursor.execute('''
        CREATE TABLE student_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            university VARCHAR(100),
            degree VARCHAR(100),
            graduation_year INTEGER,
            gpa FLOAT,
            skills TEXT,
            experience_level VARCHAR(20) DEFAULT 'fresher',
            resume_file VARCHAR(255),
            resume_text TEXT,
            github_url VARCHAR(255),
            linkedin_url VARCHAR(255),
            portfolio_url VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    
    # Create hr_profile table
    cursor.execute('''
        CREATE TABLE hr_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            hr_code VARCHAR(20) UNIQUE NOT NULL,
            company_name VARCHAR(100) NOT NULL,
            company_website VARCHAR(255),
            company_description TEXT,
            department VARCHAR(100),
            position VARCHAR(100),
            years_experience INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    
    # Create job_drive table
    cursor.execute('''
        CREATE TABLE job_drive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hr_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            job_role VARCHAR(100),
            experience_required VARCHAR(50),
            skills_required TEXT,
            number_of_positions INTEGER DEFAULT 1,
            location VARCHAR(100),
            salary_range VARCHAR(100),
            deadline DATETIME,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hr_id) REFERENCES hr_profile (id)
        )
    ''')
    
    # Create interview_session table
    cursor.execute('''
        CREATE TABLE interview_session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_drive_id INTEGER,
            session_type VARCHAR(20) DEFAULT 'practice',
            status VARCHAR(20) DEFAULT 'scheduled',
            interview_link VARCHAR(255),
            scheduled_time DATETIME,
            start_time DATETIME,
            end_time DATETIME,
            duration INTEGER,
            questions TEXT,
            responses TEXT,
            ai_feedback TEXT,
            overall_score INTEGER,
            technical_score INTEGER,
            communication_score INTEGER,
            confidence_score INTEGER,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES user (id),
            FOREIGN KEY (job_drive_id) REFERENCES job_drive (id)
        )
    ''')
    
    # Create test users with hashed passwords
    import hashlib
    
    # Hash password function (simple version)
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Insert test student
    cursor.execute('''
        INSERT INTO user (email, username, password_hash, user_type, first_name, last_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('test@student.com', 'teststudent', hash_password('password123'), 'student', 'Test', 'Student'))
    
    student_id = cursor.lastrowid
    
    cursor.execute('''
        INSERT INTO student_profile (user_id, university, degree, experience_level)
        VALUES (?, ?, ?, ?)
    ''', (student_id, 'Test University', 'Computer Science', 'fresher'))
    
    # Insert test HR
    cursor.execute('''
        INSERT INTO user (email, username, password_hash, user_type, first_name, last_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('test@hr.com', 'testhr', hash_password('password123'), 'hr', 'Test', 'HR'))
    
    hr_user_id = cursor.lastrowid
    
    cursor.execute('''
        INSERT INTO hr_profile (user_id, hr_code, company_name, department)
        VALUES (?, ?, ?, ?)
    ''', (hr_user_id, 'HR001', 'Test Company', 'Engineering'))
    
    conn.commit()
    conn.close()
    
    print("Database created successfully!")
    print("\nTest Login Credentials:")
    print("  Student: test@student.com / password123")
    print("  HR: test@hr.com / password123")
    print("\nNote: This uses simple password hashing. The app will need to be updated to use this format.")
    
    return True

if __name__ == '__main__':
    fix_database()
    print("\nQuick fix complete! Try logging in now.")