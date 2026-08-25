from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, IntegerField, FloatField,
    SelectField, TextAreaField, SubmitField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(check_deliverability=False)])
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters.')],
    )
    confirm_password = PasswordField(
        'Confirm password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')],
    )
    submit = SubmitField('Create account')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(check_deliverability=False)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class ProfileForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=13, max=120)])
    gender = SelectField(
        'Gender',
        choices=[
            ('female', 'Female'), ('male', 'Male'),
            ('other', 'Other'), ('prefer_not_to_say', 'Prefer not to say'),
        ],
    )
    height_cm = FloatField('Height (cm)', validators=[DataRequired(), NumberRange(min=100, max=250)])
    weight_kg = FloatField('Weight (kg)', validators=[DataRequired(), NumberRange(min=20, max=300)])
    fitness_goal = SelectField('Fitness goal', coerce=int)
    experience_level = SelectField(
        'Experience level',
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
    )
    submit = SubmitField('Save profile')


class BMIForm(FlaskForm):
    weight_kg = FloatField('Weight (kg)', validators=[DataRequired(), NumberRange(min=20, max=300)])
    height_cm = FloatField('Height (cm)', validators=[DataRequired(), NumberRange(min=100, max=250)])
    submit = SubmitField('Calculate BMI')


class FeedbackForm(FlaskForm):
    rating_choices = [(str(i), str(i)) for i in range(1, 6)]

    ease_of_use_rating = SelectField(
        'How easy was ThinkToFit to use? (1 = very difficult, 5 = very easy)',
        choices=rating_choices, validators=[DataRequired()],
    )
    design_rating = SelectField(
        'How would you rate the website design? (1 = poor, 5 = excellent)',
        choices=rating_choices, validators=[DataRequired()],
    )
    usefulness_rating = SelectField(
        'How useful did you find ThinkToFit overall? (1 = not useful, 5 = very useful)',
        choices=rating_choices, validators=[DataRequired()],
    )
    comments = TextAreaField(
        'What improvements would you recommend? (optional)',
        validators=[Optional(), Length(max=1000)],
    )
    submit = SubmitField('Submit feedback')


class NeedsQuestionnaireForm(FlaskForm):
    main_goal = SelectField(
        'What is your main fitness goal?',
        choices=[
            ('lose_weight', 'Lose weight'), ('build_muscle', 'Build muscle'),
            ('maintain_weight', 'Maintain weight'), ('improve_fitness', 'Improve fitness'),
            ('improve_strength', 'Improve strength'), ('be_more_active', 'Become more active'),
            ('other', 'Other'),
        ],
        validators=[DataRequired()],
    )
    experience = SelectField(
        'How would you describe your fitness experience?',
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        validators=[DataRequired()],
    )
    frequency = SelectField(
        'How often do you currently exercise?',
        choices=[
            ('never', 'Never'), ('1_2', '1–2 days per week'),
            ('3_4', '3–4 days per week'), ('5_plus', '5+ days per week'),
        ],
        validators=[DataRequired()],
    )
    interest = SelectField(
        'What type of fitness information are you most interested in?',
        choices=[
            ('weight_loss', 'Weight loss'), ('exercise', 'Exercise'), ('muscle_building', 'Muscle building'),
            ('healthy_eating', 'Healthy eating'), ('meal_planning', 'Meal planning'),
            ('bmi', 'BMI'), ('general_fitness', 'General fitness'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('Submit')
