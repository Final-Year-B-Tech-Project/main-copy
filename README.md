# 🤖 Talent Sync

A comprehensive AI-powered interview platform built with Python Flask and vanilla JavaScript. This system enables students to practice interviews with AI feedback and allows HR professionals to manage job drives and conduct efficient candidate evaluations.

## ✨ Features

### For Students
- **Practice Interviews**: Unlimited AI-powered practice sessions
- **Real-time Feedback**: Instant AI analysis and suggestions
- **Resume Upload & Parsing**: Automatic skill extraction from resumes
- **Performance Tracking**: Monitor progress over time
- **Personalized Questions**: AI generates questions based on profile and experience

### For HR Professionals
- **Job Drive Management**: Create and manage recruitment drives
- **Candidate Scheduling**: Easy interview scheduling with email notifications
- **AI-Assisted Screening**: Automated candidate evaluation
- **Comprehensive Analytics**: Detailed reports and insights
- **Bias-Free Evaluations**: Fair AI-powered assessments

### Core Features
- **Dual Account Types**: Separate interfaces for students and HR
- **AI-Powered Interviews**: Dynamic question generation using Google Gemini
- **Code Compiler Integration**: Built-in coding environment for technical interviews
- **Real-time Interface**: Live interview experience with timer and progress tracking
- **Secure Authentication**: Role-based access control with Flask-Login
- **File Upload Support**: Resume and profile photo uploads
- **Email Conflict Resolution**: Smart handling of duplicate emails across user types

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask 2.3+**: Web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Development database (PostgreSQL for production)
- **Google Gemini AI**: AI question generation and feedback
- **PyPDF2**: Resume parsing functionality

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Bootstrap 5.3**: Responsive UI framework
- **Font Awesome 6**: Icon library
- **jQuery 3.7**: DOM manipulation (minimal usage)

### Infrastructure
- **Free Hosting Options**: PythonAnywhere, Railway.app, Vercel
- **File Storage**: Local filesystem (development)
- **Environment Management**: python-dotenv for configuration

## 📋 Prerequisites

- Python 3.8 or higher
- Git (for version control)
- Google Gemini API key (free tier available)
- Modern web browser
- Text editor or IDE

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

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your configuration
# Required: Add your Google Gemini API key
```

**.env file configuration:**
```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=sqlite:///interview_agent.db
GEMINI_API_KEY=your-gemini-api-key-here
```

### 5. Get Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

**Free Tier Limits:**
- 5 requests per minute
- 25 requests per day
- Perfect for development and testing

### 6. Initialize Database

```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 7. Run the Application

```bash
# Using the development runner (recommended)
python run.py

# Or using the main app file
python app.py
```

The application will be available at: **http://127.0.0.1:5000**

## 📁 Project Structure

```
ai-interview-agent/
├── app/                      # Main application package
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── auth.py              # Authentication routes
│   ├── main.py              # Main application routes
│   ├── ai_service.py        # AI integration service
│   └── utils.py             # Utility functions
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Landing page
│   ├── auth/               # Authentication templates
│   ├── student/            # Student dashboard templates
│   ├── hr/                 # HR dashboard templates
│   ├── interview/          # Interview interface templates
│   └── components/         # Reusable components
├── static/                 # Static files
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   ├── images/            # Images and logos
│   └── uploads/           # User uploaded files
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── run.py                # Development server runner
├── app.py                # Production entry point
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🎯 Usage Guide

### For Students

1. **Registration**:
   - Visit the homepage and click "Get Started"
   - Choose "Student" account type
   - Fill in your details including educational background
   - Upload your resume (optional but recommended)

2. **Practice Interviews**:
   - Go to Dashboard → Practice Interview
   - Select job role, difficulty level, and experience
   - Start the AI-powered interview session
   - Answer questions using text, voice, or code
   - Receive instant feedback and scoring

3. **Profile Management**:
   - Update your skills and experience
   - Upload a new resume for better AI personalization
   - Track your interview performance over time

### For HR Professionals

1. **Registration**:
   - Choose "HR Professional" account type
   - Provide company details and your HR credentials
   - Get assigned a unique HR code for verification

2. **Job Drive Management**:
   - Create new job drives with detailed requirements
   - Set application deadlines and position details
   - Define custom interview questions if needed

3. **Candidate Management**:
   - Schedule interviews for candidates
   - Send interview invitations via email
   - Monitor interview status and progress
   - Review AI-generated candidate evaluations

4. **Analytics & Reports**:
   - View comprehensive hiring analytics
   - Track candidate performance metrics
   - Export reports for further analysis

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FLASK_ENV` | Environment mode | No | `development` |
| `SECRET_KEY` | Flask secret key | Yes | - |
| `DATABASE_URL` | Database connection string | No | SQLite local |
| `GEMINI_API_KEY` | Google Gemini API key | Yes for AI features | - |
| `MAIL_SERVER` | SMTP server for emails | No | - |
| `MAIL_USERNAME` | Email username | No | - |
| `MAIL_PASSWORD` | Email password | No | - |

### Database Configuration

**Development (SQLite):**
```python
DATABASE_URL=sqlite:///interview_agent.db
```

**Production (PostgreSQL):**
```python
DATABASE_URL=postgresql://username:password@host:port/database
```

## 🔧 Advanced Setup

### Custom AI Configuration

Modify `app/ai_service.py` to customize:
- Question generation algorithms
- Feedback scoring mechanisms
- Interview difficulty levels
- Custom evaluation criteria

### Email Notifications

Configure SMTP settings in `.env`:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### File Upload Limits

Adjust in `config.py`:
```python
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
```

## 🚀 Deployment

### Free Hosting Options

#### 1. PythonAnywhere (Recommended)
- Free tier includes Python web apps
- Easy setup with Flask support
- Built-in file management

#### 2. Railway.app
- Git-based deployments
- Automatic scaling
- PostgreSQL integration

#### 3. Vercel (with serverless functions)
- Fast global CDN
- Automatic deployments from Git
- Environment variable management

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Set up SSL/HTTPS
- [ ] Configure email notifications
- [ ] Set up monitoring and logging
- [ ] Backup strategy for user data

## 🔍 Troubleshooting

### Common Issues

**Database Issues:**
```bash
# Reset database
rm interview_agent.db
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

**Gemini API Errors:**
- Check API key validity
- Verify internet connection
- Monitor rate limits (5 RPM free tier)

**File Upload Issues:**
- Check file size limits
- Verify upload directory permissions
- Ensure allowed file extensions

### Debug Mode

Enable detailed error logging:
```python
FLASK_DEBUG=1
FLASK_ENV=development
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and code comments
- **Issues**: Create a GitHub issue for bugs or feature requests
- **Email**: support@aiinterview.com (if applicable)

## 🔮 Future Enhancements

- [ ] Mobile application (React Native/Flutter)
- [ ] Video interview capabilities
- [ ] Advanced analytics dashboard
- [ ] Integration with ATS systems
- [ ] Multi-language support
- [ ] Real-time collaboration features
- [ ] Advanced AI models (GPT integration)
- [ ] Blockchain-based certificate system

## 🙏 Acknowledgments

- Google Gemini AI for natural language processing
- Bootstrap team for the excellent UI framework
- Flask community for the amazing web framework
- All contributors and beta testers

---

**Made with ❤️ for better interviews and smarter hiring**

---

**Talent Sync - Revolutionizing the Interview Experience**
# main-copy
