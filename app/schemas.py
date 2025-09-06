from marshmallow import Schema, fields, validates, ValidationError

class RegisterSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class ChoiceSchema(Schema):
    id = fields.Int(dump_only=True)
    text = fields.Str(required=True)
    is_correct = fields.Bool(load_default=False)

class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    text = fields.Str(required=True)
    qtype = fields.Str(required=True)
    points = fields.Int(load_default=1)
    choices = fields.List(fields.Nested(ChoiceSchema))

    @validates('qtype')
    def validate_qtype(self, val, **kwargs):
        if val not in ('mcq', 'msq', 'coding'):
            raise ValidationError('qtype must be one of mcq, msq, or coding.')

class QuizSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    is_published = fields.Bool(load_default=False)
    time_limit_minutes = fields.Int(allow_none=True, load_default=None)
    questions = fields.List(fields.Nested(QuestionSchema), required=True)

class QuizAttemptSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    quiz_id = fields.Int(required=True)
    start_time = fields.DateTime(dump_only=True)
    end_time = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    final_score = fields.Float(dump_only=True)