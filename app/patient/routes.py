from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash, current_app
from app.patient import patient_bp
from app.decorators import patient_required
from app.models import Patient, GlucoseRecord, ExerciseRecord, Reminder, Consultation, FamilyMember
from app import db
from config import Config


# ─── Auth ────────────────────────────────────────────────────────────────────

@patient_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'patient_id' in session:
        return redirect(url_for('patient.dashboard'))

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        patient = Patient.query.filter_by(phone=phone).first()
        if patient and patient.check_password(password):
            session['patient_id'] = patient.id
            session['patient_name'] = patient.name
            flash('登录成功，欢迎回来！', 'success')
            return redirect(url_for('patient.dashboard'))
        flash('手机号或密码错误，请重试。', 'danger')

    return render_template('patient/login.html')


@patient_bp.route('/logout')
def logout():
    session.pop('patient_id', None)
    session.pop('patient_name', None)
    flash('已退出登录。', 'info')
    return redirect(url_for('patient.login'))


# ─── Dashboard ───────────────────────────────────────────────────────────────

@patient_bp.route('/dashboard')
@patient_required
def dashboard():
    patient = Patient.query.get_or_404(session['patient_id'])
    latest_glucose = patient.glucose_records.first()
    latest_exercise = patient.exercise_records.first()
    unread_reminders = Reminder.query.filter_by(patient_id=patient.id).order_by(Reminder.created_at.desc()).limit(3).all()
    unread_consultations = Consultation.query.filter_by(
        patient_id=patient.id, sender='doctor'
    ).order_by(Consultation.created_at.desc()).limit(3).all()
    return render_template(
        'patient/dashboard.html',
        patient=patient,
        latest_glucose=latest_glucose,
        latest_exercise=latest_exercise,
        reminders=unread_reminders,
        consultations=unread_consultations,
        glucose_high=Config.GLUCOSE_HIGH,
        glucose_low=Config.GLUCOSE_LOW,
    )


# ─── Profile ─────────────────────────────────────────────────────────────────

@patient_bp.route('/profile')
@patient_required
def profile():
    patient = Patient.query.get_or_404(session['patient_id'])
    return render_template('patient/profile.html', patient=patient)


# ─── Glucose Records ─────────────────────────────────────────────────────────

@patient_bp.route('/glucose', methods=['GET', 'POST'])
@patient_required
def glucose():
    patient_id = session['patient_id']
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            try:
                value = float(request.form.get('value'))
                measure_time = datetime.strptime(request.form.get('measure_time'), '%Y-%m-%dT%H:%M')
                meal_status = request.form.get('meal_status') or None
                remark = request.form.get('remark', '').strip() or None
                db.session.add(GlucoseRecord(
                    patient_id=patient_id, value=value,
                    measure_time=measure_time, meal_status=meal_status, remark=remark
                ))
                db.session.commit()
                flash('血糖记录已添加。', 'success')
            except (ValueError, TypeError):
                flash('输入数据有误，请检查后重试。', 'danger')

        elif action == 'edit':
            record_id = request.form.get('record_id', type=int)
            record = GlucoseRecord.query.filter_by(id=record_id, patient_id=patient_id).first_or_404()
            try:
                record.value = float(request.form.get('value'))
                record.measure_time = datetime.strptime(request.form.get('measure_time'), '%Y-%m-%dT%H:%M')
                record.meal_status = request.form.get('meal_status') or None
                record.remark = request.form.get('remark', '').strip() or None
                db.session.commit()
                flash('血糖记录已更新。', 'success')
            except (ValueError, TypeError):
                flash('输入数据有误，请检查后重试。', 'danger')

        elif action == 'delete':
            record_id = request.form.get('record_id', type=int)
            record = GlucoseRecord.query.filter_by(id=record_id, patient_id=patient_id).first_or_404()
            db.session.delete(record)
            db.session.commit()
            flash('血糖记录已删除。', 'success')

        return redirect(url_for('patient.glucose'))

    page = request.args.get('page', 1, type=int)
    pagination = patient.glucose_records.paginate(page=page, per_page=15, error_out=False)
    return render_template(
        'patient/glucose.html',
        patient=patient, pagination=pagination,
        glucose_high=Config.GLUCOSE_HIGH, glucose_low=Config.GLUCOSE_LOW,
        now=datetime.utcnow()
    )


# ─── Exercise Records ─────────────────────────────────────────────────────────

