"""
Professional Interview Opening Feature
Provides authoritative interview opening script
"""

class ProfessionalOpening:
    
    @staticmethod
    def get_opening_script(candidate_name="Candidate", job_role="this position"):
        """Generate professional interview opening"""
        return f"""Good day, {candidate_name}. Welcome to this interview for {job_role}.

I'll be conducting your evaluation today. This is a 20-minute structured interview where I'll assess your technical competency, problem-solving abilities, and professional experience.

Please provide detailed, specific responses. Use concrete examples from your experience. Vague or brief answers will impact your evaluation negatively.

The interview is now beginning. Let's proceed with the first question."""
    
    @staticmethod
    def get_closing_script(candidate_name="Candidate"):
        """Generate professional interview closing"""
        return f"""Thank you, {candidate_name}. The interview has concluded.

Your responses have been recorded and will be evaluated based on professional standards. You will receive detailed feedback shortly.

This concludes our session."""
