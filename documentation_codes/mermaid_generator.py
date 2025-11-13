#!/usr/bin/env python3
"""
Mermaid Diagram Generator for AI Interview System Documentation
Generates all types of Mermaid diagrams for comprehensive project documentation
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

class MermaidGenerator:
    """Comprehensive Mermaid diagram generator for project documentation"""
    
    def __init__(self, output_dir: str = "diagrams"):
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def save_diagram(self, filename: str, content: str):
        """Save diagram content to file"""
        filepath = os.path.join(self.output_dir, f"{filename}.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {filename.replace('_', ' ').title()}\n\n")
            f.write("```mermaid\n")
            f.write(content)
            f.write("\n```\n")
        print(f"Generated: {filepath}")
    
    def generate_system_architecture(self):
        """Generate system architecture diagram"""
        diagram = """graph TB
    subgraph "Frontend Layer"
        UI[Web Interface]
        JS[JavaScript Client]
        CSS[Bootstrap UI]
    end
    
    subgraph "Backend Layer"
        Flask[Flask Application]
        Auth[Authentication Module]
        API[REST API Endpoints]
    end
    
    subgraph "Business Logic"
        Student[Student Service]
        HR[HR Service]
        Interview[Interview Engine]
        AI[AI Service]
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        Files[File Storage]
        Cache[Session Cache]
    end
    
    subgraph "External Services"
        Gemini[Google Gemini AI]
        Email[Email Service]
        Upload[File Upload Service]
    end
    
    UI --> Flask
    JS --> API
    Flask --> Auth
    Flask --> Student
    Flask --> HR
    Flask --> Interview
    Interview --> AI
    AI --> Gemini
    Student --> DB
    HR --> DB
    Interview --> DB
    Flask --> Files
    HR --> Email
    Student --> Upload"""
        
        self.save_diagram("system_architecture", diagram)
    
    def generate_user_flow(self):
        """Generate user flow diagram"""
        diagram = """flowchart TD
    Start([User Visits Platform]) --> Choice{User Type?}
    
    Choice -->|Student| StudentReg[Student Registration]
    Choice -->|HR| HRReg[HR Registration]
    Choice -->|Existing User| Login[Login Page]
    
    StudentReg --> StudentDash[Student Dashboard]
    HRReg --> HRDash[HR Dashboard]
    Login --> AuthCheck{Valid Credentials?}
    
    AuthCheck -->|Yes| UserType{User Type?}
    AuthCheck -->|No| Login
    
    UserType -->|Student| StudentDash
    UserType -->|HR| HRDash
    
    StudentDash --> Practice[Practice Interview]
    StudentDash --> Profile[Update Profile]
    StudentDash --> History[View History]
    
    Practice --> AIInterview[AI Interview Session]
    AIInterview --> Feedback[Receive Feedback]
    Feedback --> StudentDash
    
    HRDash --> CreateJob[Create Job Drive]
    HRDash --> ManageCand[Manage Candidates]
    HRDash --> Analytics[View Analytics]
    
    CreateJob --> JobPosted[Job Drive Active]
    ManageCand --> Schedule[Schedule Interviews]
    Schedule --> SendInvite[Send Email Invites]"""
        
        self.save_diagram("user_flow", diagram)
    
    def generate_database_schema(self):
        """Generate database schema diagram"""
        diagram = """erDiagram
    User {
        int id PK
        string username UK
        string email UK
        string password_hash
        string user_type
        datetime created_at
        datetime updated_at
        boolean is_active
    }
    
    Student {
        int id PK
        int user_id FK
        string full_name
        string phone
        string education
        string skills
        string experience_level
        string resume_path
        string profile_photo
        text bio
    }
    
    HR {
        int id PK
        int user_id FK
        string full_name
        string company_name
        string position
        string phone
        string hr_code UK
        boolean is_verified
    }
    
    JobDrive {
        int id PK
        int hr_id FK
        string title
        text description
        string requirements
        string location
        string job_type
        decimal salary_min
        decimal salary_max
        datetime application_deadline
        boolean is_active
        datetime created_at
    }
    
    Interview {
        int id PK
        int student_id FK
        int job_drive_id FK
        string interview_type
        datetime scheduled_time
        string status
        json questions
        json responses
        decimal score
        text feedback
        datetime created_at
        datetime completed_at
    }
    
    Application {
        int id PK
        int student_id FK
        int job_drive_id FK
        string status
        text cover_letter
        datetime applied_at
        datetime updated_at
    }
    
    User ||--o| Student : "has profile"
    User ||--o| HR : "has profile"
    HR ||--o{ JobDrive : "creates"
    Student ||--o{ Application : "submits"
    JobDrive ||--o{ Application : "receives"
    Student ||--o{ Interview : "participates"
    JobDrive ||--o{ Interview : "for position"
    Application ||--|| Interview : "leads to"
"""
        
        self.save_diagram("database_schema", diagram)
    
    def generate_api_endpoints(self):
        """Generate API endpoints diagram"""
        diagram = """graph LR
    subgraph "Authentication APIs"
        A1[POST /auth/register]
        A2[POST /auth/login]
        A3[POST /auth/logout]
        A4[GET /auth/profile]
    end
    
    subgraph "Student APIs"
        S1[GET /student/dashboard]
        S2[POST /student/profile]
        S3[POST /student/upload-resume]
        S4[GET /student/interviews]
        S5[POST /student/start-interview]
    end
    
    subgraph "HR APIs"
        H1[GET /hr/dashboard]
        H2[POST /hr/create-job]
        H3[GET /hr/job-drives]
        H4[GET /hr/candidates]
        H5[POST /hr/schedule-interview]
    end
    
    subgraph "Interview APIs"
        I1[POST /interview/start]
        I2[POST /interview/submit-answer]
        I3[GET /interview/feedback]
        I4[POST /interview/complete]
    end
    
    subgraph "AI APIs"
        AI1[POST /ai/generate-questions]
        AI2[POST /ai/evaluate-answer]
        AI3[POST /ai/final-feedback]
    end
    
    Client[Web Client] --> A1
    Client --> A2
    Client --> S1
    Client --> H1
    Client --> I1
    
    S5 --> AI1
    I2 --> AI2
    I4 --> AI3"""
        
        self.save_diagram("api_endpoints", diagram)
    
    def generate_interview_process(self):
        """Generate interview process flow"""
        diagram = """sequenceDiagram
    participant S as Student
    participant UI as Web Interface
    participant API as Flask API
    participant AI as AI Service
    participant DB as Database
    participant Gemini as Google Gemini
    
    S->>UI: Start Practice Interview
    UI->>API: POST /interview/start
    API->>DB: Get student profile
    DB-->>API: Profile data
    API->>AI: Generate questions
    AI->>Gemini: Request questions based on profile
    Gemini-->>AI: Generated questions
    AI-->>API: Question set
    API->>DB: Save interview session
    API-->>UI: Interview questions
    UI-->>S: Display first question
    
    loop For each question
        S->>UI: Submit answer
        UI->>API: POST /interview/submit-answer
        API->>AI: Evaluate answer
        AI->>Gemini: Analyze response
        Gemini-->>AI: Evaluation score
        AI-->>API: Score and feedback
        API->>DB: Save response
        API-->>UI: Next question or feedback
        UI-->>S: Show result
    end
    
    S->>UI: Complete interview
    UI->>API: POST /interview/complete
    API->>AI: Generate final feedback
    AI->>Gemini: Comprehensive analysis
    Gemini-->>AI: Final report
    AI-->>API: Complete feedback
    API->>DB: Update interview record
    API-->>UI: Final results
    UI-->>S: Show complete feedback"""
        
        self.save_diagram("interview_process", diagram)
    
    def generate_deployment_diagram(self):
        """Generate deployment architecture"""
        diagram = """graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        Mobile[Mobile Browser]
    end
    
    subgraph "CDN/Load Balancer"
        LB[Load Balancer]
        CDN[Static Assets CDN]
    end
    
    subgraph "Application Layer"
        App1[Flask App Instance 1]
        App2[Flask App Instance 2]
        App3[Flask App Instance N]
    end
    
    subgraph "Database Layer"
        Primary[(Primary DB)]
        Replica[(Read Replica)]
        Cache[(Redis Cache)]
    end
    
    subgraph "File Storage"
        Static[Static Files]
        Uploads[User Uploads]
        Logs[Application Logs]
    end
    
    subgraph "External Services"
        Gemini[Google Gemini API]
        SMTP[Email Service]
        Monitor[Monitoring Service]
    end
    
    Browser --> LB
    Mobile --> LB
    LB --> CDN
    LB --> App1
    LB --> App2
    LB --> App3
    
    App1 --> Primary
    App2 --> Primary
    App3 --> Primary
    App1 --> Replica
    App2 --> Replica
    App3 --> Replica
    
    App1 --> Cache
    App2 --> Cache
    App3 --> Cache
    
    App1 --> Static
    App1 --> Uploads
    App1 --> Gemini
    App1 --> SMTP
    
    Monitor --> App1
    Monitor --> Primary
    Monitor --> Cache"""
        
        self.save_diagram("deployment_architecture", diagram)
    
    def generate_state_diagram(self):
        """Generate application state diagram"""
        diagram = """stateDiagram-v2
    [*] --> Unauthenticated
    
    Unauthenticated --> Registering : Click Register
    Unauthenticated --> LoggingIn : Click Login
    
    Registering --> StudentRegistration : Select Student
    Registering --> HRRegistration : Select HR
    
    StudentRegistration --> StudentDashboard : Complete Registration
    HRRegistration --> HRDashboard : Complete Registration
    
    LoggingIn --> StudentDashboard : Student Login Success
    LoggingIn --> HRDashboard : HR Login Success
    LoggingIn --> Unauthenticated : Login Failed
    
    StudentDashboard --> PracticeInterview : Start Practice
    StudentDashboard --> ProfileManagement : Edit Profile
    StudentDashboard --> InterviewHistory : View History
    
    PracticeInterview --> InterviewInProgress : Begin Interview
    InterviewInProgress --> InterviewCompleted : Submit All Answers
    InterviewCompleted --> StudentDashboard : View Results
    
    HRDashboard --> JobManagement : Manage Jobs
    HRDashboard --> CandidateManagement : Manage Candidates
    HRDashboard --> Analytics : View Reports
    
    JobManagement --> HRDashboard : Save Changes
    CandidateManagement --> InterviewScheduling : Schedule Interview
    InterviewScheduling --> HRDashboard : Send Invites
    
    StudentDashboard --> [*] : Logout
    HRDashboard --> [*] : Logout"""
        
        self.save_diagram("application_states", diagram)
    
    def generate_class_diagram(self):
        """Generate class diagram for main models"""
        diagram = """classDiagram
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
    Interview --> AIService : uses"""
        
        self.save_diagram("class_diagram", diagram)
    
    def generate_component_diagram(self):
        """Generate component architecture diagram"""
        diagram = """graph TB
    subgraph "Presentation Layer"
        WebUI[Web Interface]
        Templates[Jinja2 Templates]
        StaticFiles[CSS/JS/Images]
    end
    
    subgraph "Application Layer"
        FlaskApp[Flask Application]
        AuthModule[Authentication Module]
        StudentModule[Student Module]
        HRModule[HR Module]
        InterviewModule[Interview Module]
    end
    
    subgraph "Service Layer"
        AIService[AI Service]
        EmailService[Email Service]
        FileService[File Upload Service]
        ValidationService[Validation Service]
    end
    
    subgraph "Data Access Layer"
        SQLAlchemy[SQLAlchemy ORM]
        Models[Database Models]
        Migrations[Database Migrations]
    end
    
    subgraph "Infrastructure Layer"
        Database[(SQLite/PostgreSQL)]
        FileSystem[File System]
        ExternalAPIs[External APIs]
    end
    
    WebUI --> FlaskApp
    Templates --> WebUI
    StaticFiles --> WebUI
    
    FlaskApp --> AuthModule
    FlaskApp --> StudentModule
    FlaskApp --> HRModule
    FlaskApp --> InterviewModule
    
    StudentModule --> AIService
    InterviewModule --> AIService
    HRModule --> EmailService
    StudentModule --> FileService
    
    AuthModule --> ValidationService
    StudentModule --> ValidationService
    HRModule --> ValidationService
    
    AIService --> SQLAlchemy
    EmailService --> SQLAlchemy
    FileService --> SQLAlchemy
    
    SQLAlchemy --> Models
    Models --> Database
    Migrations --> Database
    
    FileService --> FileSystem
    AIService --> ExternalAPIs"""
        
        self.save_diagram("component_architecture", diagram)
    
    def generate_timeline_diagram(self):
        """Generate project timeline/roadmap"""
        diagram = """timeline
    title AI Interview System Development Timeline
    
    section Phase 1 : Foundation
        Project Setup        : Database Design
                            : Flask Application Structure
                            : Basic Authentication
        
        Core Models         : User Management
                           : Student/HR Profiles
                           : Database Migrations
    
    section Phase 2 : Core Features
        Interview Engine    : AI Integration
                           : Question Generation
                           : Response Evaluation
        
        User Interfaces    : Student Dashboard
                          : HR Dashboard
                          : Interview Interface
    
    section Phase 3 : Advanced Features
        Job Management     : Job Drive Creation
                          : Application System
                          : Interview Scheduling
        
        Analytics         : Performance Tracking
                         : Reporting System
                         : Email Notifications
    
    section Phase 4 : Production
        Testing           : Unit Tests
                         : Integration Tests
                         : User Acceptance Testing
        
        Deployment        : Production Setup
                         : Performance Optimization
                         : Monitoring & Logging"""
        
        self.save_diagram("project_timeline", diagram)
    
    def generate_gitflow_diagram(self):
        """Generate Git workflow diagram"""
        diagram = """gitgraph
    commit id: "Initial Setup"
    branch develop
    checkout develop
    commit id: "Database Models"
    commit id: "Authentication System"
    
    branch feature/student-module
    checkout feature/student-module
    commit id: "Student Registration"
    commit id: "Student Dashboard"
    commit id: "Profile Management"
    
    checkout develop
    merge feature/student-module
    
    branch feature/hr-module
    checkout feature/hr-module
    commit id: "HR Registration"
    commit id: "Job Drive Creation"
    commit id: "Candidate Management"
    
    checkout develop
    merge feature/hr-module
    
    branch feature/ai-integration
    checkout feature/ai-integration
    commit id: "Gemini API Setup"
    commit id: "Question Generation"
    commit id: "Answer Evaluation"
    
    checkout develop
    merge feature/ai-integration
    
    checkout main
    merge develop
    commit id: "v1.0.0 Release"
    
    checkout develop
    branch feature/analytics
    checkout feature/analytics
    commit id: "Performance Metrics"
    commit id: "Reporting Dashboard"
    
    checkout develop
    merge feature/analytics
    
    checkout main
    merge develop
    commit id: "v1.1.0 Release"""
        
        self.save_diagram("git_workflow", diagram)
    
    def generate_all_diagrams(self):
        """Generate all diagram types"""
        print("Generating comprehensive Mermaid diagrams for AI Interview System...")
        print("=" * 60)
        
        diagrams = [
            ("System Architecture", self.generate_system_architecture),
            ("User Flow", self.generate_user_flow),
            ("Database Schema", self.generate_database_schema),
            ("API Endpoints", self.generate_api_endpoints),
            ("Interview Process", self.generate_interview_process),
            ("Deployment Architecture", self.generate_deployment_diagram),
            ("Application States", self.generate_state_diagram),
            ("Class Diagram", self.generate_class_diagram),
            ("Component Architecture", self.generate_component_diagram),
            ("Project Timeline", self.generate_timeline_diagram),
            ("Git Workflow", self.generate_gitflow_diagram)
        ]
        
        for name, generator in diagrams:
            print(f"Generating {name}...")
            generator()
        
        print("=" * 60)
        print(f"All diagrams generated successfully in '{self.output_dir}' folder!")
        print(f"Total diagrams: {len(diagrams)}")
        print("\nUsage Instructions:")
        print("1. Copy the Mermaid code from any .md file")
        print("2. Paste it into Mermaid Live Editor (https://mermaid.live)")
        print("3. Export as PNG/SVG for documentation")
        print("4. Or use in GitHub/GitLab markdown files directly")

if __name__ == "__main__":
    generator = MermaidGenerator()
    generator.generate_all_diagrams()