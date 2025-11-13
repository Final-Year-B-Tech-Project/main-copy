
import json
from datetime import datetime

import google.generativeai as genai
import os
import requests

class SimpleAIService:
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.model = None
        self.fallback_model = None
        
        # Try Gemini first
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✓ Gemini AI initialized")
            except Exception as e:
                print(f"✗ Gemini failed: {e}")
        
        # Try OpenRouter as fallback
        if not self.model and self.openrouter_key:
            try:
                # Test OpenRouter connection
                response = requests.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={"Authorization": f"Bearer {self.openrouter_key}"},
                    timeout=5
                )
                if response.status_code == 200:
                    self.fallback_model = "openrouter"
                    print("✓ OpenRouter AI initialized as fallback")
            except Exception as e:
                print(f"✗ OpenRouter failed: {e}")
        
        if not self.model and not self.fallback_model:
            print("✗ No AI models available - using basic responses")
    
    def generate_response(self, prompt):
        """Generate AI response using available models"""
        # Try Gemini first
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Gemini response failed: {e}")
        
        # Try OpenRouter fallback
        if self.fallback_model == "openrouter":
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "meta-llama/llama-3.1-8b-instruct:free",
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
        
        # Basic contextual response
        return "I understand. Could you tell me more about that?"
    
    def generate_adaptive_question(self, user_response, job_role, question_count, conversation_history):
        """Generate next question based on user response using AI"""
        
        # Try Gemini first
        if self.model:
            try:
                question = self._generate_with_gemini(user_response, job_role)
                if question:
                    print(f"Gemini generated: {question}")
                    return question
            except Exception as e:
                print(f"Gemini failed: {e}")
        
        # Try OpenRouter fallback
        if self.fallback_model == "openrouter":
            try:
                question = self._generate_with_openrouter(user_response, job_role)
                if question:
                    print(f"OpenRouter generated: {question}")
                    return question
            except Exception as e:
                print(f"OpenRouter failed: {e}")
        
        # Generate contextual question without predefined list
        return self._generate_contextual_question(user_response, job_role, question_count)
    
    def _generate_with_gemini(self, user_response, job_role):
        """Generate question using Gemini"""
        prompt = f"You are interviewing for {job_role}. Based on: '{user_response}', ask a relevant follow-up question."
        response = self.model.generate_content(prompt)
        return response.text.strip().replace('Question:', '').strip()
    
    def _generate_with_openrouter(self, user_response, job_role):
        """Generate question using OpenRouter"""
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [{
                    "role": "user",
                    "content": f"You are interviewing for {job_role}. Based on candidate's response: '{user_response}', generate one relevant follow-up question."
                }],
                "max_tokens": 100
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        return None
    
    def _generate_contextual_question(self, user_response, job_role, question_count):
        """Generate contextual question based on response content"""
        response_lower = user_response.lower()
        
        # Analyze response content and generate appropriate questions
        if question_count == 0:
            return f"Great! Now tell me about your experience with {job_role.lower()} technologies and tools."
        elif 'project' in response_lower or 'built' in response_lower:
            return "That sounds interesting! Can you walk me through the technical challenges you faced in that project?"
        elif 'learn' in response_lower or 'study' in response_lower:
            return "How do you typically approach learning new technologies when working on complex projects?"
        elif 'team' in response_lower or 'collaborate' in response_lower:
            return "Tell me about a time when you had to resolve a conflict or disagreement within your team."
        elif 'problem' in response_lower or 'challenge' in response_lower:
            return "How do you prioritize tasks when facing multiple urgent deadlines?"
        elif len(user_response) < 20:
            return "Could you provide more specific details and examples from your experience?"
        elif question_count < 3:
            return f"What specific skills do you think are most important for success in a {job_role} role?"
        elif question_count < 5:
            return "Describe a situation where you had to adapt quickly to changing requirements or priorities."
        elif question_count < 7:
            return "What are your long-term career goals and how does this position align with them?"
        else:
            return "Do you have any questions about our company, team, or this role?"
    
    def evaluate_response(self, response, job_role="General"):
        score = min(85, max(60, len(response.split()) * 3))
        return {
            "score": score,
            "feedback": "Good response. Consider adding more specific examples."
        }
    
    def generate_feedback(self, responses, job_role="General"):
        total_responses = len(responses)
        avg_length = sum(len(r.get('answer', '').split()) for r in responses.values()) / max(1, total_responses)
        
        base_score = min(90, max(50, int(avg_length * 2)))
        
        return {
            "overall_score": base_score,
            "technical_score": base_score - 5,
            "communication_score": base_score + 5,
            "confidence_score": base_score,
            "strengths": ["Completed interview", "Engaged with questions"],
            "weaknesses": ["Could provide more detail", "Add specific examples"],
            "summary": f"Interview completed with {total_responses} responses. Overall performance: {base_score}/100"
        }
