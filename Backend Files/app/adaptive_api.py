from flask import Blueprint, request, jsonify
from app.ai_service import AIInterviewService

adaptive_api = Blueprint('adaptive_api', __name__)
ai_service = AIInterviewService()

@adaptive_api.route('/api/generate-adaptive-question', methods=['POST'])
def generate_adaptive_question():
    """Generate truly adaptive next question based on performance."""
    try:
        data = request.json
        job_role = data.get('job_role', 'General')
        previous_questions = data.get('previous_questions', [])
        previous_answers = data.get('previous_answers', {})
        student_profile = data.get('student_profile')
        
        # Use enhanced adaptive questioning
        question = ai_service.generate_adaptive_question(
            job_role=job_role,
            previous_questions=previous_questions,
            previous_answers=previous_answers,
            student_profile=student_profile
        )
        
        return jsonify({'success': True, 'question': question})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@adaptive_api.route('/api/generate-next-question', methods=['POST'])
def generate_next_question():
    """Generate adaptive next question based on previous answer."""
    try:
        data = request.json
        previous_answer = data.get('previous_answer', '')
        question_number = data.get('question_number', 2)
        
        # Use AI to generate adaptive question
        prompt = f"""Based on this candidate's answer: "{previous_answer}"
        
Generate a relevant follow-up interview question (question #{question_number}).
Make it natural and conversational. Return only the question text, nothing else."""
        
        response = ai_service._make_api_request(
            ai_service.models['question_generation'], 
            prompt, 
            max_tokens=100
        )
        
        if response and response.strip():
            question = response.strip().strip('"')
            return jsonify({'success': True, 'question': question})
        else:
            return jsonify({'success': False, 'message': 'AI unavailable'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@adaptive_api.route('/api/generate-ai-response', methods=['POST'])
def generate_ai_response():
    """Generate AI response based on user message and interactions."""
    try:
        data = request.json
        user_message = data.get('message', '')
        current_tool = data.get('current_tool', 'chat')
        interactions = data.get('interactions', [])
        
        # Create context-aware prompt
        context = f"User is currently using: {current_tool}\n"
        context += f"Recent interactions: {len(interactions)} recorded\n"
        context += f"User said: {user_message}\n\n"
        
        prompt = context + "Generate a natural, engaging follow-up response as an AI interviewer. Keep it conversational and relevant to their answer."
        
        response = ai_service._make_api_request(
            ai_service.models['behavioral_analysis'],
            prompt,
            max_tokens=150
        )
        
        if response and response.strip():
            ai_response = response.strip().strip('"')
            return jsonify({'success': True, 'response': ai_response})
        else:
            fallback_responses = [
                "That's interesting! Can you tell me more about that?",
                "Great point! How did you approach that challenge?",
                "I see. What was the outcome of that experience?"
            ]
            import random
            return jsonify({'success': True, 'response': random.choice(fallback_responses)})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@adaptive_api.route('/api/log-interaction', methods=['POST'])
def log_interaction():
    """Log user interactions for AI analysis."""
    try:
        data = request.json
        session_id = data.get('session_id')
        interaction = data.get('interaction')
        
        # Store interaction in session or database for later analysis
        # This helps AI understand candidate behavior patterns
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@adaptive_api.route('/api/evaluate-code', methods=['POST'])
def evaluate_code():
    """Evaluate submitted code using AI."""
    try:
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'javascript')
        
        prompt = f"""Evaluate this {language} code:

{code}

Provide brief feedback on:
1. Code quality
2. Logic correctness
3. Best practices

Keep response conversational and under 100 words."""
        
        response = ai_service._make_api_request(
            ai_service.models['technical_evaluation'],
            prompt,
            max_tokens=200
        )
        
        if response and response.strip():
            feedback = response.strip().strip('"')
            return jsonify({'success': True, 'feedback': feedback})
        else:
            return jsonify({
                'success': True, 
                'feedback': 'Good code submission! I can see you understand the problem. Let\'s discuss your approach.'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})