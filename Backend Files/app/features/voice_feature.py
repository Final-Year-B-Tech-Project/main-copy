"""
Voice Recognition Feature
Handles voice input with anti-interruption logic
"""

class VoiceRecognitionConfig:
    RESTART_DELAY_MS = 3000  # 3 seconds delay before restart
    PROCESSING_DELAY_MS = 3000  # 3 seconds delay during AI processing
    
    @staticmethod
    def get_restart_delay():
        return VoiceRecognitionConfig.RESTART_DELAY_MS
    
    @staticmethod
    def get_processing_delay():
        return VoiceRecognitionConfig.PROCESSING_DELAY_MS
