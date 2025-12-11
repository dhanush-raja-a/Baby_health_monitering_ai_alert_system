from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    babies = db.relationship('BabyProfile', backref='parent', lazy=True)

class BabyProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    blood_group = db.Column(db.String(10), nullable=True)
    allergies = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logs = db.relationship('HealthLog', backref='baby', lazy=True)

class HealthLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baby_id = db.Column(db.Integer, db.ForeignKey('baby_profile.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Vitals
    temperature = db.Column(db.Float, nullable=False)
    
    # Symptoms (JSON stored as string or separate fields? Keeping it simple with separate fields for now as per requirements, or a text summary)
    # Requirement: Checkbox to Cough, Runny Nose, Vomiting
    has_cough = db.Column(db.Boolean, default=False)
    has_runny_nose = db.Column(db.Boolean, default=False)
    has_vomiting = db.Column(db.Boolean, default=False)
    symptom_severity = db.Column(db.String(50)) # e.g. Mild, Moderate, Severe
    symptom_duration = db.Column(db.String(50)) # e.g. 2 days
    
    # Food/Medicine
    food_intake = db.Column(db.String(255)) # Morning, Eve, Night checkboxes + text
    stool_status = db.Column(db.String(50))
    
    # AI Analysis
    ai_risk_level = db.Column(db.String(50)) # Normal, Monitor Closely, Seek Medical Attention
    ai_analysis_text = db.Column(db.Text)
