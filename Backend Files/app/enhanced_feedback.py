#!/usr/bin/env python3
"""
Enhanced Feedback System with Conversation History
"""

import json
from datetime import datetime

class EnhancedFeedbackGenerator:
    def __init__(self):
        self.phase_weights = {
            "introduction": 0.15,
            "technical": 0.35,
            "experience": 0.25,
            "behavioral": 0.20,
            "closing": 0.05
        }
    
    def generate_comprehensive_feedback(self, responses, job_role="General"):
        """Generate detailed feedback with conversation history"""
        
        # Analyze responses by phase
        phase_analysis = self._analyze_by_phases(responses)
        
        # Calculate scores
        scores = self._calculate_detailed_scores(responses, phase_analysis)
        
        # Generate conversation summary
        conversation_history = self._format_conversation_history(responses)
        
        # Create comprehensive feedback
        feedback = {
            "overall_score": scores["overall"],
            "technical_score": scores["technical"],
            "communication_score": scores["communication"],
            "confidence_score": scores["confidence"],
            "problem_solving_score": scores["problem_solving"],
            "leadership_score": scores["leadership"],
            "adaptability_score": scores["adaptability"],
            
            "phase_breakdown": phase_analysis,
            "conversation_history": conversation_history,
            
            "strengths": self._identify_strengths(responses, scores),
            "weaknesses": self._identify_weaknesses(responses, scores),
            "improvement_areas": self._suggest_improvements(responses, scores, job_role),
            
            "detailed_analysis": {
                "communication": self._analyze_communication(responses),
                "technical_skills": self._analyze_technical_skills(responses, job_role),
                "problem_solving": self._analyze_problem_solving(responses),
                "cultural_fit": self._analyze_cultural_fit(responses)
            },
            
            "recommendations": self._generate_recommendations(responses, scores, job_role),
            "summary": self._generate_summary(scores, job_role),
            "next_steps": self._suggest_next_steps(scores, job_role),
            
            "interview_metadata": {
                "total_questions": len(responses),
                "total_duration": self._calculate_total_duration(responses),
                "average_response_time": self._calculate_avg_response_time(responses),
                "job_role": job_role,
                "interview_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        return feedback
    
    def _analyze_by_phases(self, responses):
        """Analyze responses by interview phases"""
        phases = {
            "introduction": [],
            "technical": [],
            "experience": [],
            "behavioral": [],
            "closing": []
        }
        
        # Simple phase detection based on question content and order
        for i, response in enumerate(responses):
            question = response.get('question', '').lower()
            
            if i < 2 or any(word in question for word in ['introduce', 'background', 'about yourself']):
                phases["introduction"].append(response)
            elif any(word in question for word in ['technical', 'programming', 'skills', 'technology']):
                phases["technical"].append(response)
            elif any(word in question for word in ['project', 'experience', 'work', 'internship']):
                phases["experience"].append(response)
            elif any(word in question for word in ['challenge', 'team', 'problem', 'situation']):
                phases["behavioral"].append(response)
            else:
                phases["closing"].append(response)
        
        # Analyze each phase
        phase_analysis = {}
        for phase, phase_responses in phases.items():
            if phase_responses:
                phase_analysis[phase] = {
                    "question_count": len(phase_responses),
                    "avg_response_length": sum(len(r.get('answer', '').split()) for r in phase_responses) / len(phase_responses),
                    "quality_score": self._score_phase_quality(phase_responses),
                    "key_responses": [r.get('answer', '')[:100] + "..." if len(r.get('answer', '')) > 100 else r.get('answer', '') for r in phase_responses[:2]]
                }
        
        return phase_analysis
    
    def _calculate_detailed_scores(self, responses, phase_analysis):
        """Calculate detailed scores based on response quality"""
        
        total_words = sum(len(r.get('answer', '').split()) for r in responses)
        avg_words_per_response = total_words / len(responses) if responses else 0
        
        # Base scoring
        base_score = min(85, 40 + (avg_words_per_response * 2))
        
        # Adjust based on response quality
        quality_bonus = 0
        for response in responses:
            answer = response.get('answer', '').lower()
            
            # Positive indicators
            if any(word in answer for word in ['experience', 'project', 'learned', 'developed']):
                quality_bonus += 3
            if any(word in answer for word in ['team', 'collaboration', 'worked with']):
                quality_bonus += 2
            if len(answer.split()) >= 15:
                quality_bonus += 2
            
            # Negative indicators
            if any(phrase in answer for phrase in ['nothing', "don't have", "no experience", "never"]):
                quality_bonus -= 5
            if len(answer.split()) < 3:
                quality_bonus -= 3
        
        overall = max(25, min(95, base_score + quality_bonus))
        
        return {
            "overall": overall,
            "technical": max(20, min(90, overall - 5 + (quality_bonus // 2))),
            "communication": max(30, min(95, overall + 5)),
            "confidence": max(25, min(85, overall - 10 + quality_bonus)),
            "problem_solving": max(20, min(88, overall - 8)),
            "leadership": max(15, min(80, overall - 15)),
            "adaptability": max(25, min(90, overall))
        }
    
    def _format_conversation_history(self, responses):
        """Format complete conversation history"""
        conversation = []
        
        for i, response in enumerate(responses, 1):
            conversation.append({
                "question_number": i,
                "question": response.get('question', f'Question {i}'),
                "candidate_response": response.get('answer', 'No response'),
                "response_time_seconds": response.get('response_time', 0),
                "word_count": len(response.get('answer', '').split()),
                "timestamp": response.get('timestamp', datetime.now().isoformat())
            })
        
        return conversation
    
    def _score_phase_quality(self, phase_responses):
        """Score quality of responses in a phase"""
        if not phase_responses:
            return 0
        
        total_score = 0
        for response in phase_responses:
            answer = response.get('answer', '')
            word_count = len(answer.split())
            
            # Basic scoring
            score = min(100, word_count * 3)
            
            # Quality indicators
            if any(word in answer.lower() for word in ['because', 'example', 'specifically']):
                score += 10
            if word_count >= 20:
                score += 15
            
            total_score += score
        
        return min(100, total_score // len(phase_responses))
    
    def _identify_strengths(self, responses, scores):
        """Identify candidate strengths"""
        strengths = []
        
        if scores["communication"] >= 70:
            strengths.append("Good communication skills demonstrated")
        if scores["overall"] >= 75:
            strengths.append("Strong overall interview performance")
        if any(len(r.get('answer', '').split()) >= 20 for r in responses):
            strengths.append("Provides detailed responses when engaged")
        if scores["technical"] >= 60:
            strengths.append("Shows technical awareness")
        
        return strengths if strengths else ["Completed the interview", "Shows willingness to participate"]
    
    def _identify_weaknesses(self, responses, scores):
        """Identify areas for improvement"""
        weaknesses = []
        
        if scores["communication"] < 60:
            weaknesses.append("Could provide more detailed responses")
        if scores["technical"] < 50:
            weaknesses.append("Technical knowledge needs development")
        if any("nothing" in r.get('answer', '').lower() for r in responses):
            weaknesses.append("Avoid negative responses, focus on learning experiences")
        if sum(len(r.get('answer', '').split()) for r in responses) < 50:
            weaknesses.append("Responses could be more comprehensive")
        
        return weaknesses if weaknesses else ["Continue developing professional communication"]
    
    def _suggest_improvements(self, responses, scores, job_role):
        """Suggest specific improvement areas"""
        improvements = []
        
        if scores["technical"] < 70:
            improvements.append(f"Strengthen technical skills relevant to {job_role}")
        if scores["communication"] < 70:
            improvements.append("Practice structured response techniques (STAR method)")
        if scores["problem_solving"] < 60:
            improvements.append("Prepare examples of problem-solving experiences")
        
        improvements.append("Practice interview scenarios regularly")
        return improvements
    
    def _analyze_communication(self, responses):
        """Analyze communication skills"""
        total_words = sum(len(r.get('answer', '').split()) for r in responses)
        avg_words = total_words / len(responses) if responses else 0
        
        if avg_words >= 15:
            return "Demonstrates good verbal communication with detailed responses"
        elif avg_words >= 8:
            return "Shows basic communication skills, could be more detailed"
        else:
            return "Communication skills need development - practice providing more comprehensive answers"
    
    def _analyze_technical_skills(self, responses, job_role):
        """Analyze technical competency"""
        technical_keywords = ['programming', 'coding', 'software', 'technology', 'technical', 'development']
        
        technical_mentions = sum(1 for r in responses 
                               if any(keyword in r.get('answer', '').lower() 
                                    for keyword in technical_keywords))
        
        if technical_mentions >= 2:
            return f"Shows awareness of technical concepts relevant to {job_role}"
        elif technical_mentions >= 1:
            return f"Basic technical understanding, continue learning {job_role} skills"
        else:
            return f"Focus on developing technical knowledge for {job_role} role"
    
    def _analyze_problem_solving(self, responses):
        """Analyze problem-solving approach"""
        problem_indicators = ['challenge', 'problem', 'solution', 'approach', 'method']
        
        problem_responses = [r for r in responses 
                           if any(indicator in r.get('answer', '').lower() 
                                for indicator in problem_indicators)]
        
        if problem_responses:
            return "Shows problem-solving awareness, continue developing structured approaches"
        else:
            return "Practice describing problem-solving experiences and methodologies"
    
    def _analyze_cultural_fit(self, responses):
        """Analyze cultural fit indicators"""
        positive_indicators = ['team', 'collaboration', 'learning', 'growth', 'help']
        
        cultural_score = sum(1 for r in responses 
                           if any(indicator in r.get('answer', '').lower() 
                                for indicator in positive_indicators))
        
        if cultural_score >= 2:
            return "Demonstrates positive attitude and team-oriented mindset"
        else:
            return "Shows potential for growth and learning in team environments"
    
    def _generate_recommendations(self, responses, scores, job_role):
        """Generate specific recommendations"""
        recommendations = []
        
        if scores["overall"] < 60:
            recommendations.append("Focus on interview preparation and practice")
        if scores["technical"] < 70:
            recommendations.append(f"Study technical concepts relevant to {job_role}")
        
        recommendations.extend([
            "Practice the STAR method for behavioral questions",
            "Prepare specific examples from your experience",
            "Research the company and role thoroughly"
        ])
        
        return recommendations
    
    def _generate_summary(self, scores, job_role):
        """Generate interview summary"""
        if scores["overall"] >= 80:
            return f"Strong interview performance for {job_role} position. Candidate shows good potential."
        elif scores["overall"] >= 60:
            return f"Satisfactory interview performance with room for improvement in {job_role} skills."
        else:
            return f"Interview completed with significant areas for development before pursuing {job_role} roles."
    
    def _suggest_next_steps(self, scores, job_role):
        """Suggest concrete next steps"""
        if scores["overall"] >= 75:
            return f"Continue developing {job_role} skills and apply to relevant positions"
        elif scores["overall"] >= 50:
            return f"Focus on skill development and practice more interviews for {job_role} roles"
        else:
            return f"Invest time in learning fundamentals and building experience in {job_role} field"
    
    def _calculate_total_duration(self, responses):
        """Calculate total interview duration"""
        return sum(r.get('response_time', 120) for r in responses)
    
    def _calculate_avg_response_time(self, responses):
        """Calculate average response time"""
        times = [r.get('response_time', 120) for r in responses]
        return sum(times) / len(times) if times else 120