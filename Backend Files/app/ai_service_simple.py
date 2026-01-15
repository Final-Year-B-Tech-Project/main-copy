import json
from datetime import datetime
import os
import requests

class SimpleAIService:
    def __init__(self):
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.model = None
        self.fallback_model = "openrouter"
        self.resume_data = None
        
        if self.openrouter_key:
            print("[OK] OpenRouter AI initialized")
        else:
            print("[ERROR] No OpenRouter API key found")
    
    def get_interview_opening(self, job_role, duration_minutes=20):
        """Get professional interview opening script"""
        return f"""Hello. I'm your AI interviewer for today.
This interview will assess your skills, problem-solving ability, and clarity of thought for the {job_role} position.

The interview will last approximately {duration_minutes} minutes and consists of multiple sections.
Please answer clearly and concisely.

There are no trick questions. If you don't know an answer, say so.

Let's begin."""
    
    def generate_response(self, prompt):
        """Generate AI response using OpenRouter"""
        if self.fallback_model == "openrouter":
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "meta-llama/llama-3.1-8b-instruct",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 500
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content']
            except Exception as e:
                print(f"OpenRouter response failed: {e}")
        
        return "I understand. Could you tell me more about that?"
    
    def generate_adaptive_question(self, user_response, job_role, question_count, conversation_history):
        """Generate next question using OpenRouter only"""
        
        context = self._build_conversation_context(conversation_history, job_role)
        
        if self.fallback_model == "openrouter":
            try:
                question = self._generate_with_openrouter_advanced(user_response, job_role, question_count, context)
                if question and len(question.strip()) > 10:
                    print(f"OpenRouter generated: {question}")
                    return question
            except Exception as e:
                print(f"OpenRouter failed: {e}")
        
        print("[INFO] Using smart fallback questions")
        return self._generate_smart_fallback(user_response, job_role, question_count)
    
    def _build_conversation_context(self, conversation_history, job_role):
        """Build context from conversation history"""
        if not conversation_history:
            return f"This is the beginning of a {job_role} interview."
        
        context = f"Interview for {job_role} position. Previous questions and responses:\n"
        for i, (q, a) in enumerate(conversation_history[-3:], 1):  # Last 3 exchanges
            context += f"Q{i}: {q}\nA{i}: {a}\n"
        return context

    
    def _generate_with_openrouter_advanced(self, user_response, job_role, question_count, context):
        """Advanced OpenRouter question generation with resume context and fallback models"""
        
        # Add resume context if available
        resume_context = ""
        if self.resume_data:
            skills = self.resume_data.get('skills', [])
            exp_years = self.resume_data.get('experience_years', 0)
            if skills:
                resume_context = f"\n\nCandidate's Resume: {exp_years} years experience. Skills: {', '.join(skills[:8])}"
        
        # Build more specific prompt based on response content
        response_lower = user_response.lower()
        focus_area = ""
        
        if 'project' in response_lower or 'built' in response_lower:
            focus_area = "Ask about technical challenges, decisions, or outcomes from that project."
        elif 'experience' in response_lower or 'worked' in response_lower:
            focus_area = "Dig deeper into specific responsibilities, achievements, or learnings."
        elif 'team' in response_lower or 'collaborate' in response_lower:
            focus_area = "Explore their role in team dynamics, leadership, or conflict resolution."
        elif len(user_response.split()) < 15:
            focus_area = "Ask for more specific details and concrete examples."
        else:
            focus_area = "Build naturally on what they just shared."
        
        prompt = f"""You are a professional interviewer for a {job_role} position.

{context}{resume_context}

Candidate's latest response: "{user_response}"

{focus_area}

Generate ONE relevant follow-up question that directly relates to their response.
Respond with ONLY the question, no extra text."""
        
        # Try multiple models with fallback - using available models
        models = [
            "meta-llama/llama-3.1-8b-instruct",
            "mistralai/mistral-7b-instruct",
            "anthropic/claude-3-haiku"
        ]
        
        for model in models:
            try:
                print(f"[DEBUG] Trying model: {model}")
                
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://talentsync.ai",
                        "X-Title": "TalentSync AI Interview"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100,
                        "temperature": 0.7
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        question = self._clean_question(data['choices'][0]['message']['content'])
                        print(f"[OK] {model} generated: {question}")
                        return question
                else:
                    print(f"[ERROR] {model} failed: {response.status_code}")
                    continue
                    
            except Exception as e:
                print(f"[ERROR] {model} error: {e}")
                continue
        
        # All models failed
        print("[WARNING] All LLM models failed")
        return None
    
    def _clean_question(self, question_text):
        """Clean and format question text"""
        if not question_text:
            return None
        
        # Remove common prefixes
        prefixes = ['Question:', 'Q:', 'Next question:', 'Follow-up:']
        for prefix in prefixes:
            if question_text.startswith(prefix):
                question_text = question_text[len(prefix):].strip()
        
        # Ensure it ends with a question mark
        question_text = question_text.strip()
        if question_text and not question_text.endswith('?'):
            question_text += '?'
        
        return question_text
    
    def _generate_smart_fallback(self, user_response, job_role, question_count):
        """Smart fallback questions based on response analysis"""
        response_lower = user_response.lower()
        
        # Technical depth questions
        if 'project' in response_lower or 'built' in response_lower:
            return f"What was the most challenging technical aspect of that project, and how did you solve it?"
        elif 'technology' in response_lower or 'tool' in response_lower:
            return f"How do you stay updated with the latest {job_role} technologies and trends?"
        elif 'team' in response_lower or 'collaborate' in response_lower:
            return "Describe a situation where you had to explain a complex technical concept to a non-technical team member."
        elif 'problem' in response_lower or 'challenge' in response_lower:
            return "Walk me through your problem-solving process when facing a technical issue you've never encountered before."
        elif 'experience' in response_lower:
            return f"What's the most impactful {job_role} project you've worked on and why?"
        elif len(user_response.split()) < 10:
            return "Could you elaborate on that with a specific example from your experience?"
        
        # Progressive questions based on interview stage
        if question_count < 3:
            return f"Tell me about your most significant achievement in {job_role}."
        elif question_count < 6:
            return "Describe a time when you had to learn a new technology quickly for a project."
        elif question_count < 9:
            return "How do you handle tight deadlines while maintaining code quality?"
        else:
            return "What questions do you have about this role or our team?"
    
    def evaluate_response(self, response, job_role="General"):
        """Evaluate candidate response"""
        word_count = len(response.split())
        
        # Base score on response length and content
        if word_count < 10:
            score = 50
        elif word_count < 30:
            score = 65
        elif word_count < 60:
            score = 75
        else:
            score = 85
        
        # Adjust based on content quality indicators
        response_lower = response.lower()
        if any(word in response_lower for word in ['project', 'experience', 'challenge', 'solution']):
            score += 5
        if any(word in response_lower for word in ['team', 'collaborate', 'lead']):
            score += 3
        
        return {
            "score": min(95, max(40, score)),
            "feedback": "Good response. Consider adding more specific examples." if score < 80 else "Excellent detailed response."
        }
    
    def generate_feedback(self, responses, job_role="General"):
        """Generate comprehensive interview feedback"""
        total_responses = len(responses)
        if total_responses == 0:
            return self._default_feedback()
        
        # Calculate metrics
        total_words = sum(len(r.get('answer', '').split()) for r in responses.values())
        avg_length = total_words / total_responses
        
        # Base scoring
        base_score = min(90, max(50, int(avg_length * 1.5)))
        
        # Content analysis
        all_text = ' '.join(r.get('answer', '') for r in responses.values()).lower()
        
        # Technical keywords boost
        tech_keywords = ['project', 'technology', 'solution', 'challenge', 'experience', 'team', 'development']
        tech_score = sum(3 for keyword in tech_keywords if keyword in all_text)
        
        final_score = min(95, base_score + tech_score)
        
        return {
            "overall_score": final_score,
            "technical_score": max(40, final_score - 5),
            "communication_score": min(95, final_score + 5),
            "confidence_score": final_score,
            "strengths": self._identify_strengths(all_text, final_score),
            "weaknesses": self._identify_weaknesses(all_text, final_score),
            "summary": f"Interview completed with {total_responses} responses. Overall performance: {final_score}/100. {self._get_performance_level(final_score)}"
        }
    
    def _identify_strengths(self, text, score):
        """Identify candidate strengths"""
        strengths = []
        if 'project' in text:
            strengths.append("Demonstrated project experience")
        if 'team' in text or 'collaborate' in text:
            strengths.append("Shows teamwork and collaboration skills")
        if 'challenge' in text or 'problem' in text:
            strengths.append("Problem-solving mindset")
        if score >= 80:
            strengths.append("Clear and detailed communication")
        if not strengths:
            strengths = ["Completed the interview", "Engaged with questions"]
        return strengths
    
    def _identify_weaknesses(self, text, score):
        """Identify areas for improvement"""
        weaknesses = []
        if score < 60:
            weaknesses.append("Responses could be more detailed")
        if score < 70:
            weaknesses.append("Consider providing more specific examples")
        if 'project' not in text:
            weaknesses.append("Could mention more project experience")
        if not weaknesses:
            weaknesses = ["Continue practicing technical communication"]
        return weaknesses
    
    def _get_performance_level(self, score):
        """Get performance level description"""
        if score >= 85:
            return "Excellent performance."
        elif score >= 75:
            return "Good performance with room for improvement."
        elif score >= 65:
            return "Average performance, practice recommended."
        else:
            return "Below average, significant practice needed."
    
    def _default_feedback(self):
        """Default feedback for edge cases"""
        return {
            "overall_score": 60,
            "technical_score": 55,
            "communication_score": 65,
            "confidence_score": 60,
            "strengths": ["Participated in interview"],
            "weaknesses": ["Practice providing more detailed responses"],
            "summary": "Interview completed. Practice recommended for better performance."
        }
