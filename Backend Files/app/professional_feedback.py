#!/usr/bin/env python3
"""
Professional Interview Feedback System
Provides honest, strict evaluation based on professional standards
"""

import json
import re
from datetime import datetime

class ProfessionalFeedbackSystem:
    def __init__(self):
        self.evaluation_criteria = {
            'technical_competency': {
                'weight': 0.35,
                'indicators': ['project', 'technology', 'solution', 'implementation', 'architecture', 'algorithm', 'database', 'framework']
            },
            'communication_skills': {
                'weight': 0.25,
                'indicators': ['clear', 'explain', 'articulate', 'detail', 'example', 'specific', 'understand']
            },
            'problem_solving': {
                'weight': 0.20,
                'indicators': ['challenge', 'problem', 'solve', 'approach', 'analyze', 'debug', 'troubleshoot']
            },
            'experience_depth': {
                'weight': 0.20,
                'indicators': ['experience', 'worked', 'built', 'developed', 'managed', 'led', 'responsible']
            }
        }
        
        self.performance_thresholds = {
            'excellent': 85,
            'good': 70,
            'average': 55,
            'below_average': 40,
            'poor': 0
        }
    
    def evaluate_interview_responses(self, responses, job_role="General", security_data=None):
        """
        Provide professional, honest evaluation of interview responses
        """
        if not responses or len(responses) == 0:
            return self._generate_no_response_feedback()
        
        # Analyze all responses
        analysis = self._analyze_responses(responses)
        
        # Calculate scores based on professional criteria
        scores = self._calculate_professional_scores(analysis, job_role)
        
        # Generate honest feedback with security data
        feedback = self._generate_professional_feedback(analysis, scores, job_role, len(responses), security_data)
        
        return feedback
    
    def _analyze_responses(self, responses):
        """Analyze responses for professional indicators"""
        analysis = {
            'total_words': 0,
            'avg_response_length': 0,
            'technical_indicators': 0,
            'communication_quality': 0,
            'problem_solving_evidence': 0,
            'experience_indicators': 0,
            'vague_responses': 0,
            'detailed_responses': 0,
            'professional_language': 0,
            'specific_examples': 0
        }
        
        all_text = ""
        response_lengths = []
        
        for response_data in responses:
            if isinstance(response_data, dict):
                answer = response_data.get('answer', '')
            else:
                answer = str(response_data)
            
            if not answer:
                continue
                
            all_text += " " + answer.lower()
            words = answer.split()
            response_lengths.append(len(words))
            analysis['total_words'] += len(words)
            
            # Analyze response quality
            if len(words) < 10:
                analysis['vague_responses'] += 1
            elif len(words) > 30:
                analysis['detailed_responses'] += 1
            
            # Check for specific examples
            if any(indicator in answer.lower() for indicator in ['for example', 'specifically', 'instance', 'case', 'situation']):
                analysis['specific_examples'] += 1
        
        # Calculate averages
        if response_lengths:
            analysis['avg_response_length'] = sum(response_lengths) / len(response_lengths)
        
        # Count professional indicators
        for criteria, data in self.evaluation_criteria.items():
            count = sum(1 for indicator in data['indicators'] if indicator in all_text)
            if criteria == 'technical_competency':
                analysis['technical_indicators'] = count
            elif criteria == 'communication_skills':
                analysis['communication_quality'] = count
            elif criteria == 'problem_solving':
                analysis['problem_solving_evidence'] = count
            elif criteria == 'experience_depth':
                analysis['experience_indicators'] = count
        
        return analysis
    
    def _calculate_professional_scores(self, analysis, job_role):
        """Calculate scores based on professional standards - RAW AUTHENTIC SCORING"""
        scores = {}
        
        # Technical Score (0-100) - NO BASE POINTS
        tech_base = min(100, analysis['technical_indicators'] * 12)
        if analysis['avg_response_length'] < 15:
            tech_base *= 0.7
        scores['technical_score'] = int(min(100, tech_base))
        
        # Communication Score (0-100) - NO BASE POINTS
        comm_base = min(100, analysis['communication_quality'] * 10 + analysis['specific_examples'] * 8)
        if analysis['vague_responses'] > analysis['detailed_responses']:
            comm_base *= 0.6
        scores['communication_score'] = int(min(100, comm_base))
        
        # Problem Solving Score (0-100) - NO BASE POINTS
        prob_base = min(100, analysis['problem_solving_evidence'] * 15)
        if analysis['avg_response_length'] < 20:
            prob_base *= 0.7
        scores['problem_solving_score'] = int(min(100, prob_base))
        
        # Experience Score (0-100) - NO BASE POINTS
        exp_base = min(100, analysis['experience_indicators'] * 12)
        scores['experience_score'] = int(min(100, exp_base))
        
        # Overall Score (weighted average) - RAW CALCULATION
        overall = (
            scores['technical_score'] * 0.35 +
            scores['communication_score'] * 0.25 +
            scores['problem_solving_score'] * 0.20 +
            scores['experience_score'] * 0.20
        )
        scores['overall_score'] = int(overall)
        
        return scores
    
    def _generate_professional_feedback(self, analysis, scores, job_role, response_count, security_data=None):
        """Generate honest, professional feedback"""
        
        # Determine performance level
        overall_score = scores['overall_score']
        if overall_score >= 85:
            performance_level = "Excellent"
            level_description = "demonstrates strong competency"
        elif overall_score >= 70:
            performance_level = "Good"
            level_description = "shows adequate skills with room for improvement"
        elif overall_score >= 55:
            performance_level = "Average"
            level_description = "meets basic requirements but needs development"
        elif overall_score >= 40:
            performance_level = "Below Average"
            level_description = "requires significant improvement"
        else:
            performance_level = "Poor"
            level_description = "does not meet professional standards"
        
        # Generate specific strengths
        strengths = []
        if scores['technical_score'] >= 70:
            strengths.append("Demonstrates technical knowledge relevant to the role")
        if scores['communication_score'] >= 70:
            strengths.append("Communicates ideas clearly and provides specific examples")
        if scores['problem_solving_score'] >= 70:
            strengths.append("Shows problem-solving approach and analytical thinking")
        if analysis['detailed_responses'] > analysis['vague_responses']:
            strengths.append("Provides detailed responses with context")
        if analysis['specific_examples'] > 0:
            strengths.append("Uses concrete examples to illustrate points")
        
        if not strengths:
            strengths = ["Completed the interview process", "Showed willingness to participate"]
        
        # Generate specific weaknesses
        weaknesses = []
        if scores['technical_score'] < 60:
            weaknesses.append("Limited demonstration of technical skills and knowledge")
        if scores['communication_score'] < 60:
            weaknesses.append("Responses lack clarity and specific examples")
        if scores['problem_solving_score'] < 60:
            weaknesses.append("Insufficient evidence of problem-solving capabilities")
        if analysis['vague_responses'] > analysis['detailed_responses']:
            weaknesses.append("Many responses are too brief and lack detail")
        if analysis['avg_response_length'] < 15:
            weaknesses.append("Responses are generally too short for professional evaluation")
        if analysis['specific_examples'] == 0:
            weaknesses.append("No concrete examples provided to support claims")
        
        # Generate improvement recommendations
        recommendations = []
        if scores['technical_score'] < 70:
            recommendations.append(f"Strengthen technical knowledge in {job_role} domain")
        if scores['communication_score'] < 70:
            recommendations.append("Practice articulating ideas with specific examples and details")
        if analysis['avg_response_length'] < 20:
            recommendations.append("Provide more comprehensive responses that fully address questions")
        if analysis['specific_examples'] < 2:
            recommendations.append("Use concrete examples from experience to illustrate capabilities")
        
        # Generate honest summary
        if overall_score >= 75:
            summary = f"Candidate demonstrates competency for {job_role} role with {overall_score}/100 overall performance."
        elif overall_score >= 60:
            summary = f"Candidate shows potential but needs improvement in key areas. Score: {overall_score}/100."
        else:
            summary = f"Candidate requires significant development before being ready for {job_role} role. Score: {overall_score}/100."
        
        # Process security data
        security_report = self._generate_security_report(security_data) if security_data else None
        
        feedback = {
            "overall_score": overall_score,
            "technical_score": scores['technical_score'],
            "communication_score": scores['communication_score'],
            "confidence_score": scores.get('problem_solving_score', 60),
            "performance_level": performance_level,
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5],
            "recommendations": recommendations,
            "summary": summary,
            "evaluation_details": {
                "total_responses": response_count,
                "avg_response_length": analysis['avg_response_length'],
                "technical_indicators": analysis['technical_indicators'],
                "specific_examples": analysis['specific_examples'],
                "detailed_responses": analysis['detailed_responses'],
                "vague_responses": analysis['vague_responses']
            }
        }
        
        if security_report:
            feedback['security_report'] = security_report
        
        return feedback
    
    def _generate_security_report(self, security_data):
        """Generate security and behavioral analysis report"""
        tab_switches = security_data.get('tab_switches', 0)
        violations = security_data.get('violations', 0)
        face_detections = security_data.get('face_detections', [])
        
        # Analyze face detection data
        multiple_faces = sum(1 for f in face_detections if f.get('count', 1) > 1)
        no_face = sum(1 for f in face_detections if f.get('count', 0) == 0)
        
        # Determine integrity level
        if violations == 0 and tab_switches == 0 and multiple_faces == 0 and no_face == 0:
            integrity = "Excellent"
            integrity_score = 100
        elif violations <= 2 and tab_switches <= 1:
            integrity = "Good"
            integrity_score = 80
        elif violations <= 5 and tab_switches <= 3:
            integrity = "Fair"
            integrity_score = 60
        else:
            integrity = "Poor"
            integrity_score = 40
        
        issues = []
        if tab_switches > 0:
            issues.append(f"Switched tabs {tab_switches} time(s) during interview")
        if multiple_faces > 0:
            issues.append(f"Multiple faces detected {multiple_faces} time(s)")
        if no_face > 0:
            issues.append(f"No face detected {no_face} time(s)")
        if violations > tab_switches:
            issues.append(f"Exited fullscreen {violations - tab_switches} time(s)")
        
        return {
            "integrity_level": integrity,
            "integrity_score": integrity_score,
            "tab_switches": tab_switches,
            "total_violations": violations,
            "face_analysis": {
                "multiple_faces_detected": multiple_faces,
                "no_face_detected": no_face,
                "total_checks": len(face_detections)
            },
            "issues": issues if issues else ["No security issues detected"],
            "recommendation": "Clean interview" if integrity_score >= 80 else "Review security concerns"
        }
    
    def _generate_no_response_feedback(self):
        """Feedback for candidates who provided no responses"""
        return {
            "overall_score": 0,
            "technical_score": 0,
            "communication_score": 0,
            "confidence_score": 0,
            "performance_level": "Incomplete",
            "strengths": ["Attended the interview session"],
            "weaknesses": [
                "No responses provided during interview",
                "Unable to assess technical capabilities",
                "Communication skills could not be evaluated"
            ],
            "recommendations": [
                "Practice interview skills and preparation",
                "Ensure technical setup allows for proper participation",
                "Prepare specific examples from experience"
            ],
            "summary": "Interview could not be completed due to lack of responses. Score: 0/100.",
            "evaluation_details": {
                "total_responses": 0,
                "avg_response_length": 0,
                "technical_indicators": 0,
                "specific_examples": 0,
                "detailed_responses": 0,
                "vague_responses": 0
            }
        }

def generate_professional_feedback(ai_service, responses, job_role="General", security_data=None):
    """
    Main function to generate professional feedback
    """
    feedback_system = ProfessionalFeedbackSystem()
    return feedback_system.evaluate_interview_responses(responses, job_role, security_data)