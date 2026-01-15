#!/usr/bin/env python3
"""
Complete System Test - Job Creation, Candidate Matching, and Question Generation
"""

from app import create_app, db
from app.models import User, StudentProfile, JobDrive, HRProfile
from app.resume_models import JobRequirement, CandidateScore
from app.job_parser import JobDescriptionParser
from app.candidate_scoring import CandidateScoringEngine
from app.question_generator import SkillBasedQuestionGenerator
import json

def test_complete_workflow():
    """Test the complete workflow from job creation to question generation"""
    
    app = create_app()
    with app.app_context():
        print("🚀 Testing Complete Workflow")
        print("=" * 60)
        
        # Test job description parsing
        print("\n1. 📋 Testing Job Description Parsing...")
        
        job_description = """
        We are looking for a Data Analyst with strong Python and SQL skills.
        The ideal candidate should have 2-4 years of experience in data analysis,
        machine learning, and statistical modeling. Knowledge of pandas, numpy,
        and scikit-learn is required. Experience with AWS and Docker is preferred.
        Strong communication and problem-solving skills are essential.
        """
        
        parser = JobDescriptionParser()
        parsed_job = parser.parse_job_description(job_description, "Data Analyst", "Data Scientist")
        
        print(f"✅ Parsed {len(parsed_job['required_skills'])} required skills")
        print(f"✅ Parsed {len(parsed_job['preferred_skills'])} preferred skills")
        print(f"✅ Experience: {parsed_job['experience_requirements']['min_years']}-{parsed_job['experience_requirements']['max_years']} years")
        print(f"✅ Job Category: {parsed_job['job_category']}")
        
        # Show extracted skills
        print("\n📊 Required Skills:")
        for skill in parsed_job['required_skills'][:5]:
            print(f"  • {skill['skill']} ({skill['importance']}, {skill['min_proficiency']})")
        
        # Test candidate scoring with 30% threshold
        print("\n2. 🎯 Testing Candidate Scoring (30% threshold)...")
        
        # Get a student with resume data
        student = db.session.query(StudentProfile).join(User).filter(
            User.user_type == 'student'
        ).first()
        
        if student:
            # Create a test job drive
            hr_user = User.query.filter_by(user_type='hr').first()
            if hr_user and hr_user.hr_profile:
                test_job = JobDrive(
                    hr_id=hr_user.hr_profile.id,
                    title="Data Analyst",
                    job_role="Data Scientist",
                    description=job_description,
                    experience_required="2-4 years",
                    location="Remote",
                    is_active=True
                )
                db.session.add(test_job)
                db.session.flush()
                
                # Create job requirements
                job_req = JobRequirement(
                    job_drive_id=test_job.id,
                    required_skills=json.dumps(parsed_job['required_skills']),
                    preferred_skills=json.dumps(parsed_job['preferred_skills']),
                    min_experience_years=parsed_job['experience_requirements']['min_years'],
                    max_experience_years=parsed_job['experience_requirements']['max_years'],
                    experience_level=parsed_job['experience_requirements']['level'],
                    min_degree_level='bachelor',
                    location_type='remote'
                )
                db.session.add(job_req)
                db.session.commit()
                
                # Score the candidate
                scoring_engine = CandidateScoringEngine()
                scoring_engine.eligibility_threshold = 30.0  # 30% threshold
                
                result = scoring_engine.score_candidate_for_job(student.id, test_job.id)
                
                if result['success']:
                    print(f"✅ Candidate scored: {result['overall_score']}%")
                    print(f"✅ Eligible: {'Yes' if result['is_eligible'] else 'No'}")
                    print(f"✅ Shortlisted: {'Yes' if result['is_shortlisted'] else 'No'}")
                    
                    print("\n📈 Score Breakdown:")
                    for category, data in result['breakdown'].items():
                        print(f"  • {category.replace('_', ' ').title()}: {data['score']:.1f}%")
                    
                    # Test question generation
                    print("\n3. ❓ Testing Skill-Based Question Generation...")
                    
                    question_gen = SkillBasedQuestionGenerator()
                    questions = question_gen.generate_questions_for_candidate(student.id, 8)
                    
                    print(f"✅ Generated {len(questions)} personalized questions")
                    
                    print("\n📝 Sample Questions:")
                    for i, q in enumerate(questions[:4], 1):
                        print(f"{i}. [{q['skill']} - {q['difficulty']}] {q['question']}")
                        print(f"   Time: {q['time_limit']//60} minutes")
                    
                    # Test coding question generation
                    print("\n4. 💻 Testing Coding Question Generation...")
                    
                    coding_question = question_gen.generate_coding_question('python', 'beginner')
                    if coding_question:
                        print("✅ Generated coding question:")
                        print(f"Question: {coding_question['question']}")
                        print(f"Starter Code:\n{coding_question['starter_code']}")
                    
                    print("\n🎉 Complete workflow test successful!")
                    print(f"📊 Summary:")
                    print(f"  • Job parsed: {len(parsed_job['required_skills'])} skills extracted")
                    print(f"  • Candidate scored: {result['overall_score']:.1f}%")
                    print(f"  • Eligibility: {'✅ Eligible' if result['is_eligible'] else '❌ Not Eligible'}")
                    print(f"  • Questions generated: {len(questions)} personalized")
                    
                else:
                    print(f"❌ Scoring failed: {result['error']}")
            else:
                print("❌ No HR user found")
        else:
            print("❌ No student with resume found")

if __name__ == '__main__':
    test_complete_workflow()