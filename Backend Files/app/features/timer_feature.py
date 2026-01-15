"""
Interview Timer Feature
Handles 20-minute interview duration with warnings and auto-end
"""

class InterviewTimer:
    DURATION_SECONDS = 1200  # 20 minutes
    WARNING_AT = 300  # 5 minutes remaining
    CRITICAL_AT = 60  # 1 minute remaining
    
    @staticmethod
    def get_duration():
        return InterviewTimer.DURATION_SECONDS
    
    @staticmethod
    def should_warn(remaining):
        return remaining == InterviewTimer.WARNING_AT
    
    @staticmethod
    def is_critical(remaining):
        return remaining <= InterviewTimer.CRITICAL_AT
    
    @staticmethod
    def is_expired(remaining):
        return remaining <= 0
