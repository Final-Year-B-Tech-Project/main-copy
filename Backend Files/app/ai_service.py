import json
import requests
from flask import current_app
from typing import List, Dict, Any, Optional

class AIInterviewService:
    """Service for AI-powered interview functionality using OpenRouter AI."""
    
    def __init__(self):
        self.api_key = None
        self.base_url = None
        self.models = {
            'question_generation': 'x-ai/grok-4-fast:free',
            'feedback_analysis': 'deepseek/deepseek-chat-v3.1:free',
            'technical_evaluation': 'openai/gpt-oss-120b:free',
            'behavioral_analysis': 'nvidia/nemotron-nano-9b-v2:free'
        }
        # Fallback models if primary fails
        self.fallback_models = {
            'question_generation': ['google/gemini-2.0-flash-exp:free', 'meta-llama/llama-3.2-3b-instruct:free'],
            'feedback_analysis': ['google/gemini-2.0-flash-exp:free', 'meta-llama/llama-3.2-3b-instruct:free'],
            'technical_evaluation': ['google/gemini-2.0-flash-exp:free', 'meta-llama/llama-3.2-3b-instruct:free'],
            'behavioral_analysis': ['google/gemini-2.0-flash-exp:free', 'meta-llama/llama-3.2-3b-instruct:free']
        }
        # Simple service without adaptive manager
    
    def _ensure_initialized(self):
        """Ensure the service is initialized with Flask context."""
        if self.api_key is None:
            try:
                self.api_key = current_app.config.get('OPENROUTER_API_KEY')
                self.base_url = current_app.config.get('OPENROUTER_BASE_URL')
                
                if self.api_key and self.api_key != 'your-actual-api-key-here':
                    print(f"OpenRouter service initialized successfully")
                else:
                    print("WARNING: OpenRouter API key not configured properly")
                    print("Please update OPENROUTER_API_KEY in your .env file")
            except Exception as e:
                print(f"Error initializing OpenRouter service: {e}")
    
    def _make_api_request(self, model: str, prompt: str, max_tokens: int = 2000) -> str:
        """Make API request to OpenRouter with automatic fallback."""
        self._ensure_initialized()
        
        if not self.api_key or not self.base_url or self.api_key == 'your-actual-api-key-here':
            print("OpenRouter API not configured, using fallback")
            return ""
        
        # Try primary model
        result = self._try_model(model, prompt, max_tokens)
        if result:
            return result
        
        # Try fallback models
        model_type = self._get_model_type(model)
        if model_type and model_type in self.fallback_models:
            print(f"Primary model failed, trying fallbacks for {model_type}")
            for fallback in self.fallback_models[model_type]:
                print(f"Trying fallback model: {fallback}")
                result = self._try_model(fallback, prompt, max_tokens)
                if result:
                    return result
        
        print("All models failed, returning empty")
        return ""
    
    def _try_model(self, model: str, prompt: str, max_tokens: int) -> str:
        """Try a single model."""
        try:
            print(f"Trying model: {model}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "AI Interview Agent"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"✓ Success with {model}: {len(content)} chars")
                return content
            else:
                print(f"✗ Failed {model}: {response.status_code}")
                return ""
        except Exception as e:
            print(f"✗ Exception with {model}: {e}")
            return ""
    
    def _get_model_type(self, model: str) -> str:
        """Get model type from model string."""
        for model_type, model_name in self.models.items():
            if model_name == model:
                return model_type
        return ""
    
    def get_interview_summary(self) -> Dict:
        """Get basic interview summary"""
        return {
            'total_questions': 5,
            'duration_minutes': 10,
            'performance_metrics': {'answer_quality': [7, 6, 8, 7, 6]}
        }
    
    def generate_adaptive_question(self, 
                                 job_role: str,
                                 previous_questions: List[Dict],
                                 previous_answers: Dict,
                                 student_profile: Optional[Any] = None) -> Dict:
        """Generate next adaptive question based on previous responses."""
        
        self._ensure_initialized()
        
        try:
            # Analyze previous performance
            performance_analysis = self._analyze_previous_performance(previous_questions, previous_answers)
            
            prompt = f"""You are a professional technical interviewer conducting an adaptive interview for {job_role}.

Job Role: {job_role}
Previous Questions Asked: {len(previous_questions)}

Performance Analysis:
{json.dumps(performance_analysis, indent=2)}

Previous Q&A:
{json.dumps(self._prepare_conversation_for_analysis(previous_questions, previous_answers), indent=2)}

As a professional interviewer, generate the next question that:
1. Maintains professional interview standards
2. Adapts difficulty based on candidate performance
3. Explores new technical/behavioral areas
4. Builds naturally on previous responses
5. Tests job-relevant competencies
6. Uses proper interview techniques (STAR method for behavioral questions)

Avoid:
- Casual or chatbot-like language
- Generic questions
- Overly simple questions unless candidate is struggling
- Questions already covered

Return ONLY this JSON format:
{{
  "id": {len(previous_questions) + 1},
  "type": "technical/behavioral/situational",
  "question": "Professional interview question here",
  "category": "category_name",
  "difficulty": "easy/medium/hard",
  "time_limit": 300,
  "reasoning": "Professional rationale for this question"
}}"""
            
            response = self._make_api_request(self.models['question_generation'], prompt)
            question = self._parse_json_response(response)
            
            if question and 'question' in question:
                return self._validate_single_question(question, len(previous_questions) + 1)
            
            # Fallback adaptive question
            return self._generate_fallback_adaptive_question(job_role, previous_questions, previous_answers)
            
        except Exception as e:
            print(f"Error generating adaptive question: {e}")
            return self._generate_fallback_adaptive_question(job_role, previous_questions, previous_answers)
    
    def generate_interview_questions(self, 
                                   job_role: str, 
                                   difficulty: str = 'medium',
                                   experience_level: str = 'fresher',
                                   student_profile: Optional[Any] = None,
                                   num_questions: int = 10) -> List[Dict]:
        """Generate interview questions based on job role and other parameters."""
        
        # Ensure service is initialized
        self._ensure_initialized()
        
        try:
            # Build context for question generation
            context = self._build_question_context(job_role, difficulty, experience_level, student_profile)
            
            prompt = f"""You are a professional technical interviewer. Generate {num_questions} high-quality interview questions for {job_role} position.

{context}

Requirements:
- Questions must be professional and relevant to {job_role}
- Include technical depth appropriate for the role
- Mix behavioral (STAR method), technical, and situational questions
- Progress from easier to more challenging questions
- Focus on real-world scenarios and problem-solving
- Avoid generic questions like "tell me about yourself"

Create a JSON array with this exact format:
[
  {{"id": 1, "type": "technical", "question": "Explain your experience with [specific technology/concept relevant to {job_role}]", "category": "technical_skills", "difficulty": "medium", "time_limit": 300}},
  {{"id": 2, "type": "behavioral", "question": "Describe a time when you had to solve a complex problem under pressure", "category": "problem_solving", "difficulty": "medium", "time_limit": 360}}
]

Return ONLY the JSON array, nothing else."""
            
            print(f"Generating questions for {job_role} - {difficulty} level")
            response = self._make_api_request(self.models['question_generation'], prompt)
            
            if response and response.strip():
                print(f"Got API response, parsing...")
                questions = self._parse_questions_response(response)
                print(f"Parsed {len(questions)} questions from API")
                
                if questions:
                    validated_questions = self._validate_questions(questions, num_questions)
                    print(f"Validated {len(validated_questions)} questions")
                    
                    if len(validated_questions) >= num_questions:
                        return validated_questions
            
            # Fallback to default questions if API fails
            print("Using fallback questions - API returned no valid questions")
            print("To fix this: Get a real OpenRouter API key from https://openrouter.ai/")
            return self._get_fallback_questions(job_role, difficulty, num_questions)
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_fallback_questions(job_role, difficulty, num_questions)
    
    def generate_feedback(self, 
                         questions: List[Dict],
                         responses: Dict,
                         session: Any) -> Dict:
        """Generate comprehensive feedback for the interview with full conversation history."""
        
        # Ensure service is initialized
        self._ensure_initialized()
        
        try:
            # Prepare FULL conversation for analysis with all Q&A pairs
            conversation = self._prepare_full_conversation_history(questions, responses)
            
            # Calculate response quality metrics
            answered_count = len([r for r in responses.values() if r.get('answer', '').strip()])
            avg_response_length = sum([len(r.get('answer', '')) for r in responses.values()]) / max(answered_count, 1)
            
            # Calculate dynamic base scores based on actual performance
            response_quality_score = min(100, int((answered_count / len(questions)) * 100)) if questions else 50
            length_quality = min(100, int((avg_response_length / 50) * 100))  # 50+ chars = good
            base_score = int((response_quality_score + length_quality) / 2)
            
            prompt = f"""You are a senior technical interviewer providing professional feedback based on the COMPLETE interview conversation.

Interview Details:
- Session Type: {session.session_type}
- Job Role: {session.job_drive.job_role if session.job_drive else 'Practice Interview'}
- Duration: {session.duration} seconds
- Total Questions: {len(questions)}
- Answered Questions: {answered_count}
- Average Response Length: {int(avg_response_length)} characters
- Calculated Base Performance: {base_score}/100

COMPLETE INTERVIEW CONVERSATION (Analyze ALL questions and answers):
{json.dumps(conversation, indent=2, ensure_ascii=False)}

SCORING GUIDELINES:
- Base your scores on ACTUAL answer quality, not generic assumptions
- Short answers ("hello") should score 20-40
- Medium quality answers should score 60-75
- Detailed, thoughtful answers should score 80-95
- Exceptional answers with examples should score 95-100
- Use the calculated base score ({base_score}) as a starting reference

Provide comprehensive, actionable feedback in this EXACT JSON format:
{{
  "overall_score": {base_score},
  "technical_score": {max(base_score - 10, 40)},
  "communication_score": {min(base_score + 10, 95)},
  "confidence_score": {base_score},
  "problem_solving_score": {base_score},
  "leadership_score": {max(base_score - 15, 35)},
  "adaptability_score": {base_score},
  "strengths": ["Specific strength with evidence from answers", "Another concrete strength"],
  "weaknesses": ["Specific area for improvement based on responses", "Another development area"],
  "improvement_areas": ["Actionable improvement suggestion", "Specific skill to develop"],
  "detailed_analysis": {{
    "communication": "Assessment based on actual answer clarity and structure",
    "technical_skills": "Evaluation based on technical depth shown in answers",
    "problem_solving": "Analysis based on problem-solving approach demonstrated",
    "cultural_fit": "Assessment based on professionalism and attitude shown"
  }},
  "recommendations": ["Specific recommendation based on performance", "Concrete next step"],
  "summary": "Professional summary based on actual interview performance",
  "next_steps": "Development plan based on identified gaps"
}}

Evaluate professionally based on ACTUAL responses:
1. Answer completeness and depth
2. Communication clarity and structure
3. Technical knowledge demonstrated
4. Problem-solving approach shown
5. Professional presentation
6. Specific examples provided
7. Relevance to questions asked
8. Overall engagement level

Be FAIR and ACCURATE. Reward good answers with high scores (85-95). Penalize weak answers with low scores (30-50). Return ONLY valid JSON."""
            
            response = self._make_api_request(self.models['feedback_analysis'], prompt, max_tokens=2500)
            feedback = self._parse_json_response(response)
            
            # Validate and enhance feedback structure
            return self._validate_comprehensive_feedback(feedback)
            
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return self._get_comprehensive_fallback_feedback()
    
    def analyze_answer_quality(self, question: str, answer: str) -> Dict:
        """Analyze the quality of a single answer."""
        
        # Ensure service is initialized
        self._ensure_initialized()
        
        try:
            prompt = f"""Analyze this interview answer and provide a quick assessment.

Question: {question}
Answer: {answer}

Return ONLY this JSON format:
{{
  "score": 7,
  "quick_feedback": "Brief feedback message"
}}"""
            
            response = self._make_api_request(self.models['technical_evaluation'], prompt, max_tokens=500)
            return self._parse_json_response(response)
            
        except Exception as e:
            return {"score": 5, "quick_feedback": "Answer analyzed"}
    
    def _build_question_context(self, job_role, difficulty, experience_level, student_profile):
        """Build context for question generation."""
        context = f"Job Role: {job_role}\n"
        context += f"Difficulty: {difficulty}\n"
        context += f"Experience Level: {experience_level}\n"
        
        if student_profile:
            if hasattr(student_profile, 'skills') and student_profile.skills:
                try:
                    skills = json.loads(student_profile.skills)
                    context += f"Candidate Skills: {', '.join(skills)}\n"
                except:
                    pass
            
            if hasattr(student_profile, 'degree') and student_profile.degree:
                context += f"Educational Background: {student_profile.degree}\n"
        
        return context
    
    def _parse_questions_response(self, response_text: str) -> List[Dict]:
        """Parse the AI response to extract questions."""
        try:
            # Clean the response text
            clean_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]
            if clean_text.startswith('```'):
                clean_text = clean_text[3:]
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]
            
            # Find JSON array in the text
            start_idx = clean_text.find('[')
            end_idx = clean_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_text = clean_text[start_idx:end_idx]
                questions = json.loads(json_text)
                return questions if isinstance(questions, list) else []
            
            # Try parsing the entire text as JSON
            questions = json.loads(clean_text)
            if isinstance(questions, dict) and 'questions' in questions:
                questions = questions['questions']
            
            return questions if isinstance(questions, list) else []
            
        except Exception as e:
            print(f"Error parsing questions response: {e}")
            print(f"Raw response was: {response_text[:200]}...")
            return []
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON response from AI."""
        try:
            clean_text = response_text.strip()
            
            # Remove markdown code blocks
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]
            if clean_text.startswith('```'):
                clean_text = clean_text[3:]
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]
            
            # Find JSON object in the text
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_text = clean_text[start_idx:end_idx]
                return json.loads(json_text)
            
            return json.loads(clean_text)
            
        except Exception as e:
            print(f"Error parsing JSON response: {e}")
            return {}
    
    def _validate_questions(self, questions: List[Dict], target_count: int) -> List[Dict]:
        """Validate and ensure we have the right number of questions."""
        validated = []
        
        for i, q in enumerate(questions[:target_count]):
            validated_q = {
                'id': q.get('id', i + 1),
                'type': q.get('type', 'technical'),
                'question': q.get('question', f'Sample question {i + 1}'),
                'category': q.get('category', 'general'),
                'difficulty': q.get('difficulty', 'medium'),
                'time_limit': q.get('time_limit', 300)
            }
            validated.append(validated_q)
        
        # If we don't have enough questions, add fallback ones
        while len(validated) < target_count:
            validated.append(self._create_fallback_question(len(validated) + 1))
        
        return validated
    
    def _validate_feedback(self, feedback: Dict) -> Dict:
        """Validate feedback structure and provide defaults."""
        return {
            'overall_score': feedback.get('overall_score', 75),
            'technical_score': feedback.get('technical_score', 70),
            'communication_score': feedback.get('communication_score', 80),
            'confidence_score': feedback.get('confidence_score', 75),
            'coding_score': feedback.get('coding_score', 70),
            'strengths': feedback.get('strengths', ['Good communication', 'Shows enthusiasm']),
            'weaknesses': feedback.get('weaknesses', ['Could be more specific', 'Practice more examples']),
            'summary': feedback.get('summary', 'Good overall performance with room for improvement.')
        }
    
    def _get_fallback_questions(self, job_role: str, difficulty: str, num_questions: int) -> List[Dict]:
        """Get professional interview questions when AI is not available."""
        
        # Professional technical questions based on job role
        if 'software' in job_role.lower() or 'developer' in job_role.lower() or 'engineer' in job_role.lower():
            base_questions = [
                {"id": 1, "type": "behavioral", "question": "Walk me through your background and experience in software development.", "category": "introduction", "difficulty": "easy", "time_limit": 300},
                {"id": 2, "type": "technical", "question": "Explain the difference between object-oriented and functional programming paradigms.", "category": "programming_concepts", "difficulty": "medium", "time_limit": 300},
                {"id": 3, "type": "technical", "question": "How would you optimize a slow-performing database query?", "category": "database_optimization", "difficulty": "medium", "time_limit": 360},
                {"id": 4, "type": "technical", "question": "Describe the software development lifecycle and your experience with different methodologies.", "category": "sdlc", "difficulty": "medium", "time_limit": 300},
                {"id": 5, "type": "technical", "question": "How do you handle version control and code collaboration in team projects?", "category": "version_control", "difficulty": "medium", "time_limit": 300},
                {"id": 6, "type": "technical", "question": "Explain REST APIs and how you would design a scalable API architecture.", "category": "api_design", "difficulty": "hard", "time_limit": 360},
                {"id": 7, "type": "situational", "question": "How would you approach debugging a production issue that you cannot reproduce locally?", "category": "problem_solving", "difficulty": "hard", "time_limit": 300},
                {"id": 8, "type": "technical", "question": "What are your thoughts on code testing strategies and test-driven development?", "category": "testing", "difficulty": "medium", "time_limit": 300},
                {"id": 9, "type": "technical", "question": "How do you ensure code quality and maintainability in large projects?", "category": "code_quality", "difficulty": "medium", "time_limit": 300},
                {"id": 10, "type": "behavioral", "question": "Describe a complex technical challenge you solved and the impact it had.", "category": "technical_achievement", "difficulty": "medium", "time_limit": 360}
            ]
        elif 'data' in job_role.lower() or 'analyst' in job_role.lower():
            base_questions = [
                {"id": 1, "type": "behavioral", "question": "Tell me about your experience with data analysis and what drew you to this field.", "category": "introduction", "difficulty": "easy", "time_limit": 300},
                {"id": 2, "type": "technical", "question": "Explain the difference between supervised and unsupervised machine learning.", "category": "ml_concepts", "difficulty": "medium", "time_limit": 300},
                {"id": 3, "type": "technical", "question": "How would you handle missing data in a large dataset?", "category": "data_preprocessing", "difficulty": "medium", "time_limit": 300},
                {"id": 4, "type": "technical", "question": "Walk me through your process for exploratory data analysis.", "category": "data_exploration", "difficulty": "medium", "time_limit": 360},
                {"id": 5, "type": "technical", "question": "How do you validate the accuracy of your analytical models?", "category": "model_validation", "difficulty": "medium", "time_limit": 300},
                {"id": 6, "type": "technical", "question": "Explain A/B testing and how you would design an experiment.", "category": "experimentation", "difficulty": "hard", "time_limit": 360},
                {"id": 7, "type": "situational", "question": "How would you communicate complex analytical findings to non-technical stakeholders?", "category": "communication", "difficulty": "medium", "time_limit": 300},
                {"id": 8, "type": "technical", "question": "What tools and technologies do you use for data visualization and why?", "category": "visualization", "difficulty": "medium", "time_limit": 300},
                {"id": 9, "type": "technical", "question": "How do you ensure data quality and integrity in your analysis?", "category": "data_quality", "difficulty": "medium", "time_limit": 300},
                {"id": 10, "type": "behavioral", "question": "Describe a time when your analysis led to a significant business decision.", "category": "business_impact", "difficulty": "medium", "time_limit": 360}
            ]
        else:
            # Generic professional questions
            base_questions = [
                {"id": 1, "type": "behavioral", "question": "Walk me through your professional background and key achievements.", "category": "introduction", "difficulty": "easy", "time_limit": 300},
                {"id": 2, "type": "technical", "question": f"What specific skills and experience do you bring to the {job_role} position?", "category": "relevant_skills", "difficulty": "medium", "time_limit": 300},
                {"id": 3, "type": "situational", "question": "Describe a challenging project you led and how you ensured its success.", "category": "leadership", "difficulty": "medium", "time_limit": 360},
                {"id": 4, "type": "behavioral", "question": "How do you prioritize tasks when managing multiple competing deadlines?", "category": "time_management", "difficulty": "medium", "time_limit": 300},
                {"id": 5, "type": "situational", "question": "Tell me about a time you had to adapt to significant changes in your work environment.", "category": "adaptability", "difficulty": "medium", "time_limit": 300},
                {"id": 6, "type": "behavioral", "question": "Describe your approach to continuous learning and professional development.", "category": "growth_mindset", "difficulty": "medium", "time_limit": 300},
                {"id": 7, "type": "situational", "question": "How would you handle a situation where you disagreed with your manager's approach?", "category": "conflict_resolution", "difficulty": "hard", "time_limit": 300},
                {"id": 8, "type": "behavioral", "question": "What motivates you in your work and how do you maintain high performance?", "category": "motivation", "difficulty": "medium", "time_limit": 300},
                {"id": 9, "type": "technical", "question": "How do you stay current with industry trends and best practices?", "category": "industry_knowledge", "difficulty": "medium", "time_limit": 300},
                {"id": 10, "type": "behavioral", "question": "Why are you interested in this role and what value would you bring to our team?", "category": "role_fit", "difficulty": "medium", "time_limit": 300}
            ]
        
        return base_questions[:num_questions]
    
    def _create_fallback_question(self, question_id: int) -> Dict:
        """Create a fallback question."""
        return {
            "id": question_id,
            "type": "behavioral",
            "question": f"Tell me about a time when you faced a challenge and how you overcame it.",
            "category": "problem_solving",
            "difficulty": "medium",
            "time_limit": 300
        }
    
    def _validate_comprehensive_feedback(self, feedback: Dict) -> Dict:
        """Validate comprehensive feedback structure with dynamic defaults."""
        # Ensure scores are reasonable integers
        overall = int(feedback.get('overall_score', 70))
        overall = max(20, min(100, overall))  # Clamp between 20-100
        
        return {
            'overall_score': overall,
            'technical_score': int(feedback.get('technical_score', max(overall - 5, 40))),
            'communication_score': int(feedback.get('communication_score', min(overall + 5, 95))),
            'confidence_score': int(feedback.get('confidence_score', overall)),
            'problem_solving_score': int(feedback.get('problem_solving_score', overall)),
            'leadership_score': int(feedback.get('leadership_score', max(overall - 10, 35))),
            'adaptability_score': int(feedback.get('adaptability_score', overall)),
            'strengths': feedback.get('strengths', ['Completed the interview', 'Showed engagement']),
            'weaknesses': feedback.get('weaknesses', ['Provide more detailed responses', 'Include specific examples']),
            'improvement_areas': feedback.get('improvement_areas', ['Practice STAR method', 'Prepare specific examples']),
            'detailed_analysis': feedback.get('detailed_analysis', {
                'communication': 'Responses provided with varying levels of detail',
                'technical_skills': 'Technical knowledge demonstrated at basic level',
                'problem_solving': 'Problem-solving approach needs more structure',
                'cultural_fit': 'Shows willingness to engage and learn'
            }),
            'recommendations': feedback.get('recommendations', ['Practice with more examples', 'Study technical concepts']),
            'summary': feedback.get('summary', f'Performance score of {overall}/100 indicates areas for growth and development.'),
            'next_steps': feedback.get('next_steps', 'Focus on providing detailed, structured responses with specific examples.')
        }
    
    def _get_comprehensive_fallback_feedback(self) -> Dict:
        """Get comprehensive fallback feedback when AI is not available."""
        return {
            "overall_score": 70,
            "technical_score": 65,
            "communication_score": 75,
            "confidence_score": 70,
            "problem_solving_score": 68,
            "leadership_score": 60,
            "adaptability_score": 72,
            "strengths": ["Completed all interview questions", "Maintained engagement throughout", "Showed willingness to participate"],
            "weaknesses": ["Responses could be more detailed", "Include more specific examples", "Demonstrate deeper technical knowledge"],
            "improvement_areas": ["Practice STAR method (Situation, Task, Action, Result)", "Prepare specific examples from experience", "Study technical concepts in depth"],
            "detailed_analysis": {
                "communication": "Basic communication established. Work on structuring responses more clearly.",
                "technical_skills": "Technical knowledge shown at foundational level. Deepen expertise in key areas.",
                "problem_solving": "Problem-solving approach needs more structure and specific examples.",
                "cultural_fit": "Shows positive attitude and willingness to learn."
            },
            "recommendations": ["Practice answering common interview questions", "Prepare 5-7 detailed examples using STAR method", "Research company and role thoroughly"],
            "summary": "Interview completed with room for improvement. Focus on providing detailed, structured responses with concrete examples from your experience.",
            "next_steps": "Practice interview skills daily, prepare specific examples, and strengthen technical knowledge in your field."
        }
    
    def _analyze_previous_performance(self, questions: List[Dict], answers: Dict) -> Dict:
        """Analyze previous performance to guide next question."""
        if not questions or not answers:
            return {'performance_level': 'unknown', 'areas_covered': [], 'suggested_difficulty': 'medium'}
        
        # Simple performance analysis
        answered_count = len([a for a in answers.values() if a.get('answer', '').strip()])
        performance_ratio = answered_count / len(questions) if questions else 0
        
        areas_covered = list(set([q.get('category', 'general') for q in questions]))
        
        if performance_ratio > 0.8:
            suggested_difficulty = 'hard'
            performance_level = 'excellent'
        elif performance_ratio > 0.6:
            suggested_difficulty = 'medium'
            performance_level = 'good'
        else:
            suggested_difficulty = 'easy'
            performance_level = 'needs_support'
        
        return {
            'performance_level': performance_level,
            'areas_covered': areas_covered,
            'suggested_difficulty': suggested_difficulty,
            'answered_ratio': performance_ratio
        }
    
    def _validate_single_question(self, question: Dict, question_id: int) -> Dict:
        """Validate a single question structure."""
        return {
            'id': question.get('id', question_id),
            'type': question.get('type', 'behavioral'),
            'question': question.get('question', 'Tell me about a challenge you faced.'),
            'category': question.get('category', 'general'),
            'difficulty': question.get('difficulty', 'medium'),
            'time_limit': question.get('time_limit', 300),
            'reasoning': question.get('reasoning', 'Adaptive question based on performance')
        }
    
    def _generate_fallback_adaptive_question(self, job_role: str, previous_questions: List[Dict], previous_answers: Dict) -> Dict:
        """Generate fallback adaptive question."""
        question_id = len(previous_questions) + 1
        
        # Simple adaptive logic
        areas_covered = [q.get('category', 'general') for q in previous_questions]
        
        if 'technical' not in areas_covered:
            return {
                'id': question_id,
                'type': 'technical',
                'question': f'What technical skills do you have that are relevant to {job_role}?',
                'category': 'technical',
                'difficulty': 'medium',
                'time_limit': 300,
                'reasoning': 'Exploring technical competency'
            }
        elif 'problem_solving' not in areas_covered:
            return {
                'id': question_id,
                'type': 'situational',
                'question': 'Describe a complex problem you solved and your approach.',
                'category': 'problem_solving',
                'difficulty': 'medium',
                'time_limit': 360,
                'reasoning': 'Assessing problem-solving skills'
            }
        else:
            return {
                'id': question_id,
                'type': 'behavioral',
                'question': 'How do you handle feedback and criticism?',
                'category': 'adaptability',
                'difficulty': 'medium',
                'time_limit': 300,
                'reasoning': 'Understanding adaptability and growth mindset'
            }
    
    def _get_fallback_feedback(self) -> Dict:
        """Get fallback feedback when AI is not available."""
        return self._get_comprehensive_fallback_feedback()
    
    def _prepare_conversation_for_analysis(self, questions: List[Dict], responses: Dict) -> List[Dict]:
        """Prepare conversation data for AI analysis."""
        return self._prepare_full_conversation_history(questions, responses)
    
    def _prepare_full_conversation_history(self, questions: List[Dict], responses: Dict) -> List[Dict]:
        """Prepare COMPLETE conversation history with all details for comprehensive analysis."""
        conversation = []
        
        for i, question in enumerate(questions):
            if isinstance(question, str):
                q_text = question
                q_type = 'general'
                q_category = 'general'
                q_difficulty = 'medium'
                q_id = str(i + 1)
            else:
                q_text = question.get('question', f'Question {i + 1}')
                q_type = question.get('type', 'general')
                q_category = question.get('category', 'general')
                q_difficulty = question.get('difficulty', 'medium')
                q_id = str(question.get('id', i + 1))
            
            response_data = responses.get(q_id, {})
            if isinstance(response_data, str):
                answer = response_data
                response_time = 0
            else:
                answer = response_data.get('answer', 'No response provided')
                response_time = response_data.get('time_taken', 0)
            
            # Include full context for each Q&A pair
            conversation.append({
                "question_number": i + 1,
                "question": q_text,
                "type": q_type,
                "category": q_category,
                "difficulty": q_difficulty,
                "answer": answer,
                "answer_length": len(answer),
                "response_time_seconds": response_time,
                "answered": bool(answer and answer.strip() and answer != 'No response provided')
            })
        
        return conversation