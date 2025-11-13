#!/usr/bin/env python3
"""
Adaptive Interviewer - Generates genuine questions based on candidate responses
"""

class AdaptiveInterviewer:
    def __init__(self):
        self.conversation_history = []
        self.candidate_info = {}
        self.question_count = 0
        
    def analyze_response(self, response: str) -> dict:
        """Analyze response to extract information about candidate"""
        response_lower = response.lower()
        info = {}
        
        # Extract education info
        if any(word in response_lower for word in ['student', 'btech', 'engineering', 'college', 'university']):
            info['is_student'] = True
            if 'btech' in response_lower:
                info['degree'] = 'BTech'
        
        # Extract experience level
        if any(word in response_lower for word in ["don't have", "never", "no experience", "illiterate", "dumb"]):
            info['experience_level'] = 'beginner'
        elif any(word in response_lower for word in ['work', 'job', 'company', 'project']):
            info['experience_level'] = 'experienced'
        else:
            info['experience_level'] = 'unknown'
        
        # Extract interests/attitude
        if any(word in response_lower for word in ["don't have interest", "no interest"]):
            info['shows_interest'] = False
        elif any(word in response_lower for word in ['interested', 'like', 'enjoy', 'passionate']):
            info['shows_interest'] = True
        
        # Extract technical background
        if any(word in response_lower for word in ['programming', 'coding', 'software', 'computer']):
            info['technical_background'] = True
        
        return info
    
    def generate_next_question(self, previous_response: str, question_count: int) -> str:
        """Generate next question with multiple fallback layers"""
        
        try:
            # Analyze the response
            candidate_info = self.analyze_response(previous_response)
            self.candidate_info.update(candidate_info)
            
            # Store conversation
            self.conversation_history.append({
                'question': self._get_last_question(),
                'response': previous_response,
                'info_extracted': candidate_info
            })
            
            # Use rule-based questions
            return self._get_rule_based_question(previous_response, question_count)
            
        except Exception as e:
            print(f"Error in question generation: {e}")
            # Emergency fallback
            try:
                from app.backup_questions import BackupQuestionGenerator
                backup = BackupQuestionGenerator()
                return backup.get_next_question(question_count, self.conversation_history)
            except:
                # Ultimate fallback
                return "Could you tell me more about yourself?"
    
    def _get_follow_up_to_introduction(self, response: str) -> str:
        """Generate follow-up based on introduction"""
        response_lower = response.lower()
        
        if 'student' in response_lower and 'btech' in response_lower:
            return "That's great! Which year are you in your BTech program, and what's your specialization?"
        elif 'student' in response_lower:
            return "I see you're a student. What are you studying and which year are you in?"
        elif "don't have interest" in response_lower:
            return "I understand you may not be sure about the role. What kind of work or field do you think you might enjoy?"
        elif len(response.split()) < 5:
            return "Could you tell me a bit more? For example, what's your educational background or what you're currently doing?"
        else:
            return "Thanks for that introduction. What motivated you to apply for this position?"
    
    def _get_education_question(self, response: str) -> str:
        """Generate education-related question"""
        response_lower = response.lower()
        
        if any(year in response_lower for year in ['first', '1st', 'second', '2nd']):
            return "Since you're in the early years of your program, what subjects are you most interested in so far?"
        elif any(year in response_lower for year in ['third', '3rd', 'fourth', '4th', 'final']):
            return "As you're in the later years of your program, have you worked on any projects or assignments that you found interesting?"
        elif 'computer' in response_lower or 'software' in response_lower:
            return "Computer science is a broad field. Which areas within it interest you the most - like programming, databases, or web development?"
        elif "don't" in response_lower or "never" in response_lower:
            return "That's okay, everyone starts somewhere. What subjects in school did you enjoy the most?"
        else:
            return "What has been the most interesting part of your studies so far?"
    
    def _get_skills_question(self, response: str) -> str:
        """Generate skills-related question"""
        response_lower = response.lower()
        
        if any(lang in response_lower for lang in ['java', 'python', 'c++', 'javascript']):
            return f"That's good! How did you learn programming, and what kind of programs have you written?"
        elif 'programming' in response_lower or 'coding' in response_lower:
            return "Which programming languages have you tried, even if just in class or tutorials?"
        elif "don't have" in response_lower or "no skills" in response_lower:
            return "Everyone has some abilities. Are you good at problem-solving, working with computers, or maybe explaining things to others?"
        elif 'database' in response_lower or 'web' in response_lower:
            return "That sounds interesting! Can you tell me about a specific example where you used these skills?"
        else:
            return "What's something you feel confident doing, even if it's not technical?"
    
    def _get_learning_question(self, response: str) -> str:
        """Generate learning-related question"""
        response_lower = response.lower()
        
        if self.candidate_info.get('experience_level') == 'beginner':
            return "Since you're just starting out, how do you usually approach learning something new - like a new subject or skill?"
        elif 'youtube' in response_lower or 'online' in response_lower:
            return "Online learning is great! What's the most useful thing you've learned through online resources?"
        elif 'practice' in response_lower or 'tutorial' in response_lower:
            return "That's a good approach! Can you give me an example of something you learned this way?"
        else:
            return "When you need to learn something new for your studies, what method works best for you?"
    
    def _get_motivation_question(self, response: str) -> str:
        """Generate motivation-related question"""
        if self.candidate_info.get('shows_interest') == False:
            return "I understand you might not be sure about this field. What kind of work environment do you think you'd enjoy - working with people, solving problems, or creating things?"
        elif self.candidate_info.get('is_student'):
            return "As a student, what do you hope to achieve in your career after graduation?"
        else:
            return "What motivates you to do your best work or studies?"
    
    def _get_future_question(self, response: str) -> str:
        """Generate future-oriented question"""
        response_lower = response.lower()
        
        if 'software' in response_lower or 'developer' in response_lower:
            return "That's a good goal! What kind of software or applications would you like to work on?"
        elif self.candidate_info.get('is_student'):
            return "After completing your BTech, what's the first step you'd like to take in your career?"
        else:
            return "Where do you see yourself in the next 2-3 years?"
    
    def _get_scenario_question(self, response: str) -> str:
        """Generate scenario-based question"""
        if self.candidate_info.get('experience_level') == 'beginner':
            return "Imagine you're given a task you've never done before. How would you approach it?"
        else:
            return "Tell me about a time when you had to work with others to achieve a goal."
    
    def _get_last_question(self) -> str:
        """Get the last question asked"""
        if self.conversation_history:
            return self.conversation_history[-1].get('question', 'Previous question')
        return 'Opening question'
    
    def _get_rule_based_question(self, response: str, question_count: int) -> str:
        """Generate rule-based question ensuring good flow"""
        if question_count == 0:
            return self._get_follow_up_to_introduction(response)
        elif question_count == 1:
            return self._get_education_question(response)
        elif question_count == 2:
            return self._get_skills_question(response)
        elif question_count == 3:
            return self._get_learning_question(response)
        elif question_count == 4:
            return self._get_motivation_question(response)
        elif question_count == 5:
            return self._get_future_question(response)
        elif question_count == 6:
            return self._get_scenario_question(response)
        elif question_count == 7:
            return "What's something you're particularly proud of achieving?"
        elif question_count == 8:
            return "How do you handle challenges or setbacks?"
        else:
            return "Do you have any questions about this role or our company?"
    
    def should_continue_interview(self, question_count: int, total_time: int, responses: list = None) -> bool:
        """Decide if interview should continue - ensure minimum 6 questions"""
        # Minimum 6 questions required for proper evaluation
        if question_count < 6:
            return True
            
        # Maximum 10 questions or 15 minutes to keep it focused
        if question_count >= 10 or total_time >= 900:
            return False
            
        # Analyze response quality for early completion
        if responses and question_count >= 7:
            good_responses = 0
            for resp in responses[-3:]:  # Check last 3 responses
                answer = resp.get('answer', '') or resp.get('response', '')
                if len(answer.split()) >= 10:  # Good length response
                    good_responses += 1
            
            # If getting consistently good responses, can end at 7-8 questions
            if good_responses >= 2:
                return False
        
        return True
    
    def get_opening_question(self) -> str:
        """Get the opening question with fallback"""
        try:
            return "Hello! Welcome to the interview. I'd like to start by getting to know you better. Could you please introduce yourself and tell me about your background?"
        except:
            return "Could you please introduce yourself?"