#!/usr/bin/env python3
"""
Quick fix for database and system issues
"""

import sqlite3
import os
from app import create_app, db

def fix_database():
    """Fix database issues"""
    
    # Check if database exists
    db_path = 'interview_agent.db'
    
    if os.path.exists(db_path):
        try:
            # Add notes column if missing
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if notes column exists
            cursor.execute("PRAGMA table_info(interview_session)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'notes' not in columns:
                print("Adding notes column...")
                cursor.execute("ALTER TABLE interview_session ADD COLUMN notes TEXT")
                conn.commit()
                print("✓ Notes column added")
            else:
                print("✓ Notes column already exists")
            
            conn.close()
            
        except Exception as e:
            print(f"Database fix error: {e}")
            # Recreate database if corrupted
            print("Recreating database...")
            if os.path.exists(db_path):
                os.remove(db_path)
            
            app = create_app()
            with app.app_context():
                db.create_all()
                print("✓ Database recreated")
    else:
        # Create new database
        print("Creating new database...")
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✓ Database created")

if __name__ == "__main__":
    fix_database()