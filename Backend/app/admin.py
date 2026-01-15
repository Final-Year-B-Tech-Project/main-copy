from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, logout_user
from functools import wraps
from app.models import User, InterviewSession, JobDrive, db
from app.logger import log_admin_action, log_security_event
try:
    from app.email_service import send_admin_notification_email
except ImportError:
    def send_admin_notification_email(*args, **kwargs):
        print("Email service not available - notification skipped")
import json
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def master_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'master_admin':
            flash('Access denied. Master admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Get recent users (last 10)
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Get system statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    inactive_users = total_users - active_users
    
    # User type breakdown
    students = User.query.filter_by(user_type='student').count()
    hr_users = User.query.filter_by(user_type='hr').count()
    admins = User.query.filter(User.role.in_(['admin', 'master_admin', 'developer'])).count()
    
    # Interview statistics
    total_interviews = InterviewSession.query.count()
    completed_interviews = InterviewSession.query.filter_by(status='completed').count()
    
    # Recent activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_registrations = User.query.filter(User.created_at >= yesterday).count()
    recent_interviews = InterviewSession.query.filter(InterviewSession.created_at >= yesterday).count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'students': students,
        'hr_users': hr_users,
        'admins': admins,
        'total_interviews': total_interviews,
        'completed_interviews': completed_interviews,
        'recent_registrations': recent_registrations,
        'recent_interviews': recent_interviews
    }
    
    return render_template('admin/dashboard.html', recent_users=recent_users, stats=stats)

@admin_bp.route('/users')
@admin_required
def manage_users():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    user_type_filter = request.args.get('user_type', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    
    # Build query
    query = User.query
    
    if user_type_filter:
        query = query.filter_by(user_type=user_type_filter)
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    if search_query:
        query = query.filter(
            db.or_(
                User.username.contains(search_query),
                User.email.contains(search_query),
                User.first_name.contains(search_query),
                User.last_name.contains(search_query)
            )
        )
    
    # Get paginated results
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users, 
                         user_type_filter=user_type_filter, 
                         role_filter=role_filter,
                         status_filter=status_filter,
                         search_query=search_query)

