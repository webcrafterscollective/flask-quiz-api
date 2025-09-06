import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-for-dev')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret-for-dev')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # Use in-memory storage for rate limiting in development
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

class DevelopmentConfig(Config):
    """Development configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///quiz_dev.db')
    FLASK_ENV = 'development'
    
class ProductionConfig(Config):
    """Production configuration."""
    FLASK_ENV = 'production'
    # This correctly reads the database URL provided by Railway
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL')

# Dictionary to access config classes by name
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}