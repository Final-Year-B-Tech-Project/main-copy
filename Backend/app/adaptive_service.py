import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from app import db
from app.adaptive_models import AdaptiveSession, AdaptiveQuestion, AdaptiveResponse
from app.adaptive_chains import IntroChain, AdaptiveCoreChain, ClosingChain, FinalizationChain

class AdaptiveInterviewService:
    """Main service for 20-minute adaptive interviews"""
    
    def __init__(self, ai_service):
        self.ai_service = ai_service
        self.intro_chain = IntroChain(ai_service)
        self.core_chain = AdaptiveCoreChain(ai_service)
        self.closing_chain = ClosingChain(ai_service)
        self.finalization_chain = FinalizationChain(ai_service)
    
    def start_adaptive_session(self, candidate_id: int, job_role: str) -> AdaptiveSession:
        """Start new adaptive interview session"""
        session = AdaptiveSession(
            candidate_id=candidate_id,
            job_role=job_role,
            current_phase='intro',
            status='active',
            target_duration=1200,  # 20 minutes
            conversation_history='[]',
            evaluation_notes='{}'
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session
    
    def get_next_question(self, session_id: int) -> Dict:
        """Get next adaptive question based on current context"""
        session = AdaptiveSession.query.get(session_id)
        if not session or session.status != 'active':
            return {'error': 'Invalid session'}
        
        # Calculate remaining time
        elapsed = (datetime.utcnow() - session.start_time).total_seconds()
        remaining_time = max(0, session.target_duration - elapsed)
        
        if remaining_time < 60:
            return self._force_closing(session)
        
        # Get previous questions and answers
        previous_questions = self._get_session_questions(session_id)
        previous_answers = self._get_session_answers(session_id)
        
        # Build context
        context = {
            'session': session,
            'job_role': session.job_role,
            'question_count': len(previous_questions),
            'previous_questions': previous_questions,
            'previous_answers': previous_answers,
            'remaining_time': remaining_time
        }
        
        # Generate question based on current phase
        if session.current_phase == 'intro':
            question_data = self.intro_chain.generate_question(context)
        elif session.current_phase == 'core':
            question_data = self.core_chain.generate_question(context)
        elif session.current_phase == 'closing':
            question_data = self.closing_chain.generate_question(context)
        else:
            return {'error': 'Invalid phase'}
        
        # Handle phase transitions
        next_action = question_data.get('next_action', 'ask')
        if next_action == 'move_to_core':
            session.current_phase = 'core'
        elif next_action == 'move_to_closing':
            session.current_phase = 'closing'
        elif next_action == 'finalize':
            return self._finalize_session(session)
        
        # Save question
        question = AdaptiveQuestion(
            session_id=session_id,
            question_number=len(previous_questions) + 1,
            phase=session.current_phase,
            question_text=question_data['question'],
            question_type=question_data.get('type', 'behavioral'),
            difficulty=question_data.get('difficulty', 'medium'),
            category=question_data.get('category', 'general'),
            time_limit=question_data.get('time_limit', 300)
        )
        
        db.session.add(question)
        db.session.commit()
        
        return {
            'question_id': question.id,
            'question': question.question_text,
            'type': question.question_type,
            'time_limit': question.time_limit,
            'phase': session.current_phase,
            'remaining_time': remaining_time
        }
    
    def submit_answer(self, session_id: int, question_id: int, answer: str, time_taken: int) -> Dict:
        """Submit answer and get evaluation"""
        session = AdaptiveSession.query.get(session_id)
        question = AdaptiveQuestion.query.get(question_id)
        
        if not session or not question:
            return {'error': 'Invalid session or question'}
        
        # Quick evaluation
        evaluation = self._evaluate_answer(question.question_text, answer)
        
        # Save response
        response = AdaptiveResponse(
            question_id=question_id,
            session_id=session_id,
            response_text=answer,
            response_time=time_taken,
            quality_score=evaluation.get('score', 5),
            evaluation_notes=json.dumps(evaluation)
        )
        
        db.session.add(response)
        
        # Update conversation history
        history = json.loads(session.conversation_history or '[]')
        history.append({
            'question': question.question_text,
            'answer': answer,
            'time_taken': time_taken,
            'score': evaluation.get('score', 5),
            'timestamp': datetime.utcnow().isoformat()
        })
        session.conversation_history = json.dumps(history)
        
        db.session.commit()
        
        return {
            'success': True,
            'evaluation': evaluation,
            'next_question_ready': True
        }
    
    def _evaluate_answer(self, question: str, answer: str) -> Dict:
        """Quick answer evaluation"""
        if not answer or len(answer.strip()) < 10:
            return {'score': 2, 'feedback': 'Very brief response'}
        elif len(answer) < 50:
            return {'score': 4, 'feedback': 'Short response, could be more detailed'}
        elif len(answer) < 150:
            return {'score': 6, 'feedback': 'Good response length'}
        else:
            return {'score': 8, 'feedback': 'Detailed response'}
    
    def _get_session_questions(self, session_id: int) -> List[Dict]:
        """Get all questions for session"""
        questions = AdaptiveQuestion.query.filter_by(session_id=session_id).order_by(AdaptiveQuestion.question_number).all()
        return [{'question': q.question_text, 'type': q.question_type, 'category': q.category} for q in questions]
    
    def _get_session_answers(self, session_id: int) -> Dict:
        """Get all answers for session"""
        responses = AdaptiveResponse.query.filter_by(session_id=session_id).all()
        answers = {}
        for r in responses:
            question = AdaptiveQuestion.query.get(r.question_id)
            if question:
                answers[str(question.question_number)] = {
                    'answer': r.response_text,
                    'time_taken': r.response_time,
                    'score': r.quality_score
                }
        return answers
    
    def _force_closing(self, session: AdaptiveSession) -> Dict:
        """Force session to closing when time runs out"""
        session.current_phase = 'closing'
        db.session.commit()
        return self.closing_chain.generate_question({'session': session})
    
    def _finalize_session(self, session: AdaptiveSession) -> Dict:
        """Finalize session and generate final feedback"""
        session.status = 'completed'
        session.end_time = datetime.utcnow()
        session.total_duration = int((session.end_time - session.start_time).total_seconds())
        
        # Generate full transcript
        full_transcript = self._generate_full_transcript(session.id)
        session.final_transcript = json.dumps(full_transcript)
        
        # Generate final feedback
        context = {
            'session': session,
            'full_transcript': full_transcript
        }
        
        final_feedback = self.finalization_chain.generate_final_feedback(context)
        session.final_feedback = json.dumps(final_feedback)
        
        db.session.commit()
        
        return {
            'session_completed': True,
            'final_feedback': final_feedback,
            'transcript': full_transcript,
            'duration': session.total_duration
        }
    
    def _generate_full_transcript(self, session_id: int) -> List[Dict]:
        """Generate complete interview transcript"""
        questions = AdaptiveQuestion.query.filter_by(session_id=session_id).order_by(AdaptiveQuestion.question_number).all()
        transcript = []
        
        for q in questions:
            response = AdaptiveResponse.query.filter_by(question_id=q.id).first()
            transcript.append({
                'question_number': q.question_number,
                'phase': q.phase,
                'question': q.question_text,
                'answer': response.response_text if response else 'No response',
                'time_taken': response.response_time if response else 0,
                'score': response.quality_score if response else 0
            })
        
        return transcript
    
    def get_session_status(self, session_id: int) -> Dict:
        """Get current session status"""
        session = AdaptiveSession.query.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        elapsed = (datetime.utcnow() - session.start_time).total_seconds()
        remaining = max(0, session.target_duration - elapsed)
        
        return {
            'session_id': session.id,
            'status': session.status,
            'phase': session.current_phase,
            'elapsed_time': int(elapsed),
            'remaining_time': int(remaining),
            'questions_asked': AdaptiveQuestion.query.filter_by(session_id=session_id).count()
        }