"""Duration-Based Interview Quality Management"""

from app.system_lock import register_feature, execute_hook

class DurationManager:
    
    @staticmethod
    def calculate_phase_durations(total_minutes):
        """Calculate interview phase durations"""
        return {
            'warmup': int(total_minutes * 0.15),
            'technical': int(total_minutes * 0.50),
            'behavioral': int(total_minutes * 0.25),
            'closing': int(total_minutes * 0.10)
        }
    
    @staticmethod
    def get_difficulty_for_phase(elapsed_minutes, total_minutes):
        """Determine question difficulty based on interview progress"""
        progress = elapsed_minutes / total_minutes
        
        if progress < 0.25:
            return 'easy'
        elif progress < 0.75:
            return 'medium'
        else:
            return 'hard'
    
    @staticmethod
    def calculate_optimal_questions(duration_minutes):
        """Calculate optimal number of questions for duration"""
        if duration_minutes <= 10:
            return 5
        elif duration_minutes <= 20:
            return 8
        elif duration_minutes <= 30:
            return 12
        else:
            return 15
    
    @staticmethod
    def get_time_allocation(duration_minutes, question_count):
        """Get time allocation per question"""
        return {
            'per_question': duration_minutes / question_count,
            'buffer_time': duration_minutes * 0.1,
            'active_time': duration_minutes * 0.9
        }
    
    @staticmethod
    def should_adjust_pace(elapsed_minutes, questions_asked, total_questions, total_minutes):
        """Determine if interview pace needs adjustment"""
        expected_progress = questions_asked / total_questions
        time_progress = elapsed_minutes / total_minutes
        
        if time_progress > expected_progress + 0.2:
            return 'speed_up'
        elif time_progress < expected_progress - 0.2:
            return 'slow_down'
        else:
            return 'on_track'

register_feature('duration_manager', DurationManager)
