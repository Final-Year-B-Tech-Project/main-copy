from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, StudentProfile, HRProfile, JobDrive, InterviewSession
import json

db_admin = Blueprint('db_admin', __name__, url_prefix='/admin/db')

@db_admin.route('/dashboard')
@login_required
def dashboard():
    """Simple database dashboard"""
    if not current_user.is_admin():
        return "Access Denied", 403
    
    # Get table statistics
    stats = {
        'users': User.query.count(),
        'students': StudentProfile.query.count(),
        'hr_profiles': HRProfile.query.count(),
        'job_drives': JobDrive.query.count(),
        'interviews': InterviewSession.query.count()
    }
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/db_dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users)

@db_admin.route('/table/<table_name>')
@login_required
def view_table(table_name):
    """View table data"""
    if not current_user.is_admin():
        return "Access Denied", 403
    
    models = {
        'users': User,
        'students': StudentProfile,
        'hr_profiles': HRProfile,
        'job_drives': JobDrive,
        'interviews': InterviewSession
    }
    
    if table_name not in models:
        return "Table not found", 404
    
    model = models[table_name]
    records = model.query.limit(50).all()
    
    return render_template('admin/table_view.html', 
                         table_name=table_name,
                         records=records)