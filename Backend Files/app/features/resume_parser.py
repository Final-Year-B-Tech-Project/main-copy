"""Resume Parsing & Skill Extraction Feature"""

from app.system_lock import register_feature, execute_hook
import PyPDF2
import re

class ResumeParser:
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF resume"""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    @staticmethod
    def extract_skills(resume_text):
        """Extract technical skills from resume"""
        skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'sql', 'mongodb',
            'aws', 'docker', 'kubernetes', 'git', 'html', 'css', 'angular',
            'vue', 'django', 'flask', 'spring', 'machine learning', 'ai'
        ]
        
        found_skills = []
        text_lower = resume_text.lower()
        
        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    @staticmethod
    def extract_experience(resume_text):
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience\s*:\s*(\d+)\+?\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, resume_text.lower())
            if match:
                return int(match.group(1))
        
        return 0
    
    @staticmethod
    def is_eligible(resume_text, job_requirements):
        """Check if candidate is eligible based on resume"""
        skills = ResumeParser.extract_skills(resume_text)
        experience = ResumeParser.extract_experience(resume_text)
        
        required_skills = job_requirements.get('skills', [])
        min_experience = job_requirements.get('min_experience', 0)
        
        skill_match = len(set(skills) & set(required_skills)) >= len(required_skills) * 0.5
        experience_match = experience >= min_experience
        
        return skill_match and experience_match

register_feature('resume_parser', ResumeParser)
