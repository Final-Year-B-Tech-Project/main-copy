#!/usr/bin/env python3
"""
SDLC Diagram Generator for AI Interview System
Software Development Life Cycle visualization
"""

import os

def save_diagram(name, content):
    os.makedirs("sdlc_diagrams", exist_ok=True)
    path = os.path.join("sdlc_diagrams", f"{name}.md")
    with open(path, 'w') as f:
        f.write(f"# {name.replace('_', ' ').title()}\n\n```mermaid\n{content}\n```\n")
    print(f"Generated: {path}")

def sdlc_phases():
    """Complete SDLC phases diagram"""
    diagram = """graph TB
    Start([Project Initiation]) --> P1[Phase 1: Planning]
    
    P1 --> P1A[Identify Problem<br/>Manual Interview Challenges]
    P1A --> P1B[Define Objectives<br/>AI-Powered Solution]
    P1B --> P1C[Feasibility Study<br/>Technical & Financial]
    P1C --> P1D[Project Scope<br/>Student & HR Modules]
    
    P1D --> P2[Phase 2: Analysis]
    
    P2 --> P2A[Requirements Gathering<br/>Student & HR Needs]
    P2A --> P2B[System Analysis<br/>Current vs Proposed]
    P2B --> P2C[Functional Requirements<br/>Features & Capabilities]
    P2C --> P2D[Non-Functional Requirements<br/>Performance & Security]
    
    P2D --> P3[Phase 3: Design]
    
    P3 --> P3A[System Architecture<br/>3-Layer Design]
    P3A --> P3B[Database Design<br/>ER Diagrams & Schema]
    P3B --> P3C[UI/UX Design<br/>Wireframes & Mockups]
    P3C --> P3D[API Design<br/>REST Endpoints]
    P3D --> P3E[AI Integration Design<br/>OpenRouter API]
    
    P3E --> P4[Phase 4: Implementation]
    
    P4 --> P4A[Environment Setup<br/>Python, Flask, SQLite]
    P4A --> P4B[Backend Development<br/>Flask Application]
    P4B --> P4C[Frontend Development<br/>HTML, CSS, JavaScript]
    P4C --> P4D[AI Integration<br/>Question Generation & Evaluation]
    P4D --> P4E[Database Implementation<br/>Models & Migrations]
    P4E --> P4F[Module Integration<br/>Auth, Student, HR, AI]
    
    P4F --> P5[Phase 5: Testing]
    
    P5 --> P5A[Unit Testing<br/>Individual Components]
    P5A --> P5B[Integration Testing<br/>Module Interactions]
    P5B --> P5C[System Testing<br/>End-to-End Scenarios]
    P5C --> P5D[Performance Testing<br/>Load & Stress]
    P5D --> P5E[Security Testing<br/>Authentication & Authorization]
    P5E --> P5F[User Acceptance Testing<br/>Student & HR Feedback]
    
    P5F --> P6[Phase 6: Deployment]
    
    P6 --> P6A[Production Environment<br/>Server Configuration]
    P6A --> P6B[Database Migration<br/>SQLite to PostgreSQL]
    P6B --> P6C[Application Deployment<br/>Web Server Setup]
    P6C --> P6D[Performance Optimization<br/>Caching & Indexing]
    P6D --> P6E[Documentation<br/>User & Technical Manuals]
    
    P6E --> P7[Phase 7: Maintenance]
    
    P7 --> P7A[Monitoring<br/>System Health & Performance]
    P7A --> P7B[Bug Fixes<br/>Issue Resolution]
    P7B --> P7C[Updates<br/>Feature Enhancements]
    P7C --> P7D[User Support<br/>Help & Training]
    P7D --> P7E[Backup & Recovery<br/>Data Protection]
    
    P7E --> End([Continuous Improvement])
    
    style Start fill:#4CAF50,color:#fff
    style P1 fill:#2196F3,color:#fff
    style P2 fill:#FF9800,color:#fff
    style P3 fill:#9C27B0,color:#fff
    style P4 fill:#F44336,color:#fff
    style P5 fill:#00BCD4,color:#fff
    style P6 fill:#8BC34A,color:#fff
    style P7 fill:#FFC107,color:#fff
    style End fill:#4CAF50,color:#fff"""
    
    save_diagram("01_complete_sdlc_phases", diagram)

