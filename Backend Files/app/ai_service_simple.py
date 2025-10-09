import json
import random
from typing import List, Dict, Any, Optional

class SimpleAIService:
    """Contextual AI service for adaptive interviews."""
    
    def __init__(self):
        self.processing = False
        self.conversation_history = []
        
        # Role-specific question flows
        self.role_questions = {
            "Data Scientist": [
                "Tell me about your background and experience in data science.",
                "How do you approach a new data science project from start to finish?",
                "Describe your experience with machine learning algorithms. Which ones have you used?",
                "How do you handle missing or dirty data in your datasets?",
                "What's the most challenging data problem you've solved and how did you approach it?"
            ],
            "Software Developer": [
                "Tell me about your programming background and preferred technologies.",
                "How do you approach debugging complex issues in your code?",
                "Describe your experience with version control and collaborative development.",
                "What's your process for writing clean, maintainable code?",
                "Tell me about a challenging technical problem you solved recently."
            ],
            "Product Manager": [
                "Tell me about your experience in product management.",
                "How do you prioritize features when resources are limited?",
                "Describe how you gather and analyze user feedback.",
                "How do you work with engineering teams to deliver products?",
                "Tell me about a product decision you made that had significant impact."
            ],
            "General": [
                "Tell me about yourself and your professional background.",
                "What are your key strengths and how do they apply to this role?",
                "Describe a challenging situation you faced and how you handled it.",
                "What technologies or tools are you most comfortable working with?",
                "What are your career goals and how does this position fit into them?"
            ]
        }
        
        # Contextual follow-up responses
        self.contextual_responses = {
            "experience": [
                "That's valuable experience. Can you elaborate on the specific challenges you faced?",
                "Interesting background. How has this experience prepared you for this role?",
                "Good foundation. What would you say was your biggest learning from that experience?"
            ],
            "technical": [
                "Great technical insight. How do you stay updated with new technologies?",
                "That's a solid approach. Can you walk me through your problem-solving process?",
                "Excellent. How do you ensure code quality and maintainability in your projects?"
            ],
            "project": [
                "That sounds like an impactful project. What was your specific role and contribution?",
                "Interesting project. What were the key challenges and how did you overcome them?",
                "Great example. What metrics did you use to measure the project's success?"
            ],
            "problem_solving": [
                "Good problem-solving approach. Can you give me a specific example?",
                "That's a thoughtful method. How do you handle situations with incomplete information?",
                "Excellent. How do you prioritize when dealing with multiple complex problems?"
            ]
        }
    
    def generate_simple_response(self, user_message: str, question_count: int = 0, job_role: str = "General") -> str:
        """Generate intelligent, adaptive response based on user input and role."""
        if self.processing:
            return "Please wait while I process your response..."
        
        # Store conversation history
        self.conversation_history.append({
            "user_message": user_message,
            "question_count": question_count,
            "timestamp": json.dumps({})
        })
        
        # Get role-specific questions
        questions = self.role_questions.get(job_role, self.role_questions["General"])
        
        # Initial greeting for first interaction
        if question_count == 0 and not user_message.strip():
            return f"Hello! Welcome to your TalentSync interview for the {job_role} position. I'm your AI interviewer, and I'm excited to learn about your background and experience. Let's start with our first question: {questions[0]}"
        
        # Handle user responses intelligently
        if user_message.strip():
            # Analyze the response quality and provide contextual feedback
            response_analysis = self._analyze_user_response(user_message)
            
            # Generate contextual follow-up
            contextual_response = self._get_contextual_response(user_message)
            
            # Move to next question if we have more
            if question_count + 1 < len(questions):
                next_question = questions[question_count + 1]
                return f"{contextual_response} {next_question}"
            else:
                # Final wrap-up
                return f"{contextual_response} That completes our structured interview questions. Before we finish, is there anything important about your qualifications or experience that you'd like to highlight?"
        
        # If no response, encourage the candidate
        if question_count < len(questions):
            encouragements = [
                "I'd love to hear your thoughts on this. Please take your time to respond.",
                "Feel free to share as much detail as you're comfortable with.",
                "This is your opportunity to showcase your experience. Please go ahead."
            ]
            return f"{random.choice(encouragements)} {questions[question_count]}"
        
        # Interview completion
        return "Thank you for your comprehensive responses! You've completed all the interview questions. Please click 'End Interview' to proceed to your detailed feedback and evaluation."
    
    def _analyze_user_response(self, user_message: str) -> dict:
        """Analyze user response quality and content."""
        message_lower = user_message.lower()
        analysis = {
            'length': len(user_message),
            'has_examples': any(word in message_lower for word in ['example', 'instance', 'case', 'time when']),
            'shows_confidence': any(word in message_lower for word in ['confident', 'sure', 'definitely', 'absolutely']),
            'technical_content': any(word in message_lower for word in ['code', 'programming', 'algorithm', 'technical', 'technology']),
            'experience_mentioned': any(word in message_lower for word in ['experience', 'worked', 'years', 'role', 'position']),
            'problem_solving': any(word in message_lower for word in ['problem', 'challenge', 'solve', 'solution', 'approach'])
        }
        return analysis
    
    def _get_contextual_response(self, user_message: str) -> str:
        """Generate intelligent contextual response based on user's message content."""
        message_lower = user_message.lower()
        analysis = self._analyze_user_response(user_message)
        
        # Handle very short or unclear responses
        if len(user_message.strip()) < 10:
            return "I'd appreciate if you could provide a bit more detail in your response. This helps me better understand your qualifications."
        
        # Handle negative or uncertain responses
        if any(word in message_lower for word in ['no', 'none', 'nothing', "don't have", "haven't", 'never']):
            return "That's perfectly fine. Everyone starts somewhere. Let me ask you about something else that might showcase your potential."
        
        # Contextual responses based on content analysis
        if analysis['experience_mentioned'] and analysis['has_examples']:
            return "Excellent! I can see you have relevant experience and you're providing concrete examples. That's exactly what I like to hear."
        elif analysis['technical_content']:
            return "Great technical insight! Your understanding of these concepts is evident."
        elif analysis['problem_solving']:
            return "I appreciate how you approach problem-solving. That's a valuable skill in any role."
        elif analysis['has_examples']:
            return "Thank you for providing specific examples. That really helps me understand your capabilities."
        elif analysis['shows_confidence']:
            return "I can sense your confidence in this area, which is great to see."
        else:
            # Encouraging responses for basic answers
            encouraging_responses = [
                "Thank you for sharing that. I can see you're thoughtful in your approach.",
                "That's a good start. I appreciate your honesty and directness.",
                "I understand. Let's explore this topic a bit further.",
                "That gives me some insight into your background."
            ]
            return random.choice(encouraging_responses)
    
    def generate_simple_feedback(self, responses: List[Dict] = None, feedback_type: str = "student") -> Dict:
        """Generate contextual feedback based on actual responses."""
        self.processing = True
        
        # Analyze responses if provided
        if responses and len(responses) > 0:
            # Calculate scores based on response quality
            communication_score = self._analyze_communication(responses)
            technical_score = self._analyze_technical_content(responses)
            confidence_score = self._analyze_confidence(responses)
            problem_solving_score = self._analyze_problem_solving(responses)
            
            overall_score = (communication_score + technical_score + confidence_score + problem_solving_score) / 4
        else:
            # Default scores
            communication_score = 80
            technical_score = 85
            confidence_score = 82
            problem_solving_score = 78
            overall_score = 81
        
        # Generate detailed feedback based on responses
        strengths = self._generate_strengths(responses) if responses else "Good communication skills and professional approach."
        improvements = self._generate_improvements(responses) if responses else "Continue building experience and practicing interview skills."
        
        feedback = {
            "overall_score": round(overall_score),
            "communication_score": communication_score,
            "technical_score": technical_score,
            "confidence_score": confidence_score,
            "problem_solving_score": problem_solving_score,
            "coding_score": technical_score,  # Use technical score for coding
            "status": "SHORTLISTED" if overall_score >= 75 else "UNDER_REVIEW",
            "detailed_analysis": {
                "technical_skills": strengths,
                "communication": improvements
            },
            "transcript_highlights": self._generate_highlights(responses) if responses else [
                {"type": "positive", "text": "Good overall performance", "timestamp": "0:15:30"}
            ]
        }
        
        self.processing = False
        return feedback
    
    def _analyze_communication(self, responses: List[Dict]) -> int:
        """Analyze communication quality from responses."""
        if not responses:
            return 80
        
        total_length = sum(len(r.get('answer', '')) for r in responses)
        avg_length = total_length / len(responses) if responses else 0
        
        # Score based on response length and completeness
        if avg_length > 100:
            return random.randint(85, 95)
        elif avg_length > 50:
            return random.randint(75, 85)
        else:
            return random.randint(65, 75)
    
    def _analyze_technical_content(self, responses: List[Dict]) -> int:
        """Analyze technical content quality."""
        if not responses:
            return 85
        
        technical_keywords = ['algorithm', 'data', 'code', 'programming', 'technical', 'system', 'framework', 'technology']
        technical_mentions = 0
        
        for response in responses:
            answer = response.get('answer', '').lower()
            technical_mentions += sum(1 for keyword in technical_keywords if keyword in answer)
        
        # Score based on technical content
        if technical_mentions >= 5:
            return random.randint(88, 95)
        elif technical_mentions >= 3:
            return random.randint(80, 88)
        else:
            return random.randint(70, 80)
    
    def _analyze_confidence(self, responses: List[Dict]) -> int:
        """Analyze confidence level from responses."""
        if not responses:
            return 82
        
        confidence_indicators = ['i can', 'i have', 'i will', 'confident', 'sure', 'definitely', 'absolutely']
        confidence_score = 0
        
        for response in responses:
            answer = response.get('answer', '').lower()
            confidence_score += sum(1 for indicator in confidence_indicators if indicator in answer)
        
        base_score = 75 + min(confidence_score * 3, 20)
        return random.randint(max(base_score - 5, 70), min(base_score + 5, 95))
    
    def _analyze_problem_solving(self, responses: List[Dict]) -> int:
        """Analyze problem-solving approach."""
        if not responses:
            return 78
        
        problem_keywords = ['solve', 'approach', 'method', 'strategy', 'plan', 'analyze', 'solution']
        problem_mentions = 0
        
        for response in responses:
            answer = response.get('answer', '').lower()
            problem_mentions += sum(1 for keyword in problem_keywords if keyword in answer)
        
        base_score = 70 + min(problem_mentions * 4, 25)
        return random.randint(max(base_score - 5, 65), min(base_score + 5, 95))
    
    def _generate_strengths(self, responses: List[Dict]) -> str:
        """Generate strengths based on responses."""
        if not responses:
            return "Good communication skills and professional approach."
        
        strengths = []
        
        # Analyze response patterns
        avg_length = sum(len(r.get('answer', '')) for r in responses) / len(responses)
        if avg_length > 80:
            strengths.append("provides detailed and comprehensive responses")
        
        # Check for technical content
        technical_content = any('technical' in r.get('answer', '').lower() or 'code' in r.get('answer', '').lower() for r in responses)
        if technical_content:
            strengths.append("demonstrates strong technical knowledge")
        
        # Check for examples
        has_examples = any('example' in r.get('answer', '').lower() or 'project' in r.get('answer', '').lower() for r in responses)
        if has_examples:
            strengths.append("supports answers with concrete examples")
        
        if not strengths:
            strengths = ["shows good communication skills", "maintains professional demeanor"]
        
        return "Candidate " + ", ".join(strengths) + "."
    
    def _generate_improvements(self, responses: List[Dict]) -> str:
        """Generate improvement suggestions."""
        improvements = [
            "Consider providing more specific examples to illustrate your points",
            "Practice articulating technical concepts in simpler terms",
            "Work on structuring responses with clear beginning, middle, and end",
            "Continue building hands-on experience with relevant technologies"
        ]
        
        return random.choice(improvements) + "."
    
    def _generate_highlights(self, responses: List[Dict]) -> List[Dict]:
        """Generate transcript highlights."""
        if not responses:
            return [{"type": "positive", "text": "Good overall performance", "timestamp": "0:15:30"}]
        
        highlights = []
        for i, response in enumerate(responses[:3]):  # Take first 3 responses
            timestamp = f"0:{15 + i*5}:30"
            answer = response.get('answer', '')[:50] + "..." if len(response.get('answer', '')) > 50 else response.get('answer', '')
            highlights.append({
                "type": "positive",
                "text": f"Candidate: {answer}",
                "timestamp": timestamp
            })
        
        return highlights