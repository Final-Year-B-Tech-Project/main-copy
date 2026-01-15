# 🎨 Universal Diagram Prompts for AI Interview System

## Complete prompts to generate system diagrams in any tool (ChatGPT, Claude, Gemini, Draw.io, etc.)

---

## 📊 PROMPT 1: Compressed Proposed System Architecture (BEST)

### **For AI Tools (ChatGPT, Claude, Gemini, Copilot):**

```
Create a flowchart diagram for an AI Interview System with the following specifications:

SYSTEM OVERVIEW:
An AI-powered interview platform with dual user roles (Students and HR Professionals)

DIAGRAM REQUIREMENTS:
1. Start with User node (Student/HR)
2. Web Interface for access
3. Authentication system
4. Dashboard that splits into two paths:
   - Student Path: Practice Interview → AI generates questions → Student answers → AI evaluates → Score & Feedback → Save to Database
   - HR Path: Create Job Drive → Post to Database → Schedule Interviews → AI-assisted evaluation

5. Central AI Engine (OpenRouter API) that:
   - Generates interview questions
   - Evaluates student answers
   - Provides scoring and feedback

6. Database for storing:
   - User profiles
   - Interview records
   - Job postings
   - Results and analytics

7. Results display back to Web Interface

COLOR CODING:
- User/Start: Green (#4CAF50)
- AI Processing: Purple (#9C27B0)
- Database: Blue (#2196F3)
- Results/Output: Orange (#FF9800)

STYLE: Professional, clean, flowchart format with clear arrows showing data flow

OUTPUT: Generate as Mermaid diagram code or visual flowchart
```

---

## 📊 PROMPT 2: Simple 3-Layer Architecture

### **For AI Tools:**

```
Create a 3-layer system architecture diagram for an AI Interview System:

LAYER 1 - FRONTEND (Top):
- Web Interface (HTML5 + Bootstrap)
- Responsive UI for cross-platform access

LAYER 2 - BACKEND (Middle):
- Flask Web Server (Python)
- Authentication Module
- AI Service Integration

LAYER 3 - DATA (Bottom):
- SQLite/PostgreSQL Database
- File Storage System

EXTERNAL CONNECTION:
- Backend AI Service connects to OpenRouter API (external)

CONNECTIONS:
- Frontend → Backend (bidirectional)
- Backend → Authentication → Database
- Backend → AI Service → Database
- Backend → File Storage
- AI Service → OpenRouter API (dotted line, external)

COLORS:
- Frontend: Light Blue (#E3F2FD)
- Backend: Light Orange (#FFF3E0)
- AI Service: Light Purple (#F3E5F5)
- Database: Light Green (#E8F5E9)
- External API: Light Pink (#FCE4EC)

STYLE: Layered architecture diagram with clear separation and labeled connections

OUTPUT: Generate as architectural diagram
```

---

## 📊 PROMPT 3: Complete System Workflow

### **For AI Tools:**

```
Create a comprehensive workflow diagram for an AI Interview System showing both user journeys:

START: User accesses system → Login/Register

BRANCH 1 - STUDENT JOURNEY:
1. Student Profile Setup
2. Upload Resume (optional)
3. Start Practice Interview
4. AI Generates Questions (based on profile and job role)
5. Student Answers Questions
6. AI Evaluates Each Response
7. Receive Feedback & Score
8. View Performance History
9. Exit

BRANCH 2 - HR JOURNEY:
1. HR Profile Setup
2. Company Details
3. Create Job Drive
4. Post Job Requirements
5. Receive Student Applications
6. Review Candidates
7. Schedule Interviews
8. AI-Assisted Interview Evaluation
9. Make Hiring Decision
10. Exit

KEY DECISION POINTS:
- After Login: Student or HR?
- After Registration: Account Type?

AI INTEGRATION POINTS:
- Question Generation (Student path)
- Answer Evaluation (Both paths)
- Candidate Assessment (HR path)

COLORS:
- Start/End: Green/Red
- Student Path: Blue nodes
- HR Path: Orange nodes
- AI Processing: Purple nodes
- Database: Cylinder shapes

STYLE: Top-to-bottom flowchart with clear decision diamonds and process rectangles

OUTPUT: Generate as detailed flowchart
```

---

## 📊 PROMPT 4: AI Interview Process Sequence

### **For AI Tools:**

