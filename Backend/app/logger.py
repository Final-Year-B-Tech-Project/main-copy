import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import request
from flask_login import current_user

class SystemLogger:
    """Custom logging system for the AI Interview application."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize logging for the Flask app."""
        # Create logs directory
        log_dir = os.path.join(app.root_path, '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        log_file = os.path.join(log_dir, 'system.log')
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        # Set log format
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Configure app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        
        # Log application startup
        app.logger.info("AI Interview System started")
    
    @staticmethod
    def log_user_action(action, details=""):
        """Log user actions."""
        try:
            user_info = "Anonymous"
            if current_user.is_authenticated:
                user_info = f"{current_user.username} ({current_user.user_type})"
            
            ip_address = request.remote_addr if request else "Unknown"
            
            message = f"USER_ACTION | {user_info} | {ip_address} | {action}"
            if details:
                message += f" | {details}"
            
            from flask import current_app
            current_app.logger.info(message)
        except:
            pass  # Don't break the app if logging fails
    
    @staticmethod
    def log_interview_action(session_id, action, details=""):
        """Log interview-related actions."""
        try:
            user_info = "Anonymous"
            if current_user.is_authenticated:
                user_info = f"{current_user.username}"
            
            message = f"INTERVIEW | Session:{session_id} | {user_info} | {action}"
            if details:
                message += f" | {details}"
            
            from flask import current_app
            current_app.logger.info(message)
        except:
            pass
    
    @staticmethod
    def log_admin_action(action, details=""):
        """Log admin actions."""
        try:
            user_info = "Unknown Admin"
            if current_user.is_authenticated:
                user_info = f"{current_user.username} ({current_user.role})"
            
            message = f"ADMIN_ACTION | {user_info} | {action}"
            if details:
                message += f" | {details}"
            
            from flask import current_app
            current_app.logger.warning(message)  # Use warning level for admin actions
        except:
            pass
    
    @staticmethod
    def log_security_event(event, details=""):
        """Log security-related events."""
        try:
            user_info = "Anonymous"
            if current_user.is_authenticated:
                user_info = f"{current_user.username}"
            
            ip_address = request.remote_addr if request else "Unknown"
            
            message = f"SECURITY | {user_info} | {ip_address} | {event}"
            if details:
                message += f" | {details}"
            
            from flask import current_app
            current_app.logger.error(message)  # Use error level for security events
        except:
            pass
    
    @staticmethod
    def log_system_event(event, details=""):
        """Log system events."""
        try:
            message = f"SYSTEM | {event}"
            if details:
                message += f" | {details}"
            
            from flask import current_app
            current_app.logger.info(message)
        except:
            pass

# Create global logger instance
system_logger = SystemLogger()

# Convenience functions
def log_user_action(action, details=""):
    SystemLogger.log_user_action(action, details)

def log_interview_action(session_id, action, details=""):
    SystemLogger.log_interview_action(session_id, action, details)

def log_admin_action(action, details=""):
    SystemLogger.log_admin_action(action, details)

def log_security_event(event, details=""):
    SystemLogger.log_security_event(event, details)

def log_system_event(event, details=""):
    SystemLogger.log_system_event(event, details)