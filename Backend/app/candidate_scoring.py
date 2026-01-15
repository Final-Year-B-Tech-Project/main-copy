import json
from typing import Dict, List, Tuple
from app import db
from app.models import StudentProfile, JobDrive
from app.resume_models import CandidateSkill, ParsedResume, JobRequirement, CandidateScore

class CandidateScoringEngine:
    """Advanced candidate scoring and shortlisting system"""
    
    def __init__(self):
        self.scoring_weights = {
            'skill_match': 0.40,    # 40%
            'experience': 0.30,     # 30%
            'education': 0.20,      # 20%
            'other': 0.10          # 10%
        }
        self.eligibility_threshold = 30.0  # 30% minimum for eligibility
        self.shortlist_threshold = 75.0    # 75% for shortlisting
    
    def score_candidate_for_job(self, student_id: int, job_drive_id: int) -> Dict:
        """Score a candidate for a specific job"""
        try:
            # Get candidate and job data
            student = StudentProfile.query.get(student_id)
            job = JobDrive.query.get(job_drive_id)
            job_req = JobRequirement.query.filter_by(job_drive_id=job_drive_id).first()
            
            if not all([student, job, job_req]):
                return {'success': False, 'error': 'Missing data'}
            
            # Calculate individual scores
            skill_score = self._calculate_skill_match_score(student_id, job_req)
            experience_score = self._calculate_experience_score(student_id, job_req)
            education_score = self._calculate_education_score(student_id, job_req)
            other_score = self._calculate_other_score(student_id, job_req)
            
            # Calculate weighted overall score
            overall_score = (
                skill_score['score'] * self.scoring_weights['skill_match'] +
                experience_score['score'] * self.scoring_weights['experience'] +
                education_score['score'] * self.scoring_weights['education'] +
                other_score['score'] * self.scoring_weights['other']
            )
            
            # Determine eligibility
            is_eligible = overall_score >= self.eligibility_threshold
            is_shortlisted = overall_score >= self.shortlist_threshold
            
            # Save score to database
            candidate_score = self._save_candidate_score(
                student_id, job_drive_id, skill_score, experience_score,
                education_score, other_score, overall_score, is_eligible, is_shortlisted
            )
            
            return {
                'success': True,
                'candidate_score_id': candidate_score.id,
                'overall_score': round(overall_score, 2),
                'is_eligible': is_eligible,
                'is_shortlisted': is_shortlisted,
                'breakdown': {
                    'skill_match': skill_score,
                    'experience': experience_score,
                    'education': education_score,
                    'other': other_score
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_skill_match_score(self, student_id: int, job_req: JobRequirement) -> Dict:
        """Calculate skill matching score using consolidated skills from student profile"""
        from app.models import StudentProfile
        
        # Get candidate skills from student profile
        student_profile = StudentProfile.query.get(student_id)
        if not student_profile or not student_profile.skills:
            return {
                'score': 0,
                'matched_skills': [],
                'missing_skills': [],
                'match_percentage': 0
            }
        
        # Parse candidate skills from JSON
        candidate_skills_data = json.loads(student_profile.skills)
        candidate_skill_names = {skill['skill_name'].lower(): skill for skill in candidate_skills_data}
        
        # Parse job requirements
        required_skills = json.loads(job_req.required_skills or '[]')
        preferred_skills = json.loads(job_req.preferred_skills or '[]')
        
        matched_skills = []
        missing_skills = []
        total_weight = 0
        matched_weight = 0
        
        # Check required skills
        for skill_req in required_skills:
            skill_name = skill_req['skill'].lower()
            importance = skill_req.get('importance', 'required')  # required, preferred, nice-to-have
            min_proficiency = skill_req.get('min_proficiency', 'beginner')
            
            # Weight based on importance
            weight = {'required': 3, 'preferred': 2, 'nice-to-have': 1}.get(importance, 2)
            total_weight += weight
            
            if skill_name in candidate_skill_names:
                candidate_skill = candidate_skill_names[skill_name]
                
                # Check proficiency match
                proficiency_match = self._check_proficiency_match(
                    candidate_skill['proficiency_level'], min_proficiency
                )
                
                if proficiency_match:
                    matched_weight += weight
                    matched_skills.append({
                        'skill': skill_req['skill'],
                        'candidate_proficiency': candidate_skill['proficiency_level'],
                        'required_proficiency': min_proficiency,
                        'match_quality': 'exact' if candidate_skill['proficiency_level'] == min_proficiency else 'exceeds'
                    })
                else:
                    missing_skills.append({
                        'skill': skill_req['skill'],
                        'required_proficiency': min_proficiency,
                        'candidate_proficiency': candidate_skill['proficiency_level'],
                        'reason': 'proficiency_gap'
                    })
            else:
                missing_skills.append({
                    'skill': skill_req['skill'],
                    'required_proficiency': min_proficiency,
                    'reason': 'skill_missing'
                })
        
        # Calculate score
        score = (matched_weight / total_weight * 100) if total_weight > 0 else 0
        
        return {
            'score': min(100, score),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'match_percentage': round(len(matched_skills) / len(required_skills) * 100, 1) if required_skills else 100
        }
    
    def _calculate_experience_score(self, student_id: int, job_req: JobRequirement) -> Dict:
        """Calculate experience matching score"""
        # Get parsed resume data
        parsed_resume = ParsedResume.query.filter_by(student_id=student_id).first()
        student = StudentProfile.query.get(student_id)
        
        candidate_experience = 0
        if parsed_resume and parsed_resume.total_experience_years:
            candidate_experience = parsed_resume.total_experience_years
        elif student and student.experience_level:
            # Estimate based on experience level
            exp_mapping = {'fresher': 0, 'entry': 1, 'mid': 3, 'senior': 7}
            candidate_experience = exp_mapping.get(student.experience_level, 0)
        
        min_exp = job_req.min_experience_years or 0
        max_exp = job_req.max_experience_years or 20
        
        # Score calculation
        if candidate_experience < min_exp:
            # Below minimum - penalize
            gap = min_exp - candidate_experience
            score = max(0, 100 - (gap * 20))  # -20 points per year gap
        elif candidate_experience > max_exp:
            # Over-qualified - slight penalty
            excess = candidate_experience - max_exp
            score = max(70, 100 - (excess * 5))  # -5 points per excess year
        else:
            # Within range - full score
            score = 100
        
        return {
            'score': score,
            'candidate_experience': candidate_experience,
            'required_range': f"{min_exp}-{max_exp} years",
            'match_status': 'perfect' if min_exp <= candidate_experience <= max_exp else 
                           'under_qualified' if candidate_experience < min_exp else 'over_qualified'
        }
    
    def _calculate_education_score(self, student_id: int, job_req: JobRequirement) -> Dict:
        """Calculate education matching score"""
        student = StudentProfile.query.get(student_id)
        parsed_resume = ParsedResume.query.filter_by(student_id=student_id).first()
        
        score = 50  # Base score
        education_details = {}
        
        # Check degree level
        if job_req.min_degree_level:
            degree_hierarchy = {'bachelor': 1, 'master': 2, 'phd': 3}
            required_level = degree_hierarchy.get(job_req.min_degree_level.lower(), 1)
            
            candidate_level = 0
            if student and student.degree:
                if any(term in student.degree.lower() for term in ['phd', 'doctorate']):
                    candidate_level = 3
                elif any(term in student.degree.lower() for term in ['master', 'mba', 'ms', 'ma']):
                    candidate_level = 2
                elif any(term in student.degree.lower() for term in ['bachelor', 'bs', 'ba', 'btech']):
                    candidate_level = 1
            
            if candidate_level >= required_level:
                score += 30
                education_details['degree_match'] = 'meets_requirement'
            else:
                education_details['degree_match'] = 'below_requirement'
        
        # Check GPA
        if job_req.min_gpa and student and student.gpa:
            if student.gpa >= job_req.min_gpa:
                score += 20
                education_details['gpa_match'] = 'meets_requirement'
            else:
                education_details['gpa_match'] = 'below_requirement'
        
        return {
            'score': min(100, score),
            'details': education_details,
            'candidate_degree': student.degree if student else None,
            'candidate_gpa': student.gpa if student else None
        }
    
    def _calculate_other_score(self, student_id: int, job_req: JobRequirement) -> Dict:
        """Calculate other factors score (location, availability, etc.)"""
        score = 80  # Base score for other factors
        
        factors = {
            'location_preference': 'compatible',  # Simplified
            'availability': 'immediate',
            'cultural_fit': 'good'
        }
        
        return {
            'score': score,
            'factors': factors
        }
    
    def _check_proficiency_match(self, candidate_level: str, required_level: str) -> bool:
        """Check if candidate proficiency meets requirement"""
        proficiency_hierarchy = {'beginner': 1, 'intermediate': 2, 'expert': 3}
        
        candidate_score = proficiency_hierarchy.get(candidate_level, 1)
        required_score = proficiency_hierarchy.get(required_level, 1)
        
        return candidate_score >= required_score
    
    def _save_candidate_score(self, student_id: int, job_drive_id: int, skill_score: Dict,
                            experience_score: Dict, education_score: Dict, other_score: Dict,
                            overall_score: float, is_eligible: bool, is_shortlisted: bool) -> CandidateScore:
        """Save candidate score to database"""
        
        # Check if score already exists
        existing_score = CandidateScore.query.filter_by(
            student_id=student_id, job_drive_id=job_drive_id
        ).first()
        
        if existing_score:
            # Update existing score
            candidate_score = existing_score
        else:
            # Create new score
            candidate_score = CandidateScore(
                student_id=student_id,
                job_drive_id=job_drive_id
            )
        
        # Update scores
        candidate_score.skill_match_score = skill_score['score']
        candidate_score.experience_score = experience_score['score']
        candidate_score.education_score = education_score['score']
        candidate_score.other_score = other_score['score']
        candidate_score.overall_score = overall_score
        candidate_score.is_eligible = is_eligible
        candidate_score.is_shortlisted = is_shortlisted
        
        # Save detailed breakdown
        candidate_score.skill_matches = json.dumps(skill_score['matched_skills'])
        candidate_score.missing_skills = json.dumps(skill_score['missing_skills'])
        candidate_score.score_breakdown = json.dumps({
            'skill_match': skill_score,
            'experience': experience_score,
            'education': education_score,
            'other': other_score
        })
        
        if is_shortlisted:
            candidate_score.shortlist_reason = f"Overall score: {overall_score:.1f}% - Strong match"
            candidate_score.shortlisted_at = db.func.now()
        
        if not existing_score:
            db.session.add(candidate_score)
        
        db.session.commit()
        return candidate_score
    
    def get_shortlisted_candidates(self, job_drive_id: int, limit: int = 10) -> List[Dict]:
        """Get top shortlisted candidates for a job"""
        shortlisted = CandidateScore.query.filter_by(
            job_drive_id=job_drive_id,
            is_shortlisted=True
        ).order_by(CandidateScore.overall_score.desc()).limit(limit).all()
        
        candidates = []
        for score in shortlisted:
            student = StudentProfile.query.get(score.student_id)
            if student:
                candidates.append({
                    'student_id': score.student_id,
                    'name': student.user.full_name,
                    'email': student.user.email,
                    'overall_score': score.overall_score,
                    'skill_match_score': score.skill_match_score,
                    'experience_score': score.experience_score,
                    'shortlisted_at': score.shortlisted_at,
                    'shortlist_reason': score.shortlist_reason
                })
        
        return candidates
    
    def bulk_score_candidates(self, job_drive_id: int) -> Dict:
        """Score all eligible candidates for a job"""
        # Get all students with resumes
        students_with_resumes = db.session.query(StudentProfile).join(ParsedResume).all()
        
        results = {
            'total_candidates': len(students_with_resumes),
            'scored': 0,
            'eligible': 0,
            'shortlisted': 0,
            'errors': []
        }
        
        for student in students_with_resumes:
            try:
                score_result = self.score_candidate_for_job(student.id, job_drive_id)
                if score_result['success']:
                    results['scored'] += 1
                    if score_result['is_eligible']:
                        results['eligible'] += 1
                    if score_result['is_shortlisted']:
                        results['shortlisted'] += 1
                else:
                    results['errors'].append(f"Student {student.id}: {score_result['error']}")
            except Exception as e:
                results['errors'].append(f"Student {student.id}: {str(e)}")
        
        return results