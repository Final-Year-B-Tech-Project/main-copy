# Class Diagram

```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string email
        +string password_hash
        +string user_type
        +datetime created_at
        +boolean is_active
        +check_password(password)
        +set_password(password)
        +get_profile()
    }
    
    class Student {
        +int id
        +int user_id
        +string full_name
        +string phone
        +string education
        +string skills
        +string experience_level
        +string resume_path
        +update_profile(data)
        +get_interviews()
        +calculate_performance()
    }
    
    class HR {
        +int id
        +int user_id
        +string full_name
        +string company_name
        +string position
        +string hr_code
        +boolean is_verified
        +create_job_drive(data)
        +get_candidates()
        +schedule_interview(student_id, job_id)
    }
    
    class JobDrive {
        +int id
        +int hr_id
        +string title
        +string description
        +string requirements
        +datetime application_deadline
        +boolean is_active
        +get_applications()
        +is_deadline_passed()
        +deactivate()
    }
    
    class Interview {
        +int id
        +int student_id
        +int job_drive_id
        +string interview_type
        +datetime scheduled_time
        +string status
        +json questions
        +json responses
        +decimal score
        +start_interview()
        +submit_answer(question_id, answer)
        +calculate_final_score()
        +generate_feedback()
    }
    
    class AIService {
        +generate_questions(profile, job_requirements)
        +evaluate_answer(question, answer, context)
        +provide_feedback(interview_data)
        +calculate_score(responses)
    }
    
    User ||--|| Student : has
    User ||--|| HR : has
    HR ||--o{ JobDrive : creates
    Student ||--o{ Interview : participates
    JobDrive ||--o{ Interview : for
    Interview --> AIService : uses
```
