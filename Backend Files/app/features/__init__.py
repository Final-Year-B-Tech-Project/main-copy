"""
Features Module - Modular Feature Architecture
Each feature is isolated in its own file for easy maintenance and modification
"""

from .feature_registry import (
    FeatureRegistry,
    InterviewTimer,
    VoiceRecognitionConfig,
    AdaptiveQuestions,
    ProfessionalOpening,
    AuthenticScoring
)

from .resume_parser import ResumeParser
from .assessment_monitor import AssessmentMonitor
from .training_system import TrainingSystem
from .behavioral_analyzer import BehavioralAnalyzer
from .security_system import SecuritySystem
from .duration_manager import DurationManager

__all__ = [
    'FeatureRegistry',
    'InterviewTimer',
    'VoiceRecognitionConfig',
    'AdaptiveQuestions',
    'ProfessionalOpening',
    'AuthenticScoring',
    'ResumeParser',
    'AssessmentMonitor',
    'TrainingSystem',
    'BehavioralAnalyzer',
    'SecuritySystem',
    'DurationManager'
]
