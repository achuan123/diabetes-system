from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from .crypto import decrypt_text, encrypt_text
from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(30), unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bound_patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'doctor_id': self.doctor_id,
            'bound_patient_id': self.bound_patient_id,
        }


class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    record_type = db.Column(db.String(20), nullable=False)  # blood_sugar / oxygen
    value_encrypted = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    measured_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_value(self, app_config, value: str):
        self.value_encrypted = encrypt_text(app_config, value)

    def get_value(self, app_config) -> str:
        return decrypt_text(app_config, self.value_encrypted)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    reminder_type = db.Column(db.String(20), nullable=False)  # medication / diet
    content = db.Column(db.String(255), nullable=False)
    remind_time = db.Column(db.String(20), nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
