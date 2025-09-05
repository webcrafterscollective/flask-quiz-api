from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Correctly import from the new structure
from ...extensions import db
from ...models import Quiz, Question, Choice, User
from ...schemas import QuizSchema
from .. import api_bp
from ..admin.decorators import admin_required

# Create a blueprint for quiz-related routes
quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quizzes', methods=['POST'])
@admin_required
def create_quiz():
    """Admin endpoint to create a new quiz."""
    data = request.get_json()
    try:
        payload = QuizSchema().load(data)
    except Exception as err:
        return jsonify({'errors': str(err)}), 400

    quiz = Quiz(
        title=payload['title'],
        description=payload.get('description'),
        is_published=payload.get('is_published', False)
    )

    for q_data in payload.get('questions', []):
        question = Question(
            text=q_data['text'],
            qtype=q_data['qtype'],
            points=q_data.get('points', 1)
        )
        if q_data['qtype'] != 'coding':
            for c_data in q_data.get('choices', []):
                choice = Choice(
                    text=c_data['text'],
                    is_correct=c_data.get('is_correct', False)
                )
                question.choices.append(choice)
        quiz.questions.append(question)

    db.session.add(quiz)
    db.session.commit()
    return jsonify({'msg': 'Quiz created successfully', 'quiz_id': quiz.id}), 201

@quiz_bp.route('/quizzes', methods=['GET'])
@jwt_required(optional=True)
def list_quizzes():
    """
    Lists quizzes. Admins see all, others see only published quizzes.
    If no token is provided, it lists only published quizzes.
    """
    identity = get_jwt_identity()
    user = db.session.get(User, identity) if identity else None

    if user and user.role == 'admin':
        quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    else:
        quizzes = Quiz.query.filter_by(is_published=True).order_by(Quiz.created_at.desc()).all()

    schema = QuizSchema(many=True)
    return jsonify(schema.dump(quizzes))

@quiz_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    """Gets a single quiz by its ID. Requires authentication."""
    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return jsonify({"msg": "Quiz not found"}), 404
        
    identity = get_jwt_identity()
    user = db.session.get(User, identity)

    # Hide the 'is_correct' flag for non-admin users
    schema = QuizSchema()
    data = schema.dump(quiz)
    if not user or user.role != 'admin':
        for q in data.get('questions', []):
            if 'choices' in q:
                for c in q.get('choices', []):
                    c.pop('is_correct', None)
    return jsonify(data)

# Register this blueprint with the main API blueprint
api_bp.register_blueprint(quiz_bp)

