#!/usr/bin/env python3
"""
Custom Mermaid Diagrams for Specific Use Cases
Additional specialized diagrams for the AI Interview System
"""

import os
from mermaid_generator import MermaidGenerator

class CustomDiagramGenerator(MermaidGenerator):
    """Extended generator for custom and specialized diagrams"""
    
    def generate_security_flow(self):
        """Generate security and authentication flow"""
        diagram = """flowchart TD
    Start([User Access Request]) --> HTTPS{HTTPS?}
    HTTPS -->|No| Redirect[Redirect to HTTPS]
    HTTPS -->|Yes| Auth{Authenticated?}
    
    Redirect --> Auth
    Auth -->|No| Login[Login Required]
    Auth -->|Yes| Role{User Role?}
    
    Login --> Validate{Valid Credentials?}
    Validate -->|No| LoginFail[Login Failed]
    Validate -->|Yes| Session[Create Session]
    
    LoginFail --> RateLimit{Rate Limited?}
    RateLimit -->|Yes| Block[Block IP]
    RateLimit -->|No| Login
    
    Session --> Role
    Role -->|Student| StudentAuth[Student Authorization]
    Role -->|HR| HRAuth[HR Authorization]
    Role -->|Admin| AdminAuth[Admin Authorization]
    
    StudentAuth --> StudentAccess[Access Student Features]
    HRAuth --> HRAccess[Access HR Features]
    AdminAuth --> AdminAccess[Access Admin Features]
    
    StudentAccess --> CSRF{CSRF Token Valid?}
    HRAccess --> CSRF
    AdminAccess --> CSRF
    
    CSRF -->|No| SecurityError[Security Error]
    CSRF -->|Yes| ProcessRequest[Process Request]
    
    ProcessRequest --> Audit[Log Activity]
    SecurityError --> Audit
    
    Audit --> Response[Send Response]"""
        
        self.save_diagram("security_flow", diagram)
    
    def generate_ai_processing_flow(self):
        """Generate AI processing and decision flow"""
        diagram = """flowchart TD
    Input[User Input/Answer] --> Preprocess[Preprocess Text]
    Preprocess --> Validate{Input Valid?}
    
    Validate -->|No| Error[Return Error]
    Validate -->|Yes| Context[Get Context Data]
    
    Context --> Profile[Load User Profile]
    Context --> JobReq[Load Job Requirements]
    Context --> History[Load Interview History]
    
    Profile --> AIRequest[Prepare AI Request]
    JobReq --> AIRequest
    History --> AIRequest
    
    AIRequest --> RateLimit{Within Rate Limit?}
    RateLimit -->|No| Queue[Add to Queue]
    RateLimit -->|Yes| GeminiAPI[Call Gemini API]
    
    Queue --> Wait[Wait for Slot]
    Wait --> GeminiAPI
    
    GeminiAPI --> APIResponse{API Success?}
    APIResponse -->|No| Retry{Retry Count < 3?}
    APIResponse -->|Yes| ParseResponse[Parse AI Response]
    
    Retry -->|Yes| GeminiAPI
    Retry -->|No| Fallback[Use Fallback Logic]
    
    ParseResponse --> Validate2{Response Valid?}
    Validate2 -->|No| Fallback
    Validate2 -->|Yes| Score[Calculate Score]
    
    Fallback --> Score
    Score --> Feedback[Generate Feedback]
    Feedback --> Store[Store Results]
    Store --> Return[Return to User]"""
        
        self.save_diagram("ai_processing_flow", diagram)
    
    def generate_data_flow(self):
        """Generate data flow diagram"""
        diagram = """flowchart LR
    subgraph "Data Sources"
        UserInput[User Input]
        FileUpload[File Uploads]
        APIData[External API Data]
    end
    
    subgraph "Data Processing"
        Validation[Data Validation]
        Transformation[Data Transformation]
        Enrichment[Data Enrichment]
    end
    
    subgraph "Data Storage"
        Database[(Primary Database)]
        FileSystem[File System]
        Cache[(Cache Layer)]
        Logs[Log Files]
    end
    
    subgraph "Data Output"
        WebResponse[Web Response]
        EmailNotif[Email Notifications]
        Reports[Generated Reports]
        Analytics[Analytics Data]
    end
    
    UserInput --> Validation
    FileUpload --> Validation
    APIData --> Validation
    
    Validation --> Transformation
    Transformation --> Enrichment
    
    Enrichment --> Database
    Enrichment --> FileSystem
    Enrichment --> Cache
    Enrichment --> Logs
    
    Database --> WebResponse
    Database --> EmailNotif
    Database --> Reports
    Database --> Analytics
    
    Cache --> WebResponse
    FileSystem --> WebResponse"""
        
        self.save_diagram("data_flow", diagram)
    
    def generate_error_handling(self):
        """Generate error handling and recovery flow"""
        diagram = """flowchart TD
    Operation[System Operation] --> Success{Success?}
    
    Success -->|Yes| Complete[Operation Complete]
    Success -->|No| ErrorType{Error Type?}
    
    ErrorType -->|Validation| ValidationError[Validation Error]
    ErrorType -->|Database| DatabaseError[Database Error]
    ErrorType -->|API| APIError[External API Error]
    ErrorType -->|System| SystemError[System Error]
    
    ValidationError --> LogError[Log Error Details]
    DatabaseError --> LogError
    APIError --> LogError
    SystemError --> LogError
    
    LogError --> UserFriendly[Generate User-Friendly Message]
    
    DatabaseError --> DBRetry{Retry Available?}
    DBRetry -->|Yes| RetryDB[Retry Database Operation]
    DBRetry -->|No| Fallback[Use Fallback Method]
    
    APIError --> APIRetry{Retry Available?}
    APIRetry -->|Yes| RetryAPI[Retry API Call]
    APIRetry -->|No| CachedData[Use Cached Data]
    
    RetryDB --> Success
    RetryAPI --> Success
    Fallback --> UserFriendly
    CachedData --> UserFriendly
    
    UserFriendly --> NotifyUser[Notify User]
    NotifyUser --> RecoveryAction{Recovery Possible?}
    
    RecoveryAction -->|Yes| SuggestAction[Suggest Recovery Action]
    RecoveryAction -->|No| GracefulDegradation[Graceful Degradation]
    
    SuggestAction --> Complete
    GracefulDegradation --> Complete"""
        
        self.save_diagram("error_handling", diagram)
    
    def generate_performance_monitoring(self):
        """Generate performance monitoring diagram"""
        diagram = """graph TB
    subgraph "Monitoring Points"
        WebReq[Web Requests]
        DBQuery[Database Queries]
        APICall[External API Calls]
        FileOp[File Operations]
    end
    
    subgraph "Metrics Collection"
        ResponseTime[Response Time]
        Throughput[Throughput]
        ErrorRate[Error Rate]
        ResourceUsage[Resource Usage]
    end
    
    subgraph "Analysis Engine"
        Aggregation[Data Aggregation]
        Trending[Trend Analysis]
        Alerting[Alert Generation]
        Reporting[Report Generation]
    end
    
    subgraph "Storage & Visualization"
        MetricsDB[(Metrics Database)]
        Dashboard[Performance Dashboard]
        Alerts[Alert System]
        Reports[Performance Reports]
    end
    
    WebReq --> ResponseTime
    WebReq --> Throughput
    WebReq --> ErrorRate
    
    DBQuery --> ResponseTime
    APICall --> ResponseTime
    FileOp --> ResourceUsage
    
    ResponseTime --> Aggregation
    Throughput --> Aggregation
    ErrorRate --> Aggregation
    ResourceUsage --> Aggregation
    
    Aggregation --> MetricsDB
    Aggregation --> Trending
    Trending --> Alerting
    Alerting --> Alerts
    
    MetricsDB --> Dashboard
    MetricsDB --> Reporting
    Reporting --> Reports"""
        
        self.save_diagram("performance_monitoring", diagram)
    
    def generate_backup_recovery(self):
        """Generate backup and recovery strategy"""
        diagram = """flowchart TD
    Schedule[Backup Schedule] --> BackupType{Backup Type?}
    
    BackupType -->|Full| FullBackup[Full Database Backup]
    BackupType -->|Incremental| IncrementalBackup[Incremental Backup]
    BackupType -->|Files| FileBackup[File System Backup]
    
    FullBackup --> Compress[Compress Backup]
    IncrementalBackup --> Compress
    FileBackup --> Compress
    
    Compress --> Encrypt[Encrypt Backup]
    Encrypt --> Store[Store Backup]
    
    Store --> LocalStorage[Local Storage]
    Store --> CloudStorage[Cloud Storage]
    Store --> OffSite[Off-site Storage]
    
    LocalStorage --> Verify[Verify Backup Integrity]
    CloudStorage --> Verify
    OffSite --> Verify
    
    Verify --> Success{Backup Valid?}
    Success -->|Yes| UpdateLog[Update Backup Log]
    Success -->|No| Alert[Send Alert]
    
    Alert --> RetryBackup[Retry Backup]
    RetryBackup --> BackupType
    
    UpdateLog --> Retention[Apply Retention Policy]
    Retention --> Cleanup[Cleanup Old Backups]
    
    DisasterEvent[Disaster Event] --> AssessImpact[Assess Impact]
    AssessImpact --> RecoveryPlan[Select Recovery Plan]
    
    RecoveryPlan --> RestoreData[Restore Data]
    RestoreData --> ValidateRestore[Validate Restoration]
    ValidateRestore --> SystemTest[System Testing]
    SystemTest --> GoLive[Go Live]"""
        
        self.save_diagram("backup_recovery", diagram)
    
    def generate_testing_strategy(self):
        """Generate testing strategy diagram"""
        diagram = """graph TB
    subgraph "Test Types"
        Unit[Unit Tests]
        Integration[Integration Tests]
        System[System Tests]
        Performance[Performance Tests]
        Security[Security Tests]
        UAT[User Acceptance Tests]
    end
    
    subgraph "Test Automation"
        CI[Continuous Integration]
        TestRunner[Test Runner]
        Coverage[Code Coverage]
        Reporting[Test Reporting]
    end
    
    subgraph "Test Environments"
        Dev[Development]
        Staging[Staging]
        PreProd[Pre-Production]
        Prod[Production]
    end
    
    subgraph "Test Data"
        MockData[Mock Data]
        TestDB[Test Database]
        Fixtures[Test Fixtures]
        Factories[Data Factories]
    end
    
    Unit --> CI
    Integration --> CI
    System --> TestRunner
    Performance --> TestRunner
    Security --> TestRunner
    UAT --> Manual[Manual Testing]
    
    CI --> Dev
    TestRunner --> Staging
    Manual --> PreProd
    
    MockData --> Unit
    TestDB --> Integration
    Fixtures --> System
    Factories --> Performance
    
    CI --> Coverage
    TestRunner --> Coverage
    Coverage --> Reporting
    
    Reporting --> QualityGate{Quality Gate Pass?}
    QualityGate -->|Yes| Deploy[Deploy to Next Environment]
    QualityGate -->|No| FixIssues[Fix Issues]
    
    FixIssues --> Unit"""
        
        self.save_diagram("testing_strategy", diagram)
    
    def generate_all_custom_diagrams(self):
        """Generate all custom diagrams"""
        print("Generating custom specialized diagrams...")
        print("=" * 50)
        
        custom_diagrams = [
            ("Security Flow", self.generate_security_flow),
            ("AI Processing Flow", self.generate_ai_processing_flow),
            ("Data Flow", self.generate_data_flow),
            ("Error Handling", self.generate_error_handling),
            ("Performance Monitoring", self.generate_performance_monitoring),
            ("Backup & Recovery", self.generate_backup_recovery),
            ("Testing Strategy", self.generate_testing_strategy)
        ]
        
        for name, generator in custom_diagrams:
            print(f"Generating {name}...")
            generator()
        
        print("=" * 50)
        print(f"All custom diagrams generated successfully!")

if __name__ == "__main__":
    generator = CustomDiagramGenerator()
    generator.generate_all_custom_diagrams()