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
***The 7-Second Rule: Making Every Moment Count***

Research from Harvard Business School shows that interviewers form their first impression within 7 seconds of meeting you. This lesson teaches you how to maximize those crucial moments and create a lasting positive impact that sets the tone for your entire interview.

**Professional Appearance Mastery**

• **Dress Code Intelligence**: Research company culture thoroughly using LinkedIn employee photos, company website career pages, and Glassdoor reviews. The golden rule: dress 10-15% more formal than their standard to show respect and professionalism without appearing out of place.

• **Color Psychology in Professional Attire**: Navy blue projects trustworthiness and reliability (ideal for finance/consulting), charcoal gray shows professionalism and authority (perfect for corporate roles), while black conveys sophistication (great for creative industries). Avoid bright colors that may distract from your message.

• **Grooming Excellence Checklist**: Fresh haircut within 2 weeks of interview, trimmed and clean nails, minimal cologne/perfume (others should only smell it when very close), fresh breath with mints available, well-maintained and polished shoes, and wrinkle-free clothing.

• **Strategic Accessories**: Conservative watch (demonstrates time management skills), professional bag or briefcase, portfolio folder with 5+ copies of resume, quality pen for note-taking, and business cards if you have them.

**Body Language That Commands Respect**

• **The Power Entrance**: Walk with purpose and confidence - shoulders back, head up, confident stride. Your entrance sets the tone for the entire interview. Practice walking into a room with intention and presence.

• **Handshake Mastery**: Firm grip with web-to-web contact, 2-3 pumps maximum, maintain eye contact throughout, use your full hand (not just fingertips), and match their pressure without overdoing it.

• **Optimal Posture**: Sit forward slightly (shows engagement), keep both feet flat on floor, hands visible on table or armrests, avoid crossing arms or legs (creates barriers), and maintain an open, approachable stance.

• **Eye Contact Formula**: Maintain direct eye contact 70-80% of the time, look away naturally to avoid staring, use the triangle technique (eyes to forehead) for comfort, and remember that eye contact shows confidence and honesty.

**Voice & Presence Optimization**

• **Vocal Tonality**: Speak 10-15% slower than your normal pace (allows for better comprehension), use a slightly lower pitch to convey authority and confidence, vary your tone to maintain engagement, and practice breathing techniques to avoid nervous speech patterns.

• **Energy Matching**: Mirror the interviewer's energy level while staying authentic to yourself. If they're formal, match that tone; if they're casual, adjust accordingly while maintaining professionalism.

