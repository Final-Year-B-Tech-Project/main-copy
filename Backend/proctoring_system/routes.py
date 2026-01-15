"""
Proctoring Routes for Interview System
Handles video streaming, frame processing, and violation tracking
"""

from flask import Blueprint, request, jsonify, Response, session, render_template
from flask_login import login_required, current_user
# import cv2
import base64
import numpy as np
import json
from datetime import datetime
import threading
import queue
import logging

# from .core import ProctoringSuite
from .simple_core import SimpleProctoringSystem
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import InterviewSession, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

proctoring_bp = Blueprint('proctoring', __name__, url_prefix='/api/proctoring')

# Global proctoring instances (one per session)
proctoring_sessions = {}
session_lock = threading.Lock()

# Use simple proctoring system for better reliability
USE_SIMPLE_PROCTORING = True

@proctoring_bp.route('/start', methods=['POST'])
@login_required
def start_proctoring():
    """Start a new proctoring session"""
    try:
        data = request.get_json()
        interview_session_id = data.get('interview_session_id')
        
        if not interview_session_id:
            return jsonify({'error': 'Interview session ID required'}), 400
        
        # Check if interview session exists
        interview_session = InterviewSession.query.get(interview_session_id)
        if not interview_session:
            return jsonify({'error': 'Interview session not found'}), 404
        
        # Check if user owns this session
        if interview_session.candidate_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        session_key = f"{current_user.id}_{interview_session_id}"
        
        with session_lock:
            # Stop existing session if any
            if session_key in proctoring_sessions:
                proctoring_sessions[session_key] = None
            
            # Create new proctoring instance
            if USE_SIMPLE_PROCTORING:
                proctoring_suite = SimpleProctoringSystem()
                logger.info("Using Simple Proctoring System")
            else:
                from .core import ProctoringSuite
                proctoring_suite = ProctoringSuite()
                logger.info("Using Full Proctoring Suite")
            
            proctoring_sessions[session_key] = proctoring_suite
        
        # Update interview session status
        interview_session.status = 'in_progress'
        interview_session.start_time = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Started proctoring session for user {current_user.id}, interview {interview_session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Proctoring session started',
            'session_key': session_key
        })
        
    except Exception as e:
        logger.error(f"Error starting proctoring session: {e}")
        return jsonify({'error': 'Failed to start proctoring session'}), 500

@proctoring_bp.route('/stop', methods=['POST'])
@login_required
def stop_proctoring():
    """Stop the proctoring session"""
    try:
        data = request.get_json()
        interview_session_id = data.get('interview_session_id')
        
        if not interview_session_id:
            return jsonify({'error': 'Interview session ID required'}), 400
        
        session_key = f"{current_user.id}_{interview_session_id}"
        
        with session_lock:
            if session_key in proctoring_sessions:
                proctoring_suite = proctoring_sessions[session_key]
                if proctoring_suite:
                    # Get session summary
                    summary = proctoring_suite.get_session_summary()
                    
                    # Update interview session
                    interview_session = InterviewSession.query.get(interview_session_id)
                    if interview_session:
                        interview_session.status = 'completed'
                        interview_session.end_time = datetime.utcnow()
                        
                        # Store proctoring results in notes
                        existing_notes = json.loads(interview_session.notes or '{}')
                        existing_notes['proctoring_summary'] = summary
                        interview_session.notes = json.dumps(existing_notes)
                        
                        db.session.commit()
                    
                    # Remove from active sessions
                    del proctoring_sessions[session_key]
                    
                    logger.info(f"Stopped proctoring session for user {current_user.id}, interview {interview_session_id}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Proctoring session stopped',
                        'summary': summary
                    })
        
        return jsonify({'error': 'No active proctoring session found'}), 404
        
    except Exception as e:
        logger.error(f"Error stopping proctoring session: {e}")
        return jsonify({'error': 'Failed to stop proctoring session'}), 500

@proctoring_bp.route('/process_frame', methods=['POST'])
@login_required
def process_frame():
    """Process a video frame for proctoring analysis"""
    try:
        data = request.get_json()
        interview_session_id = data.get('interview_session_id')
        frame_data = data.get('frame')
        
        if not interview_session_id or not frame_data:
            return jsonify({'error': 'Interview session ID and frame data required'}), 400
        
        session_key = f"{current_user.id}_{interview_session_id}"
        
        with session_lock:
            if session_key not in proctoring_sessions:
                return jsonify({'error': 'No active proctoring session'}), 404
            
            proctoring_suite = proctoring_sessions[session_key]
            if not proctoring_suite:
                return jsonify({'error': 'Proctoring session not initialized'}), 500
        
        # Store frame analysis in database
        try:
            from .models import log_frame_analysis
            log_frame_analysis(interview_session_id, {'processing_time': 0})
        except Exception as e:
            logger.error(f"Database logging error: {e}")
        
        # Decode base64 frame
        try:
            # Remove data URL prefix if present
            if ',' in frame_data:
                frame_data = frame_data.split(',')[1]
            
            # Decode base64
            frame_bytes = base64.b64decode(frame_data)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            import cv2
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                return jsonify({'error': 'Invalid frame data'}), 400
            
        except Exception as e:
            logger.error(f"Error decoding frame: {e}")
            return jsonify({'error': 'Failed to decode frame'}), 400
        
        # Process frame
        results = proctoring_suite.process_frame(frame)
        
        # Log results for debugging
        logger.info(f"Frame processing results: {results}")
        
        # Remove the annotated frame from results (too large for JSON)
        if 'annotated_frame' in results:
            del results['annotated_frame']
        
        # Return results
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        return jsonify({'error': 'Failed to process frame'}), 500

