"""
ThinkToFit — all page routes.

Every URL the site responds to is defined here as one function.
Routes are grouped by feature with a comment header, in the same order
as the project brief: auth, profile, BMI, exercises, nutrition,
questionnaire, feedback, dashboard, admin, legal pages.
"""
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db
from models import User, UserProfile, FitnessGoal, Exercise, MealPlan, BMIRecord
from models import Questionnaire, QuestionnaireQuestion, QuestionnaireResponse, ResponseAnswer, Feedback
from forms import RegisterForm, LoginForm, ProfileForm, BMIForm, NeedsQuestionnaireForm, FeedbackForm


# =========================================================================
# HOME
# =========================================================================

@app.route('/')
def landing():
    return render_template('landing.html')


# =========================================================================
# AUTHENTICATION
# =========================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'error')
            return render_template('auth/register.html', form=form)

        user = User(name=form.name.data.strip(), email=email)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created. Let's set up your profile.", 'success')
        return redirect(url_for('edit_profile'))

    return render_template('auth/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Welcome back.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))

        flash('Incorrect email or password.', 'error')

    return render_template('auth/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))


# =========================================================================
# PROFILE
# =========================================================================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    form.fitness_goal.choices = [(g.id, g.label) for g in FitnessGoal.query.all()]

    profile = current_user.profile

    if form.validate_on_submit():
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.session.add(profile)

        profile.age = form.age.data
        profile.gender = form.gender.data
        profile.height_cm = form.height_cm.data
        profile.weight_kg = form.weight_kg.data
        profile.fitness_goal_id = form.fitness_goal.data
        profile.experience_level = form.experience_level.data
        db.session.commit()

        flash('Profile saved.', 'success')
        return redirect(url_for('dashboard'))

    if profile and not form.is_submitted():  # pre-fill on GET
        form.age.data = profile.age
        form.gender.data = profile.gender
        form.height_cm.data = profile.height_cm
        form.weight_kg.data = profile.weight_kg
        form.fitness_goal.data = profile.fitness_goal_id
        form.experience_level.data = profile.experience_level

    return render_template('profile.html', form=form)


# =========================================================================
# BMI CALCULATOR
# =========================================================================

def calculate_bmi(weight_kg, height_cm):
    """Adult BMI (18+) and category. Not a diagnosis — see the disclaimer page."""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        category = 'Underweight'
    elif bmi < 25:
        category = 'Healthy weight'
    elif bmi < 30:
        category = 'Overweight'
    else:
        category = 'Obesity'

    return round(bmi, 1), category


@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    form = BMIForm()
    result = None

    if current_user.is_authenticated and current_user.profile and not form.is_submitted():
        form.weight_kg.data = current_user.profile.weight_kg
        form.height_cm.data = current_user.profile.height_cm

    if form.validate_on_submit():
        bmi_value, category = calculate_bmi(form.weight_kg.data, form.height_cm.data)
        result = {'bmi': bmi_value, 'category': category}

        record = BMIRecord(
            user_id=current_user.id if current_user.is_authenticated else None,
            weight_kg=form.weight_kg.data,
            height_cm=form.height_cm.data,
            bmi_value=bmi_value,
            category=category,
        )
        db.session.add(record)
        db.session.commit()

    history = []
    if current_user.is_authenticated:
        history = (
            BMIRecord.query.filter_by(user_id=current_user.id)
            .order_by(BMIRecord.recorded_at.desc())
            .limit(10)
            .all()
        )

    return render_template('bmi.html', form=form, result=result, history=history)


# =========================================================================
# EXERCISES
# =========================================================================

TARGET_AREAS = ['chest', 'back', 'shoulders', 'arms', 'legs', 'core', 'full_body', 'cardio']
EXPERIENCE_ORDER = {'beginner': 0, 'intermediate': 1, 'advanced': 2}


@app.route('/exercises')
def exercises():
    target_area = request.args.get('area')
    goal_key = None
    experience_level = 'beginner'

    if current_user.is_authenticated and current_user.profile:
        experience_level = current_user.profile.experience_level or 'beginner'
        if current_user.profile.fitness_goal:
            goal_key = current_user.profile.fitness_goal.key

    # Simple rule-based filtering: body area, then experience level, then goal —
    # no machine learning needed for this project's scope.
    query = Exercise.query
    if target_area:
        query = query.filter(Exercise.target_area == target_area)
    all_exercises = query.all()

    max_level = EXPERIENCE_ORDER.get(experience_level, 0)
    matched = [e for e in all_exercises if EXPERIENCE_ORDER.get(e.difficulty, 0) <= max_level]

    if goal_key:
        goal_matched = [e for e in matched if goal_key in e.goal_tag_list()]
        if goal_matched:
            matched = goal_matched

    return render_template('exercises.html', exercises=matched[:50], areas=TARGET_AREAS, selected_area=target_area)


# =========================================================================
# NUTRITION
# =========================================================================

@app.route('/weight-loss')
def weight_loss():
    return render_template('nutrition/weight_loss.html')


@app.route('/healthy-eating')
def healthy_eating():
    return render_template('nutrition/healthy_eating.html')


@app.route('/meal-plans')
def meal_plans():
    category = request.args.get('category')
    query = MealPlan.query
    if category:
        query = query.filter_by(goal_category=category)
    plans = query.all()

    return render_template('nutrition/meal_plans.html', plans=plans, selected_category=category)


# =========================================================================
# QUESTIONNAIRE
# =========================================================================

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    form = NeedsQuestionnaireForm()

    if form.validate_on_submit():
        needs_q = Questionnaire.query.filter_by(type='needs').first()

        response = QuestionnaireResponse(
            questionnaire_id=needs_q.id if needs_q else None,
            user_id=current_user.id if current_user.is_authenticated else None,
        )
        db.session.add(response)
        db.session.flush()  # get response.id before adding answers

        # Seeded questions are ordered 1-4 to match these four fields (see seed.py).
        questions = []
        if needs_q:
            questions = (
                QuestionnaireQuestion.query.filter_by(questionnaire_id=needs_q.id)
                .order_by(QuestionnaireQuestion.order)
                .all()
            )
        values = [form.main_goal.data, form.experience.data, form.frequency.data, form.interest.data]

        for question, value in zip(questions, values):
            db.session.add(ResponseAnswer(response_id=response.id, question_id=question.id, answer_value=value))

        db.session.commit()
        flash('Thanks — your answers help us tailor ThinkToFit to you.', 'success')
        return redirect(url_for('dashboard') if current_user.is_authenticated else url_for('landing'))

    return render_template('questionnaire.html', form=form)


# =========================================================================
# FEEDBACK
# =========================================================================

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()

    if form.validate_on_submit():
        entry = Feedback(
            user_id=current_user.id if current_user.is_authenticated else None,
            ease_of_use_rating=int(form.ease_of_use_rating.data),
            design_rating=int(form.design_rating.data),
            usefulness_rating=int(form.usefulness_rating.data),
            comments=form.comments.data,
        )
        db.session.add(entry)
        db.session.commit()

        flash('Thanks for your feedback.', 'success')
        return redirect(url_for('landing'))

    return render_template('feedback.html', form=form)


# =========================================================================
# DASHBOARD (logged-in home page)
# =========================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    latest_bmi = (
        BMIRecord.query.filter_by(user_id=current_user.id)
        .order_by(BMIRecord.recorded_at.desc())
        .first()
    )
    return render_template('dashboard.html', latest_bmi=latest_bmi)


# =========================================================================
# ADMIN / RESEARCH VIEW
# =========================================================================

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)

    from sqlalchemy import func

    total_users = User.query.count()

    goal_counts = (
        db.session.query(FitnessGoal.label, func.count(UserProfile.id))
        .join(UserProfile, UserProfile.fitness_goal_id == FitnessGoal.id)
        .group_by(FitnessGoal.label)
        .all()
    )

    avg_ease = db.session.query(func.avg(Feedback.ease_of_use_rating)).scalar()
    avg_design = db.session.query(func.avg(Feedback.design_rating)).scalar()
    avg_usefulness = db.session.query(func.avg(Feedback.usefulness_rating)).scalar()

    stats = {
        'total_users': total_users,
        'goal_counts': goal_counts,
        'avg_ease': round(avg_ease, 2) if avg_ease else None,
        'avg_design': round(avg_design, 2) if avg_design else None,
        'avg_usefulness': round(avg_usefulness, 2) if avg_usefulness else None,
        'feedback_count': Feedback.query.count(),
    }

    # Aggregated stats only — individual responses are never linked back to a
    # user's identity in this view, to protect participant privacy.
    recent_comments = (
        Feedback.query.filter(Feedback.comments.isnot(None), Feedback.comments != '')
        .order_by(Feedback.submitted_at.desc())
        .limit(20)
        .all()
    )

    return render_template('admin.html', stats=stats, comments=recent_comments)


# =========================================================================
# LEGAL PAGES
# =========================================================================

@app.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')


@app.route('/disclaimer')
def disclaimer():
    return render_template('legal/disclaimer.html')