```
Create a sequence diagram showing the AI interview process interaction:

PARTICIPANTS (Left to Right):
1. Student
2. Web Interface
3. Backend Server
4. AI Service
5. Database
6. OpenRouter API

SEQUENCE FLOW:
1. Student → Web Interface: "Start Interview"
2. Web Interface → Backend: "Request Interview Session"
3. Backend → Database: "Fetch Student Profile"
4. Database → Backend: "Return Profile Data"
5. Backend → AI Service: "Generate Questions" (with profile data)
6. AI Service → OpenRouter API: "Request AI Generation"
7. OpenRouter API → AI Service: "Generated Questions"
8. AI Service → Backend: "Question Set"
9. Backend → Database: "Save Interview Session"
10. Backend → Web Interface: "Display Questions"
11. Web Interface → Student: "Show Question 1"

LOOP (For Each Question):
12. Student → Web Interface: "Submit Answer"
13. Web Interface → Backend: "Send Response"
14. Backend → AI Service: "Evaluate Answer"
15. AI Service → OpenRouter API: "Analyze Response"
16. OpenRouter API → AI Service: "Evaluation Score"
17. AI Service → Backend: "Score & Feedback"
18. Backend → Database: "Store Response"
19. Backend → Web Interface: "Next Question"
20. Web Interface → Student: "Display Next"

COMPLETION:
21. Student → Web Interface: "Complete Interview"
22. Web Interface → Backend: "Finish Request"
23. Backend → AI Service: "Generate Final Report"
24. AI Service → OpenRouter API: "Comprehensive Analysis"
25. OpenRouter API → AI Service: "Final Evaluation"
26. AI Service → Backend: "Complete Report"
27. Backend → Database: "Update Records"
28. Backend → Web Interface: "Show Results"
29. Web Interface → Student: "Display Feedback"

STYLE: UML sequence diagram with lifelines and activation boxes

OUTPUT: Generate as sequence diagram
```

---

## 📊 PROMPT 5: Research Methodology Flow

### **For AI Tools:**

```
Create a research methodology flowchart for developing an AI Interview System:

PHASE 1 - ANALYSIS (Red boxes):
1. Problem Identification: Manual Interview Challenges
2. Literature Review: AI in Recruitment
3. Requirements Analysis: Student & HR Needs
4. System Design: Architecture & Database

PHASE 2 - TECHNOLOGY SELECTION (Blue boxes):
From System Design, branch into 4 parallel selections:
- Backend: Flask + Python
- Frontend: HTML5 + Bootstrap
- AI: OpenRouter API
- Database: SQLite

All converge to: Implementation Phase

PHASE 3 - DEVELOPMENT (Green boxes):
Module Development branches into 4 parallel modules:
- Authentication System
- Student Module
- HR Module
- AI Interview Engine

All converge to: Integration & Testing

PHASE 4 - TESTING (Yellow boxes):
System Testing branches into 3 parallel tests:
- Unit Testing
- Integration Testing
- User Acceptance Testing

All converge to: Performance Evaluation

PHASE 5 - FINALIZATION (Pink boxes):
1. Results Analysis & Documentation
2. Deployment & Validation

COLORS:
- Phase 1: Light Red (#FFCDD2)
- Phase 2: Light Blue (#C5CAE9)
- Phase 3: Light Green (#B2DFDB)
- Phase 4: Light Yellow (#FFF9C4)
- Phase 5: Light Pink (#F8BBD0)

STYLE: Top-to-bottom flowchart with clear phase separation

OUTPUT: Generate as methodology flowchart
```

---

## 📊 PROMPT 6: Module Architecture Diagram

### **For AI Tools:**

```
Create a module architecture diagram showing interconnected system modules:

MODULE 1 - AUTHENTICATION (Green):
- User Registration
- Login System
- Session Management
- Role-Based Access Control

MODULE 2 - STUDENT (Blue):
- Profile Management
- Resume Upload
- Practice Interview
- Performance Tracking
- Job Applications

MODULE 3 - HR (Orange):
- Company Profile
- Job Drive Creation
- Candidate Management
- Interview Scheduling
- Analytics Dashboard

MODULE 4 - AI INTERVIEW (Purple):
- Question Generation
- Adaptive Questioning
- Answer Evaluation
- Feedback System
- Performance Scoring

MODULE 5 - DATABASE (Gray):
- User Data
- Interview Data
- Job Data
- Analytics Data

CONNECTIONS:
- Authentication → Student Profile
- Authentication → HR Profile
- Student Practice Interview → AI Question Generation
- AI modules connected in sequence
- HR Job Creation → Database
- All modules connect to respective database components

STYLE: Block diagram with grouped modules and clear connection lines

OUTPUT: Generate as modular architecture diagram
```

---

## 📊 PROMPT 7: Technology Stack Diagram

### **For AI Tools:**

