#!/usr/bin/env python3
"""
Development server runner for AI Interview Agent.
Use this file to run the application in development mode.
"""

import os
import sys
from app import create_app

def main():
    """Main function to run the development server."""
    
    # Set development environment
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    # Create application
    app = create_app('development')
    
    # Server configuration
    host = '127.0.0.1'
    port = 5000
    
    print("\n" + "="*60)
    print("AI INTERVIEW AGENT - DEVELOPMENT SERVER")
    print("="*60)
    print(f"URL: http://{host}:{port}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug Mode: {os.environ.get('FLASK_DEBUG', '1') == '1'}")
    print("="*60)
    print("Features Available:")
    print("  • Student Registration & Dashboard")
    print("  • HR Registration & Dashboard") 
    print("  • AI-Powered Practice Interviews")
    print("  • Job Drive Management")
    print("  • Interview Scheduling & Feedback")
    print("  • Master Admin Panel")
    print("="*60)
    print("Tips:")
    print("  • Master Admin: adminsuyash / adminsuyash")
    print("  • Use Ctrl+C to stop the server")
    print("  • Admin Panel: /admin/dashboard")
    print("="*60)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=True,
            use_reloader=True,
            use_debugger=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()