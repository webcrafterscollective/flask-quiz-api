from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

# Correctly import from the new structure
from ...extensions import db
from ...models import Submission, Question
from .. import api_bp

# Create a blueprint for submission-related routes
submission_bp = Blueprint('submission', __name__)

def grade_question_auto(question: Question, selected_choice_ids):
    """
    Automatically grades a multiple-choice or multiple-select question.
    """
    if question.qtype not in ('mcq', 'msq'):
        return 0.0
    
    correct_choices = [c.id for c in question.choices if c.is_correct]
    all_choice_ids = [c.id for c in question.choices]
    
    # Ensure selected_choice_ids is a list of integers if provided
    try:
        selected_ids = [int(i) for i in selected_choice_ids] if selected_choice_ids else []
    except (ValueError, TypeError):
        selected_ids = []

    selected_set = set(selected_ids)
    correct_set = set(correct_choices)

    correct_selected = len(selected_set & correct_set)
    wrong_selected = len(selected_set - correct_set)
    total_correct = len(correct_set)
    total_choices = len(all_choice_ids) if all_choice_ids else 1

    if question.qtype == 'mcq':
        # For MCQ, score is all or nothing
        return float(question.points) if selected_set == correct_set and len(selected_set) == 1 else 0.0
    
    if total_correct == 0:
        # If there are no correct answers, score is full if nothing is selected
        return float(question.points) if len(selected_set) == 0 else 0.0

    # For MSQ, apply partial scoring with a penalty for incorrect selections
    raw_score = (correct_selected / total_correct) - (wrong_selected / total_choices)
    score = max(0.0, raw_score)
    
    return round(score * question.points, 3)

@submission_bp.route('/submissions/submit', methods=['POST'])
@jwt_required()
def submit_answers():
    """Endpoint for users to submit their answers for a quiz."""
    data = request.get_json()
    user_id = get_jwt_identity()
    quiz_id = data.get('quiz_id')
    answers = data.get('answers', [])

    if not isinstance(answers, list) or not quiz_id:
        return jsonify({'msg': 'quiz_id and answers are required'}), 400

    total_auto_score = 0.0
    submissions_created = []
    for ans in answers:
        qid = ans.get('question_id')
        question = db.session.get(Question, qid)
        if not question:
            continue

        submission = Submission(user_id=user_id, quiz_id=quiz_id, question_id=qid)
        
        if question.qtype in ('mcq', 'msq'):
            selected = ans.get('selected_choice_ids', [])
            submission.selected_choice_ids = ','.join(map(str, selected)) if selected else None
            score = grade_question_auto(question, selected)
            submission.score = score
            submission.graded = True
            submission.graded_at = datetime.utcnow()
            total_auto_score += score
        else: # 'coding' type
            submission.code = ans.get('code')
            submission.language = ans.get('language', 'python')
            submission.graded = False
            submission.score = None
            
        db.session.add(submission)
        submissions_created.append(submission)

    db.session.commit()
    return jsonify({
        'msg': 'Submission received successfully.', 
        'total_auto_score': total_auto_score, 
        'submission_count': len(submissions_created)
    }), 201

@submission_bp.route('/submissions/mine', methods=['GET'])
@jwt_required()
def get_my_submissions():
    """Endpoint for users to retrieve their own submission history."""
    user_id = get_jwt_identity()
    submissions = Submission.query.filter_by(user_id=user_id).order_by(Submission.submitted_at.desc()).limit(100).all()
    
    result = [{
        'id': s.id,
        'quiz_id': s.quiz_id,
        'question_id': s.question_id,
        'score': s.score,
        'graded': s.graded,
        'feedback': s.feedback,
        'submitted_at': s.submitted_at.isoformat()
    } for s in submissions]
    
    return jsonify(result)

# Register this blueprint with the main API blueprint
api_bp.register_blueprint(submission_bp)

