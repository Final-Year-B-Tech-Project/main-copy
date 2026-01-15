import os
import re
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import PyPDF2
from docx import Document
from app import db
from app.resume_models import ParsedResume, CandidateSkill, ResumeParsingLog

class EnhancedResumeParser:
    """Advanced resume parser with multi-format support"""
    
    def __init__(self):
        self.skill_database = self._load_skill_database()
        self.education_keywords = ['university', 'college', 'degree', 'bachelor', 'master', 'phd', 'gpa']
        self.experience_keywords = ['experience', 'work', 'employment', 'company', 'position', 'role']
        
    def parse_resume(self, file_path: str, student_id: int) -> Dict:
        """Main parsing function for all file types"""
        start_time = time.time()
        
        try:
            # Extract text based on file type
            text = self._extract_text(file_path)
            if not text:
                return self._create_error_result("Failed to extract text from file")
            
            # Parse different sections
            contact_info = self._extract_contact_info(text)
            education = self._extract_education(text)
            experience = self._extract_experience(text)
            projects = self._extract_projects(text)
            skills = self._extract_skills(text)
            
            # Calculate total experience
            total_exp = self._calculate_total_experience(experience)
            
            # Save parsed data
            parsed_resume = self._save_parsed_resume(
                student_id, contact_info, education, experience, 
                projects, total_exp, file_path
            )
            
            # Save extracted skills
            self._save_candidate_skills(student_id, skills)
            
            # Log parsing attempt
            processing_time = time.time() - start_time
            self._log_parsing_attempt(
                student_id, file_path, 'success', 
                len(skills), processing_time
            )
            
            return {
                'success': True,
                'parsed_resume_id': parsed_resume.id,
                'skills_extracted': len(skills),
                'total_experience': total_exp,
                'contact_info': contact_info,
                'processing_time': processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._log_parsing_attempt(
                student_id, file_path, 'failed', 
                0, processing_time, str(e)
            )
            return self._create_error_result(str(e))
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from different file formats"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext == '.docx':
            return self._extract_from_docx(file_path)
        elif file_ext == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise ValueError(f"PDF parsing error: {e}")
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"DOCX parsing error: {e}")
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"TXT parsing error: {e}")
    
    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information"""
        contact = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact['email'] = emails[0]
        
        # Phone extraction
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        # LinkedIn extraction
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin:
            contact['linkedin_url'] = 'https://' + linkedin.group()
        
        return contact
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        
        # Look for degree patterns
        degree_patterns = [
            r'(Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?)\s+(?:of\s+)?([^,\n]+)',
            r'(B\.?Tech|M\.?Tech|B\.?E\.?|M\.?E\.?)\s+(?:in\s+)?([^,\n]+)'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                degree_info = {
                    'degree': match[0].strip(),
                    'field': match[1].strip(),
                    'university': self._extract_university_name(text, match[0]),
                    'year': self._extract_graduation_year(text),
                    'gpa': self._extract_gpa(text)
                }
                education.append(degree_info)
        
        return education
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        experience = []
        
        # Look for company and position patterns
        exp_patterns = [
            r'([A-Z][^,\n]+(?:Inc|Corp|Ltd|LLC|Company))[,\s]+([^,\n]+)',
            r'([^,\n]+)\s+at\s+([A-Z][^,\n]+)',
            r'([^,\n]+)\s+-\s+([A-Z][^,\n]+)'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                exp_info = {
                    'company': match[1].strip() if 'at' in pattern else match[0].strip(),
                    'position': match[0].strip() if 'at' in pattern else match[1].strip(),
                    'duration': self._extract_duration(text, match[0]),
                    'description': self._extract_job_description(text, match[0])
                }
                experience.append(exp_info)
        
        return experience
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract project information"""
        projects = []
        
        # Look for project sections
        project_section = re.search(r'projects?:?\s*(.*?)(?=\n\s*[A-Z][^:]*:|$)', 
                                  text, re.IGNORECASE | re.DOTALL)
        
        if project_section:
            project_text = project_section.group(1)
            # Extract individual projects
            project_lines = [line.strip() for line in project_text.split('\n') if line.strip()]
            
            for line in project_lines:
                if len(line) > 20:  # Filter out short lines
                    project_info = {
                        'name': self._extract_project_name(line),
                        'description': line,
                        'technologies': self._extract_technologies_from_text(line)
                    }
                    projects.append(project_info)
        
        return projects
    
    def _extract_skills(self, text: str) -> List[Dict]:
        """Extract and categorize skills"""
        skills = []
        text_lower = text.lower()
        
        for skill_name, skill_info in self.skill_database.items():
            if skill_name.lower() in text_lower:
                # Determine proficiency based on context
                proficiency = self._determine_proficiency(text, skill_name)
                
                skill_data = {
                    'skill_name': skill_name,
                    'skill_category': skill_info['category'],
                    'skill_type': skill_info['type'],
                    'proficiency_level': proficiency,
                    'years_experience': self._estimate_skill_experience(text, skill_name),
                    'confidence_score': self._calculate_confidence(text, skill_name)
                }
                skills.append(skill_data)
        
        return skills
    
    def _load_skill_database(self) -> Dict:
        """Load comprehensive skill database"""
        return {
            # Programming Languages
            'Python': {'category': 'technical', 'type': 'programming'},
            'Java': {'category': 'technical', 'type': 'programming'},
            'JavaScript': {'category': 'technical', 'type': 'programming'},
            'TypeScript': {'category': 'technical', 'type': 'programming'},
            'C++': {'category': 'technical', 'type': 'programming'},
            'C#': {'category': 'technical', 'type': 'programming'},
            'Go': {'category': 'technical', 'type': 'programming'},
            'Rust': {'category': 'technical', 'type': 'programming'},
            'PHP': {'category': 'technical', 'type': 'programming'},
            'Ruby': {'category': 'technical', 'type': 'programming'},
            
            # Frameworks
            'React': {'category': 'technical', 'type': 'framework'},
            'Angular': {'category': 'technical', 'type': 'framework'},
            'Vue.js': {'category': 'technical', 'type': 'framework'},
            'Django': {'category': 'technical', 'type': 'framework'},
            'Flask': {'category': 'technical', 'type': 'framework'},
            'Spring': {'category': 'technical', 'type': 'framework'},
            'Express.js': {'category': 'technical', 'type': 'framework'},
            'Laravel': {'category': 'technical', 'type': 'framework'},
            
            # Tools & Technologies
            'Docker': {'category': 'technical', 'type': 'tool'},
            'Kubernetes': {'category': 'technical', 'type': 'tool'},
            'Git': {'category': 'technical', 'type': 'tool'},
            'Jenkins': {'category': 'technical', 'type': 'tool'},
            'AWS': {'category': 'technical', 'type': 'cloud'},
            'Azure': {'category': 'technical', 'type': 'cloud'},
            'GCP': {'category': 'technical', 'type': 'cloud'},
            
            # Databases
            'MySQL': {'category': 'technical', 'type': 'database'},
            'PostgreSQL': {'category': 'technical', 'type': 'database'},
            'MongoDB': {'category': 'technical', 'type': 'database'},
            'Redis': {'category': 'technical', 'type': 'database'},
            
            # Soft Skills
            'Leadership': {'category': 'soft', 'type': 'soft_skill'},
            'Communication': {'category': 'soft', 'type': 'soft_skill'},
            'Problem Solving': {'category': 'soft', 'type': 'soft_skill'},
            'Team Work': {'category': 'soft', 'type': 'soft_skill'},
            'Project Management': {'category': 'soft', 'type': 'soft_skill'},
        }
    
    def _determine_proficiency(self, text: str, skill: str) -> str:
        """Determine skill proficiency level from context"""
        skill_context = self._get_skill_context(text, skill)
        
        expert_indicators = ['expert', 'advanced', 'senior', 'lead', 'architect', '5+ years', '3+ years']
        intermediate_indicators = ['intermediate', 'experienced', '2+ years', '1+ years']
        
        for indicator in expert_indicators:
            if indicator.lower() in skill_context.lower():
                return 'expert'
        
        for indicator in intermediate_indicators:
            if indicator.lower() in skill_context.lower():
                return 'intermediate'
        
        return 'beginner'
    
    def _save_parsed_resume(self, student_id: int, contact: Dict, education: List, 
                          experience: List, projects: List, total_exp: float, file_path: str) -> ParsedResume:
        """Save parsed resume data to database"""
        parsed_resume = ParsedResume(
            student_id=student_id,
            email=contact.get('email'),
            phone=contact.get('phone'),
            linkedin_url=contact.get('linkedin_url'),
            education_data=json.dumps(education),
            experience_data=json.dumps(experience),
            projects_data=json.dumps(projects),
            total_experience_years=total_exp,
            parsing_confidence=0.85  # Default confidence
        )
        
        db.session.add(parsed_resume)
        db.session.commit()
        return parsed_resume
    
    def _save_candidate_skills(self, student_id: int, skills: List[Dict]):
        """Save extracted skills to student profile as consolidated JSON"""
        from app.models import StudentProfile
        
        # Get student profile
        student_profile = StudentProfile.query.get(student_id)
        if not student_profile:
            print(f"Student profile {student_id} not found")
            return
        
        # Separate technical and soft skills
        technical_skills = [s for s in skills if s['skill_category'] == 'technical']
        soft_skills = [s for s in skills if s['skill_category'] == 'soft']
        
        # Update student profile with consolidated skills
        student_profile.skills = json.dumps(skills)
        student_profile.technical_skills = json.dumps(technical_skills)
        student_profile.soft_skills = json.dumps(soft_skills)
        student_profile.skills_count = len(skills)
        student_profile.parsing_confidence = 0.85
        student_profile.last_parsed_at = datetime.utcnow()
        
        # Also save to ParsedResume if exists
        parsed_resume = ParsedResume.query.filter_by(student_id=student_id).first()
        if parsed_resume:
            student_profile.parsed_contact = json.dumps({
                'email': parsed_resume.email,
                'phone': parsed_resume.phone,
                'linkedin_url': parsed_resume.linkedin_url
            })
            student_profile.parsed_education = parsed_resume.education_data
            student_profile.parsed_experience = parsed_resume.experience_data
            student_profile.parsed_projects = parsed_resume.projects_data
            student_profile.total_experience_years = parsed_resume.total_experience_years
        
        db.session.commit()
        print(f"✅ Saved {len(skills)} skills to student profile {student_id}")
    
    def _log_parsing_attempt(self, student_id: int, file_path: str, status: str, 
                           skills_count: int, processing_time: float, error: str = None):
        """Log parsing attempt"""
        log = ResumeParsingLog(
            student_id=student_id,
            file_name=os.path.basename(file_path),
            file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            file_type=os.path.splitext(file_path)[1],
            parsing_status=status,
            skills_extracted=skills_count,
            processing_time=processing_time,
            error_message=error
        )
        
        db.session.add(log)
        db.session.commit()
    
    def _create_error_result(self, error_message: str) -> Dict:
        """Create error result dictionary"""
        return {
            'success': False,
            'error': error_message,
            'skills_extracted': 0,
            'total_experience': 0
        }
    
    # Helper methods (simplified implementations)
    def _extract_university_name(self, text: str, degree: str) -> str:
        return "University Name"  # Simplified
    
    def _extract_graduation_year(self, text: str) -> int:
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        return int(years[-1]) if years else None
    
    def _extract_gpa(self, text: str) -> float:
        gpa_match = re.search(r'gpa:?\s*(\d+\.?\d*)', text, re.IGNORECASE)
        return float(gpa_match.group(1)) if gpa_match else None
    
    def _extract_duration(self, text: str, company: str) -> str:
        return "2 years"  # Simplified
    
    def _extract_job_description(self, text: str, position: str) -> str:
        return "Job description"  # Simplified
    
    def _extract_project_name(self, line: str) -> str:
        return line.split(':')[0].strip() if ':' in line else line[:50]
    
    def _extract_technologies_from_text(self, text: str) -> List[str]:
        techs = []
        for skill in self.skill_database:
            if skill.lower() in text.lower():
                techs.append(skill)
        return techs
    
    def _calculate_total_experience(self, experience: List[Dict]) -> float:
        return len(experience) * 2.0  # Simplified: 2 years per job
    
    def _get_skill_context(self, text: str, skill: str) -> str:
        # Get 100 characters around the skill mention
        skill_pos = text.lower().find(skill.lower())
        if skill_pos == -1:
            return ""
        start = max(0, skill_pos - 50)
        end = min(len(text), skill_pos + 50)
        return text[start:end]
    
    def _estimate_skill_experience(self, text: str, skill: str) -> float:
        context = self._get_skill_context(text, skill)
        # Look for year mentions near the skill
        years = re.findall(r'(\d+)\s*(?:years?|yrs?)', context, re.IGNORECASE)
        return float(years[0]) if years else 1.0
    
    def _calculate_confidence(self, text: str, skill: str) -> float:
        # Higher confidence if skill appears multiple times or in context
        occurrences = text.lower().count(skill.lower())
        return min(0.9, 0.5 + (occurrences * 0.1))