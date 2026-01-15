"""
Adaptive Question Generation Feature
Generates context-aware follow-up questions based on candidate responses
"""

class AdaptiveQuestions:
    
    @staticmethod
    def analyze_response_context(response_text):
        """Analyze response and return focus areas for next question"""
        response_lower = response_text.lower()
        focus_areas = []
        
        if 'project' in response_lower:
            focus_areas.append("Ask about technical challenges in the project")
        
        if 'experience' in response_lower or 'worked' in response_lower:
            focus_areas.append("Dig deeper into specific responsibilities")
        
        if 'team' in response_lower:
            focus_areas.append("Explore team dynamics and collaboration")
        
        if len(response_text.split()) < 20:
            focus_areas.append("Ask for more specific details and examples")
        
        return focus_areas
    
    @staticmethod
    def build_adaptive_prompt(base_prompt, response_text):
        """Build adaptive prompt with context from previous response"""
        focus_areas = AdaptiveQuestions.analyze_response_context(response_text)
        
        if focus_areas:
            adaptive_section = "\n\nBased on the candidate's previous response, focus on: " + ", ".join(focus_areas)
            return base_prompt + adaptive_section
        
        return base_prompt