@proctoring_bp.route('/status', methods=['GET'])
@login_required
def get_status():
    """Get current proctoring session status"""
    try:
        interview_session_id = request.args.get('interview_session_id')
        
        if not interview_session_id:
            return jsonify({'error': 'Interview session ID required'}), 400
        
        session_key = f"{current_user.id}_{interview_session_id}"
        
        with session_lock:
            is_active = session_key in proctoring_sessions and proctoring_sessions[session_key] is not None
            
            if is_active:
                proctoring_suite = proctoring_sessions[session_key]
                summary = proctoring_suite.get_session_summary()
                
                return jsonify({
                    'active': True,
                    'summary': summary
                })
            else:
                return jsonify({
                    'active': False
                })
        
    except Exception as e:
        logger.error(f"Error getting proctoring status: {e}")
        return jsonify({'error': 'Failed to get status'}), 500

@proctoring_bp.route('/violations', methods=['GET'])
@login_required
def get_violations():
    """Get violations for current session"""
    try:
        interview_session_id = request.args.get('interview_session_id')
        
        if not interview_session_id:
            return jsonify({'error': 'Interview session ID required'}), 400
        
        session_key = f"{current_user.id}_{interview_session_id}"
        
        with session_lock:
            if session_key in proctoring_sessions and proctoring_sessions[session_key]:
                proctoring_suite = proctoring_sessions[session_key]
                violations = proctoring_suite.violations
                
                return jsonify({
                    'success': True,
                    'violations': violations,
                    'total_violations': len(violations)
                })
        
        return jsonify({
            'success': True,
            'violations': [],
            'total_violations': 0
        })
        
    except Exception as e:
        logger.error(f"Error getting violations: {e}")
        return jsonify({'error': 'Failed to get violations'}), 500

@proctoring_bp.route('/test', methods=['GET'])
def test_proctoring():
    """Test endpoint to verify proctoring system"""
    try:
        # Test both systems
        if USE_SIMPLE_PROCTORING:
            proctoring_suite = SimpleProctoringSystem()
            system_type = "Simple Proctoring System"
        else:
            from .core import ProctoringSuite
            proctoring_suite = ProctoringSuite()
            system_type = "Full Proctoring Suite"
        
        # Test with dummy frame
        import numpy as np
        import cv2
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_frame, "TEST", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        results = proctoring_suite.process_frame(test_frame)
        
        return jsonify({
            'success': True,
            'message': f'{system_type} is working',
            'system_type': system_type,
            'test_results': results,
            'models_loaded': {
                'face_detection': hasattr(proctoring_suite, 'face_cascade'),
                'simple_system': USE_SIMPLE_PROCTORING
            }
        })
        
    except Exception as e:
        logger.error(f"Proctoring test failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proctoring_bp.route('/test_page', methods=['GET'])
def test_page():
    """Render proctoring test page"""
    return render_template('proctoring_system/proctoring_test.html')

@proctoring_bp.route('/dashboard', methods=['GET'])
@login_required
def proctoring_dashboard():
    """Proctoring dashboard for HR and admins"""
    if current_user.user_type not in ['hr', 'admin']:
        flash('Access denied. HR/Admin only.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('proctoring_system/dashboard.html')

@proctoring_bp.route('/dashboard/sessions', methods=['GET'])
@login_required
def get_dashboard_sessions():
    """Get active sessions for dashboard"""
    try:
        from app.models import InterviewSession, User
        
        # Get active interview sessions
        active_sessions = InterviewSession.query.filter_by(status='in_progress').all()
        
        sessions_data = []
        for session in active_sessions:
            session_data = {
                'id': session.id,
                'candidate_name': session.candidate.full_name,
                'candidate_email': session.candidate.email,
                'job_role': session.notes.split('Job Role: ')[1].split('\n')[0] if session.notes and 'Job Role:' in session.notes else 'Practice',
                'status': 'active',
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'duration': int((datetime.utcnow() - session.start_time).total_seconds()) if session.start_time else 0,
                'violation_count': 0,
                'recent_violations': []
            }
            sessions_data.append(session_data)
        
        statistics = {
            'active_sessions': len(sessions_data),
            'total_violations': 0,
            'high_alerts': 0,
            'completed_today': InterviewSession.query.filter(
                InterviewSession.status == 'completed',
                InterviewSession.end_time >= datetime.utcnow().replace(hour=0, minute=0, second=0)
            ).count()
        }
        
        return jsonify({
            'success': True,
            'sessions': sessions_data,
            'statistics': statistics
        })
        
    except Exception as e:
        logger.error(f"Dashboard sessions error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@proctoring_bp.route('/dashboard/live', methods=['GET'])
@login_required
def get_live_updates():
    """Get live updates for dashboard"""
    try:
        # This would typically get real-time data from active proctoring sessions
        return jsonify({
            'success': True,
            'sessions': [],
            'alerts': [],
            'statistics': {
                'active_sessions': 0,
                'total_violations': 0,
                'high_alerts': 0,
                'completed_today': 0
            }
        })
        
    except Exception as e:
        logger.error(f"Live updates error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Cleanup function to remove inactive sessions
def cleanup_inactive_sessions():
    """Remove inactive proctoring sessions"""
    with session_lock:
        inactive_keys = []
        for key, suite in proctoring_sessions.items():
            if suite is None:
                inactive_keys.append(key)
        
        for key in inactive_keys:
            del proctoring_sessions[key]

# Register cleanup to run periodically (you might want to use a scheduler)
import atexit
atexit.register(cleanup_inactive_sessions)