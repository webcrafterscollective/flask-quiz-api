import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env file only for local development
if os.getenv('RAILWAY_ENVIRONMENT') != 'production':
    print("Not in Railway production, loading .env file for local development.")
    load_dotenv()

from .config import config_by_name
from .extensions import db, migrate, jwt, limiter

def create_app():
    """Application factory function."""
    app = Flask(__name__)

    # Set config based on environment
    config_name = 'production' if os.getenv('RAILWAY_ENVIRONMENT') == 'production' else 'development'
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    # Setup CORS
    cors_origin = os.getenv('CORS_ORIGIN', "http://localhost:3000")
    CORS(app, resources={r"/api/*": {"origins": cors_origin}})

    # Import and register blueprints inside a context
    with app.app_context():
        from .api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')

    return app