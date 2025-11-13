#!/usr/bin/env python3
"""
Interview Controller - Main controller for interview flow
"""

import json
from datetime import datetime
from .question_generator import QuestionGenerator
from .response_evaluator import ResponseEvaluator

class InterviewController:
    def __init__(self, session_id):
        self.session_id = session_id
        self.question_generator = QuestionGenerator()
        self.response_evaluator = ResponseEvaluator()
        self.current_question_index = 0
        self.responses = []
        self.evaluations = []
        self.start_time = None
        
    def start_interview(self):
        """Start the interview and get first question"""
        self.start_time = datetime.utcnow()
        self.current_question_index = 0
        
        first_question = self.question_generator.get_question(0)
        return {
            "question": first_question["question"],
            "question_index": 0,
            "type": first_question["type"]
        }
    
    def process_response(self, user_response: str, response_time: int = 120):
        """Process user response and get next question"""
        
        if not user_response:
            return self._get_current_question()
        
        # Store the response
        response_data = {
            "question_index": self.current_question_index,
            "response": user_response,
            "timestamp": datetime.utcnow().isoformat(),
            "response_time": response_time
        }
        self.responses.append(response_data)
        
        # Evaluate the response
        current_question = self.question_generator.get_question(self.current_question_index)
        evaluation = self.response_evaluator.evaluate_single_response(
            current_question["question"], 
            user_response, 
            response_time
        )
        self.evaluations.append(evaluation)
        
        # Check if we should advance to next question
        should_advance = self.question_generator.should_advance_question(user_response)
        
        if should_advance:
            self.current_question_index += 1
            
            # Check if interview should end
            if self.current_question_index >= 8:
                return {
                    "question": "Thank you for completing the interview! Please click 'End Interview' to see your feedback.",
                    "question_index": self.current_question_index,
                    "type": "completion",
                    "should_end": True
                }
            
            # Get next question
            next_question = self.question_generator.get_question(self.current_question_index)
            return {
                "question": next_question["question"],
                "question_index": self.current_question_index,
                "type": next_question["type"]
            }
        else:
            # Ask for clarification on same question
            clarification = self.question_generator.get_question(self.current_question_index, user_response)
            return {
                "question": clarification["question"],
                "question_index": self.current_question_index,
                "type": "clarification"
            }
    
    def _get_current_question(self):
        """Get current question without advancing"""
        current_question = self.question_generator.get_question(self.current_question_index)
        return {
            "question": current_question["question"],
            "question_index": self.current_question_index,
            "type": current_question["type"]
        }
    
    def complete_interview(self):
        """Complete interview and generate final scores"""
        
        end_time = datetime.utcnow()
        duration = 0
        if self.start_time:
            duration = int((end_time - self.start_time).total_seconds())
        
        # Calculate final scores
        final_scores = self.response_evaluator.calculate_final_scores(self.evaluations, duration)
        
        # Generate feedback
        feedback = self.response_evaluator.generate_feedback(final_scores, self.responses)
        
        # Combine everything
        result = {
            **final_scores,
            **feedback,
            "responses": self.responses,
            "evaluations": self.evaluations,
            "duration": duration,
            "questions_answered": len(self.responses),
            "completion_rate": min(100, (len(self.responses) / 8) * 100)
        }
        
        return result
    
    def get_session_data(self):
        """Get current session data"""
        return {
            "session_id": self.session_id,
            "current_question_index": self.current_question_index,
            "responses_count": len(self.responses),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "responses": self.responses,
            "evaluations": self.evaluations
        }