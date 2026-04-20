from app import create_app
from app.extensions import db
from app.models import User


class TestConfig:
    TESTING = True
    SECRET_KEY = 'test-secret'
    JWT_SECRET_KEY = 'test-jwt'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MEDICAL_ENCRYPTION_KEY = 'BhwDGcyDHdoH0VwXP53dBB_QrmrvF-Gu2bCE1LfhRNM='


def _auth_header(token):
    return {'Authorization': f'Bearer {token}'}


def test_patient_doctor_record_flow():
    app = create_app(TestConfig)
    client = app.test_client()

    doctor_login = client.post('/api/auth/web/login', json={'email': 'doctor@123.com', 'password': 'doctor123456'})
    assert doctor_login.status_code == 200
    doctor_id = doctor_login.get_json()['user']['id']

    patient = client.post('/api/auth/patient/register', json={'name': '张三', 'phone': '13800000000', 'password': '123456', 'doctor_id': doctor_id})
    assert patient.status_code == 200
    patient_data = patient.get_json()
    patient_token = patient_data['token']
    patient_id = patient_data['user']['id']

    add_record = client.post('/api/patient/records', json={'record_type': 'blood_sugar', 'value': '6.2'}, headers=_auth_header(patient_token))
    assert add_record.status_code == 200

    doctor_token = doctor_login.get_json()['token']
    doctor_records = client.get(f'/api/patient/records?patient_id={patient_id}', headers=_auth_header(doctor_token))
    assert doctor_records.status_code == 200
    assert doctor_records.get_json()[0]['value'] == '6.2'


def test_family_bind_and_login():
    app = create_app(TestConfig)
    client = app.test_client()

    doctor = client.post('/api/auth/web/login', json={'email': 'doctor@123.com', 'password': 'doctor123456'}).get_json()['user']
    patient_resp = client.post('/api/auth/patient/register', json={'name': '李四', 'phone': '13900000000', 'password': '123456', 'doctor_id': doctor['id']})
    patient_token = patient_resp.get_json()['token']

    family_bind = client.post('/api/auth/family/register', json={'name': '李四家属', 'phone': '13700000000', 'password': '123456'}, headers=_auth_header(patient_token))
    assert family_bind.status_code == 200

    family_login = client.post('/api/auth/family/login', json={'phone': '13700000000', 'password': '123456'})
    assert family_login.status_code == 200

    family_token = family_login.get_json()['token']
    add_oxygen = client.post('/api/patient/records', json={'record_type': 'oxygen', 'value': '98'}, headers=_auth_header(family_token))
    assert add_oxygen.status_code == 200
