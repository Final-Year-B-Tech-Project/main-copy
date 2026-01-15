#!/usr/bin/env python3
"""
Resume Parsing Test Script
Usage: python test_resume_parsing.py [resume_file_path]
"""

import os
import sys
import json
from tabulate import tabulate
from app import create_app, db
from app.models import User, StudentProfile, JobDrive, HRProfile
from app.resume_models import CandidateSkill, ParsedResume, JobRequirement, CandidateScore
from app.resume_parser import EnhancedResumeParser
from app.candidate_scoring import CandidateScoringEngine

class ResumeTestSuite:
    def __init__(self):
        self.app = create_app()
        self.parser = EnhancedResumeParser()
        self.scoring_engine = CandidateScoringEngine()
        
    def create_test_data(self):
        """Create test student and job for testing"""
        with self.app.app_context():
            # Create test student
            test_user = User.query.filter_by(username='test_student').first()
            if not test_user:
                test_user = User(
                    username='test_student',
                    email='test@student.com',
                    user_type='student',
                    first_name='Test',
                    last_name='Student',
                    is_active=True
                )
                test_user.set_password('test123')
                db.session.add(test_user)
                db.session.flush()
                
                # Create student profile
                student_profile = StudentProfile(
                    user_id=test_user.id,
                    university='Test University',
                    degree='Bachelor of Technology',
                    graduation_year=2024,
                    experience_level='fresher'
                )
                db.session.add(student_profile)
            
            # Create test HR and job
            test_hr_user = User.query.filter_by(username='test_hr').first()
            if not test_hr_user:
                test_hr_user = User(
                    username='test_hr',
                    email='hr@company.com',
                    user_type='hr',
                    first_name='HR',
                    last_name='Manager',
                    is_active=True
                )
                test_hr_user.set_password('hr123')
                db.session.add(test_hr_user)
                db.session.flush()
                
                # Create HR profile
                hr_profile = HRProfile(
                    user_id=test_hr_user.id,
                    company_name='Test Company',
                    hr_code='HR001'
                )
                db.session.add(hr_profile)
                db.session.flush()
                
                # Create test job
                test_job = JobDrive(
                    hr_id=hr_profile.id,
                    title='Software Developer',
                    job_role='Full Stack Developer',
                    description='Looking for a skilled developer',
                    experience_required='1-3 years',
                    location='Remote',
                    is_active=True
                )
                db.session.add(test_job)
                db.session.flush()
                
                # Create job requirements
                job_req = JobRequirement(
                    job_drive_id=test_job.id,
                    required_skills=json.dumps([
                        {'skill': 'Python', 'importance': 'required', 'min_proficiency': 'intermediate'},
                        {'skill': 'JavaScript', 'importance': 'required', 'min_proficiency': 'beginner'},
                        {'skill': 'React', 'importance': 'preferred', 'min_proficiency': 'beginner'}
                    ]),
                    preferred_skills=json.dumps([
                        {'skill': 'Django', 'importance': 'preferred', 'min_proficiency': 'beginner'},
                        {'skill': 'AWS', 'importance': 'nice-to-have', 'min_proficiency': 'beginner'}
                    ]),
                    min_experience_years=0.5,
                    max_experience_years=3.0,
                    experience_level='entry',
                    min_degree_level='bachelor',
                    location_type='remote'
                )
                db.session.add(job_req)
            
            db.session.commit()
            
            student = StudentProfile.query.filter_by(user_id=test_user.id).first()
            job = JobDrive.query.filter_by(title='Software Developer').first()
            
            return student, job
    
    def test_resume_parsing(self, resume_path):
        """Test resume parsing functionality"""
        print("🔍 Testing Resume Parsing...")
        print("=" * 60)
        
        if not os.path.exists(resume_path):
            print(f"❌ Resume file not found: {resume_path}")
            return None
            
        with self.app.app_context():
            student, job = self.create_test_data()
            
            # Parse resume
            result = self.parser.parse_resume(resume_path, student.id)
            
            if result['success']:
                print("✅ Resume parsing successful!")
                print(f"📊 Processing time: {result['processing_time']:.2f} seconds")
                print(f"🎯 Skills extracted: {result['skills_extracted']}")
                print(f"💼 Total experience: {result['total_experience']} years")
                
                # Display contact info
                if result.get('contact_info'):
                    print("\n📞 Contact Information:")
                    contact_table = []
                    for key, value in result['contact_info'].items():
                        contact_table.append([key.title(), value])
                    print(tabulate(contact_table, headers=['Field', 'Value'], tablefmt='grid'))
                
                return student.id, job.id
            else:
                print(f"❌ Resume parsing failed: {result['error']}")
                return None
    
    def display_parsed_data(self, student_id):
        """Display detailed parsed resume data"""
        with self.app.app_context():
            print("\n📋 Detailed Parsing Results:")
            print("=" * 60)
            
            # Get parsed resume
            parsed_resume = ParsedResume.query.filter_by(student_id=student_id).first()
            if parsed_resume:
                print("\n🎓 Education Data:")
                if parsed_resume.education_data:
                    education = json.loads(parsed_resume.education_data)
                    if education:
                        edu_table = []
                        for edu in education:
                            edu_table.append([
                                edu.get('degree', 'N/A'),
                                edu.get('field', 'N/A'),
                                edu.get('university', 'N/A'),
                                edu.get('year', 'N/A'),
                                edu.get('gpa', 'N/A')
                            ])
                        print(tabulate(edu_table, headers=['Degree', 'Field', 'University', 'Year', 'GPA'], tablefmt='grid'))
                    else:
                        print("No education data extracted")
                
                print("\n💼 Experience Data:")
                if parsed_resume.experience_data:
                    experience = json.loads(parsed_resume.experience_data)
                    if experience:
                        exp_table = []
                        for exp in experience:
                            exp_table.append([
                                exp.get('company', 'N/A'),
                                exp.get('position', 'N/A'),
                                exp.get('duration', 'N/A')
                            ])
                        print(tabulate(exp_table, headers=['Company', 'Position', 'Duration'], tablefmt='grid'))
                    else:
                        print("No experience data extracted")
                
                print("\n🚀 Projects Data:")
                if parsed_resume.projects_data:
                    projects = json.loads(parsed_resume.projects_data)
                    if projects:
                        proj_table = []
                        for proj in projects:
                            technologies = ', '.join(proj.get('technologies', []))
                            proj_table.append([
                                proj.get('name', 'N/A'),
                                proj.get('description', 'N/A')[:50] + '...' if len(proj.get('description', '')) > 50 else proj.get('description', 'N/A'),
                                technologies
                            ])
                        print(tabulate(proj_table, headers=['Project', 'Description', 'Technologies'], tablefmt='grid'))
                    else:
                        print("No projects data extracted")
            
            # Get extracted skills
            skills = CandidateSkill.query.filter_by(student_id=student_id).all()
            if skills:
                print(f"\n🎯 Extracted Skills ({len(skills)} total):")
                
                # Group by category
                skills_by_category = {}
                for skill in skills:
                    category = skill.skill_category or 'other'
                    if category not in skills_by_category:
                        skills_by_category[category] = []
                    skills_by_category[category].append(skill)
                
                for category, category_skills in skills_by_category.items():
                    print(f"\n📂 {category.title()} Skills:")
                    skill_table = []
                    for skill in category_skills:
                        skill_table.append([
                            skill.skill_name,
                            skill.skill_type or 'N/A',
                            skill.proficiency_level or 'N/A',
                            f"{skill.years_experience:.1f}" if skill.years_experience else 'N/A',
                            f"{skill.confidence_score:.2f}" if skill.confidence_score else 'N/A'
                        ])
                    print(tabulate(skill_table, headers=['Skill', 'Type', 'Proficiency', 'Years', 'Confidence'], tablefmt='grid'))
    
    def test_candidate_scoring(self, student_id, job_id):
        """Test candidate scoring functionality"""
        print("\n🎯 Testing Candidate Scoring...")
        print("=" * 60)
        
        with self.app.app_context():
            result = self.scoring_engine.score_candidate_for_job(student_id, job_id)
            
            if result['success']:
                print("✅ Candidate scoring successful!")
                print(f"📊 Overall Score: {result['overall_score']}%")
                print(f"✅ Eligible: {'Yes' if result['is_eligible'] else 'No'}")
                print(f"⭐ Shortlisted: {'Yes' if result['is_shortlisted'] else 'No'}")
                
                # Display score breakdown
                print("\n📈 Score Breakdown:")
                breakdown_table = []
                for category, data in result['breakdown'].items():
                    breakdown_table.append([
                        category.replace('_', ' ').title(),
                        f"{data['score']:.1f}%"
                    ])
                print(tabulate(breakdown_table, headers=['Category', 'Score'], tablefmt='grid'))
                
                # Display skill matches
                skill_data = result['breakdown']['skill_match']
                if skill_data['matched_skills']:
                    print(f"\n✅ Matched Skills ({len(skill_data['matched_skills'])}):")
                    match_table = []
                    for match in skill_data['matched_skills']:
                        match_table.append([
                            match['skill'],
                            match['candidate_proficiency'],
                            match['required_proficiency'],
                            match['match_quality']
                        ])
                    print(tabulate(match_table, headers=['Skill', 'Your Level', 'Required', 'Match'], tablefmt='grid'))
                
                if skill_data['missing_skills']:
                    print(f"\n❌ Missing Skills ({len(skill_data['missing_skills'])}):")
                    missing_table = []
                    for missing in skill_data['missing_skills']:
                        missing_table.append([
                            missing['skill'],
                            missing['required_proficiency'],
                            missing['reason']
                        ])
                    print(tabulate(missing_table, headers=['Skill', 'Required Level', 'Issue'], tablefmt='grid'))
                
                return True
            else:
                print(f"❌ Candidate scoring failed: {result['error']}")
                return False
    
    def display_job_requirements(self, job_id):
        """Display job requirements"""
        with self.app.app_context():
            job = JobDrive.query.get(job_id)
            job_req = JobRequirement.query.filter_by(job_drive_id=job_id).first()
            
            print(f"\n💼 Job: {job.title}")
            print("=" * 60)
            
            if job_req:
                print(f"📋 Experience Required: {job_req.min_experience_years}-{job_req.max_experience_years} years")
                print(f"🎓 Education: {job_req.min_degree_level}")
                print(f"📍 Location: {job_req.location_type}")
                
                if job_req.required_skills:
                    required = json.loads(job_req.required_skills)
                    print(f"\n✅ Required Skills ({len(required)}):")
                    req_table = []
                    for skill in required:
                        req_table.append([
                            skill['skill'],
                            skill['importance'],
                            skill['min_proficiency']
                        ])
                    print(tabulate(req_table, headers=['Skill', 'Importance', 'Min Level'], tablefmt='grid'))

