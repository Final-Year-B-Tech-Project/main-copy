#!/usr/bin/env python3
"""
Compressed Proposed System Diagram
Simple, clear diagram showing how the system works
"""

import os

def save_diagram(name, content):
    os.makedirs("compressed_diagrams", exist_ok=True)
    path = os.path.join("compressed_diagrams", f"{name}.md")
    with open(path, 'w') as f:
        f.write(f"# {name.replace('_', ' ').title()}\n\n```mermaid\n{content}\n```\n")
    print(f"Generated: {path}")

def compressed_proposed_system():
    """Ultra-compressed proposed system - how it works"""
    diagram = """flowchart TB
    User([User: Student/HR]) -->|Access| Web[Web Interface]
    
    Web -->|Login/Register| Auth[Authentication]
    Auth -->|Verified| Dashboard{User Type?}
    
    Dashboard -->|Student| S1[Practice Interview]
    Dashboard -->|HR| H1[Create Job Drive]
    
    S1 -->|Request Questions| AI[AI Engine<br/>OpenRouter API]
    AI -->|Generate| Q[Interview Questions]
    Q -->|Display| S1
    
    S1 -->|Submit Answers| AI
    AI -->|Evaluate| Score[Score & Feedback]
    Score -->|Save| DB[(Database)]
    
    H1 -->|Post Job| DB
    H1 -->|Schedule| Interview[Interview Sessions]
    Interview -->|AI Assisted| AI
    
    DB -->|Retrieve| Results[Results & Analytics]
    Results -->|Display| Web
    
    style User fill:#4CAF50,color:#fff
    style AI fill:#9C27B0,color:#fff
    style DB fill:#2196F3,color:#fff
    style Score fill:#FF9800,color:#fff"""
    
    save_diagram("compressed_proposed_system", diagram)

def how_system_works():
    """Simple flow showing how the system works"""
    diagram = """flowchart LR
    A[User Login] --> B{Student or HR?}
    
    B -->|Student| C[Start Interview]
    C --> D[AI Generates Questions]
    D --> E[Answer Questions]
    E --> F[AI Evaluates]
    F --> G[Get Feedback]
    
    B -->|HR| H[Create Job]
    H --> I[Review Candidates]
    I --> J[Schedule Interview]
    J --> K[AI Evaluation]
    K --> L[Hire Decision]
    
    style A fill:#4CAF50,color:#fff
    style D fill:#9C27B0,color:#fff
    style F fill:#9C27B0,color:#fff
    style K fill:#9C27B0,color:#fff"""
    
    save_diagram("how_system_works", diagram)

def simple_architecture():
    """Minimal 3-layer architecture"""
    diagram = """graph TB
    subgraph Frontend["Frontend Layer"]
        UI[Web Interface<br/>HTML + Bootstrap]
    end
    
    subgraph Backend["Backend Layer"]
        Flask[Flask Server]
        Auth[Authentication]
        AI[AI Service]
    end
    
    subgraph Data["Data Layer"]
        DB[(Database)]
        Files[File Storage]
    end
    
    UI --> Flask
    Flask --> Auth
    Flask --> AI
    Auth --> DB
    AI --> DB
    Flask --> Files
    
    AI -.->|API Call| API[OpenRouter AI]
    
    style UI fill:#E3F2FD
    style Flask fill:#FFF3E0
    style AI fill:#F3E5F5
    style DB fill:#E8F5E9
    style API fill:#FCE4EC"""
    
    save_diagram("simple_architecture", diagram)

def working_flow():
    """Complete working flow in one diagram"""
    diagram = """flowchart TD
    Start([User Accesses System]) --> Login[Login/Register]
    Login --> Type{User Type}
    
    Type -->|Student| SP[Student Profile]
    Type -->|HR| HP[HR Profile]
    
    SP --> SI[Start Interview]
    SI --> Gen[AI Generates<br/>Questions]
    Gen --> Ans[Student Answers]
    Ans --> Eval[AI Evaluates<br/>Response]
    Eval --> Feed[Feedback &<br/>Score]
    Feed --> Save1[(Save Results)]
    
    HP --> Job[Create Job Drive]
    Job --> Post[Post Requirements]
    Post --> Apps[Receive Applications]
    Apps --> Rev[Review Candidates]
    Rev --> Sch[Schedule Interviews]
    Sch --> AIInt[AI Interview]
    AIInt --> Eval
    Eval --> Dec[Hiring Decision]
    Dec --> Save2[(Save Records)]
    
    Save1 --> End([Exit])
    Save2 --> End
    
    style Start fill:#4CAF50,color:#fff
    style Gen fill:#9C27B0,color:#fff
    style Eval fill:#9C27B0,color:#fff
    style End fill:#F44336,color:#fff"""
    
    save_diagram("complete_working_flow", diagram)

if __name__ == "__main__":
    print("Generating Compressed Proposed System Diagrams")
    print("=" * 50)
    
    compressed_proposed_system()
    how_system_works()
    simple_architecture()
    working_flow()
    
    print("=" * 50)
    print("Generated 4 compressed diagrams!")
    print("Location: compressed_diagrams/")
    print("\nBest for presentations: compressed_proposed_system.md")
    print("Best for papers: simple_architecture.md")