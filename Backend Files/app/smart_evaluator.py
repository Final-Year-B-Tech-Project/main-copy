#!/usr/bin/env python3
"""
Smart Evaluator - Realistic scoring based on actual response quality
"""

class SmartEvaluator:
    def __init__(self):
        pass
    
    def evaluate_interview(self, responses: list) -> dict:
        """Evaluate entire interview and return realistic scores"""
        
        if not responses:
            return self._get_no_response_scores()
        
        total_score = 0
        response_qualities = []
        
        for response in responses:
            answer = response.get('answer', '')
            quality = self._evaluate_single_response(answer)
            response_qualities.append(quality)
            total_score += quality
        
        # Calculate average
        avg_quality = total_score / len(responses) if responses else 0
        
        # Determine performance level
        if avg_quality >= 80:
            performance = "Excellent"
        elif avg_quality >= 60:
            performance = "Good"
        elif avg_quality >= 40:
            performance = "Fair"
        elif avg_quality >= 20:
            performance = "Poor"
        else:
            performance = "Very Poor"
        
        # Calculate component scores
        overall_score = int(avg_quality)
        technical_score = max(15, int(avg_quality * 0.9))
        communication_score = max(20, int(avg_quality * 1.1))
        confidence_score = max(15, int(avg_quality * 0.8))
        
        return {
            "overall_score": overall_score,
            "technical_score": technical_score,
            "communication_score": communication_score,
            "confidence_score": confidence_score,
            "problem_solving_score": max(15, int(avg_quality * 0.85)),
            "leadership_score": max(10, int(avg_quality * 0.7)),
            "adaptability_score": max(15, int(avg_quality * 0.8)),
            "performance_level": performance,
            "total_responses": len(responses),
            "average_quality": int(avg_quality),
            "strengths": self._get_strengths(avg_quality, responses),
            "weaknesses": self._get_weaknesses(avg_quality, responses),
            "recommendations": self._get_recommendations(avg_quality),
            "summary": f"Interview completed with {performance.lower()} performance. Overall score: {overall_score}/100 based on {len(responses)} responses."
        }
    
    def _evaluate_single_response(self, answer: str) -> int:
        """Evaluate single response quality (0-100)"""
        
        if not answer or len(answer.strip()) < 3:
            return 5
        
        answer_lower = answer.lower().strip()
        word_count = len(answer.split())
        
        # Very negative responses
        negative_phrases = [
            "i don't know", "don't know", "no idea", "nothing", 
            "i don't have", "don't have", "never", "illiterate", 
            "dumb", "stupid", "no experience", "no skills",
            "i don't understand", "don't understand"
        ]
        
        negative_count = sum(1 for phrase in negative_phrases if phrase in answer_lower)
        
        # If response is mostly negative
        if negative_count > 0 and word_count < 10:
            return max(5, 15 - (negative_count * 3))
        
        # Positive indicators
        positive_words = [
            "student", "study", "learn", "project", "work", "experience",
            "skill", "programming", "computer", "engineering", "college",
            "university", "course", "subject", "interested", "like", "enjoy"
        ]
        
        positive_count = sum(1 for word in positive_words if word in answer_lower)
        
        # Base score calculation
        length_score = min(40, word_count * 2)  # Up to 40 points for length
        content_score = min(40, positive_count * 8)  # Up to 40 points for content
        coherence_score = 20 if word_count >= 5 else 10  # Basic coherence
        
        total_score = length_score + content_score + coherence_score
        
        # Penalty for excessive negativity
        if negative_count > positive_count:
            total_score = max(10, total_score - (negative_count * 10))
        
        return min(100, max(5, int(total_score)))
    
    def _get_no_response_scores(self) -> dict:
        """Scores for no responses"""
        return {
            "overall_score": 5,
            "technical_score": 5,
            "communication_score": 5,
            "confidence_score": 5,
            "problem_solving_score": 5,
            "leadership_score": 5,
            "adaptability_score": 5,
            "performance_level": "No Response",
            "total_responses": 0,
            "average_quality": 5,
            "strengths": [],
            "weaknesses": ["Did not participate in interview"],
            "recommendations": ["Complete the interview process"],
            "summary": "Interview not completed - no responses provided."
        }
    
    def _get_strengths(self, avg_quality: float, responses: list) -> list:
        """Get strengths based on performance"""
        strengths = []
        
        if avg_quality >= 70:
            strengths.extend(["Good communication skills", "Provides detailed responses"])
        elif avg_quality >= 50:
            strengths.extend(["Shows engagement", "Willing to participate"])
        elif avg_quality >= 30:
            strengths.extend(["Participated in interview"])
        
        # Check for specific positive content
        all_text = " ".join([r.get('answer', '') for r in responses]).lower()
        
        if any(word in all_text for word in ['student', 'study', 'learn']):
            strengths.append("Shows learning orientation")
        
        if any(word in all_text for word in ['programming', 'computer', 'technical']):
            strengths.append("Has technical awareness")
        
        return strengths if strengths else ["Attended the interview"]
    
    def _get_weaknesses(self, avg_quality: float, responses: list) -> list:
        """Get weaknesses based on performance"""
        weaknesses = []
        
        if avg_quality < 30:
            weaknesses.extend([
                "Very brief responses", 
                "Lacks specific examples", 
                "Shows limited engagement"
            ])
        elif avg_quality < 50:
            weaknesses.extend([
                "Responses could be more detailed",
                "Needs more specific examples"
            ])
        elif avg_quality < 70:
            weaknesses.extend([
                "Could provide more depth in responses"
            ])
        
        # Check for negative patterns
        all_text = " ".join([r.get('answer', '') for r in responses]).lower()
        
        if "don't know" in all_text or "don't have" in all_text:
            weaknesses.append("Frequently indicates lack of knowledge/experience")
        
        return weaknesses if weaknesses else ["Minor areas for improvement"]
    
    def _get_recommendations(self, avg_quality: float) -> list:
        """Get recommendations based on performance"""
        if avg_quality >= 70:
            return [
                "Continue developing technical skills",
                "Prepare for advanced interview questions"
            ]
        elif avg_quality >= 50:
            return [
                "Practice providing more detailed responses",
                "Prepare specific examples from experience",
                "Work on confidence in communication"
            ]
        elif avg_quality >= 30:
            return [
                "Practice basic interview skills",
                "Prepare responses to common questions",
                "Build confidence through mock interviews"
            ]
        else:
            return [
                "Extensive interview preparation needed",
                "Practice basic communication skills",
                "Prepare personal examples and experiences",
                "Consider interview coaching or training"
            ]