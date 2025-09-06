from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from .extensions import db
from passlib.hash import pbkdf2_sha256

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    submissions = db.relationship('Submission', backref='user', lazy=True)

    def set_password(self, password: str):
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password, self.password_hash)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_published = db.Column(db.Boolean, default=False)
    time_limit_minutes = db.Column(db.Integer, nullable=True) # In minutes
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    qtype = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, default=1, nullable=False)
    choices = db.relationship('Choice', backref='question', lazy=True, cascade='all, delete-orphan')

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='in-progress', nullable=False) # e.g., 'in-progress', 'submitted', 'time_expired'
    final_score = db.Column(db.Float, nullable=True)
    
    # A user can only have one 'in-progress' attempt for any given quiz
    __table_args__ = (
        UniqueConstraint('user_id', 'quiz_id', name='_user_quiz_uc'),
    )


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=True)
    selected_choice_ids = db.Column(db.String(200), nullable=True)
    code = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(50), nullable=True)
    score = db.Column(db.Float, nullable=True)
    graded = db.Column(db.Boolean, default=False)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    graded_at = db.Column(db.DateTime, nullable=True)