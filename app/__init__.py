import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# --- Start of new logic ---
# Only load the .env file if the app is NOT running in a production environment.
# Railway sets a 'RAILWAY_ENVIRONMENT' variable to 'production' automatically.
if os.getenv('RAILWAY_ENVIRONMENT') != 'production':
    print("Not in Railway production, loading .env file for local development.")
    load_dotenv()
# --- End of new logic ---

from .config import config_by_name
from .extensions import db, migrate, jwt, limiter

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    
    # Use 'production' as the default config on Railway, otherwise 'development'
    config_name = os.getenv('FLASK_CONFIG', 'production' if os.getenv('RAILWAY_ENVIRONMENT') == 'production' else 'development')
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Enable CORS for frontend - get origin from environment variable
    cors_origin = os.getenv('CORS_ORIGIN', "http://localhost:3000")
    CORS(app, resources={r"/api/*": {"origins": cors_origin}})

    # Import and register the main API blueprint
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app