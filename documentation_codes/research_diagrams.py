#!/usr/bin/env python3
"""
Research Paper & Presentation Diagrams
Professional diagrams for academic documentation
"""

import os

class ResearchDiagramGenerator:
    def __init__(self, output_dir="research_diagrams"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def save(self, name, content):
        path = os.path.join(self.output_dir, f"{name}.md")
        with open(path, 'w') as f:
            f.write(f"# {name.replace('_', ' ').title()}\n\n```mermaid\n{content}\n```\n")
        print(f"Generated: {path}")
    
    def proposed_system_architecture(self):
        """Main proposed system architecture"""
        diagram = """graph TB
    subgraph "Presentation Layer"
        A[Web Interface<br/>HTML5, CSS3, Bootstrap]
        B[Responsive UI<br/>Cross-platform Access]
    end
    
    subgraph "Application Layer"
        C[Flask Web Framework<br/>Python 3.8+]
        D[Authentication Module<br/>Flask-Login]
        E[Session Management<br/>Secure Token-based]
    end
    
    subgraph "Business Logic Layer"
        F[Student Management<br/>Profile & Resume]
        G[HR Management<br/>Job Drive & Scheduling]
        H[Interview Engine<br/>Question Generation]
        I[AI Service<br/>OpenRouter API]
    end
    
    subgraph "Data Layer"
        J[(SQLite Database<br/>User & Interview Data)]
        K[File Storage<br/>Resume & Documents]
        L[Session Cache<br/>Performance Optimization]
    end
    
    subgraph "External Services"
        M[AI Models<br/>Grok, DeepSeek, GPT]
        N[Email Service<br/>SMTP Notifications]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    D --> F
    D --> G
    E --> H
    H --> I
    F --> J
    G --> J
    H --> J
    F --> K
    G --> K
    I --> M
    G --> N
    
    style A fill:#e1f5ff
    style C fill:#fff3e0
    style H fill:#f3e5f5
    style J fill:#e8f5e9
    style M fill:#fce4ec"""
        
        self.save("01_proposed_system_architecture", diagram)
    
    def research_methodology(self):
        """Research methodology flowchart"""
        diagram = """flowchart TD
    A[Problem Identification<br/>Manual Interview Challenges] --> B[Literature Review<br/>AI in Recruitment]
    B --> C[Requirements Analysis<br/>Student & HR Needs]
    C --> D[System Design<br/>Architecture & Database]
    
    D --> E[Technology Selection]
    E --> E1[Backend: Flask + Python]
    E --> E2[Frontend: HTML5 + Bootstrap]
    E --> E3[AI: OpenRouter API]
    E --> E4[Database: SQLite]
    
    E1 --> F[Implementation Phase]
    E2 --> F
    E3 --> F
    E4 --> F
    
    F --> G[Module Development]
    G --> G1[Authentication System]
    G --> G2[Student Module]
    G --> G3[HR Module]
    G --> G4[AI Interview Engine]
    
    G1 --> H[Integration & Testing]
    G2 --> H
    G3 --> H
    G4 --> H
    
    H --> I[System Testing]
    I --> I1[Unit Testing]
    I --> I2[Integration Testing]
    I --> I3[User Acceptance Testing]
    
    I1 --> J[Performance Evaluation]
    I2 --> J
    I3 --> J
    
    J --> K[Results Analysis<br/>& Documentation]
    K --> L[Deployment<br/>& Validation]
    
    style A fill:#ffcdd2
    style D fill:#c5cae9
    style F fill:#b2dfdb
    style H fill:#fff9c4
    style J fill:#f8bbd0
    style L fill:#c8e6c9"""
        
        self.save("02_research_methodology", diagram)
    
    def system_workflow(self):
        """Complete system workflow"""
        diagram = """flowchart TD
    Start([User Access]) --> Auth{Authenticated?}
    Auth -->|No| Login[Login/Register]
    Auth -->|Yes| Role{User Role?}
    
    Login --> Register[Registration Form]
    Register --> Type{Account Type?}
    Type -->|Student| S1[Student Profile Setup]
    Type -->|HR| H1[HR Profile Setup]
    
    S1 --> S2[Upload Resume]
    S2 --> SDash[Student Dashboard]
    
    H1 --> H2[Company Details]
    H2 --> HDash[HR Dashboard]
    
    Role -->|Student| SDash
    Role -->|HR| HDash
    
    SDash --> S3[Practice Interview]
    S3 --> S4[AI Generates Questions]
    S4 --> S5[Answer Questions]
    S5 --> S6[AI Evaluation]
    S6 --> S7[Feedback & Score]
    S7 --> S8[Performance History]
    
    HDash --> H3[Create Job Drive]
    H3 --> H4[Post Requirements]
    H4 --> H5[Receive Applications]
    H5 --> H6[Review Candidates]
    H6 --> H7[Schedule Interviews]
    H7 --> H8[AI-Assisted Evaluation]
    H8 --> H9[Selection Decision]
    
    S8 --> End([Exit])
    H9 --> End
    
    style Start fill:#4caf50,color:#fff
    style SDash fill:#2196f3,color:#fff
    style HDash fill:#ff9800,color:#fff
    style S6 fill:#9c27b0,color:#fff
    style H8 fill:#9c27b0,color:#fff
    style End fill:#f44336,color:#fff"""
        
        self.save("03_system_workflow", diagram)
    
    def ai_interview_process(self):
        """AI interview process detailed"""
        diagram = """sequenceDiagram
    participant S as Student
    participant UI as Web Interface
    participant BE as Backend Server
    participant AI as AI Service
    participant DB as Database
    participant API as OpenRouter API
    
    S->>UI: Start Interview
    UI->>BE: Request Interview Session
    BE->>DB: Fetch Student Profile
    DB-->>BE: Profile Data
    
    BE->>AI: Generate Questions
    Note over AI: Job Role<br/>Experience Level<br/>Skills
    AI->>API: Request AI Generation
    API-->>AI: Generated Questions
    AI-->>BE: Question Set
    
    BE->>DB: Save Interview Session
    BE-->>UI: Display Questions
    UI-->>S: Show Question 1
    
    loop For Each Question
        S->>UI: Submit Answer
        UI->>BE: Send Response
        BE->>AI: Evaluate Answer
        AI->>API: Analyze Response
        API-->>AI: Evaluation Score
        AI-->>BE: Score & Feedback
        BE->>DB: Store Response
        BE-->>UI: Next Question
        UI-->>S: Display Next
    end
    
    S->>UI: Complete Interview
    UI->>BE: Finish Request
    BE->>AI: Generate Final Report
    AI->>API: Comprehensive Analysis
    API-->>AI: Final Evaluation
    AI-->>BE: Complete Report
    BE->>DB: Update Records
    BE-->>UI: Show Results
    UI-->>S: Display Feedback
    
    Note over S,API: Interview Complete<br/>Performance Saved"""
        
        self.save("04_ai_interview_process", diagram)
    
    def data_flow_architecture(self):
        """Data flow in the system"""
        diagram = """flowchart LR
    subgraph Input
        A[User Input]
        B[Resume Upload]
        C[Job Requirements]
    end
    
    subgraph Processing
        D[Data Validation]
        E[Authentication]
        F[Business Logic]
    end
    
    subgraph AI_Processing
        G[Question Generation]
        H[Answer Evaluation]
        I[Feedback Generation]
    end
    
    subgraph Storage
        J[(User Database)]
        K[(Interview Records)]
        L[File Storage]
    end
    
    subgraph Output
        M[Dashboard Display]
        N[Reports & Analytics]
        O[Email Notifications]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    E --> F
    
    F --> G
    F --> H
    H --> I
    
    F --> J
    F --> K
    B --> L
    
    J --> M
    K --> N
    K --> O
    
    style Input fill:#e3f2fd
    style Processing fill:#fff3e0
    style AI_Processing fill:#f3e5f5
    style Storage fill:#e8f5e9
    style Output fill:#fce4ec"""
        
        self.save("05_data_flow_architecture", diagram)
    
    def module_architecture(self):
        """Module-wise architecture"""
        diagram = """graph TB
    subgraph "Authentication Module"
        A1[User Registration]
        A2[Login System]
        A3[Session Management]
        A4[Role-Based Access]
    end
    
    subgraph "Student Module"
        S1[Profile Management]
        S2[Resume Upload]
        S3[Practice Interview]
        S4[Performance Tracking]
        S5[Job Applications]
    end
    
    subgraph "HR Module"
        H1[Company Profile]
        H2[Job Drive Creation]
        H3[Candidate Management]
        H4[Interview Scheduling]
        H5[Analytics Dashboard]
    end
    
    subgraph "AI Interview Module"
        I1[Question Generation]
        I2[Adaptive Questioning]
        I3[Answer Evaluation]
        I4[Feedback System]
        I5[Performance Scoring]
    end
    
    subgraph "Database Module"
        D1[(User Data)]
        D2[(Interview Data)]
        D3[(Job Data)]
        D4[(Analytics Data)]
    end
    
    A1 --> S1
    A1 --> H1
    A2 --> A4
    A4 --> S1
    A4 --> H1
    
    S3 --> I1
    I1 --> I2
    I2 --> I3
    I3 --> I4
    I4 --> I5
    
    H2 --> H3
    H3 --> H4
    
    S1 --> D1
    H1 --> D1
    I5 --> D2
    H2 --> D3
    H5 --> D4
    
    style A1 fill:#4caf50,color:#fff
    style S1 fill:#2196f3,color:#fff
    style H1 fill:#ff9800,color:#fff
    style I1 fill:#9c27b0,color:#fff
    style D1 fill:#607d8b,color:#fff"""
        
        self.save("06_module_architecture", diagram)
    
    def implementation_phases(self):
        """Implementation phases timeline"""
        diagram = """gantt
    title Project Implementation Timeline
    dateFormat YYYY-MM-DD
    section Phase 1: Planning
    Requirements Analysis           :2024-01-01, 15d
    System Design                   :2024-01-16, 20d
    Technology Selection            :2024-02-05, 10d
    
    section Phase 2: Development
    Database Design                 :2024-02-15, 10d
    Authentication Module           :2024-02-25, 15d
    Student Module                  :2024-03-11, 20d
    HR Module                       :2024-03-31, 20d
    AI Integration                  :2024-04-20, 25d
    
    section Phase 3: Testing
    Unit Testing                    :2024-05-15, 10d
    Integration Testing             :2024-05-25, 15d
    User Acceptance Testing         :2024-06-09, 10d
    
    section Phase 4: Deployment
    Production Setup                :2024-06-19, 7d
    Performance Optimization        :2024-06-26, 10d
    Documentation                   :2024-07-06, 7d
    Final Deployment                :2024-07-13, 3d"""
        
        self.save("07_implementation_timeline", diagram)
    
    def use_case_diagram(self):
        """Use case diagram"""
        diagram = """graph TB
    subgraph System["AI Interview System"]
        UC1[Register Account]
        UC2[Login]
        UC3[Manage Profile]
        UC4[Upload Resume]
        UC5[Practice Interview]
        UC6[View Feedback]
        UC7[Create Job Drive]
        UC8[Schedule Interview]
        UC9[Review Candidates]
        UC10[Generate Reports]
    end
    
    Student([Student]) --> UC1
    Student --> UC2
    Student --> UC3
    Student --> UC4
    Student --> UC5
    Student --> UC6
    
    HR([HR Professional]) --> UC1
    HR --> UC2
    HR --> UC3
    HR --> UC7
    HR --> UC8
    HR --> UC9
    HR --> UC10
    
    UC5 --> AI[AI Service]
    UC6 --> AI
    UC9 --> AI
    UC10 --> AI
    
    UC4 --> Storage[(File Storage)]
    UC7 --> DB[(Database)]
    UC8 --> Email[Email Service]
    
    style Student fill:#2196f3,color:#fff
    style HR fill:#ff9800,color:#fff
    style AI fill:#9c27b0,color:#fff
    style System fill:#e8eaf6"""
        
        self.save("08_use_case_diagram", diagram)
    
    def technology_stack(self):
        """Technology stack diagram"""
        diagram = """graph TB
    subgraph "Frontend Technologies"
        F1[HTML5]
        F2[CSS3 + Bootstrap 5.3]
        F3[JavaScript ES6+]
        F4[jQuery 3.7]
    end
    
    subgraph "Backend Technologies"
        B1[Python 3.8+]
        B2[Flask 2.3+]
        B3[Flask-Login]
        B4[Flask-SQLAlchemy]
        B5[Werkzeug Security]
    end
    
    subgraph "Database"
        D1[SQLite Development]
        D2[PostgreSQL Production]
    end
    
    subgraph "AI & APIs"
        A1[OpenRouter API]
        A2[Grok-4-Fast]
        A3[DeepSeek Chat]
        A4[GPT-OSS-120B]
    end
    
    subgraph "Additional Tools"
        T1[PyPDF2 Resume Parser]
        T2[Python-dotenv]
        T3[Requests Library]
        T4[Email SMTP]
    end
    
    F1 --> B2
    F2 --> B2
    F3 --> B2
    F4 --> B2
    
    B1 --> B2
    B2 --> B3
    B2 --> B4
    B2 --> B5
    
    B4 --> D1
    B4 --> D2
    
    B2 --> A1
    A1 --> A2
    A1 --> A3
    A1 --> A4
    
    B2 --> T1
    B2 --> T2
    B2 --> T3
    B2 --> T4
    
    style F1 fill:#e3f2fd
    style B2 fill:#fff3e0
    style A1 fill:#f3e5f5
    style D1 fill:#e8f5e9"""
        
        self.save("09_technology_stack", diagram)
    
    def generate_all(self):
        """Generate all research diagrams"""
        print("Generating Research Paper & Presentation Diagrams")
        print("=" * 50)
        
        diagrams = [
            ("Proposed System Architecture", self.proposed_system_architecture),
            ("Research Methodology", self.research_methodology),
            ("System Workflow", self.system_workflow),
            ("AI Interview Process", self.ai_interview_process),
            ("Data Flow Architecture", self.data_flow_architecture),
            ("Module Architecture", self.module_architecture),
            ("Implementation Timeline", self.implementation_phases),
            ("Use Case Diagram", self.use_case_diagram),
            ("Technology Stack", self.technology_stack)
        ]
        
        for name, func in diagrams:
            print(f"Creating {name}...")
            func()
        
        print("=" * 50)
        print(f"Generated {len(diagrams)} research diagrams!")
        print(f"Location: {self.output_dir}/")
        print("\nDiagrams are numbered for easy reference in papers")

if __name__ == "__main__":
    generator = ResearchDiagramGenerator()
    generator.generate_all()