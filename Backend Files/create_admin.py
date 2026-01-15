#!/usr/bin/env python3
"""Script to create master admin user."""

from app import create_app, db
from app.models import User
import json

def create_master_admin():
    app = create_app()
    with app.app_context():
        # Check if master admin exists
        existing = User.query.filter_by(username='adminsuyash').first()
        if existing:
            print("Master admin already exists!")
            return
        
        # Create master admin
        admin = User(
            username='adminsuyash',
            email='admin@system.com',
            first_name='Admin',
            last_name='Suyash',
            user_type='master_admin',
            role='master_admin',
            permissions=json.dumps(['all'])
        )
        admin.set_password('adminsuyash')
        
        db.session.add(admin)
        db.session.commit()
        
        print("Master admin created successfully!")
        print("Username: adminsuyash")
        print("Password: adminsuyash")

if __name__ == '__main__':
    create_master_admin()