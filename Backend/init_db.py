#!/usr/bin/env python3
"""
Initialize Database with all tables
"""

from app import create_app, db

def init_database():
    """Initialize database with all tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database initialized successfully!")
        print("✓ All tables created")

if __name__ == "__main__":
    init_database()