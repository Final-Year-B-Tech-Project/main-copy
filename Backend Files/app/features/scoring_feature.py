"""
Authentic Scoring Feature
Raw, honest evaluation with NO base points or soft penalties
Real is real - no artificial inflation
"""

class AuthenticScoring:
    
    # Evaluation weights
    WEIGHTS = {
        'technical': 0.35,
        'communication': 0.25,
        'problem_solving': 0.20,
        'experience': 0.20
    }
    
    # Performance thresholds
    THRESHOLDS = {
        'excellent': 85,
        'good': 70,
        'average': 55,
        'below_average': 40,
        'poor': 0
    }
    
    @staticmethod
    def calculate_technical_score(indicators, avg_length):
        """Raw technical score - NO BASE POINTS"""
        score = min(100, indicators * 12)
        if avg_length < 15:
            score *= 0.7
        return int(score)
    
    @staticmethod
    def calculate_communication_score(quality, examples, vague_count, detailed_count):
        """Raw communication score - NO BASE POINTS"""
        score = min(100, quality * 10 + examples * 8)
        if vague_count > detailed_count:
            score *= 0.6
        return int(score)
    
    @staticmethod
    def calculate_problem_solving_score(evidence, avg_length):
        """Raw problem-solving score - NO BASE POINTS"""
        score = min(100, evidence * 15)
        if avg_length < 20:
            score *= 0.7
        return int(score)
    
    @staticmethod
    def calculate_experience_score(indicators):
        """Raw experience score - NO BASE POINTS"""
        return min(100, int(indicators * 12))
    
    @staticmethod
    def calculate_overall_score(tech, comm, prob, exp):
        """Weighted overall score - RAW CALCULATION"""
        return int(
            tech * AuthenticScoring.WEIGHTS['technical'] +
            comm * AuthenticScoring.WEIGHTS['communication'] +
            prob * AuthenticScoring.WEIGHTS['problem_solving'] +
            exp * AuthenticScoring.WEIGHTS['experience']
        )
    
    @staticmethod
    def get_performance_level(score):
        """Get performance level based on score"""
        if score >= AuthenticScoring.THRESHOLDS['excellent']:
            return "Excellent"
        elif score >= AuthenticScoring.THRESHOLDS['good']:
            return "Good"
        elif score >= AuthenticScoring.THRESHOLDS['average']:
            return "Average"
        elif score >= AuthenticScoring.THRESHOLDS['below_average']:
            return "Below Average"
        else:
            return "Poor"
