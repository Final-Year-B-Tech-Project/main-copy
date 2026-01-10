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

@student_bp.route('/training-modules')
@student_required
def training_modules():
    """Training modules overview page."""
    
    # Comprehensive training modules with proper structure
    training_modules = [
        {
            'id': 'interview-fundamentals',
            'title': 'Interview Fundamentals',
            'icon': '🎯',
            'description': 'Master the essential skills every successful candidate needs',
            'duration': '2-3 hours',
            'difficulty': 'Beginner',
            'lessons_count': 8,
            'color': '#6366f1',
            'preview': 'Learn professional appearance, body language, research techniques, and how to make powerful first impressions that set you apart from other candidates.'
        },
        {
            'id': 'behavioral-mastery',
            'title': 'Behavioral Interview Mastery',
            'icon': '⭐',
            'description': 'Perfect the STAR method and storytelling techniques',
            'duration': '2-3 hours',
            'difficulty': 'Intermediate',
            'lessons_count': 7,
            'color': '#10b981',
            'preview': 'Master the STAR framework, craft compelling stories, and learn to answer any behavioral question with confidence and impact.'
        },
        {
            'id': 'technical-excellence',
            'title': 'Technical Interview Excellence',
            'icon': '💻',
            'description': 'Ace coding challenges and technical assessments',
            'duration': '3-4 hours',
            'difficulty': 'Advanced',
            'lessons_count': 9,
            'color': '#8b5cf6',
            'preview': 'Develop problem-solving strategies, master data structures & algorithms, and learn system design principles that impress technical interviewers.'
        },
        {
            'id': 'communication-confidence',
            'title': 'Communication & Confidence',
            'icon': '🗣️',
            'description': 'Build unshakeable confidence and communication skills',
            'duration': '2-3 hours',
            'difficulty': 'Intermediate',
            'lessons_count': 6,
            'color': '#f59e0b',
            'preview': 'Transform your communication style, overcome interview anxiety, and project confidence that makes interviewers remember you positively.'
        },
        {
            'id': 'industry-preparation',
            'title': 'Industry-Specific Preparation',
            'icon': '🏢',
            'description': 'Tailored strategies for different industries and roles',
            'duration': '2-3 hours',
            'difficulty': 'Advanced',
            'lessons_count': 8,
            'color': '#ef4444',
            'preview': 'Get insider knowledge about tech, finance, healthcare, and consulting interviews with industry-specific questions and expectations.'
        },
        {
            'id': 'salary-negotiation',
            'title': 'Salary Negotiation Mastery',
            'icon': '💰',
            'description': 'Negotiate compensation packages like a professional',
            'duration': '1-2 hours',
            'difficulty': 'Advanced',
            'lessons_count': 5,
            'color': '#06b6d4',
            'preview': 'Learn research techniques, negotiation strategies, and how to maximize your total compensation package beyond just base salary.'
        }
    ]
    
    return render_template('student/training_modules.html', modules=training_modules)

