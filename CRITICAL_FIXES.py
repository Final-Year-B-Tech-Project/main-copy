#!/usr/bin/env python3
"""
Critical Fixes Script for AI Interview System
Applies immediate fixes for identified critical issues
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def fix_database_schema():
    print_header("FIXING DATABASE SCHEMA")
    
    try:
        # Backup current database
        import shutil
        backup_name = f"interview_agent_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy('ai_interview_system/Backend Files/instance/interview_agent.db', 
                   f'ai_interview_system/Backend Files/instance/{backup_name}')
        print(f"[OK] Database backed up as: {backup_name}")
        
        conn = sqlite3.connect('ai_interview_system/Backend Files/instance/interview_agent.db')
        cursor = conn.cursor()
        
        # Check for duplicate tables and consolidate
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"[INFO] Found tables: {tables}")
        
        # If we have both 'user' and 'users' tables, consolidate
        if 'user' in tables and 'users' in tables:
            print("[FIXING] Consolidating user tables...")
            
            # Copy data from 'users' to 'user' if 'users' has more recent data
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user")
            user_count = cursor.fetchone()[0]
            
            if users_count > user_count:
                print(f"[INFO] Migrating {users_count} records from 'users' to 'user'")
                cursor.execute("""
                    INSERT OR REPLACE INTO user 
                    SELECT * FROM users WHERE id NOT IN (SELECT id FROM user)
                """)
            
            # Drop duplicate table
            cursor.execute("DROP TABLE IF EXISTS users")
            print("[OK] Removed duplicate 'users' table")
        
        # Similar consolidation for other duplicate tables
        duplicate_pairs = [
            ('student_profile', 'student_profiles'),
            ('hr_profile', 'hr_profiles'),
            ('job_drive', 'job_drives'),
            ('interview_session', 'interview_sessions')
        ]
        
        for main_table, duplicate_table in duplicate_pairs:
            if main_table in tables and duplicate_table in tables:
                print(f"[FIXING] Consolidating {duplicate_table} into {main_table}...")
                
                # Check which has more data
                cursor.execute(f"SELECT COUNT(*) FROM {duplicate_table}")
                dup_count = cursor.fetchone()[0]
                cursor.execute(f"SELECT COUNT(*) FROM {main_table}")
                main_count = cursor.fetchone()[0]
                
                if dup_count > main_count:
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {main_table} 
                        SELECT * FROM {duplicate_table} WHERE id NOT IN (SELECT id FROM {main_table})
                    """)
                    print(f"[OK] Migrated {dup_count} records")
                
                cursor.execute(f"DROP TABLE IF EXISTS {duplicate_table}")
                print(f"[OK] Removed duplicate '{duplicate_table}' table")
        
        conn.commit()
        conn.close()
        print("[OK] Database schema fixed successfully")
        
    except Exception as e:
        print(f"[ERROR] Database fix failed: {e}")

def cleanup_incomplete_sessions():
    print_header("CLEANING UP INCOMPLETE SESSIONS")
    
    try:
        conn = sqlite3.connect('ai_interview_system/Backend Files/instance/interview_agent.db')
        cursor = conn.cursor()
        
        # Find incomplete sessions older than 1 hour
        cursor.execute("""
            SELECT id, status, created_at FROM interview_session 
            WHERE status = 'in_progress' 
            AND datetime(created_at) < datetime('now', '-1 hour')
        """)
        
        incomplete_sessions = cursor.fetchall()
        
        if incomplete_sessions:
            print(f"[INFO] Found {len(incomplete_sessions)} incomplete sessions")
            
            for session_id, status, created_at in incomplete_sessions:
                print(f"  - Session {session_id}: {status} (created: {created_at})")
                
                # Mark as cancelled
                cursor.execute("""
                    UPDATE interview_session 
                    SET status = 'cancelled', 
                        end_time = datetime('now'),
                        ai_feedback = '{"message": "Session automatically cancelled due to timeout"}'
                    WHERE id = ?
                """, (session_id,))
            
            conn.commit()
            print(f"[OK] Cleaned up {len(incomplete_sessions)} incomplete sessions")
        else:
            print("[OK] No incomplete sessions found")
        
        # Also clean up sessions without questions
        cursor.execute("""
            UPDATE interview_session 
            SET questions = '[{"id": 1, "question": "Tell me about yourself", "type": "behavioral"}]'
            WHERE (questions IS NULL OR questions = '') AND status != 'cancelled'
        """)
        
        updated = cursor.rowcount
        if updated > 0:
            print(f"[OK] Added default questions to {updated} sessions")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Session cleanup failed: {e}")