def sdlc_circular():
    """Circular SDLC model"""
    diagram = """graph TB
    subgraph "SDLC Cycle"
        P1[1. Planning<br/>Problem Identification<br/>Feasibility Study]
        P2[2. Analysis<br/>Requirements Gathering<br/>System Analysis]
        P3[3. Design<br/>Architecture Design<br/>Database Design<br/>UI/UX Design]
        P4[4. Implementation<br/>Coding<br/>AI Integration<br/>Module Development]
        P5[5. Testing<br/>Unit Testing<br/>Integration Testing<br/>UAT]
        P6[6. Deployment<br/>Production Setup<br/>Go Live]
        P7[7. Maintenance<br/>Monitoring<br/>Updates<br/>Support]
    end
    
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    P5 --> P6
    P6 --> P7
    P7 -.->|Feedback Loop| P1
    
    P5 -.->|Issues Found| P4
    P6 -.->|Critical Issues| P5
    
    style P1 fill:#E3F2FD
    style P2 fill:#FFF3E0
    style P3 fill:#F3E5F5
    style P4 fill:#E8F5E9
    style P5 fill:#FFF9C4
    style P6 fill:#FCE4EC
    style P7 fill:#E0F2F1"""
    
    save_diagram("02_sdlc_circular_model", diagram)

def waterfall_model():
    """Waterfall SDLC model"""
    diagram = """flowchart TD
    P1[Phase 1: Requirements Analysis] --> D1[Deliverable: Requirements Document<br/>SRS, Use Cases, User Stories]
    D1 --> P2[Phase 2: System Design]
    P2 --> D2[Deliverable: Design Documents<br/>Architecture, Database Schema, UI Mockups]
    D2 --> P3[Phase 3: Implementation]
    P3 --> D3[Deliverable: Source Code<br/>Backend, Frontend, AI Integration]
    D3 --> P4[Phase 4: Testing]
    P4 --> D4[Deliverable: Test Reports<br/>Test Cases, Bug Reports, UAT Results]
    D4 --> P5[Phase 5: Deployment]
    P5 --> D5[Deliverable: Production System<br/>Live Application, Documentation]
    D5 --> P6[Phase 6: Maintenance]
    P6 --> D6[Deliverable: Updates & Support<br/>Bug Fixes, Enhancements]
    
    style P1 fill:#2196F3,color:#fff
    style P2 fill:#4CAF50,color:#fff
    style P3 fill:#FF9800,color:#fff
    style P4 fill:#9C27B0,color:#fff
    style P5 fill:#F44336,color:#fff
    style P6 fill:#00BCD4,color:#fff
    
    style D1 fill:#E3F2FD
    style D2 fill:#E8F5E9
    style D3 fill:#FFF3E0
    style D4 fill:#F3E5F5
    style D5 fill:#FFEBEE
    style D6 fill:#E0F7FA"""
    
    save_diagram("03_waterfall_model", diagram)

