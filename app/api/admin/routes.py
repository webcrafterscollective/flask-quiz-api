from flask import Blueprint, request, jsonify
from datetime import datetime

from ...extensions import db
from ...models import Submission
from .. import api_bp
from .decorators import admin_required

# Create a blueprint for admin-only routes
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/pending_coding', methods=['GET'])
@admin_required
def get_pending_coding_submissions():
    """Admin endpoint to get all ungraded coding submissions."""
    submissions = (
        Submission.query
        .filter_by(graded=False)
        .filter(Submission.code.isnot(None))
        .order_by(Submission.submitted_at.asc())
        .all()
    )
    
    result = [{
        'id': s.id,
        'user_id': s.user_id,
        'quiz_id': s.quiz_id,
        'question_id': s.question_id,
        'code_preview': (s.code[:400] + '...') if s.code and len(s.code) > 400 else s.code,
        'language': s.language,
        'submitted_at': s.submitted_at.isoformat()
    } for s in submissions]
    
    return jsonify(result)

@admin_bp.route('/admin/grade/<int:submission_id>', methods=['POST'])
@admin_required
def grade_submission(submission_id):
    """Admin endpoint to grade a specific submission."""
    data = request.get_json()
    score = data.get('score')
    feedback = data.get('feedback', '')

    if score is None:
        return jsonify({'msg': 'Score is required'}), 400

    submission = db.session.get(Submission, submission_id)
    if not submission:
        return jsonify({'msg': 'Submission not found'}), 404

    submission.score = float(score)
    submission.feedback = feedback
    submission.graded = True
    submission.graded_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'msg': 'Submission graded successfully'})

# Register this blueprint with the main API blueprint
api_bp.register_blueprint(admin_bp)

