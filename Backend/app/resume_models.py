from datetime import datetime
from app import db
import json

class CandidateSkill(db.Model):
    """Enhanced skill tracking for candidates"""
    __tablename__ = 'candidate_skill'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    skill_category = db.Column(db.String(50))  # 'technical', 'soft', 'domain'
    skill_type = db.Column(db.String(50))  # 'programming', 'framework', 'tool', 'soft_skill'
    proficiency_level = db.Column(db.String(20))  # 'beginner', 'intermediate', 'expert'
    years_experience = db.Column(db.Float)
    extracted_from = db.Column(db.String(20))  # 'resume', 'manual', 'assessment'
    confidence_score = db.Column(db.Float)  # AI confidence in extraction
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ParsedResume(db.Model):
    """Structured resume parsing results"""
    __tablename__ = 'parsed_resume'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    
    # Contact Information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    linkedin_url = db.Column(db.String(255))
    location = db.Column(db.String(100))
    
    # Education
    education_data = db.Column(db.Text)  # JSON: [{'degree', 'university', 'year', 'gpa'}]
    
    # Experience
    experience_data = db.Column(db.Text)  # JSON: [{'company', 'title', 'duration', 'description'}]
    total_experience_years = db.Column(db.Float)
    
    # Projects
    projects_data = db.Column(db.Text)  # JSON: [{'name', 'description', 'technologies'}]
    
    # Parsing metadata
    parsing_confidence = db.Column(db.Float)
    parsing_errors = db.Column(db.Text)
    parsed_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobRequirement(db.Model):
    """Detailed job requirements for matching"""
    __tablename__ = 'job_requirement'
    
    id = db.Column(db.Integer, primary_key=True)
    job_drive_id = db.Column(db.Integer, db.ForeignKey('job_drive.id'), nullable=False)
    
    # Skill requirements
    required_skills = db.Column(db.Text)  # JSON: [{'skill', 'importance', 'min_proficiency'}]
    preferred_skills = db.Column(db.Text)  # JSON
    
    # Experience requirements
    min_experience_years = db.Column(db.Float)
    max_experience_years = db.Column(db.Float)
    experience_level = db.Column(db.String(20))  # 'entry', 'mid', 'senior'
    
    # Education requirements
    min_degree_level = db.Column(db.String(50))  # 'bachelor', 'master', 'phd'
    preferred_degrees = db.Column(db.Text)  # JSON
    min_gpa = db.Column(db.Float)
    
    # Location and availability
    location_type = db.Column(db.String(20))  # 'remote', 'onsite', 'hybrid'
    max_notice_period = db.Column(db.Integer)  # days
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CandidateScore(db.Model):
    """Candidate scoring for specific jobs"""
    __tablename__ = 'candidate_score'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    job_drive_id = db.Column(db.Integer, db.ForeignKey('job_drive.id'), nullable=False)
    
    # Individual scores
    skill_match_score = db.Column(db.Float)  # 0-100
    experience_score = db.Column(db.Float)   # 0-100
    education_score = db.Column(db.Float)    # 0-100
    other_score = db.Column(db.Float)        # 0-100
    
    # Overall eligibility
    overall_score = db.Column(db.Float)      # Weighted average
    is_eligible = db.Column(db.Boolean, default=False)
    is_shortlisted = db.Column(db.Boolean, default=False)
    
    # Detailed breakdown
    skill_matches = db.Column(db.Text)       # JSON: matched skills details
    missing_skills = db.Column(db.Text)      # JSON: missing required skills
    score_breakdown = db.Column(db.Text)     # JSON: detailed scoring
    
    # Shortlisting metadata
    shortlist_reason = db.Column(db.Text)
    shortlisted_at = db.Column(db.DateTime)
    scored_at = db.Column(db.DateTime, default=datetime.utcnow)

class ResumeParsingLog(db.Model):
    """Track resume parsing attempts and results"""
    __tablename__ = 'resume_parsing_log'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(20))
    
    parsing_status = db.Column(db.String(20))  # 'success', 'partial', 'failed'
    skills_extracted = db.Column(db.Integer, default=0)
    sections_parsed = db.Column(db.Text)  # JSON: which sections were successfully parsed
    
    processing_time = db.Column(db.Float)  # seconds
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)