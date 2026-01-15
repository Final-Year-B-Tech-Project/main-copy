"""Resume Parser - Extract skills and info from resume"""

import PyPDF2
import re
import json

class ResumeParser:
    
    SKILLS_DATABASE = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
        # Web Technologies
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'asp.net',
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd', 'terraform',
        # Data Science & AI
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn',
        'data analysis', 'data science', 'nlp', 'computer vision',
        # Other
        'agile', 'scrum', 'rest api', 'graphql', 'microservices', 'linux', 'testing', 'debugging'
    ]
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""
    
    @staticmethod
    def extract_skills(text):
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in ResumeParser.SKILLS_DATABASE:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))  # Remove duplicates
    
    @staticmethod
    def extract_email(text):
        """Extract email from resume"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    @staticmethod
    def extract_phone(text):
        """Extract phone number from resume"""
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else None
    
    @staticmethod
    def extract_experience_years(text):
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience\s*:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s*(?:of)?\s*experience'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0
    
    @staticmethod
    def extract_education(text):
        """Extract education details"""
        degrees = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'bca', 'mca', 'b.e', 'm.e', 'bsc', 'msc']
        found_degrees = []
        
        text_lower = text.lower()
        for degree in degrees:
            if degree in text_lower:
                found_degrees.append(degree.upper())
        
        return list(set(found_degrees))
    
    @staticmethod
    def parse_resume(file_path):
        """Parse resume and extract all information"""
        text = ResumeParser.extract_text_from_pdf(file_path)
        
        if not text:
            return None
        
        return {
            'text': text,
            'skills': ResumeParser.extract_skills(text),
            'email': ResumeParser.extract_email(text),
            'phone': ResumeParser.extract_phone(text),
            'experience_years': ResumeParser.extract_experience_years(text),
            'education': ResumeParser.extract_education(text)
        }
    
    @staticmethod
    def generate_resume_summary(parsed_data):
        """Generate a summary from parsed resume data"""
        if not parsed_data:
            return "No resume data available"
        
        skills = parsed_data.get('skills', [])
        exp_years = parsed_data.get('experience_years', 0)
        education = parsed_data.get('education', [])
        
        summary = f"Candidate with {exp_years} years of experience. "
        
        if education:
            summary += f"Education: {', '.join(education)}. "
        
        if skills:
            summary += f"Key skills: {', '.join(skills[:10])}."
        
        return summary

def parse_and_store_resume(file_path, student_profile):
    """Parse resume and store in student profile"""
    parsed = ResumeParser.parse_resume(file_path)
    
    if parsed:
        student_profile.resume_text = parsed['text']
        student_profile.skills = json.dumps(parsed['skills'])
        return parsed
    
    return None
