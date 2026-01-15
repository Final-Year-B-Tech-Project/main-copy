class ProfessionalInterviewer:
    def __init__(self, job_role):
        self.job_role = job_role
        self.question_bank = {
            'intro': [
                f"Excellent! Now, could you walk me through your educational background and how it relates to the {job_role} position?",
                "That's great to hear! What specific technical skills have you developed that would be valuable for this role?"
            ],
            'technical': [
                "Can you describe a challenging technical problem you've solved and your approach to solving it?",
                "How do you stay updated with the latest technologies and industry trends?",
                "Tell me about a project where you had to learn a new technology quickly. How did you approach it?"
            ],
            'experience': [
                "Describe a time when you had to work under pressure or tight deadlines. How did you manage it?",
                "Can you give me an example of how you've collaborated with others on a technical project?",
                "Tell me about a mistake you made in a project and how you handled it."
            ],
            'problem_solving': [
                "How would you approach debugging a complex issue in a production system?",
                "Describe your process for breaking down a large, complex problem into manageable parts.",
                "Can you walk me through how you would design a solution for a scalable web application?"
            ],
            'closing': [
                "What questions do you have about our company, the team, or this role?",
                "Where do you see yourself professionally in the next 2-3 years?",
                "Is there anything else you'd like to share that we haven't covered?"
            ]
        }
    
    def get_adaptive_question(self, response, count, remaining_time):
        # Enhanced adaptive logic based on response quality
        response_lower = response.lower() if response else ""
        
        if count == 0:
            return f"Thank you for that introduction! Now, could you tell me about your experience with {self.job_role.lower()} technologies and tools?"
        elif count == 1:
            # Adapt based on first response
            if len(response) > 50:
                return "That's great! Can you walk me through a specific project where you applied these skills?"
            else:
                return "Could you provide more details about your technical background and the technologies you've worked with?"
        elif count < 4:
            # Mid-interview adaptive questions
            if 'project' in response_lower or 'built' in response_lower or 'developed' in response_lower:
                return self.question_bank['experience'][count % len(self.question_bank['experience'])]
            elif 'learn' in response_lower or 'study' in response_lower:
                return "How do you approach learning new technologies when working on challenging projects?"
            elif len(response) < 20:
                return "I'd love to hear more detail. Can you give me a specific example from your experience?"
            else:
                return self.question_bank['technical'][count % len(self.question_bank['technical'])]
        elif remaining_time < 180:
            return "As we wrap up, what questions do you have about this role or our company?"
        else:
            return self.question_bank['problem_solving'][count % len(self.question_bank['problem_solving'])]
    
    def should_continue(self, count, remaining_time):
        return count < 8 and remaining_time > 60