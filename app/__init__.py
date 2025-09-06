# app/__init__.py

import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

if os.getenv('RAILWAY_ENVIRONMENT') != 'production':
    print("Not in Railway production, loading .env file for local development.")
    load_dotenv()

from .config import config_by_name
from .extensions import db, migrate, jwt, limiter

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    
    config_name = os.getenv('FLASK_CONFIG', 'production' if os.getenv('RAILWAY_ENVIRONMENT') == 'production' else 'development')
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions WITH the app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    
    cors_origin = os.getenv('CORS_ORIGIN', "http://localhost:3000")
    CORS(app, resources={r"/api/*": {"origins": cors_origin}})

    # --- IMPORTANT CHANGE ---
    # Import and register blueprints AFTER extensions are initialized
    with app.app_context():
        from .api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')

    return app