```
Create a technology stack diagram organized in layers:

LAYER 1 - FRONTEND TECHNOLOGIES (Light Blue):
- HTML5
- CSS3 + Bootstrap 5.3
- JavaScript ES6+
- jQuery 3.7

LAYER 2 - BACKEND TECHNOLOGIES (Light Orange):
- Python 3.8+
- Flask 2.3+
- Flask-Login
- Flask-SQLAlchemy
- Werkzeug Security

LAYER 3 - DATABASE (Light Green):
- SQLite (Development)
- PostgreSQL (Production)

LAYER 4 - AI & APIs (Light Purple):
- OpenRouter API
- Grok-4-Fast
- DeepSeek Chat
- GPT-OSS-120B

LAYER 5 - ADDITIONAL TOOLS (Light Gray):
- PyPDF2 (Resume Parser)
- Python-dotenv
- Requests Library
- Email SMTP

CONNECTIONS:
- Frontend → Backend
- Backend → Database
- Backend → AI APIs
- Backend → Additional Tools

STYLE: Layered stack diagram with technology icons/names in boxes

OUTPUT: Generate as technology stack visualization
```

---

## 🛠️ TOOL-SPECIFIC FORMATS

### **For Draw.io / Diagrams.net:**
```
Use the prompts above and specify:
"Create this diagram in Draw.io format with:
- Flowchart shapes from the standard library
- Professional color scheme as specified
- Clear labels and arrows
- Proper alignment and spacing"
```

### **For Lucidchart:**
```
Use the prompts above and specify:
"Create this diagram in Lucidchart format with:
- UML or Flowchart templates
- Professional styling
- Smart connectors
- Grouped elements by layer/module"
```

### **For Microsoft Visio:**
```
Use the prompts above and specify:
"Create this diagram in Visio format with:
- Basic Flowchart or Cross-Functional Flowchart template
- Professional theme
- Auto-layout enabled
- Connector routing"
```

### **For PlantUML:**
```
Use the prompts above and specify:
"Generate PlantUML code for this diagram with:
- Appropriate diagram type (@startuml)
- Skinparam for colors
- Proper syntax for connections
- Comments for clarity"
```

### **For Mermaid (Already Generated):**
```
Use the .md files in:
- compressed_diagrams/
- research_diagrams/
```

---

## 🎯 QUICK COPY-PASTE PROMPTS

### **Ultra-Short Prompt (Any Tool):**
```
Create a flowchart for an AI Interview System:
- Users (Students/HR) login via web interface
- Students: take AI-powered practice interviews, get feedback
- HR: create jobs, schedule interviews, review AI evaluations
- Central AI engine (OpenRouter API) generates questions and evaluates answers
- Database stores all data
- Results displayed on web interface
Use professional colors: Green (users), Purple (AI), Blue (database), Orange (results)
```

### **One-Line Prompt:**
```
Flowchart: User → Web → Auth → [Student: Interview+AI Evaluation | HR: Jobs+Scheduling] → Database → Results, with AI engine (purple) at center
```

---

## 📋 USAGE INSTRUCTIONS

### **Step 1: Choose Your Tool**
- AI Tools: ChatGPT, Claude, Gemini, Copilot
- Diagram Tools: Draw.io, Lucidchart, Visio, PlantUML

### **Step 2: Select Prompt**
- Compressed System: Use Prompt 1
- Architecture: Use Prompt 2
- Workflow: Use Prompt 3
- Sequence: Use Prompt 4
- Methodology: Use Prompt 5

### **Step 3: Copy & Paste**
- Copy the entire prompt
- Paste into your chosen tool
- Adjust if needed

### **Step 4: Refine**
- Ask for modifications
- Request different colors
- Change layout orientation

---

## 💡 PRO TIPS

1. **For AI Tools**: Start with "Create a Mermaid diagram" for code output
2. **For Visual Tools**: Start with "Create a flowchart diagram" for visual output
3. **Add Context**: Mention it's for a research paper/presentation
4. **Specify Format**: Request PNG, SVG, or code as needed
5. **Iterate**: Ask for refinements after first generation

---

## ✅ VALIDATION CHECKLIST

After generating, ensure diagram has:
- [ ] Clear start and end points
- [ ] All user roles shown (Student & HR)
- [ ] AI integration clearly marked
- [ ] Database storage indicated
- [ ] Proper color coding
- [ ] Readable labels
- [ ] Logical flow direction
- [ ] Professional appearance

---

**These prompts work with:**
✅ ChatGPT (GPT-4, GPT-3.5)
✅ Claude (Anthropic)
✅ Google Gemini
✅ Microsoft Copilot
✅ Draw.io / Diagrams.net
✅ Lucidchart
✅ Microsoft Visio
✅ PlantUML
✅ Any diagram generation tool

---

**Copy any prompt above and paste it into your preferred tool to generate professional diagrams instantly! 🎨**