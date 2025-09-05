from flask import Blueprint

# This is the main blueprint for the entire API.
# All other route blueprints will be registered on this one,
# which is then registered on the Flask app instance in the factory.
api_bp = Blueprint('api', __name__)

# Import the route modules here.
# The act of importing them executes the code within, including
# the `api_bp.register_blueprint(...)` calls in each routes file.
# This is the standard way to organize routes in a blueprint-based Flask app.
from . import health
from .auth import routes as auth_routes
from .quiz import routes as quiz_routes
from .submission import routes as submission_routes
from .admin import routes as admin_routes