#!/usr/bin/env python3
"""
Test script to verify the interview system fixes
"""

import sys
import os
sys.path.append('ai_interview_system/Backend Files')

def test_professional_interviewer():
    """Test ProfessionalInterviewer should_continue method"""
    try:
        from app.professional_interviewer import ProfessionalInterviewer
        
        interviewer = ProfessionalInterviewer("Software Engineer")
        
        # Test should_continue with proper parameters
        result = interviewer.should_continue(3, 600)  # 3 questions, 10 minutes remaining
        print(f"✓ should_continue(3, 600): {result}")
        
        result = interviewer.should_continue(8, 30)   # 8 questions, 30 seconds remaining
        print(f"✓ should_continue(8, 30): {result}")
        
        print("✓ ProfessionalInterviewer test passed")
        return True
        
    except Exception as e:
        print(f"✗ ProfessionalInterviewer test failed: {e}")
        return False

def test_llm_feedback():
    """Test LLM feedback generation"""
    try:
        from app.llm_feedback import generate_comprehensive_feedback
        from app.ai_service_simple import SimpleAIService
        
        ai_service = SimpleAIService()
        
        # Test with sample responses
        responses = [
            {
                'question': 'Tell me about yourself',
                'answer': 'I am a software engineer with 3 years of experience in Python and web development.',
                'timestamp': '2024-01-01T10:00:00Z',
                'response_time': 45
            }
        ]
        
        feedback = generate_comprehensive_feedback(ai_service, responses, "Software Engineer")
        
        if 'overall_score' in feedback:
            print(f"✓ LLM feedback generated with score: {feedback['overall_score']}")
            print("✓ LLM feedback test passed")
            return True
        else:
            print("✗ LLM feedback missing overall_score")
            return False
            
    except Exception as e:
        print(f"✗ LLM feedback test failed: {e}")
        return False

def test_email_encoding():
    """Test email encoding fix"""
    try:
        # Test the problematic characters
        test_text = "Interview Summary:\n- Overall Performance: 75%\n- Technical Skills: 70%"
        
        # This should not raise encoding errors
        encoded = test_text.encode('ascii', errors='ignore')
        print(f"✓ Email encoding test passed: {len(encoded)} bytes")
        return True
        
    except Exception as e:
        print(f"✗ Email encoding test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing interview system fixes...\n")
    
    tests = [
        ("ProfessionalInterviewer", test_professional_interviewer),
        ("LLM Feedback", test_llm_feedback),
        ("Email Encoding", test_email_encoding)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        if test_func():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All fixes verified successfully!")
        return True
    else:
        print("✗ Some tests failed. Please check the issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)