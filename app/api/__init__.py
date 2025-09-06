# app/api/__init__.py

from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import health
from .auth import routes as auth_routes
from .quiz import routes as quiz_routes
from .submission import routes as submission_routes
from .admin import routes as admin_routes