def agile_sprints():
    """Agile/Iterative SDLC"""
    diagram = """graph TB
    Start([Project Start]) --> Planning[Sprint Planning]
    
    Planning --> Sprint1[Sprint 1: 2 Weeks]
    Sprint1 --> S1A[Design: Authentication Module]
    S1A --> S1B[Develop: User Registration & Login]
    S1B --> S1C[Test: Auth Functionality]
    S1C --> S1D[Review: Sprint Demo]
    S1D --> S1E[Deploy: Auth Module]
    
    S1E --> Sprint2[Sprint 2: 2 Weeks]
    Sprint2 --> S2A[Design: Student Module]
    S2A --> S2B[Develop: Profile & Resume Upload]
    S2B --> S2C[Test: Student Features]
    S2C --> S2D[Review: Sprint Demo]
    S2D --> S2E[Deploy: Student Module]
    
    S2E --> Sprint3[Sprint 3: 2 Weeks]
    Sprint3 --> S3A[Design: AI Integration]
    S3A --> S3B[Develop: Question Generation]
    S3B --> S3C[Test: AI Functionality]
    S3C --> S3D[Review: Sprint Demo]
    S3D --> S3E[Deploy: AI Module]
    
    S3E --> Sprint4[Sprint 4: 2 Weeks]
    Sprint4 --> S4A[Design: HR Module]
    S4A --> S4B[Develop: Job Drive & Scheduling]
    S4B --> S4C[Test: HR Features]
    S4C --> S4D[Review: Sprint Demo]
    S4D --> S4E[Deploy: HR Module]
    
    S4E --> Sprint5[Sprint 5: 2 Weeks]
    Sprint5 --> S5A[Integration Testing]
    S5A --> S5B[Performance Optimization]
    S5B --> S5C[Security Hardening]
    S5C --> S5D[Final Review]
    S5D --> S5E[Production Deployment]
    
    S5E --> End([Project Complete])
    
    S1D -.->|Feedback| Planning
    S2D -.->|Feedback| Planning
    S3D -.->|Feedback| Planning
    S4D -.->|Feedback| Planning
    
    style Start fill:#4CAF50,color:#fff
    style Sprint1 fill:#2196F3,color:#fff
    style Sprint2 fill:#FF9800,color:#fff
    style Sprint3 fill:#9C27B0,color:#fff
    style Sprint4 fill:#F44336,color:#fff
    style Sprint5 fill:#00BCD4,color:#fff
    style End fill:#4CAF50,color:#fff"""
    
    save_diagram("04_agile_sprints", diagram)

def v_model():
    """V-Model SDLC"""
    diagram = """graph TB
    subgraph "Development Phase"
        D1[Requirements Analysis]
        D2[System Design]
        D3[Architecture Design]
        D4[Module Design]
        D5[Coding]
    end
    
    subgraph "Testing Phase"
        T1[Acceptance Testing]
        T2[System Testing]
        T3[Integration Testing]
        T4[Unit Testing]
    end
    
    D1 --> D2
    D2 --> D3
    D3 --> D4
    D4 --> D5
    
    D5 --> T4
    T4 --> T3
    T3 --> T2
    T2 --> T1
    
    D1 -.->|Validates| T1
    D2 -.->|Validates| T2
    D3 -.->|Validates| T3
    D4 -.->|Validates| T4
    
    style D1 fill:#2196F3,color:#fff
    style D2 fill:#4CAF50,color:#fff
    style D3 fill:#FF9800,color:#fff
    style D4 fill:#9C27B0,color:#fff
    style D5 fill:#F44336,color:#fff
    
    style T4 fill:#F44336,color:#fff
    style T3 fill:#9C27B0,color:#fff
    style T2 fill:#FF9800,color:#fff
    style T1 fill:#4CAF50,color:#fff"""
    
    save_diagram("05_v_model", diagram)

