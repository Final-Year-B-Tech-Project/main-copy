#!/usr/bin/env python3
"""Add adaptive interview tables to existing database."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.adaptive_models import AdaptiveSession, AdaptiveQuestion, AdaptiveResponse

def add_adaptive_tables():
    """Add adaptive interview tables to database."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create adaptive tables
            db.create_all()
            print("✓ Adaptive interview tables created successfully")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            adaptive_tables = ['adaptive_session', 'adaptive_question', 'adaptive_response']
            for table in adaptive_tables:
                if table in tables:
                    print(f"✓ Table '{table}' exists")
                else:
                    print(f"✗ Table '{table}' missing")
            
            print("\nAdaptive interview system ready!")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
    
    return True

if __name__ == '__main__':
    add_adaptive_tables()