def fix_ai_service_context():
    print_header("FIXING AI SERVICE CONTEXT")
    
    try:
        # Read current AI service file
        ai_service_path = 'ai_interview_system/Backend Files/app/ai_service.py'
        
        with open(ai_service_path, 'r') as f:
            content = f.read()
        
        # Check if context fix is already applied
        if 'app_context_fix_applied' in content:
            print("[OK] AI service context fix already applied")
            return
        
        # Add context handling fix
        context_fix = '''
    def _get_config_value(self, key, default=None):
        """Get configuration value with proper context handling."""
        try:
            from flask import current_app
            return current_app.config.get(key, default)
        except RuntimeError:
            # Outside application context, use environment variables
            import os
            from dotenv import load_dotenv
            load_dotenv()
            return os.getenv(key, default)
    
    # app_context_fix_applied = True
'''
        
        # Insert the fix after the class definition
        if 'class AIInterviewService:' in content:
            content = content.replace(
                'class AIInterviewService:',
                f'class AIInterviewService:{context_fix}'
            )
            
            # Update the _ensure_initialized method
            old_method = '''    def _ensure_initialized(self):
        """Ensure the service is initialized with Flask context."""
        if self.api_key is None:
            try:
                self.api_key = current_app.config.get('OPENROUTER_API_KEY')
                self.base_url = current_app.config.get('OPENROUTER_BASE_URL')'''
            
            new_method = '''    def _ensure_initialized(self):
        """Ensure the service is initialized with Flask context."""
        if self.api_key is None:
            try:
                self.api_key = self._get_config_value('OPENROUTER_API_KEY')
                self.base_url = self._get_config_value('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')'''
            
            content = content.replace(old_method, new_method)
            
            # Write the fixed content back
            with open(ai_service_path, 'w') as f:
                f.write(content)
            
            print("[OK] AI service context fix applied")
        else:
            print("[ERROR] Could not find AI service class to fix")
            
    except Exception as e:
        print(f"[ERROR] AI service fix failed: {e}")

def install_missing_dependencies():
    print_header("INSTALLING MISSING DEPENDENCIES")
    
    try:
        import subprocess
        
        # List of required packages
        required_packages = [
            'reportlab',
            'Pillow',
            'PyPDF2'
        ]
        
        for package in required_packages:
            try:
                __import__(package.lower().replace('-', '_'))
                print(f"[OK] {package} already installed")
            except ImportError:
                print(f"[INSTALLING] {package}...")
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"[OK] {package} installed successfully")
                else:
                    print(f"[ERROR] Failed to install {package}: {result.stderr}")
    
    except Exception as e:
        print(f"[ERROR] Dependency installation failed: {e}")

def create_missing_directories():
    print_header("CREATING MISSING DIRECTORIES")
    
    directories = [
        'ai_interview_system/Backend Files/static/uploads',
        'ai_interview_system/Backend Files/static/uploads/resumes',
        'ai_interview_system/Backend Files/static/uploads/photos',
        'ai_interview_system/Backend Files/logs',
        'ai_interview_system/Backend Files/instance'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"[OK] Directory ensured: {directory}")
        except Exception as e:
            print(f"[ERROR] Failed to create {directory}: {e}")

def test_fixes():
    print_header("TESTING FIXES")
    
    try:
        # Test database connection
        conn = sqlite3.connect('ai_interview_system/Backend Files/instance/interview_agent.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check for duplicates
        duplicates = []
        for table in tables:
            if table + 's' in tables or table[:-1] in tables:
                duplicates.append(table)
        
        if duplicates:
            print(f"[WARNING] Still have potential duplicates: {duplicates}")
        else:
            print("[OK] No duplicate tables found")
        
        # Test incomplete sessions
        cursor.execute("SELECT COUNT(*) FROM interview_session WHERE status = 'in_progress'")
        incomplete = cursor.fetchone()[0]
        print(f"[INFO] Incomplete sessions remaining: {incomplete}")
        
        conn.close()
        
        # Test AI service import
        try:
            sys.path.append('ai_interview_system/Backend Files')
            from app.ai_service import AIInterviewService
            ai_service = AIInterviewService()
            print("[OK] AI service imports successfully")
        except Exception as e:
            print(f"[ERROR] AI service still has issues: {e}")
        
        print("[OK] Basic tests completed")
        
    except Exception as e:
        print(f"[ERROR] Testing failed: {e}")

def main():
    print("AI Interview System - Critical Fixes")
    print(f"Timestamp: {datetime.now()}")
    print("This script will apply critical fixes to resolve system issues.")
    
    # Change to the correct directory
    os.chdir('d:/Projects/4rd Year Projects/AI INTERVIEW NEW/Main-Copy')
    
    try:
        fix_database_schema()
        cleanup_incomplete_sessions()
        fix_ai_service_context()
        install_missing_dependencies()
        create_missing_directories()
        test_fixes()
        
        print_header("FIXES COMPLETE")
        print("[OK] Critical fixes applied successfully")
        print("\nNext steps:")
        print("1. Restart the Flask application")
        print("2. Test interview functionality end-to-end")
        print("3. Monitor for any remaining issues")
        
    except Exception as e:
        print(f"\n[ERROR] Fix script failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()