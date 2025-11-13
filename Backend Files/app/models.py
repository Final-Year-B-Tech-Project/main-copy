from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """User model for both HR and Students."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'student', 'hr', 'admin', 'master_admin'
    role = db.Column(db.String(50), default='user')  # 'user', 'admin', 'master_admin', 'developer'
    permissions = db.Column(db.Text)  # JSON string of permissions
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    profile_photo = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    hr_profile = db.relationship('HRProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    interview_sessions = db.relationship('InterviewSession', backref='candidate', lazy='dynamic')
    
    def has_permission(self, permission):
        """Check if user has specific permission."""
        if self.role == 'master_admin':
            return True
        if not self.permissions:
            return False
        import json
        try:
            perms = json.loads(self.permissions)
            return permission in perms
        except:
            return False
    
    def is_admin(self):
        """Check if user is any type of admin."""
        return self.role in ['admin', 'master_admin', 'developer']
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        # Handle both Werkzeug hashes and simple SHA256 hashes
        if self.password_hash.startswith('pbkdf2:') or self.password_hash.startswith('scrypt:'):
            return check_password_hash(self.password_hash, password)
        else:
            # Simple SHA256 hash (from quick fix)
            import hashlib
            return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    @property
    def full_name(self):
        """Get full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.username}>'

class StudentProfile(db.Model):
    """Extended profile for students."""
    __tablename__ = 'student_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    university = db.Column(db.String(100))
    degree = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer)
    gpa = db.Column(db.Float)
    skills = db.Column(db.Text)  # JSON string of skills
    resume_file = db.Column(db.String(255))
    resume_text = db.Column(db.Text)  # Parsed resume content
    experience_level = db.Column(db.String(20))  # 'fresher', 'experienced'
    preferred_roles = db.Column(db.Text)  # JSON string of preferred job roles
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HRProfile(db.Model):
    """Extended profile for HR professionals."""
    __tablename__ = 'hr_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_website = db.Column(db.String(255))
    company_description = db.Column(db.Text)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    employee_id = db.Column(db.String(50))
    hr_code = db.Column(db.String(20), unique=True)  # Special HR identification code
    years_experience = db.Column(db.Integer)
    specializations = db.Column(db.Text)  # JSON string of HR specializations
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_drives = db.relationship('JobDrive', backref='hr', lazy='dynamic')

class JobDrive(db.Model):
    """Job drives created by HR."""
    __tablename__ = 'job_drive'
    
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('hr_profile.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    job_role = db.Column(db.String(100), nullable=False)
    experience_required = db.Column(db.String(50))
    skills_required = db.Column(db.Text)  # JSON string
    number_of_positions = db.Column(db.Integer, default=1)
    location = db.Column(db.String(100))
    salary_range = db.Column(db.String(100))
    deadline = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    interview_questions = db.Column(db.Text)  # JSON string of custom questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interview_sessions = db.relationship('InterviewSession', backref='job_drive', lazy='dynamic')

class InterviewSession(db.Model):
    """Interview sessions for tracking interviews."""
    __tablename__ = 'interview_session'
    
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_drive_id = db.Column(db.Integer, db.ForeignKey('job_drive.id'), nullable=True)  # Null for practice interviews
    session_type = db.Column(db.String(20), nullable=False)  # 'practice', 'actual'
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'in_progress', 'completed', 'cancelled'
    scheduled_time = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # Duration in seconds
    questions = db.Column(db.Text)  # JSON string of questions asked
    responses = db.Column(db.Text)  # JSON string of candidate responses
    ai_feedback = db.Column(db.Text)  # AI-generated feedback
    hr_feedback = db.Column(db.Text)  # HR feedback (for actual interviews)
    overall_score = db.Column(db.Float)
    technical_score = db.Column(db.Float)
    communication_score = db.Column(db.Float)
    confidence_score = db.Column(db.Float)
    coding_score = db.Column(db.Float)
    interview_link = db.Column(db.String(255))  # Unique interview link
    notes = db.Column(db.Text)  # Additional notes and metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Removed unused models to fix foreign key issues