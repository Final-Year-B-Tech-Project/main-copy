# 🤖 Talent Sync

A comprehensive AI-powered interview platform built with Python Flask and vanilla JavaScript. This system enables students to practice interviews with real-time AI feedback and allows HR professionals to manage job drives and conduct efficient, proctored candidate evaluations.

---

## ✨ Key Features

### For Students
- **Practice Interviews**: Unlimited AI-powered practice sessions for standard and custom roles.
- **Custom Target Role Customization**: Custom form to input target job role, key requirements, targeted skills, and focus area.
- **Real-time Feedback**: Instant AI analysis, suggestions, and communication score breakdown.
- **Resume Upload & Parsing**: Automatic skill extraction from PDF/Text resumes.
- **Voice-to-Text Support**: Speak answers directly with built-in voice recognition, modern soundwave indicators, and smart timeout detection.

### For HR & Recruiters
- **Job Drive Management**: Create, view, and track recruitment drives.
- **Candidate Scheduling**: Invite and coordinate candidates with automated email notifications.
- **Bias-Free Screening & Scorecards**: Automated grading across Technical, Communication, Problem Solving, and Confidence scores.
- **Dynamic Proctoring Panel**: Monitors tab switching and tracks active face counts.

### Core Architecture & AI Engine
- **Multimodal AI Supervisor**: Dynamically adjusts question difficulty, paces the interview flow, and determines optimal session endings.
- **Provider Failover Chain**: Gracefully redirects API queries from Groq (Llama 3) to OpenRouter (Gemini/Claude) and local fallback servers for 99.9% uptime.
- **SMTP Email Notifications**: Formats dynamic interview duration (e.g., `5m 24s`) and delivers dark-themed scorecard feedback directly to candidates.

---

## 🛠️ Technology Stack

### Backend
- **Python 3.12**: Core programming language
- **Flask 2.3+**: Web framework
- **SQLAlchemy (SQLite)**: Database ORM and persistence
- **Google Gemini & Groq APIs**: Advanced LLMs for adaptive responses and evaluation
- **PyPDF2**: Resume parsing functionality

### Frontend
- **Vanilla JavaScript**: Zero heavy framework dependencies
- **CSS3 / theme_fixes**: Sleek, glassmorphic dark-themed user interface
- **Font Awesome 6 & Google Fonts**: Premium iconography and typography

---

## 📋 Prerequisites

- Python 3.8 or higher
- Git (for version control)
- Google Gemini API Key and/or Groq API Key
- Modern web browser (Chrome, Edge, or Safari for SpeechRecognition support)

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-interview-agent.git
cd ai-interview-agent
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root folder with the following variables:
```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///interview_agent.db
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
OPENROUTER_API_KEY=your-openrouter-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 5. Initialize the Database
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 6. Run the Application
```bash
python run.py
```
The application will be available at: **http://127.0.0.1:5000**

---

## 📁 Project Structure

```
ai-interview-system/
├── app/                      # Backend application package
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models & schemas
│   ├── auth.py              # Authentication routes & sessions
│   ├── main.py              # Main dashboard and student views
│   ├── adaptive_api.py      # AI question generation engine
│   ├── ai_supervisor.py    # AI Supervisor difficulty/ending manager
│   ├── real_scoring_system.py # Evaluation & scoring metrics
│   ├── ai_service.py        # Failover API provider dispatcher
│   └── email_service.py     # SMTP feedback email delivery
├── templates/               # HTML5 templates
│   ├── base.html           # Main navbar/head layout
│   ├── student/            # Practice, resume, dashboard views
│   ├── hr/                 # Job creation, scheduling, candidate scorecards
│   ├── interview/          # Fullscreen proctored interview panel
│   └── emails/             # Feedback email layouts
├── static/                 # Assets & stylesheets
│   ├── css/               # Futuristic themes and theme fixes
│   └── js/                # Face tracking and voice recognition
├── requirements.txt       # Python dependency file
└── README.md             # Project documentation
```

---

## 🎯 Usage Guide

### 1. Student Custom Role Practice
* Navigate to the Student Dashboard and click **Practice Interview**.
* Select the **Custom Role** card option.
* Enter your custom job role, targeted skills (comma separated), targeted key requirements, and interview focus details.
* The welcome prompt and all subsequent adaptive questions will target these customized requirements.

### 2. Proctored Voice & Face Checks
* Standard/Adaptive interviews require browser permissions for camera and microphone.
* The system utilizes **face-api.js** to track face counts and detect cheating/tab-switches.
* Dynamic voice submission evaluates speech patterns and automatically pauses voice recognition when the system speaks.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes and push.
4. Submit a pull request.

---

**Made with ❤️ for better interviews and smarter hiring**