def project_timeline():
    """Project timeline with SDLC phases"""
    diagram = """gantt
    title AI Interview System - SDLC Timeline
    dateFormat YYYY-MM-DD
    
    section Planning
    Problem Identification           :done, p1, 2024-01-01, 5d
    Feasibility Study               :done, p2, 2024-01-06, 5d
    Project Scope Definition        :done, p3, 2024-01-11, 5d
    
    section Analysis
    Requirements Gathering          :done, a1, 2024-01-16, 7d
    System Analysis                 :done, a2, 2024-01-23, 7d
    Requirements Documentation      :done, a3, 2024-01-30, 6d
    
    section Design
    System Architecture             :done, d1, 2024-02-05, 7d
    Database Design                 :done, d2, 2024-02-12, 5d
    UI/UX Design                    :done, d3, 2024-02-17, 8d
    API Design                      :done, d4, 2024-02-25, 5d
    
    section Implementation
    Environment Setup               :done, i1, 2024-03-01, 3d
    Authentication Module           :done, i2, 2024-03-04, 10d
    Student Module                  :done, i3, 2024-03-14, 12d
    HR Module                       :done, i4, 2024-03-26, 12d
    AI Integration                  :done, i5, 2024-04-07, 15d
    Integration                     :done, i6, 2024-04-22, 8d
    
    section Testing
    Unit Testing                    :active, t1, 2024-04-30, 7d
    Integration Testing             :active, t2, 2024-05-07, 7d
    System Testing                  :t3, 2024-05-14, 7d
    UAT                            :t4, 2024-05-21, 7d
    
    section Deployment
    Production Setup                :t5, 2024-05-28, 5d
    Data Migration                  :t6, 2024-06-02, 3d
    Go Live                        :milestone, t7, 2024-06-05, 1d
    
    section Maintenance
    Monitoring & Support            :t8, 2024-06-06, 30d"""
    
    save_diagram("06_project_timeline", diagram)

def sdlc_activities():
    """Detailed activities in each SDLC phase"""
    diagram = """mindmap
  root((SDLC<br/>AI Interview<br/>System))
    Planning
      Problem Identification
        Manual interview inefficiency
        Time-consuming process
        Lack of standardization
      Feasibility Study
        Technical feasibility
        Financial feasibility
        Operational feasibility
      Scope Definition
        Student module
        HR module
        AI integration
    Analysis
      Requirements Gathering
        Student requirements
        HR requirements
        System requirements
      Functional Requirements
        User authentication
        Interview management
        AI evaluation
      Non-Functional Requirements
        Performance
        Security
        Scalability
    Design
      System Architecture
        3-layer architecture
        Component design
        Integration design
      Database Design
        ER diagrams
        Schema design
        Relationships
      UI/UX Design
        Wireframes
        Mockups
        User flows
    Implementation
      Backend Development
        Flask application
        REST APIs
        Business logic
      Frontend Development
        HTML/CSS/JS
        Responsive design
        User interface
      AI Integration
        OpenRouter API
        Question generation
        Answer evaluation
    Testing
      Unit Testing
        Component testing
        Function testing
      Integration Testing
        Module integration
        API testing
      System Testing
        End-to-end testing
        Performance testing
      UAT
        User feedback
        Acceptance criteria
    Deployment
      Production Setup
        Server configuration
        Database setup
        Environment variables
      Go Live
        Application deployment
        Monitoring setup
        Documentation
    Maintenance
      Monitoring
        System health
        Performance metrics
        Error tracking
      Updates
        Bug fixes
        Feature enhancements
        Security patches
      Support
        User support
        Technical support
        Training"""
    
    save_diagram("07_sdlc_activities_mindmap", diagram)

def generate_all():
    """Generate all SDLC diagrams"""
    print("Generating SDLC Diagrams for AI Interview System")
    print("=" * 50)
    
    diagrams = [
        ("Complete SDLC Phases", sdlc_phases),
        ("Circular SDLC Model", sdlc_circular),
        ("Waterfall Model", waterfall_model),
        ("Agile Sprints", agile_sprints),
        ("V-Model", v_model),
        ("Project Timeline", project_timeline),
        ("SDLC Activities Mindmap", sdlc_activities)
    ]
    
    for name, func in diagrams:
        print(f"Creating {name}...")
        func()
    
    print("=" * 50)
    print(f"Generated {len(diagrams)} SDLC diagrams!")
    print("Location: sdlc_diagrams/")

if __name__ == "__main__":
    generate_all()