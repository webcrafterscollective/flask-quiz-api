import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

class DevelopmentConfig(Config):
    """Development configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///quiz.db')
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    FLASK_ENV = 'production'
    # --- CHANGE THIS LINE ---
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') # Changed from SQLALCHEMY_DATABASE_URI
    # --- END OF CHANGE ---
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL')

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}