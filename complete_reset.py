#!/usr/bin/env python3
"""
Complete database reset with proper structure
"""

import sqlite3
import hashlib
import os
from pathlib import Path

def complete_reset():
    """Completely reset and recreate database."""
    
    print("Complete Database Reset...")
    
    # Database path
    db_path = Path("ai_interview_system/Backend Files/instance/interview_system.db")
    
    # Remove old database
    if db_path.exists():
        print("Removing old database...")
        db_path.unlink()
    
    # Create instance directory
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create new database
    print("Creating new database...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create user table with all columns
    cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(120) NOT NULL,
            username VARCHAR(80) NOT NULL UNIQUE,
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
        CREATE TABLE student_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            university VARCHAR(100),
            degree VARCHAR(100),
            graduation_year INTEGER,
            gpa FLOAT,
            skills TEXT,
            resume_file VARCHAR(255),
            resume_text TEXT,
            experience_level VARCHAR(20) DEFAULT 'fresher',
            preferred_roles TEXT,
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
            company_name VARCHAR(100) NOT NULL,
            company_website VARCHAR(255),
            company_description TEXT,
            department VARCHAR(100),
            position VARCHAR(100),
            employee_id VARCHAR(50),
            hr_code VARCHAR(20) UNIQUE NOT NULL,
            years_experience INTEGER,
            specializations TEXT,
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
    
    # Create interview_session table
    cursor.execute('''
        CREATE TABLE interview_session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_drive_id INTEGER,
            session_type VARCHAR(20) NOT NULL DEFAULT 'practice',
            status VARCHAR(20) DEFAULT 'scheduled',
            scheduled_time DATETIME,
            start_time DATETIME,
            end_time DATETIME,
            duration INTEGER,
            questions TEXT,
            responses TEXT,
            ai_feedback TEXT,
            hr_feedback TEXT,
            overall_score FLOAT,
            technical_score FLOAT,
            communication_score FLOAT,
            confidence_score FLOAT,
            coding_score FLOAT,
            interview_link VARCHAR(255),
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES user (id),
            FOREIGN KEY (job_drive_id) REFERENCES job_drive (id)
        )
    ''')
    
    # Hash password function
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Insert test student
    cursor.execute('''
        INSERT INTO user (email, username, password_hash, user_type, role, first_name, last_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('test@student.com', 'teststudent', hash_password('password123'), 'student', 'user', 'Test', 'Student'))
    
    student_id = cursor.lastrowid
    
    cursor.execute('''
        INSERT INTO student_profile (user_id, university, degree, experience_level)
        VALUES (?, ?, ?, ?)
    ''', (student_id, 'Test University', 'Computer Science', 'fresher'))
    
    # Insert test HR
    cursor.execute('''
        INSERT INTO user (email, username, password_hash, user_type, role, first_name, last_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('test@hr.com', 'testhr', hash_password('password123'), 'hr', 'user', 'Test', 'HR'))
    
    hr_user_id = cursor.lastrowid
    
    cursor.execute('''
        INSERT INTO hr_profile (user_id, hr_code, company_name, department)
        VALUES (?, ?, ?, ?)
    ''', (hr_user_id, 'HR001', 'Test Company', 'Engineering'))
    
    # Insert master admin
    cursor.execute('''
        INSERT INTO user (email, username, password_hash, user_type, role, first_name, last_name, permissions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'admin@aiinterview.com',
        'adminsuyash', 
        hash_password('adminsuyash'),
        'admin',
        'master_admin',
        'Suyash',
        'Master Admin',
        '["all"]'
    ))
    
    conn.commit()
    conn.close()
    
    print("Database reset complete!")
    print("\nTest Login Credentials:")
    print("  Student: test@student.com / password123")
    print("  HR: test@hr.com / password123")
    print("  Master Admin: adminsuyash / adminsuyash")
    print("\nAdmin Panel: http://127.0.0.1:5000/admin/dashboard")
    
    return True

if __name__ == '__main__':
    complete_reset()