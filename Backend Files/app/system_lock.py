"""
SYSTEM LOCK - CORE WORKFLOW PROTECTION
This file defines the locked core system that MUST NOT be modified by new features
All new features must integrate through feature hooks, not by modifying core files
"""

# LOCKED CORE FILES - DO NOT MODIFY
LOCKED_CORE_FILES = [
    'app/__init__.py',           # Flask app initialization
    'app/models.py',             # Database models
    'app/auth.py',               # Authentication system
    'config.py',                 # Core configuration
    'run.py',                    # Application entry point
]

# LOCKED CORE ROUTES - DO NOT MODIFY
LOCKED_CORE_ROUTES = [
    '/login',
    '/register',
    '/logout',
    '/dashboard',
]

# LOCKED DATABASE SCHEMA - DO NOT MODIFY
LOCKED_DB_TABLES = [
    'user',
    'student_profile',
    'hr_profile',
    'job_drive',
    'interview_session',
]

# FEATURE INTEGRATION POINTS - USE THESE ONLY
FEATURE_HOOKS = {
    'before_interview_start': [],      # Hook before interview starts
    'after_interview_start': [],       # Hook after interview starts
    'before_question_generate': [],    # Hook before generating question
    'after_question_generate': [],     # Hook after generating question
    'before_response_process': [],     # Hook before processing response
    'after_response_process': [],      # Hook after processing response
    'before_interview_end': [],        # Hook before interview ends
    'after_interview_end': [],         # Hook after interview ends
    'before_scoring': [],              # Hook before scoring
    'after_scoring': [],               # Hook after scoring
}

# FEATURE REGISTRATION
REGISTERED_FEATURES = {}

def register_feature(feature_name, feature_class, hooks=None):
    """
    Register new feature without modifying core system
    
    Args:
        feature_name: Unique feature identifier
        feature_class: Feature implementation class
        hooks: Dict of hook names and methods to call
    """
    if feature_name in REGISTERED_FEATURES:
        raise ValueError(f"Feature {feature_name} already registered")
    
    REGISTERED_FEATURES[feature_name] = {
        'class': feature_class,
        'enabled': True,
        'hooks': hooks or {}
    }
    
    # Register hooks
    if hooks:
        for hook_name, method in hooks.items():
            if hook_name in FEATURE_HOOKS:
                FEATURE_HOOKS[hook_name].append({
                    'feature': feature_name,
                    'method': method
                })

def execute_hook(hook_name, *args, **kwargs):
    """Execute all registered methods for a hook"""
    results = []
    if hook_name in FEATURE_HOOKS:
        for hook_data in FEATURE_HOOKS[hook_name]:
            feature_name = hook_data['feature']
            if REGISTERED_FEATURES[feature_name]['enabled']:
                method = hook_data['method']
                result = method(*args, **kwargs)
                results.append(result)
    return results

def disable_feature(feature_name):
    """Disable feature without removing it"""
    if feature_name in REGISTERED_FEATURES:
        REGISTERED_FEATURES[feature_name]['enabled'] = False

def enable_feature(feature_name):
    """Enable previously disabled feature"""
    if feature_name in REGISTERED_FEATURES:
        REGISTERED_FEATURES[feature_name]['enabled'] = True

def is_feature_enabled(feature_name):
    """Check if feature is enabled"""
    return REGISTERED_FEATURES.get(feature_name, {}).get('enabled', False)
