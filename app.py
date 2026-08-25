"""
ThinkToFit — main application file.

This creates the Flask app, connects the database, and sets up login.
Everything else (database tables, forms, and page routes) lives in
models.py, forms.py, and routes.py, and gets wired in below.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file, if present

app = Flask(__name__)

# --- Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///thinktofit.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Tests set this to 'False' so submitting forms in tests doesn't need a CSRF token.
app.config['WTF_CSRF_ENABLED'] = os.environ.get('WTF_CSRF_ENABLED', 'True') == 'True'

# --- Extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Import models AFTER `db` exists, so SQLAlchemy can register their tables.
from models import User, UserProfile, FitnessGoal, Exercise, MealPlan, Meal, BMIRecord  # noqa: E402
from models import Questionnaire, QuestionnaireQuestion, QuestionnaireResponse, ResponseAnswer, Feedback  # noqa: E402


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Import routes AFTER models, so every @app.route in routes.py can use them.
import routes  # noqa: E402,F401

# Create tables and add starter data (exercises, meal plans, goals, questionnaire,
# and a default admin account) automatically. Safe to run every time — it checks
# whether data already exists before inserting anything.
with app.app_context():
    db.create_all()
    from seed import seed_data, create_admin_if_missing
    seed_data()
    create_admin_if_missing()


if __name__ == '__main__':
    app.run(debug=True)
