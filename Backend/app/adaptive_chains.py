import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

class InterviewChain:
    """Base class for interview chains"""
    
    def __init__(self, ai_service):
        self.ai_service = ai_service
    
    def generate_question(self, context: Dict) -> Dict:
        raise NotImplementedError

class IntroChain(InterviewChain):
    """Handles intro phase (1-2 warm-up questions)"""
    
    def generate_question(self, context: Dict) -> Dict:
        session = context['session']
        job_role = context['job_role']
        
        if context.get('question_count', 0) == 0:
            return {
                'question': f"Tell me about your background and what interests you about the {job_role} role.",
                'type': 'behavioral',
                'category': 'introduction',
                'difficulty': 'easy',
                'time_limit': 180,
                'next_action': 'ask'
            }
        else:
            return {
                'question': "What do you consider your strongest professional skill and why?",
                'type': 'behavioral', 
                'category': 'strengths',
                'difficulty': 'easy',
                'time_limit': 180,
                'next_action': 'move_to_core'
            }

class AdaptiveCoreChain(InterviewChain):
    """Main adaptive engine for core questions"""
    
    def generate_question(self, context: Dict) -> Dict:
        previous_questions = context.get('previous_questions', [])
        previous_answers = context.get('previous_answers', {})
        remaining_time = context.get('remaining_time', 600)
        job_role = context['job_role']
        
        # Analyze performance
        performance = self._analyze_performance(previous_answers)
        
        prompt = f"""Generate next adaptive interview question for {job_role}.

Previous Q&A: {json.dumps(self._prepare_context(previous_questions, previous_answers), indent=2)}
Performance Level: {performance['level']}
Remaining Time: {remaining_time} seconds
Areas Covered: {performance['areas_covered']}

Rules:
- If strong answers → increase difficulty
- If weak answers → ask clarifying questions  
- If off-topic → redirect
- Avoid repeating categories: {performance['areas_covered']}

Return JSON:
{{
  "question": "Professional question text",
  "type": "technical/behavioral/situational", 
  "category": "new_category",
  "difficulty": "easy/medium/hard",
  "time_limit": 300,
  "reasoning": "Why this question",
  "next_action": "ask/clarify/move_to_closing"
}}"""

        response = self.ai_service._make_api_request(
            self.ai_service.models['question_generation'], 
            prompt
        )
        
        result = self.ai_service._parse_json_response(response)
        
        # Determine next action based on time and performance
        if remaining_time < 300:
            result['next_action'] = 'move_to_closing'
        elif len(previous_questions) >= 8:
            result['next_action'] = 'move_to_closing'
        else:
            result['next_action'] = 'ask'
            
        return result or self._fallback_question(context)
    
    def _analyze_performance(self, answers: Dict) -> Dict:
        if not answers:
            return {'level': 'unknown', 'areas_covered': [], 'avg_length': 0}
        
        lengths = [len(str(a.get('answer', ''))) for a in answers.values()]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        if avg_length > 100:
            level = 'strong'
        elif avg_length > 50:
            level = 'moderate'
        else:
            level = 'weak'
            
        return {
            'level': level,
            'areas_covered': [],
            'avg_length': avg_length
        }
    
    def _prepare_context(self, questions: List, answers: Dict) -> List:
        context = []
        for i, q in enumerate(questions):
            q_id = str(i + 1)
            answer = answers.get(q_id, {}).get('answer', 'No response')
            context.append({'question': q.get('question', ''), 'answer': answer})
        return context
    
    def _fallback_question(self, context: Dict) -> Dict:
        return {
            'question': 'How do you approach problem-solving in challenging situations?',
            'type': 'behavioral',
            'category': 'problem_solving', 
            'difficulty': 'medium',
            'time_limit': 300,
            'next_action': 'ask'
        }

class ClosingChain(InterviewChain):
    """Handles closing phase and wrap-up"""
    
    def generate_question(self, context: Dict) -> Dict:
        return {
            'question': 'Do you have any questions about the role or our company?',
            'type': 'behavioral',
            'category': 'closing',
            'difficulty': 'easy', 
            'time_limit': 180,
            'next_action': 'finalize'
        }

class FinalizationChain(InterviewChain):
    """Handles final feedback generation and reporting"""
    
    def generate_final_feedback(self, context: Dict) -> Dict:
        full_transcript = context['full_transcript']
        session = context['session']
        
        prompt = f"""Analyze complete interview transcript and provide final assessment.

Full Interview Transcript:
{json.dumps(full_transcript, indent=2)}

Session Details:
- Duration: {session.total_duration} seconds
- Job Role: {session.job_role}
- Questions Asked: {len(full_transcript)}

Provide comprehensive evaluation in JSON:
{{
  "overall_score": 75,
  "technical_score": 70,
  "communication_score": 80,
  "confidence_score": 75,
  "strengths": ["Specific strength 1", "Specific strength 2"],
  "weaknesses": ["Area for improvement 1", "Area for improvement 2"], 
  "detailed_analysis": {{
    "communication": "Assessment of communication skills",
    "technical_skills": "Technical competency evaluation",
    "problem_solving": "Problem-solving approach analysis"
  }},
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "summary": "Overall interview performance summary",
  "pass_fail_recommendation": "pass/needs_improvement/fail"
}}"""

        response = self.ai_service._make_api_request(
            self.ai_service.models['feedback_analysis'],
            prompt,
            max_tokens=2000
        )
        
        return self.ai_service._parse_json_response(response) or self._fallback_feedback()
    
    def _fallback_feedback(self) -> Dict:
        return {
            "overall_score": 70,
            "technical_score": 65,
            "communication_score": 75,
            "confidence_score": 70,
            "strengths": ["Completed interview", "Engaged throughout"],
            "weaknesses": ["Provide more detail", "Include examples"],
            "detailed_analysis": {
                "communication": "Basic communication demonstrated",
                "technical_skills": "Technical knowledge at foundational level", 
                "problem_solving": "Problem-solving approach needs development"
            },
            "recommendations": ["Practice STAR method", "Prepare specific examples"],
            "summary": "Interview completed with areas for improvement identified",
            "pass_fail_recommendation": "needs_improvement"
        }