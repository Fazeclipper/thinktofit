"""
ThinkToFit — database models.

Each class here is one database table. Flask-SQLAlchemy turns these
into real tables automatically when app.py calls db.create_all().
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    bmi_records = db.relationship('BMIRecord', backref='user', cascade='all, delete-orphan')
    questionnaire_responses = db.relationship('QuestionnaireResponse', backref='user', cascade='all, delete-orphan')
    feedback_entries = db.relationship('Feedback', backref='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class FitnessGoal(db.Model):
    __tablename__ = 'fitness_goals'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)   # e.g. 'weight_loss'
    label = db.Column(db.String(100), nullable=False)             # e.g. 'Lose weight'


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(30))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    fitness_goal_id = db.Column(db.Integer, db.ForeignKey('fitness_goals.id'))
    experience_level = db.Column(db.String(20))  # beginner | intermediate | advanced
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    fitness_goal = db.relationship('FitnessGoal')


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    target_area = db.Column(db.String(50), nullable=False)   # chest, back, legs, core, cardio...
    difficulty = db.Column(db.String(20), nullable=False)    # beginner, intermediate, advanced
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)   # newline-separated steps
    sets = db.Column(db.String(20))
    reps = db.Column(db.String(20))
    rest_seconds = db.Column(db.Integer)
    # Comma-separated goal keys, e.g. "weight_loss,general_fitness" — simplified
    # from a full join table, which would be overkill for this project's scope.
    goal_tags = db.Column(db.String(200))

    def instructions_list(self):
        return [line.strip() for line in (self.instructions or '').split('\n') if line.strip()]

    def goal_tag_list(self):
        return [t.strip() for t in (self.goal_tags or '').split(',') if t.strip()]


class MealPlan(db.Model):
    __tablename__ = 'meal_plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    goal_category = db.Column(db.String(50), nullable=False)  # weight_management, general_fitness, muscle_building

    meals = db.relationship('Meal', backref='meal_plan', cascade='all, delete-orphan')


class Meal(db.Model):
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plans.id'), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, snack, dinner
    description = db.Column(db.String(255), nullable=False)


class BMIRecord(db.Model):
    __tablename__ = 'bmi_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # nullable: guests can calculate without saving
    weight_kg = db.Column(db.Float, nullable=False)
    height_cm = db.Column(db.Float, nullable=False)
    bmi_value = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(30), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Questionnaire(db.Model):
    __tablename__ = 'questionnaires'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'needs' | 'feedback'

    questions = db.relationship('QuestionnaireQuestion', backref='questionnaire', cascade='all, delete-orphan')


class QuestionnaireQuestion(db.Model):
    __tablename__ = 'questionnaire_questions'

    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), nullable=False)
    prompt = db.Column(db.String(255), nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # multiple_choice, likert, yes_no, text
    order = db.Column(db.Integer, default=0)


class QuestionnaireResponse(db.Model):
    __tablename__ = 'questionnaire_responses'

    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # nullable: anonymous allowed
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('ResponseAnswer', backref='response', cascade='all, delete-orphan')


class ResponseAnswer(db.Model):
    __tablename__ = 'response_answers'

    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('questionnaire_responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questionnaire_questions.id'), nullable=True)
    answer_value = db.Column(db.String(255))


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # nullable: anonymous feedback allowed
    ease_of_use_rating = db.Column(db.Integer, nullable=False)
    design_rating = db.Column(db.Integer, nullable=False)
    usefulness_rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
