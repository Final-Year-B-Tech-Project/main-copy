#!/usr/bin/env python3
"""
Update shortlisting logic and re-score candidates
"""

from app import create_app, db
from app.candidate_scoring import CandidateScoringEngine

def update_shortlisting():
    """Update shortlisting thresholds and re-score candidates"""
    
    app = create_app()
    with app.app_context():
        print("🎯 Updating Shortlisting Logic")
        print("=" * 60)
        
        # Update shortlisting thresholds
        scoring_engine = CandidateScoringEngine()
        scoring_engine.eligibility_threshold = 30.0   # 30% for eligibility
        scoring_engine.shortlist_threshold = 50.0     # 50% for shortlisting (reduced from 75%)
        
        print(f"📊 New Thresholds:")
        print(f"  • Eligibility: {scoring_engine.eligibility_threshold}%")
        print(f"  • Shortlisting: {scoring_engine.shortlist_threshold}%")
        
        # Get all candidate scores
        with db.engine.connect() as conn:
            scores = conn.execute(db.text("""
                SELECT cs.id, cs.student_id, cs.job_drive_id, cs.overall_score,
                       u.username, jd.title
                FROM candidate_score cs
                JOIN student_profile sp ON cs.student_id = sp.id
                JOIN user u ON sp.user_id = u.id
                JOIN job_drive jd ON cs.job_drive_id = jd.id
                ORDER BY cs.job_drive_id, cs.overall_score DESC
            """)).fetchall()
            
            print(f"\n🔄 Updating {len(scores)} candidate scores...")
            
            updated_count = 0
            shortlisted_count = 0
            
            for score_id, student_id, job_drive_id, overall_score, username, job_title in scores:
                # Update eligibility and shortlisting status
                is_eligible = overall_score >= scoring_engine.eligibility_threshold
                is_shortlisted = overall_score >= scoring_engine.shortlist_threshold
                
                # Update database
                conn.execute(db.text("""
                    UPDATE candidate_score 
                    SET is_eligible = :is_eligible, 
                        is_shortlisted = :is_shortlisted,
                        shortlist_reason = :reason
                    WHERE id = :score_id
                """), {
                    'is_eligible': is_eligible,
                    'is_shortlisted': is_shortlisted,
                    'reason': f"Score: {overall_score:.1f}% - {'Shortlisted' if is_shortlisted else 'Eligible only'}",
                    'score_id': score_id
                })
                
                status = "🌟 Shortlisted" if is_shortlisted else "✅ Eligible" if is_eligible else "❌ Not Eligible"
                print(f"  • {username} for {job_title}: {overall_score:.1f}% - {status}")
                
                updated_count += 1
                if is_shortlisted:
                    shortlisted_count += 1
            
            conn.commit()
            
            print(f"\n🎉 Update Complete!")
            print(f"📊 Results:")
            print(f"  • Total candidates updated: {updated_count}")
            print(f"  • Shortlisted candidates: {shortlisted_count}")
            
            # Show shortlisted candidates by job
            print(f"\n📋 Shortlisted Candidates by Job:")
            job_summary = conn.execute(db.text("""
                SELECT jd.title, COUNT(*) as shortlisted_count
                FROM candidate_score cs
                JOIN job_drive jd ON cs.job_drive_id = jd.id
                WHERE cs.is_shortlisted = 1
                GROUP BY jd.id, jd.title
                ORDER BY shortlisted_count DESC
            """)).fetchall()
            
            for job_title, count in job_summary:
                print(f"  • {job_title}: {count} shortlisted")

if __name__ == '__main__':
    update_shortlisting()