#!/usr/bin/env python3
"""
AI Interview Agent - Main Application Entry Point
A comprehensive interview management system with AI-powered interviews.
"""

import os
from app import create_app

if __name__ == '__main__':
    # Development server configuration
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Create Flask application
    app = create_app()
    
    print("=" * 50)
    print("[AI INTERVIEW] Starting Application...")
    print("=" * 50)
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print("=" * 50)
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )