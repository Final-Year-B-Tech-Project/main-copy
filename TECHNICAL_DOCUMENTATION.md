# TALENT SYNC - TECHNICAL DOCUMENTATION

## System Architecture & Implementation Details

---

## TABLE OF CONTENTS

1. System Architecture
2. Database Design
3. API Documentation
4. AI Implementation
5. Security Implementation
6. Deployment Guide
7. Code Structure

---

## 1. SYSTEM ARCHITECTURE

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Browser │  │  Mobile  │  │  Tablet  │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Flask Templates (Jinja2)                            │  │
│  │  - HTML5, CSS3, Bootstrap 5                          │  │
│  │  - JavaScript (Vanilla)                              │  │
│  │  - Web Speech API                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Flask Application (Python 3.11)                     │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │   Auth     │  │  Student   │  │     HR     │    │  │
│  │  │  Module    │  │   Module   │  │   Module   │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │    AI      │  │   Email    │  │    PDF     │    │  │
│  │  │  Service   │  │  Service   │  │ Generator  │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SQLAlchemy ORM                                      │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │   SQLite   │  │    File    │  │   Cache    │    │  │
│  │  │  Database  │  │  Storage   │  │   (Redis)  │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ OpenRouter │  │   SMTP     │  │  Storage   │           │
│  │     AI     │  │   Server   │  │  Service   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  app/__init__.py (Application Factory)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌─────────────┬──────────┴──────────┬─────────────┐      │
│  │             │                     │             │      │
│  ▼             ▼                     ▼             ▼      │
│  auth.py    student.py            hr.py        main.py    │
│  (Auth)     (Student)             (HR)         (Core)     │
│                                                             │
│  ┌─────────────┬──────────┬──────────┬─────────────┐      │
│  │             │          │          │             │      │
│  ▼             ▼          ▼          ▼             ▼      │
│  models.py  ai_service  email_    pdf_        utils.py    │
│  (DB)       .py (AI)    service   generator   (Helpers)   │
│                         .py       .py                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. DATABASE DESIGN

### 2.1 Entity-Relationship Diagram

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    User      │         │   Student    │         │      HR      │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id (PK)      │◄───────┤ id (PK)      │         │ id (PK)      │
│ email        │         │ user_id (FK) │         │ user_id (FK) │
│ password     │         │ college      │         │ company      │
│ user_type    │         │ degree       │         │ designation  │
│ created_at   │         │ skills       │         │ department   │
└──────────────┘         │ resume_path  │         │ hr_code      │
                         └──────────────┘         └──────────────┘
                                │                         │
                                │                         │
                                ▼                         ▼
                         ┌──────────────┐         ┌──────────────┐
                         │  Interview   │◄────────┤  Job Drive   │
                         │   Session    │         ├──────────────┤
                         ├──────────────┤         │ id (PK)      │
                         │ id (PK)      │         │ hr_id (FK)   │
                         │ student_id   │         │ job_title    │
                         │ job_drive_id │         │ description  │
                         │ status       │         │ skills_req   │
                         │ score        │         │ deadline     │
                         │ duration     │         └──────────────┘
                         │ feedback     │
                         └──────────────┘
```

### 2.2 Table Schemas

**users**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**students**
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    college VARCHAR(200),
    degree VARCHAR(100),
    year_of_study VARCHAR(20),
    skills TEXT,
    resume_path VARCHAR(255),
    profile_photo VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**hr_professionals**
```sql
CREATE TABLE hr_professionals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    designation VARCHAR(100),
    department VARCHAR(100),
    phone VARCHAR(15),
    hr_code VARCHAR(20) UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**job_drives**
```sql
CREATE TABLE job_drives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hr_id INTEGER NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    job_type VARCHAR(50),
    experience_required VARCHAR(50),
    skills_required TEXT,
    job_description TEXT,
    num_positions INTEGER,
    application_deadline DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hr_id) REFERENCES hr_professionals(id)
);
```

**interview_sessions**
```sql
CREATE TABLE interview_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    job_drive_id INTEGER,
    session_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    scheduled_at DATETIME,
    started_at DATETIME,
    completed_at DATETIME,
    duration INTEGER,
    overall_score FLOAT,
    technical_score FLOAT,
    communication_score FLOAT,
    problem_solving_score FLOAT,
    feedback_json TEXT,
    questions_json TEXT,
    responses_json TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (job_drive_id) REFERENCES job_drives(id)
);
```

---

## 3. API DOCUMENTATION

### 3.1 Authentication APIs

**POST /auth/register**
```json
Request:
{
    "email": "student@example.com",
    "password": "SecurePass123",
    "user_type": "student",
    "full_name": "John Doe",
    "college": "MIT",
    "degree": "Computer Science"
}

Response (200):
{
    "success": true,
    "message": "Registration successful",
    "user_id": 123
}
```

**POST /auth/login**
```json
Request:
{
    "email": "student@example.com",
    "password": "SecurePass123"
}

Response (200):
{
    "success": true,
    "message": "Login successful",
    "redirect": "/student/dashboard"
}
```

### 3.2 Interview APIs

**POST /student/start-practice**
```json
Request:
{
    "job_role": "Software Developer",
    "difficulty": "medium",
    "experience_level": "fresher",
    "num_questions": 5
}

Response (200):
{
    "success": true,
    "session_id": 456,
    "redirect_url": "/adaptive-interview/456"
}
```

**POST /api/generate-ai-response**
```json
Request:
{
    "session_id": 456,
    "message": "I have 3 years of experience in Python",
    "current_tool": "video",
    "interactions": []
}

Response (200):
{
    "success": true,
    "response": "That's great! Can you describe a complex project you worked on?"
}
```

**POST /adaptive-interview/{session_id}/complete**
```json
Request:
{
    "interactions": [...],
    "all_responses": [...],
    "completed": true
}

Response (200):
{
    "success": true,
    "redirect_url": "/interview/456/feedback"
}
```

### 3.3 HR APIs

**POST /hr/create-job-drive**
```json
Request:
{
    "job_title": "Senior Software Engineer",
    "job_role": "Software Developer",
    "department": "Engineering",
    "experience_required": "3-5 years",
    "skills_required": "Python, Flask, React",
    "num_positions": 5,
    "application_deadline": "2025-02-28"
}

Response (200):
{
    "success": true,
    "job_drive_id": 789,
    "message": "Job drive created successfully"
}
```

---

## 4. AI IMPLEMENTATION

### 4.1 AI Service Architecture

```python
class AIInterviewService:
    def __init__(self):
        self.models = {
            'question_generation': 'x-ai/grok-4-fast:free',
            'feedback_analysis': 'deepseek/deepseek-chat-v3.1:free',
            'technical_evaluation': 'openai/gpt-oss-120b:free'
        }
        self.fallback_models = {
            'question_generation': ['google/gemini-2.0-flash-exp:free'],
            'feedback_analysis': ['meta-llama/llama-3.2-3b-instruct:free']
        }
```

### 4.2 Question Generation Algorithm

```python
def generate_interview_questions(self, job_role, difficulty, num_questions):
    prompt = f"""Generate {num_questions} professional interview questions 
    for {job_role} position at {difficulty} difficulty level.
    
    Requirements:
    - Mix technical, behavioral, and situational questions
    - Progress from easier to harder
    - Focus on real-world scenarios
    
    Return JSON array format."""
    
    response = self._make_api_request(self.models['question_generation'], prompt)
    questions = self._parse_questions_response(response)
    return self._validate_questions(questions, num_questions)
```

### 4.3 Dynamic Scoring Algorithm

```python
def calculate_dynamic_score(answered_count, total_questions, avg_response_length):
    # Response quality based on completion
    response_quality = (answered_count / total_questions) * 100
    
    # Length quality (50+ chars = good)
    length_quality = min(100, (avg_response_length / 50) * 100)
    
    # Base score calculation
    base_score = (response_quality + length_quality) / 2
    
    # Clamp between 20-100
    return max(20, min(100, int(base_score)))
```

### 4.4 Feedback Generation

```python
def generate_feedback(self, questions, responses, session):
    conversation = self._prepare_full_conversation_history(questions, responses)
    base_score = self._calculate_dynamic_score(responses)
    
    prompt = f"""Analyze this interview conversation and provide feedback.
    
    Base Performance Score: {base_score}/100
    
    Conversation: {json.dumps(conversation)}
    
    Scoring Guidelines:
    - Short answers ("hello"): 20-40
    - Medium answers: 60-75
    - Detailed answers: 80-95
    
    Return comprehensive JSON feedback."""
    
    response = self._make_api_request(self.models['feedback_analysis'], prompt)
    return self._validate_comprehensive_feedback(response)
```

---

## 5. SECURITY IMPLEMENTATION

### 5.1 Authentication Security

**Password Hashing:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Storing password
password_hash = generate_password_hash(password, method='pbkdf2:sha256')

# Verifying password
is_valid = check_password_hash(stored_hash, provided_password)
```

**Session Management:**
```python
from flask_login import LoginManager, login_user, logout_user

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
```

### 5.2 Data Protection

**SQL Injection Prevention:**
```python
# Using SQLAlchemy ORM (parameterized queries)
user = User.query.filter_by(email=email).first()

# Never use string concatenation
# BAD: f"SELECT * FROM users WHERE email='{email}'"
```

**XSS Prevention:**
```python
# Jinja2 auto-escapes by default
{{ user_input }}  # Automatically escaped

# For raw HTML (use cautiously)
{{ user_input | safe }}
```

**CSRF Protection:**
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# In forms
<form method="POST">
    {{ form.csrf_token }}
    ...
</form>
```

### 5.3 File Upload Security

```python
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename_custom(filename):
    # Remove dangerous characters
    filename = secure_filename(filename)
    # Add timestamp to prevent overwrites
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{filename}"
```

---

## 6. DEPLOYMENT GUIDE

### 6.1 Local Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/talentsync.git
cd talentsync

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Run development server
python run.py
```

### 6.2 Production Deployment

**Using Gunicorn:**
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

**Using Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

### 6.3 Environment Variables

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-super-secret-key-change-this

# Database
DATABASE_URL=postgresql://user:pass@localhost/talentsync

# AI Service
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# File Upload
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=5242880
```

---

## 7. CODE STRUCTURE

### 7.1 Project Directory Structure

```
talentsync/
├── app/
│   ├── __init__.py           # Application factory
│   ├── models.py             # Database models
│   ├── auth.py               # Authentication routes
│   ├── student.py            # Student routes
│   ├── hr.py                 # HR routes
│   ├── main.py               # Main routes
│   ├── adaptive_api.py       # Interview API
│   ├── ai_service.py         # AI service
│   ├── email_service.py      # Email service
│   ├── pdf_generator.py      # PDF generation
│   └── utils.py              # Utility functions
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   ├── student/
│   ├── hr/
│   ├── interview/
│   └── emails/
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── run.py                    # Development server
├── .env.example              # Environment template
└── README.md                 # Documentation
```

### 7.2 Key Files Explained

**app/__init__.py** - Application Factory
```python
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    return app
```

**app/models.py** - Database Models
```python
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
```

**app/ai_service.py** - AI Service
```python
class AIInterviewService:
    def generate_interview_questions(self, job_role, difficulty):
        # Question generation logic
        pass
    
    def generate_feedback(self, questions, responses):
        # Feedback generation logic
        pass
```

---

**Version:** 1.0
**Last Updated:** January 2025
**Maintained By:** TalentSync Development Team

---

**END OF TECHNICAL DOCUMENTATION**
