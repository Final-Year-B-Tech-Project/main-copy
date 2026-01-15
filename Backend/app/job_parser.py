import re
import json
from typing import List, Dict, Set

class JobDescriptionParser:
    """Parse job descriptions to extract required skills and requirements"""
    
    def __init__(self):
        self.skill_keywords = {
            # Programming Languages
            'python': {'category': 'technical', 'type': 'programming', 'aliases': ['py', 'python3']},
            'java': {'category': 'technical', 'type': 'programming', 'aliases': ['java8', 'java11']},
            'javascript': {'category': 'technical', 'type': 'programming', 'aliases': ['js', 'node.js', 'nodejs']},
            'typescript': {'category': 'technical', 'type': 'programming', 'aliases': ['ts']},
            'c++': {'category': 'technical', 'type': 'programming', 'aliases': ['cpp', 'c plus plus']},
            'c#': {'category': 'technical', 'type': 'programming', 'aliases': ['csharp', 'c sharp']},
            'php': {'category': 'technical', 'type': 'programming', 'aliases': []},
            'ruby': {'category': 'technical', 'type': 'programming', 'aliases': []},
            'go': {'category': 'technical', 'type': 'programming', 'aliases': ['golang']},
            'rust': {'category': 'technical', 'type': 'programming', 'aliases': []},
            'swift': {'category': 'technical', 'type': 'programming', 'aliases': []},
            'kotlin': {'category': 'technical', 'type': 'programming', 'aliases': []},
            'scala': {'category': 'technical', 'type': 'programming', 'aliases': []},
            'r': {'category': 'technical', 'type': 'programming', 'aliases': []},
            'matlab': {'category': 'technical', 'type': 'programming', 'aliases': []},
            'sql': {'category': 'technical', 'type': 'programming', 'aliases': ['mysql', 'postgresql', 'sqlite']},
            
            # Frameworks & Libraries
            'react': {'category': 'technical', 'type': 'framework', 'aliases': ['reactjs', 'react.js']},
            'angular': {'category': 'technical', 'type': 'framework', 'aliases': ['angularjs']},
            'vue': {'category': 'technical', 'type': 'framework', 'aliases': ['vue.js', 'vuejs']},
            'django': {'category': 'technical', 'type': 'framework', 'aliases': []},
            'flask': {'category': 'technical', 'type': 'framework', 'aliases': []},
            'spring': {'category': 'technical', 'type': 'framework', 'aliases': ['spring boot', 'springboot']},
            'express': {'category': 'technical', 'type': 'framework', 'aliases': ['express.js', 'expressjs']},
            'laravel': {'category': 'technical', 'type': 'framework', 'aliases': []},
            'tensorflow': {'category': 'technical', 'type': 'framework', 'aliases': ['tf']},
            'pytorch': {'category': 'technical', 'type': 'framework', 'aliases': []},
            'scikit-learn': {'category': 'technical', 'type': 'framework', 'aliases': ['sklearn']},
            'pandas': {'category': 'technical', 'type': 'framework', 'aliases': []},
            'numpy': {'category': 'technical', 'type': 'framework', 'aliases': []},
            
            # Tools & Technologies
            'docker': {'category': 'technical', 'type': 'tool', 'aliases': []},
            'kubernetes': {'category': 'technical', 'type': 'tool', 'aliases': ['k8s']},
            'git': {'category': 'technical', 'type': 'tool', 'aliases': ['github', 'gitlab']},
            'jenkins': {'category': 'technical', 'type': 'tool', 'aliases': []},
            'aws': {'category': 'technical', 'type': 'cloud', 'aliases': ['amazon web services']},
            'azure': {'category': 'technical', 'type': 'cloud', 'aliases': ['microsoft azure']},
            'gcp': {'category': 'technical', 'type': 'cloud', 'aliases': ['google cloud', 'google cloud platform']},
            
            # Databases
            'mongodb': {'category': 'technical', 'type': 'database', 'aliases': ['mongo']},
            'redis': {'category': 'technical', 'type': 'database', 'aliases': []},
            'elasticsearch': {'category': 'technical', 'type': 'database', 'aliases': ['elastic']},
            
            # Data Science & AI
            'machine learning': {'category': 'technical', 'type': 'domain', 'aliases': ['ml', 'ai', 'artificial intelligence']},
            'deep learning': {'category': 'technical', 'type': 'domain', 'aliases': ['dl', 'neural networks']},
            'data science': {'category': 'technical', 'type': 'domain', 'aliases': ['data analysis', 'analytics']},
            'nlp': {'category': 'technical', 'type': 'domain', 'aliases': ['natural language processing', 'text processing']},
            'computer vision': {'category': 'technical', 'type': 'domain', 'aliases': ['cv', 'image processing']},
            
            # Soft Skills
            'leadership': {'category': 'soft', 'type': 'soft_skill', 'aliases': ['team lead', 'management']},
            'communication': {'category': 'soft', 'type': 'soft_skill', 'aliases': ['verbal', 'written']},
            'problem solving': {'category': 'soft', 'type': 'soft_skill', 'aliases': ['analytical', 'critical thinking']},
            'teamwork': {'category': 'soft', 'type': 'soft_skill', 'aliases': ['collaboration', 'team player']},
            'project management': {'category': 'soft', 'type': 'soft_skill', 'aliases': ['agile', 'scrum']},
        }
        
        self.experience_patterns = [
            r'(\d+)[\s-]*(?:to|-)[\s-]*(\d+)[\s-]*years?',  # 2-5 years
            r'(\d+)\+[\s-]*years?',  # 3+ years
            r'minimum[\s-]*(\d+)[\s-]*years?',  # minimum 2 years
            r'at least[\s-]*(\d+)[\s-]*years?',  # at least 3 years
            r'(\d+)[\s-]*years?[\s-]*(?:of\s+)?experience',  # 5 years experience
        ]
        
        self.requirement_indicators = [
            'required', 'must have', 'essential', 'mandatory', 'need', 'should have',
            'preferred', 'nice to have', 'plus', 'bonus', 'advantage', 'desirable'
        ]
    
    def parse_job_description(self, description: str, job_title: str = "", job_role: str = "") -> Dict:
        """Parse job description and extract structured requirements"""
        description_lower = description.lower()
        
        # Extract skills
        required_skills = self._extract_skills(description, importance='required')
        preferred_skills = self._extract_skills(description, importance='preferred')
        
        # Extract experience requirements
        experience_req = self._extract_experience_requirements(description)
        
        # Determine job category and add category-specific skills
        job_category = self._determine_job_category(job_title, job_role, description)
        category_skills = self._get_category_specific_skills(job_category)
        
        # Merge category skills with extracted skills
        for skill in category_skills:
            if not any(s['skill'].lower() == skill.lower() for s in required_skills):
                required_skills.append({
                    'skill': skill,
                    'importance': 'preferred',
                    'min_proficiency': 'beginner'
                })
        
        return {
            'required_skills': required_skills,
            'preferred_skills': preferred_skills,
            'experience_requirements': experience_req,
            'job_category': job_category,
            'parsed_skills_count': len(required_skills) + len(preferred_skills)
        }
    
    def _extract_skills(self, description: str, importance: str = 'required') -> List[Dict]:
        """Extract skills from job description"""
        skills = []
        description_lower = description.lower()
        
        # Look for each skill and its aliases
        for skill_name, skill_info in self.skill_keywords.items():
            skill_found = False
            proficiency = 'beginner'
            
            # Check main skill name
            if skill_name in description_lower:
                skill_found = True
            
            # Check aliases
            for alias in skill_info['aliases']:
                if alias in description_lower:
                    skill_found = True
                    break
            
            if skill_found:
                # Determine proficiency level based on context
                proficiency = self._determine_skill_proficiency(description_lower, skill_name)
                
                # Determine importance based on context
                skill_importance = self._determine_skill_importance(description_lower, skill_name)
                
                skills.append({
                    'skill': skill_name.title(),
                    'importance': skill_importance,
                    'min_proficiency': proficiency,
                    'category': skill_info['category'],
                    'type': skill_info['type']
                })
        
        return skills
    
    def _determine_skill_proficiency(self, description: str, skill: str) -> str:
        """Determine required proficiency level for a skill"""
        skill_context = self._get_skill_context(description, skill)
        
        expert_indicators = ['expert', 'advanced', 'senior', 'lead', 'architect', 'mastery', 'deep']
        intermediate_indicators = ['intermediate', 'experienced', 'solid', 'strong', 'good']
        
        for indicator in expert_indicators:
            if indicator in skill_context:
                return 'expert'
        
        for indicator in intermediate_indicators:
            if indicator in skill_context:
                return 'intermediate'
        
        return 'beginner'
    
    def _determine_skill_importance(self, description: str, skill: str) -> str:
        """Determine importance level of a skill"""
        skill_context = self._get_skill_context(description, skill)
        
        required_indicators = ['required', 'must', 'essential', 'mandatory', 'need']
        preferred_indicators = ['preferred', 'nice', 'plus', 'bonus', 'advantage']
        
        for indicator in required_indicators:
            if indicator in skill_context:
                return 'required'
        
        for indicator in preferred_indicators:
            if indicator in skill_context:
                return 'preferred'
        
        return 'required'  # Default to required
    
    def _get_skill_context(self, description: str, skill: str) -> str:
        """Get context around skill mention"""
        skill_pos = description.find(skill)
        if skill_pos == -1:
            return ""
        
        start = max(0, skill_pos - 100)
        end = min(len(description), skill_pos + 100)
        return description[start:end]
    
    def _extract_experience_requirements(self, description: str) -> Dict:
        """Extract experience requirements from job description"""
        description_lower = description.lower()
        
        min_exp = 0
        max_exp = 10
        
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, description_lower)
            if matches:
                if isinstance(matches[0], tuple):
                    # Range pattern (2-5 years)
                    min_exp = int(matches[0][0])
                    max_exp = int(matches[0][1])
                else:
                    # Single number pattern
                    min_exp = int(matches[0])
                    max_exp = min_exp + 3
                break
        
        # Determine experience level
        if min_exp <= 1:
            level = 'entry'
        elif min_exp <= 4:
            level = 'mid'
        else:
            level = 'senior'
        
        return {
            'min_years': min_exp,
            'max_years': max_exp,
            'level': level
        }
    
    def _determine_job_category(self, job_title: str, job_role: str, description: str) -> str:
        """Determine job category from title, role, and description"""
        combined_text = f"{job_title} {job_role} {description}".lower()
        
        categories = {
            'data_science': ['data scientist', 'data analyst', 'machine learning', 'ai', 'analytics'],
            'frontend': ['frontend', 'front-end', 'react', 'angular', 'vue', 'ui', 'ux'],
            'backend': ['backend', 'back-end', 'api', 'server', 'database'],
            'fullstack': ['fullstack', 'full-stack', 'full stack'],
            'devops': ['devops', 'infrastructure', 'deployment', 'docker', 'kubernetes'],
            'mobile': ['mobile', 'android', 'ios', 'react native', 'flutter'],
            'qa': ['qa', 'quality assurance', 'testing', 'test'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in combined_text for keyword in keywords):
                return category
        
        return 'general'
    
    def _get_category_specific_skills(self, category: str) -> List[str]:
        """Get additional skills based on job category"""
        category_skills = {
            'data_science': ['Python', 'R', 'SQL', 'Machine Learning', 'Pandas', 'Numpy', 'Scikit-learn'],
            'frontend': ['JavaScript', 'HTML', 'CSS', 'React', 'Angular', 'Vue'],
            'backend': ['Python', 'Java', 'Node.js', 'SQL', 'API', 'Database'],
            'fullstack': ['JavaScript', 'Python', 'React', 'Node.js', 'SQL'],
            'devops': ['Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Git'],
            'mobile': ['Java', 'Swift', 'Kotlin', 'React Native', 'Flutter'],
            'qa': ['Testing', 'Automation', 'Selenium', 'API Testing'],
        }
        
        return category_skills.get(category, [])