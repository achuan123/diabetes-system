from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required

from .extensions import db
from .models import HealthRecord, Message, Reminder, User

api = Blueprint('api', __name__, url_prefix='/api')


def _token(user: User):
    claims = {'role': user.role}
    return create_access_token(identity=str(user.id), additional_claims=claims)


def _current_user():
    return db.session.get(User, int(get_jwt_identity()))


def _allowed_patient_id(user: User):
    if user.role == 'patient':
        return user.id
    if user.role == 'family':
        return user.bound_patient_id
    return None


@api.post('/auth/web/register')
def web_register():
    data = request.get_json() or {}
    role = data.get('role')
    if role not in {'doctor', 'admin'}:
        return jsonify({'error': 'role must be doctor/admin'}), 400
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'email/password required'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'email exists'}), 409
    user = User(role=role, name=data.get('name', role), email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'token': _token(user), 'user': user.to_dict()})


@api.post('/auth/web/login')
def web_login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or user.role not in {'doctor', 'admin'} or not user.check_password(data.get('password', '')):
        return jsonify({'error': 'invalid credentials'}), 401
    return jsonify({'token': _token(user), 'user': user.to_dict()})


@api.get('/doctors')
def list_doctors_public():
    doctors = User.query.filter_by(role='doctor').all()
    return jsonify([{'id': d.id, 'name': d.name, 'email': d.email} for d in doctors])


@api.post('/auth/patient/register')
def patient_register():
    data = request.get_json() or {}
    if not data.get('phone') or not data.get('password'):
        return jsonify({'error': 'phone/password required'}), 400
    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({'error': 'phone exists'}), 409
    doctor = db.session.get(User, data.get('doctor_id')) if data.get('doctor_id') else None
    if data.get('doctor_id') and (not doctor or doctor.role != 'doctor'):
        return jsonify({'error': 'doctor invalid'}), 400
    user = User(role='patient', name=data.get('name', '患者'), phone=data['phone'], doctor_id=data.get('doctor_id'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'token': _token(user), 'user': user.to_dict()})


@api.post('/auth/patient/login')
def patient_login():
    data = request.get_json() or {}
    user = User.query.filter_by(phone=data.get('phone')).first()
    if not user or user.role != 'patient' or not user.check_password(data.get('password', '')):
        return jsonify({'error': 'invalid credentials'}), 401
    return jsonify({'token': _token(user), 'user': user.to_dict()})


@api.post('/auth/family/register')
@jwt_required()
def family_register():
    me = _current_user()
    if me.role != 'patient':
        return jsonify({'error': 'only patient can bind family'}), 403
    data = request.get_json() or {}
    if not data.get('phone') or not data.get('password'):
        return jsonify({'error': 'phone/password required'}), 400
    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({'error': 'phone exists'}), 409
    family = User(role='family', name=data.get('name', '家属'), phone=data['phone'], bound_patient_id=me.id)
    family.set_password(data['password'])
    db.session.add(family)
    db.session.commit()
    return jsonify({'user': family.to_dict()})


@api.post('/auth/family/login')
def family_login():
    data = request.get_json() or {}
    user = User.query.filter_by(phone=data.get('phone')).first()
    if not user or user.role != 'family' or not user.check_password(data.get('password', '')):
        return jsonify({'error': 'invalid credentials'}), 401
    return jsonify({'token': _token(user), 'user': user.to_dict()})


@api.post('/patient/records')
@jwt_required()
def create_record():
    me = _current_user()
    patient_id = _allowed_patient_id(me)
    if not patient_id:
        return jsonify({'error': 'patient/family only'}), 403
    data = request.get_json() or {}
    if data.get('record_type') not in {'blood_sugar', 'oxygen'}:
        return jsonify({'error': 'record_type invalid'}), 400
    if not data.get('value'):
        return jsonify({'error': 'value required'}), 400
    unit = 'mmol/L' if data['record_type'] == 'blood_sugar' else '%'
    record = HealthRecord(patient_id=patient_id, record_type=data['record_type'], unit=unit)
    record.set_value(current_app.config, str(data['value']))
    db.session.add(record)
    db.session.commit()
    return jsonify({'id': record.id})


