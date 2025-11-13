#!/usr/bin/env python3
"""
Interview System Test Script
Tests specific interview functionality
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
import requests
from pathlib import Path

def test_interview_flow():
    print("="*60)
    print(" INTERVIEW FLOW TEST")
    print("="*60)
    
    # Test database connection
    try:
        conn = sqlite3.connect('instance/interview_agent.db')
        cursor = conn.cursor()
        
        # Get a test session
        cursor.execute("SELECT * FROM interview_session ORDER BY id DESC LIMIT 1")
        session = cursor.fetchone()
        
        if session:
            print(f"[OK] Found test session: ID {session[0]}")
            print(f"  - Status: {session[4]}")
            print(f"  - Type: {session[3]}")
            print(f"  - Questions: {session[9][:100] if session[9] else 'None'}...")
            print(f"  - Responses: {session[10][:100] if session[10] else 'None'}...")
        else:
            print("[ERROR] No interview sessions found")
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")

def test_ai_service_functions():
    print("\n" + "="*60)
    print(" AI SERVICE FUNCTIONS TEST")
    print("="*60)
    
    try:
        # Import AI service
        sys.path.append('.')
        from app.ai_service import AIInterviewService
        
        ai_service = AIInterviewService()
        print("[OK] AI Service imported successfully")
        
        # Test question generation
        try:
            questions = ai_service.generate_interview_questions(
                job_role="Software Developer",
                difficulty="medium",
                experience_level="fresher",
                num_questions=3
            )
            print(f"[OK] Generated {len(questions)} questions")
            for i, q in enumerate(questions[:2], 1):
                print(f"  Q{i}: {q.get('question', 'No question')[:80]}...")
        except Exception as e:
            print(f"[ERROR] Question generation failed: {e}")
        
        # Test feedback generation
        try:
            mock_questions = [{"id": 1, "question": "Tell me about yourself"}]
            mock_responses = {"1": {"answer": "I am a software developer"}}
            
            # Create mock session object
            class MockSession:
                def __init__(self):
                    self.session_type = 'practice'
                    self.job_drive = None
                    self.duration = 300
            
            feedback = ai_service.generate_feedback(mock_questions, mock_responses, MockSession())
            print(f"[OK] Generated feedback with score: {feedback.get('overall_score', 'N/A')}")
        except Exception as e:
            print(f"[ERROR] Feedback generation failed: {e}")
            
    except Exception as e:
        print(f"[ERROR] AI Service import failed: {e}")

def test_interview_routes():
    print("\n" + "="*60)
    print(" INTERVIEW ROUTES TEST")
    print("="*60)
    
    # Check if Flask app can be imported
    try:
        from app import create_app
        app = create_app()
        print("[OK] Flask app created successfully")
        
        with app.app_context():
            # Test route registration
            routes = []
            for rule in app.url_map.iter_rules():
                if 'interview' in rule.rule:
                    routes.append(rule.rule)
            
            print(f"[OK] Found {len(routes)} interview routes:")
            for route in routes:
                print(f"  - {route}")
                
    except Exception as e:
        print(f"[ERROR] Flask app test failed: {e}")

def test_template_rendering():
    print("\n" + "="*60)
    print(" TEMPLATE RENDERING TEST")
    print("="*60)
    
    templates = [
        'templates/interview/pro_interface.html',
        'templates/student/dashboard.html',
        'templates/hr/dashboard.html'
    ]
    
    for template in templates:
        if os.path.exists(template):
            print(f"[OK] {template} exists")
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'session' in content:
                    print(f"  - Contains session variables")
                if 'javascript' in content.lower() or '<script>' in content:
                    print(f"  - Contains JavaScript")
        else:
            print(f"[ERROR] {template} missing")

def test_javascript_functionality():
    print("\n" + "="*60)
    print(" JAVASCRIPT FUNCTIONALITY TEST")
    print("="*60)
    
    js_file = 'templates/interview/pro_interface.html'
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key JavaScript functions
        js_functions = [
            'ProInterviewSystem',
            'generateAIResponse',
            'endInterview',
            'initializeVoiceRecognition',
            'sendManualResponse'
        ]
        
        for func in js_functions:
            if func in content:
                print(f"[OK] {func} function found")
            else:
                print(f"[ERROR] {func} function missing")
    else:
        print(f"[ERROR] JavaScript file not found")

def identify_interview_issues():
    print("\n" + "="*60)
    print(" INTERVIEW ISSUES ANALYSIS")
    print("="*60)
    
    issues = []
    
    # Check database schema issues
    try:
        conn = sqlite3.connect('instance/interview_agent.db')
        cursor = conn.cursor()
        
        # Check for duplicate tables (schema migration issue)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%user%'")
        user_tables = cursor.fetchall()
        if len(user_tables) > 1:
            issues.append("SCHEMA: Duplicate user tables detected - database migration needed")
        
        # Check for incomplete sessions
        cursor.execute("SELECT COUNT(*) FROM interview_session WHERE status = 'in_progress'")
        incomplete = cursor.fetchone()[0]
        if incomplete > 0:
            issues.append(f"DATA: {incomplete} incomplete interview sessions")
        
        # Check for sessions without questions
        cursor.execute("SELECT COUNT(*) FROM interview_session WHERE questions IS NULL OR questions = ''")
        no_questions = cursor.fetchone()[0]
        if no_questions > 0:
            issues.append(f"DATA: {no_questions} sessions without questions")
        
        conn.close()
        
    except Exception as e:
        issues.append(f"DATABASE: Connection error - {e}")
    
    # Check AI service configuration
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key or len(api_key) < 20:
        issues.append("AI: Invalid or missing OpenRouter API key")
    
    # Check file permissions
    upload_dirs = ['static/uploads', 'static/uploads/resumes', 'static/uploads/photos']
    for upload_dir in upload_dirs:
        if not os.path.exists(upload_dir):
            issues.append(f"FILES: Upload directory missing - {upload_dir}")
    
    if issues:
        print("ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("[OK] No major interview issues detected")

def provide_interview_fixes():
    print("\n" + "="*60)
    print(" RECOMMENDED FIXES")
    print("="*60)
    
    fixes = [
        "1. DATABASE: Run 'python migrate_db.py' to fix schema issues",
        "2. AI SERVICE: Verify OpenRouter API key is valid and has credits",
        "3. SESSIONS: Clear incomplete sessions with status cleanup",
        "4. UPLOADS: Create missing upload directories",
        "5. JAVASCRIPT: Test voice recognition in Chrome/Edge browsers",
        "6. TEMPLATES: Verify all template variables are properly passed",
        "7. ROUTES: Test all interview endpoints manually",
        "8. FEEDBACK: Check AI feedback generation with sample data",
        "9. EMAIL: Test email notifications for interview completion",
        "10. SECURITY: Verify interview link validation works correctly"
    ]
    
    for fix in fixes:
        print(fix)

def main():
    print("AI Interview System - Interview Functionality Test")
    print(f"Timestamp: {datetime.now()}")
    
    try:
        test_interview_flow()
        test_ai_service_functions()
        test_interview_routes()
        test_template_rendering()
        test_javascript_functionality()
        identify_interview_issues()
        provide_interview_fixes()
        
        print("\n" + "="*60)
        print(" INTERVIEW TEST COMPLETE")
        print("="*60)
        print("[OK] Interview system analysis completed")
        
    except Exception as e:
        print(f"\n[ERROR] Test script error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()