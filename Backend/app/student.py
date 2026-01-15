from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models import User, InterviewSession, JobDrive, db
from app.logger import log_user_action
import json
from datetime import datetime, timedelta

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'student':
            flash('Access denied. Students only.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@student_bp.route('/resume')
@student_required
def resume_upload():
    """Resume upload and management page"""
    return render_template('student/resume_upload.html')

@student_bp.route('/dashboard')
@student_required
def enhanced_dashboard():
    # Get user statistics
    total_interviews = InterviewSession.query.filter_by(candidate_id=current_user.id).count()
    completed_interviews = InterviewSession.query.filter_by(
        candidate_id=current_user.id, status='completed'
    ).count()
    
    # Calculate average scores
    scores = db.session.query(InterviewSession.overall_score).filter_by(
        candidate_id=current_user.id, status='completed'
    ).filter(InterviewSession.overall_score.isnot(None)).all()
    
    avg_score = sum([s[0] for s in scores]) / len(scores) if scores else 0
    
    # Get recent interviews
    recent_interviews = InterviewSession.query.filter_by(
        candidate_id=current_user.id
    ).order_by(InterviewSession.created_at.desc()).limit(5).all()
    
    # Calculate streak
    streak = calculate_practice_streak(current_user.id)
    
    # Get achievements
    achievements = get_user_achievements(current_user.id)
    
    # Performance trends (last 10 interviews)
    performance_data = []
    last_interviews = InterviewSession.query.filter_by(
        candidate_id=current_user.id, status='completed'
    ).order_by(InterviewSession.created_at.desc()).limit(10).all()
    
    for interview in reversed(last_interviews):
        if interview.overall_score:
            performance_data.append({
                'date': interview.created_at.strftime('%m/%d'),
                'score': interview.overall_score
            })
    
    dashboard_data = {
        'total_interviews': total_interviews,
        'completed_interviews': completed_interviews,
        'average_score': round(avg_score, 1),
        'practice_streak': streak,
        'recent_interviews': recent_interviews,
        'achievements': achievements,
        'performance_data': performance_data,
        'completion_rate': round((completed_interviews / total_interviews * 100) if total_interviews > 0 else 0, 1)
    }
    
    return render_template('student/enhanced_dashboard.html', data=dashboard_data)

@student_bp.route('/practice')
@student_required
def practice_hub():
    # Get available practice categories
    categories = [
        {'id': 'technical', 'name': 'Technical Skills', 'icon': '💻', 'description': 'Programming, algorithms, system design'},
        {'id': 'behavioral', 'name': 'Behavioral', 'icon': '🤝', 'description': 'Leadership, teamwork, problem-solving'},
        {'id': 'communication', 'name': 'Communication', 'icon': '🗣️', 'description': 'Presentation, articulation, clarity'},
        {'id': 'industry', 'name': 'Industry Specific', 'icon': '🏢', 'description': 'Finance, healthcare, tech, consulting'}
    ]
    
    # Get difficulty levels
    difficulty_levels = [
        {'id': 'beginner', 'name': 'Beginner', 'color': '#27ae60'},
        {'id': 'intermediate', 'name': 'Intermediate', 'color': '#f39c12'},
        {'id': 'advanced', 'name': 'Advanced', 'color': '#e74c3c'}
    ]
    
    return render_template('student/practice_hub.html', 
                         categories=categories, 
                         difficulty_levels=difficulty_levels)

@student_bp.route('/analytics')
@student_required
def personal_analytics():
    # Get detailed performance analytics
    interviews = InterviewSession.query.filter_by(
        candidate_id=current_user.id, status='completed'
    ).all()
    
    # Skill breakdown
    skill_scores = {
        'technical': [],
        'communication': [],
        'confidence': [],
        'overall': []
    }
    
    for interview in interviews:
        if interview.technical_score:
            skill_scores['technical'].append(interview.technical_score)
        if interview.communication_score:
            skill_scores['communication'].append(interview.communication_score)
        if interview.confidence_score:
            skill_scores['confidence'].append(interview.confidence_score)
        if interview.overall_score:
            skill_scores['overall'].append(interview.overall_score)
    
    # Calculate averages
    analytics_data = {}
    for skill, scores in skill_scores.items():
        analytics_data[f'{skill}_avg'] = round(sum(scores) / len(scores) if scores else 0, 1)
        analytics_data[f'{skill}_trend'] = calculate_trend(scores)
    
    # Monthly progress
    monthly_data = get_monthly_progress(current_user.id)
    
    return render_template('student/analytics.html', 
                         analytics=analytics_data,
                         monthly_data=monthly_data,
                         total_interviews=len(interviews))

@student_bp.route('/learning-hub')
@student_required
def learning_hub():
    # Learning resources
    resources = [
        {
            'category': 'Interview Guides',
            'items': [
                {'title': 'STAR Method Guide', 'type': 'guide', 'duration': '15 min'},
                {'title': 'Technical Interview Prep', 'type': 'guide', 'duration': '30 min'},
                {'title': 'Behavioral Questions', 'type': 'guide', 'duration': '20 min'}
            ]
        },
        {
            'category': 'Video Tutorials',
            'items': [
                {'title': 'Body Language Tips', 'type': 'video', 'duration': '12 min'},
                {'title': 'Confidence Building', 'type': 'video', 'duration': '18 min'},
                {'title': 'Voice Modulation', 'type': 'video', 'duration': '10 min'}
            ]
        },
        {
            'category': 'Practice Questions',
            'items': [
                {'title': 'Common Questions Bank', 'type': 'questions', 'count': '150+ questions'},
                {'title': 'Industry Specific', 'type': 'questions', 'count': '200+ questions'},
                {'title': 'Coding Challenges', 'type': 'questions', 'count': '100+ problems'}
            ]
        }
    ]
    
    return render_template('student/learning_hub.html', resources=resources)

@student_bp.route('/social')
@student_required
def social_hub():
    # Get peer connections and study groups
    study_groups = [
        {'name': 'Tech Interview Prep', 'members': 45, 'activity': 'Active'},
        {'name': 'Behavioral Practice', 'members': 32, 'activity': 'Active'},
        {'name': 'Mock Interview Partners', 'members': 28, 'activity': 'Very Active'}
    ]
    
    # Recent discussions
    discussions = [
        {'title': 'How to handle stress during interviews?', 'replies': 12, 'time': '2 hours ago'},
        {'title': 'Best resources for system design prep', 'replies': 8, 'time': '5 hours ago'},
        {'title': 'Mock interview partner needed', 'replies': 15, 'time': '1 day ago'}
    ]
    
    return render_template('student/social_hub.html', 
                         study_groups=study_groups,
                         discussions=discussions)

@student_bp.route('/achievements')
@student_required
def achievements():
    user_achievements = get_user_achievements(current_user.id)
    available_achievements = get_available_achievements()
    
    return render_template('student/achievements.html',
                         user_achievements=user_achievements,
                         available_achievements=available_achievements)

@student_bp.route('/job-market')
@student_required
def job_market():
    # Mock job recommendations
    job_recommendations = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'match': 85,
            'salary': '$70k - $90k',
            'location': 'Remote'
        },
        {
            'title': 'Frontend Developer',
            'company': 'StartupXYZ',
            'match': 78,
            'salary': '$60k - $80k',
            'location': 'New York'
        }
    ]
    
    # Industry trends
    trends = [
        {'skill': 'React.js', 'demand': 'High', 'growth': '+15%'},
        {'skill': 'Python', 'demand': 'Very High', 'growth': '+22%'},
        {'skill': 'Cloud Computing', 'demand': 'High', 'growth': '+18%'}
    ]
    
    return render_template('student/job_market.html',
                         recommendations=job_recommendations,
                         trends=trends)

