from flask import Blueprint
from . import api_bp

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health():
    return {'status': 'ok'}

api_bp.register_blueprint(health_bp)
