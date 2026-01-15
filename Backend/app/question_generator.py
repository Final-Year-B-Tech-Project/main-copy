import json
import random
from typing import List, Dict
from app.resume_models import CandidateSkill

class SkillBasedQuestionGenerator:
    """Generate interview questions based on candidate's extracted skills"""
    
    def __init__(self):
        self.question_bank = {
            # Programming Languages
            'python': {
                'beginner': [
                    "What are the key differences between Python 2 and Python 3?",
                    "Explain the concept of list comprehensions in Python with an example.",
                    "What is the difference between a list and a tuple in Python?",
                    "How do you handle exceptions in Python?",
                    "What are Python decorators and how do you use them?"
                ],
                'intermediate': [
                    "Explain the Global Interpreter Lock (GIL) in Python and its implications.",
                    "What are generators in Python and how do they differ from regular functions?",
                    "Implement a function to find the second largest number in a list using Python.",
                    "Explain the concept of metaclasses in Python.",
                    "How would you optimize a slow Python script?"
                ],
                'expert': [
                    "Design a Python decorator that can cache function results with TTL support.",
                    "Explain Python's memory management and garbage collection mechanism.",
                    "How would you implement a thread-safe singleton pattern in Python?",
                    "Discuss the performance implications of different Python data structures.",
                    "Design a Python library for handling large datasets efficiently."
                ]
            },
            
            'javascript': {
                'beginner': [
                    "What is the difference between var, let, and const in JavaScript?",
                    "Explain event bubbling and event capturing in JavaScript.",
                    "What are closures in JavaScript? Provide an example.",
                    "How do you handle asynchronous operations in JavaScript?",
                    "What is the difference between == and === in JavaScript?"
                ],
                'intermediate': [
                    "Explain the concept of prototypal inheritance in JavaScript.",
                    "What are Promises and how do they work?",
                    "Implement a debounce function in JavaScript.",
                    "Explain the event loop in JavaScript.",
                    "What are the differences between arrow functions and regular functions?"
                ],
                'expert': [
                    "Design a JavaScript module system from scratch.",
                    "Explain how JavaScript engines optimize code execution.",
                    "Implement a custom Promise library with all standard methods.",
                    "How would you handle memory leaks in a large JavaScript application?",
                    "Design a reactive programming system in JavaScript."
                ]
            },
            
            'react': {
                'beginner': [
                    "What is JSX and how does it work in React?",
                    "Explain the difference between functional and class components.",
                    "What are props in React and how do you use them?",
                    "What is state in React and how do you manage it?",
                    "Explain the React component lifecycle methods."
                ],
                'intermediate': [
                    "What are React Hooks and why were they introduced?",
                    "Explain the useEffect hook and its use cases.",
                    "How do you optimize React component performance?",
                    "What is the Context API and when would you use it?",
                    "Explain the concept of controlled vs uncontrolled components."
                ],
                'expert': [
                    "Design a custom React hook for data fetching with caching.",
                    "How would you implement server-side rendering with React?",
                    "Explain React's reconciliation algorithm and virtual DOM.",
                    "Design a React component library with proper TypeScript support.",
                    "How would you handle state management in a large React application?"
                ]
            },
            
            'java': {
                'beginner': [
                    "What are the main principles of Object-Oriented Programming in Java?",
                    "Explain the difference between abstract classes and interfaces.",
                    "What is the difference between String, StringBuilder, and StringBuffer?",
                    "How does garbage collection work in Java?",
                    "What are the access modifiers in Java?"
                ],
                'intermediate': [
                    "Explain the concept of multithreading in Java.",
                    "What are Java Collections and which ones would you use when?",
                    "How do you handle exceptions in Java? Explain checked vs unchecked exceptions.",
                    "What is the difference between HashMap and ConcurrentHashMap?",
                    "Explain the concept of Java generics."
                ],
                'expert': [
                    "Design a thread-safe cache implementation in Java.",
                    "Explain the Java Memory Model and its implications.",
                    "How would you optimize Java application performance?",
                    "Design a custom annotation processor in Java.",
                    "Implement a producer-consumer pattern using Java concurrency utilities."
                ]
            },
            
            # Frameworks
            'django': {
                'beginner': [
                    "What is Django and what are its main components?",
                    "Explain the MVC pattern in Django.",
                    "What are Django models and how do you define them?",
                    "How do you create views in Django?",
                    "What is Django ORM and how does it work?"
                ],
                'intermediate': [
                    "How do you handle user authentication in Django?",
                    "Explain Django's middleware and how to create custom middleware.",
                    "What are Django signals and when would you use them?",
                    "How do you optimize Django database queries?",
                    "Explain Django's caching framework."
                ],
                'expert': [
                    "Design a scalable Django application architecture.",
                    "How would you implement custom user models in Django?",
                    "Explain Django's security features and best practices.",
                    "How would you handle file uploads and media management in Django?",
                    "Design a Django REST API with proper authentication and permissions."
                ]
            },
            
            # Databases
            'sql': {
                'beginner': [
                    "What are the different types of SQL joins?",
                    "Explain the difference between WHERE and HAVING clauses.",
                    "What are primary keys and foreign keys?",
                    "How do you create and modify tables in SQL?",
                    "What are SQL indexes and why are they important?"
                ],
                'intermediate': [
                    "Write a SQL query to find the second highest salary from an employee table.",
                    "Explain the concept of database normalization.",
                    "What are stored procedures and functions in SQL?",
                    "How do you handle transactions in SQL?",
                    "Explain the different types of SQL constraints."
                ],
                'expert': [
                    "Design a database schema for an e-commerce application.",
                    "How would you optimize slow SQL queries?",
                    "Explain database partitioning and sharding strategies.",
                    "Design a data warehouse schema using star or snowflake schema.",
                    "How would you handle database migrations in a production environment?"
                ]
            },
            
            # Cloud Technologies
            'aws': {
                'beginner': [
                    "What are the main AWS services and their use cases?",
                    "Explain the difference between EC2, ECS, and Lambda.",
                    "What is S3 and how do you use it for storage?",
                    "How do you set up a basic web application on AWS?",
                    "What are AWS security groups and how do they work?"
                ],
                'intermediate': [
                    "How do you implement auto-scaling in AWS?",
                    "Explain AWS VPC and its components.",
                    "What are the different AWS storage options and when to use each?",
                    "How do you monitor AWS resources and applications?",
                    "Explain AWS IAM and best practices for access management."
                ],
                'expert': [
                    "Design a highly available and scalable architecture on AWS.",
                    "How would you implement disaster recovery on AWS?",
                    "Explain AWS cost optimization strategies.",
                    "Design a CI/CD pipeline using AWS services.",
                    "How would you implement microservices architecture on AWS?"
                ]
            },
            
            # Tools
            'docker': {
                'beginner': [
                    "What is Docker and how does it differ from virtual machines?",
                    "Explain the concept of Docker containers and images.",
                    "How do you create a Dockerfile?",
                    "What are Docker volumes and why are they important?",
                    "How do you run and manage Docker containers?"
                ],
                'intermediate': [
                    "Explain Docker networking and different network types.",
                    "What is Docker Compose and how do you use it?",
                    "How do you optimize Docker images for production?",
                    "Explain Docker security best practices.",
                    "How do you handle persistent data in Docker containers?"
                ],
                'expert': [
                    "Design a multi-stage Docker build for a complex application.",
                    "How would you implement Docker container orchestration?",
                    "Explain Docker registry management and security.",
                    "Design a Docker-based CI/CD pipeline.",
                    "How would you monitor and troubleshoot Docker containers in production?"
                ]
            },
            
            # Soft Skills
            'leadership': [
                "Describe a time when you had to lead a team through a difficult project.",
                "How do you handle conflicts within your team?",
                "What strategies do you use to motivate team members?",
                "How do you delegate tasks effectively?",
                "Describe your approach to giving feedback to team members."
            ],
            
            'communication': [
                "How do you explain technical concepts to non-technical stakeholders?",
                "Describe a time when you had to present a complex solution to management.",
                "How do you handle disagreements with colleagues?",
                "What methods do you use to ensure clear communication in remote teams?",
                "How do you adapt your communication style for different audiences?"
            ],
            
            'problem solving': [
                "Walk me through your approach to solving a complex technical problem.",
                "Describe a time when you had to debug a critical production issue.",
                "How do you prioritize multiple competing problems?",
                "What tools and techniques do you use for root cause analysis?",
                "Describe a creative solution you implemented to solve a business problem."
            ]
        }
    
    def generate_questions_for_candidate(self, student_id: int, num_questions: int = 10) -> List[Dict]:
        """Generate personalized interview questions based on candidate's consolidated skills"""
        from app.models import StudentProfile
        
        # Get candidate's skills from student profile
        student_profile = StudentProfile.query.get(student_id)
        if not student_profile or not student_profile.skills:
            return self._get_default_questions(num_questions)
        
        # Parse skills from JSON
        candidate_skills_data = json.loads(student_profile.skills)
        
        questions = []
        
        # Group skills by category
        technical_skills = [s for s in candidate_skills_data if s['skill_category'] == 'technical']
        soft_skills = [s for s in candidate_skills_data if s['skill_category'] == 'soft']
        
        # Generate technical questions (70% of total)
        tech_question_count = int(num_questions * 0.7)
        questions.extend(self._generate_technical_questions_from_data(technical_skills, tech_question_count))
        
        # Generate soft skill questions (30% of total)
        soft_question_count = num_questions - len(questions)
        questions.extend(self._generate_soft_skill_questions_from_data(soft_skills, soft_question_count))
        
        # Fill remaining slots with general questions if needed
        while len(questions) < num_questions:
            questions.extend(self._get_default_questions(num_questions - len(questions)))
        
        return questions[:num_questions]
    
    def _generate_technical_questions_from_data(self, technical_skills: List[Dict], count: int) -> List[Dict]:
        """Generate technical questions from consolidated skill data"""
        questions = []
        
        # Sort skills by confidence score (prioritize high-confidence skills)
        sorted_skills = sorted(technical_skills, key=lambda x: x.get('confidence_score', 0), reverse=True)
        
        for skill_data in sorted_skills:
            if len(questions) >= count:
                break
                
            skill_name = skill_data['skill_name'].lower()
            proficiency = skill_data.get('proficiency_level', 'beginner')
            
            if skill_name in self.question_bank:
                skill_questions = self.question_bank[skill_name]
                
                if isinstance(skill_questions, dict) and proficiency in skill_questions:
                    # Technical skill with proficiency levels
                    available_questions = skill_questions[proficiency]
                    selected_question = random.choice(available_questions)
                    
                    questions.append({
                        'question': selected_question,
                        'skill': skill_data['skill_name'],
                        'category': 'technical',
                        'difficulty': proficiency,
                        'type': skill_data.get('skill_type', 'technical'),
                        'time_limit': self._get_time_limit(proficiency)
                    })
                elif isinstance(skill_questions, list):
                    # Simple skill list
                    selected_question = random.choice(skill_questions)
                    questions.append({
                        'question': selected_question,
                        'skill': skill_data['skill_name'],
                        'category': 'technical',
                        'difficulty': proficiency,
                        'type': skill_data.get('skill_type', 'technical'),
                        'time_limit': self._get_time_limit(proficiency)
                    })
        
        return questions
    
    def _generate_soft_skill_questions_from_data(self, soft_skills: List[Dict], count: int) -> List[Dict]:
        """Generate soft skill questions from consolidated skill data"""
        questions = []
        
        for skill_data in soft_skills:
            if len(questions) >= count:
                break
                
            skill_name = skill_data['skill_name'].lower()
            
            if skill_name in self.question_bank:
                available_questions = self.question_bank[skill_name]
                selected_question = random.choice(available_questions)
                
                questions.append({
                    'question': selected_question,
                    'skill': skill_data['skill_name'],
                    'category': 'behavioral',
                    'difficulty': 'general',
                    'type': 'soft_skill',
                    'time_limit': 300  # 5 minutes for behavioral questions
                })
        
        # Fill remaining with general soft skill questions
        general_soft_skills = ['leadership', 'communication', 'problem solving']
        while len(questions) < count:
            skill_name = random.choice(general_soft_skills)
            available_questions = self.question_bank[skill_name]
            selected_question = random.choice(available_questions)
            
            questions.append({
                'question': selected_question,
                'skill': skill_name.title(),
                'category': 'behavioral',
                'difficulty': 'general',
                'type': 'soft_skill',
                'time_limit': 300
            })
        
        return questions
    
    def _generate_technical_questions(self, technical_skills: List[CandidateSkill], count: int) -> List[Dict]:
        """Generate technical questions based on candidate's technical skills"""
        questions = []
        
        # Sort skills by confidence score (prioritize high-confidence skills)
        sorted_skills = sorted(technical_skills, key=lambda x: x.confidence_score or 0, reverse=True)
        
        for skill in sorted_skills:
            if len(questions) >= count:
                break
                
            skill_name = skill.skill_name.lower()
            proficiency = skill.proficiency_level or 'beginner'
            
            if skill_name in self.question_bank:
                skill_questions = self.question_bank[skill_name]
                
                if isinstance(skill_questions, dict) and proficiency in skill_questions:
                    # Technical skill with proficiency levels
                    available_questions = skill_questions[proficiency]
                    selected_question = random.choice(available_questions)
                    
                    questions.append({
                        'question': selected_question,
                        'skill': skill.skill_name,
                        'category': 'technical',
                        'difficulty': proficiency,
                        'type': skill.skill_type,
                        'time_limit': self._get_time_limit(proficiency)
                    })
                elif isinstance(skill_questions, list):
                    # Simple skill list
                    selected_question = random.choice(skill_questions)
                    questions.append({
                        'question': selected_question,
                        'skill': skill.skill_name,
                        'category': 'technical',
                        'difficulty': proficiency,
                        'type': skill.skill_type,
                        'time_limit': self._get_time_limit(proficiency)
                    })
        
        return questions
    
    def _generate_soft_skill_questions(self, soft_skills: List[CandidateSkill], count: int) -> List[Dict]:
        """Generate soft skill questions"""
        questions = []
        
        for skill in soft_skills:
            if len(questions) >= count:
                break
                
            skill_name = skill.skill_name.lower()
            
            if skill_name in self.question_bank:
                available_questions = self.question_bank[skill_name]
                selected_question = random.choice(available_questions)
                
                questions.append({
                    'question': selected_question,
                    'skill': skill.skill_name,
                    'category': 'behavioral',
                    'difficulty': 'general',
                    'type': 'soft_skill',
                    'time_limit': 300  # 5 minutes for behavioral questions
                })
        
        # Fill remaining with general soft skill questions
        general_soft_skills = ['leadership', 'communication', 'problem solving']
        while len(questions) < count:
            skill_name = random.choice(general_soft_skills)
            available_questions = self.question_bank[skill_name]
            selected_question = random.choice(available_questions)
            
            questions.append({
                'question': selected_question,
                'skill': skill_name.title(),
                'category': 'behavioral',
                'difficulty': 'general',
                'type': 'soft_skill',
                'time_limit': 300
            })
        
        return questions
    
    def _get_default_questions(self, count: int) -> List[Dict]:
        """Get default general questions when no skills are available"""
        default_questions = [
            {
                'question': "Tell me about yourself and your background.",
                'skill': 'General',
                'category': 'general',
                'difficulty': 'general',
                'type': 'introduction',
                'time_limit': 180
            },
            {
                'question': "Why are you interested in this position?",
                'skill': 'General',
                'category': 'general',
                'difficulty': 'general',
                'type': 'motivation',
                'time_limit': 180
            },
            {
                'question': "What are your greatest strengths and weaknesses?",
                'skill': 'General',
                'category': 'behavioral',
                'difficulty': 'general',
                'type': 'self_assessment',
                'time_limit': 240
            },
            {
                'question': "Where do you see yourself in 5 years?",
                'skill': 'General',
                'category': 'general',
                'difficulty': 'general',
                'type': 'career_goals',
                'time_limit': 180
            },
            {
                'question': "Describe a challenging project you worked on recently.",
                'skill': 'General',
                'category': 'behavioral',
                'difficulty': 'general',
                'type': 'experience',
                'time_limit': 300
            }
        ]
        
        return default_questions[:count]
    
    def _get_time_limit(self, proficiency: str) -> int:
        """Get time limit in seconds based on proficiency level"""
        time_limits = {
            'beginner': 180,    # 3 minutes
            'intermediate': 240, # 4 minutes
            'expert': 300       # 5 minutes
        }
        return time_limits.get(proficiency, 180)
    
    def generate_coding_question(self, skill_name: str, proficiency: str) -> Dict:
        """Generate a coding question for technical skills"""
        coding_questions = {
            'python': {
                'beginner': {
                    'question': "Write a Python function to check if a string is a palindrome.",
                    'starter_code': "def is_palindrome(s):\n    # Your code here\n    pass",
                    'test_cases': [
                        {'input': 'racecar', 'expected': True},
                        {'input': 'hello', 'expected': False}
                    ]
                },
                'intermediate': {
                    'question': "Implement a function to find the longest common subsequence of two strings.",
                    'starter_code': "def lcs(str1, str2):\n    # Your code here\n    pass",
                    'test_cases': [
                        {'input': ['ABCDGH', 'AEDFHR'], 'expected': 'ADH'},
                        {'input': ['AGGTAB', 'GXTXAYB'], 'expected': 'GTAB'}
                    ]
                }
            },
            'javascript': {
                'beginner': {
                    'question': "Write a JavaScript function to reverse an array without using built-in methods.",
                    'starter_code': "function reverseArray(arr) {\n    // Your code here\n}",
                    'test_cases': [
                        {'input': [1, 2, 3, 4, 5], 'expected': [5, 4, 3, 2, 1]},
                        {'input': ['a', 'b', 'c'], 'expected': ['c', 'b', 'a']}
                    ]
                }
            }
        }
        
        skill_lower = skill_name.lower()
        if skill_lower in coding_questions and proficiency in coding_questions[skill_lower]:
            question_data = coding_questions[skill_lower][proficiency]
            return {
                'question': question_data['question'],
                'starter_code': question_data['starter_code'],
                'test_cases': question_data['test_cases'],
                'skill': skill_name,
                'difficulty': proficiency,
                'type': 'coding',
                'time_limit': 1800  # 30 minutes for coding questions
            }
        
        return None