"""Security & Anti-Cheating Measures"""

from app.system_lock import register_feature, execute_hook
from datetime import datetime

class SecuritySystem:
    
    violations = {}
    
    @staticmethod
    def init_session(session_id):
        """Initialize security tracking for session"""
        SecuritySystem.violations[session_id] = {
            'tab_switches': 0,
            'fullscreen_exits': 0,
            'suspicious_activity': [],
            'start_time': datetime.now()
        }
    
    @staticmethod
    def log_tab_switch(session_id):
        """Log tab switch violation"""
        if session_id not in SecuritySystem.violations:
            SecuritySystem.init_session(session_id)
        
        SecuritySystem.violations[session_id]['tab_switches'] += 1
        SecuritySystem.violations[session_id]['suspicious_activity'].append({
            'type': 'tab_switch',
            'timestamp': datetime.now()
        })
    
    @staticmethod
    def log_fullscreen_exit(session_id):
        """Log fullscreen exit violation"""
        if session_id not in SecuritySystem.violations:
            SecuritySystem.init_session(session_id)
        
        SecuritySystem.violations[session_id]['fullscreen_exits'] += 1
        SecuritySystem.violations[session_id]['suspicious_activity'].append({
            'type': 'fullscreen_exit',
            'timestamp': datetime.now()
        })
    
    @staticmethod
    def check_integrity(session_id):
        """Check interview integrity"""
        if session_id not in SecuritySystem.violations:
            return {'integrity': 'clean', 'violations': 0}
        
        data = SecuritySystem.violations[session_id]
        total_violations = data['tab_switches'] + data['fullscreen_exits']
        
        if total_violations == 0:
            integrity = 'clean'
        elif total_violations <= 2:
            integrity = 'minor_violations'
        elif total_violations <= 5:
            integrity = 'moderate_violations'
        else:
            integrity = 'severe_violations'
        
        return {
            'integrity': integrity,
            'violations': total_violations,
            'tab_switches': data['tab_switches'],
            'fullscreen_exits': data['fullscreen_exits'],
            'details': data['suspicious_activity']
        }
    
    @staticmethod
    def is_interview_valid(session_id):
        """Determine if interview is valid based on violations"""
        integrity = SecuritySystem.check_integrity(session_id)
        return integrity['violations'] < 5

register_feature('security_system', SecuritySystem)
