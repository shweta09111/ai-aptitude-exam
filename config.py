import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production-2025'
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'aptitude_exam.db'
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application config
    MAX_QUESTIONS_PER_EXAM = 50
    ADAPTIVE_EXAM_MIN_QUESTIONS = 5
    ADAPTIVE_EXAM_MAX_QUESTIONS = 20
    
    # Performance config
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # Admin config
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    
    # Export limits
    MAX_EXPORT_RECORDS = 10000
    
    # File upload config
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
class DevelopmentConfig(Config):
    """Development configuration"""  
    DEBUG = True
    TESTING = False
    
class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_PATH = 'test_aptitude_exam.db'
    SECRET_KEY = 'test-secret-key'

# Configuration dictionary - THIS IS WHAT WAS MISSING
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
