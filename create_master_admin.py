#!/usr/bin/env python3
"""
Create master admin user for the AI Interview System.
"""

import sqlite3
import hashlib
from pathlib import Path

def create_master_admin():
    """Create master admin user in database."""
    
    print("Creating Master Admin User...")
    
    # Database path
    db_path = Path("ai_interview_system/Backend Files/instance/interview_system.db")
    
    if not db_path.exists():
        print("Database not found. Please run the system first to create the database.")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if master admin already exists
    cursor.execute("SELECT * FROM user WHERE username = ?", ('adminsuyash',))
    if cursor.fetchone():
        print("Master admin already exists!")
        conn.close()
        return True
    
    # Hash password
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Add missing columns first
    try:
        cursor.execute('ALTER TABLE user ADD COLUMN role VARCHAR(50) DEFAULT "user"')
        cursor.execute('ALTER TABLE user ADD COLUMN permissions TEXT')
    except:
        pass  # Columns might already exist
    
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
    
    print("Master Admin Created Successfully!")
    print("Username: adminsuyash")
    print("Password: adminsuyash")
    print("Role: master_admin")
    print("Access: /admin/dashboard")
    
    return True

if __name__ == '__main__':
    create_master_admin()