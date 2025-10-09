import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, StudentProfile, HRProfile
from app.utils import allowed_file, generate_hr_code, parse_resume

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page with user type selection."""
    if request.method == 'POST':
        return register_post()
    return render_template('auth/register.html')

def register_post():
    """Handle registration form submission."""
    user_type = request.form.get('user_type')
    if not user_type or user_type not in ['student', 'hr']:
        flash('Please select a valid user type.', 'error')
        return render_template('auth/register.html')
    
    # Get form data
    email = request.form.get('email', '').strip().lower()
    username = request.form.get('username', '').strip()
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    
    # Validation
    if not all([email, username, password, first_name, last_name]):
        flash('All required fields must be filled.', 'error')
        return render_template('auth/register.html')
    
    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return render_template('auth/register.html')
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        return render_template('auth/register.html')
    
    # Check for existing username (must be unique across all user types)
    if User.query.filter_by(username=username).first():
        flash('Username already exists. Please choose another.', 'error')
        return render_template('auth/register.html')
    
    # Check for existing email with same user type
    if User.query.filter_by(email=email, user_type=user_type).first():
        flash(f'An account with this email already exists for {user_type} type.', 'error')
        return render_template('auth/register.html')
    
    try:
        # Create new user
        user = User(
            email=email,
            username=username,
            user_type=user_type,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()
        
        # Create basic profile
        if user_type == 'student':
            student_profile = StudentProfile(user_id=user.id)
            db.session.add(student_profile)
        elif user_type == 'hr':
            hr_profile = HRProfile(
                user_id=user.id, 
                hr_code=generate_hr_code(),
                company_name='Not Specified'  # Default value for required field
            )
            db.session.add(hr_profile)
        
        db.session.commit()
        
        # Send welcome email
        try:
            from app.email_service import send_admin_notification_email
            login_url = f"{request.url_root}auth/login"
            details = {
                'username': username,
                'user_type': user_type,
                'role': 'user',
                'created_by': 'Self Registration',
                'login_url': login_url
            }
            send_admin_notification_email(email, f"{first_name} {last_name}", 'account_created', details)
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        flash('Registration failed. Please try again.', 'error')
        return render_template('auth/register.html')



@auth.route('/login')
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    """Handle login form submission."""
    identifier = request.form.get('identifier', '').strip()  # username or email
    password = request.form.get('password')
    remember = bool(request.form.get('remember'))
    
    if not identifier or not password:
        flash('Please provide both username/email and password.', 'error')
        return render_template('auth/login.html')
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()
    
    if not user or not user.check_password(password):
        flash('Invalid credentials. Please try again.', 'error')
        return render_template('auth/login.html')
    
    if not user.is_active:
        flash('Your account has been deactivated. Please contact support.', 'error')
        return render_template('auth/login.html')
    
    # Handle multiple account types for same email
    if request.form.get('user_type'):
        requested_type = request.form.get('user_type')
        if user.user_type != requested_type:
            # Find the correct user account for this type
            user = User.query.filter_by(email=user.email, user_type=requested_type).first()
            if not user:
                flash('No account found for this user type.', 'error')
                return render_template('auth/login.html')
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Log in user
    login_user(user, remember=remember)
    
    # Redirect to appropriate dashboard
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    
    return redirect(url_for('main.dashboard'))

@auth.route('/check-email')
def check_email():
    """AJAX endpoint to check if email exists and for which user types."""
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'exists': False})
    
    users = User.query.filter_by(email=email).all()
    
    if not users:
        return jsonify({'exists': False})
    
    user_types = [user.user_type for user in users]
    return jsonify({
        'exists': True,
        'user_types': user_types,
        'show_selection': len(user_types) > 1
    })

@auth.route('/logout')
@login_required
def logout():
    """Log out current user."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/profile')
@login_required
def profile():
    """User profile page."""
    return render_template('auth/profile.html', user=current_user)

@auth.route('/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile."""
    try:
        # Update basic user info
        current_user.first_name = request.form.get('first_name', '').strip()
        current_user.last_name = request.form.get('last_name', '').strip()
        current_user.phone = request.form.get('phone', '').strip()
        
        # Handle profile photo upload
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos', filename)
                file.save(file_path)
                current_user.profile_photo = f"uploads/photos/{filename}"
        
        # Update type-specific profile
        if current_user.user_type == 'student' and current_user.student_profile:
            profile = current_user.student_profile
            profile.university = request.form.get('university', '')
            profile.degree = request.form.get('degree', '')
            profile.graduation_year = int(request.form.get('graduation_year', 0)) or None
            profile.gpa = float(request.form.get('gpa', 0)) or None
            profile.experience_level = request.form.get('experience_level', 'fresher')
            
            # Handle skills (JSON)
            skills = request.form.get('skills', '').split(',')
            skills = [skill.strip() for skill in skills if skill.strip()]
            profile.skills = json.dumps(skills)
            
            # Handle resume upload
            if 'resume' in request.files:
                file = request.files['resume']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"resume_{current_user.id}_{file.filename}")
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes', filename)
                    file.save(file_path)
                    profile.resume_file = f"uploads/resumes/{filename}"
                    
                    # Parse resume content
                    try:
                        profile.resume_text = parse_resume(file_path)
                    except Exception as e:
                        flash('Resume uploaded but could not be parsed for content.', 'warning')
        
        elif current_user.user_type == 'hr' and current_user.hr_profile:
            profile = current_user.hr_profile
            profile.company_name = request.form.get('company_name', '')
            profile.company_website = request.form.get('company_website', '')
            profile.company_description = request.form.get('company_description', '')
            profile.department = request.form.get('department', '')
            profile.position = request.form.get('position', '')
            profile.years_experience = int(request.form.get('years_experience', 0)) or None
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send profile update notification
        try:
            from app.email_service import send_profile_update_notification
            send_profile_update_notification(current_user.email, current_user.full_name)
        except Exception as e:
            print(f"Failed to send profile update email: {e}")
        
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to update profile. Please try again.', 'error')
    
    return redirect(url_for('auth.profile'))