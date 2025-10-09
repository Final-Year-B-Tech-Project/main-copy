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
            'question_generation': 'x-ai/grok-4-fast:free',        # Best for creative question generation
            'feedback_analysis': 'deepseek/deepseek-chat-v3.1:free', # Best for detailed analysis
            'technical_evaluation': 'openai/gpt-oss-120b:free',    # Best for technical assessment
            'behavioral_analysis': 'nvidia/nemotron-nano-9b-v2:free' # Good for behavioral insights
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
        """Make API request to OpenRouter."""
        # Ensure service is initialized
        self._ensure_initialized()
        
        if not self.api_key or not self.base_url or self.api_key == 'your-actual-api-key-here':
            print("OpenRouter API not configured properly, using fallback")
            print(f"API Key present: {bool(self.api_key)}")
            print(f"API Key valid: {self.api_key != 'your-actual-api-key-here' if self.api_key else False}")
            return ""
        
        print(f"Making API request to model: {model}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "AI Interview Agent"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            print(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"API Response received: {len(content)} characters")
                return content
            else:
                print(f"API request failed: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            print(f"API request exception: {e}")
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
                # Parse response
                questions = self._parse_questions_response(response)
                print(f"Parsed {len(questions)} questions from API")
                
                if questions:
                    # Validate and clean questions
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
        """Generate comprehensive feedback for the interview."""
        
        # Ensure service is initialized
        self._ensure_initialized()
        
        try:
            # Prepare conversation for analysis
            conversation = self._prepare_conversation_for_analysis(questions, responses)
            
            prompt = f"""You are a senior technical interviewer providing professional feedback.

Interview Details:
- Session Type: {session.session_type}
- Job Role: {session.job_drive.job_role if session.job_drive else 'Practice Interview'}
- Duration: {session.duration} seconds
- Total Questions: {len(questions)}
- Answered Questions: {len([r for r in responses.values() if r.get('answer', '').strip()])}

Conversation Analysis:
{json.dumps(conversation, indent=2)}

As a professional interviewer, provide comprehensive, actionable feedback in this EXACT JSON format:
{{
  "overall_score": 75,
  "technical_score": 70,
  "communication_score": 80,
  "confidence_score": 75,
  "problem_solving_score": 70,
  "leadership_score": 65,
  "adaptability_score": 75,
  "strengths": ["Specific strength with evidence", "Another concrete strength"],
  "weaknesses": ["Specific area for improvement", "Another development area"],
  "improvement_areas": ["Actionable improvement suggestion", "Specific skill to develop"],
  "detailed_analysis": {{
    "communication": "Professional assessment of communication skills with examples",
    "technical_skills": "Detailed technical competency evaluation with specifics",
    "problem_solving": "Analysis of problem-solving approach and methodology",
    "cultural_fit": "Assessment of cultural alignment and team fit"
  }},
  "recommendations": ["Specific, actionable recommendation", "Concrete next step"],
  "summary": "Professional summary highlighting key performance indicators and growth areas",
  "next_steps": "Clear, actionable development plan for candidate improvement"
}}

Evaluate professionally:
1. Technical competency depth and accuracy
2. Communication clarity and structure (STAR method usage)
3. Problem-solving methodology and critical thinking
4. Professional presentation and confidence
5. Adaptability and learning orientation
6. Leadership potential and team collaboration
7. Industry knowledge and best practices awareness
8. Cultural fit and professional maturity

Provide specific, evidence-based feedback. Avoid generic comments. Return ONLY valid JSON."""
            
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
        """Validate comprehensive feedback structure."""
        return {
            'overall_score': feedback.get('overall_score', 75),
            'technical_score': feedback.get('technical_score', 70),
            'communication_score': feedback.get('communication_score', 80),
            'confidence_score': feedback.get('confidence_score', 75),
            'problem_solving_score': feedback.get('problem_solving_score', 70),
            'leadership_score': feedback.get('leadership_score', 65),
            'adaptability_score': feedback.get('adaptability_score', 75),
            'strengths': feedback.get('strengths', ['Good communication', 'Shows enthusiasm']),
            'weaknesses': feedback.get('weaknesses', ['Could be more specific', 'Practice more examples']),
            'improvement_areas': feedback.get('improvement_areas', ['Practice STAR method', 'Study technical concepts']),
            'detailed_analysis': feedback.get('detailed_analysis', {
                'communication': 'Clear and articulate responses',
                'technical_skills': 'Solid foundation with room for growth',
                'problem_solving': 'Good analytical approach',
                'cultural_fit': 'Shows good alignment with team values'
            }),
            'recommendations': feedback.get('recommendations', ['Continue practicing', 'Focus on technical depth']),
            'summary': feedback.get('summary', 'Good overall performance with clear areas for improvement.'),
            'next_steps': feedback.get('next_steps', 'Focus on technical skills and provide more specific examples.')
        }
    
    def _get_comprehensive_fallback_feedback(self) -> Dict:
        """Get comprehensive fallback feedback when AI is not available."""
        return {
            "overall_score": 75,
            "technical_score": 70,
            "communication_score": 80,
            "confidence_score": 75,
            "problem_solving_score": 70,
            "leadership_score": 65,
            "adaptability_score": 75,
            "strengths": ["Clear communication skills", "Shows enthusiasm for the role", "Good problem-solving approach"],
            "weaknesses": ["Could provide more specific examples", "Technical knowledge needs strengthening", "Leadership experience limited"],
            "improvement_areas": ["Practice STAR method for behavioral questions", "Deepen technical knowledge", "Gain more leadership experience"],
            "detailed_analysis": {
                "communication": "Demonstrates clear and articulate communication throughout the interview",
                "technical_skills": "Shows solid foundation but could benefit from deeper technical knowledge",
                "problem_solving": "Good analytical thinking and structured approach to problems",
                "cultural_fit": "Shows good alignment with team values and company culture"
            },
            "recommendations": ["Continue practicing interview skills", "Focus on technical depth in your field", "Prepare more specific examples using STAR method"],
            "summary": "Good overall performance with strong communication skills. Focus on strengthening technical knowledge and providing more specific examples.",
            "next_steps": "Practice technical concepts, prepare specific examples, and continue developing leadership skills."
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
        conversation = []
        
        for i, question in enumerate(questions):
            if isinstance(question, str):
                q_text = question
                q_type = 'general'
                q_category = 'general'
                q_id = str(i + 1)
            else:
                q_text = question.get('question', f'Question {i + 1}')
                q_type = question.get('type', 'general')
                q_category = question.get('category', 'general')
                q_id = str(question.get('id', i + 1))
            
            response_data = responses.get(q_id, {})
            if isinstance(response_data, str):
                answer = response_data
            else:
                answer = response_data.get('answer', 'No response')
            
            conversation.append({
                "question": q_text,
                "type": q_type,
                "category": q_category,
                "answer": answer
            })
        
        return conversation