• **Space Awareness**: Respect personal boundaries (maintain arm's length distance), lean in slightly to show engagement without invading space, and be mindful of cultural differences in personal space preferences.

💡 **Practical Exercise:**

Practice your complete entrance routine daily for one week: knock confidently (3 firm knocks), enter with purpose, offer a warm greeting using their name, wait to be seated unless invited, and establish rapport within the first 30 seconds through genuine interest and enthusiasm.

📚 **Essential Reading:**

• "The Like Switch" by Jack Schafer - FBI techniques for building rapport
• "Presence" by Amy Cuddy - Body language and confidence building
• "The Charisma Myth" by Olivia Fox Cabane - Developing executive presence

🔗 **Additional Resources:**

• TED Talk: "Your Body Language May Shape Who You Are" by Amy Cuddy
• Harvard Business Review: "The Science of First Impressions"
• LinkedIn Learning: "Executive Presence on Video Calls"

✅ **Mastery Checklist:**

• Can enter a room with confidence and presence
• Maintains appropriate eye contact naturally
• Demonstrates professional handshake consistently
• Speaks with clear, confident voice tonality
• Adapts energy level to match interviewer appropriately
'''
                },
                {
                    'id': 2,
                    'title': 'Strategic Research & Preparation',
                    'duration': '40 min',
                    'content': '''
***The Research Advantage: Outpreparing Your Competition***

Thorough preparation separates good candidates from great ones. This systematic approach ensures you know more about the company than most employees and demonstrates genuine interest that interviewers notice and appreciate.

**Company Intelligence Gathering**

• **Financial Health Analysis**: Review annual reports (10-K forms) for revenue trends and challenges, listen to recent earnings calls for current priorities, analyze stock performance over the last 12 months, and research major investments, acquisitions, or partnerships that indicate strategic direction.

• **Culture Deep-Dive**: Study employee reviews on Glassdoor for honest insights about management and work environment, analyze company social media (LinkedIn, Twitter, Instagram) for values and personality, read "About Us" and "Careers" pages for official culture statements, and look for employee testimonials and success stories.

• **Recent Developments Research**: Set up Google News alerts for company mentions in the last 6 months, review press releases for official announcements and strategic initiatives, research product launches or service expansions, and note any awards, recognition, or industry rankings received.

• **Leadership Research**: Study LinkedIn profiles of key executives and their backgrounds, read recent interviews or articles by leadership team, review company blog posts by team members for insights into company thinking, and research any leadership changes or new hires that might indicate direction.

• **Competitive Landscape**: Identify 3-5 main competitors and their market positioning, understand the company's unique advantages and differentiators, research recent competitive moves or market share changes, and analyze industry trends affecting all players.

**Role Mastery Framework**

• **Job Description Analysis**: Identify 5-7 key requirements and prepare specific examples for each, understand both required and preferred qualifications, note any skills or technologies mentioned multiple times (these are priorities), and research the reporting structure and team dynamics.

• **Skills Gap Assessment**: Honestly evaluate your fit percentage (aim for 70%+ match), prepare to address any weaknesses with learning plans and transferable skills, identify unique strengths that set you apart, and prepare examples of rapid skill acquisition.

• **Growth Trajectory**: Understand how this role leads to your 3-5 year career goals, research typical career progression paths in this field, identify skills you'll develop in this position, and prepare questions about advancement opportunities.

• **Success Metrics**: Research how performance is measured in similar roles, understand key performance indicators (KPIs) for the position, prepare examples of how you've met similar metrics in past roles, and ask about success measurement in your interview.

**Industry Context Understanding**

• **Market Trends**: Research current challenges and opportunities in the industry, understand emerging technologies affecting the sector, stay informed about regulatory changes or compliance requirements, and know major industry events or conferences.

• **Technology Impact**: Understand how AI, automation, or digital transformation affects this role, research new tools or platforms becoming standard in the industry, identify skills that are becoming more valuable, and prepare to discuss technology adoption.

• **Future Outlook**: Study 3-5 year industry projections and implications, understand potential disruptions or growth areas, research how the company is positioning for future challenges, and prepare thoughtful questions about industry direction.

✅ **24-Hour Preparation Checklist:**

• Print 5 copies of resume on quality paper (32lb weight minimum)
• Prepare 10 thoughtful questions about the role and company
• Practice elevator pitch in 30, 60, and 90-second versions
• Plan route with backup transportation options and arrive 15 minutes early
• Prepare references list with current contact information
• Review your LinkedIn profile for consistency with resume
• Prepare portfolio with work samples if relevant to the role
• Research interviewer backgrounds if names are provided
• Prepare thoughtful questions that show deep company knowledge
• Practice key stories using STAR method framework

📚 **Research Sources Toolkit:**

• **Primary Sources**: Company website (especially "About Us," "Careers," and "News" sections), LinkedIn company page and employee profiles, SEC filings for public companies (10-K, 10-Q reports), company annual reports and investor presentations

• **Industry Intelligence**: Industry publications and trade journals, Google News alerts and recent press coverage, Crunchbase for startup funding and growth information, industry association websites and reports

• **Employee Insights**: Glassdoor for employee reviews and salary information, LinkedIn for employee backgrounds and career paths, company social media presence (Twitter, Instagram, Facebook), employee blogs and thought leadership articles

• **Competitive Analysis**: Competitor websites and recent news, industry analyst reports (Gartner, Forrester), market research reports, customer review sites for company products/services

💡 **Pro Research Tips:**

• Create a research document with sections for company, role, industry, and questions
• Use the "People Also Viewed" section on LinkedIn to find similar companies
• Set up Google Alerts for the company name 2 weeks before your interview
• Check if the company has a podcast, YouTube channel, or blog for insider insights
• Research the interviewer's background and find common connections or interests

🔗 **Additional Resources:**

• SEC.gov - Public company financial filings
• Crunchbase.com - Startup and private company information
• PitchBook - Private market intelligence
• LinkedIn Sales Navigator - Advanced people and company research
• Google Trends - Track company and industry interest over time

⚠️ **Research Red Flags:**

• Consistently negative employee reviews mentioning same issues
• High executive turnover or recent leadership departures
• Declining financial performance or missed earnings
• Negative press coverage or regulatory issues
• Lack of recent innovation or product development
'''
                },
                {
                    'id': 3,
                    'title': 'Mastering Different Interview Formats',
                    'duration': '45 min',
                    'content': '''
***Adapting to Every Interview Style***

Different interview formats require different strategies and preparation approaches. Master each format to excel regardless of the company's approach and demonstrate your adaptability and professionalism.

**Phone Interview Excellence**

• **Environment Setup**: Choose a quiet room with excellent cell signal, have a backup phone ready (landline or second mobile), keep notepad, pen, and water accessible, eliminate all distractions (TV, computer notifications, pets), and ensure comfortable seating with good posture support.

• **Voice Optimization**: Stand while talking to improve vocal energy and breathing, smile while speaking (it's genuinely audible in your voice), speak clearly and 10-15% slower than normal conversation, use hand gestures even though they can't see you (improves vocal expression), and practice vocal warm-ups before the call.

• **Strategic Preparation**: Have your resume, job description, and key talking points visible, prepare a "cheat sheet" with company facts and your STAR examples, keep water nearby to avoid dry mouth, have the interviewer's contact information ready, and test your phone's speaker quality beforehand.

• **Energy Projection**: Vary your tone to maintain engagement and show enthusiasm, ask clarifying questions to demonstrate active listening, use the interviewer's name naturally throughout the conversation, and maintain high energy throughout (phone interviews can feel flat).

**Video Interview Mastery**

• **Technical Setup**: Test camera and audio 30 minutes before the interview, have a backup device ready (tablet or second computer), ensure stable internet connection with ethernet cable if possible, close unnecessary applications to prevent lag and notifications, and have technical support contact information ready.

• **Lighting and Visual**: Face a window or use a ring light for even, flattering lighting, avoid backlighting that creates shadows on your face, position camera at eye level (use books to adjust height if needed), ensure your face is well-lit and clearly visible, and test your setup at the same time of day as your interview.

• **Background Strategy**: Choose a clean, professional background with minimal distractions, avoid personal items or family photos in view, consider a virtual background if your space isn't ideal (test it first), ensure the background isn't too busy or colorful, and have good contrast between you and the background.

• **Eye Contact Technique**: Look directly at the camera lens (not the screen) when speaking, place a small arrow or reminder near your camera, practice this beforehand to make it natural, remember that looking at the screen appears as looking down to them, and maintain this even when they're speaking.

• **Professional Presentation**: Dress professionally from head to toe (you might need to stand), keep your hands visible and use natural gestures within the camera frame, maintain good posture throughout the entire interview, have water available but drink discretely, and practice your setup with a friend beforehand.

**Panel Interview Strategy**

• **Name and Role Management**: Write down each person's name and role as introductions are made, create a simple seating chart if helpful for reference, use names naturally throughout the conversation, ask for business cards or LinkedIn connections at the end, and remember that each person may evaluate different aspects.

• **Attention Distribution**: Make eye contact with all panel members, not just the person asking questions, include everyone when giving responses by scanning the group, acknowledge each person's expertise area when relevant, gauge reactions from all members to adjust your approach, and ensure no one feels ignored or excluded.

• **Question Addressing**: Start by looking at the person who asked the question, then include others in your response by making eye contact, end by looking back at the questioner for confirmation, address follow-up questions to the appropriate person, and ask clarifying questions if the source isn't clear.

• **Follow-up Strategy**: Send personalized thank-you notes to each panel member within 24 hours, reference specific points from your conversation with each person, connect on LinkedIn if appropriate and company culture allows, mention something unique you discussed with each individual, and maintain consistent messaging across all communications.

**Behavioral Interview Preparation**

• **STAR Method Mastery**: Situation (context and background with specific details), Task (your responsibility and what needed to be accomplished), Action (specific steps YOU took, not the team), Result (quantifiable outcomes and lessons learned), and practice timing to keep responses to 2-3 minutes maximum.

• **Story Bank Development**: Prepare 8-10 detailed examples covering leadership, teamwork, problem-solving, adaptability, conflict resolution, innovation, overcoming challenges, and customer focus, with each story demonstrating multiple competencies when possible.

• **Quantified Results**: Include specific numbers, percentages, timeframes, and measurable impacts in every story, prepare backup details for follow-up questions, show progression and growth over time, and connect results to business impact when possible.

**Case Study and Presentation Interviews**

• **Structure Framework**: Problem definition and analysis (show you understand the challenge), solution development (demonstrate your thinking process), implementation plan (prove you can execute), expected outcomes and metrics (show business acumen), and risk assessment and mitigation (display strategic thinking).

• **Time Management**: Allocate time for each section and practice with a timer, leave time for questions and discussion (usually 25% of total time), prepare for both short (15-minute) and extended (45-minute) versions, have a clear agenda and stick to it, and practice smooth transitions between sections.

• **Visual Communication**: Create clean, professional slides with minimal text (6x6 rule: max 6 bullet points, 6 words each), use charts and graphs to illustrate key points, prepare for technical difficulties with printed backup copies, ensure slides are readable on various screen sizes, and practice presenting without relying heavily on slides.

• **Interactive Approach**: Engage the audience with thoughtful questions, handle interruptions gracefully and professionally, demonstrate collaborative thinking and openness to feedback, show how you incorporate different perspectives, and maintain confidence while being receptive to input.

💡 **Format-Specific Success Tips:**

• **Phone**: Use a mirror to maintain good facial expressions (it affects your voice)
• **Video**: Have a glass of water nearby but drink during their speaking time
• **Panel**: Address the decision-maker most, but include everyone
• **Behavioral**: Always end with what you learned or how you grew
• **Case Study**: Ask clarifying questions to show analytical thinking

📚 **Recommended Reading:**

• "The Complete Guide to Virtual Interviews" by Harvard Business Review
• "Panel Interview Success" by Career Development Center
• "Case Interview Secrets" by Victor Cheng
• "Behavioral Interview Questions and Answers" by Jeff and Mike

🔗 **Practice Resources:**

• Pramp.com - Free mock interviews with peers
• InterviewBuddy.in - Professional mock interview platform
• Zoom/Teams - Practice video interview settings
• Voice recorder app - Practice phone interview responses
• Case interview practice websites (consulting roles)

✅ **Format Mastery Checklist:**

• Comfortable with phone interviews (clear voice, good energy)
• Video interview setup tested and professional
• Panel interview strategy for attention management
• STAR method responses prepared and practiced
• Case study presentation skills developed
• Backup plans ready for technical difficulties

⚠️ **Common Format Mistakes:**

• **Phone**: Forgetting to smile (affects voice quality)
• **Video**: Looking at screen instead of camera
• **Panel**: Focusing only on one person
• **Behavioral**: Giving vague or theoretical answers
• **Case Study**: Not asking clarifying questions
'''
                }
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
**The STAR Method: Your Blueprint for Compelling Responses**

The STAR method is the gold standard for answering behavioral interview questions. It provides structure, ensures completeness, and makes your responses memorable and impactful.

**S - Situation: Setting the Stage**

• **Context Creation**: Provide enough background for the interviewer to understand the scenario without overwhelming details. Include when, where, and who was involved.

• **Relevance Focus**: Choose situations that are recent (within 2-3 years), relevant to the role you're applying for, and demonstrate the skills they're seeking.

• **Specificity**: Avoid vague statements like "we always" or "I usually." Focus on one specific instance that showcases your abilities.

**T - Task: Defining Your Role**

• **Personal Responsibility**: Clearly articulate what YOU were responsible for, not what the team or organization needed to do. Use "I" statements consistently.

• **Challenge Identification**: Explain the specific challenge, goal, or problem you needed to address. What made this situation difficult or important?

• **Stakes and Pressure**: Help the interviewer understand why this mattered - deadlines, budget constraints, customer impact, or strategic importance.

**A - Action: Your Strategic Response**

• **Detailed Steps**: Describe the specific actions YOU took, not what "we" did. Break down your approach into clear, logical steps.

• **Decision-Making Process**: Explain your thought process - why you chose this approach over alternatives, how you prioritized actions, what factors you considered.

• **Skills Demonstration**: Highlight the specific skills, tools, or competencies you used. This is where you showcase your capabilities.

• **Collaboration and Leadership**: If you worked with others, explain how you influenced, coordinated, or led the effort while maintaining focus on your contributions.

**R - Result: Quantifiable Impact**

• **Measurable Outcomes**: Provide specific numbers, percentages, timeframes, or other quantifiable results whenever possible. "Increased sales by 23%" is better than "improved sales."

• **Multiple Benefits**: Often your actions had several positive outcomes - cost savings, time efficiency, improved relationships, process improvements.

• **Learning and Growth**: What did you learn from this experience? How did it change your approach to similar situations? This shows self-awareness and continuous improvement.

• **Long-term Impact**: If applicable, mention the lasting effects of your actions - did the solution become standard practice? Did it influence future decisions?

**STAR Method Best Practices**

• **Time Management**: Keep responses to 2-3 minutes maximum. Practice with a timer to develop natural pacing.

• **Authenticity**: Use real examples from your experience. Fabricated stories are often detected and always backfire.

• **Variety**: Prepare examples from different contexts - work, school, volunteer activities, personal projects - to show well-rounded experience.

• **Flexibility**: Be ready to adapt your examples to different questions. One situation might demonstrate multiple competencies.
'''
                },
                {
                    'id': 2,
                    'title': 'Building Your Story Bank',
                    'duration': '35 min',
                    'content': '''
**Creating a Powerful Portfolio of Examples**

Your story bank is your competitive advantage. These carefully crafted examples will serve as the foundation for answering any behavioral question with confidence and impact.

**Essential Story Categories**

• **Leadership Examples**: Times you led a team, project, or initiative. Include both formal leadership roles and situations where you took initiative without authority.

• **Teamwork and Collaboration**: Situations where you worked effectively with others, resolved team conflicts, or contributed to group success.

• **Problem-Solving and Innovation**: Complex challenges you solved, creative solutions you developed, or processes you improved.

• **Adaptability and Change**: Times you successfully navigated change, learned new skills quickly, or adjusted to unexpected circumstances.

• **Conflict Resolution**: Professional disagreements you resolved, difficult conversations you navigated, or tense situations you defused.

• **Achievement and Excellence**: Your biggest accomplishments, times you exceeded expectations, or goals you achieved against odds.

• **Learning from Failure**: Mistakes you made, lessons you learned, and how you applied those lessons to future situations.

• **Customer Focus**: Times you went above and beyond for customers, resolved customer issues, or improved customer experience.

**Story Development Framework**

• **Choose High-Impact Examples**: Select situations with clear, measurable outcomes that demonstrate multiple skills and competencies.

• **Vary Your Contexts**: Include examples from work, education, volunteer activities, and personal projects to show diverse experience.

• **Recent and Relevant**: Prioritize examples from the last 2-3 years that relate to the role you're seeking.

• **Complexity Levels**: Have both simple, straightforward examples and complex, multi-faceted situations in your repertoire.

**Making Stories Memorable**

• **Emotional Connection**: Include appropriate emotions and motivations to make your stories more engaging and human.

• **Vivid Details**: Use specific details that help the interviewer visualize the situation without overwhelming them with unnecessary information.

• **Clear Progression**: Structure your story with a clear beginning, middle, and end that flows logically and maintains interest.

• **Unique Perspective**: Highlight what made your approach different or innovative compared to conventional solutions.

**Story Bank Organization**

• **Master Document**: Create a comprehensive document with 10-12 fully developed STAR examples, including all details and potential variations.

• **Quick Reference Cards**: Develop condensed versions (bullet points) for each story that you can review quickly before interviews.

• **Competency Mapping**: Tag each story with the competencies it demonstrates so you can quickly select appropriate examples.

• **Industry Adaptation**: Prepare variations of your stories that emphasize different aspects depending on the industry or role.

**Practice and Refinement**

• **Record Yourself**: Practice telling your stories aloud and record them to identify areas for improvement in pacing, clarity, and impact.

• **Seek Feedback**: Share your stories with trusted colleagues, mentors, or career counselors for honest feedback and suggestions.

• **Mock Interviews**: Use your stories in practice interviews to test their effectiveness and refine your delivery.

• **Continuous Updates**: Regularly add new examples and retire older ones to keep your story bank current and relevant.

**Advanced Storytelling Techniques**

• **Layered Narratives**: Develop stories that can be told at different lengths (1 minute, 2 minutes, 3 minutes) depending on the interview context.

• **Multiple Angles**: Prepare to tell the same story from different perspectives to highlight various competencies.

• **Follow-up Preparation**: Anticipate likely follow-up questions for each story and prepare detailed responses.

• **Connection Points**: Identify how each story connects to the specific role, company, or industry you're targeting.
'''
                },
                {
                    'id': 3,
                    'title': 'Mastering Common Behavioral Questions',
                    'duration': '40 min',
                    'content': '''
**Strategic Responses to Frequently Asked Questions**

Understanding the intent behind common behavioral questions helps you select the most appropriate examples and craft responses that directly address what interviewers want to know.

**Leadership and Initiative Questions**

• **"Tell me about a time you led a team"**: Focus on your leadership style, how you motivated others, and the results you achieved. Highlight both task leadership and relationship management.

• **"Describe a situation where you took initiative"**: Choose an example where you identified an opportunity or problem and took action without being asked. Emphasize proactive thinking and ownership.

• **"How do you motivate others?"**: Use a specific example that shows your understanding of different motivation styles and your ability to adapt your approach to individual team members.

**Problem-Solving and Innovation Questions**

• **"Describe a complex problem you solved"**: Walk through your analytical process, the alternatives you considered, and why you chose your specific approach. Quantify the impact.

• **"Tell me about a time you had to think outside the box"**: Highlight creative thinking, unconventional approaches, and innovative solutions. Explain why traditional methods wouldn't work.

• **"How do you approach learning new skills?"**: Demonstrate your learning methodology, adaptability, and commitment to continuous improvement with a specific example.

**Teamwork and Collaboration Questions**

• **"Describe a time you worked with a difficult team member"**: Focus on your professionalism, communication skills, and ability to find common ground while achieving team objectives.

• **"Tell me about a successful team project"**: Highlight your specific contributions, how you supported team success, and the collaborative processes that led to positive outcomes.

• **"How do you handle conflicts with colleagues?"**: Demonstrate emotional intelligence, conflict resolution skills, and your ability to maintain professional relationships.

**Adaptability and Change Questions**

• **"Describe a time you had to adapt to significant change"**: Show flexibility, positive attitude toward change, and your ability to help others navigate transitions.

• **"Tell me about a time you failed"**: Choose a real failure, focus on what you learned, and demonstrate how you applied those lessons to achieve future success.

• **"How do you handle pressure and tight deadlines?"**: Provide an example that shows your time management, prioritization skills, and ability to maintain quality under pressure.

**Achievement and Excellence Questions**

• **"What's your greatest professional accomplishment?"**: Choose something significant that required substantial effort, showcases multiple skills, and had measurable impact.

• **"Tell me about a time you exceeded expectations"**: Focus on going above and beyond, anticipating needs, and delivering exceptional results.

• **"Describe a goal you set and achieved"**: Highlight your goal-setting process, persistence, and strategic approach to achieving objectives.

**Customer and Stakeholder Focus Questions**

• **"Tell me about a time you dealt with a difficult customer"**: Demonstrate patience, problem-solving skills, and commitment to customer satisfaction while maintaining professional boundaries.

• **"How do you handle competing priorities from different stakeholders?"**: Show your ability to balance multiple demands, communicate effectively, and find win-win solutions.

**Question Analysis Framework**

• **Identify the Core Competency**: What skill or trait is the interviewer really trying to assess with this question?

• **Consider the Role Context**: How does this competency relate specifically to the position you're applying for?

• **Select the Best Example**: Which of your stories most directly demonstrates this competency with the strongest results?

• **Anticipate Follow-ups**: What additional questions might the interviewer ask based on your response?

**Advanced Response Strategies**

• **Competency Stacking**: Choose examples that demonstrate multiple relevant competencies within a single story.

• **Industry Relevance**: Adapt your examples to highlight aspects most relevant to the specific industry or company.

• **Role Progression**: Use examples that show increasing responsibility and impact over time.

• **Cultural Fit**: Select stories that align with the company's stated values and culture.

**Common Pitfalls to Avoid**

• **Generic Responses**: Avoid vague or theoretical answers. Always use specific, personal examples.

• **Negative Focus**: Even when discussing failures or conflicts, maintain a constructive, learning-focused tone.

• **Taking All Credit**: In team situations, acknowledge others' contributions while clearly stating your role.

• **Rambling**: Stay focused and concise. Practice your timing to avoid losing the interviewer's attention.
'''
                }
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
***Systematic Approach to Technical Excellence***

Technical interviews test not just your coding ability, but your problem-solving process, communication skills, and ability to work under pressure. This lesson provides a proven framework for approaching any technical challenge with confidence.

**The UMPIRE Method Framework**

• **U - Understand**: Listen carefully to the entire problem statement, ask clarifying questions about requirements and constraints, confirm your understanding by restating the problem, identify edge cases and special scenarios, and understand the expected input/output format.

• **M - Match**: Recognize the problem pattern (array manipulation, tree traversal, dynamic programming, etc.), recall similar problems you've solved before, identify the underlying data structures and algorithms needed, and consider multiple approaches before coding.

• **P - Plan**: Outline your approach step-by-step before writing any code, discuss your strategy with the interviewer, estimate time and space complexity, identify potential optimizations, and plan for edge case handling.

• **I - Implement**: Write clean, readable code with meaningful variable names, think aloud as you code to show your thought process, start with a working solution even if not optimal, test your code with simple examples as you go, and handle edge cases systematically.

• **R - Review**: Test your solution with the provided examples, walk through your code line by line, check for off-by-one errors and boundary conditions, verify time and space complexity, and look for potential bugs or improvements.

• **E - Evaluate**: Discuss alternative approaches and trade-offs, explain why you chose your specific solution, identify potential optimizations for different constraints, and demonstrate understanding of when your solution would or wouldn't work well.

**Communication During Coding**

• **Think Aloud Protocol**: Verbalize your thought process continuously, explain why you're choosing specific approaches, discuss trade-offs between different solutions, ask for feedback or hints when genuinely stuck, and maintain a collaborative tone throughout.

• **Structured Problem-Solving**: Break complex problems into smaller, manageable pieces, solve subproblems first and then combine solutions, use helper functions to organize your code logically, and explain how pieces fit together in the larger solution.

• **Handling Uncertainty**: Admit when you're unsure about something specific, ask clarifying questions rather than making assumptions, propose multiple approaches when you're not sure which is best, and show your debugging process when code doesn't work initially.

**Time Management Strategies**

• **The 40-20-40 Rule**: Spend 40% of time understanding and planning, 20% implementing the core solution, and 40% testing, debugging, and optimizing. This prevents rushing into code without proper planning.

• **Progressive Refinement**: Start with a brute force solution that works, then optimize for better time/space complexity, add error handling and edge case management, and finally clean up code for readability and maintainability.

• **Checkpoint Strategy**: Set mental checkpoints ("I should have a working solution in 15 minutes"), communicate progress to the interviewer, ask for time checks if you're unsure, and be prepared to discuss partial solutions if time runs short.

**Common Technical Interview Patterns**

• **Array and String Manipulation**: Two-pointer technique, sliding window, prefix sums, and in-place modifications. Practice problems involving searching, sorting, and transformation.

• **Tree and Graph Problems**: Depth-first search (DFS), breadth-first search (BFS), tree traversals (inorder, preorder, postorder), and shortest path algorithms.

• **Dynamic Programming**: Identify overlapping subproblems, define state transitions, choose between top-down (memoization) and bottom-up approaches, and optimize space complexity.

• **System Design Elements**: Understand basic scalability concepts, database design principles, API design patterns, and caching strategies even for coding interviews.

💡 **Pro Tips for Technical Success:**

• **Code Quality Matters**: Use meaningful variable names, add comments for complex logic, maintain consistent indentation, and write code you'd be proud to submit in a code review.

• **Test-Driven Mindset**: Think about test cases before coding, include edge cases in your testing, walk through examples step by step, and explain how you would test your solution in production.

• **Optimization Strategy**: Always start with a working solution, then optimize, discuss time/space trade-offs explicitly, and know when "good enough" is sufficient versus when optimization is critical.

📚 **Essential Technical Resources:**

• "Cracking the Coding Interview" by Gayle McDowell - Comprehensive interview preparation
• "Elements of Programming Interviews" by Aziz, Lee, and Prakash - Advanced problem-solving
• "System Design Interview" by Alex Xu - Scalability and architecture
• "Clean Code" by Robert Martin - Code quality and best practices

🔗 **Practice Platforms:**

• LeetCode.com - Extensive problem database with company-specific questions
• HackerRank.com - Skill-based challenges and competitions
• CodeSignal.com - Timed practice sessions and company assessments
• InterviewBit.com - Structured learning paths by topic
• Pramp.com - Free peer-to-peer mock interviews

✅ **Technical Readiness Checklist:**

• Can solve easy problems in under 15 minutes
• Comfortable with medium problems in 25-30 minutes
• Explains thought process clearly while coding
• Handles edge cases and error conditions
• Optimizes solutions for time and space complexity
• Writes clean, readable code under pressure

⚠️ **Common Technical Pitfalls:**

• **Jumping to Code**: Starting to code before fully understanding the problem
• **Silent Coding**: Not explaining your thought process during implementation
• **Perfectionism**: Spending too much time on optimal solution instead of working solution
• **Ignoring Edge Cases**: Not considering empty inputs, single elements, or boundary conditions
• **Poor Communication**: Not asking clarifying questions or explaining trade-offs
'''
                },
                {
                    'id': 2,
                    'title': 'Data Structures & Algorithms Mastery',
                    'duration': '60 min',
                    'content': '''
***Foundation Knowledge for Technical Success***

Mastering fundamental data structures and algorithms is essential for technical interviews. This comprehensive guide covers the most important concepts with practical applications and interview-focused insights.

**Essential Data Structures**

• **Arrays and Strings**: Master in-place manipulation techniques, understand time complexity of operations (access O(1), search O(n), insertion/deletion O(n)), practice two-pointer and sliding window techniques, and learn string manipulation algorithms (substring search, pattern matching).

• **Linked Lists**: Understand singly, doubly, and circular linked lists, master pointer manipulation and edge case handling, practice reversal, merging, and cycle detection algorithms, and know when to use linked lists vs. arrays (dynamic size, insertion/deletion efficiency).

• **Stacks and Queues**: Implement using arrays and linked lists, understand LIFO (stack) and FIFO (queue) principles, master applications like expression evaluation, parentheses matching, and BFS/DFS, and learn about deques and priority queues.

• **Trees and Binary Trees**: Understand tree terminology (root, leaf, height, depth), master tree traversals (inorder, preorder, postorder, level-order), practice binary search tree operations, and learn about balanced trees (AVL, Red-Black) concepts.

• **Hash Tables**: Understand hash functions and collision resolution (chaining, open addressing), know average O(1) and worst-case O(n) time complexities, practice problems involving frequency counting and fast lookups, and understand load factor and resizing concepts.

• **Graphs**: Represent graphs using adjacency lists and matrices, understand directed vs. undirected graphs, master graph traversal algorithms (DFS, BFS), and learn shortest path algorithms (Dijkstra, Bellman-Ford) for advanced problems.

**Critical Algorithms**

• **Sorting Algorithms**: Master quicksort (average O(n log n), worst O(n²)), mergesort (stable, O(n log n) guaranteed), heapsort (in-place, O(n log n)), and understand when to use each algorithm based on constraints.

• **Searching Algorithms**: Perfect binary search and its variations (find first/last occurrence, search in rotated array), understand linear search applications, and practice search in 2D matrices and specialized data structures.

• **Graph Algorithms**: Master depth-first search (DFS) for connectivity and cycle detection, breadth-first search (BFS) for shortest paths in unweighted graphs, topological sorting for dependency resolution, and union-find for disjoint set operations.

• **Dynamic Programming**: Identify overlapping subproblems and optimal substructure, master both top-down (memoization) and bottom-up approaches, practice classic problems (knapsack, longest common subsequence, edit distance), and optimize space complexity when possible.

• **Greedy Algorithms**: Understand when greedy approach works (optimal substructure + greedy choice property), practice interval scheduling and minimum spanning tree problems, and learn to prove correctness of greedy solutions.

**Time and Space Complexity Analysis**

• **Big O Notation Mastery**: Understand O(1), O(log n), O(n), O(n log n), O(n²), O(2^n) complexities, analyze nested loops and recursive algorithms, identify best, average, and worst-case scenarios, and communicate complexity trade-offs clearly.

• **Space Complexity**: Distinguish between auxiliary space and total space, understand recursive call stack space, analyze in-place vs. out-of-place algorithms, and optimize space usage when memory is constrained.

• **Amortized Analysis**: Understand amortized time complexity (dynamic arrays, hash tables), analyze algorithms with occasional expensive operations, and explain why average-case analysis matters in practice.

**Advanced Topics for Senior Roles**

• **Advanced Data Structures**: Tries for string processing, segment trees for range queries, Fenwick trees (Binary Indexed Trees) for efficient updates, and disjoint set union (DSU) for connectivity problems.

• **String Algorithms**: KMP algorithm for pattern matching, rolling hash for substring problems, suffix arrays and trees for advanced string processing, and edit distance algorithms for similarity matching.

• **Mathematical Algorithms**: Number theory basics (GCD, LCM, prime numbers), combinatorics for counting problems, probability and statistics for data analysis, and bit manipulation techniques for optimization.

**Interview-Specific Strategies**

• **Pattern Recognition**: Group similar problems by underlying patterns, practice transitioning between different approaches, identify when to use specific data structures, and build intuition for algorithm selection.

• **Code Implementation**: Write clean, bug-free code under pressure, handle edge cases systematically, use meaningful variable names and comments, and test code with examples during implementation.

• **Optimization Techniques**: Start with brute force, then optimize, use appropriate data structures for efficiency, consider space-time trade-offs, and explain why optimizations matter.

💡 **Study Strategy for DSA:**

• **Week 1-2**: Master basic data structures (arrays, strings, linked lists, stacks, queues)
• **Week 3-4**: Learn tree and graph algorithms (DFS, BFS, tree traversals)
• **Week 5-6**: Practice dynamic programming and greedy algorithms
• **Week 7-8**: Advanced topics and company-specific problem patterns
• **Ongoing**: Daily practice with timed problem-solving sessions

📚 **Recommended Study Materials:**

• "Introduction to Algorithms" by Cormen (CLRS) - Comprehensive theoretical foundation
• "Algorithm Design Manual" by Skiena - Practical problem-solving approach
• "Competitive Programming" by Halim - Advanced techniques and optimization
• MIT 6.006 Introduction to Algorithms (online course) - Video lectures and exercises

🔗 **Practice Resources by Topic:**

• **Arrays/Strings**: LeetCode Arrays 101, HackerRank Arrays and Strings
• **Trees/Graphs**: LeetCode Explore Trees, Graph Theory courses on Coursera
• **Dynamic Programming**: LeetCode DP Explore, AtCoder DP Contest problems
• **System Design**: Grokking System Design, High Scalability blog

✅ **DSA Mastery Indicators:**

• Can implement basic data structures from scratch
• Recognizes problem patterns quickly (within 2-3 minutes)
• Chooses optimal data structure for given constraints
• Analyzes time/space complexity accurately
• Optimizes solutions systematically
• Explains algorithmic choices clearly

⚠️ **Common DSA Mistakes:**

• **Memorizing Solutions**: Focus on understanding patterns, not memorizing code
• **Ignoring Complexity**: Always analyze and communicate time/space complexity
• **Skipping Basics**: Master fundamentals before moving to advanced topics
• **No Edge Cases**: Always consider empty inputs, single elements, duplicates
• **Poor Implementation**: Write clean, testable code even under pressure
'''
                },
                {
                    'id': 3,
                    'title': 'System Design Fundamentals',
                    'duration': '55 min',
                    'content': '''
***Building Scalable Systems: From Concept to Implementation***

System design interviews evaluate your ability to architect large-scale distributed systems. This lesson covers fundamental concepts, design patterns, and communication strategies essential for system design success.

**System Design Interview Process**

• **Requirements Clarification (5-10 minutes)**: Ask about functional requirements (what the system should do), non-functional requirements (performance, scalability, availability), scale expectations (users, data, requests per second), and any specific constraints or assumptions.

• **High-Level Design (10-15 minutes)**: Draw major components and their interactions, show data flow between components, identify key services and databases, discuss API design and communication protocols, and get interviewer feedback before diving deeper.

• **Detailed Design (15-20 minutes)**: Deep dive into critical components, discuss data models and database schemas, explain algorithms for core functionality, address scalability and performance concerns, and show understanding of trade-offs.

• **Scale and Optimize (5-10 minutes)**: Identify bottlenecks and scaling challenges, propose solutions for high availability and fault tolerance, discuss monitoring and observability, and address security and compliance considerations.

**Fundamental System Design Concepts**

• **Scalability Patterns**: Horizontal scaling (adding more servers) vs. vertical scaling (upgrading hardware), load balancing strategies (round-robin, least connections, geographic), database sharding and partitioning techniques, and caching layers (application, database, CDN).

• **Reliability and Availability**: Design for fault tolerance with redundancy, implement circuit breakers and graceful degradation, plan for disaster recovery and backup strategies, understand CAP theorem (Consistency, Availability, Partition tolerance), and design for 99.9% vs. 99.99% availability requirements.

• **Performance Optimization**: Identify and eliminate bottlenecks, implement appropriate caching strategies, optimize database queries and indexing, use asynchronous processing for heavy operations, and design efficient data structures and algorithms.

• **Data Management**: Choose between SQL and NoSQL databases based on requirements, design efficient database schemas and relationships, implement data replication and backup strategies, and handle data consistency in distributed systems.

**Core System Components**

• **Load Balancers**: Distribute incoming requests across multiple servers, implement health checks and failover mechanisms, choose between Layer 4 (transport) and Layer 7 (application) load balancing, and handle session affinity when needed.

• **Databases**: Understand ACID properties for transactional systems, choose appropriate database types (relational, document, key-value, graph), implement read replicas for scaling read operations, and design effective indexing strategies.

• **Caching Systems**: Implement multi-level caching (browser, CDN, application, database), choose appropriate cache eviction policies (LRU, LFU, TTL), handle cache invalidation and consistency, and use caching for both data and computed results.

• **Message Queues**: Decouple services with asynchronous messaging, choose between push and pull models, implement dead letter queues for error handling, and ensure message ordering and delivery guarantees when needed.

• **Microservices Architecture**: Break monoliths into focused, independent services, design service boundaries and communication patterns, implement service discovery and configuration management, and handle distributed system challenges (network partitions, eventual consistency).

**Common System Design Patterns**

• **Database Patterns**: Master-slave replication for read scaling, database sharding for write scaling, CQRS (Command Query Responsibility Segregation) for complex domains, and event sourcing for audit trails and temporal queries.

• **Communication Patterns**: Synchronous communication (REST APIs, GraphQL), asynchronous messaging (pub/sub, message queues), event-driven architecture for loose coupling, and API gateways for service orchestration.

• **Scalability Patterns**: Horizontal partitioning (sharding) of data and services, vertical partitioning by feature or domain, federation of databases and services, and denormalization for read performance.

• **Reliability Patterns**: Circuit breaker pattern for fault tolerance, bulkhead pattern for resource isolation, retry mechanisms with exponential backoff, and graceful degradation when dependencies fail.

**Technology Stack Considerations**

• **Frontend Technologies**: Content Delivery Networks (CDNs) for static assets, client-side caching and offline capabilities, responsive design for multiple devices, and progressive web app features.

• **Backend Technologies**: Choose appropriate programming languages and frameworks, implement containerization with Docker and Kubernetes, use serverless computing for event-driven workloads, and design RESTful APIs with proper versioning.

• **Data Storage**: Relational databases (PostgreSQL, MySQL) for structured data, NoSQL databases (MongoDB, Cassandra, Redis) for specific use cases, data warehouses (Snowflake, BigQuery) for analytics, and object storage (S3) for files and media.

• **Infrastructure**: Cloud platforms (AWS, GCP, Azure) for scalability and reliability, infrastructure as code (Terraform, CloudFormation) for reproducibility, monitoring and logging systems (Prometheus, ELK stack), and CI/CD pipelines for deployment automation.

**Real-World System Examples**

• **Social Media Platform**: Handle billions of posts and interactions, implement news feed generation algorithms, design real-time messaging systems, and scale media storage and delivery.

• **E-commerce System**: Process high-volume transactions securely, manage inventory across multiple warehouses, implement recommendation engines, and handle peak traffic during sales events.

• **Video Streaming Service**: Encode and store videos in multiple formats, implement adaptive bitrate streaming, design global content delivery networks, and handle millions of concurrent viewers.

• **Ride-Sharing Application**: Match drivers and riders in real-time, calculate optimal routes and pricing, handle location tracking and updates, and process payments securely.

💡 **System Design Success Strategies:**

• **Start Simple**: Begin with basic architecture, then add complexity as needed
• **Think in Numbers**: Estimate capacity, throughput, and storage requirements
• **Consider Trade-offs**: Discuss pros and cons of different approaches
• **Be Practical**: Use technologies and patterns you understand well
• **Ask Questions**: Clarify requirements and constraints throughout the interview

📚 **Essential System Design Resources:**

• "Designing Data-Intensive Applications" by Martin Kleppmann - Comprehensive system design principles
• "System Design Interview" by Alex Xu - Interview-focused preparation guide
• "Building Microservices" by Sam Newman - Microservices architecture patterns
• "High Performance Browser Networking" by Ilya Grigorik - Network and performance optimization

🔗 **Learning and Practice Platforms:**

• Grokking the System Design Interview (EducativeIO) - Structured learning path
• System Design Primer (GitHub) - Comprehensive open-source guide
• High Scalability blog - Real-world system architecture case studies
• AWS Architecture Center - Cloud-native design patterns and best practices
• Google Cloud Architecture Framework - Scalable system design principles

✅ **System Design Readiness Checklist:**

• Can estimate system capacity and performance requirements
• Understands trade-offs between different architectural choices
• Designs APIs and data models effectively
• Addresses scalability, reliability, and security concerns
• Communicates design decisions clearly with diagrams
• Handles follow-up questions about implementation details

⚠️ **System Design Interview Pitfalls:**

• **Jumping to Details**: Start with high-level design before diving deep
• **Ignoring Requirements**: Always clarify functional and non-functional requirements
• **Over-Engineering**: Design for stated requirements, not hypothetical future needs
• **Poor Communication**: Use clear diagrams and explain your thought process
• **No Trade-offs**: Always discuss pros and cons of design decisions
'''
                }
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
***Mastering the Art of Compelling Communication***

Effective verbal communication is your most powerful tool in interviews. This lesson teaches you to speak with clarity, confidence, and impact that leaves lasting positive impressions on interviewers.

**Voice and Delivery Mastery**

• **Optimal Speaking Pace**: Speak 10-15% slower than normal conversation (allows better comprehension), practice with a metronome or recording app, pause strategically for emphasis and to let important points sink in, and vary your pace to maintain engagement and highlight key information.

• **Volume and Projection**: Use appropriate volume for the room size and setting, project your voice from your diaphragm (not throat), ensure you can be heard clearly without shouting, and practice breathing exercises to support strong vocal projection.

• **Vocal Tonality and Inflection**: Use a slightly lower pitch to convey authority and confidence, vary your tone to show enthusiasm and engagement, avoid uptalk (ending statements like questions), and practice vocal warm-ups before important conversations.

• **Articulation and Clarity**: Pronounce words clearly and completely, avoid mumbling or trailing off at sentence endings, practice tongue twisters to improve articulation, and record yourself speaking to identify areas for improvement.

**Language and Vocabulary Optimization**

• **Professional Language Choices**: Use industry-appropriate terminology without overcomplicating, choose active voice over passive voice ("I led the project" vs. "The project was led by me"), avoid filler words (um, uh, like, you know), and replace weak phrases with confident alternatives.

• **Concise and Impactful Communication**: Get to the point quickly and clearly, use the "bottom line up front" approach for key messages, eliminate unnecessary words and redundancies, and practice the "elevator pitch" format for various time constraints.

• **Storytelling Structure**: Use clear beginning, middle, and end in your examples, include specific details that make stories memorable and credible, connect your experiences directly to the role requirements, and practice smooth transitions between different topics or examples.

• **Adaptable Communication Style**: Match the interviewer's communication style and energy level, adjust formality based on company culture and interviewer preferences, use appropriate technical depth based on audience expertise, and demonstrate cultural awareness and sensitivity.

**Advanced Communication Techniques**

• **Strategic Pausing**: Use pauses to emphasize important points, take brief pauses to collect thoughts before answering complex questions, allow silence after asking questions to encourage detailed responses, and use pauses to create dramatic effect in storytelling.

• **Bridging and Redirecting**: Acknowledge the question before redirecting to your strengths, use phrases like "That's a great question, and it reminds me of..." to transition smoothly, redirect negative questions to positive examples, and bridge from weaknesses to learning and growth.

• **Mirroring and Rapport Building**: Subtly match the interviewer's speaking pace and energy, use similar vocabulary and communication style, reflect their level of formality or casualness, and build on their comments to show active listening.

**Handling Difficult Communication Scenarios**

• **Managing Nervousness**: Practice deep breathing techniques to calm your voice, use positive self-talk before and during interviews, reframe nerves as excitement and energy, and have backup phrases ready when you need time to think.

• **Clarifying Complex Questions**: Ask for clarification when questions are unclear or multi-part, repeat back your understanding of complex questions, break down multi-part questions into components, and confirm you're addressing what they really want to know.

• **Recovering from Mistakes**: Acknowledge mistakes quickly and move on, use humor appropriately to lighten the mood, show how you learn from errors and improve, and maintain confidence even after stumbling.

• **Dealing with Interruptions**: Handle interruptions gracefully and professionally, finish your thought when appropriate or acknowledge the interruption, adapt to the interviewer's communication style and preferences, and maintain composure when conversations don't go as planned.

💡 **Vocal Excellence Exercises:**

• **Daily Practice**: Read news articles aloud for 10 minutes daily, record yourself answering common interview questions, practice speaking with a pen between your teeth (improves articulation), and do vocal warm-ups before important conversations.

• **Breathing Techniques**: Practice diaphragmatic breathing (belly breathing), do the 4-7-8 breathing exercise for calm, practice speaking on the exhale for better voice control, and use breathing to manage nervousness and maintain steady speech.

• **Pace and Rhythm**: Practice speaking with a metronome app, record conversations and analyze your speaking pace, practice varying your rhythm for emphasis, and work on eliminating rushed speech patterns.

📚 **Communication Skills Resources:**

• "Talk Like TED" by Carmine Gallo - Public speaking and presentation skills
• "The Quick and Easy Way to Effective Speaking" by Dale Carnegie - Fundamental communication principles
• "Speak With Impact" by Allison Shapira - Executive communication strategies
• "The Charisma Myth" by Olivia Fox Cabane - Building presence and influence

🔗 **Practice and Improvement Tools:**

• Toastmasters International - Public speaking practice and feedback
• Voice recording apps (Voice Memos, Audacity) - Self-assessment and improvement
• TED Talks - Study excellent speakers and presentation techniques
• Pronunciation apps (Sounds, ELSA Speak) - Accent and clarity improvement

✅ **Verbal Communication Mastery Checklist:**

• Speaks at optimal pace with clear articulation
• Uses confident, professional language consistently
• Eliminates filler words and weak phrases
• Adapts communication style to audience and context
• Handles difficult questions and interruptions gracefully
• Uses strategic pausing and emphasis effectively

⚠️ **Common Verbal Communication Mistakes:**

• **Speaking Too Fast**: Rushing through responses due to nervousness
• **Filler Word Overuse**: Excessive "um," "uh," "like," "you know"
• **Weak Language**: Using tentative phrases like "I think maybe" or "sort of"
• **Monotone Delivery**: Speaking without variation in pace or tone
• **Poor Listening**: Not adapting communication style to interviewer preferences
'''
                },
                {
                    'id': 2,
                    'title': 'Non-Verbal Communication Mastery',
                    'duration': '35 min',
                    'content': '''
***Your Silent Language: Mastering Body Language and Presence***

Research shows that 55% of communication is body language, 38% is tone of voice, and only 7% is actual words. This lesson teaches you to align your non-verbal communication with your verbal message for maximum impact and credibility.

**Posture and Physical Presence**

• **Confident Posture**: Sit up straight with shoulders back and relaxed, keep both feet flat on the floor (avoid crossing legs), lean slightly forward to show engagement and interest, maintain an open chest and avoid hunching, and practice good posture until it becomes natural.

• **Strategic Positioning**: Choose seats that allow you to face the interviewer directly, maintain appropriate distance (arm's length for most cultures), position yourself to see all panel members in group interviews, and be mindful of personal space preferences and cultural differences.

• **Movement and Gestures**: Use purposeful hand gestures to emphasize points, keep movements controlled and professional, avoid fidgeting, pen-clicking, or repetitive movements, and use open gestures (palms visible) rather than closed or defensive positions.

• **Professional Presence**: Enter rooms with confidence and purpose, stand and sit with intention and grace, maintain professional demeanor even during casual moments, and project executive presence regardless of your current level.

**Eye Contact and Facial Expressions**

• **Strategic Eye Contact**: Maintain natural eye contact 70-80% of the time during conversation, look at the interviewer when they're speaking to show attention, make eye contact when making important points, and use the triangle technique (eyes to forehead) for comfort in intense conversations.

• **Authentic Facial Expressions**: Show genuine interest through facial expressions, smile naturally when appropriate (not forced or constant), match your expressions to your message content, and practice expressing enthusiasm and engagement authentically.

• **Active Listening Signals**: Nod appropriately to show understanding and agreement, use micro-expressions to show you're processing information, maintain engaged facial expressions even during long explanations, and avoid looking bored, distracted, or judgmental.

• **Managing Nervous Expressions**: Practice relaxing facial muscles when tense, avoid excessive blinking or eye movements, control nervous smiles or inappropriate expressions, and develop awareness of your default facial expressions.

**Hand Gestures and Movement**

• **Purposeful Gestures**: Use hand gestures that support and emphasize your words, practice gestures that feel natural and authentic to you, avoid pointing directly at people (use open-hand gestures instead), and keep gestures within the "box" of your torso width.

• **Professional Hand Positioning**: Keep hands visible (not in pockets or behind back), rest hands naturally on the table or armrests when not gesturing, avoid fidgeting with objects (pens, jewelry, clothing), and use steepling or other confident hand positions when listening.

• **Cultural Sensitivity**: Be aware that gesture meanings vary across cultures, avoid gestures that might be offensive in different contexts, adapt your gesture style to match the interviewer's preferences, and when in doubt, use more conservative gestures.

**Virtual Interview Body Language**

• **Camera Positioning and Framing**: Position camera at eye level to avoid looking down or up, frame yourself from mid-chest up for professional appearance, ensure good lighting on your face and avoid shadows, and test your setup beforehand to ensure optimal positioning.

• **Virtual Eye Contact**: Look directly at the camera lens when speaking (not the screen), place a small reminder arrow near your camera, practice this technique until it becomes natural, and remember that screen-looking appears as looking down to the interviewer.

• **Gesture Adaptation**: Keep gestures within the camera frame, use slightly more pronounced gestures than in-person, avoid movements that take you out of frame, and be mindful of how gestures appear on camera.

• **Virtual Presence**: Maintain good posture even though only upper body is visible, dress professionally from head to toe (you might need to stand), minimize distracting background movement, and maintain energy and engagement despite the screen barrier.

**Reading and Responding to Interviewer Cues**

• **Interpreting Body Language**: Notice when interviewers lean in (shows interest) or lean back (may indicate disengagement), observe facial expressions for confusion, agreement, or concern, watch for signs of time pressure or desire to move on, and adapt your approach based on their non-verbal feedback.

• **Mirroring and Matching**: Subtly match the interviewer's energy level and posture, adapt to their preferred level of formality or casualness, mirror their pace and communication style appropriately, and build rapport through synchronized non-verbal communication.

• **Responding to Negative Cues**: Address signs of confusion or disagreement directly, adjust your approach if you notice disengagement, ask clarifying questions if you sense misunderstanding, and maintain professionalism even if you detect negative reactions.

💡 **Body Language Practice Exercises:**

• **Mirror Practice**: Practice confident posture and gestures in front of a mirror, record yourself during mock interviews to observe your body language, practice maintaining eye contact with your reflection, and work on natural, authentic expressions.

• **Video Analysis**: Record practice interviews and analyze your non-verbal communication, watch successful speakers and note their body language techniques, study your own patterns and identify areas for improvement, and practice until confident body language becomes automatic.

• **Awareness Building**: Practice mindful awareness of your posture throughout the day, notice how different postures affect your confidence and energy, observe successful professionals and their non-verbal communication, and develop sensitivity to others' body language cues.

📚 **Body Language and Presence Resources:**

• "Presence" by Amy Cuddy - Power posing and confident body language
• "The Definitive Book of Body Language" by Allan and Barbara Pease - Comprehensive non-verbal communication guide
• "Executive Presence" by Sylvia Ann Hewlett - Building leadership presence and gravitas
• "What Every BODY is Saying" by Joe Navarro - FBI insights on reading body language

🔗 **Practice and Assessment Tools:**

• Video conferencing platforms (Zoom, Teams) - Practice virtual presence
• Body language analysis apps - Get feedback on posture and gestures
• TED Talks on body language - Learn from experts and successful speakers
• Professional coaching services - Get personalized feedback on presence

✅ **Non-Verbal Communication Mastery Checklist:**

• Maintains confident, professional posture consistently
• Uses appropriate eye contact and facial expressions
• Employs purposeful gestures that support verbal message
• Adapts body language to virtual and in-person settings
• Reads and responds to interviewer non-verbal cues
• Projects executive presence regardless of current level

⚠️ **Non-Verbal Communication Pitfalls:**

• **Defensive Postures**: Crossing arms, leaning back, or creating barriers
• **Nervous Fidgeting**: Playing with objects, excessive movement, or self-soothing behaviors
• **Poor Eye Contact**: Looking away too much, staring, or avoiding eye contact
• **Inconsistent Messaging**: Body language that contradicts verbal message
• **Cultural Insensitivity**: Using gestures or positioning inappropriate for the context
'''
                },
                {
                    'id': 3,
                    'title': 'Building Unshakeable Confidence',
                    'duration': '45 min',
                    'content': '''
***Developing Authentic Confidence for Interview Success***

True confidence comes from thorough preparation, self-awareness, and the right mindset. This lesson provides practical strategies to build genuine confidence that will serve you in interviews and throughout your career.

**Understanding Confidence vs. Arrogance**

• **Authentic Confidence**: Based on genuine competence and self-awareness, includes humility and willingness to learn, acknowledges both strengths and areas for growth, and focuses on value you can provide rather than personal superiority.

• **Confidence Indicators**: Speaking clearly about your accomplishments without minimizing them, asking thoughtful questions that show genuine interest, admitting when you don't know something while showing eagerness to learn, and maintaining composure under pressure or when challenged.

• **Avoiding Arrogance**: Never dismiss others' ideas or experiences, avoid claiming expertise you don't possess, show respect for the interviewer's time and expertise, and demonstrate collaborative rather than competitive attitudes.

**Mental Preparation and Mindset**

• **Visualization Techniques**: Spend 10 minutes daily visualizing successful interview scenarios, imagine yourself answering questions confidently and competently, visualize positive interactions and outcomes, and practice mental rehearsal of challenging situations.

• **Positive Self-Talk and Affirmations**: Replace negative thoughts with realistic, positive alternatives, use evidence-based affirmations ("I have successfully handled similar challenges before"), practice self-compassion when you make mistakes, and develop a growth mindset focused on learning and improvement.

• **Reframing Perspective**: View interviews as conversations rather than interrogations, see them as opportunities to learn about the company and role, focus on mutual fit rather than one-sided evaluation, and remember that you're also evaluating whether the opportunity is right for you.

• **Managing Expectations**: Set realistic goals for interview performance, focus on doing your best rather than being perfect, prepare for various outcomes and have backup plans, and remember that rejection often reflects fit rather than personal worth.

**Physical Confidence Building**

• **Power Posing and Presence**: Practice confident postures for 2 minutes before interviews (hands on hips, arms raised, chest open), use breathing techniques to calm nerves and center yourself, maintain good posture throughout the day to build confidence habits, and practice walking and sitting with intention and presence.

• **Breathing and Relaxation**: Master diaphragmatic breathing for calm and control, practice the 4-7-8 breathing technique (inhale 4, hold 7, exhale 8), use progressive muscle relaxation to release physical tension, and develop pre-interview routines that help you feel centered and prepared.

• **Energy Management**: Get adequate sleep before important interviews, eat nutritious meals and stay hydrated, exercise regularly to build physical and mental resilience, and avoid caffeine excess that might increase anxiety.

**Preparation-Based Confidence**

• **Thorough Research and Preparation**: Know the company, role, and industry thoroughly, prepare detailed STAR examples for common behavioral questions, practice your elevator pitch and key talking points, and anticipate potential questions and prepare thoughtful responses.

• **Skills and Competency Building**: Continuously develop skills relevant to your target roles, seek feedback and work on areas for improvement, build a portfolio of accomplishments and success stories, and stay current with industry trends and best practices.

• **Mock Interview Practice**: Conduct regular practice interviews with friends, mentors, or professional services, record yourself answering questions to identify areas for improvement, practice in various formats (phone, video, in-person, panel), and seek honest feedback and work on suggested improvements.

**Confidence During the Interview**

• **Authentic Enthusiasm**: Show genuine interest in the role and company, ask thoughtful questions that demonstrate engagement, express enthusiasm for challenges and learning opportunities, and let your personality shine through while maintaining professionalism.

• **Handling Uncertainty**: Admit when you don't know something specific, explain how you would find the answer or learn the skill, redirect to related experience or transferable skills, and show curiosity and eagerness to learn new things.

• **Recovery Strategies**: If you make a mistake, acknowledge it briefly and move on, use appropriate humor to lighten the mood when suitable, ask for a moment to collect your thoughts if needed, and maintain perspective that one mistake doesn't define the entire interview.

**Overcoming Interview Anxiety**

• **Anxiety Management Techniques**: Identify your specific anxiety triggers and prepare strategies for each, practice grounding techniques (5-4-3-2-1 sensory method), use cognitive behavioral techniques to challenge negative thoughts, and develop coping strategies for worst-case scenarios.

• **Reframing Nerves as Energy**: Recognize that some nervousness is normal and shows you care, channel nervous energy into enthusiasm and engagement, use physical movement to release excess energy before interviews, and remember that interviewers expect some nervousness and often find it endearing.

• **Building Resilience**: Learn from each interview experience regardless of outcome, maintain perspective that interviews are just one part of your career journey, build a support network of mentors, friends, and career advisors, and celebrate small wins and progress along the way.

**Long-term Confidence Building**

• **Continuous Learning and Growth**: Seek out challenging projects and learning opportunities, ask for feedback regularly and act on it constructively, set and achieve progressively challenging goals, and build expertise in areas that matter for your career.

• **Professional Network Development**: Build relationships with colleagues, mentors, and industry professionals, participate in professional organizations and industry events, seek out speaking opportunities to build confidence in public settings, and offer help and value to others in your network.

• **Personal Brand Building**: Develop a clear understanding of your unique value proposition, build an online presence that reflects your expertise and interests, share knowledge and insights through writing or speaking, and consistently deliver high-quality work that builds your reputation.

💡 **Daily Confidence Building Practices:**

• **Morning Routine**: Start each day with positive affirmations and visualization, practice power poses for 2 minutes, review your accomplishments and strengths, and set intentions for confident interactions throughout the day.

• **Evening Reflection**: Review positive interactions and successes from the day, identify lessons learned from challenges or setbacks, practice gratitude for opportunities and support received, and prepare mentally for the next day's opportunities.

• **Weekly Preparation**: Schedule regular mock interviews or presentation practice, seek feedback from trusted colleagues or mentors, update your accomplishment list with recent successes, and set learning goals for continued growth.

📚 **Confidence and Mindset Resources:**

• "Mindset" by Carol Dweck - Growth mindset and resilience building
• "The Confidence Code" by Kay and Shipman - Science-based confidence building
• "Presence" by Amy Cuddy - Body language and confidence connection
• "Daring Greatly" by Brené Brown - Vulnerability and authentic confidence

🔗 **Confidence Building Tools:**

• Meditation apps (Headspace, Calm) - Mindfulness and anxiety management
• Confidence building courses (Coursera, LinkedIn Learning) - Structured skill development
• Professional coaching services - Personalized confidence building strategies
• Toastmasters International - Public speaking and confidence practice

✅ **Confidence Mastery Indicators:**

• Speaks about accomplishments without minimizing or exaggerating
• Asks thoughtful questions that show genuine interest
• Admits knowledge gaps while showing eagerness to learn
• Maintains composure under pressure or when challenged
• Recovers gracefully from mistakes or unexpected situations
• Projects authentic enthusiasm for opportunities and challenges

⚠️ **Confidence Building Mistakes:**

• **Fake It Till You Make It**: Pretending to know things you don't or overselling abilities
• **Perfectionism**: Setting unrealistic standards that undermine confidence
• **Comparison Trap**: Constantly comparing yourself to others rather than focusing on your growth
• **Negative Self-Talk**: Engaging in harsh self-criticism that erodes confidence
• **Avoiding Challenges**: Staying in comfort zone instead of building confidence through experience
'''
                }
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
***Navigating Tech Interviews with Industry Expertise***

The technology sector has unique interview processes, cultural expectations, and skill requirements. This lesson provides insider knowledge to help you excel in tech company interviews from startups to FAANG companies.

**Tech Industry Culture and Values**

• **Innovation and Continuous Learning**: Emphasize your passion for technology and problem-solving, demonstrate ability to learn new technologies quickly, show examples of staying current with tech trends, discuss side projects or contributions to open source, and highlight instances where you've driven innovation or process improvement.

• **Collaboration and Agile Methodologies**: Showcase experience with cross-functional teams, demonstrate understanding of agile/scrum methodologies, provide examples of effective collaboration with designers, product managers, and other engineers, and show ability to work in fast-paced, iterative environments.

• **Growth Mindset and Adaptability**: Share examples of learning from failure and iterating quickly, demonstrate flexibility in changing requirements or priorities, show willingness to take on challenges outside your comfort zone, and discuss how you stay updated with rapidly evolving technology landscape.

**Common Tech Interview Formats**

• **Technical Phone/Video Screens**: Prepare for coding challenges on platforms like CoderPad or HackerRank, practice explaining your thought process while coding, be ready to discuss technical concepts and trade-offs, and prepare for questions about your past projects and technical decisions.

• **Coding Challenges and Pair Programming**: Practice coding in collaborative environments, be comfortable with others watching and commenting on your code, prepare to give and receive feedback constructively, and demonstrate good coding practices and clean code principles.

• **System Design Discussions**: Understand scalability, reliability, and performance concepts, practice designing systems for millions of users, be familiar with common architectures and design patterns, and prepare to discuss trade-offs between different technical approaches.

• **Cultural Fit and Values Alignment**: Research company values and mission thoroughly, prepare examples that demonstrate alignment with company culture, show passion for the company's products or services, and be ready to discuss why you want to work specifically for this company.

**Key Technical Skills to Highlight**

• **Programming Languages and Frameworks**: Demonstrate depth in relevant programming languages, show breadth across different technologies and platforms, discuss experience with both frontend and backend technologies when relevant, and highlight experience with cloud platforms and modern development tools.

• **Problem-Solving and Analytical Thinking**: Provide examples of complex technical problems you've solved, demonstrate systematic approach to debugging and troubleshooting, show ability to break down large problems into manageable pieces, and highlight experience with performance optimization and scalability challenges.

• **Software Development Lifecycle**: Show understanding of version control systems (Git), demonstrate experience with CI/CD pipelines and deployment processes, discuss testing strategies and quality assurance practices, and highlight experience with code reviews and collaborative development.

**Tech-Specific Behavioral Questions**

• **"How do you stay updated with new technologies?"**: Discuss specific resources you use (blogs, conferences, courses), mention recent technologies you've learned and applied, show a systematic approach to continuous learning, and demonstrate balance between depth and breadth in learning.

• **"Describe a challenging technical problem you solved"**: Use STAR method with technical depth, explain your debugging and problem-solving process, discuss alternative approaches you considered, and highlight the impact of your solution on the team or product.

• **"How do you approach learning a new technology quickly?"**: Describe your learning methodology and resources, provide specific examples of rapid technology adoption, show how you balance learning with delivery deadlines, and demonstrate ability to become productive quickly in new environments.

• **"Tell me about a time you had to make a technical trade-off"**: Discuss competing priorities (performance vs. maintainability, speed vs. quality), explain your decision-making process and criteria, show understanding of business impact of technical decisions, and demonstrate ability to communicate technical concepts to non-technical stakeholders.

**Company-Specific Preparation**

• **FAANG Companies (Facebook/Meta, Amazon, Apple, Netflix, Google)**: Prepare for rigorous technical interviews with multiple rounds, focus heavily on algorithms and data structures, practice system design for large-scale applications, and research company-specific values and leadership principles.

• **Startups and Scale-ups**: Emphasize versatility and ability to wear multiple hats, show comfort with ambiguity and rapid change, demonstrate entrepreneurial mindset and ownership, and highlight experience building products from scratch or in resource-constrained environments.

• **Enterprise Technology Companies**: Focus on scalability, reliability, and enterprise-grade solutions, demonstrate understanding of enterprise sales cycles and customer needs, show experience with complex, large-scale systems, and highlight ability to work within established processes and frameworks.

💡 **Tech Interview Success Strategies:**

• **Build a Strong Portfolio**: Maintain an active GitHub profile with diverse projects, contribute to open source projects in your area of interest, build and deploy applications that demonstrate your skills, and document your projects with clear README files and technical explanations.

• **Practice Coding Regularly**: Solve coding problems daily on platforms like LeetCode, practice explaining your solutions clearly, time yourself to simulate interview pressure, and focus on both correctness and code quality.

• **Stay Current with Technology**: Follow industry blogs and thought leaders, attend tech meetups and conferences, experiment with new technologies in side projects, and engage with the tech community through forums and social media.

📚 **Tech Industry Resources:**

• "Cracking the Coding Interview" by Gayle McDowell - Essential for technical preparation
• "System Design Interview" by Alex Xu - Comprehensive system design guide
• "The Pragmatic Programmer" by Hunt and Thomas - Software development best practices
• "Clean Code" by Robert Martin - Code quality and craftsmanship

🔗 **Tech Preparation Platforms:**

• LeetCode.com - Coding interview practice with company-specific questions
• HackerRank.com - Technical assessments and skill development
• Pramp.com - Free peer-to-peer mock technical interviews
• InterviewBit.com - Structured technical interview preparation
• Glassdoor.com - Company-specific interview experiences and questions
'''
                },
                {
                    'id': 2,
                    'title': 'Finance & Banking Excellence',
                    'duration': '40 min',
                    'content': '''
