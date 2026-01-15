import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # Set template and static folder paths relative to Backend Files directory
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    mail.init_app(app)
    
    # Create upload directories
    upload_dir = os.path.join(app.root_path, '..', app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(os.path.join(upload_dir, 'resumes'), exist_ok=True)
    os.makedirs(os.path.join(upload_dir, 'photos'), exist_ok=True)
    
    # Initialize logging
    from app.logger import system_logger
    system_logger.init_app(app)
    
    # Register blueprints
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from app.admin import admin_bp as admin_blueprint
    app.register_blueprint(admin_blueprint)
    
    from app.student import student_bp as student_blueprint
    app.register_blueprint(student_blueprint)
    
    try:
        from app.hr_simple import hr as hr_blueprint
        app.register_blueprint(hr_blueprint)
    except ImportError as e:
        print(f"HR blueprint disabled due to import error: {e}")
    
    # Register database admin blueprint
    from app.db_admin import db_admin as db_admin_blueprint
    app.register_blueprint(db_admin_blueprint)
    
    # Register resume API blueprint
    from app.resume_api import resume_api as resume_api_blueprint
    app.register_blueprint(resume_api_blueprint)
    
    # Register test routes
    from app.test_routes import test_bp as test_blueprint
    app.register_blueprint(test_blueprint)
    
    # Register proctoring routes
    try:
        from proctoring_system.routes import proctoring_bp
        app.register_blueprint(proctoring_bp)
        print("✓ Proctoring system loaded successfully")
        
        # Skip proctoring models for now to avoid DB issues
        # from proctoring_system.models import ProctoringSession, ProctoringViolation, ProctoringFrameLog, ProctoringAlert
        # print("✓ Proctoring models registered")
        
    except ImportError as e:
        print(f"⚠ Proctoring system disabled due to import error: {e}")
    except Exception as e:
        print(f"⚠ Proctoring system disabled due to error: {e}")
    
    # Register adaptive models for database creation
    from app.adaptive_models import AdaptiveSession, AdaptiveQuestion, AdaptiveResponse
    
    # Register resume models for database creation
    from app.resume_models import CandidateSkill, ParsedResume, JobRequirement, CandidateScore, ResumeParsingLog
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Context processor for template variables
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.now().year}
    
    # Custom template filters
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Parse JSON string in templates"""
        try:
            import json
            if isinstance(value, str):
                return json.loads(value)
            return value
        except:
            return []
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Skip automatic admin creation to avoid column issues
        pass
    
    return app