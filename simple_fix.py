#!/usr/bin/env python3
"""
Simple system fix - install packages and test
"""

import subprocess
import sys
import os

def install_packages():
    """Install required packages."""
    
    print("Installing required packages...")
    
    packages = [
        'flask',
        'flask-login', 
        'flask-mail',
        'flask-sqlalchemy',
        'werkzeug',
        'requests',
        'python-dotenv'
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"  OK: {package}")
        except Exception as e:
            print(f"  ERROR: {package} - {e}")
    
    print("Package installation complete!")

def test_imports():
    """Test if imports work."""
    
    print("\nTesting imports...")
    
    try:
        import flask
        print("  OK: flask")
        
        import flask_login
        print("  OK: flask_login")
        
        import flask_mail
        print("  OK: flask_mail")
        
        import flask_sqlalchemy
        print("  OK: flask_sqlalchemy")
        
        import requests
        print("  OK: requests")
        
        import dotenv
        print("  OK: python-dotenv")
        
        print("\nAll imports successful!")
        return True
        
    except Exception as e:
        print(f"Import error: {e}")
        return False

def main():
    print("="*50)
    print("AI INTERVIEW SYSTEM - SIMPLE FIX")
    print("="*50)
    
    # Install packages
    install_packages()
    
    # Test imports
    if test_imports():
        print("\nSYSTEM READY!")
        print("\nNext steps:")
        print("1. cd 'ai_interview_system/Backend Files'")
        print("2. python run.py")
        print("3. Login with: adminsuyash / adminsuyash")
    else:
        print("\nSome packages failed to install.")
        print("Try running: pip install -r requirements.txt")

if __name__ == '__main__':
    main()