***Mastering Finance Industry Interviews***

Finance and banking interviews require deep analytical skills, attention to detail, and understanding of market dynamics. This lesson prepares you for the rigorous interview processes in investment banking, asset management, corporate finance, and fintech.

**Finance Industry Expectations**

• **Analytical and Quantitative Skills**: Demonstrate strong mathematical and statistical abilities, show experience with financial modeling and valuation techniques, highlight proficiency with Excel, SQL, and financial software, and provide examples of data-driven decision making and analysis.

• **Attention to Detail and Accuracy**: Emphasize precision in financial calculations and reporting, show experience with reconciliation and error detection, demonstrate understanding of the importance of accuracy in financial decisions, and highlight quality control processes you've implemented or followed.

• **Risk Management Awareness**: Understand different types of financial risk (market, credit, operational, liquidity), demonstrate experience with risk assessment and mitigation strategies, show knowledge of regulatory requirements and compliance, and discuss how you've managed risk in previous roles or projects.

• **Ethical Standards and Integrity**: Emphasize commitment to ethical behavior and fiduciary responsibility, understand conflicts of interest and how to manage them, demonstrate knowledge of industry regulations and compliance requirements, and provide examples of ethical decision-making in challenging situations.

**Technical Knowledge Areas**

• **Financial Modeling and Valuation**: Master DCF (Discounted Cash Flow) modeling techniques, understand comparable company analysis and precedent transactions, know LBO (Leveraged Buyout) modeling for private equity roles, and be familiar with options pricing models and derivatives valuation.

