from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum('doctor', 'admin'), nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'other'))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    diabetes_type = db.Column(db.String(50))
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship('User', backref='patients')
    glucose_records = db.relationship(
        'GlucoseRecord', backref='patient', lazy='dynamic',
        order_by='GlucoseRecord.measure_time.desc()'
    )
    exercise_records = db.relationship(
        'ExerciseRecord', backref='patient', lazy='dynamic',
        order_by='ExerciseRecord.record_time.desc()'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


class GlucoseRecord(db.Model):
    __tablename__ = 'glucose_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    measure_time = db.Column(db.DateTime, nullable=False)
    meal_status = db.Column(db.Enum('before_meal', 'after_meal', 'fasting', 'random'))
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ExerciseRecord(db.Model):
    __tablename__ = 'exercise_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    exercise_type = db.Column(db.String(100))
    duration = db.Column(db.Integer)
    calories = db.Column(db.Integer)
    intensity = db.Column(db.Enum('low', 'medium', 'high'))
    record_time = db.Column(db.DateTime, nullable=False)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Reminder(db.Model):
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    level = db.Column(db.Enum('low', 'medium', 'high', 'urgent'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship('User', backref='reminders')
    patient = db.relationship('Patient', backref='reminders')


class Consultation(db.Model):
    __tablename__ = 'consultations'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    sender = db.Column(db.Enum('patient', 'doctor'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='consultations')
    doctor = db.relationship('User', backref='consultations')


class FamilyMember(db.Model):
    __tablename__ = 'family_members'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    relation = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='family_members')
