#!/usr/bin/env python3
"""
Migrate database to add missing columns
"""

import sqlite3
import hashlib
from pathlib import Path

def migrate_database():
    """Add missing columns to existing database."""
    
    print("Migrating database...")
    
    # Database path
    db_path = Path("ai_interview_system/Backend Files/instance/interview_system.db")
    
    if not db_path.exists():
        print("Database not found!")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Add missing columns to user table
        print("Adding role column...")
        cursor.execute('ALTER TABLE user ADD COLUMN role VARCHAR(50) DEFAULT "user"')
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Role column already exists")
        else:
            print(f"Error adding role column: {e}")
    
    try:
        print("Adding permissions column...")
        cursor.execute('ALTER TABLE user ADD COLUMN permissions TEXT')
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Permissions column already exists")
        else:
            print(f"Error adding permissions column: {e}")
    
    # Check if master admin exists
    cursor.execute("SELECT * FROM user WHERE username = ?", ('adminsuyash',))
    if not cursor.fetchone():
        print("Creating master admin...")
        
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()
        
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
        print("Master admin created!")
    else:
        print("Master admin already exists")
    
    conn.commit()
    conn.close()
    
    print("Database migration complete!")
    return True

if __name__ == '__main__':
    migrate_database()