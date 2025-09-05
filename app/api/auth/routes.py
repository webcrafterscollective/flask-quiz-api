from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

# Correctly import extensions, models, and schemas from the new structure
from ...extensions import db, limiter
from ...models import User
from ...schemas import RegisterSchema, LoginSchema
# Import the main api_bp to register this blueprint onto it
from .. import api_bp

# Create a blueprint specifically for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    """Registers a new user."""
    data = request.get_json()
    try:
        payload = RegisterSchema().load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    if User.query.filter((User.username == payload['username']) | (User.email == payload['email'])).first():
        return jsonify({'msg': 'Username or email already exists'}), 400

    user = User(username=payload['username'], email=payload['email'])
    user.set_password(payload['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'User registered successfully'}), 201

@auth_bp.route('/auth/login', methods=['POST'])
@limiter.limit("20 per minute")
def login():
    """Logs in a user and returns a JWT."""
    data = request.get_json()
    try:
        payload = LoginSchema().load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    user = User.query.filter_by(username=payload['username']).first()
    if not user or not user.check_password(payload['password']):
        return jsonify({'msg': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token,
        'user': {'id': user.id, 'username': user.username, 'role': user.role}
    })

# This line is crucial: it registers the auth routes with the main API blueprint.
api_bp.register_blueprint(auth_bp)

