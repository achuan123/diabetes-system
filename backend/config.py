import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///../database/diabetes.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MEDICAL_ENCRYPTION_KEY = os.getenv('MEDICAL_ENCRYPTION_KEY', '')
