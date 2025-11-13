#!/usr/bin/env python3
"""
Question Generator - Handles question generation and progression
"""

class QuestionGenerator:
    def __init__(self):
        self.questions_bank = {
            0: {
                "question": "Good day! Welcome to your interview. Please tell me about yourself - your background, education, and what interests you about this role.",
                "type": "introduction",
                "follow_up_needed": True
            },
            1: {
                "question": "I'd like to know more about your background. Can you share details about your education, work experience, or any relevant projects you've worked on?",
                "type": "background", 
                "follow_up_needed": True
            },
            2: {
                "question": "What are your key technical skills and strengths? Please provide specific examples of how you've applied them.",
                "type": "technical",
                "follow_up_needed": True
            },
            3: {
                "question": "Describe a challenging problem you've solved. Walk me through your approach and the outcome.",
                "type": "problem_solving",
                "follow_up_needed": True
            },
            4: {
                "question": "Tell me about a time when you had to learn something new quickly. How did you approach it?",
                "type": "learning",
                "follow_up_needed": True
            },
            5: {
                "question": "How do you handle working in a team? Can you give me an example of a successful team project?",
                "type": "teamwork",
                "follow_up_needed": True
            },
            6: {
                "question": "Where do you see yourself in the next 3-5 years? What are your career goals?",
                "type": "goals",
                "follow_up_needed": True
            },
            7: {
                "question": "Do you have any questions about this role, the company, or the team you'd be working with?",
                "type": "closing",
                "follow_up_needed": False
            }
        }
    
    def get_question(self, question_index: int, previous_response: str = "") -> dict:
        """Get question based on index and previous response quality"""
        
        # If response is too poor, ask for clarification
        if previous_response and self._is_poor_response(previous_response):
            return self._get_clarification_question(question_index)
        
        # Get next question
        if question_index < len(self.questions_bank):
            return self.questions_bank[question_index]
        else:
            return self.questions_bank[7]  # Closing question
    
    def _is_poor_response(self, response: str) -> bool:
        """Check if response is too poor to proceed"""
        if not response or len(response.strip()) < 10:
            return True
        
        poor_indicators = [
            "i don't know", "don't know", "no idea", "nothing", 
            "i don't have", "don't have", "no experience",
            "i don't understand", "don't understand"
        ]
        
        response_lower = response.lower()
        poor_count = sum(1 for indicator in poor_indicators if indicator in response_lower)
        
        # If response is mostly poor indicators
        return poor_count > 0 and len(response.split()) < 15
    
    def _get_clarification_question(self, current_index: int) -> dict:
        """Get clarification question for poor responses"""
        clarifications = {
            0: "I'd like to learn more about you. Could you share your name, educational background, or any work experience you have?",
            1: "Please provide more details. For example, what did you study, where did you work, or what projects have you been involved in?",
            2: "Can you think of any skills you have? Perhaps computer skills, communication abilities, or things you're good at?",
            3: "Think of any challenge you've faced - it could be a school project, work task, or personal situation. How did you handle it?",
            4: "Consider any time you had to learn something new - maybe a software, skill, or subject. How did you go about learning it?",
            5: "Have you worked with others on any project, assignment, or activity? How was that experience?",
            6: "What would you like to achieve in your career? What kind of work interests you?",
            7: "Is there anything you'd like to know about this opportunity or the work environment?"
        }
        
        return {
            "question": clarifications.get(current_index, "Could you please provide a more detailed response?"),
            "type": "clarification",
            "follow_up_needed": True
        }
    
    def should_advance_question(self, response: str) -> bool:
        """Determine if response is good enough to advance to next question"""
        if not response or len(response.strip()) < 15:
            return False
        
        # Check for meaningful content
        meaningful_words = [
            "experience", "project", "work", "study", "learn", "skill",
            "challenge", "problem", "solution", "team", "goal", "career"
        ]
        
        response_lower = response.lower()
        meaningful_count = sum(1 for word in meaningful_words if word in response_lower)
        
        return meaningful_count > 0 and len(response.split()) >= 8