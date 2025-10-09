#!/usr/bin/env python3
"""Database migration script to add role and permissions columns."""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add role and permissions columns to existing database."""
    db_path = os.path.join('instance', 'interview_agent.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Will be created on next app start.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add role column if it doesn't exist
        if 'role' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN role TEXT DEFAULT 'user'")
            print("Added 'role' column")
        
        # Add permissions column if it doesn't exist
        if 'permissions' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN permissions TEXT")
            print("Added 'permissions' column")
        
        # Update existing users with default roles
        cursor.execute("""
            UPDATE user 
            SET role = CASE 
                WHEN user_type = 'master_admin' THEN 'master_admin'
                WHEN user_type = 'admin' THEN 'admin'
                ELSE 'user'
            END
            WHERE role IS NULL OR role = ''
        """)
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()