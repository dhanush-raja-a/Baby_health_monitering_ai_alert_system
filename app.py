from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, BabyProfile, HealthLog
import os
from datetime import datetime
from datetime import datetime
from dotenv import load_dotenv
import pytz

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'devbox')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baby_health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Initialized the database.")
@app.template_filter('ist_time')
def ist_time_filter(dt):
    if dt is None:
        return ""
    utc_tz = pytz.timezone('UTC')
    ist_tz = pytz.timezone('Asia/Kolkata')
    # Assuming dt is naive and in UTC as per models.py default
    dt = utc_tz.localize(dt)
    ist_dt = dt.astimezone(ist_tz)
    return ist_dt.strftime('%Y-%m-%d %I:%M %p')

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.password == password: # Plain text as requested
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'warning')
        else:
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect(url_for('dashboard'))
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

def calculate_age(dob):
    today = datetime.now().date()
    # Calculate age in months
    age_months = (today.year - dob.year) * 12 + today.month - dob.month
    if today.day < dob.day:
        age_months -= 1
        
    if age_months < 1:
        age_days = (today - dob).days
        return f"{age_days} days"
    elif age_months < 12:
        return f"{age_months} months"
    else:
        years = age_months // 12
        months = age_months % 12
        if months == 0:
            return f"{years} years"
        return f"{years} years, {months} months"

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Enrich babies with age string for display
    babies_data = []
    for baby in user.babies:
        babies_data.append({
            'obj': baby,
            'age_display': calculate_age(baby.dob)
        })
        
    return render_template('dashboard.html', babies=babies_data)

@app.route('/add_baby', methods=['GET', 'POST'])
def add_baby():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        dob_str = request.form.get('dob')
        blood_group = request.form.get('blood_group')
        allergies = request.form.get('allergies')
        
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            new_baby = BabyProfile(
                name=name,
                dob=dob,
                blood_group=blood_group,
                allergies=allergies,
                user_id=session['user_id']
            )
            db.session.add(new_baby)
            db.session.commit()
            flash('Baby profile added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid Date format', 'danger')
            
    return render_template('add_baby.html')
    return render_template('add_baby.html')

