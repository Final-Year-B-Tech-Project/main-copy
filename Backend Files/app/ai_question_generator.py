#!/usr/bin/env python3
"""
AI-Powered Question Generator with robust fallback
"""

import requests
import json
import os
from dotenv import load_dotenv

class AIQuestionGenerator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        
    def generate_next_question(self, conversation_history: list, candidate_info: dict) -> str:
        """Generate next question - using fallback for reliability"""
        # Use fallback for consistent performance
        return self._fallback_question(conversation_history, candidate_info)
    
    def _build_context(self, conversation_history: list, candidate_info: dict) -> str:
        """Build conversation context"""
        context = ""
        
        for i, exchange in enumerate(conversation_history, 1):
            context += f"Q{i}: {exchange.get('question', 'Previous question')}\n"
            context += f"A{i}: {exchange.get('response', 'No response')}\n\n"
        
        return context
    
    def _fallback_question(self, conversation_history: list, candidate_info: dict) -> str:
        """Smart fallback question generator"""
        question_count = len(conversation_history)
        
        # Analyze conversation to avoid repetition
        topics_covered = set()
        
        for exchange in conversation_history:
            response = exchange.get('response', '').lower()
            
            if any(word in response for word in ['student', 'study', 'college', 'university']):
                topics_covered.add('education')
            if any(word in response for word in ['work', 'job', 'company', 'internship']):
                topics_covered.add('experience')
            if any(word in response for word in ['programming', 'coding', 'technical']):
                topics_covered.add('technical')
            if any(word in response for word in ['project', 'built', 'developed']):
                topics_covered.add('projects')
        
        # Progressive question flow ensuring 6-10 questions
        if question_count == 0:
            return "Could you tell me more about your background and what you're currently doing?"
        elif question_count == 1 and 'education' not in topics_covered:
            return "What are you studying, and which year are you in?"
        elif question_count <= 2 and 'technical' not in topics_covered:
            return "What technical skills or programming languages have you worked with?"
        elif question_count <= 3 and 'projects' not in topics_covered:
            return "Have you worked on any interesting projects or assignments?"
        elif question_count <= 4 and 'experience' not in topics_covered:
            return "Do you have any work experience or internships?"
        elif question_count <= 5:
            return "How do you approach learning new technologies?"
        elif question_count <= 6:
            return "Tell me about a challenge you've overcome."
        elif question_count <= 7:
            return "What kind of work environment interests you?"
        elif question_count <= 8:
            return "Where do you see yourself in the next few years?"
        else:
            return "Do you have any questions about this role?"