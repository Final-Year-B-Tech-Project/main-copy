#!/usr/bin/env python3
"""
Focused Diagram Generator - Block Diagrams, Flowcharts, Methodology
Minimal code for essential documentation diagrams
"""

import os

class FocusedDiagramGenerator:
    def __init__(self, output_dir="focused_diagrams"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def save_diagram(self, filename, content):
        filepath = os.path.join(self.output_dir, f"{filename}.md")
        with open(filepath, 'w') as f:
            f.write(f"# {filename.replace('_', ' ').title()}\n\n```mermaid\n{content}\n```\n")
        print(f"Generated: {filepath}")
    
    def generate_system_block_diagram(self):
        """Main system block diagram"""
        diagram = """block-beta
    columns 3
    
    Frontend["Frontend Layer"]:3
    space:3
    
    Auth["Authentication"] Student["Student Module"] HR["HR Module"]
    space:3
    
    AI["AI Engine"] Interview["Interview Engine"] Analytics["Analytics"]
    space:3
    
    Database[("Database")] Files[("File Storage")] Cache[("Cache")]
    
    Frontend --> Auth
    Frontend --> Student  
    Frontend --> HR
    
    Student --> Interview
    HR --> Interview
    Interview --> AI
    
    Auth --> Database
    Student --> Database
    HR --> Database
    Interview --> Database
    
    Student --> Files
    HR --> Files"""
        
        self.save_diagram("system_block_diagram", diagram)
    
    def generate_ai_interview_flowchart(self):
        """AI Interview process flowchart"""
        diagram = """flowchart TD
    Start([Student Starts Interview]) --> Profile[Load Student Profile]
    Profile --> Generate[AI Generates Questions]
    Generate --> Display[Display Question]
    Display --> Answer[Student Answers]
    Answer --> Evaluate[AI Evaluates Response]
    Evaluate --> Score[Calculate Score]
    Score --> More{More Questions?}
    More -->|Yes| Generate
    More -->|No| Final[Generate Final Report]
    Final --> Save[Save Results]
    Save --> End([Interview Complete])"""
        
        self.save_diagram("ai_interview_flowchart", diagram)
    
    def generate_user_registration_flowchart(self):
        """User registration flowchart"""
        diagram = """flowchart TD
    Start([User Visits Site]) --> Choose{Choose User Type}
    Choose -->|Student| StudentForm[Fill Student Form]
    Choose -->|HR| HRForm[Fill HR Form]
    
    StudentForm --> ValidateS[Validate Student Data]
    HRForm --> ValidateH[Validate HR Data]
    
    ValidateS --> SaveS[Save Student Profile]
    ValidateH --> SaveH[Save HR Profile]
    
    SaveS --> LoginS[Auto Login Student]
    SaveH --> LoginH[Auto Login HR]
    
    LoginS --> DashS[Student Dashboard]
    LoginH --> DashH[HR Dashboard]"""
        
        self.save_diagram("user_registration_flowchart", diagram)
    
    def generate_methodology_diagram(self):
        """Project methodology diagram"""
        diagram = """flowchart TB
    subgraph "Phase 1: Analysis"
        A1[Requirements Gathering]
        A2[System Analysis]
        A3[Technology Selection]
    end
    
    subgraph "Phase 2: Design"
        D1[Database Design]
        D2[UI/UX Design]
        D3[API Design]
    end
    
    subgraph "Phase 3: Development"
        Dev1[Backend Development]
        Dev2[Frontend Development]
        Dev3[AI Integration]
    end
    
    subgraph "Phase 4: Testing"
        T1[Unit Testing]
        T2[Integration Testing]
        T3[User Testing]
    end
    
    subgraph "Phase 5: Deployment"
        Dep1[Production Setup]
        Dep2[Performance Optimization]
        Dep3[Documentation]
    end
    
    A1 --> A2 --> A3
    A3 --> D1 --> D2 --> D3
    D3 --> Dev1 --> Dev2 --> Dev3
    Dev3 --> T1 --> T2 --> T3
    T3 --> Dep1 --> Dep2 --> Dep3"""
        
        self.save_diagram("project_methodology", diagram)
    
    def generate_data_flow_diagram(self):
        """Simplified data flow"""
        diagram = """flowchart LR
    Input[User Input] --> Process[Data Processing]
    Upload[File Upload] --> Process
    
    Process --> Validate[Validation]
    Validate --> Store[(Database)]
    Validate --> AI[AI Processing]
    
    AI --> Response[Generate Response]
    Store --> Response
    
    Response --> Output[User Interface]"""
        
        self.save_diagram("data_flow_diagram", diagram)
    
    def generate_hr_workflow(self):
        """HR workflow diagram"""
        diagram = """flowchart TD
    Login[HR Login] --> Dashboard[HR Dashboard]
    Dashboard --> Create[Create Job Drive]
    Create --> Post[Post Job]
    Post --> Applications[Receive Applications]
    Applications --> Review[Review Candidates]
    Review --> Schedule[Schedule Interviews]
    Schedule --> Conduct[Conduct Interviews]
    Conduct --> Evaluate[Evaluate Results]
    Evaluate --> Decision[Make Decision]
    Decision --> Notify[Notify Candidates]"""
        
        self.save_diagram("hr_workflow", diagram)
    
    def generate_student_workflow(self):
        """Student workflow diagram"""
        diagram = """flowchart TD
    Register[Student Registration] --> Profile[Complete Profile]
    Profile --> Upload[Upload Resume]
    Upload --> Practice[Start Practice Interview]
    Practice --> Questions[Answer Questions]
    Questions --> Feedback[Receive AI Feedback]
    Feedback --> Improve[Improve Skills]
    Improve --> Apply[Apply for Jobs]
    Apply --> Interview[Real Interview]
    Interview --> Results[View Results]"""
        
        self.save_diagram("student_workflow", diagram)
    
    def generate_architecture_blocks(self):
        """Architecture block diagram"""
        diagram = """block-beta
    columns 4
    
    block:Frontend:2
        UI["User Interface"]
        JS["JavaScript"]
    end
    
    block:Backend:2
        API["REST API"]
        Auth["Authentication"]
    end
    
    space:4
    
    block:Services:4
        Student["Student Service"] HR["HR Service"] Interview["Interview Service"] AI["AI Service"]
    end
    
    space:4
    
    block:Data:4
        DB[("Database")] Files[("Files")] Cache[("Cache")] Logs[("Logs")]
    end
    
    Frontend --> Backend
    Backend --> Services
    Services --> Data"""
        
        self.save_diagram("architecture_blocks", diagram)
    
    def generate_all_focused_diagrams(self):
        """Generate all focused diagrams"""
        print("Generating focused diagrams for AI Interview System...")
        print("=" * 50)
        
        diagrams = [
            ("System Block Diagram", self.generate_system_block_diagram),
            ("AI Interview Flowchart", self.generate_ai_interview_flowchart),
            ("User Registration Flowchart", self.generate_user_registration_flowchart),
            ("Project Methodology", self.generate_methodology_diagram),
            ("Data Flow Diagram", self.generate_data_flow_diagram),
            ("HR Workflow", self.generate_hr_workflow),
            ("Student Workflow", self.generate_student_workflow),
            ("Architecture Blocks", self.generate_architecture_blocks)
        ]
        
        for name, generator in diagrams:
            print(f"Generating {name}...")
            generator()
        
        print("=" * 50)
        print(f"Generated {len(diagrams)} focused diagrams!")
        print(f"Location: {self.output_dir}/")

if __name__ == "__main__":
    generator = FocusedDiagramGenerator()
    generator.generate_all_focused_diagrams()