@app.route('/edit_baby/<int:baby_id>', methods=['GET', 'POST'])
def edit_baby(baby_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    baby = BabyProfile.query.get_or_404(baby_id)
    if baby.parent.id != session['user_id']:
        return "Unauthorized", 403
        
    if request.method == 'POST':
        baby.name = request.form.get('name')
        dob_str = request.form.get('dob')
        baby.blood_group = request.form.get('blood_group')
        baby.allergies = request.form.get('allergies')
        
        try:
             baby.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
             db.session.commit()
             flash('Baby profile updated successfully!', 'success')
             return redirect(url_for('profile'))
        except ValueError:
             flash('Invalid Date format', 'danger')
             
    return render_template('edit_baby.html', baby=baby)

from services import analyze_risk, send_alert_email
from datetime import timedelta

@app.route('/enter_log/<int:baby_id>', methods=['GET', 'POST'])
def enter_log(baby_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    baby = BabyProfile.query.get_or_404(baby_id)
    if baby.parent.id != session['user_id']:
        return "Unauthorized", 403
        
    if request.method == 'POST':
        # Deduplication check: Check if a log was added for this baby in the last 30 seconds
        last_log = HealthLog.query.filter_by(baby_id=baby.id).order_by(HealthLog.timestamp.desc()).first()
        if last_log and (datetime.utcnow() - last_log.timestamp) < timedelta(seconds=30):
             flash('Log already saved recently. Preventing duplicate entry.', 'warning')
             return redirect(url_for('view_logs', baby_id=baby.id))

        try:
            temp = float(request.form.get('temperature'))
        except ValueError:
            flash("Invalid Temperature", 'danger')
            return redirect(request.url)

        has_cough = 'has_cough' in request.form
        has_runny = 'has_runny_nose' in request.form
        has_vomit = 'has_vomiting' in request.form
        severity = request.form.get('symptom_severity')
        duration = request.form.get('symptom_duration')
        
        # Build symptoms string for AI
        symptoms_list = []
        if has_cough: symptoms_list.append("Cough")
        if has_runny: symptoms_list.append("Runny Nose")
        if has_vomit: symptoms_list.append("Vomiting")
        symptoms_str = ", ".join(symptoms_list) if symptoms_list else "None"
        
        food = []
        if 'food_mrg' in request.form: food.append("Morning")
        if 'food_eve' in request.form: food.append("Evening")
        if 'food_night' in request.form: food.append("Night")
        food_details = request.form.get('food_details')
        food_str = ", ".join(food) + f" ({food_details})" if food_details else ", ".join(food)
        
        stool = request.form.get('stool_status')
        
        # Prepare data for AI
        ai_data = {
            'age': calculate_age(baby.dob),
            'temperature': temp,
            'symptoms': symptoms_str,
            'severity': severity,
            'duration': duration,
            'stool': stool
        }
        
        # Call AI Service
        risk, advice = analyze_risk(ai_data)
        
        # Save to DB
        log = HealthLog(
            baby_id=baby.id,
            temperature=temp,
            has_cough=has_cough,
            has_runny_nose=has_runny,
            has_vomiting=has_vomit,
            symptom_severity=severity,
            symptom_duration=duration,
            food_intake=food_str,
            stool_status=stool,
            ai_risk_level=risk,
            ai_analysis_text=advice
        )
        db.session.add(log)
        db.session.commit()
        
        # Send Email Alert
        send_alert_email(baby.parent.email, baby.name, risk, ai_data)
        
        flash(f'Log saved. Risk Assessment: {risk}', 'success' if risk == 'Normal' else 'warning')
        return redirect(url_for('view_logs', baby_id=baby.id))
        
    return render_template('enter_log.html', baby=baby)

@app.route('/view_logs/<int:baby_id>')
def view_logs(baby_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    baby = BabyProfile.query.get_or_404(baby_id)
    if baby.parent.id != session['user_id']:
        return "Unauthorized", 403
        
    logs = HealthLog.query.filter_by(baby_id=baby_id).order_by(HealthLog.timestamp.desc()).all()
    return render_template('view_logs.html', baby=baby, logs=logs)

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Prepare data structure for the frontend
    analytics_data = []
    
    for baby in user.babies:
        baby_stats = {
            'id': baby.id,
            'name': baby.name,
            'total_logs': len(baby.logs),
            'risk_counts': {'Normal': 0, 'Monitor Closely': 0, 'Seek Medical Attention': 0},
            'symptom_counts': {'Cough': 0, 'Runny Nose': 0, 'Vomiting': 0},
            'dates': [],
            'temps': []
        }
        
        # Process logs in chronological order for the graph
        sorted_logs = sorted(baby.logs, key=lambda x: x.timestamp)
        for log in sorted_logs:
            # Stats
            if log.ai_risk_level in baby_stats['risk_counts']:
                baby_stats['risk_counts'][log.ai_risk_level] += 1
            if log.has_cough: baby_stats['symptom_counts']['Cough'] += 1
            if log.has_runny_nose: baby_stats['symptom_counts']['Runny Nose'] += 1
            if log.has_vomiting: baby_stats['symptom_counts']['Vomiting'] += 1
            
            # Graph Data
            baby_stats['dates'].append(log.timestamp.strftime('%Y-%m-%d %H:%M'))
            baby_stats['temps'].append(log.temperature)
            
        analytics_data.append(baby_stats)
            
    return render_template('analytics.html', analytics_data=analytics_data)

@app.route('/wheezing')
def wheezing():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('wheezing.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/select_log_baby')
def select_log_baby():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('select_baby_logs.html', babies=user.babies)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
