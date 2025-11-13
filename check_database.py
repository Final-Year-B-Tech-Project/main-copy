#!/usr/bin/env python3
"""
Check database structure
"""

import sqlite3
from pathlib import Path

def check_database():
    """Check database structure."""
    
    db_path = Path("ai_interview_system/Backend Files/instance/interview_system.db")
    
    if not db_path.exists():
        print("Database not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check user table structure
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    
    print("User table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check if role and permissions columns exist
    column_names = [col[1] for col in columns]
    
    if 'role' not in column_names:
        print("Missing 'role' column - adding it...")
        cursor.execute('ALTER TABLE user ADD COLUMN role VARCHAR(50) DEFAULT "user"')
    
    if 'permissions' not in column_names:
        print("Missing 'permissions' column - adding it...")
        cursor.execute('ALTER TABLE user ADD COLUMN permissions TEXT')
    
    # Check users
    cursor.execute("SELECT username, user_type, role FROM user")
    users = cursor.fetchall()
    
    print("\nUsers in database:")
    for user in users:
        print(f"  {user[0]} - {user[1]} - {user[2] if user[2] else 'None'}")
    
    conn.commit()
    conn.close()
    
    print("\nDatabase check complete!")

if __name__ == '__main__':
    check_database()