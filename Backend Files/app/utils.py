import os
import re
import uuid
import secrets
# import PyPDF2  # Temporarily disabled
from typing import Optional
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    if not filename:
        return False
    
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'})
    if '.' not in filename:
        return False
    
    parts = filename.rsplit('.', 1)
    if len(parts) < 2:
        return False
    
    return parts[1].lower() in allowed_extensions

def generate_hr_code() -> str:
    """Generate unique HR code."""
    return f"HR{secrets.token_hex(4).upper()}"

def generate_interview_link() -> str:
    """Generate unique interview link."""
    return str(uuid.uuid4())

def parse_resume(file_path: str) -> Optional[str]:
    """Parse resume content from PDF file."""
    try:
        if not os.path.exists(file_path):
            return None
        
        # Handle PDF files
        if file_path.lower().endswith('.pdf'):
            # PDF parsing temporarily disabled - install PyPDF2 to enable
            return "PDF parsing temporarily disabled. Please install PyPDF2."
        
        # Handle text files
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return clean_resume_text(file.read())
        
        # For other file types, return empty string
        return ""
        
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return None

def clean_resume_text(text: str) -> str:
    """Clean and normalize resume text."""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    
    # Remove common PDF artifacts
    text = re.sub(r'[^\w\s\n.,;:()\-@]', '', text)
    
    return text.strip()

def extract_skills_from_resume(resume_text: str) -> list:
    """Extract skills from resume text using basic keyword matching."""
    if not resume_text:
        return []
    
    # Common technical skills keywords
    skill_keywords = [
        # Programming languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css',
        
        # Frameworks and libraries
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'nodejs', 'laravel',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
        
        # Tools and technologies
        'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'travis',
        'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
        
        # Soft skills
        'leadership', 'teamwork', 'communication', 'problem solving', 'analytical',
        'project management', 'agile', 'scrum'
    ]
    
    found_skills = []
    resume_lower = resume_text.lower()
    
    for skill in skill_keywords:
        if skill in resume_lower:
            found_skills.append(skill.title())
    
    return list(set(found_skills))  # Remove duplicates

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes == 0:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"

def calculate_interview_score(responses: dict, questions: list) -> dict:
    """Calculate basic interview scores based on responses."""
    if not responses or not questions:
        return {
            'overall_score': 0,
            'completion_rate': 0,
            'average_response_length': 0
        }
    
    total_questions = len(questions)
    answered_questions = len([r for r in responses.values() if r.get('answer', '').strip()])
    completion_rate = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
    
    # Calculate average response length
    response_lengths = [len(r.get('answer', '')) for r in responses.values()]
    avg_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
    
    # Basic scoring algorithm
    base_score = completion_rate * 0.7  # 70% weight for completion
    length_bonus = min(avg_length / 100, 30)  # Up to 30 points for response length
    
    overall_score = min(base_score + length_bonus, 100)
    
    return {
        'overall_score': round(overall_score, 1),
        'completion_rate': round(completion_rate, 1),
        'average_response_length': round(avg_length, 1)
    }

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    if not filename:
        return "file"
    
    # Keep only alphanumeric characters, dots, hyphens, and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Ensure filename is not too long
    name, ext = os.path.splitext(sanitized)
    if len(name) > 50:
        name = name[:50]
    
    return f"{name}{ext}"

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB."""
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except OSError:
        return 0.0

def create_safe_directory(directory_path: str) -> bool:
    """Create directory safely if it doesn't exist."""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except OSError as e:
        print(f"Error creating directory {directory_path}: {e}")
        return False

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis."""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def format_score_color(score: float) -> str:
    """Get CSS class name for score color coding."""
    if score >= 80:
        return "text-success"  # Green
    elif score >= 60:
        return "text-warning"  # Yellow/Orange
    else:
        return "text-danger"   # Red

def parse_json_safely(json_string: str, default=None):
    """Parse JSON string safely with fallback."""
    try:
        if not json_string:
            return default or {}
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default or {}

def generate_session_token() -> str:
    """Generate secure session token."""
    return secrets.token_urlsafe(32)

def mask_email(email: str) -> str:
    """Mask email for privacy (e.g., j***@example.com)."""
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    if len(username) <= 2:
        masked_username = username
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
    
    return f"{masked_username}@{domain}"

def get_time_ago(datetime_obj) -> str:
    """Get human-readable time ago string."""
    if not datetime_obj:
        return "Unknown"
    
    from datetime import datetime, timezone
    
    if datetime_obj.tzinfo is None:
        datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - datetime_obj
    
    if diff.days > 30:
        return f"{diff.days // 30} month{'s' if diff.days // 30 != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def validate_phone_number(phone: str) -> bool:
    """Basic phone number validation."""
    if not phone:
        return True  # Phone is optional
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a reasonable length (7-15 digits)
    return 7 <= len(digits_only) <= 15

def get_file_icon(filename: str) -> str:
    """Get appropriate icon class for file type."""
    if not filename:
        return "fa-file"
    
    extension = filename.lower().split('.')[-1]
    
    icon_map = {
        'pdf': 'fa-file-pdf',
        'doc': 'fa-file-word',
        'docx': 'fa-file-word',
        'txt': 'fa-file-text',
        'jpg': 'fa-file-image',
        'jpeg': 'fa-file-image',
        'png': 'fa-file-image',
        'gif': 'fa-file-image',
        'zip': 'fa-file-archive',
        'rar': 'fa-file-archive',
    }
    
    return icon_map.get(extension, 'fa-file')