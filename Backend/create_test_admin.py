#!/usr/bin/env python3
"""
Create a test admin user to access the database dashboard
"""

from app import create_app, db
from app.models import User

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("✅ Admin user already exists!")
            print(f"Username: admin")
            print(f"Email: {admin.email}")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@talentsync.com',
            user_type='admin',
            role='admin',
            first_name='Admin',
            last_name='User',
            is_active=True
        )
        admin.set_password('admin123')  # Change this password!
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Email: admin@talentsync.com")
        print("\n🔗 Access database dashboard at: http://127.0.0.1:5001/admin/db/dashboard")

if __name__ == '__main__':
    create_admin()