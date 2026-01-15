#!/usr/bin/env python3
"""
Backup Question Generator - Ensures interview never gets stuck
"""

class BackupQuestionGenerator:
    def __init__(self):
        self.question_pool = [
            # Introduction & Background
            "Could you tell me about yourself and your background?",
            "What are you currently studying or working on?",
            
            # Education
            "Tell me about your educational background.",
            "Which subjects or courses have you found most interesting?",
            "What year are you in your studies?",
            
            # Technical Skills
            "What technical skills or programming languages are you familiar with?",
            "Have you worked with any specific technologies or tools?",
            "How do you typically learn new technical concepts?",
            
            # Projects & Experience
            "Have you worked on any projects, either academic or personal?",
            "Can you describe a project you're proud of?",
            "Do you have any work experience or internships?",
            
            # Problem Solving
            "How do you approach solving problems?",
            "Tell me about a challenge you've faced and how you handled it.",
            "What do you do when you encounter something you don't know?",
            
            # Motivation & Goals
            "What motivates you in your studies or work?",
            "What are your career goals for the next few years?",
            "What kind of work environment interests you?",
            
            # Teamwork & Communication
            "Have you worked in teams before? How was that experience?",
            "How do you handle feedback or criticism?",
            "Tell me about a time you had to explain something complex to someone.",
            
            # Closing
            "What questions do you have about this role or company?",
            "Is there anything else you'd like me to know about you?"
        ]
        
        self.used_questions = set()
    
    def get_next_question(self, question_count: int, previous_responses: list = None) -> str:
        """Get next backup question ensuring no repetition"""
        
        # Analyze previous responses to avoid similar topics
        covered_topics = set()
        if previous_responses:
            for response in previous_responses:
                text = response.get('answer', '').lower()
                if any(word in text for word in ['student', 'study', 'college']):
                    covered_topics.add('education')
                if any(word in text for word in ['programming', 'coding', 'technical']):
                    covered_topics.add('technical')
                if any(word in text for word in ['project', 'built', 'developed']):
                    covered_topics.add('projects')
                if any(word in text for word in ['work', 'job', 'company']):
                    covered_topics.add('experience')
        
        # Select appropriate question based on count and topics covered
        if question_count == 0:
            return self.question_pool[0]  # Introduction
        elif question_count == 1 and 'education' not in covered_topics:
            return self.question_pool[2]  # Education
        elif question_count <= 2 and 'technical' not in covered_topics:
            return self.question_pool[5]  # Technical skills
        elif question_count <= 3 and 'projects' not in covered_topics:
            return self.question_pool[8]  # Projects
        elif question_count <= 4:
            return self.question_pool[11]  # Problem solving
        elif question_count <= 5:
            return self.question_pool[14]  # Motivation
        elif question_count <= 6:
            return self.question_pool[17]  # Teamwork
        elif question_count <= 7:
            return self.question_pool[15]  # Career goals
        else:
            return self.question_pool[20]  # Closing question
    
    def get_emergency_question(self) -> str:
        """Get emergency question when all else fails"""
        return "Could you tell me more about yourself?"
    
    def reset(self):
        """Reset used questions for new interview"""
        self.used_questions.clear()