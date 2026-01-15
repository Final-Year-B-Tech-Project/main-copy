#!/usr/bin/env python3
"""
Simple database fix without imports
"""

import sqlite3
import os

def fix_db():
    """Simple database fix"""
    db_path = 'interview_agent.db'
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Add notes column
            cursor.execute("ALTER TABLE interview_session ADD COLUMN notes TEXT")
            conn.commit()
            conn.close()
            print("✓ Database fixed - notes column added")
            
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("✓ Notes column already exists")
            else:
                print(f"Database error: {e}")
    else:
        print("Database file not found")

if __name__ == "__main__":
    fix_db()