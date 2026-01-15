"""Training & Mock Interview Module"""

from app.system_lock import register_feature, execute_hook

class TrainingSystem:
    
    learning_paths = {
        'beginner': ['basics', 'fundamentals', 'simple_projects'],
        'intermediate': ['advanced_concepts', 'design_patterns', 'real_projects'],
        'advanced': ['system_design', 'architecture', 'optimization']
    }
    
    @staticmethod
    def get_learning_path(skill_level):
        """Get personalized learning path"""
        return TrainingSystem.learning_paths.get(skill_level, TrainingSystem.learning_paths['beginner'])
    
    @staticmethod
    def generate_practice_questions(topic, difficulty):
        """Generate practice questions for topic"""
        questions = {
            'easy': [f"Explain basic concepts of {topic}", f"What is {topic}?"],
            'medium': [f"How would you implement {topic}?", f"Compare different approaches to {topic}"],
            'hard': [f"Design a system using {topic}", f"Optimize {topic} for scale"]
        }
        return questions.get(difficulty, questions['easy'])
    
    @staticmethod
    def provide_learning_feedback(answer, expected_keywords):
        """Provide educational feedback"""
        answer_lower = answer.lower()
        matched = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
        coverage = matched / len(expected_keywords) if expected_keywords else 0
        
        if coverage >= 0.8:
            return "Excellent understanding! You covered all key concepts."
        elif coverage >= 0.5:
            return f"Good effort. Consider exploring: {', '.join([k for k in expected_keywords if k.lower() not in answer_lower])}"
        else:
            return f"Needs improvement. Focus on: {', '.join(expected_keywords)}"
    
    @staticmethod
    def track_progress(student_id, topic, score):
        """Track student learning progress"""
        return {
            'student_id': student_id,
            'topic': topic,
            'score': score,
            'next_recommendation': 'Continue practicing' if score < 70 else 'Move to next topic'
        }

register_feature('training_system', TrainingSystem)
