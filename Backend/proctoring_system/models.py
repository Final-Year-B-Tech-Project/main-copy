"""
Proctoring Database Models
Stores proctoring session data, violations, and security events
"""

from app import db
from datetime import datetime
import json

class ProctoringSession(db.Model):
    """Proctoring session data"""
    __tablename__ = 'proctoring_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    interview_session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session timing
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # seconds
    
    # Violation counts
    total_violations = db.Column(db.Integer, default=0)
    warning_count = db.Column(db.Integer, default=0)
    
    # Session status
    status = db.Column(db.String(20), default='active')  # active, completed, terminated
    termination_reason = db.Column(db.String(200))
    
    # Summary data (JSON)
    session_summary = db.Column(db.Text)  # JSON string
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interview_session = db.relationship('InterviewSession', backref='proctoring_session')
    candidate = db.relationship('User', backref='proctoring_sessions')
    violations = db.relationship('ProctoringViolation', backref='session', cascade='all, delete-orphan')

class ProctoringViolation(db.Model):
    """Individual proctoring violations"""
    __tablename__ = 'proctoring_violations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('proctoring_sessions.id'), nullable=False)
    
    # Violation details
    violation_type = db.Column(db.String(50), nullable=False)  # face_absent, multiple_faces, etc.
    violation_message = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    
    # Detection data
    frame_data = db.Column(db.Text)  # JSON string with detection results
    confidence = db.Column(db.Float)
    
    # Timing
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    frame_number = db.Column(db.Integer)
    
    # Action taken
    warning_issued = db.Column(db.Boolean, default=False)
    action_taken = db.Column(db.String(100))  # warning, termination, etc.
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProctoringFrameLog(db.Model):
    """Log of processed frames for analysis"""
    __tablename__ = 'proctoring_frame_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('proctoring_sessions.id'), nullable=False)
    
    # Frame analysis results
    face_count = db.Column(db.Integer, default=0)
    gaze_direction = db.Column(db.String(20))
    blink_status = db.Column(db.String(20))
    mouth_status = db.Column(db.String(20))
    head_pose = db.Column(db.String(20))
    
    # Object detection
    objects_detected = db.Column(db.Text)  # JSON array
    suspicious_objects = db.Column(db.Text)  # JSON array
    
    # Analysis metadata
    processing_time = db.Column(db.Float)  # milliseconds
    frame_quality = db.Column(db.String(20))
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    session = db.relationship('ProctoringSession', backref='frame_logs')

class ProctoringAlert(db.Model):
    """Real-time alerts and notifications"""
    __tablename__ = 'proctoring_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('proctoring_sessions.id'), nullable=False)
    
    # Alert details
    alert_type = db.Column(db.String(50), nullable=False)
    alert_message = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    acknowledged_at = db.Column(db.DateTime)
    
    # Metadata
    alert_data = db.Column(db.Text)  # JSON string
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = db.relationship('ProctoringSession', backref='alerts')
    acknowledger = db.relationship('User', foreign_keys=[acknowledged_by])

# Helper functions for proctoring data
def create_proctoring_session(interview_session_id, candidate_id):
    """Create a new proctoring session"""
    session = ProctoringSession(
        interview_session_id=interview_session_id,
        candidate_id=candidate_id,
        status='active'
    )
    db.session.add(session)
    db.session.commit()
    return session

def log_violation(session_id, violation_type, message, severity='medium', frame_data=None):
    """Log a proctoring violation"""
    violation = ProctoringViolation(
        session_id=session_id,
        violation_type=violation_type,
        violation_message=message,
        severity=severity,
        frame_data=json.dumps(frame_data) if frame_data else None,
        warning_issued=True
    )
    db.session.add(violation)
    
    # Update session violation count
    session = ProctoringSession.query.get(session_id)
    if session:
        session.total_violations += 1
        session.warning_count += 1
        session.updated_at = datetime.utcnow()
    
    db.session.commit()
    return violation

def log_frame_analysis(session_id, analysis_results):
    """Log frame analysis results"""
    frame_log = ProctoringFrameLog(
        session_id=session_id,
        face_count=analysis_results.get('face_count', 0),
        gaze_direction=analysis_results.get('gaze_direction'),
        blink_status=analysis_results.get('blink_status'),
        mouth_status=analysis_results.get('mouth_status'),
        head_pose=analysis_results.get('head_pose'),
        objects_detected=json.dumps(analysis_results.get('objects', [])),
        suspicious_objects=json.dumps(analysis_results.get('suspicious_objects', [])),
        processing_time=analysis_results.get('processing_time', 0)
    )
    db.session.add(frame_log)
    db.session.commit()
    return frame_log

def create_alert(session_id, alert_type, message, priority='medium', alert_data=None):
    """Create a proctoring alert"""
    alert = ProctoringAlert(
        session_id=session_id,
        alert_type=alert_type,
        alert_message=message,
        priority=priority,
        alert_data=json.dumps(alert_data) if alert_data else None
    )
    db.session.add(alert)
    db.session.commit()
    return alert

def complete_proctoring_session(session_id, summary_data=None):
    """Complete a proctoring session"""
    session = ProctoringSession.query.get(session_id)
    if session:
        session.status = 'completed'
        session.end_time = datetime.utcnow()
        if session.start_time:
            session.duration = int((session.end_time - session.start_time).total_seconds())
        
        if summary_data:
            session.session_summary = json.dumps(summary_data)
        
        session.updated_at = datetime.utcnow()
        db.session.commit()
    
    return session