@admin_bp.route('/user/<int:user_id>/role', methods=['POST'])
@master_admin_required
def update_user_role(user_id):
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        if user.role == 'master_admin' and user.id != current_user.id:
            return jsonify({'success': False, 'message': 'Cannot modify other master admin roles'})
        
        old_role = user.role
        user.role = new_role
        
        # Set default permissions based on role
        if new_role == 'admin':
            user.permissions = json.dumps(['manage_users', 'view_analytics', 'manage_interviews'])
        elif new_role == 'developer':
            user.permissions = json.dumps(['view_logs', 'manage_system'])
        elif new_role == 'master_admin':
            user.permissions = json.dumps(['all'])
        else:
            user.permissions = None
        
        db.session.commit()
        
        # Log action
        log_admin_action(current_user.id, f"Changed user {user.username} role from {old_role} to {new_role}")
        
        # Send role change notification
        try:
            send_admin_notification_email(
                recipient_email=user.email,
                recipient_name=user.full_name,
                action='role_changed',
                details={
                    'username': user.username,
                    'old_role': old_role,
                    'new_role': new_role,
                    'changed_by': current_user.full_name,
                    'change_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
        except Exception as e:
            print(f"Failed to send role change email: {e}")
        
        return jsonify({'success': True, 'message': 'Role updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/logout')
@admin_required
def admin_logout():
    log_admin_action(current_user.id, f"Admin {current_user.username} logged out")
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.index'))

@admin_bp.route('/activity-log')
@admin_required
def activity_log():
    # Get recent admin actions from logs
    import os
    log_file = os.path.join('logs', 'admin.log')
    recent_activities = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()[-50:]  # Last 50 entries
            for line in lines:
                if line.strip():
                    recent_activities.append(line.strip())
    
    return render_template('admin/activity_log.html', activities=recent_activities)

@admin_bp.route('/system-stats')
@admin_required
def system_stats():
    # Get comprehensive system statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_interviews = InterviewSession.query.count()
    completed_interviews = InterviewSession.query.filter_by(status='completed').count()
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_registrations = User.query.filter(User.created_at >= week_ago).count()
    recent_interviews = InterviewSession.query.filter(InterviewSession.created_at >= week_ago).count()
    
    # User type breakdown
    students = User.query.filter_by(user_type='student').count()
    hr_users = User.query.filter_by(user_type='hr').count()
    admins = User.query.filter(User.role.in_(['admin', 'master_admin', 'developer'])).count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'students': students,
        'hr_users': hr_users,
        'admins': admins,
        'total_interviews': total_interviews,
        'completed_interviews': completed_interviews,
        'recent_registrations': recent_registrations,
        'recent_interviews': recent_interviews
    }
    
    return render_template('admin/system_stats.html', stats=stats)

@admin_bp.route('/create-user', methods=['GET', 'POST'])
@master_admin_required
def create_user():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 'password']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'success': False, 'message': f'{field} is required'})
            
            # Check if user already exists
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'success': False, 'message': 'Username already exists'})
            
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'message': 'Email already exists'})
            
            # Create new user
            new_user = User(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                user_type=data['user_type'],
                role=data.get('role', 'user'),
                phone=data.get('phone', ''),
                is_active=True
            )
            new_user.set_password(data['password'])
            
            # Set permissions based on role
            if data.get('role') == 'admin':
                new_user.permissions = json.dumps(['manage_users', 'view_analytics', 'manage_interviews'])
            elif data.get('role') == 'developer':
                new_user.permissions = json.dumps(['view_logs', 'manage_system'])
            
            db.session.add(new_user)
            db.session.commit()
            
            # Log action
            log_admin_action(current_user.id, f"Created user: {new_user.username} ({new_user.user_type})")
            
            # Send welcome email to new user
            try:
                send_admin_notification_email(
                    recipient_email=new_user.email,
                    recipient_name=new_user.full_name,
                    action='account_created',
                    details={
                        'username': new_user.username,
                        'user_type': new_user.user_type,
                        'role': new_user.role,
                        'created_by': current_user.full_name,
                        'login_url': request.url_root + 'auth/login',
                        'password': data['password']
                    }
                )
            except Exception as e:
                print(f"Failed to send welcome email: {e}")
            
            return jsonify({'success': True, 'message': 'User created successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    return render_template('admin/create_user.html')

@admin_bp.route('/user/<int:user_id>/terminate', methods=['POST'])
@master_admin_required
def terminate_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        if user.role == 'master_admin' and user.id != current_user.id:
            return jsonify({'success': False, 'message': 'Cannot terminate other master admins'})
        
        # Deactivate user instead of deleting
        user.is_active = False
        db.session.commit()
        
        # Log action
        log_admin_action(current_user.id, f"Terminated user: {user.username} ({user.email})")
        log_security_event('USER_TERMINATED', f'User {user.username} terminated by admin {current_user.username}')
        
        # Send termination notification
        try:
            send_admin_notification_email(
                recipient_email=user.email,
                recipient_name=user.full_name,
                action='account_terminated',
                details={
                    'username': user.username,
                    'terminated_by': current_user.full_name,
                    'termination_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    'reason': 'Administrative action'
                }
            )
        except Exception as e:
            print(f"Failed to send termination email: {e}")
        
        return jsonify({'success': True, 'message': 'User terminated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@master_admin_required
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': 'Cannot delete your own account'})
        
        if user.role == 'master_admin':
            return jsonify({'success': False, 'message': 'Cannot delete master admin accounts'})
        
        # Store user info for email
        username = user.username
        email = user.email
        full_name = user.full_name
        user_type = user.user_type
        
        # Send deletion notification before deleting
        try:
            send_admin_notification_email(
                recipient_email=email,
                recipient_name=full_name,
                action='account_deleted',
                details={
                    'username': username,
                    'user_type': user_type,
                    'deleted_by': current_user.full_name,
                    'deletion_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    'reason': 'Account permanently deleted by administrator'
                }
            )
        except Exception as e:
            print(f"Failed to send deletion email: {e}")
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        # Log action
        log_admin_action(current_user.id, f"Deleted user: {username} ({email})")
        log_security_event('USER_DELETED', f'User {username} permanently deleted by admin {current_user.username}')
        
        return jsonify({'success': True, 'message': f'User {username} deleted successfully and notified via email'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/user/<int:user_id>/activate', methods=['POST'])
@master_admin_required
def activate_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        user.is_active = True
        db.session.commit()
        
        # Log action
        log_admin_action(current_user.id, f"Activated user: {user.username} ({user.email})")
        
        # Send activation notification
        try:
            send_admin_notification_email(
                recipient_email=user.email,
                recipient_name=user.full_name,
                action='account_activated',
                details={
                    'username': user.username,
                    'activated_by': current_user.full_name,
                    'activation_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    'login_url': request.url_root + 'auth/login'
                }
            )
        except Exception as e:
            print(f"Failed to send activation email: {e}")
        
        return jsonify({'success': True, 'message': 'User activated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/user/<int:user_id>/reset-password', methods=['POST'])
@master_admin_required
def reset_user_password(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        # Generate temporary password
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        user.set_password(temp_password)
        db.session.commit()
        
        # Log action
        log_admin_action(current_user.id, f"Reset password for user: {user.username}")
        log_security_event('PASSWORD_RESET', f'Password reset for user {user.username} by admin {current_user.username}')
        
        # Send new password email
        try:
            send_admin_notification_email(
                recipient_email=user.email,
                recipient_name=user.full_name,
                action='password_reset',
                details={
                    'username': user.username,
                    'new_password': temp_password,
                    'reset_by': current_user.full_name,
                    'reset_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    'login_url': request.url_root + 'auth/login'
                }
            )
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
        
        return jsonify({'success': True, 'message': 'Password reset successfully. New password sent to user email.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/interviews')
@admin_required
def manage_interviews():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    session_type_filter = request.args.get('session_type', '')
    
    # Build query
    query = InterviewSession.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if session_type_filter:
        query = query.filter_by(session_type=session_type_filter)
    
    # Get paginated results
    interviews = query.order_by(InterviewSession.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/interviews.html', interviews=interviews,
                         status_filter=status_filter,
                         session_type_filter=session_type_filter)

@admin_bp.route('/clear-logs', methods=['POST'])
@master_admin_required
def clear_logs():
    try:
        log_type = request.json.get('log_type', 'all')
        
        import os
        logs_dir = 'logs'
        
        if log_type == 'all':
            log_files = ['system.log', 'admin.log', 'security.log', 'user.log']
        else:
            log_files = [f'{log_type}.log']
        
        cleared_files = []
        for log_file in log_files:
            file_path = os.path.join(logs_dir, log_file)
            if os.path.exists(file_path):
                open(file_path, 'w').close()  # Clear file content
                cleared_files.append(log_file)
        
        # Log the action
        log_admin_action(current_user.id, f"Cleared logs: {', '.join(cleared_files)}")
        
        return jsonify({
            'success': True, 
            'message': f'Cleared {len(cleared_files)} log files successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@admin_bp.route('/analytics')
@admin_required
def analytics_dashboard():
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    daily_registrations = []
    for i in range(7):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = User.query.filter(db.func.date(User.created_at) == date).count()
        daily_registrations.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
    
    total_interviews = InterviewSession.query.count()
    completed_interviews = InterviewSession.query.filter_by(status='completed').count()
    completion_rate = (completed_interviews / total_interviews * 100) if total_interviews > 0 else 0
    
    avg_scores = db.session.query(db.func.avg(InterviewSession.overall_score)).filter(
        InterviewSession.overall_score.isnot(None)
    ).scalar() or 0
    
    analytics_data = {
        'daily_registrations': daily_registrations,
        'completion_rate': round(completion_rate, 1),
        'average_score': round(avg_scores, 1),
        'total_interviews': total_interviews,
        'completed_interviews': completed_interviews,
        'active_users': User.query.filter_by(is_active=True).count()
    }
    
    return render_template('admin/analytics.html', analytics=analytics_data)

@admin_bp.route('/notifications')
@admin_required
def notification_center():
    notifications = []
    
    inactive_users = User.query.filter_by(is_active=False).count()
    if inactive_users > 0:
        notifications.append({
            'type': 'warning',
            'title': 'Inactive Users',
            'message': f'{inactive_users} users are currently inactive',
            'timestamp': datetime.utcnow()
        })
    
    recent_users = User.query.filter(User.created_at >= datetime.utcnow() - timedelta(hours=24)).count()
    if recent_users > 0:
        notifications.append({
            'type': 'success',
            'title': 'New Registrations',
            'message': f'{recent_users} new users registered in the last 24 hours',
            'timestamp': datetime.utcnow()
        })
    
    return render_template('admin/notifications.html', notifications=notifications)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@master_admin_required
def system_settings():
    if request.method == 'POST':
        try:
            settings = request.get_json()
            
            with open('system_config.json', 'w') as f:
                json.dump(settings, f, indent=2)
            
            log_admin_action(current_user.id, "Updated system settings")
            return jsonify({'success': True, 'message': 'Settings updated successfully'})
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    default_settings = {
        'system_name': 'AI Interview System',
        'maintenance_mode': False,
        'email_notifications': True,
        'max_interview_duration': 60,
        'security_level': 'medium'
    }
    
    try:
        with open('system_config.json', 'r') as f:
            current_settings = json.load(f)
    except:
        current_settings = default_settings
    
    return render_template('admin/settings.html', settings=current_settings)

@admin_bp.route('/security')
@admin_required
def security_dashboard():
    active_sessions = User.query.filter(
        User.last_login >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    security_events = []
    try:
        with open('logs/security.log', 'r') as f:
            lines = f.readlines()[-20:]
            for line in lines:
                if line.strip():
                    security_events.append(line.strip())
    except:
        security_events = ['No security events logged']
    
    security_data = {
        'active_sessions': active_sessions,
        'security_events': security_events,
        'total_users': User.query.count(),
        'admin_users': User.query.filter(User.role.in_(['admin', 'master_admin', 'developer'])).count()
    }
    
    return render_template('admin/security.html', security=security_data)