@student_bp.route('/training-module/<module_id>')
@student_required
def training_module_detail(module_id):
    """Detailed view of a specific training module with lessons."""
    
    # Comprehensive lesson content for each module
    modules_content = {
        'interview-fundamentals': {
            'title': 'Interview Fundamentals',
            'icon': '🎯',
            'description': 'Master the essential skills every successful candidate needs',
            'duration': '2-3 hours',
            'difficulty': 'Beginner',
            'color': '#6366f1',
            'lessons': [
                {
                    'id': 1,
                    'title': 'First Impressions & Professional Presence',
                    'duration': '35 min',
                    'content': '''
<h3><i class="fas fa-eye"></i> The 7-Second Rule: Making Every Moment Count</h3>
<p>Research from Harvard Business School shows that interviewers form their first impression within 7 seconds of meeting you. This lesson teaches you how to maximize those crucial moments and create a lasting positive impact that sets the tone for your entire interview.</p>

<div class="tip-section">
    <h5><i class="fas fa-user-tie"></i> HR Insider Perspective</h5>
    <p><strong>What We Look For:</strong> It's not just about the suit. We look for <em>congruence</em>—does your energy, attire, and body language match the role you're applying for? A developer in a three-piece suit might feel "off" at a startup, just as a banker in jeans would at a firm.</p>
</div>

<h4>Professional Appearance Mastery</h4>
<ul>
    <li><strong>Dress Code Intelligence:</strong> Research company culture thoroughly using LinkedIn employee photos. The golden rule: dress 10-15% more formal than their standard.</li>
    <li><strong>Color Psychology:</strong>
        <ul>
            <li><strong>Navy Blue:</strong> Trustworthiness (Finance/Law)</li>
            <li><strong>Charcoal Gray:</strong> Authority (Management)</li>
            <li><strong>Black:</strong> Sophistication (Creative/Fashion)</li>
        </ul>
    </li>
    <li><strong>Grooming Checklist:</strong> Fresh haircut, trimmed nails, minimal scent (others should only smell it when hugging you), and polished shoes.</li>
</ul>

<h4>Body Language That Commands Respect</h4>
<ul>
    <li><strong>The Power Entrance:</strong> Walk with purpose. Shoulders back, head up. Don't shuffle.</li>
    <li><strong>Handshake Mastery:</strong> Web-to-web contact, 2-3 pumps, match their pressure. It's the first physical connection—make it count.</li>
    <li><strong>Eye Contact Formula:</strong> Aim for 70-80% direct contact. Use the "Triangle Technique" (move focus between eyes and forehead) to avoid an intense stare.</li>
</ul>

<div class="warning-section">
    <h5><i class="fas fa-exclamation-triangle"></i> Common Red Flags</h5>
    <ul>
        <li><strong>Weak/Clammy Handshake:</strong> Suggests nervousness or lack of confidence.</li>
        <li><strong>Checking the Watch:</strong> implies you have somewhere better to be.</li>
        <li><strong>Slouching:</strong> Communicates disinterest or low energy.</li>
    </ul>
</div>

<div class="reference-section">
    <h5><i class="fas fa-book"></i> Recommended Reading</h5>
    <ul>
        <li><a href="https://www.amazon.com/Like-Switch-Influencing-People-Thinking/dp/1476754489" target="_blank">The Like Switch</a> by Jack Schafer (Ex-FBI agent on rapport)</li>
        <li><a href="https://www.amazon.com/Presence-Bringing-Boldest-Biggest-Challenges/dp/1478930166" target="_blank">Presence</a> by Amy Cuddy</li>
    </ul>
</div>

<div class="links-section">
    <h5><i class="fas fa-link"></i> Useful Resources</h5>
    <ul>
        <li><a href="https://www.ted.com/talks/amy_cuddy_your_body_language_may_shape_who_you_are" target="_blank">TED Talk: Your Body Language May Shape Who You Are</a></li>
        <li><a href="https://hbr.org/2011/02/the-science-of-first-impressions" target="_blank">HBR: The Science of First Impressions</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'Strategic Research & Preparation',
                    'duration': '40 min',
                    'content': '''
<h3><i class="fas fa-search"></i> The Research Advantage</h3>
<p>Thorough preparation separates good candidates from great ones. This systematic approach ensures you know more about the company than most employees and demonstrates genuine interest.</p>

<div class="tip-section">
    <h5><i class="fas fa-lightbulb"></i> The "Deep Dive" Technique</h5>
    <p>Don't just read the "About Us" page. Read their <strong>Investor Relations</strong> page (10-K reports) if public, or <strong>Crunchbase</strong> if a startup. Know their revenue model, recent acquisitions, and biggest threats.</p>
</div>

<h4>Company Intelligence Gathering</h4>
<ul>
    <li><strong>Financial Health:</strong> Revenue trends, stock performance (1-year view), major investments.</li>
    <li><strong>Culture Deep-Dive:</strong> Glassdoor reviews (sort by "Recent"), LinkedIn tenure of employees (do people stay?), social media tone.</li>
    <li><strong>Leadership:</strong> Who are the C-level execs? Watch their recent interviews or podcasts to understand their vision.</li>
</ul>

<h4>Role Mastery Framework</h4>
<ul>
    <li><strong>Job Description Analysis:</strong> Highlight every verb (e.g., "Manage", "Design", "Analyze"). Prepare a specific story for each.</li>
    <li><strong>The "Pain Point" Hypothesis:</strong> Every job exists to solve a problem. Identify what pain this role solves for the manager and frame your answers as the solution.</li>
</ul>

<div class="checklist-section">
    <h5><i class="fas fa-check-circle"></i> Pre-Interview Checklist</h5>
    <ul>
        <li>[ ] 5 printed copies of resume on high-quality paper</li>
        <li>[ ] 10 thoughtful questions prepared for the interviewer</li>
        <li>[ ] Route planned with traffic buffer (arrive 15 mins early)</li>
        <li>[ ] LinkedIn profiles of interviewers reviewed</li>
        <li>[ ] "Tell me about yourself" pitch practiced (30s, 60s, 90s versions)</li>
    </ul>
</div>

<div class="links-section">
    <h5><i class="fas fa-tools"></i> Research Toolkit</h5>
    <ul>
        <li><a href="https://www.sec.gov/edgar/searchedgar/companysearch" target="_blank">SEC Edgar (Public Filings)</a></li>
        <li><a href="https://www.crunchbase.com/" target="_blank">Crunchbase (Startup Data)</a></li>
        <li><a href="https://trends.google.com/" target="_blank">Google Trends (Market Interest)</a></li>
        <li><a href="https://www.glassdoor.com/" target="_blank">Glassdoor (Culture Reviews)</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'Mastering Different Interview Formats',
                    'duration': '45 min',
                    'content': '''
<h3><i class="fas fa-shapes"></i> Adapting to Every Style</h3>
<p>Different formats require different strategies. Master each to excel regardless of the setting.</p>

<h4>1. Phone Screen (The Gatekeeper)</h4>
<p><strong>Goal:</strong> Prove you are sane, qualified, and affordable.</p>
<ul>
    <li><strong>Strategy:</strong> Stand up while talking to increase energy. Smile (it changes your voice).</li>
    <li><strong>Cheat Sheet:</strong> Have your resume and key stats taped to the wall in front of you.</li>
</ul>

<h4>2. Video Interview (The New Standard)</h4>
<ul>
    <li><strong>Eye Contact:</strong> Look at the <em>camera lens</em>, not the screen. Stick a googly eye near the lens to remind you.</li>
    <li><strong>Lighting:</strong> Light source should be <em>behind</em> the camera, facing you. No windows behind your back (silhouette effect).</li>
    <li><strong>Background:</strong> Clean, professional, or a high-quality blur. Remove distractions.</li>
</ul>

<h4>3. The Panel (The Gauntlet)</h4>
<p><strong>Challenge:</strong> Managing multiple personalities.</p>
<ul>
    <li><strong>The "Lighthouse" Technique:</strong> When answering, start eye contact with the asker, sweep across the group, and finish back on the asker.</li>
    <li><strong>Name Mapping:</strong> Write down names/positions immediately in your notebook layout matching their seating.</li>
</ul>

<div class="warning-section">
    <h5><i class="fas fa-bug"></i> Technical Failures</h5>
    <p>Always have a backup plan. If Zoom fails, have your phone ready to dial in immediately. "I'm having technical trouble, switching to phone" shows problem-solving skills, not failure.</p>
</div>

<div class="links-section">
    <h5><i class="fas fa-laptop-code"></i> Practice Tools</h5>
    <ul>
        <li><a href="https://zoom.us/test" target="_blank">Zoom Test Meeting</a></li>
        <li><a href="https://www.pramp.com/" target="_blank">Pramp (Mock Interviews)</a></li>
        <li><a href="https://interviewbuddy.in/" target="_blank">InterviewBuddy</a></li>
    </ul>
</div>
'''
                },
            ]
        },
        'behavioral-mastery': {
            'title': 'Behavioral Interview Mastery',
            'icon': '⭐',
            'description': 'Perfect the STAR method and storytelling techniques',
            'duration': '2-3 hours',
            'difficulty': 'Intermediate',
            'color': '#10b981',
            'lessons': [
                {
                    'id': 1,
                    'title': 'STAR Method Framework Mastery',
                    'duration': '30 min',
                    'content': '''
<h3><i class="fas fa-star"></i> The STAR Method Explained</h3>
<p>The STAR method is not just a format; it's a story arc. It ensures you provide evidence, not just claims.</p>

<h4>S - Situation (10%)</h4>
<p>Set the scene briefly. "In my role as Lead Dev at XYZ Corp, we faced a critical database failure during Black Friday..."</p>

<h4>T - Task (10%)</h4>
<p>What was your specific responsibility? "I needed to restore service within 1 hour while minimizing data loss..."</p>

<h4>A - Action (60% - The Meat)</h4>
<p><strong>Crucial:</strong> Use "I", not "We". This is about <em>your</em> contribution.</p>
<ul>
    <li>"I diagnosed the deadlock..."</li>
    <li>"I coordinated with the infra team..."</li>
    <li>"I implemented a hotfix..."</li>
</ul>

<h4>R - Result (20% - The "So What?")</h4>
<p>Quantify the outcome. Numbers speak louder than adjectives.</p>
<ul>
    <li>"Restored service in 14 minutes."</li>
    <li>"Saved an estimated $50k in lost revenue."</li>
    <li>"Implemented a new protocol that prevented recurrence for 12 months."</li>
</ul>

<div class="tip-section">
    <h5><i class="fas fa-bullseye"></i> Pro Tip: The "Learning" Add-on</h5>
    <p>Add an <strong>"L"</strong> (STAR-L). Briefly mention what you learned. It shows a growth mindset and maturity.</p>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'Building Your Story Bank',
                    'duration': '35 min',
                    'content': '''
<h3><i class="fas fa-database"></i> Your Personal Story Database</h3>
<p>Don't memorize answers to 100 questions. Memorize <strong>6-8 adaptable stories</strong> that can answer <em>any</em> question.</p>

<h4>The 6 Essential Stories</h4>
<ol>
    <li><strong>The Conflict:</strong> A disagreement with a coworker/boss and how you resolved it diplomatically.</li>
    <li><strong>The Failure:</strong> A genuine mistake, how you fixed it, and what you changed to prevent it.</li>
    <li><strong>The Leadership:</strong> A time you stepped up (even without a title) to drive a result.</li>
    <li><strong>The Innovation:</strong> A time you improved a process or saved money/time.</li>
    <li><strong>The Pressure:</strong> Handling a tight deadline or crisis.</li>
    <li><strong>The "Above & Beyond":</strong> Exceeding expectations for a client or team.</li>
</ol>

<div class="checklist-section">
    <h5><i class="fas fa-tasks"></i> Story Polishing Checklist</h5>
    <ul>
        <li>[ ] Does it have a clear conflict/challenge?</li>
        <li>[ ] Is the "Action" section focused on ME, not WE?</li>
        <li>[ ] Is the result quantified ($, %, hours)?</li>
        <li>[ ] Can I tell it in under 2 minutes?</li>
    </ul>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'Mastering Common Behavioral Questions',
                    'duration': '40 min',
                    'content': '''
<h3><i class="fas fa-comments"></i> Decoding the Questions</h3>
<p>Interviewers ask specific questions to test specific traits. Understand the code.</p>

<h4>1. "Tell me about a time you failed."</h4>
<p><strong>What they want:</strong> Self-awareness, resilience, ability to learn.</p>
<p><strong>Red Flag:</strong> "I never fail" or "I worked too hard" (humblebrag).</p>
<p><strong>Strategy:</strong> Admit a real mistake (not a fatal one), focus heavily on the fix and the lesson.</p>

<h4>2. "Describe a conflict with a coworker."</h4>
<p><strong>What they want:</strong> Emotional intelligence (EQ), conflict resolution.</p>
<p><strong>Strategy:</strong> Focus on the <em>issue</em>, not the <em>person</em>. Show you can compromise for the business goal.</p>

<h4>3. "Why do you want to work here?"</h4>
<p><strong>What they want:</strong> Cultural fit, genuine interest.</p>
<p><strong>Strategy:</strong> Connect your personal values/goals with the company's mission. "I've always been passionate about [Mission], and I admire how you [Specific Achievement]..."</p>

<div class="links-section">
    <h5><i class="fas fa-external-link-alt"></i> Question Banks</h5>
    <ul>
        <li><a href="https://www.themuse.com/advice/behavioral-interview-questions-answers-examples" target="_blank">The Muse: 30 Behavioral Questions</a></li>
        <li><a href="https://www.indeed.com/career-advice/interviewing/how-to-use-the-star-method" target="_blank">Indeed STAR Guide</a></li>
    </ul>
</div>
'''
                },
            ]
        },
        'technical-excellence': {
            'title': 'Technical Interview Excellence',
            'icon': '💻',
            'description': 'Ace coding challenges and technical assessments',
            'duration': '3-4 hours',
            'difficulty': 'Advanced',
            'color': '#8b5cf6',
            'lessons': [
                {
                    'id': 1,
                    'title': 'Technical Problem-Solving Strategy',
                    'duration': '50 min',
                    'content': '''
<h3><i class="fas fa-chess"></i> The UMPIRE Method</h3>
<p>Never jump straight into coding. Use a structured approach to show your thought process.</p>

<h4>U - Understand</h4>
<p>Ask clarifying questions. "Are inputs always positive?", "Can the array be empty?", "What about memory constraints?"</p>

<h4>M - Match</h4>
<p>Match the problem to a pattern: "This looks like a sliding window problem" or "This is a graph traversal."</p>

<h4>P - Plan</h4>
<p>Write pseudocode or comments. Get buy-in from the interviewer: "Does this logic look sound to you?"</p>

<h4>I - Implement</h4>
<p>Write clean code. Use descriptive variable names (<code>userIndex</code> vs <code>i</code>). Modularize with helper functions.</p>

<h4>R - Review & E - Evaluate</h4>
<p>Dry run your code with a sample case. Analyze Time (Big O) and Space complexity explicitly.</p>

<div class="tip-section">
    <h5><i class="fas fa-comment-dots"></i> Think Out Loud</h5>
    <p>Silence is your enemy. If you are stuck, say "I'm thinking about using a Hash Map here to optimize lookup, but I'm worried about space..." The interviewer can't help you if they don't know your thoughts.</p>
</div>

<div class="links-section">
    <h5><i class="fas fa-code"></i> Practice Platforms</h5>
    <ul>
        <li><a href="https://leetcode.com/" target="_blank">LeetCode (Standard)</a></li>
        <li><a href="https://www.hackerrank.com/" target="_blank">HackerRank</a></li>
        <li><a href="https://codesignal.com/" target="_blank">CodeSignal</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'Data Structures & Algorithms Mastery',
                    'duration': '60 min',
                    'content': '''
<h3><i class="fas fa-project-diagram"></i> Core Concepts Checklist</h3>
<p>You must be fluent in these basics. If you stumble here, advanced topics won't save you.</p>

<h4>Essential Data Structures</h4>
<ul>
    <li><strong>Arrays/Strings:</strong> Two pointers, Sliding Window.</li>
    <li><strong>Hash Maps:</strong> O(1) lookups. Know when to use them for frequency counting.</li>
    <li><strong>Linked Lists:</strong> Fast/Slow pointer (Floyd's Cycle Finding).</li>
    <li><strong>Trees/Graphs:</strong> BFS vs DFS. Know when to use which (Shortest path vs Exhaustive search).</li>
</ul>

<h4>The "Big O" Cheat Sheet</h4>
<ul>
    <li><strong>O(1):</strong> Constant (Hash Map lookup)</li>
    <li><strong>O(log n):</strong> Logarithmic (Binary Search)</li>
    <li><strong>O(n):</strong> Linear (Iterating an array)</li>
    <li><strong>O(n log n):</strong> Log Linear (Efficient Sorting like Merge Sort)</li>
    <li><strong>O(n²):</strong> Quadratic (Nested loops - avoid if possible!)</li>
</ul>

<div class="reference-section">
    <h5><i class="fas fa-university"></i> Top Resources</h5>
    <ul>
        <li><a href="https://www.coursera.org/specializations/algorithms" target="_blank">Stanford Algorithms (Coursera)</a></li>
        <li><a href="https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/" target="_blank">MIT 6.006 Intro to Algorithms</a></li>
        <li><a href="https://visualgo.net/en" target="_blank">VisuAlgo (Visualizing DS/A)</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'System Design Fundamentals',
                    'duration': '55 min',
                    'content': '''
<h3><i class="fas fa-server"></i> Designing for Scale</h3>
<p>For mid-to-senior roles, this is often the dealbreaker. Move from "making it work" to "making it scale".</p>

<h4>The 4-Step Framework</h4>
<ol>
    <li><strong>Clarify Requirements:</strong> Functional (Users can post tweets) & Non-Functional (Highly available, eventual consistency ok).</li>
    <li><strong>High-Level Design:</strong> Draw the big boxes. Client -> Load Balancer -> Web Server -> Database.</li>
    <li><strong>Deep Dive:</strong> Focus on the bottleneck. "How do we handle 1M writes/second?" (Sharding, Caching, Queues).</li>
    <li><strong>Wrap Up:</strong> Discuss trade-offs. (SQL vs NoSQL, Latency vs Consistency).</li>
</ol>

<h4>Key Concepts</h4>
<ul>
    <li><strong>Load Balancing:</strong> Nginx, HAProxy. Round-robin vs Least connections.</li>
    <li><strong>Caching:</strong> Redis/Memcached. Cache-aside vs Write-through.</li>
    <li><strong>Database Sharding:</strong> Horizontal vs Vertical scaling. Consistent Hashing.</li>
    <li><strong>CAP Theorem:</strong> You can only pick 2: Consistency, Availability, Partition Tolerance.</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-book-reader"></i> Must-Read</h5>
    <ul>
        <li><a href="https://github.com/donnemartin/system-design-primer" target="_blank">The System Design Primer (GitHub)</a></li>
        <li><a href="http://highscalability.com/" target="_blank">High Scalability Blog</a></li>
        <li><a href="https://aws.amazon.com/architecture/" target="_blank">AWS Architecture Center</a></li>
    </ul>
</div>
'''
                },
            ]
        },
        'communication-confidence': {
            'title': 'Communication & Confidence',
            'icon': '🗣️',
            'description': 'Build unshakeable confidence and communication skills',
            'duration': '2-3 hours',
            'difficulty': 'Intermediate',
            'color': '#f59e0b',
            'lessons': [
                {
                    'id': 1,
                    'title': 'Verbal Communication Excellence',
                    'duration': '40 min',
                    'content': '''
<h3><i class="fas fa-microphone-alt"></i> Speaking with Impact</h3>
<p>It's not just what you say, but how you say it.</p>

<h4>The 3 Ps of Voice</h4>
<ul>
    <li><strong>Pace:</strong> Slow down. Nervous people speed up. Speaking slowly signals confidence and authority.</li>
    <li><strong>Pitch:</strong> End sentences with a downward inflection. Upward inflection sounds like a question (uncertainty).</li>
    <li><strong>Pause:</strong> embrace silence. A 2-second pause before answering a tough question makes you look thoughtful, not stumped.</li>
</ul>

<h4>Eliminating Weak Language</h4>
<p>Stop sabotaging yourself with "hedging" words.</p>
<ul>
    <li>Avoid: "I think," "Maybe," "Sort of," "Just."</li>
    <li>Use: "I believe," "Based on my experience," "My recommendation is."</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-video"></i> Video Resources</h5>
    <ul>
        <li><a href="https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen" target="_blank">Julian Treasure: How to speak so that people want to listen</a></li>
        <li><a href="https://www.toastmasters.org/" target="_blank">Toastmasters International</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'Building Unshakeable Confidence',
                    'duration': '45 min',
                    'content': '''
<h3><i class="fas fa-shield-alt"></i> The Inner Game</h3>
<p>Confidence is a skill, not a trait. You can build it.</p>

<h4>Reframing the Interview</h4>
<p>Stop thinking of it as an "Interrogation." Reframe it as a <strong>"Consultation."</strong> You are a consultant there to see if you can help solve their problems. This shifts the power dynamic to a balanced one.</p>

<h4>Physical Hacks (Amy Cuddy)</h4>
<p><strong>Power Posing:</strong> Stand in a "Wonder Woman" or "Victory" pose for 2 minutes before the interview. It lowers cortisol (stress) and raises testosterone (confidence).</p>

<h4>Handling "I Don't Know"</h4>
<p>Never BS. If you don't know:</p>
<p><em>"That's a great question. I don't know the specific answer offhand, but here is how I would find out / here is my hypothesis..."</em></p>

<div class="reference-section">
    <h5><i class="fas fa-book-open"></i> Mindset Reading</h5>
    <ul>
        <li><a href="https://www.amazon.com/Mindset-Psychology-Carol-S-Dweck/dp/0345472322" target="_blank">Mindset</a> by Carol Dweck</li>
        <li><a href="https://www.headspace.com/" target="_blank">Headspace (Meditation for focus)</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'Non-Verbal Communication Mastery',
                    'duration': '35 min',
                    'content': '''
<h3><i class="fas fa-user-check"></i> Silent Signals</h3>
<p>55% of communication is non-verbal. Your body is screaming; make sure it's saying the right things.</p>

<h4>Mirroring</h4>
<p>Subtly mirror the interviewer's energy and posture. If they lean in, you lean in. It builds unconscious rapport.</p>

<h4>The "Steeple" Hand Gesture</h4>
<p>Touching fingertips together (like a steeple) signals confidence and precision. Avoid hiding hands or crossing arms (defensiveness).</p>

<h4>Facial Feedback</h4>
<p>Nodding while listening shows engagement. A genuine Duchenne smile (involving the eyes) builds trust.</p>

<div class="links-section">
    <h5><i class="fas fa-link"></i> Further Study</h5>
    <ul>
        <li><a href="https://www.ted.com/topics/body+language" target="_blank">TED Topics: Body Language</a></li>
        <li><a href="https://www.amazon.com/Definitive-Book-Body-Language/dp/0553804723" target="_blank">The Definitive Book of Body Language</a></li>
    </ul>
</div>
'''
                },
            ]
        },
        'industry-preparation': {
            'title': 'Industry-Specific Preparation',
            'icon': '🏢',
            'description': 'Tailored strategies for different industries and roles',
            'duration': '2-3 hours',
            'difficulty': 'Advanced',
            'color': '#ef4444',
            'lessons': [
                {
                    'id': 1,
                    'title': 'Technology Sector Mastery',
                    'duration': '45 min',
                    'content': '''
<h3><i class="fas fa-microchip"></i> Breaking into Tech</h3>
<p>Tech moves fast. Show you can keep up.</p>

<h4>Cultural Values</h4>
<ul>
    <li><strong>Bias for Action:</strong> Better to ship and iterate than wait for perfection.</li>
    <li><strong>Ownership:</strong> "You build it, you run it."</li>
    <li><strong>Data-Driven:</strong> Opinions are nice; data is better.</li>
</ul>

<h4>The Process</h4>
<ol>
    <li>Recruiter Screen (Culture/Basics)</li>
    <li>Technical Screen (1 Coding problem)</li>
    <li>Onsite Loop (3-5 rounds: Coding, System Design, Behavioral)</li>
</ol>

<div class="tip-section">
    <h5><i class="fas fa-code-branch"></i> GitHub Matters</h5>
    <p>For junior/mid roles, a clean GitHub with 2-3 pinned, well-documented projects works wonders. It proves passion.</p>
</div>

<div class="links-section">
    <h5><i class="fas fa-globe"></i> Tech Hubs</h5>
    <ul>
        <li><a href="https://news.ycombinator.com/" target="_blank">Hacker News (Industry Pulse)</a></li>
        <li><a href="https://www.blind.com/" target="_blank">Blind (Insider chatter)</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'Finance & Banking Excellence',
                    'duration': '40 min',
                    'content': '''
<h3><i class="fas fa-chart-line"></i> Wall Street Ready</h3>
<p>Precision, stamina, and market awareness are key.</p>

<h4>Key Competencies</h4>
<ul>
    <li><strong>Quantitative Ability:</strong> Mental math must be sharp.</li>
    <li><strong>Market Awareness:</strong> "Where is the S&P 500 today?", "What did the Fed do last meeting?" Have an opinion on the market.</li>
    <li><strong>Work Ethic:</strong> Demonstrate capacity for long hours and attention to detail.</li>
</ul>

<h4>Technical Concepts</h4>
<ul>
    <li><strong>Valuation:</strong> Walk me through a DCF. Comparable Comps. Precedent Transactions.</li>
    <li><strong>Accounting:</strong> How are the 3 financial statements linked? (e.g., Depreciation increases -> Net Income down -> Cash Flow up).</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-file-invoice-dollar"></i> Finance Resources</h5>
    <ul>
        <li><a href="https://www.wallstreetprep.com/" target="_blank">Wall Street Prep</a></li>
        <li><a href="https://www.bloomberg.com/" target="_blank">Bloomberg</a></li>
        <li><a href="https://www.investopedia.com/" target="_blank">Investopedia</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'Healthcare & Life Sciences',
                    'duration': '35 min',
                    'content': '''
<h3><i class="fas fa-heartbeat"></i> Patient-First Mindset</h3>
<p>Whether clinical or admin, the mission is life-saving.</p>

<h4>Core Values</h4>
<ul>
    <li><strong>Empathy:</strong> Understanding the patient experience.</li>
    <li><strong>Compliance:</strong> HIPAA, FDA regulations. Rules are not suggestions here.</li>
    <li><strong>Safety:</strong> Zero tolerance for error in critical paths.</li>
</ul>

<h4>Behavioral Focus</h4>
<p>Expect questions on ethics ("What would you do if you saw a colleague cut a corner?") and stress management.</p>

<div class="links-section">
    <h5><i class="fas fa-user-md"></i> Industry Bodies</h5>
    <ul>
        <li><a href="https://www.himss.org/" target="_blank">HIMSS (Health IT)</a></li>
        <li><a href="https://www.hfma.org/" target="_blank">HFMA (Finance)</a></li>
    </ul>
</div>
'''
                },
            ]
        },
        'salary-negotiation': {
            'title': 'Salary Negotiation Mastery',
            'icon': '💰',
            'description': 'Negotiate compensation packages like a professional',
            'duration': '1-2 hours',
            'difficulty': 'Advanced',
            'color': '#06b6d4',
            'lessons': [
                {
                    'id': 1,
                    'title': 'Research & Market Analysis',
                    'duration': '45 min',
                    'content': '''
<h3><i class="fas fa-search-dollar"></i> Know Your Worth</h3>
<p>Information is leverage. Never enter a negotiation without data.</p>

<h4>Sources of Truth</h4>
<ul>
    <li><strong>Levels.fyi:</strong> The bible for tech salaries (Base + Stock + Bonus).</li>
    <li><strong>H1B Data:</strong> Public filings of actual salaries paid to visa workers.</li>
    <li><strong>Glassdoor/Payscale:</strong> Good for general ranges, often lag behind market.</li>
</ul>

<h4>Understanding Total Comp (TC)</h4>
<p>Salary is just one piece.</p>
<ul>
    <li><strong>Base:</strong> Cash.</li>
    <li><strong>Equity:</strong> RSUs (Public) or Options (Private). Understand vesting (usually 4 years).</li>
    <li><strong>Sign-on Bonus:</strong> One-time cash. Easiest lever to pull.</li>
    <li><strong>Benefits:</strong> 401k match, health, remote stipend.</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-calculator"></i> Data Tools</h5>
    <ul>
        <li><a href="https://www.levels.fyi/" target="_blank">Levels.fyi</a></li>
        <li><a href="https://h1bdata.info/" target="_blank">H1B Salary Data</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'Negotiation Strategies & Tactics',
                    'duration': '50 min',
                    'content': '''
<h3><i class="fas fa-handshake"></i> The Art of the Deal</h3>
<p>Negotiation is a collaboration, not a fight. You both want you to work there.</p>

<h4>Rules of Engagement</h4>
<ol>
    <li><strong>Don't speak first:</strong> "I'm open to competitive offers based on market rates."</li>
    <li><strong>The Pause:</strong> When they give a number, count to 5. Silence makes them want to justify or improve it.</li>
    <li><strong>Counter-offer:</strong> Always counter. "I'm excited about the role. Based on X and Y, I was targeting $Z. Can we get closer to that?"</li>
</ol>

<div class="tip-section">
    <h5><i class="fas fa-lightbulb"></i> The "Competing Offer"</h5>
    <p>This is your strongest card. "Company B offered $X. I prefer you, but the gap is too large." This creates FOMO (Fear Of Missing Out).</p>
</div>

<div class="reference-section">
    <h5><i class="fas fa-book"></i> Negotiation Bible</h5>
    <ul>
        <li><a href="https://www.amazon.com/Never-Split-Difference-Negotiating-Depended/dp/0062407805" target="_blank">Never Split the Difference</a> by Chris Voss</li>
    </ul>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'Beyond Base Salary: Total Compensation',
                    'duration': '35 min',
                    'content': '''
<h3><i class="fas fa-gift"></i> Hidden Value</h3>
<p>If the base salary is capped, pull other levers.</p>

<h4>Negotiable Perks</h4>
<ul>
    <li><strong>Start Date:</strong> Take a month off between jobs?</li>
    <li><strong>Title:</strong> "Senior Manager" vs "Manager" can mean future earnings.</li>
    <li><strong>Education Budget:</strong> $5k/year for conferences?</li>
    <li><strong>Severance:</strong> Protection if things go wrong.</li>
    <li><strong>Performance Review Cycle:</strong> Ask for a review at 6 months instead of 12 (potential raise sooner).</li>
</ul>

<div class="checklist-section">
    <h5><i class="fas fa-file-contract"></i> Offer Review Checklist</h5>
    <ul>
        <li>[ ] Is the bonus guaranteed or discretionary?</li>
        <li>[ ] What is the vesting schedule for stock?</li>
        <li>[ ] Is there a clawback clause on the sign-on bonus?</li>
        <li>[ ] Get everything in writing!</li>
    </ul>
</div>
'''
                },
            ]
        },
    }

    module_data = modules_content.get(module_id)
    if not module_data:
        flash('Training module not found.', 'error')
        return redirect(url_for('student.training_modules'))
    
    return render_template('student/training_module_detail.html', module=module_data, module_id=module_id)

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

@student_bp.route('/training-module/<module_id>/lesson/<int:lesson_id>')
@student_required
def training_lesson_detail(module_id, lesson_id):
    """Individual lesson view with comprehensive content."""
    # This would contain the full lesson content
    # For now, redirect to module detail
    return redirect(url_for('student.training_module_detail', module_id=module_id))