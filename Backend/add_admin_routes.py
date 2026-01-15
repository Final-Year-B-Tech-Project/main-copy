#!/usr/bin/env python3
"""Script to add advanced admin routes to admin.py"""

import os

def add_routes():
    admin_file = 'app/admin.py'
    
    # Read current content
    with open(admin_file, 'r') as f:
        content = f.read()
    
    # New routes to add
    new_routes = '''
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
    
    return render_template('admin/security.html', security=security_data)'''
    
    # Add routes before the last line
    content = content.rstrip() + new_routes
    
    # Write back
    with open(admin_file, 'w') as f:
        f.write(content)
    
    print("Advanced admin routes added successfully!")

if __name__ == '__main__':
    add_routes()