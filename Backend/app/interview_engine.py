#!/usr/bin/env python3
"""
Professional Interview Engine - Proper Question Flow and Evaluation
"""

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

class InterviewEngine:
    def __init__(self):
        self.min_duration = 8 * 60  # 8 minutes
        self.max_duration = 20 * 60  # 20 minutes
        self.target_questions = 8
        self.current_question_index = 0
        self.start_time = None
        
    def generate_adaptive_question(self, job_role: str, previous_responses: List[Dict], question_index: int) -> Dict:
        """Generate next question based on previous responses and interview flow"""
        
        # Professional question flow based on interview best practices
        question_flow = {
            0: self._get_opening_question(job_role),
            1: self._get_background_question(previous_responses),
            2: self._get_technical_question(job_role, previous_responses),
            3: self._get_experience_question(previous_responses),
            4: self._get_problem_solving_question(job_role),
            5: self._get_behavioral_question(previous_responses),
            6: self._get_situational_question(job_role),
            7: self._get_closing_question()
        }
        
        if question_index < len(question_flow):
            return question_flow[question_index]
        else:
            return self._get_closing_question()
    
    def _get_opening_question(self, job_role: str) -> Dict:
        return {
            "id": 1,
            "type": "introduction",
            "question": f"Good day! Welcome to your interview for the {job_role} position. Please tell me about yourself, your background, and what interests you about this role.",
            "category": "introduction",
            "difficulty": "easy",
            "time_limit": 120,
            "expected_duration": 90
        }
    
    def _get_background_question(self, previous_responses: List[Dict]) -> Dict:
        # Analyze previous response to ask relevant follow-up
        last_response = previous_responses[-1] if previous_responses else {}
        answer = last_response.get('answer', '').lower()
        
        if 'student' in answer or 'graduate' in answer:
            question = "As a recent graduate, what projects or coursework have you completed that demonstrate your practical skills?"
        elif 'experience' in answer or 'worked' in answer:
            question = "Tell me about your most significant professional achievement and what you learned from it."
        else:
            question = "What specific skills and experiences make you a strong candidate for this position?"
            
        return {
            "id": 2,
            "type": "background",
            "question": question,
            "category": "experience",
            "difficulty": "medium",
            "time_limit": 150,
            "expected_duration": 120
        }
    
    def _get_technical_question(self, job_role: str, previous_responses: List[Dict]) -> Dict:
        # Technical questions based on job role
        tech_questions = {
            "software developer": "Explain the difference between object-oriented and functional programming. Which approach do you prefer and why?",
            "data analyst": "How would you approach analyzing a large dataset with missing values? Walk me through your process.",
            "web developer": "Describe how you would optimize a slow-loading website. What tools and techniques would you use?",
            "default": "Describe a technical challenge you've faced and how you approached solving it."
        }
        
        role_key = next((key for key in tech_questions.keys() if key in job_role.lower()), "default")
        
        return {
            "id": 3,
            "type": "technical",
            "question": tech_questions[role_key],
            "category": "technical_skills",
            "difficulty": "medium",
            "time_limit": 180,
            "expected_duration": 150
        }
    
    def _get_experience_question(self, previous_responses: List[Dict]) -> Dict:
        return {
            "id": 4,
            "type": "experience",
            "question": "Describe a time when you had to learn something new quickly. How did you approach it and what was the outcome?",
            "category": "learning_ability",
            "difficulty": "medium",
            "time_limit": 150,
            "expected_duration": 120
        }
    
    def _get_problem_solving_question(self, job_role: str) -> Dict:
        return {
            "id": 5,
            "type": "problem_solving",
            "question": "Tell me about a complex problem you solved. Walk me through your thought process from identifying the issue to implementing the solution.",
            "category": "problem_solving",
            "difficulty": "hard",
            "time_limit": 200,
            "expected_duration": 180
        }
    
    def _get_behavioral_question(self, previous_responses: List[Dict]) -> Dict:
        return {
            "id": 6,
            "type": "behavioral",
            "question": "Describe a situation where you had to work with a difficult team member or handle conflict. How did you manage it?",
            "category": "teamwork",
            "difficulty": "medium",
            "time_limit": 150,
            "expected_duration": 120
        }
    
    def _get_situational_question(self, job_role: str) -> Dict:
        return {
            "id": 7,
            "type": "situational",
            "question": "If you were given a project with a tight deadline and limited resources, how would you prioritize and manage your work?",
            "category": "time_management",
            "difficulty": "medium",
            "time_limit": 150,
            "expected_duration": 120
        }
    
    def _get_closing_question(self) -> Dict:
        return {
            "id": 8,
            "type": "closing",
            "question": "Do you have any questions about the role, company, or team? What would you like to know about working here?",
            "category": "engagement",
            "difficulty": "easy",
            "time_limit": 120,
            "expected_duration": 90
        }
    
    def should_continue_interview(self, start_time: datetime, question_count: int) -> bool:
        """Determine if interview should continue based on time and questions"""
        if not start_time:
            return True
            
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        
        # Must ask at least 5 questions
        if question_count < 5:
            return True
            
        # Stop if we've reached max time
        if elapsed >= self.max_duration:
            return False
            
        # Stop if we've asked enough questions and minimum time passed
        if question_count >= self.target_questions and elapsed >= self.min_duration:
            return False
            
        return True
    
    def evaluate_response_quality(self, question: Dict, answer: str, response_time: int) -> Dict:
        """Evaluate individual response quality"""
        if not answer or len(answer.strip()) < 10:
            return {
                "quality_score": 20,
                "feedback": "Response too brief. Please provide more detailed answers.",
                "areas": ["detail", "elaboration"]
            }
        
        # Basic quality metrics
        word_count = len(answer.split())
        expected_time = question.get('expected_duration', 120)
        
        # Score based on multiple factors
        length_score = min(100, (word_count / 50) * 100)  # 50 words = good length
        time_score = 100 if response_time <= expected_time else max(50, 100 - (response_time - expected_time))
        
        # Content analysis (basic)
        content_score = 70  # Base score
        if any(word in answer.lower() for word in ['example', 'experience', 'project', 'result']):
            content_score += 15
        if any(word in answer.lower() for word in ['challenge', 'problem', 'solution', 'learned']):
            content_score += 10
        
        overall_score = (length_score * 0.3 + time_score * 0.2 + content_score * 0.5)
        
        return {
            "quality_score": min(100, max(20, int(overall_score))),
            "word_count": word_count,
            "response_time": response_time,
            "feedback": self._generate_response_feedback(overall_score, word_count)
        }
    
    def _generate_response_feedback(self, score: float, word_count: int) -> str:
        """Generate specific feedback for response"""
        if score >= 85:
            return "Excellent response with good detail and examples."
        elif score >= 70:
            return "Good response. Consider adding more specific examples."
        elif score >= 50:
            return "Adequate response. Try to provide more detail and context."
        else:
            return "Please provide more comprehensive answers with specific examples."
    
    def calculate_final_scores(self, all_responses: List[Dict], total_duration: int) -> Dict:
        """Calculate comprehensive final scores"""
        if not all_responses:
            return self._get_default_scores()
        
        # Calculate individual metrics
        response_scores = []
        total_words = 0
        
        for response in all_responses:
            answer = response.get('answer', '')
            if answer and len(answer.strip()) > 5:
                quality = self.evaluate_response_quality(
                    response.get('question_data', {}), 
                    answer, 
                    response.get('response_time', 120)
                )
                response_scores.append(quality['quality_score'])
                total_words += quality['word_count']
        
        if not response_scores:
            return self._get_default_scores()
        
        # Calculate component scores
        avg_response_quality = sum(response_scores) / len(response_scores)
        
        # Communication score (based on response quality and length)
        communication_score = min(100, avg_response_quality + (total_words / len(all_responses) / 30 * 10))
        
        # Technical score (based on technical question responses)
        technical_responses = [r for r in all_responses if r.get('question_data', {}).get('type') == 'technical']
        technical_score = avg_response_quality if technical_responses else max(40, avg_response_quality - 20)
        
        # Confidence score (based on response completeness)
        answered_count = len([r for r in all_responses if r.get('answer', '').strip()])
        confidence_score = min(100, (answered_count / len(all_responses)) * 100 + avg_response_quality * 0.3)
        
        # Problem solving score
        problem_responses = [r for r in all_responses if 'problem' in r.get('question_data', {}).get('category', '').lower()]
        problem_solving_score = avg_response_quality if problem_responses else max(35, avg_response_quality - 25)
        
        # Overall score with time factor
        time_factor = 1.0
        if total_duration < self.min_duration:
            time_factor = 0.8  # Penalty for too short
        elif total_duration > self.max_duration:
            time_factor = 0.9  # Small penalty for too long
        
        overall_score = int(avg_response_quality * time_factor)
        
        return {
            "overall_score": max(25, min(100, overall_score)),
            "technical_score": max(20, min(100, int(technical_score))),
            "communication_score": max(30, min(100, int(communication_score))),
            "confidence_score": max(25, min(100, int(confidence_score))),
            "problem_solving_score": max(20, min(100, int(problem_solving_score))),
            "leadership_score": max(15, min(100, int(avg_response_quality * 0.7))),
            "adaptability_score": max(25, min(100, int(avg_response_quality * 0.8))),
            "total_responses": len(all_responses),
            "answered_responses": answered_count,
            "average_response_quality": int(avg_response_quality),
            "interview_duration": total_duration
        }
    
    def _get_default_scores(self) -> Dict:
        """Default scores for incomplete interviews"""
        return {
            "overall_score": 35,
            "technical_score": 25,
            "communication_score": 40,
            "confidence_score": 30,
            "problem_solving_score": 25,
            "leadership_score": 20,
            "adaptability_score": 30,
            "total_responses": 0,
            "answered_responses": 0,
            "average_response_quality": 35,
            "interview_duration": 0
        }