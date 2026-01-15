"""Assessment Monitoring & Rating System"""

from app.system_lock import register_feature, execute_hook
from datetime import datetime

class AssessmentMonitor:
    
    monitoring_data = {}
    
    @staticmethod
    def start_monitoring(session_id):
        """Initialize monitoring for session"""
        AssessmentMonitor.monitoring_data[session_id] = {
            'start_time': datetime.now(),
            'responses': [],
            'response_times': [],
            'quality_scores': []
        }
    
    @staticmethod
    def track_response(session_id, response_text, time_taken):
        """Track individual response metrics"""
        if session_id not in AssessmentMonitor.monitoring_data:
            AssessmentMonitor.start_monitoring(session_id)
        
        data = AssessmentMonitor.monitoring_data[session_id]
        data['responses'].append(response_text)
        data['response_times'].append(time_taken)
        
        quality = len(response_text.split()) / 50.0
        data['quality_scores'].append(min(1.0, quality))
    
    @staticmethod
    def calculate_metrics(session_id):
        """Calculate performance metrics"""
        if session_id not in AssessmentMonitor.monitoring_data:
            return {}
        
        data = AssessmentMonitor.monitoring_data[session_id]
        
        return {
            'total_responses': len(data['responses']),
            'avg_response_time': sum(data['response_times']) / len(data['response_times']) if data['response_times'] else 0,
            'avg_quality': sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0,
            'consistency': 1.0 - (max(data['quality_scores']) - min(data['quality_scores'])) if data['quality_scores'] else 0
        }
    
    @staticmethod
    def generate_rating(session_id):
        """Generate final rating"""
        metrics = AssessmentMonitor.calculate_metrics(session_id)
        
        rating = (
            metrics.get('avg_quality', 0) * 0.5 +
            metrics.get('consistency', 0) * 0.3 +
            (1.0 if metrics.get('total_responses', 0) >= 5 else 0.5) * 0.2
        )
        
        return {
            'rating': round(rating * 100, 2),
            'metrics': metrics
        }

register_feature('assessment_monitor', AssessmentMonitor)
