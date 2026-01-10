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
            'description': 'Master the essential skills every successful candidate needs to stand out.',
            'duration': '3-4 hours',
            'difficulty': 'Beginner',
            'lessons_count': 7,
            'color': '#6366f1',
            'preview': 'Go beyond basics. Learn the psychology of first impressions, strategic company intelligence, and how to craft a professional narrative that resonates with HR recruiters.'
        },
        {
            'id': 'behavioral-mastery',
            'title': 'Behavioral Interview Mastery',
            'icon': '⭐',
            'description': 'Perfect the STAR+R method and advanced storytelling techniques.',
            'duration': '2-3 hours',
            'difficulty': 'Intermediate',
            'lessons_count': 5,
            'color': '#10b981',
            'preview': 'Engineering high-impact answers using the STAR+R framework. Build a versatile 6-story bank and learn to handle "weakness" and "conflict" questions with high emotional intelligence.'
        },
        {
            'id': 'technical-excellence',
            'title': 'Technical Interview Excellence',
            'icon': '💻',
            'description': 'Ace coding challenges and high-level technical assessments.',
            'duration': '3-4 hours',
            'difficulty': 'Advanced',
            'lessons_count': 5,
            'color': '#8b5cf6',
            'preview': 'Master the UMPIRE method for problem-solving, deep dive into system design for global scale, and learn the "Radio DJ" technique for collaborative coding.'
        },
        {
            'id': 'communication-confidence',
            'title': 'Communication & Confidence',
            'icon': '🗣️',
            'description': 'Project authority and build instant rapport with any interviewer.',
            'duration': '2-3 hours',
            'difficulty': 'Intermediate',
            'lessons_count': 5,
            'color': '#f59e0b',
            'preview': 'Control the room with the 3 Ps of vocal authority. Master non-verbal signals, overcome imposter syndrome, and win the "pre-interview" with smart small talk.'
        },
        {
            'id': 'industry-preparation',
            'title': 'Industry-Specific Preparation',
            'icon': '🏢',
            'description': 'Tailored strategies for Tech, Finance, Healthcare, and Consulting.',
            'duration': '2-3 hours',
            'difficulty': 'Advanced',
            'lessons_count': 4,
            'color': '#ef4444',
            'preview': 'Get the "Insider POV" from specialized HR recruiters. Understand the unique values, terminologies, and "fit" tests for the world\'s most competitive industries.'
        },
        {
            'id': 'salary-negotiation',
            'title': 'Salary Negotiation Mastery',
            'icon': '💰',
            'description': 'Maximize your total compensation like a professional negotiator.',
            'duration': '1-2 hours',
            'difficulty': 'Advanced',
            'lessons_count': 5,
            'color': '#06b6d4',
            'preview': 'Learn data-driven negotiation using market benchmarks. Understand the "Total Compensation" equation and master the art of the counter-offer and graceful resignation.'
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
            'description': 'Master the essential skills every successful candidate needs to stand out from the crowd and impress HR recruiters.',
            'duration': '3-4 hours',
            'difficulty': 'Beginner',
            'color': '#6366f1',
            'lessons': [
                {
                    'id': 1,
                    'title': 'The Psychology of First Impressions & Professional Gravity',
                    'duration': '45 min',
                    'content': '''
<h3><i class="fas fa-brain"></i> The Neuroscience of the First 7 Seconds</h3>
<p>In the world of recruitment, the "Halo Effect" is a cognitive bias where our overall impression of a person influences how we feel and think about their character. Research from Harvard Business School and Princeton confirms that humans decide on trustworthiness and competence within milliseconds. By the 7-second mark, the interviewer has already formed a "Working Hypothesis" about you. Your goal for the rest of the interview is either to confirm a positive hypothesis or to fight an uphill battle against a negative one.</p>

<div class="tip-section">
    <h5><i class="fas fa-user-tie"></i> HR Recruiter Inner Monologue: The "Representation" Test</h5>
    <p><strong>Recruiter Secret:</strong> When you walk into the room (or join the Zoom call), I'm asking myself: "Can I put this person in front of our most demanding client or our most critical VP?" If you look disheveled, lack energy, or can't hold eye contact, the answer is "No." I'm not just hiring a skill set; I'm hiring a representative of our company brand. I want to see "Professional Gravity"—a combination of composure, preparation, and quiet confidence.</p>
</div>

<h4>1. Visual Architecture: Dressing with Intent</h4>
<p>Professional attire is a tool of communication. It signals respect for the opportunity and an understanding of the environment.</p>
<ul>
    <li><strong>The 10% Culture Rule:</strong> Research the company culture via LinkedIn or Instagram. Your goal is to dress 10-15% more formal than the "average Friday" in that office. If they wear t-shirts, you wear a polo and chinos. If they wear business casual, you wear a blazer.</li>
    <li><strong>Color Psychology in the Boardroom:</strong> 
        <ul>
            <li><em>Navy Blue:</em> Trust, stability, and teamwork. The safest and most effective color.</li>
            <li><em>Charcoal Gray:</em> Maturity and efficiency. Excellent for technical roles.</li>
            <li><em>Black:</em> Authority and leadership. Use for senior-level positions.</li>
            <li><em>White:</em> Precision and cleanliness. A crisp white shirt is non-negotiable.</li>
        </ul>
    </li>
    <li><strong>The "Detail" Audit:</strong> HR recruiters notice the things you think they don't. Scuffed shoes, wrinkled collars, or chipped nail polish suggest a lack of "Attention to Detail"—a trait critical in almost every job.</li>
</ul>

<h4>2. Body Language: The Silent Narrative of Success</h4>
<p>Your body speaks long before your voice does. High-power posing and non-verbal cues can actually change your body chemistry, lowering cortisol (stress) and increasing testosterone (confidence).</p>
<ul>
    <li><strong>The Power Entrance:</strong> Stop before the door. Take a deep breath. Shoulders back, chest open. Walk to the chair with a deliberate pace. Do not "scurry."</li>
    <li><strong>The Micro-Expression Mirror:</strong> Subtle mirroring of the interviewer's posture (if they lean in, you lean in) builds subconscious rapport. It signals: "We are on the same wavelength."</li>
    <li><strong>The "Triangle" Eye Contact:</strong> To avoid staring aggressively, move your gaze in a small triangle between the left eye, right eye, and mouth. This feels natural and shows you are actively engaged.</li>
    <li><strong>Hand Placement:</strong> Keep hands visible. Hiding hands under the table signals defensiveness or dishonesty. Resting them on the table shows you have nothing to hide.</li>
</ul>

<h4>3. The "Atmospheric" First Impression (Virtual)</h4>
<p>In a remote-first world, your background is your office. What does it say about you?</p>
<ul>
    <li><strong>Lighting:</strong> Light must be in front of you, not behind. A backlit candidate looks like they're in a witness protection program.</li>
    <li><strong>Camera Height:</strong> Position the camera at eye level. Looking down into a laptop camera creates a "Double Chin" effect and makes the interviewer feel like they're being looked down upon.</li>
    <li><strong>Sound Isolation:</strong> Use a dedicated microphone. Poor audio is more mentally taxing for a recruiter than poor video.</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-graduation-cap"></i> High-Value Resources for Deep Learning</h5>
    <ul>
        <li><a href="https://www.ted.com/talks/amy_cuddy_your_body_language_may_shape_who_you_are" target="_blank">TED: Your Body Language Shapes Who You Are (Amy Cuddy)</a></li>
        <li><a href="https://hbr.org/2011/02/the-science-of-first-impressions" target="_blank">HBR: The Science of First Impressions</a></li>
        <li><a href="https://www.forbes.com/sites/jacquelynsmith/2013/03/11/how-to-ace-the-first-7-seconds-of-an-interview/" target="_blank">Forbes: The 7-Second Rule</a></li>
        <li><a href="https://www.scienceofpeople.com/body-language-interview-tips/" target="_blank">Science of People: 15 Body Language Secrets</a></li>
    </ul>
</div>

<div class="exercise-section">
    <h5><i class="fas fa-edit"></i> Action Item: The "Digital Mirror" Exercise</h5>
    <p>Record a 30-second video of yourself walking into a room, sitting down, and saying: "Hello, it's a pleasure to meet you. Thank you for having me today." Watch it with the sound <em>off</em>. Do you look like someone you would trust with a million-dollar project? If not, adjust your posture and try again.</p>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'Strategic Company Intelligence: Thinking Like a Shareholder',
                    'duration': '55 min',
                    'content': '''
<h3><i class="fas fa-microscope"></i> Beyond the "About Us" Page: The Intelligence Gap</h3>
<p>90% of candidates read the company's "About" page. 9% read a recent press release. The 1%—the ones who get the offer—understand the company's business model, its competitive pressures, and its future "Growth Levers." To an HR recruiter, a candidate who understands the business is a candidate who requires less training and has higher "Business Acumen."</p>

<div class="tip-section">
    <h5><i class="fas fa-lightbulb"></i> HR Recruiter POV: The "Alignment" Test</h5>
    <p>When I ask "What do you know about us?", I'm not looking for a Wikipedia summary. I'm looking for <strong>Value Alignment</strong>. I want to know if you understand our "North Star" metric. If you can say, "I noticed you're pivoting from B2B to B2C, and that's exciting because my experience in user acquisition directly supports that transition," you've just moved to the top of my list.</p>
</div>

<h4>Level 1: The Business Model Deep-Dive</h4>
<p>You must be able to answer the "Golden Question": <em>How does this company make money?</em></p>
<ul>
    <li><strong>Revenue Streams:</strong> Is it subscription-based (SaaS)? Transactional? Advertising-driven? Each model requires a different mindset (Retention vs. Volume vs. Engagement).</li>
    <li><strong>The Customer Avatar:</strong> Who is the hero of their story? Is it the CTO of a Fortune 500 company or a Gen Z consumer? Research their pain points.</li>
    <li><strong>Market Position:</strong> Are they the "Disruptor" (low cost/high innovation) or the "Incumbent" (high trust/premium)?</li>
</ul>

<h4>Level 2: The "CEO Mindset" Research (10-K & Beyond)</h4>
<p>If the company is public, you have access to their "Cheat Sheet": the Annual Report (10-K).</p>
<ul>
    <li><strong>The Risk Factors Section:</strong> Read this first. It tells you exactly what the company is worried about (e.g., supply chain issues, regulatory changes, aggressive competitors). Reference these in your questions.</li>
    <li><strong>Earnings Calls:</strong> Listen to the last quarter's earnings call (available on their "Investor Relations" page). What are the analysts asking? What are the "wins" the CEO is bragging about?</li>
    <li><strong>The Competitor Landscape:</strong> Use tools like SimilarWeb or Crunchbase to see who is stealing their traffic or funding. Knowing the "Enemy" makes you a better "Ally."</li>
</ul>

<h4>Level 3: Cultural Archeology</h4>
<p>Culture isn't what's written on the walls; it's how people behave when the boss isn't looking.</p>
<ul>
    <li><strong>LinkedIn Employee Pulse:</strong> Look at the "People" tab. Where do they come from? (e.g., Do they all come from Ivy Leagues or big tech?) What is the average tenure? Long tenure = High loyalty.</li>
    <li><strong>The "Medium" Deep-Dive:</strong> Look for the company's engineering or design blogs. This shows you their actual problem-solving process and the "Tech Stack" or "Ops Model" they value.</li>
</ul>

<div class="checklist-section">
    <h5><i class="fas fa-clipboard-list"></i> The "High-Stakes" Research Checklist</h5>
    <ul>
        <li>[ ] I can name the company's CEO, CFO, and the Head of the Department I'm applying to.</li>
        <li>[ ] I know the company's top 3 products and their primary revenue model.</li>
        <li>[ ] I have read the last 3 press releases and understand the "Why" behind them.</li>
        <li>[ ] I can name their top 2 competitors and 1 way this company is better.</li>
        <li>[ ] I have identified 1 recent challenge the company faced and have a thought on how to help.</li>
    </ul>
</div>

<div class="links-section">
    <h5><i class="fas fa-search-plus"></i> Advanced Research Toolkit</h5>
    <ul>
        <li><a href="https://www.crunchbase.com/" target="_blank">Crunchbase</a> - Track funding, acquisitions, and leadership changes for startups.</li>
        <li><a href="https://www.similarweb.com/" target="_blank">SimilarWeb</a> - Analyze any company's digital footprint and competitor traffic.</li>
        <li><a href="https://builtwith.com/" target="_blank">BuiltWith</a> - See the exact technology stack any company is using.</li>
        <li><a href="https://www.glassdoor.com/" target="_blank">Glassdoor (Advanced Search)</a> - Look for themes in reviews.</li>
    </ul>
</div>

<div class="exercise-section">
    <h5><i class="fas fa-pen-nib"></i> Action Item: The "3x3" Strategy</h5>
    <p>Identify 3 recent "News Items" about the company and prepare 3 "Value-Add" questions based on them. Example: "I saw you recently expanded into the European market. How is that impacting your local customer support strategy?"</p>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'Tell Me About Yourself: Your Master Narrative',
                    'duration': '50 min',
                    'content': '''
<h3><i class="fas fa-comments"></i> The First Move: Winning the Narrative Battle</h3>
<p>This is not a question; it's an <strong>Icebreaker Audition</strong>. HR recruiters use this to test your "Communication ROI"—can you deliver maximum value in minimum time? If you spend 5 minutes talking about your childhood, you've already demonstrated a lack of professional focus. If you give a 20-second summary, you lack depth. The "Sweet Spot" is a 90-second professional trailer of your career.</p>

<div class="tip-section">
    <h5><i class="fas fa-bullseye"></i> HR Recruiter POV: The "Problem Solver" Filter</h5>
    <p>I'm not looking for a chronological history of your life. I'm looking for the <strong>"Connecting Thread."</strong> I want to see that every step in your career (including your education) was a deliberate move toward becoming the person who can solve <em>my</em> current problems. Show me you are a high-potential asset, not just a job-seeker.</p>
</div>

<h4>The "Present-Past-Future" (PPF) Framework</h4>
<p>This is the industry-standard structure for high-impact introductions.</p>
<ul>
    <li><strong>The Present (25%): The Hook.</strong> 
        <br>State your current title and your "Main Superpower." 
        <br><em>Example:</em> "I'm a Full-Stack Developer specializing in high-load React applications, currently helping [Company X] reduce their page load times by 40%."</li>
    <li><strong>The Past (50%): The Proof.</strong> 
        <br>Mention 2-3 key milestones that prove your expertise. Focus on <em>results</em>, not just responsibilities. 
        <br><em>Example:</em> "Before this, I led a team of 4 at [Startup Y], where we built a payment gateway from scratch that processed $2M in its first month."</li>
    <li><strong>The Future (25%): The Why.</strong> 
        <br>Connect your journey to <em>this</em> specific role. Why them? Why now?
        <br><em>Example:</em> "While I love my current role, I've followed [Your Company] for a year, and your move into AI-driven analytics perfectly aligns with my passion for data integrity. I'm here to bring that 'scale-first' mindset to your core product team."</li>
</ul>

<h4>The "Hero's Journey" Technique</h4>
<p>Human brains are wired for stories. Instead of listing skills, frame your career as a series of solved challenges.</p>
<ul>
    <li><strong>The Catalyst:</strong> What made you interested in this field?</li>
    <li><strong>The Conflict:</strong> What's the hardest problem you've solved?</li>
    <li><strong>The Resolution:</strong> How are you better now because of it?</li>
</ul>

<div class="warning-section">
    <h5><i class="fas fa-exclamation-triangle"></i> The "Narrative Killers": What to Avoid</h5>
    <ul>
        <li><strong>The "Resume Reciter":</strong> Don't just read your resume. They have it in front of them. Give the "Director's Commentary."</li>
        <li><strong>The "Modesty Trap":</strong> This is the only time in your life where "bragging" is a requirement. Use "I led," "I built," "I achieved."</li>
        <li><strong>The "Personal Detour":</strong> Avoid talking about hobbies, family, or personal struggles.</li>
    </ul>
</div>

<div class="links-section">
    <h5><i class="fas fa-video"></i> Master the Opening</h5>
    <ul>
        <li><a href="https://www.youtube.com/watch?v=mmVnOnm6PTo" target="_blank">The Perfect 'Tell Me About Yourself' Answer</a> - A step-by-step video guide.</li>
        <li><a href="https://hbr.org/2019/08/how-to-respond-to-tell-me-about-yourself" target="_blank">HBR: The Science of Storytelling</a> - How to make your professional narrative stick.</li>
        <li><a href="https://www.themuse.com/advice/tell-me-about-yourself-interview-question-answer-examples" target="_blank">The Muse: 4 Example Scripts</a> - Tailored for different career stages.</li>
        <li><a href="https://www.forbes.com/sites/ashiraprossack1/2018/05/29/how-to-answer-tell-me-about-yourself/" target="_blank">Forbes: The 2-Minute Rule</a> - Controlling the clock.</li>
    </ul>
</div>

<div class="exercise-section">
    <h5><i class="fas fa-microphone-alt"></i> Action Item: The "Elevator Pitch" Recording</h5>
    <p>Write your script using the PPF framework. Record it on your phone. Listen for "Filler Words". Practice until you can deliver it while walking—it needs to be "Muscle Memory".</p>
</div>
'''
                },
                {
                    'id': 4,
                    'title': 'Resume Walkthrough: Mapping Your Career ROI',
                    'duration': '45 min',
                    'content': '''
<h3><i class="fas fa-map-signs"></i> Guiding the Recruiter: Beyond the Bullet Points</h3>
<p>When a recruiter says, "Walk me through your resume," they aren't asking for a summary. They are asking for <strong>Strategic Justification</strong>. Every job you took, every project you joined, and even every "gap" should have a logical, growth-oriented explanation. HR looks for "intentionality"—are you someone who happens to things, or someone who things happen to?</p>

<h4>1. The "Logic of the Move"</h4>
<p>For every transition on your resume, prepare a "Growth Anchor."
    <br>❌ "I left because the pay was bad."
    <br>✅ "I reached a technical ceiling in my previous role and sought a position where I could lead cross-functional teams and own the product roadmap."
</p>

<h4>2. The "Impact Mapping" Framework</h4>
<p>Turn "Duties" into "Achievements" using the <strong>Action + Context = Result</strong> formula.</p>
<ul>
    <li><strong>Action:</strong> What did YOU do? (e.g., Optimized, Negotiated, Architected).</li>
    <li><strong>Context:</strong> What was the scale or difficulty? (e.g., $5M budget, 10-person team, legacy codebase).</li>
    <li><strong>Result:</strong> What was the tangible benefit? (e.g., 20% cost reduction, 15% faster delivery, 5-star rating).</li>
</ul>

<div class="tip-section">
    <h5><i class="fas fa-search-dollar"></i> HR Recruiter POV: The "Profit & Loss" Mindset</h5>
    <p>Every hire is a financial risk. I'm looking for evidence that you are a <strong>Value Creator</strong>. If you can't quantify your impact on your resume, I assume you didn't have any. I want to see numbers, percentages, and dollar signs. "Improved efficiency" is a phrase; "Reduced processing time from 4 days to 4 hours" is a hire.</p>
</div>

<h4>3. Handling "The Gaps" and "The Hops"</h4>
<p>HR recruiters are trained to spot "Red Flags." Address them before we even ask.</p>
<ul>
    <li><strong>Employment Gaps:</strong> Focus on "Upskilling." "I took 6 months to complete a specialized certification in AWS Architecture and did pro-bono consulting for two non-profits."</li>
    <li><strong>Short Tenures:</strong> Explain as "Strategic Projects" or "Contract-to-Hire" if possible, or focus on the <em>intensity</em> of the work done during that short time.</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-file-invoice"></i> Resources for Resume Mastery</h5>
    <ul>
        <li><a href="https://www.google.com/about/careers/how-we-hire/resume/" target="_blank">Google: How we hire (Resume Tips)</a> - From the world's most selective recruiter.</li>
        <li><a href="https://medium.com/swlh/how-to-quantify-your-resume-bullets-when-you-dont-work-with-numbers-77a834e062c3" target="_blank">Medium: Quantifying Impact for Non-Math Roles</a> - Excellent for creative and HR roles.</li>
        <li><a href="https://www.overleaf.com/gallery/tagged/cv" target="_blank">Overleaf: LaTeX CV Templates</a> - Professional and ATS-friendly look.</li>
        <li><a href="https://www.jobscan.co/" target="_blank">JobScan</a> - Match your resume to the job description.</li>
    </ul>
</div>
'''
                },
                {
                    'id': 5,
                    'title': 'The Hybrid Master: Thriving in Video, Phone, & In-Person Stages',
                    'duration': '50 min',
                    'content': '''
<h3><i class="fas fa-laptop-code"></i> Medium Mastery: Adapting Your Performance</h3>
<p>Modern hiring is an endurance race with different terrains. A "Phone Screen" is about energy and voice; a "Video Call" is about staging and micro-expressions; an "In-Person Meeting" is about presence and spatial awareness. The ideal student is a <strong>Communication Chameleon</strong>, maintaining a consistent core message while adjusting the delivery for the medium.</p>

<div class="tip-section">
    <h5><i class="fas fa-video-slash"></i> HR Recruiter POV: The "Crisis" Test</h5>
    <p>I once had a candidate's internet cut out during a final interview. Instead of panicking, they immediately called my cell phone, apologized, and finished the interview via audio while they fixed their router. <strong>I hired them on the spot.</strong> Why? Because they showed me exactly how they would handle a crisis. Technical glitches are opportunities to show Resilience.</p>
</div>

<h4>1. Stage 1: The Video Interview (The Digital First Impression)</h4>
<ul>
    <li><strong>Eye Contact 2.0:</strong> Look at the <em>camera lens</em>, not the screen. If you look at the person's eyes on the screen, it looks like you're looking down. Put a small sticker of a "Smiley Face" next to your camera lens to remind you where to look.</li>
    <li><strong>The "Three-Point" Lighting:</strong> You don't need a studio. Just ensure your primary light source is <em>behind</em> the camera, facing you. Avoid "Raccoon Eyes" caused by overhead lights.</li>
    <li><strong>The "Stage" Design:</strong> A cluttered background suggests a cluttered mind. Use a neutral background or a very subtle professional bookshelf. Avoid "Blur" if possible—it looks like you're hiding something.</li>
</ul>

<h4>2. Stage 2: The Phone Screen (The Gatekeeper)</h4>
<ul>
    <li><strong>Stand Up to Speak:</strong> Standing opens your diaphragm. Your voice becomes deeper, more resonant, and more energetic. Recruiter's hear the difference.</li>
    <li><strong>The "Smile" Sound:</strong> Scientists have proven that "Smiling" changes the shape of your mouth and the tone of your voice. The listener can "hear" the warmth.</li>
    <li><strong>Cheat Sheets:</strong> The best part of a phone interview? You can have your resume, the job description, and your "Story Bank" taped to the wall in front of you. Use them!</li>
</ul>

<h4>3. Stage 3: The In-Person Panel (The Final Gauntlet)</h4>
<ul>
    <li><strong>The "Sweep" Technique:</strong> When asked a question by one person, start your answer looking at them, but "sweep" the room to include everyone else. End your answer looking back at the person who asked.</li>
    <li><strong>The "Water" Tactic:</strong> If you get a "Killer Question," take a slow, deliberate sip of water. It gives you 5-10 seconds of "Thinking Time" without an awkward silence.</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-tools"></i> Virtual Interview Toolkit</h5>
    <ul>
        <li><a href="https://www.speedtest.net/" target="_blank">Speedtest by Ookla</a> - Ensure your upload speed is at least 5Mbps.</li>
        <li><a href="https://www.themuse.com/advice/video-interview-tips" target="_blank">The Muse: 20 Video Interview Tips</a> - A comprehensive checklist.</li>
        <li><a href="https://hbr.org/2020/03/how-to-nail-a-video-interview" target="_blank">HBR: How to Nail a Video Interview</a> - Remote connection tips.</li>
        <li><a href="https://www.youtube.com/watch?v=S5m-EAbv7nU" target="_blank">YouTube: Dressing for Video Interviews</a> - Color and pattern advice.</li>
    </ul>
</div>
'''
                },
                {
                    'id': 6,
                    'title': 'The Strategic Follow-Up: Closing the Deal with Value',
                    'duration': '40 min',
                    'content': '''
<h3><i class="fas fa-envelope-open-text"></i> From "Thank You" to "You're Hired"</h3>
<p>Most candidates think the interview ends when the Zoom window closes. They are wrong. The follow-up is your <strong>Final Pitch</strong>. It is the last piece of data the recruiter has before they make a decision. A generic "Thanks for your time" is a wasted opportunity. A "Strategic Follow-Up" provides new value and reinforces your fit.</p>

<div class="tip-section">
    <h5><i class="fas fa-user-clock"></i> HR Recruiter POV: The "Enthusiasm" Factor</h5>
    <p>I am often choosing between two equally qualified candidates. The tie-breaker is almost always <strong>"Who wants this more?"</strong> A follow-up that references a specific problem we discussed—and maybe even suggests a solution—proves you are already doing the job in your head. That makes you a "Low-Risk" hire.</p>
</div>

<h4>The "3-Component" Follow-Up Framework</h4>
<ol>
    <li><strong>The Specific Connection:</strong> Mention something unique you discussed. "I really enjoyed our conversation about the challenges of scaling your Postgres database."</li>
    <li><strong>The Value Reinforcement:</strong> Briefly connect a skill back to that conversation. "Reflecting on our talk, my experience with sharding at [Previous Company] would be directly applicable to the Q3 goals you mentioned."</li>
    <li><strong>The "Bonus" Asset:</strong> (Optional but powerful) "I found this article/case study on that topic we discussed and thought you might find it interesting."</li>
</ol>

<h4>The Timing Hierarchy</h4>
<ul>
    <li><strong>The 2-Hour Window:</strong> Send a quick "Thank You" to the recruiter to confirm you're still interested.</li>
    <li><strong>The 12-24 Hour Window:</strong> Send the detailed, personalized note to the hiring manager.</li>
    <li><strong>The 7-Day Window:</strong> The "Polite Ping" if you haven't heard back. "I'm still very excited about this role and wanted to see if there are any updates or further information I can provide."</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-copy"></i> Templates & Professional Etiquette</h5>
    <ul>
        <li><a href="https://hbr.org/2021/05/how-to-write-a-thank-you-email-after-an-interview" target="_blank">HBR: How to Write a Thank-You Email</a> - The professional standard.</li>
        <li><a href="https://www.themuse.com/advice/the-perfect-template-for-your-followup-thankyou-email" target="_blank">The Muse: Follow-up Templates</a> - Scenarios for after every interview type.</li>
        <li><a href="https://www.glassdoor.com/blog/guide/thank-you-email-after-interview/" target="_blank">Glassdoor: The Follow-Up Guide</a> - Timing and frequency advice.</li>
        <li><a href="https://www.forbes.com/sites/ashiraprossack1/2019/01/24/how-to-follow-up-after-an-interview/" target="_blank">Forbes: The Art of the Follow-Up</a> - How to be persistent without being annoying.</li>
    </ul>
</div>
'''
                },
                {
                    'id': 7,
                    'title': 'The Resilience Mindset: Turning Rejection into a Return Offer',
                    'duration': '40 min',
                    'content': '''
<h3><i class="fas fa-seedling"></i> Failing Forward: The Professional Growth Loop</h3>
<p>In a competitive market, you will get rejected. Even the most talented people on earth have a "Wall of Rejection." The difference between a "Candidate" and a "Professional" is how they handle the word "No." Rejection is not a personal failure; it is <strong>Market Feedback</strong>. HR recruiters keep "Silver Medalists" on file for months. How you handle the rejection determines if you stay at the top of that list.</p>

<div class="tip-section">
    <h5><i class="fas fa-users-cog"></i> HR Recruiter POV: The "Emotional Intelligence" Test</h5>
    <p>I once had a candidate send me the most graceful rejection response I've ever seen. They thanked me for the feedback, congratulated the successful candidate, and asked if we could stay in touch. <strong>Six months later, another role opened up. I didn't even post the job. I called them directly and hired them.</strong> Their resilience was more impressive than any resume bullet point.</p>
</div>

<h4>The "Professional Grace" Response Protocol</h4>
<p>When you get the "Thank you for your interest, but..." email, do this:</p>
<ul>
    <li><strong>Step 1: The "Immediate Gratitude":</strong> Respond within 24 hours. "Thank you for letting me know. While I'm disappointed because I truly admire [Company], I appreciate the transparency."</li>
    <li><strong>Step 2: The "Feedback Request":</strong> Ask for <em>one</em> specific area of improvement. "If there is one technical skill or competency where I could improve to be a better fit for [Company] in the future, I'd value your insight."</li>
    <li><strong>Step 3: The "Network Bridge":</strong> Ask to connect on LinkedIn. This turns a "No" into a "Not Yet."</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-heart"></i> Resilience & Mindset Resources</h5>
    <ul>
        <li><a href="https://www.ted.com/talks/angela_lee_duckworth_grit_the_power_of_passion_and_perseverance" target="_blank">TED: Grit (Angela Duckworth)</a> - Why persistence beats talent every time.</li>
        <li><a href="https://hbr.org/2015/01/how-to-bounce-back-from-a-job-rejection" target="_blank">HBR: Bouncing Back from Rejection</a> - Practical steps for recovery.</li>
        <li><a href="https://www.psychologytoday.com/us/blog/the-right-mindset/202008/how-deal-job-rejection" target="_blank">Psychology Today: The Science of Rejection</a> - Managing the emotional impact.</li>
        <li><a href="https://www.linkedin.com/pulse/how-turn-job-rejection-opportunity-stay-touch-lindsey-pollak/" target="_blank">LinkedIn: Turning Rejection into Opportunity</a> - Networking after a "No."</li>
    </ul>
</div>

<div class="exercise-section">
    <h5><i class="fas fa-shield-alt"></i> Action Item: The "Future-Proof" Response Template</h5>
    <p>Draft a "Graceful Rejection Response" right now, while you're in a good headspace. Save it in your notes. When you eventually get a rejection, you won't have to fight your emotions to write a professional reply—you'll just hit "Send."</p>
</div>
'''
                }
            ]
        },
        'behavioral-mastery': {
            'title': 'Behavioral Interview Mastery',
            'icon': '⭐',
            'description': 'Master the art of storytelling and prove your value through concrete evidence that resonates with HR professionals.',
            'duration': '3-4 hours',
            'difficulty': 'Intermediate',
            'color': '#10b981',
            'lessons': [
                {
                    'id': 1,
                    'title': 'The STAR+R Framework: Engineering High-Impact Answers',
                    'duration': '50 min',
                    'content': '''
<h3><i class="fas fa-star"></i> Beyond the Basics: The Pro STAR Method</h3>
<p>The STAR method is not just a structure; it's a way to prove your competency through data. HR recruiters use "Behavioral-Based Interviewing" because past behavior is the best predictor of future performance. We're adding a fifth letter: <strong>R for Reflection</strong>. This is the difference between an "Experienced" candidate and a "High-Potential" candidate.</p>

<div class="tip-section">
    <h5><i class="fas fa-user-check"></i> HR Recruiter POV: The "Evidence" Check</h5>
    <p>I am literally checking off boxes in my head (or on a scorecard). If you give me a vague answer like 'I'm a good team player,' I have zero evidence to present to the hiring manager. If you tell me a STAR story about how you resolved a specific conflict using data and diplomacy, I have "Courtroom Evidence" to justify your hire. <strong>Give me the data I need to fight for you.</strong></p>
</div>

<h4>1. S - Situation (10%): The Strategic Context</h4>
<p>Keep it brief. "While working as a Junior Dev at X during a major system migration..." Avoid unnecessary details. Only give the context needed to understand the stakes. <strong>HR Secret:</strong> If you spend 2 minutes on the situation, I've already lost interest.</p>

<h4>2. T - Task (10%): The Stakes</h4>
<p>What was the specific problem? "Our database was crashing every Friday at 5 PM, affecting 5,000 users and costing us $20k per hour in lost revenue." <strong>Stating the cost makes the task real.</strong></p>

<h4>3. A - Action (60%): The "Hero" Narrative</h4>
<p>This is where 90% of candidates fail. You must use "I," not "We." 
    <ul>
        <li><strong>The Diagnostic:</strong> How did you identify the root cause? "I analyzed the logs using Splunk and identified a memory leak in the batch processing script."</li>
        <li><strong>The Strategy:</strong> "I proposed a two-stage fix: an immediate patch to prevent crashes and a long-term refactor."</li>
        <li><strong>The Execution:</strong> "I led the implementation of the patch, coordinating with the DevOps team for a midnight deploy."</li>
    </ul>
</p>

<h4>4. R - Result (20%): The Data-Driven Payoff</h4>
<p>Quantify everything. 
    <ul>
        <li>"I reduced crash frequency by 98%."</li>
        <li>"I saved the company an estimated $100k in monthly revenue loss."</li>
        <li>"The solution was adopted as the new standard for all batch jobs."</li>
    </ul>
</p>

<h4>5. R - Reflection (The 1% Move)</h4>
<p>What did you learn? "This taught me that 'Done is better than Perfect' during a crisis, but 'Scalability is non-negotiable' in the long run." This shows the <strong>Growth Mindset</strong> HR loves.</p>

<div class="links-section">
    <h5><i class="fas fa-external-link-alt"></i> STAR Mastery Resources</h5>
    <ul>
        <li><a href="https://www.indeed.com/career-advice/interviewing/how-to-use-the-star-method" target="_blank">Indeed: The Definitive Guide to STAR</a></li>
        <li><a href="https://hbr.org/2019/02/how-to-answer-behavioral-interview-questions" target="_blank">HBR: Behavioral Interviewing at Top Companies</a></li>
        <li><a href="https://www.theladders.com/career-advice/how-to-use-the-star-method-to-ace-your-next-job-interview" target="_blank">The Ladders: Advanced STAR Techniques</a></li>
        <li><a href="https://www.youtube.com/watch?v=W60XGf04O6Q" target="_blank">YouTube: STAR Method Examples</a></li>
    </ul>
</div>
'''
                },
                        {
                            'id': 2,
                            'title': 'The "Swiss Army Knife" Story Bank: 6 Stories, 100 Answers',
                            'duration': '55 min',
                            'content': '''
<h3><i class="fas fa-database"></i> Versatility Over Memorization</h3>
<p>Don't try to memorize 50 answers. Prepare <strong>6 versatile "Anchor Stories"</strong> that can be adapted to hundreds of questions. HR recruiters often ask "Reverse Questions" (e.g., "Tell me about a time you <em>didn't</em> meet a deadline"). Having a modular story bank allows you to pivot instantly.</p>

<h4>The Essential 6 Stories:</h4>
<ol>
    <li><strong>The "Big Win" (Achievement):</strong> A time you exceeded expectations. (Tests: Drive, Standards)</li>
    <li><strong>The "Mistake" (Accountability):</strong> A time you failed and owned it. (Tests: Integrity, Growth)</li>
    <li><strong>The "Conflict" (Diplomacy):</strong> A disagreement with a peer or boss. (Tests: EQ, Professionalism)</li>
    <li><strong>The "Initiative" (Leadership):</strong> A time you acted without being asked. (Tests: Ownership)</li>
    <li><strong>The "Pivot" (Adaptability):</strong> A time you had to change course quickly. (Tests: Resilience)</li>
    <li><strong>The "Above & Beyond" (Customer/Team):</strong> A time you helped someone else succeed. (Tests: Culture Fit)</li>
</ol>

<div class="tip-section">
    <h5><i class="fas fa-lightbulb"></i> HR Recruiter POV: The "Pivot" Test</h5>
    <p>I might ask the same question in different ways. "Tell me about a time you failed" vs. "Tell me about a time you received tough feedback." If you have your 'Mistake' story ready, you can easily pivot it. I'm looking for <strong>Consistency</strong>. If your story changes too much when I rephrase the question, I start to doubt your authenticity.</p>
</div>

<h4>Case Study: The "Mistake" Story (Good vs. Great)</h4>
<ul>
    <li><strong>Good:</strong> "I made a typo in a report, my boss caught it, I fixed it and said sorry." (Result: Neutral. You just did your job.)</li>
    <li><strong>Great:</strong> "I missed a critical bug in a release because I rushed the QA process to meet a deadline. I immediately informed the PM, worked 48 hours to fix it, and then <strong>built a new automated test suite</strong> to ensure that specific bug could never happen again." (Result: Hire. You solved the problem <em>and</em> the system.)</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-book-open"></i> Storytelling Mastery</h5>
    <ul>
        <li><a href="https://hbr.org/2014/07/the-irresistible-power-of-storytelling-as-a-strategic-business-tool" target="_blank">HBR: The Strategic Power of Storytelling</a></li>
        <li><a href="https://www.themuse.com/advice/the-6-stories-you-need-to-have-in-your-back-pocket-for-any-interview" target="_blank">The Muse: The 6 Stories for Your Back Pocket</a></li>
        <li><a href="https://www.forbes.com/sites/carolinecenizalevine/2021/01/24/the-6-types-of-stories-you-need-for-a-successful-job-interview/" target="_blank">Forbes: The 6 Story Types</a></li>
    </ul>
</div>
'''
                        },
                        {
                            'id': 3,
                            'title': 'The Honesty Test: Handling "Weakness" & "Failure"',
                            'duration': '45 min',
                            'content': '''
<h3><i class="fas fa-shield-virus"></i> Authenticity vs. Strategy</h3>
<p>When HR asks "What is your greatest weakness?", they aren't looking for a reason to disqualify you. They are looking for <strong>Self-Awareness</strong>. The worst answer is "I'm a perfectionist" or "I work too hard." These are "Fake Weaknesses" and HR hates them.</p>

<div class="tip-section">
    <h5><i class="fas fa-user-shield"></i> HR Recruiter POV: The Integrity Check</h5>
    <p>We value someone who knows their limits more than someone who pretends to be perfect. A candidate who admits to a real mistake and shows how they learned from it is 10x more valuable than one who blames others. I want to see that you have a "Self-Correction" mechanism.</p>
</div>

<h4>The Three-Part "Mitigation" Formula</h4>
<ol>
    <li><strong>The Admission:</strong> State a <em>real</em> but non-essential weakness. (e.g., "I used to struggle with delegating tasks because I wanted to ensure every detail was perfect.")</li>
    <li><strong>The Action:</strong> What are you doing <em>today</em> to fix it? (e.g., "I started using Trello to track my team's progress and set up weekly 15-minute check-ins.")</li>
    <li><strong>The Result:</strong> How has it improved? (e.g., "Now, I'm able to manage 30% more projects because I've empowered my team to own their segments.")</li>
</ol>

<h4>Case Study: Recovering from Failure</h4>
<p>Failure isn't the problem; <strong>Stagnation</strong> is. When telling a failure story, focus on the <em>Pivot</em>. What did the failure teach you that a success never could? HR looks for "Post-Traumatic Growth" in a career context.</p>

<div class="links-section">
    <h5><i class="fas fa-video"></i> Authenticity & Growth</h5>
    <ul>
        <li><a href="https://www.ted.com/talks/brene_brown_the_power_of_vulnerability" target="_blank">TED: The Power of Vulnerability (Brené Brown)</a></li>
        <li><a href="https://hbr.org/2019/03/how-to-respond-to-what-is-your-greatest-weakness" target="_blank">HBR: Responding to 'Greatest Weakness'</a></li>
        <li><a href="https://www.themuse.com/advice/how-to-answer-what-is-your-greatest-weakness" target="_blank">The Muse: Weakness Answer Examples</a></li>
        <li><a href="https://www.forbes.com/sites/jackkelly/2020/02/14/how-to-answer-the-interview-question-what-is-your-greatest-failure/" target="_blank">Forbes: Answering the 'Failure' Question</a></li>
    </ul>
</div>
'''
                        },
                        {
                            'id': 4,
                            'title': 'Conflict Resolution: Proving Emotional Intelligence',
                            'duration': '35 min',
                            'content': '''
        <h3><i class="fas fa-handshake"></i> Diplomacy in the Workplace</h3>
        <p>Conflict is inevitable. HR recruiters want to know: Are you a "Firefighter" or a "Firestarter"? This is a test of your <strong>Emotional Intelligence (EQ)</strong>.</p>
        
        <h4>The De-Escalation Framework</h4>
        <ul>
            <li><strong>Step 1: Focus on the Goal:</strong> Remind the interviewer that the conflict was about the <em>work</em>, not the <em>person</em>.</li>
            <li><strong>Step 2: Empathy First:</strong> Show you tried to understand the other person's perspective. "I sat down with them to understand why they felt the deadline was unrealistic."</li>
            <li><strong>Step 3: The Compromise:</strong> Explain the middle ground you found.</li>
            <li><strong>Step 4: The Professional Outcome:</strong> The project was successful and the relationship was preserved.</li>
        </ul>
        
        <div class="tip-section">
            <h5><i class="fas fa-users"></i> HR Recruiter POV: Culture Fit vs. Culture Add</h5>
            <p>We don't want 'Yes Men.' We want people who can disagree productively. If you can show me how you handled a disagreement without burning a bridge, you've just proven you're a high-EQ hire.</p>
        </div>
        '''
                        },
                        {
                            'id': 5,
                            'title': 'The "Curveball" Questions: Logic Under Pressure',
                            'duration': '30 min',
                            'content': '''
        <h3><i class="fas fa-brain"></i> Thinking Out Loud</h3>
        <p>"How many piano tuners are there in Chicago?" or "If you were an animal, which one would you be?" HR uses these to test your <strong>composure</strong> and <strong>logical framework</strong>.</p>
        
        <h4>Strategy for Logic Puzzles</h4>
        <ol>
            <li><strong>Clarify:</strong> Ask a question back. "Are we including the suburbs of Chicago?"</li>
            <li><strong>Structure:</strong> Explain your approach. "I'll start by estimating the population, then the percentage of households with pianos..."</li>
            <li><strong>Calculate:</strong> Do the math out loud. It doesn't have to be perfect; the <em>process</em> is what matters.</li>
        </ol>
        
        <h4>Strategy for Personality Curveballs</h4>
        <p>Align your answer with the job. 
            <br><em>Applying for Sales?</em> "I'd be a Wolf—I'm collaborative but focused on the target."
            <br><em>Applying for Engineering?</em> "I'd be an Elephant—I have a great memory for detail and I'm very steady under pressure."</p>
        
        <div class="tip-section">
            <h5><i class="fas fa-vial"></i> HR Recruiter POV: The Stress Test</h5>
            <p>I don't actually care how many piano tuners there are. I want to see if you panic when you don't know the answer. Stay calm, smile, and show me your brain at work.</p>
        </div>
        '''
                        }
                    ]
                },
                'technical-excellence': {
            'title': 'Technical Interview Excellence',
            'icon': '💻',
            'description': 'Master the technical assessments and coding challenges with a strategic mindset that impresses both engineers and HR.',
            'duration': '3-4 hours',
            'difficulty': 'Advanced',
            'color': '#8b5cf6',
            'lessons': [
                {
                    'id': 1,
                    'title': 'The UMPIRE Method: A Framework for Coding Success',
                    'duration': '60 min',
                    'content': '''
<h3><i class="fas fa-chess-knight"></i> Solving Problems, Not Just Writing Code</h3>
<p>Technical interviews are often less about the final code and more about your <strong>problem-solving process</strong>. The UMPIRE method is used by top-tier tech companies to evaluate how candidates handle complex, ambiguous problems.</p>

<h4>The 6 Steps of UMPIRE:</h4>
<ul>
    <li><strong>1. Understand:</strong> Ask clarifying questions. What are the input types? What are the constraints? (e.g., "Will the array be sorted?" "What is the maximum size?")</li>
    <li><strong>2. Match:</strong> Match the problem to a pattern (e.g., Two Pointers, BFS, Dynamic Programming).</li>
    <li><strong>3. Plan:</strong> Write pseudocode <em>before</em> you write a single line of real code. This shows the interviewer you have a strategy.</li>
    <li><strong>4. Implement:</strong> Write the actual code. Keep it clean and follow naming conventions.</li>
    <li><strong>5. Review:</strong> Walk through your code with a sample input. Spot bugs before the interviewer does.</li>
    <li><strong>6. Evaluate:</strong> Discuss the Time and Space complexity (Big O). Can you optimize it?</li>
</ul>

<div class="tip-section">
    <h5><i class="fas fa-microchip"></i> HR Recruiter POV: The "Code Quality" Signal</h5>
    <p>We look for 'Maintainability.' If you write messy code but it works, we might pass. We want to see if you consider edge cases (null inputs, empty arrays). This tells us if you're a 'Production-Ready' engineer or just a hobbyist.</p>
</div>

<div class="links-section">
    <h5><i class="fas fa-terminal"></i> Problem Solving Resources</h5>
    <ul>
        <li><a href="https://neetcode.io/" target="_blank">NeetCode: The Best Structured DSA Path</a></li>
        <li><a href="https://leetcode.com/discuss/general-discussion/458695/dynamic-programming-patterns" target="_blank">LeetCode: Common DP Patterns</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'System Design: Thinking at Global Scale',
                    'duration': '75 min',
                    'content': '''
<h3><i class="fas fa-server"></i> Building for Millions of Users</h3>
<p>System design interviews test your ability to think about <strong>Trade-offs</strong>. There is no "perfect" solution; every decision has a cost.</p>

<h4>Core Components of a Design Answer:</h4>
<ol>
    <li><strong>Requirements Clarification:</strong> Functional vs. Non-Functional (e.g., Availability vs. Consistency).</li>
    <li><strong>Back-of-the-Envelope Estimation:</strong> How much storage? How much bandwidth?</li>
    <li><strong>High-Level Design:</strong> Load Balancers, Web Servers, Database, Cache.</li>
    <li><strong>Detailed Deep Dive:</strong> Sharding strategies, API design, security.</li>
</ol>

<div class="tip-section">
    <h5><i class="fas fa-project-diagram"></i> HR Recruiter POV: The "Seniority" Indicator</h5>
    <p>System design performance is how we differentiate between Junior, Mid, and Senior levels. Seniors talk about 'Single Points of Failure' and 'Scalability Bottlenecks.' Juniors focus only on the code. Show us you understand the big picture.</p>
</div>

<div class="links-section">
    <h5><i class="fas fa-book"></i> The "Gold Standard" Resources</h5>
    <ul>
        <li><a href="https://github.com/donnemartin/system-design-primer" target="_blank">The System Design Primer (GitHub) - Must Read</a></li>
        <li><a href="https://www.educative.io/courses/grokking-the-system-design-interview" target="_blank">Grokking the System Design Interview</a></li>
        <li><a href="https://www.youtube.com/@SystemDesignFightClub" target="_blank">YouTube: System Design Fight Club</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'Data Structures & Algorithms Cheat Sheet',
                    'duration': '55 min',
                    'content': '''
<h3><i class="fas fa-brain"></i> The Toolkit of a High-Performer</h3>
<p>You must know when and why to use specific structures. Memorization isn't enough; you need <strong>Intuition</strong>.</p>

<h4>The "Big 5" You Must Master:</h4>
<ul>
    <li><strong>Hash Maps:</strong> The most important structure. O(1) lookup. Use it to trade space for time.</li>
    <li><strong>Heaps (Priority Queues):</strong> Essential for "Top K" problems and scheduling.</li>
    <li><strong>Trees & Graphs:</strong> Master DFS and BFS. Understand the difference between Dijkstra's and A*.</li>
    <li><strong>Linked Lists:</strong> The classic test for pointer manipulation.</li>
    <li><strong>Stacks & Queues:</strong> Understanding LIFO and FIFO for processing order.</li>
</ul>

<h4>The Big O Cheat Sheet:</h4>
<table class="table table-sm mt-3">
    <thead><tr><th>Operation</th><th>Time</th><th>When to Use</th></tr></thead>
    <tbody>
        <tr><td>Binary Search</td><td>O(log n)</td><td>Searching sorted data</td></tr>
        <tr><td>Sorting</td><td>O(n log n)</td><td>Preprocessing</td></tr>
        <tr><td>Nested Loops</td><td>O(n²)</td><td>Avoid if possible</td></tr>
        <tr><td>BFS/DFS</td><td>O(V+E)</td><td>Graph traversal</td></tr>
    </tbody>
</table>
'''
                },
                {
                    'id': 4,
                    'title': 'Whiteboard Etiquette & Collaborative Coding',
                    'duration': '45 min',
                    'content': '''
<h3><i class="fas fa-chalkboard-teacher"></i> The "Radio DJ" Technique</h3>
<p>Never code in silence. A silent interview is a failed interview. You must narrate your thoughts.</p>

<h4>Why Narrate?</h4>
<ul>
    <li>It lets the interviewer "see" your logic.</li>
    <li>If you take a wrong turn, the interviewer can give you a hint. If you're silent, they can't help.</li>
    <li>It proves you can communicate technical concepts—a key requirement for team roles.</li>
</ul>

<div class="tip-section">
    <h5><i class="fas fa-headset"></i> HR Recruiter POV: The "Coachability" Test</h5>
    <p>Engineers want to work with people they can mentor or collaborate with. If you are defensive when corrected or refuse to explain your logic, you're a 'Red Flag' hire, regardless of your talent.</p>
</div>

<div class="exercise-section">
    <h5><i class="fas fa-microphone-alt"></i> Action Item: Narrated Practice</h5>
    <p>Solve a simple LeetCode problem, but record yourself explaining <em>every single line</em> as you type it. Listen back. Do you sound clear? Confident?</p>
</div>
'''
                },
                {
                    'id': 5,
                    'title': 'Explaining Technical Concepts to Stakeholders',
                    'duration': '40 min',
                    'content': '''
<h3><i class="fas fa-comments-dollar"></i> The Bridge Builder Skill</h3>
<p>The best engineers can explain an "API Timeout" to a Product Manager in a way they understand. This is the skill that leads to promotions.</p>

<h4>The Analogy Technique:</h4>
<p>Use real-world examples to explain complex tech:
    <ul>
        <li><strong>Database Index:</strong> Like a book's index—helps you find the page without reading every chapter.</li>
        <li><strong>API:</strong> Like a waiter in a restaurant—you (the client) tell them what you want, they go to the kitchen (server), and bring back the food.</li>
        <li><strong>Load Balancer:</strong> Like a traffic cop—distributing cars (requests) to different lanes so no one gets stuck.</li>
    </ul>
</p>

<div class="tip-section">
    <h5><i class="fas fa-user-friends"></i> HR Recruiter POV: The "Leadership" Potential</h5>
    <p>When we hire for growth, we look for 'T-Shaped' individuals—deep technical skills combined with broad communication skills. If you can bridge the gap between Tech and Business, you're on the fast track to Lead/Manager roles.</p>
</div>
'''
                }
            ]
        },
        'communication-confidence': {
            'title': 'Communication & Confidence',
            'icon': '🗣️',
            'description': 'Project authority and build rapport through advanced communication techniques that make you the obvious hire.',
            'duration': '2-3 hours',
            'difficulty': 'Intermediate',
            'color': '#f59e0b',
            'lessons': [
                {
                    'id': 1,
                    'title': 'The 3 Ps of Vocal Authority: Pace, Pitch, Pause',
                    'duration': '45 min',
                    'content': '''
<h3><i class="fas fa-microphone-alt"></i> Controlling the Room with Your Voice</h3>
<p>In a high-stakes interview, <em>how</em> you say something is often as important as <em>what</em> you say. HR recruiters judge your leadership potential and confidence through your vocal delivery.</p>

<h4>Mastering the 3 Ps:</h4>
<ul>
    <li><strong>1. Pace:</strong> Nervous candidates talk fast. Confident candidates talk at 140-160 words per minute. Slowing down signals that you are in control of your thoughts.</li>
    <li><strong>2. Pitch:</strong> Avoid "Up-talking" (ending every sentence with a rising tone that sounds like a question). It makes you sound uncertain. Use a "Downward Inflection" to sound authoritative.</li>
    <li><strong>3. Pause:</strong> The "Strategic Pause" (2-3 seconds) before an important point builds anticipation and shows you aren't afraid of silence. It also gives you time to breathe.</li>
</ul>

<div class="tip-section">
    <h5><i class="fas fa-volume-up"></i> HR Recruiter POV: The "Gravitas" Factor</h5>
    <p>We look for 'Executive Presence.' If a candidate is breathless and squeaky, we subconsciously worry they won't be able to handle pressure in front of clients. A steady, calm voice suggests a steady, calm mind.</p>
</div>

<div class="links-section">
    <h5><i class="fas fa-play-circle"></i> Voice Mastery Resources</h5>
    <ul>
        <li><a href="https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen" target="_blank">TED: How to Speak So People Want to Listen (Julian Treasure)</a></li>
        <li><a href="https://hbr.org/2014/06/the-voice-of-authority" target="_blank">HBR: The Voice of Authority (Scientific Analysis)</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'Active Listening & Mirroring: The Rapport Secret',
                    'duration': '40 min',
                    'content': '''
<h3><i class="fas fa-ear-listen"></i> Becoming an Expert Listener</h3>
<p>Interviewing is a two-way street. HR professionals want to hire someone they <em>like</em> working with. Rapport is built when the interviewer feels heard and understood.</p>

<h4>Techniques for Instant Connection:</h4>
<ul>
    <li><strong>The "L-Shaped" Listen:</strong> Lean in slightly, Look at the speaker, and Listen for the emotion behind the words.</li>
    <li><strong>Subtle Mirroring:</strong> If they lean back, you lean back after a few seconds. If they use specific terminology (e.g., "Our North Star metric"), use those same words in your answer. This creates a subconscious feeling of "sameness."</li>
    <li><strong>The Clarification Loop:</strong> "So, if I understand correctly, the main challenge for this team is [X]. Is that right?" This proves you are engaged.</li>
</ul>

<div class="tip-section">
    <h5><i class="fas fa-heart"></i> HR Recruiter POV: The "Beer Test"</h5>
    <p>It's an old cliché, but we often ask ourselves: 'Would I want to be stuck in an airport with this person for 4 hours?' If you're purely transactional and don't listen, the answer is 'No.' Show us your human side.</p>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'Non-Verbal Mastery: The 55-38-7 Rule',
                    'duration': '40 min',
                    'content': '''
<h3><i class="fas fa-user-check"></i> Communicating Without Words</h3>
<p>Albert Mehrabian's famous study suggests that 55% of communication is body language, 38% is tone of voice, and only 7% is the actual words. Are your signals consistent?</p>

<h4>The "Confident Candidate" Posture:</h4>
<ul>
    <li><strong>Open Stance:</strong> Don't cross your arms; it looks defensive. Rest your hands on the table or your lap.</li>
    <li><strong>The "Steeple" Hand Gesture:</strong> Bringing your fingertips together shows intellectual confidence.</li>
    <li><strong>Node & Smile:</strong> Use "Active Nods" to encourage the interviewer. It makes them feel like they are doing a good job too!</li>
</ul>

<div class="tip-section">
    <h5><i class="fas fa-eye"></i> HR Recruiter POV: Spotting Incongruence</h5>
    <p>If you say you're 'passionate about data' but you're looking at the floor with slumped shoulders, I don't believe you. Your body must tell the same story as your mouth.</p>
</div>

<div class="links-section">
    <h5><i class="fas fa-book-open"></i> Visual Learning</h5>
    <ul>
        <li><a href="https://www.scienceofpeople.com/body-language-interview-tips/" target="_blank">Science of People: 15 Body Language Tips for Interviews</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 4,
                    'title': 'Overcoming Imposter Syndrome & Anxiety',
                    'duration': '50 min',
                    'content': '''
<h3><i class="fas fa-shield-alt"></i> The Inner Game of Success</h3>
<p>Even the most successful executives feel like "frauds" sometimes. The key isn't to eliminate the fear; it's to manage it so it doesn't manage you.</p>

<h4>Tactics to Beat the Jitters:</h4>
<ul>
    <li><strong>Box Breathing:</strong> 4 seconds in, 4 hold, 4 out, 4 hold. This physically resets your nervous system before you walk into the room.</li>
    <li><strong>The "I'm Excited" Reframing:</strong> Physiologically, fear and excitement feel identical (fast heart rate, sweating). Instead of saying "I'm nervous," tell yourself "I'm excited for this opportunity."</li>
    <li><strong>The Value-Focus:</strong> Shift your focus from "What do they think of me?" to "How can I help them solve their problems?" It takes the pressure off your ego.</li>
</ul>

<div class="tip-section">
    <h5><i class="fas fa-award"></i> HR Recruiter POV: Why You're Already a Winner</h5>
    <p>We are busy people. We don't interview people we don't think can do the job. If you are in the room, it means you have already passed the hardest filter. You are qualified—now just show us your personality.</p>
</div>

<div class="links-section">
    <h5><i class="fas fa-video"></i> Mindset Shifts</h5>
    <ul>
        <li><a href="https://www.ted.com/talks/elizabeth_cox_what_is_imposter_syndrome_and_how_can_you_combat_it" target="_blank">TED-Ed: What is Imposter Syndrome?</a></li>
        <li><a href="https://www.apa.org/gradpsych/2013/11/fraud" target="_blank">APA: Learning to Deal with the Imposter Syndrome</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 5,
                    'title': 'The First 5 Minutes: Small Talk & "Social Lubrication"',
                    'duration': '35 min',
                    'content': '''
<h3><i class="fas fa-coffee"></i> Winning the "Pre-Interview"</h3>
<p>Small talk is the bridge between being a "Resume" and being a "Colleague." It's where the interviewer decides if they'd actually enjoy working with you for 40 hours a week.</p>

<h4>3 Safe & Smart Small Talk Topics:</h4>
<ul>
    <li><strong>The Environment:</strong> "I love the office design here—has the team been in this space long?"</li>
    <li><strong>The Commute/Location:</strong> "The area around here is growing so fast—any good lunch spots you recommend?"</li>
    <li><strong>The Interviewer's Tenure:</strong> "I saw on LinkedIn you've been here for 3 years—what's been your favorite project so far?"</li>
</ul>

<div class="tip-section">
    <h5><i class="fas fa-comment-dots"></i> HR Recruiter POV: The Cultural Indicator</h5>
    <p>I use small talk to see if you can handle 'Unstructured Time.' Many roles involve client dinners or hallway chats. If you can't hold a basic conversation for 2 minutes, I worry about your client-facing skills.</p>
</div>
'''
                }
            ]
        },
        'industry-preparation': {
            'title': 'Industry-Specific Preparation',
            'icon': '🏢',
            'description': 'Tailored strategies for Tech, Finance, Healthcare, and Consulting, designed with input from specialized HR recruiters.',
            'duration': '4-5 hours',
            'difficulty': 'Advanced',
            'color': '#ef4444',
            'lessons': [
                {
                    'id': 1,
                    'title': 'The Tech Sector: Navigating Silicon Valley Culture',
                    'duration': '55 min',
                    'content': '''
<h3><i class="fas fa-microchip"></i> Moving at the Speed of Code</h3>
<p>Tech companies value <strong>Autonomy, Speed, and "Extreme Ownership."</strong> HR recruiters in tech aren't just looking for coders; they are looking for "Force Multipliers"—people who make the whole team better through their presence and process. <strong>I want to hire someone who doesn't wait for a ticket to fix a bug.</strong></p>

<div class="tip-section">
    <h5><i class="fas fa-user-ninja"></i> HR Recruiter POV: The Tech "Force Multiplier"</h5>
    <p>I don't just care about your Python skills. I care about your 'Product Sense.' Do you understand how your code impacts the user? Do you know who our competitors are? If you're a 'Code Monkey,' you're replaceable. If you're a 'Product-Minded Engineer,' you're a unicorn. Show me you understand the <strong>Business of Technology</strong>.</p>
</div>

<h4>Key Values in Tech Interviews:</h4>
<ul>
    <li><strong>"Bias for Action":</strong> They'd rather you try and fail than wait for permission. Show this in your stories.</li>
    <li><strong>Data-Driven Decision Making:</strong> Don't just say you did something; explain <em>why</em> using metrics (e.g., "Our A/B test showed a 12% increase in CTR").</li>
    <li><strong>Scale Mindset:</strong> Can your solution handle 1 user? 1 million? 1 billion? Always mention scalability and observability.</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-external-link-square-alt"></i> Tech Insider Resources</h5>
    <ul>
        <li><a href="https://hbr.org/2019/11/how-to-land-a-job-in-tech-if-youre-not-a-techie" target="_blank">HBR: How to Land a Job in Tech</a></li>
        <li><a href="https://www.ycombinator.com/library" target="_blank">Y Combinator: Startup School Library</a></li>
        <li><a href="https://www.wired.com/story/how-to-get-a-job-at-google-meta-amazon/" target="_blank">Wired: Getting Hired at Big Tech</a></li>
        <li><a href="https://www.pramp.com/dev/tech-interview-prep" target="_blank">Pramp: Technical Interview Preparation</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'Finance & Banking: The World of High-Stakes Precision',
                    'duration': '55 min',
                    'content': '''
<h3><i class="fas fa-chart-line"></i> Rigor, Compliance, and Professional Stamina</h3>
<p>In Finance, there is <strong>Zero Tolerance for Error</strong>. Whether you're in Investment Banking, Fintech, or Corporate Finance, HR recruiters are looking for extreme attention to detail and professional stamina. <strong>I want to hire someone who checks their work three times before I see it once.</strong></p>

<div class="tip-section">
    <h5><i class="fas fa-briefcase"></i> HR Recruiter POV: The Finance "Composure" Test</h5>
    <p>We look for 'Executive Presence.' The environment can be high-pressure and the hours can be long. We want to see if you are someone who stays calm when the markets are volatile. If you're easily flustered by a tough question, I won't trust you with a multi-million dollar portfolio or a mission-critical financial system.</p>
</div>

<h4>Core Expectations in Finance:</h4>
<ul>
    <li><strong>Integrity Above All:</strong> You are handling people's money. Any hint of ethical ambiguity is an immediate rejection.</li>
    <li><strong>Quantitative Rigor:</strong> You should be able to do "Mental Math" under pressure and explain complex financial concepts (like EBITDA or NPV) simply.</li>
    <li><strong>Regulatory Awareness:</strong> Know your KYC (Know Your Customer) and AML (Anti-Money Laundering) basics. Show you understand the <strong>Cost of Non-Compliance</strong>.</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-landmark"></i> Industry Guides</h5>
    <ul>
        <li><a href="https://www.investopedia.com/financial-careers-4427763" target="_blank">Investopedia: Financial Career Paths</a></li>
        <li><a href="https://www.wallstreetoasis.com/" target="_blank">Wall Street Oasis: The IB/PE Community</a></li>
        <li><a href="https://www.efinancialcareers.com/" target="_blank">eFinancialCareers: News and Advice</a></li>
        <li><a href="https://www.bloomberg.com/learning/" target="_blank">Bloomberg: Market Concepts</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'Healthcare & Life Sciences: Mission-Driven Excellence',
                    'duration': '50 min',
                    'content': '''
<h3><i class="fas fa-heartbeat"></i> Innovation with a Patient-First Mindset</h3>
<p>Healthcare is one of the most regulated industries in the world. HR recruiters look for a blend of <strong>Technical Excellence and Deep Empathy</strong>. <strong>I want to hire someone who remembers that at the end of every line of code is a human life.</strong></p>

<div class="tip-section">
    <h5><i class="fas fa-stethoscope"></i> HR Recruiter POV: The "Why Healthcare?" Test</h5>
    <p>We ask 'Why Healthcare?' and we're looking for a deep personal connection to the field. People who are just here for the paycheck tend to burn out during long clinical trial cycles. We want people who are motivated by the fact that their work <strong>Saves Lives</strong>. Show me your mission-alignment.</p>
</div>

<h4>Healthcare Deep-Dive Areas:</h4>
<ul>
    <li><strong>Compliance & Privacy:</strong> You <em>must</em> understand HIPAA (US), GDPR (EU), and clinical trial regulations. Mention your commitment to <strong>Data Integrity</strong>.</li>
    <li><strong>Cross-Functional Collaboration:</strong> You'll work with doctors, researchers, and insurance adjusters. Can you speak "Medical," "Legal," and "Technical" fluently?</li>
    <li><strong>Long-Cycle Thinking:</strong> Product cycles in healthcare can take years. They look for <strong>Persistence and Documentation Skills</strong>.</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-microscope"></i> Healthcare Resources</h5>
    <ul>
        <li><a href="https://www.hhs.gov/hipaa/index.html" target="_blank">HHS: HIPAA Privacy Rule Summary</a></li>
        <li><a href="https://www.healthit.gov/topic/health-it-basics" target="_blank">HealthIT.gov: Basics of Health IT</a></li>
        <li><a href="https://www.mckinsey.com/industries/healthcare-systems-and-services/our-insights" target="_blank">McKinsey Healthcare Insights</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 4,
                    'title': 'Consulting: The Case Interview & Problem Architecture',
                    'duration': '60 min',
                    'content': '''
<h3><i class="fas fa-lightbulb"></i> Selling Structured Thinking</h3>
<p>Management consulting (McKinsey, BCG, Bain) values <strong>Structured Thinking</strong> above all else. They don't just want the answer; they want to see your "Mental Architecture." <strong>I want to hire someone I can put in front of a Fortune 500 CEO tomorrow.</strong></p>

<div class="tip-section">
    <h5><i class="fas fa-puzzle-piece"></i> HR Recruiter POV: The "Client-Ready" Test</h5>
    <p>We are essentially selling your brain to our clients. Professional polish, clear communication, and the ability to break down a "Wicked Problem" into MECE (Mutually Exclusive, Collectively Exhaustive) components are non-negotiable. Show me your <strong>Problem-Solving Framework</strong>.</p>
</div>

<h4>The Case Framework Essentials:</h4>
<ol>
    <li><strong>Profitability Framework:</strong> Revenue (Price x Volume) - Cost (Fixed + Variable).</li>
    <li><strong>Market Entry:</strong> Market Size, Competition, Barriers to Entry, Distribution.</li>
    <li><strong>M&A (Mergers & Acquisitions):</strong> Why buy? Is it a good price? What are the synergies?</li>
    <li><strong>The "So What?":</strong> Never just give a number. Tell me what the business should <em>do</em> about it.</li>
</ol>

<div class="links-section">
    <h5><i class="fas fa-graduation-cap"></i> Case Prep Mastery</h5>
    <ul>
        <li><a href="https://www.caseinterview.com/" target="_blank">CaseInterview.com (Victor Cheng)</a></li>
        <li><a href="https://mconsultingprep.com/" target="_blank">MConsultingPrep: Free Case Library</a></li>
        <li><a href="https://www.rocketblocks.me/" target="_blank">RocketBlocks: Consulting Case Prep</a></li>
        <li><a href="https://www.bcg.com/careers/interviewing/practice-cases" target="_blank">BCG: Interactive Practice Cases</a></li>
    </ul>
</div>
'''
                }
            ]
        },
        'salary-negotiation': {
            'title': 'Salary Negotiation Mastery',
            'icon': '💰',
            'description': 'Maximize your lifetime earnings with professional negotiation strategies that HR recruiters respect.',
            'duration': '1-2 hours',
            'difficulty': 'Advanced',
            'color': '#06b6d4',
            'lessons': [
                {
                    'id': 1,
                    'title': 'Determining Your Market Value: Data-Driven Leverage',
                    'duration': '45 min',
                    'content': '''
<h3><i class="fas fa-search-dollar"></i> Knowledge is Your Only Real Power</h3>
<p>Negotiation is not about what you <em>want</em>; it's about what the <em>market pays</em> for your specific set of skills in a specific geography. Entering a negotiation without data is like flying a plane without a dashboard. HR recruiters use sophisticated databases (like Mercer or Radford) to set their ranges. You must counter with your own data.</p>

<div class="tip-section">
    <h5><i class="fas fa-user-tag"></i> HR Recruiter POV: The "Data-Driven" Candidate</h5>
    <p>I respect a candidate who says, 'Based on my research for a Senior Software Engineer role in New York at a Series C startup, the market 25th-75th percentile range is $160k to $195k.' <strong>I can't argue with data, but I can easily dismiss a "feeling."</strong> It tells me you are professional, informed, and objective.</p>
</div>

<h4>Where to Find Accurate Compensation Data:</h4>
<ul>
    <li><strong>Levels.fyi:</strong> The gold standard for Tech and Finance. It tracks "Total Compensation" (TC), including equity and bonuses.</li>
    <li><strong>H1B Salary Database:</strong> Search public government data. Companies are required by law to report what they pay H1B holders—this is an extremely accurate "Floor" for any role.</li>
    <li><strong>LinkedIn Salary:</strong> Good for broad industry averages and seeing how years of experience correlate with pay.</li>
    <li><strong>Glassdoor:</strong> Use with caution. It's often outdated or skewed by self-reporting bias.</li>
</ul>

<h4>The "Range" Rule:</h4>
<p>Never give a single number. Always give a <strong>$20k - $30k range</strong>. Ensure the bottom of your range is a number you would be genuinely happy to accept. <strong>HR Secret:</strong> If you give me a range, I will almost always try to hit the bottom of it. Factor that into your math.</p>

<div class="links-section">
    <h5><i class="fas fa-database"></i> Compensation Intelligence</h5>
    <ul>
        <li><a href="https://www.levels.fyi/" target="_blank">Levels.fyi: The Tech Salary Bible</a></li>
        <li><a href="https://h1bdata.info/" target="_blank">H1B Salary Database: Public Payroll Data</a></li>
        <li><a href="https://www.payscale.com/personal-salary-report" target="_blank">PayScale: Personal Salary Reports</a></li>
        <li><a href="https://www.salary.com/" target="_blank">Salary.com: Industry Benchmarks</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 2,
                    'title': 'The "TC" Equation: Deciphering Total Compensation',
                    'duration': '50 min',
                    'content': '''
<h3><i class="fas fa-gift"></i> Looking Beyond the Monthly Paycheck</h3>
<p>In modern professional roles, the "Base Salary" might only represent 60% of your actual wealth creation. If you only negotiate the base, you're leaving a fortune on the table. HR recruiters often have <strong>Limited Flex</strong> on base salary but <strong>High Flex</strong> on "one-time" or "equity" components.</p>

<div class="tip-section">
    <h5><i class="fas fa-chart-pie"></i> HR Recruiter POV: The Flexibility Secret</h5>
    <p>My budget for 'Base Salary' is often strictly capped by Finance. However, I often have a pool of 'Sign-on Bonus' cash or 'Discretionary Equity' that I can use to close a deal. If I can't give you $10k more in salary, I might be able to give you $25k more in stock options. <strong>Ask me where the flexibility is.</strong></p>
</div>

<h4>The 5 Pillars of TC:</h4>
<ul>
    <li><strong>Base Salary:</strong> The guaranteed monthly cash. This determines your future raises.</li>
    <li><strong>Annual Bonus:</strong> Usually a % of base (e.g., 15%). Ask if it's based on personal performance, company performance, or both.</li>
    <li><strong>Sign-on Bonus:</strong> A one-time cash payment. Use this to bridge "Vesting Cliffs" from your previous job.</li>
    <li><strong>Equity (RSUs or Options):</strong> Shares in the company. <em>Crucial:</em> Understand the "Vesting Schedule" (usually 4 years with a 1-year cliff).</li>
    <li><strong>Benefits & Perks:</strong> 401k/PF matching, WFH stipends, gym memberships, and "Learning & Development" budgets (often $2k - $5k/year).</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-coins"></i> Equity & Bonus Guides</h5>
    <ul>
        <li><a href="https://www.holloway.com/g/equity-compensation" target="_blank">Holloway: Guide to Equity Compensation</a></li>
        <li><a href="https://carta.com/blog/equity-101-stock-option-basics/" target="_blank">Carta: Equity 101 for Employees</a></li>
        <li><a href="https://stdlaw.com/understanding-sign-on-bonuses/" target="_blank">Understanding Sign-on Bonus Clawbacks</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 3,
                    'title': 'The "Expectations" Shield: Protecting Your Leverage',
                    'duration': '40 min',
                    'content': '''
<h3><i class="fas fa-shield-alt"></i> The First Recruiter Call: The Danger Zone</h3>
<p>The "What are your salary expectations?" question usually comes in the first 15 minutes of the first call. This is a <strong>Filter</strong>, not a negotiation. If you give a number too early, you have lost your leverage. Your goal is to defer the number until they are "In Love" with you.</p>

<div class="tip-section">
    <h5><i class="fas fa-user-secret"></i> HR Recruiter POV: Why We Ask Early</h5>
    <p>We don't want to waste 10 hours of interviewer time only to find out you want $250k when our budget is $130k. If you're hesitant to give a number, I understand—but tell me at least that you're 'market-aligned' or 'flexible.' <strong>I'm looking for a reason to keep you in the process, not to lowball you.</strong></p>
</div>

<h4>The "Deflection" Script Bank:</h4>
<ul>
    <li><strong>The "Fit First" Move:</strong> "I'm really excited about the role's responsibilities. Right now, I'm focused on determining if I'm the best fit for the team. I'm sure we can reach a fair agreement once we're both sure about the partnership. What is the budget range for this position?"</li>
    <li><strong>The "Market Move":</strong> "I'm looking for a competitive package that aligns with the market rate for this level of responsibility in [City]. Do you have a range in mind?"</li>
</ul>

<h4>The "Walk-Away" Number:</h4>
<p>Before you even apply, decide on your "Walk-Away" number. This is the absolute minimum you need to live comfortably and feel valued. <strong>Never tell the recruiter this number.</strong></p>

<div class="links-section">
    <h5><i class="fas fa-microphone"></i> Negotiation Scripts</h5>
    <ul>
        <li><a href="https://fearlesssalarynegotiation.com/salary-expectations-interview-question/" target="_blank">Fearless Salary Negotiation: The expectations question</a></li>
        <li><a href="https://www.kalzumeus.com/2012/01/23/salary-negotiation/" target="_blank">Patio11's Salary Negotiation Seminal Article</a></li>
        <li><a href="https://hbr.org/2014/04/15-rules-for-negotiating-a-job-offer" target="_blank">HBR: 15 Rules for Negotiating an Offer</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 4,
                    'title': 'Tactical Negotiation: The Art of the Counter-Offer',
                    'duration': '45 min',
                    'content': '''
<h3><i class="fas fa-handshake"></i> From Offer to Agreement</h3>
<p>Negotiation is a <strong>Collaborative Problem-Solving</strong> exercise, not a confrontation. Your goal is for both sides to feel like they "Won." The most powerful tool you have is <strong>Silence</strong>.</p>

<h4>Rule #1: The "24-Hour" Pause</h4>
<p>Never accept an offer on the spot, even if it's amazing. "Thank you! I'm thrilled. Can you send the full package in writing? I'll review it and get back to you by tomorrow afternoon." This shows you are methodical and not desperate.</p>

<h4>Rule #2: The "Consolidated" Counter</h4>
<p>Gather ALL your requests (Salary, Bonus, PTO, Start Date) and present them in <strong>One Single Email or Call</strong>. Going back and forth 5 times with "just one more thing" is the fastest way to annoy an HR recruiter and have an offer rescinded.</p>

<h4>Rule #3: Use Your "Alternatives"</h4>
<p>If you have another offer, use it. "I really prefer [Your Company], but [Company B] has offered a higher base. If you can close the gap to $X, I'm ready to sign today."</p>

<div class="tip-section">
    <h5><i class="fas fa-stopwatch"></i> HR Recruiter POV: The Closing Tactic</h5>
    <p>I hate it when a candidate drags out a negotiation for a week. If you give me a 'Firm Yes' conditional on a specific, reasonable change, I will move mountains to get it approved by Finance so I can close the role. <strong>Give me a number that makes you a 'Yes' today.</strong></p>
</div>

<div class="links-section">
    <h5><i class="fas fa-play"></i> Negotiation Masterclass</h5>
    <ul>
        <li><a href="https://www.ted.com/talks/alex_carter_how_to_negotiate_successfully" target="_blank">TED: How to Negotiate Successfully (Alex Carter)</a></li>
        <li><a href="https://hbr.org/2015/06/the-right-way-to-respond-to-a-job-offer" target="_blank">HBR: The Right Way to Respond to an Offer</a></li>
        <li><a href="https://www.pon.harvard.edu/category/blog/salary-negotiation/" target="_blank">Harvard: Program on Negotiation (Salary Tips)</a></li>
    </ul>
</div>
'''
                },
                {
                    'id': 5,
                    'title': 'The Final Handshake: Signing & Professional Resignation',
                    'duration': '35 min',
                    'content': '''
<h3><i class="fas fa-signature"></i> Leaving a Legacy, Not a Mess</h3>
<p>Congratulations! You've secured the bag. Now, you need to ensure the transition is flawless. Your reputation in your industry is your most valuable long-term asset. How you leave a company is just as important as how you join one.</p>

<div class="tip-section">
    <h5><i class="fas fa-door-open"></i> HR Recruiter POV: The Bridge-Building Test</h5>
    <p>The world is small. I've seen candidates resign rudely, only to meet their old boss as a client or interviewer 3 years later. Leave on a high note, and your old company becomes part of your lifelong network. <strong>I want to hire someone who is a "Good Leaver."</strong></p>
</div>

<h4>1. Reviewing the Contract (The Fine Print)</h4>
<ul>
    <li><strong>Non-Compete Clauses:</strong> Are they enforceable in your state? Do they prevent you from working for a specific competitor?</li>
    <li><strong>Clawbacks:</strong> If you leave within 12 months, do you have to pay back your sign-on bonus or relocation costs?</li>
    <li><strong>Intellectual Property:</strong> Ensure the contract only covers work done <em>for</em> the company, not your personal side-projects.</li>
</ul>

<h4>2. The Graceful Resignation Protocol:</h4>
<ul>
    <li><strong>Tell your Manager First:</strong> Never let your boss hear it through the grapevine. Do it via Video or In-Person.</li>
    <li><strong>Keep the Letter Brief:</strong> "I'm writing to formally resign as [Title]. My last day will be [Date]. I'm grateful for the opportunity and will do everything to ensure a smooth handover."</li>
    <li><strong>The "Handover Document":</strong> Create a 5-page guide for your replacement. This is the single best way to be remembered as a "Legend" at your old company.</li>
</ul>

<div class="links-section">
    <h5><i class="fas fa-heart"></i> Professional Transition Resources</h5>
    <ul>
        <li><a href="https://hbr.org/2023/01/how-to-quit-your-job-gracefully" target="_blank">HBR: How to Quit Your Job Gracefully</a></li>
        <li><a href="https://www.themuse.com/advice/resignation-letter-template-sample" target="_blank">The Muse: Resignation Letter Templates</a></li>
        <li><a href="https://www.glassdoor.com/blog/guide/how-to-resign-from-a-job/" target="_blank">Glassdoor: The Complete Resignation Guide</a></li>
        <li><a href="https://www.linkedin.com/pulse/importance-handover-document-when-leaving-job-sarah-knight/" target="_blank">LinkedIn: The Power of the Handover Document</a></li>
    </ul>
</div>
'''
                }
            ]
        }
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