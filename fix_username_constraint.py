#!/usr/bin/env python3
"""
Fix Username Constraint Script
Removes unique constraint from email and ensures username is unique across all user types
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.join(os.path.dirname(__file__), 'ai_interview_system', 'Backend Files')
sys.path.insert(0, project_dir)

def fix_database_constraints():
    """Fix database constraints for username uniqueness"""
    db_path = os.path.join(project_dir, 'instance', 'interview_agent.db')
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Fixing database constraints...")
        
        # Check current schema
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        print(f"Current user table columns: {len(columns)}")
        
        # Check for duplicate usernames across different user types
        cursor.execute("""
            SELECT username, COUNT(*) as count, GROUP_CONCAT(user_type) as types
            FROM user 
            GROUP BY username 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"Found {len(duplicates)} duplicate usernames:")
            for username, count, types in duplicates:
                print(f"   - '{username}' appears {count} times in types: {types}")
            
            # Fix duplicates by appending user type to username
            for username, count, types in duplicates:
                cursor.execute("SELECT id, username, user_type FROM user WHERE username = ?", (username,))
                users = cursor.fetchall()
                
                # Keep the first one as is, modify others
                for i, (user_id, orig_username, user_type) in enumerate(users[1:], 1):
                    new_username = f"{orig_username}_{user_type}"
                    cursor.execute("UPDATE user SET username = ? WHERE id = ?", (new_username, user_id))
                    print(f"   Updated user {user_id}: '{orig_username}' -> '{new_username}'")
        
        # Drop the new table if it exists
        cursor.execute("DROP TABLE IF EXISTS user_new")
        
        # Create new table with correct constraints
        cursor.execute("""
            CREATE TABLE user_new (
                id INTEGER PRIMARY KEY,
                email VARCHAR(120) NOT NULL,
                username VARCHAR(80) UNIQUE NOT NULL,
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
        """)
        
        # Copy data to new table with proper column mapping
        cursor.execute("""
            INSERT INTO user_new (id, email, username, password_hash, user_type, role, permissions, 
                                 first_name, last_name, phone, date_of_birth, profile_photo, 
                                 is_active, created_at, updated_at, last_login)
            SELECT id, email, username, password_hash, user_type, 
                   COALESCE(role, 'user') as role,
                   permissions,
                   COALESCE(first_name, 'Unknown') as first_name,
                   COALESCE(last_name, 'User') as last_name,
                   phone, date_of_birth, profile_photo,
                   COALESCE(is_active, 1) as is_active,
                   COALESCE(created_at, datetime('now')) as created_at,
                   COALESCE(updated_at, datetime('now')) as updated_at,
                   last_login
            FROM user
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE user")
        cursor.execute("ALTER TABLE user_new RENAME TO user")
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_email ON user (email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_username ON user (username)")
        
        # Commit changes
        conn.commit()
        
        print("Database constraints fixed successfully!")
        print("   - Email: No longer unique (allows same email for different user types)")
        print("   - Username: Unique across all user types")
        
        # Verify the fix
        cursor.execute("SELECT COUNT(DISTINCT username) as unique_usernames, COUNT(*) as total_users FROM user")
        unique_usernames, total_users = cursor.fetchone()
        print(f"Verification: {unique_usernames} unique usernames for {total_users} total users")
        
        if unique_usernames == total_users:
            print("All usernames are now unique!")
        else:
            print("Still have duplicate usernames!")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error fixing database constraints: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def main():
    """Main function"""
    print("Starting Username Constraint Fix...")
    print("=" * 50)
    
    if fix_database_constraints():
        print("\nUsername constraint fix completed successfully!")
        print("\nNow you can:")
        print("1. Use same email for different user types (student, hr, admin)")
        print("2. Usernames must be unique across all user types")
        print("3. Custom fullscreen security system is active")
    else:
        print("\nUsername constraint fix failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())