• **Financial Statements Analysis**: Thoroughly understand income statements, balance sheets, and cash flow statements, know how to analyze financial ratios and trends, understand the relationship between different financial statements, and be able to identify red flags and areas of concern in financial reports.

• **Market Knowledge**: Stay current with market conditions and economic indicators, understand how macroeconomic factors affect different asset classes, know major market events and their implications, and be familiar with different investment strategies and their risk-return profiles.

• **Regulatory Environment**: Understand key regulations affecting your target role (Dodd-Frank, Basel III, MiFID II), know compliance requirements and reporting obligations, understand the role of regulatory bodies (SEC, FINRA, Fed), and stay updated on regulatory changes and their industry impact.

**Finance-Specific Interview Questions**

• **"Walk me through a DCF model"**: Explain each component clearly (revenue projections, expenses, capital expenditures, working capital, terminal value), discuss key assumptions and sensitivities, explain how to determine appropriate discount rates, and be prepared to build a simple model on paper or whiteboard.

• **"How do you value a company?"**: Discuss multiple valuation methodologies (DCF, comparable companies, precedent transactions), explain when to use each approach, understand the pros and cons of different methods, and be able to walk through a valuation step-by-step.

• **"Explain a recent market event and its implications"**: Choose a significant recent event you understand well, explain the causes and immediate effects, discuss broader market implications, and demonstrate understanding of how different stakeholders were affected.

• **"How do you assess credit risk?"**: Discuss financial ratio analysis and credit metrics, explain the importance of cash flow analysis, understand collateral and covenant structures, and be familiar with credit rating methodologies and factors.

**Behavioral Competencies**

• **Decision-Making Under Pressure**: Provide examples of making important decisions with incomplete information, show ability to prioritize and manage multiple urgent tasks, demonstrate composure during market volatility or crisis situations, and highlight experience working under tight deadlines with high stakes.

• **Client Relationship Management**: Show experience building and maintaining professional relationships, demonstrate ability to explain complex financial concepts to non-experts, provide examples of managing difficult client situations, and highlight success in meeting client needs and expectations.

• **Team Collaboration**: Demonstrate ability to work effectively in high-pressure team environments, show experience collaborating across different functions (sales, operations, compliance), provide examples of contributing to team success, and highlight leadership experience in project or deal teams.

💡 **Finance Interview Preparation Tips:**

• **Stay Market Current**: Read financial news daily (WSJ, FT, Bloomberg), understand current market conditions and trends, follow key economic indicators and their implications, and be prepared to discuss recent market events intelligently.

• **Practice Technical Skills**: Build financial models from scratch, practice valuation exercises with real companies, work through case studies and brain teasers, and be comfortable with mental math and quick calculations.

• **Understand the Business**: Research the specific firm's business model and strategy, understand their key clients and market position, know their recent deals or investment performance, and be familiar with their competitive landscape.

📚 **Finance Industry Resources:**

• "Investment Banking: Valuation, Leveraged Buyouts, and Mergers & Acquisitions" by Rosenbaum and Pearl
• "Financial Modeling" by Simon Benninga - Comprehensive modeling techniques
• "The Intelligent Investor" by Benjamin Graham - Investment philosophy and analysis
• "Options, Futures, and Other Derivatives" by John Hull - Derivatives and risk management

🔗 **Finance Preparation Resources:**

• Wall Street Prep - Financial modeling courses and practice
• CFA Institute - Professional development and industry standards
• Bloomberg Terminal training - Industry-standard financial data platform
• Financial Edge - Interview preparation specifically for finance roles
'''
                },
                {
                    'id': 3,
                    'title': 'Healthcare & Life Sciences',
                    'duration': '35 min',
                    'content': '''
***Excellence in Healthcare Industry Interviews***

Healthcare interviews emphasize patient care, ethical decision-making, and regulatory compliance. This lesson prepares you for interviews in hospitals, pharmaceutical companies, medical device firms, and healthcare technology organizations.

**Healthcare Industry Values**

• **Patient-Centered Care and Safety**: Demonstrate commitment to patient welfare above all else, show understanding of patient rights and dignity, provide examples of advocating for patient needs, and highlight experience with patient safety protocols and quality improvement initiatives.

• **Ethical Decision-Making**: Understand healthcare ethics principles (autonomy, beneficence, non-maleficence, justice), demonstrate ability to navigate ethical dilemmas, show respect for patient confidentiality and privacy, and provide examples of ethical decision-making in challenging situations.

• **Continuous Learning and Evidence-Based Practice**: Show commitment to staying current with medical advances and best practices, demonstrate ability to critically evaluate research and evidence, highlight participation in continuing education and professional development, and provide examples of implementing evidence-based improvements.

• **Collaboration and Interdisciplinary Teamwork**: Demonstrate ability to work effectively with diverse healthcare professionals, show experience in multidisciplinary team settings, provide examples of successful collaboration across departments, and highlight communication skills with both clinical and non-clinical staff.

**Key Healthcare Competencies**

• **Clinical Knowledge and Technical Skills**: Demonstrate relevant clinical expertise for your role, show proficiency with medical technologies and equipment, understand diagnostic and treatment protocols, and highlight experience with clinical documentation and record-keeping.

• **Communication with Patients and Families**: Provide examples of explaining complex medical information clearly, demonstrate empathy and compassion in difficult situations, show ability to handle emotional or distressed patients and families, and highlight experience with diverse patient populations and cultural sensitivity.

• **Critical Thinking and Problem-Solving**: Demonstrate ability to assess complex clinical situations, show systematic approach to diagnosis and treatment planning, provide examples of identifying and resolving problems quickly, and highlight experience with emergency or crisis situations.

**Regulatory and Compliance Knowledge**

• **HIPAA and Patient Privacy**: Understand patient privacy rights and confidentiality requirements, demonstrate knowledge of proper information sharing protocols, show experience with secure communication and documentation practices, and understand consequences of privacy violations.

• **Quality Assurance and Safety Protocols**: Understand Joint Commission standards and accreditation requirements, demonstrate knowledge of infection control and safety procedures, show experience with quality improvement initiatives, and understand incident reporting and root cause analysis.

• **Regulatory Bodies and Standards**: Understand FDA regulations for medical devices and pharmaceuticals, know CMS requirements for healthcare reimbursement, be familiar with state licensing and certification requirements, and stay current with healthcare policy changes and their implications.

**Healthcare-Specific Interview Questions**

• **"How do you handle difficult patient situations?"**: Provide specific examples using STAR method, demonstrate empathy and professional boundaries, show de-escalation and communication skills, and highlight collaboration with other team members when appropriate.

• **"Describe your approach to maintaining patient confidentiality"**: Explain understanding of HIPAA requirements, provide examples of protecting patient information, discuss proper communication protocols, and show awareness of technology and security considerations.

• **"How do you stay current with medical advances?"**: Discuss specific resources and continuing education activities, mention professional organizations and conferences you attend, show systematic approach to learning and skill development, and provide examples of implementing new knowledge or practices.

• **"Tell me about a time you had to make a critical decision quickly"**: Use healthcare-specific example with patient safety implications, explain your decision-making process and criteria, discuss how you involved other team members when appropriate, and highlight the outcome and lessons learned.

**Specialized Healthcare Sectors**

• **Pharmaceutical and Biotech**: Understand drug development and clinical trial processes, know FDA approval pathways and regulatory requirements, demonstrate knowledge of pharmacovigilance and safety monitoring, and show understanding of market access and commercialization strategies.

• **Medical Devices**: Understand device development and testing protocols, know FDA classification and approval processes, demonstrate knowledge of quality management systems (ISO 13485), and show understanding of clinical evidence requirements and post-market surveillance.

• **Healthcare Technology**: Understand electronic health records and interoperability challenges, know healthcare data standards (HL7, FHIR), demonstrate knowledge of telemedicine and digital health trends, and show understanding of healthcare IT security and privacy requirements.

💡 **Healthcare Interview Success Strategies:**

• **Understand the Organization**: Research the healthcare system's mission and patient population, understand their quality metrics and performance indicators, know their recent initiatives and strategic priorities, and be familiar with their reputation and market position.

• **Prepare Patient-Centered Examples**: Develop stories that demonstrate patient advocacy and care, show examples of improving patient outcomes or satisfaction, highlight experience with diverse patient populations, and demonstrate cultural competency and sensitivity.

• **Stay Current with Healthcare Trends**: Understand current healthcare challenges (cost, access, quality), know about healthcare reform and policy changes, be familiar with emerging technologies and their applications, and understand population health and value-based care concepts.

📚 **Healthcare Industry Resources:**

• "The Checklist Manifesto" by Atul Gawande - Quality and safety in healthcare
• "Being Mortal" by Atul Gawande - Healthcare ethics and patient care
• "The Innovator's Prescription" by Clayton Christensen - Healthcare innovation and disruption
• "Redefining Health Care" by Porter and Teisberg - Value-based healthcare delivery

🔗 **Healthcare Preparation Resources:**

• Healthcare Financial Management Association (HFMA) - Industry knowledge and networking
• American Organization for Nursing Leadership (AONL) - Healthcare leadership development
• Healthcare Information and Management Systems Society (HIMSS) - Health IT knowledge
• Joint Commission Resources - Quality and safety standards and best practices
'''
                }
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
                    'duration': '25 min',
                    'content': 'Learn to research salary ranges, understand total compensation packages, and assess your market value accurately.'
                },
                {
                    'id': 2,
                    'title': 'Negotiation Strategies & Tactics',
                    'duration': '30 min',
                    'content': 'Master negotiation techniques, timing strategies, and communication approaches that lead to successful salary negotiations.'
                },
                {
                    'id': 3,
                    'title': 'Beyond Base Salary',
                    'duration': '20 min',
                    'content': 'Explore benefits, equity, flexible work arrangements, and other compensation elements that can significantly impact your total package.'
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