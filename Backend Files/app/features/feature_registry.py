"""
Feature Registry
Central registry for all modular features
Easy to enable/disable features without touching core code
"""

from .timer_feature import InterviewTimer
from .voice_feature import VoiceRecognitionConfig
from .adaptive_questions_feature import AdaptiveQuestions
from .opening_feature import ProfessionalOpening
from .scoring_feature import AuthenticScoring

class FeatureRegistry:
    """
    Central feature management
    Add new features here without modifying existing code
    """
    
    # Feature flags
    FEATURES = {
        'timer': True,
        'voice_recognition': True,
        'adaptive_questions': True,
        'professional_opening': True,
        'authentic_scoring': True,
    }
    
    @staticmethod
    def is_enabled(feature_name):
        """Check if feature is enabled"""
        return FeatureRegistry.FEATURES.get(feature_name, False)
    
    @staticmethod
    def get_timer():
        """Get timer feature"""
        if FeatureRegistry.is_enabled('timer'):
            return InterviewTimer
        return None
    
    @staticmethod
    def get_voice_config():
        """Get voice recognition config"""
        if FeatureRegistry.is_enabled('voice_recognition'):
            return VoiceRecognitionConfig
        return None
    
    @staticmethod
    def get_adaptive_questions():
        """Get adaptive questions feature"""
        if FeatureRegistry.is_enabled('adaptive_questions'):
            return AdaptiveQuestions
        return None
    
    @staticmethod
    def get_opening():
        """Get professional opening feature"""
        if FeatureRegistry.is_enabled('professional_opening'):
            return ProfessionalOpening
        return None
    
    @staticmethod
    def get_scoring():
        """Get authentic scoring feature"""
        if FeatureRegistry.is_enabled('authentic_scoring'):
            return AuthenticScoring
        return None

# Export all features
__all__ = [
    'FeatureRegistry',
    'InterviewTimer',
    'VoiceRecognitionConfig',
    'AdaptiveQuestions',
    'ProfessionalOpening',
    'AuthenticScoring'
]
