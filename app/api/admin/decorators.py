from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ...extensions import db
from ...models import User

def admin_required(fn):
    """
    A decorator to protect routes that require admin privileges.
    It checks for a valid JWT and ensures the user has the 'admin' role.
    """
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        user = db.session.get(User, identity)
        
        if not user or user.role != 'admin':
            return jsonify({'msg': 'Admin access required'}), 403
            
        return fn(*args, **kwargs)
    return wrapper

