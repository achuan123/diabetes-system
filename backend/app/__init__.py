from flask import Flask, jsonify

from config import Config

from .extensions import db, jwt, migrate
from .models import User
from .routes import api


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if not app.config.get('MEDICAL_ENCRYPTION_KEY'):
        raise RuntimeError('MEDICAL_ENCRYPTION_KEY is required for encrypted medical data storage')

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(api)

    @app.get('/health')
    def health():
        return jsonify({'status': 'ok'})

    with app.app_context():
        db.create_all()
        seed_defaults()

    return app


def seed_defaults():
    doctor = User.query.filter_by(email='doctor@123.com').first()
    if not doctor:
        doctor = User(role='doctor', name='默认医生', email='doctor@123.com')
        doctor.set_password('doctor123456')
        db.session.add(doctor)

    admin = User.query.filter_by(email='admin@123').first()
    if not admin:
        admin = User(role='admin', name='系统管理员', email='admin@123')
        admin.set_password('admin123456')
        db.session.add(admin)

    db.session.commit()