@patient_bp.route('/exercise', methods=['GET', 'POST'])
@patient_required
def exercise():
    patient_id = session['patient_id']
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            try:
                exercise_type = request.form.get('exercise_type', '').strip() or None
                duration_raw = request.form.get('duration', '').strip()
                calories_raw = request.form.get('calories', '').strip()
                record_time = datetime.strptime(request.form.get('record_time'), '%Y-%m-%dT%H:%M')
                db.session.add(ExerciseRecord(
                    patient_id=patient_id,
                    exercise_type=exercise_type,
                    duration=int(duration_raw) if duration_raw else None,
                    calories=int(calories_raw) if calories_raw else None,
                    intensity=request.form.get('intensity') or None,
                    record_time=record_time,
                    remark=request.form.get('remark', '').strip() or None
                ))
                db.session.commit()
                flash('运动记录已添加。', 'success')
            except (ValueError, TypeError):
                flash('输入数据有误，请检查后重试。', 'danger')

        elif action == 'edit':
            record_id = request.form.get('record_id', type=int)
            record = ExerciseRecord.query.filter_by(id=record_id, patient_id=patient_id).first_or_404()
            try:
                record.exercise_type = request.form.get('exercise_type', '').strip() or None
                duration_raw = request.form.get('duration', '').strip()
                calories_raw = request.form.get('calories', '').strip()
                record.duration = int(duration_raw) if duration_raw else None
                record.calories = int(calories_raw) if calories_raw else None
                record.intensity = request.form.get('intensity') or None
                record.record_time = datetime.strptime(request.form.get('record_time'), '%Y-%m-%dT%H:%M')
                record.remark = request.form.get('remark', '').strip() or None
                db.session.commit()
                flash('运动记录已更新。', 'success')
            except (ValueError, TypeError):
                flash('输入数据有误，请检查后重试。', 'danger')

        elif action == 'delete':
            record_id = request.form.get('record_id', type=int)
            record = ExerciseRecord.query.filter_by(id=record_id, patient_id=patient_id).first_or_404()
            db.session.delete(record)
            db.session.commit()
            flash('运动记录已删除。', 'success')

        return redirect(url_for('patient.exercise'))

    page = request.args.get('page', 1, type=int)
    pagination = patient.exercise_records.paginate(page=page, per_page=15, error_out=False)
    return render_template(
        'patient/exercise.html',
        patient=patient, pagination=pagination, now=datetime.utcnow()
    )


# ─── Reminders ───────────────────────────────────────────────────────────────

@patient_bp.route('/reminders')
@patient_required
def reminders():
    patient_id = session['patient_id']
    page = request.args.get('page', 1, type=int)
    pagination = (
        Reminder.query
        .filter_by(patient_id=patient_id)
        .order_by(Reminder.created_at.desc())
        .paginate(page=page, per_page=15, error_out=False)
    )
    return render_template('patient/reminders.html', pagination=pagination)


# ─── Consultation ─────────────────────────────────────────────────────────────

@patient_bp.route('/consultation', methods=['GET', 'POST'])
@patient_required
def consultation():
    patient_id = session['patient_id']
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            msg = Consultation(
                patient_id=patient_id,
                doctor_id=patient.doctor_id,
                sender='patient',
                content=content
            )
            db.session.add(msg)
            db.session.commit()
            flash('消息已发送。', 'success')
        else:
            flash('消息内容不能为空。', 'danger')
        return redirect(url_for('patient.consultation'))

    messages = (
        Consultation.query
        .filter_by(patient_id=patient_id)
        .order_by(Consultation.created_at.asc())
        .all()
    )
    return render_template('patient/consultation.html', patient=patient, messages=messages)


# ─── Family Members ───────────────────────────────────────────────────────────

@patient_bp.route('/family', methods=['GET', 'POST'])
@patient_required
def family():
    patient_id = session['patient_id']

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            name = request.form.get('name', '').strip()
            relation = request.form.get('relation', '').strip() or None
            phone = request.form.get('phone', '').strip() or None
            if not name:
                flash('家属姓名不能为空。', 'danger')
            else:
                db.session.add(FamilyMember(
                    patient_id=patient_id, name=name, relation=relation, phone=phone
                ))
                db.session.commit()
                flash(f'家属「{name}」已添加。', 'success')

        elif action == 'delete':
            member_id = request.form.get('member_id', type=int)
            member = FamilyMember.query.filter_by(id=member_id, patient_id=patient_id).first_or_404()
            db.session.delete(member)
            db.session.commit()
            flash('家属信息已删除。', 'success')

        return redirect(url_for('patient.family'))

    members = FamilyMember.query.filter_by(patient_id=patient_id).order_by(FamilyMember.created_at.desc()).all()
    return render_template('patient/family.html', members=members)