@api.get('/patient/records')
@jwt_required()
def list_records():
    me = _current_user()
    role = get_jwt().get('role')
    patient_id = request.args.get('patient_id', type=int)
    if role in {'patient', 'family'}:
        patient_id = _allowed_patient_id(me)
    elif role == 'doctor':
        if not patient_id:
            return jsonify({'error': 'patient_id required'}), 400
        patient = db.session.get(User, patient_id)
        if not patient or patient.doctor_id != me.id:
            return jsonify({'error': 'forbidden patient'}), 403
    elif role != 'admin':
        return jsonify({'error': 'forbidden'}), 403

    records = HealthRecord.query.filter_by(patient_id=patient_id).order_by(HealthRecord.id.desc()).all()
    return jsonify([
        {
            'id': r.id,
            'patient_id': r.patient_id,
            'record_type': r.record_type,
            'value': r.get_value(current_app.config),
            'unit': r.unit,
            'measured_at': r.measured_at.isoformat(),
        }
        for r in records
    ])


@api.post('/patient/reminders')
@jwt_required()
def create_reminder():
    me = _current_user()
    if me.role not in {'patient', 'doctor'}:
        return jsonify({'error': 'patient/doctor only'}), 403
    data = request.get_json() or {}
    if data.get('reminder_type') not in {'medication', 'diet'}:
        return jsonify({'error': 'reminder_type invalid'}), 400
    patient_id = data.get('patient_id', me.id)
    if me.role == 'doctor':
        patient = db.session.get(User, patient_id)
        if not patient or patient.doctor_id != me.id:
            return jsonify({'error': 'forbidden patient'}), 403
    reminder = Reminder(
        patient_id=patient_id,
        reminder_type=data['reminder_type'],
        content=data.get('content', ''),
        remind_time=data.get('remind_time', '08:00'),
    )
    db.session.add(reminder)
    db.session.commit()
    return jsonify({'id': reminder.id})


@api.get('/patient/reminders')
@jwt_required()
def list_reminders():
    me = _current_user()
    patient_id = _allowed_patient_id(me) if me.role in {'patient', 'family'} else request.args.get('patient_id', type=int)
    if me.role == 'doctor' and patient_id:
        patient = db.session.get(User, patient_id)
        if not patient or patient.doctor_id != me.id:
            return jsonify({'error': 'forbidden patient'}), 403
    if me.role == 'admin' and not patient_id:
        return jsonify({'error': 'patient_id required'}), 400
    reminders = Reminder.query.filter_by(patient_id=patient_id).all()
    return jsonify([{'id': r.id, 'reminder_type': r.reminder_type, 'content': r.content, 'remind_time': r.remind_time} for r in reminders])


@api.post('/messages')
@jwt_required()
def send_message():
    me = _current_user()
    data = request.get_json() or {}
    receiver = db.session.get(User, data.get('receiver_id'))
    if not receiver:
        return jsonify({'error': 'receiver not found'}), 404
    allowed = (
        (me.role == 'patient' and receiver.role == 'doctor' and me.doctor_id == receiver.id)
        or (me.role == 'doctor' and receiver.role == 'patient' and receiver.doctor_id == me.id)
        or me.role == 'admin'
    )
    if not allowed:
        return jsonify({'error': 'forbidden'}), 403
    msg = Message(sender_id=me.id, receiver_id=receiver.id, content=data.get('content', ''))
    db.session.add(msg)
    db.session.commit()
    return jsonify({'id': msg.id})


@api.get('/messages')
@jwt_required()
def list_messages():
    me = _current_user()
    messages = Message.query.filter((Message.sender_id == me.id) | (Message.receiver_id == me.id)).order_by(Message.id.desc()).all()
    return jsonify([
        {'id': m.id, 'sender_id': m.sender_id, 'receiver_id': m.receiver_id, 'content': m.content, 'created_at': m.created_at.isoformat()}
        for m in messages
    ])


@api.get('/admin/users')
@jwt_required()
def admin_users():
    if get_jwt().get('role') != 'admin':
        return jsonify({'error': 'admin only'}), 403
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([u.to_dict() for u in users])


@api.get('/doctor/patients')
@jwt_required()
def doctor_patients():
    me = _current_user()
    if me.role != 'doctor':
        return jsonify({'error': 'doctor only'}), 403
    users = User.query.filter_by(role='patient', doctor_id=me.id).all()
    return jsonify([u.to_dict() for u in users])
