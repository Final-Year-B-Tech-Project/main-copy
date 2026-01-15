#!/usr/bin/env python3
"""
Database Migration Script - Add notes column to InterviewSession
"""

import sqlite3
import os

def migrate_database():
    """Add notes column to interview_session table if it doesn't exist"""
    
    db_path = 'interview_agent.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Creating new database...")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if notes column exists
        cursor.execute("PRAGMA table_info(interview_session)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'notes' not in columns:
            print("Adding 'notes' column to interview_session table...")
            cursor.execute("ALTER TABLE interview_session ADD COLUMN notes TEXT")
            conn.commit()
            print("✓ Successfully added 'notes' column")
        else:
            print("✓ 'notes' column already exists")
        
        conn.close()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_database()