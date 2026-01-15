#!/usr/bin/env python3
"""
Response Evaluator - Evaluates response quality and generates scores
"""

class ResponseEvaluator:
    def __init__(self):
        pass
    
    def evaluate_single_response(self, question: str, response: str, response_time: int = 120) -> dict:
        """Evaluate a single response and return quality metrics"""
        
        if not response or len(response.strip()) < 5:
            return {
                "quality_score": 10,
                "word_count": 0,
                "completeness": 0,
                "relevance": 0,
                "detail_level": 0
            }
        
        # Basic metrics
        word_count = len(response.split())
        char_count = len(response.strip())
        
        # Quality indicators
        quality_words = [
            "experience", "project", "work", "learn", "skill", "challenge",
            "problem", "solution", "team", "goal", "achieve", "develop",
            "create", "manage", "lead", "collaborate", "implement", "design"
        ]
        
        poor_indicators = [
            "don't know", "no idea", "nothing", "don't have", "don't understand",
            "not sure", "maybe", "i think", "probably"
        ]
        
        response_lower = response.lower()
        
        # Count quality and poor indicators
        quality_count = sum(1 for word in quality_words if word in response_lower)
        poor_count = sum(1 for indicator in poor_indicators if indicator in response_lower)
        
        # Calculate scores
        completeness = min(100, (word_count / 30) * 100)  # 30 words = complete
        relevance = max(0, (quality_count * 20) - (poor_count * 15))
        detail_level = min(100, (char_count / 200) * 100)  # 200 chars = detailed
        
        # Overall quality score
        if poor_count > quality_count and word_count < 10:
            quality_score = max(10, 20 - (poor_count * 5))
        else:
            quality_score = min(100, (completeness * 0.4 + relevance * 0.4 + detail_level * 0.2))
        
        return {
            "quality_score": int(quality_score),
            "word_count": word_count,
            "completeness": int(completeness),
            "relevance": int(relevance),
            "detail_level": int(detail_level),
            "response_time": response_time
        }
    
    def calculate_final_scores(self, all_evaluations: list, total_duration: int) -> dict:
        """Calculate final interview scores based on all responses"""
        
        if not all_evaluations:
            return self._get_minimum_scores()
        
        # Calculate averages
        avg_quality = sum(e["quality_score"] for e in all_evaluations) / len(all_evaluations)
        avg_completeness = sum(e["completeness"] for e in all_evaluations) / len(all_evaluations)
        avg_relevance = sum(e["relevance"] for e in all_evaluations) / len(all_evaluations)
        avg_detail = sum(e["detail_level"] for e in all_evaluations) / len(all_evaluations)
        
        # Calculate component scores
        communication_score = min(100, (avg_completeness + avg_detail) / 2)
        technical_score = max(20, avg_relevance)
        confidence_score = min(100, avg_quality)
        problem_solving_score = max(15, avg_quality * 0.8)
        
        # Time factor
        time_factor = 1.0
        if total_duration < 300:  # Less than 5 minutes
            time_factor = 0.7
        elif total_duration < 480:  # Less than 8 minutes
            time_factor = 0.85
        
        # Overall score
        overall_score = int(avg_quality * time_factor)
        
        return {
            "overall_score": max(15, min(100, overall_score)),
            "technical_score": max(20, min(100, int(technical_score))),
            "communication_score": max(25, min(100, int(communication_score))),
            "confidence_score": max(20, min(100, int(confidence_score))),
            "problem_solving_score": max(15, min(100, int(problem_solving_score))),
            "leadership_score": max(10, min(100, int(avg_quality * 0.6))),
            "adaptability_score": max(20, min(100, int(avg_quality * 0.7))),
            "total_responses": len(all_evaluations),
            "average_quality": int(avg_quality),
            "interview_duration": total_duration
        }
    
    def _get_minimum_scores(self) -> dict:
        """Return minimum scores for very poor performance"""
        return {
            "overall_score": 15,
            "technical_score": 20,
            "communication_score": 25,
            "confidence_score": 20,
            "problem_solving_score": 15,
            "leadership_score": 10,
            "adaptability_score": 20,
            "total_responses": 0,
            "average_quality": 15,
            "interview_duration": 0
        }
    
    def generate_feedback(self, scores: dict, responses: list) -> dict:
        """Generate detailed feedback based on scores and responses"""
        
        overall = scores["overall_score"]
        
        if overall >= 75:
            performance_level = "Excellent"
            strengths = ["Strong communication skills", "Detailed responses", "Good technical knowledge"]
            weaknesses = ["Continue developing leadership skills"]
            recommendations = ["Prepare for advanced technical questions", "Practice leadership scenarios"]
        elif overall >= 55:
            performance_level = "Good"
            strengths = ["Adequate communication", "Shows potential"]
            weaknesses = ["Provide more detailed examples", "Improve technical explanations"]
            recommendations = ["Practice STAR method responses", "Prepare specific examples"]
        elif overall >= 35:
            performance_level = "Needs Improvement"
            strengths = ["Participated in interview", "Shows willingness to learn"]
            weaknesses = ["Responses lack detail", "Limited examples provided", "Needs more preparation"]
            recommendations = ["Practice interview questions", "Prepare detailed examples", "Study relevant technical concepts"]
        else:
            performance_level = "Poor"
            strengths = ["Attended the interview"]
            weaknesses = ["Very brief responses", "Lack of specific examples", "Insufficient preparation"]
            recommendations = ["Extensive interview practice needed", "Prepare detailed personal examples", "Research the role and company thoroughly"]
        
        return {
            "performance_level": performance_level,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_areas": weaknesses,
            "recommendations": recommendations,
            "detailed_analysis": {
                "communication": f"Communication score: {scores['communication_score']}/100",
                "technical_skills": f"Technical score: {scores['technical_score']}/100", 
                "problem_solving": f"Problem-solving score: {scores['problem_solving_score']}/100",
                "overall_assessment": f"Overall performance: {performance_level} ({overall}/100)"
            },
            "summary": f"Interview completed with {performance_level.lower()} performance. Score: {overall}/100. {len(responses)} questions answered.",
            "next_steps": recommendations[0] if recommendations else "Continue practicing interview skills"
        }