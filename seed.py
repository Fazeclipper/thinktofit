"""Baseline data: fitness goals, exercises, meal plans, the needs
questionnaire, and a default admin account. Idempotent — safe to run
more than once.
"""
from app import db
from models import FitnessGoal, Exercise, MealPlan, Meal, Questionnaire, QuestionnaireQuestion, User


def seed_data():
    if FitnessGoal.query.count() == 0:
        db.session.add_all([
            FitnessGoal(key='weight_loss', label='Lose weight'),
            FitnessGoal(key='muscle_building', label='Build muscle'),
            FitnessGoal(key='maintain', label='Maintain weight'),
            FitnessGoal(key='general_fitness', label='Improve fitness'),
        ])

    if Exercise.query.count() == 0:
        db.session.add_all([
            Exercise(
                name='Bodyweight Squat', target_area='legs', difficulty='beginner',
                description='A foundational lower-body movement using just body weight.',
                instructions=(
                    'Stand with feet approximately shoulder-width apart.\n'
                    'Lower your body in a controlled movement, as if sitting into a chair.\n'
                    'Keep your chest up and knees tracking over your toes.\n'
                    'Return to the starting position.'
                ),
                sets='3', reps='10-15', rest_seconds=60, goal_tags='weight_loss,general_fitness',
            ),
            Exercise(
                name='Push-Up', target_area='chest', difficulty='beginner',
                description='Classic bodyweight chest and shoulder exercise.',
                instructions=(
                    'Start in a plank position with hands under shoulders.\n'
                    'Lower your chest toward the floor with control.\n'
                    'Keep your body in a straight line from head to heels.\n'
                    'Push back up to the start.'
                ),
                sets='3', reps='8-12', rest_seconds=60, goal_tags='muscle_building,general_fitness',
            ),
            Exercise(
                name='Dumbbell Row', target_area='back', difficulty='intermediate',
                description='Builds back strength using a dumbbell and a bench or stable surface.',
                instructions=(
                    'Place one knee and hand on a bench for support.\n'
                    'Hold a dumbbell in your free hand, arm extended.\n'
                    'Pull the dumbbell toward your hip, squeezing your shoulder blade.\n'
                    'Lower with control.'
                ),
                sets='3', reps='10-12', rest_seconds=60, goal_tags='muscle_building',
            ),
            Exercise(
                name='Plank', target_area='core', difficulty='beginner',
                description='An isometric core-stability exercise.',
                instructions=(
                    'Rest on your forearms and toes, body in a straight line.\n'
                    'Engage your core and avoid letting your hips sag.\n'
                    'Hold for the set time, breathing steadily.'
                ),
                sets='3', reps='20-40 sec hold', rest_seconds=45, goal_tags='general_fitness,weight_loss',
            ),
            Exercise(
                name='Walking', target_area='cardio', difficulty='beginner',
                description='Low-impact cardio suitable for all fitness levels.',
                instructions=(
                    'Walk at a brisk pace where you can still hold a conversation.\n'
                    'Aim for a steady, sustainable effort.'
                ),
                sets='1', reps='20-30 min', rest_seconds=0, goal_tags='weight_loss,general_fitness',
            ),
            Exercise(
                name='Bodyweight Lunge', target_area='legs', difficulty='beginner',
                description='Single-leg movement that builds lower-body strength and balance.',
                instructions=(
                    'Step forward with one leg and lower your hips until both knees are bent around 90 degrees.\n'
                    'Push back to the starting position.\n'
                    'Alternate legs.'
                ),
                sets='3', reps='10-12 per leg', rest_seconds=60, goal_tags='weight_loss,general_fitness',
            ),
            Exercise(
                name='Dumbbell Shoulder Press', target_area='shoulders', difficulty='intermediate',
                description='Builds shoulder strength using dumbbells.',
                instructions=(
                    'Hold a dumbbell in each hand at shoulder height.\n'
                    'Press overhead until arms are extended.\n'
                    'Lower with control back to shoulder height.'
                ),
                sets='3', reps='8-10', rest_seconds=60, goal_tags='muscle_building',
            ),
            Exercise(
                name='Bicycle Crunch', target_area='core', difficulty='intermediate',
                description='A rotational core exercise targeting the obliques.',
                instructions=(
                    'Lie on your back with hands lightly behind your head.\n'
                    'Bring opposite elbow to opposite knee in a pedaling motion.\n'
                    'Keep the movement controlled, not rushed.'
                ),
                sets='3', reps='15-20 per side', rest_seconds=45, goal_tags='general_fitness',
            ),
        ])

    if MealPlan.query.count() == 0:
        wl = MealPlan(name='Weight Management Plan', goal_category='weight_management')
        gf = MealPlan(name='General Fitness Plan', goal_category='general_fitness')
        mb = MealPlan(name='Muscle-Building Support Plan', goal_category='muscle_building')
        db.session.add_all([wl, gf, mb])
        db.session.flush()

        db.session.add_all([
            Meal(meal_plan_id=wl.id, meal_type='breakfast', description='Eggs, whole-grain toast, and fruit'),
            Meal(meal_plan_id=wl.id, meal_type='lunch', description='Grilled chicken, rice, and vegetables'),
            Meal(meal_plan_id=wl.id, meal_type='snack', description='Yogurt and fruit'),
            Meal(meal_plan_id=wl.id, meal_type='dinner', description='Fish, potatoes, and vegetables'),

            Meal(meal_plan_id=gf.id, meal_type='breakfast', description='Oats with fruit and nuts'),
            Meal(meal_plan_id=gf.id, meal_type='lunch', description='Turkey wrap with salad'),
            Meal(meal_plan_id=gf.id, meal_type='snack', description='Handful of nuts'),
            Meal(meal_plan_id=gf.id, meal_type='dinner', description='Chicken, quinoa, and roasted vegetables'),

            Meal(meal_plan_id=mb.id, meal_type='breakfast', description='Eggs, oats, and a banana'),
            Meal(meal_plan_id=mb.id, meal_type='lunch', description='Beef or beans, rice, and vegetables'),
            Meal(meal_plan_id=mb.id, meal_type='snack', description='Cottage cheese and fruit'),
            Meal(meal_plan_id=mb.id, meal_type='dinner', description='Salmon, sweet potato, and greens'),
        ])

    if Questionnaire.query.filter_by(type='needs').count() == 0:
        needs_q = Questionnaire(title='Fitness Needs Questionnaire', type='needs')
        db.session.add(needs_q)
        db.session.flush()

        db.session.add_all([
            QuestionnaireQuestion(questionnaire_id=needs_q.id, prompt='What is your main fitness goal?', question_type='multiple_choice', order=1),
            QuestionnaireQuestion(questionnaire_id=needs_q.id, prompt='How would you describe your fitness experience?', question_type='multiple_choice', order=2),
            QuestionnaireQuestion(questionnaire_id=needs_q.id, prompt='How often do you currently exercise?', question_type='multiple_choice', order=3),
            QuestionnaireQuestion(questionnaire_id=needs_q.id, prompt='What type of fitness information are you most interested in?', question_type='multiple_choice', order=4),
        ])

    db.session.commit()


def create_admin_if_missing(email='admin@thinktofit.example', password='ChangeMe123!'):
    if not User.query.filter_by(email=email).first():
        admin = User(name='Admin', email=email, is_admin=True)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
