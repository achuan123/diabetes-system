from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, flash, jsonify, abort
from app.doctor import doctor_bp
from app.decorators import doctor_required
from app.models import Patient, GlucoseRecord, ExerciseRecord, Reminder, User, Consultation
from app import db
from config import Config


@doctor_bp.route('/dashboard')
@doctor_required
def dashboard():
    doctor_id = session['user_id']
    patient_count = Patient.query.filter_by(doctor_id=doctor_id).count()

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    abnormal_count = (
        db.session.query(GlucoseRecord)
        .join(Patient)
        .filter(
            Patient.doctor_id == doctor_id,
            GlucoseRecord.measure_time >= seven_days_ago,
            db.or_(
                GlucoseRecord.value > Config.GLUCOSE_HIGH,
                GlucoseRecord.value < Config.GLUCOSE_LOW
            )
        )
        .count()
    )

    reminder_count = (
        db.session.query(Reminder)
        .filter_by(doctor_id=doctor_id)
        .count()
    )

    return render_template(
        'doctor/dashboard.html',
        patient_count=patient_count,
        abnormal_count=abnormal_count,
        reminder_count=reminder_count
    )


@doctor_bp.route('/patients')
@doctor_required
def patients():
    doctor_id = session['user_id']
    search = request.args.get('search', '').strip()
    query = Patient.query.filter_by(doctor_id=doctor_id)
    if search:
        query = query.filter(Patient.name.ilike(f'%{search}%'))
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Patient.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('doctor/patients.html', pagination=pagination, search=search)


@doctor_bp.route('/patients/<int:patient_id>', methods=['GET', 'POST'])
@doctor_required
def patient_detail(patient_id):
    doctor_id = session['user_id']
    patient = Patient.query.filter_by(id=patient_id, doctor_id=doctor_id).first_or_404()

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'glucose':
            try:
                value = float(request.form.get('value'))
                measure_time_str = request.form.get('measure_time')
                measure_time = datetime.strptime(measure_time_str, '%Y-%m-%dT%H:%M')
                meal_status = request.form.get('meal_status')
                remark = request.form.get('remark', '').strip()
                record = GlucoseRecord(
                    patient_id=patient_id,
                    value=value,
                    measure_time=measure_time,
                    meal_status=meal_status if meal_status else None,
                    remark=remark if remark else None
                )
                db.session.add(record)
                db.session.commit()
                flash('血糖记录添加成功！', 'success')
            except (ValueError, TypeError):
                flash('输入数据有误，请检查后重试。', 'danger')

        elif form_type == 'exercise':
            try:
                exercise_type = request.form.get('exercise_type', '').strip()
                duration_raw = request.form.get('duration', '').strip()
                calories_raw = request.form.get('calories', '').strip()
                duration = int(duration_raw) if duration_raw else None
                calories = int(calories_raw) if calories_raw else None
                intensity = request.form.get('intensity')
                record_time_str = request.form.get('record_time')
                record_time = datetime.strptime(record_time_str, '%Y-%m-%dT%H:%M')
                remark = request.form.get('remark', '').strip()
                record = ExerciseRecord(
                    patient_id=patient_id,
                    exercise_type=exercise_type if exercise_type else None,
                    duration=duration,
                    calories=calories,
                    intensity=intensity if intensity else None,
                    record_time=record_time,
                    remark=remark if remark else None
                )
                db.session.add(record)
                db.session.commit()
                flash('运动记录添加成功！', 'success')
            except (ValueError, TypeError):
                flash('输入数据有误，请检查后重试。', 'danger')

        return redirect(url_for('doctor.patient_detail', patient_id=patient_id))

    glucose_records = patient.glucose_records.limit(20).all()
    exercise_records = patient.exercise_records.limit(20).all()

    return render_template(
        'doctor/patient_detail.html',
        patient=patient,
        glucose_records=glucose_records,
        exercise_records=exercise_records,
        glucose_high=Config.GLUCOSE_HIGH,
        glucose_low=Config.GLUCOSE_LOW
    )


@doctor_bp.route('/patients/<int:patient_id>/glucose_data')
@doctor_required
def glucose_data(patient_id):
    doctor_id = session['user_id']
    patient = Patient.query.filter_by(id=patient_id, doctor_id=doctor_id).first_or_404()
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    records = (
        patient.glucose_records
        .filter(GlucoseRecord.measure_time >= thirty_days_ago)
        .order_by(GlucoseRecord.measure_time.asc())
        .all()
    )
    data = {
        'labels': [r.measure_time.strftime('%m-%d %H:%M') for r in records],
        'values': [r.value for r in records],
        'glucose_high': Config.GLUCOSE_HIGH,
        'glucose_low': Config.GLUCOSE_LOW
    }
    return jsonify(data)


@doctor_bp.route('/reminders', methods=['GET', 'POST'])
@doctor_required
def reminders():
    doctor_id = session['user_id']
    doctor_patients = Patient.query.filter_by(doctor_id=doctor_id).order_by(Patient.name).all()

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        content = request.form.get('content', '').strip()
        level = request.form.get('level')

        if not patient_id or not content:
            flash('请选择患者并填写提醒内容。', 'danger')
        else:
            patient = Patient.query.filter_by(id=patient_id, doctor_id=doctor_id).first()
            if not patient:
                abort(403)
            reminder = Reminder(
                doctor_id=doctor_id,
                patient_id=patient_id,
                content=content,
                level=level if level else 'low'
            )
            db.session.add(reminder)
            db.session.commit()
            flash('提醒创建成功！', 'success')
        return redirect(url_for('doctor.reminders'))

    page = request.args.get('page', 1, type=int)
    pagination = (
        Reminder.query
        .filter_by(doctor_id=doctor_id)
        .order_by(Reminder.created_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    return render_template('doctor/reminders.html', pagination=pagination, patients=doctor_patients)


@doctor_bp.route('/consultations')
@doctor_required
def consultations():
    doctor_id = session['user_id']
    doctor_patients = Patient.query.filter_by(doctor_id=doctor_id).order_by(Patient.name).all()
    selected_patient_id = request.args.get('patient_id', type=int)
    selected_patient = None
    messages = []
    if selected_patient_id:
        selected_patient = Patient.query.filter_by(id=selected_patient_id, doctor_id=doctor_id).first_or_404()
        messages = (
            Consultation.query
            .filter_by(patient_id=selected_patient_id)
            .order_by(Consultation.created_at.asc())
            .all()
        )
    return render_template(
        'doctor/consultation.html',
        doctor_patients=doctor_patients,
        selected_patient=selected_patient,
        messages=messages
    )


@doctor_bp.route('/consultations/reply', methods=['POST'])
@doctor_required
def consultation_reply():
    doctor_id = session['user_id']
    patient_id = request.form.get('patient_id', type=int)
    content = request.form.get('content', '').strip()
    patient = Patient.query.filter_by(id=patient_id, doctor_id=doctor_id).first_or_404()
    if content:
        db.session.add(Consultation(
            patient_id=patient_id,
            doctor_id=doctor_id,
            sender='doctor',
            content=content
        ))
        db.session.commit()
        flash('回复已发送。', 'success')
    else:
        flash('回复内容不能为空。', 'danger')
    return redirect(url_for('doctor.consultations', patient_id=patient_id))