@student_bp.route('/settings')
@student_required
def student_settings():
    return render_template('student/settings.html')

# Helper functions
def calculate_practice_streak(user_id):
    # Calculate consecutive days of practice
    today = datetime.utcnow().date()
    streak = 0
    
    for i in range(30):  # Check last 30 days
        check_date = today - timedelta(days=i)
        has_practice = InterviewSession.query.filter(
            InterviewSession.candidate_id == user_id,
            db.func.date(InterviewSession.created_at) == check_date
        ).first()
        
        if has_practice:
            streak += 1
        else:
            break
    
    return streak

def get_user_achievements(user_id):
    # Get user's achievements based on their activity
    achievements = []
    
    total_interviews = InterviewSession.query.filter_by(candidate_id=user_id).count()
    completed_interviews = InterviewSession.query.filter_by(
        candidate_id=user_id, status='completed'
    ).count()
    
    # Achievement logic
    if completed_interviews >= 1:
        achievements.append({'name': 'First Interview', 'icon': '🎯', 'earned': True})
    if completed_interviews >= 5:
        achievements.append({'name': 'Practice Warrior', 'icon': '⚔️', 'earned': True})
    if completed_interviews >= 10:
        achievements.append({'name': 'Interview Master', 'icon': '👑', 'earned': True})
    
    streak = calculate_practice_streak(user_id)
    if streak >= 3:
        achievements.append({'name': '3-Day Streak', 'icon': '🔥', 'earned': True})
    if streak >= 7:
        achievements.append({'name': 'Week Warrior', 'icon': '📅', 'earned': True})
    
    return achievements

def get_available_achievements():
    return [
        {'name': 'First Interview', 'icon': '🎯', 'description': 'Complete your first practice interview'},
        {'name': 'Practice Warrior', 'icon': '⚔️', 'description': 'Complete 5 practice interviews'},
        {'name': 'Interview Master', 'icon': '👑', 'description': 'Complete 10 practice interviews'},
        {'name': '3-Day Streak', 'icon': '🔥', 'description': 'Practice for 3 consecutive days'},
        {'name': 'Week Warrior', 'icon': '📅', 'description': 'Practice for 7 consecutive days'},
        {'name': 'Perfect Score', 'icon': '💯', 'description': 'Achieve a perfect interview score'},
        {'name': 'Social Butterfly', 'icon': '🦋', 'description': 'Join 3 study groups'},
        {'name': 'Mentor', 'icon': '🎓', 'description': 'Help 5 other students'}
    ]

def calculate_trend(scores):
    if len(scores) < 2:
        return 'stable'
    
    recent_avg = sum(scores[-3:]) / len(scores[-3:]) if len(scores) >= 3 else scores[-1]
    older_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else scores[0]
    
    if recent_avg > older_avg + 5:
        return 'improving'
    elif recent_avg < older_avg - 5:
        return 'declining'
    else:
        return 'stable'

def get_monthly_progress(user_id):
    # Get monthly interview data for the last 6 months
    monthly_data = []
    
    for i in range(6):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        count = InterviewSession.query.filter(
            InterviewSession.candidate_id == user_id,
            InterviewSession.created_at >= month_start,
            InterviewSession.created_at < month_end
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%b'),
            'count': count
        })
    
    return list(reversed(monthly_data))