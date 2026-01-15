"""
FEATURE INTEGRATION GUIDE
═══════════════════════════════════════════════════════════════════════════════

CORE SYSTEM IS LOCKED - DO NOT MODIFY:
- app/__init__.py
- app/models.py
- app/auth.py
- config.py
- run.py

═══════════════════════════════════════════════════════════════════════════════
AVAILABLE FEATURES
═══════════════════════════════════════════════════════════════════════════════

1. resume_parser.py          - Resume parsing & skill extraction
2. assessment_monitor.py     - Real-time assessment monitoring
3. training_system.py        - Training & mock interviews
4. behavioral_analyzer.py    - Face, eye, posture analysis
5. security_system.py        - Tab detection, fullscreen enforcement
6. duration_manager.py       - Time-based interview optimization

═══════════════════════════════════════════════════════════════════════════════
HOW TO USE A FEATURE
═══════════════════════════════════════════════════════════════════════════════

# Import the feature
from app.features import ResumeParser

# Use it
skills = ResumeParser.extract_skills(resume_text)
eligible = ResumeParser.is_eligible(resume_text, job_requirements)

═══════════════════════════════════════════════════════════════════════════════
HOW TO ADD NEW FEATURE
═══════════════════════════════════════════════════════════════════════════════

1. Create new file: app/features/my_feature.py

2. Write your feature class:

from app.system_lock import register_feature

class MyFeature:
    @staticmethod
    def do_something():
        return "result"

register_feature('my_feature', MyFeature)

3. Export in app/features/__init__.py:

from .my_feature import MyFeature
__all__ = [..., 'MyFeature']

4. Use it anywhere:

from app.features import MyFeature
result = MyFeature.do_something()

═══════════════════════════════════════════════════════════════════════════════
FEATURE HOOKS (Advanced)
═══════════════════════════════════════════════════════════════════════════════

Available hooks:
- before_interview_start
- after_interview_start
- before_question_generate
- after_question_generate
- before_response_process
- after_response_process
- before_interview_end
- after_interview_end
- before_scoring
- after_scoring

Example:

register_feature('my_feature', MyFeature, hooks={
    'before_interview_start': MyFeature.initialize
})

═══════════════════════════════════════════════════════════════════════════════
"""
