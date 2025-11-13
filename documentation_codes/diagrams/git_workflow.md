# Git Workflow

```mermaid
gitgraph
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
    commit id: "v1.1.0 Release
```
