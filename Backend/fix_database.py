#!/usr/bin/env python3
"""
Database fix script to add missing notes column and ensure proper schema
"""
import os
import sqlite3
from datetime import datetime

def fix_database():
    """Fix database schema by adding missing columns"""
    db_path = 'interview_agent.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if notes column exists
        cursor.execute("PRAGMA table_info(interview_session)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'notes' not in columns:
            print("Adding missing 'notes' column to interview_session table...")
            cursor.execute("ALTER TABLE interview_session ADD COLUMN notes TEXT")
            conn.commit()
            print("[SUCCESS] Added notes column successfully")
        else:
            print("[INFO] Notes column already exists")
        
        # Verify the fix
        cursor.execute("SELECT COUNT(*) FROM interview_session")
        count = cursor.fetchone()[0]
        print(f"[SUCCESS] Database verified - {count} interview sessions found")
        
        conn.close()
        print("[SUCCESS] Database fix completed successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database fix failed: {e}")
        return False

if __name__ == '__main__':
    fix_database()