from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
from ...extensions import db
from ...models import Submission, Question, Quiz, QuizAttempt, User
from .. import api_bp
from ...schemas import QuizAttemptSchema, QuizSchema


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
        return float(question.points) if selected_set == correct_set else 0.0
    
    if total_correct == 0:
        # If there are no correct answers, score is full if nothing is selected
        return float(question.points) if len(selected_set) == 0 else 0.0

    # For MSQ, apply partial scoring with a penalty for incorrect selections
    raw_score = (correct_selected / total_correct) - (wrong_selected / total_choices)
    score = max(0.0, raw_score)
    
    return round(score * question.points, 3)

@submission_bp.route('/quizzes/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    """Endpoint for a user to start a quiz attempt."""
    user_id = get_jwt_identity()

    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return jsonify({"msg": "Quiz not found"}), 404

    # Check for ANY existing attempt for this quiz by this user
    existing_attempt = QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if existing_attempt:
        return jsonify({
            'msg': 'You have already attempted this quiz.',
            'attempt_id': existing_attempt.id,
            'status': existing_attempt.status
        }), 409

    new_attempt = QuizAttempt(user_id=user_id, quiz_id=quiz_id)
    db.session.add(new_attempt)
    db.session.commit()

    return jsonify({
        'msg': 'Quiz started successfully.',
        'attempt_id': new_attempt.id,
        'start_time': new_attempt.start_time.isoformat(),
        'time_limit_minutes': quiz.time_limit_minutes
    }), 201

@submission_bp.route('/quizzes/attempts/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_answers(attempt_id):
    """Endpoint for users to submit their answers for a quiz attempt."""
    data = request.get_json()
    user_id = get_jwt_identity() # This is a string, needs to be converted to int for comparison
    answers = data.get('answers', [])

    attempt = db.session.get(QuizAttempt, attempt_id)

    # --- Validation ---
    if not attempt:
        return jsonify({'msg': 'Quiz attempt not found.'}), 404
    if attempt.user_id != int(user_id):
        return jsonify({'msg': 'This is not your quiz attempt.'}), 403
    if attempt.status != 'in-progress':
        return jsonify({'msg': f'This quiz was already submitted or expired.'}), 409

    quiz = db.session.get(Quiz, attempt.quiz_id)
    
    # --- Time Limit Check ---
    if quiz.time_limit_minutes:
        time_limit = timedelta(minutes=quiz.time_limit_minutes)
        elapsed_time = datetime.utcnow() - attempt.start_time
        if elapsed_time > time_limit:
            attempt.status = 'time_expired'
            attempt.final_score = 0
            attempt.end_time = datetime.utcnow()
            db.session.commit()
            return jsonify({'msg': 'Time limit exceeded. Your submission was not graded.'}), 408 # Using 408 Request Timeout

    total_auto_score = 0.0
    has_manual_grading = False
    submissions_created = []

    for ans in answers:
        qid = ans.get('question_id')
        question = db.session.get(Question, qid)
        if not question:
            continue

        submission = Submission(attempt_id=attempt.id, user_id=user_id, quiz_id=quiz.id, question_id=qid)
        
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
            has_manual_grading = True # Flag that this attempt needs manual grading
            
        db.session.add(submission)
        submissions_created.append(submission)

    # Update the attempt record
    attempt.end_time = datetime.utcnow()
    attempt.final_score = total_auto_score
    
    # If there are no coding questions, the attempt is fully graded immediately.
    if not has_manual_grading:
        attempt.status = 'graded'
    else:
        attempt.status = 'submitted' # Otherwise, it's submitted and pending review.
    
    db.session.commit()
    
    return jsonify({
        'msg': 'Submission received successfully.', 
        'final_score': total_auto_score,
        'attempt_id': attempt.id
    }), 201


@submission_bp.route('/submissions/mine', methods=['GET'])
@jwt_required()
def get_my_submissions():
    """Endpoint for users to retrieve their own submission history."""
    user_id = get_jwt_identity()
    attempts = (
        db.session.query(QuizAttempt, Quiz.title)
        .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
        .filter(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.start_time.desc())
        .limit(50)
        .all()
    )
    
    result = []
    for attempt, quiz_title in attempts:
        submissions = Submission.query.filter_by(attempt_id=attempt.id).all()
        submission_details = [{
            'question_id': s.question_id,
            'score': s.score,
            'feedback': s.feedback
        } for s in submissions]

        result.append({
            'attempt_id': attempt.id,
            'quiz_id': attempt.quiz_id,
            'quiz_title': quiz_title, # --- ADDED ---
            'status': attempt.status,
            'final_score': attempt.final_score,
            'start_time': attempt.start_time.isoformat(),
            'end_time': attempt.end_time.isoformat() if attempt.end_time else None,
            'details': submission_details
        })
    
    return jsonify(result)

@submission_bp.route('/quizzes/attempts/<int:attempt_id>', methods=['GET'])
@jwt_required()
def get_attempt(attempt_id):
    """Endpoint for a user to get details of a quiz attempt."""
    user_id = get_jwt_identity()
    attempt = db.session.get(QuizAttempt, attempt_id)

    if not attempt:
        return jsonify({"msg": "Attempt not found"}), 404

    if attempt.user_id != int(user_id):
        return jsonify({"msg": "This is not your quiz attempt"}), 403

    quiz = db.session.get(Quiz, attempt.quiz_id)

    # --- START: Robust Elapsed Time Calculation ---
    elapsed_seconds = 0
    if attempt.start_time:
        # Make the start_time timezone-aware if it's naive (for old records)
        start_time = attempt.start_time
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
            
        elapsed_delta = datetime.now(timezone.utc) - start_time
        elapsed_seconds = int(elapsed_delta.total_seconds())
    # --- END ---

    attempt_schema = QuizAttemptSchema()
    quiz_schema = QuizSchema()

    return jsonify({
        'attempt': attempt_schema.dump(attempt),
        'quiz': quiz_schema.dump(quiz),
        'elapsed_seconds': elapsed_seconds
    })

# Register this blueprint with the main API blueprint
api_bp.register_blueprint(submission_bp)