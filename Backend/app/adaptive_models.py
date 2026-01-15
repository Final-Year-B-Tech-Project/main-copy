from datetime import datetime
from app import db
import json

class AdaptiveSession(db.Model):
    """Adaptive interview session with 3-phase system"""
    __tablename__ = 'adaptive_session'
    
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    current_phase = db.Column(db.String(20), default='intro')  # intro, core, closing
    status = db.Column(db.String(20), default='active')  # active, completed, terminated
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_duration = db.Column(db.Integer, default=0)  # seconds
    target_duration = db.Column(db.Integer, default=1200)  # 20 minutes
    conversation_history = db.Column(db.Text)  # JSON
    evaluation_notes = db.Column(db.Text)  # JSON
    final_transcript = db.Column(db.Text)
    final_feedback = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdaptiveQuestion(db.Model):
    """Individual questions in adaptive session"""
    __tablename__ = 'adaptive_question'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('adaptive_session.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    phase = db.Column(db.String(20), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))
    category = db.Column(db.String(50))
    time_limit = db.Column(db.Integer, default=300)
    asked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class AdaptiveResponse(db.Model):
    """Candidate responses to adaptive questions"""
    __tablename__ = 'adaptive_response'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('adaptive_question.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('adaptive_session.id'), nullable=False)
    response_text = db.Column(db.Text)
    response_time = db.Column(db.Integer)  # seconds taken
    quality_score = db.Column(db.Float)
    evaluation_notes = db.Column(db.Text)  # JSON
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)