def main():
    # Get resume file path from command line or use default
    if len(sys.argv) > 1:
        resume_path = sys.argv[1]
    else:
        # Look for sample resume in project directory
        possible_files = ['sample_resume.pdf', 'test_resume.pdf', 'resume.pdf']
        resume_path = None
        for file in possible_files:
            if os.path.exists(file):
                resume_path = file
                break
        
        if not resume_path:
            print("❌ No resume file found!")
            print("Usage: python test_resume_parsing.py [resume_file_path]")
            print("Or place a resume file named 'sample_resume.pdf' in the current directory")
            return
    
    print("🚀 Resume Parsing Test Suite")
    print("=" * 60)
    print(f"📄 Testing with: {resume_path}")
    
    # Initialize test suite
    test_suite = ResumeTestSuite()
    
    # Test resume parsing
    result = test_suite.test_resume_parsing(resume_path)
    if not result:
        return
    
    student_id, job_id = result
    
    # Display parsed data
    test_suite.display_parsed_data(student_id)
    
    # Display job requirements
    test_suite.display_job_requirements(job_id)
    
    # Test candidate scoring
    test_suite.test_candidate_scoring(student_id, job_id)
    
    print("\n🎉 Test completed successfully!")
    print("💡 Tip: Check the database dashboard at http://127.0.0.1:5002/admin/db/dashboard")

if __name__ == '__main__':
    main()