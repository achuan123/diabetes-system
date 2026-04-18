from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from app.admin import admin_bp
from app.decorators import admin_required
from app.models import User, Patient, GlucoseRecord, ExerciseRecord, Reminder, Consultation, FamilyMember
from app import db
from config import Config


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_patients = Patient.query.count()
    total_doctors = User.query.filter_by(role='doctor').count()

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_glucose = GlucoseRecord.query.filter(
        GlucoseRecord.measure_time >= seven_days_ago
    ).count()

    abnormal_count = GlucoseRecord.query.filter(
        GlucoseRecord.measure_time >= seven_days_ago,
        db.or_(
            GlucoseRecord.value > Config.GLUCOSE_HIGH,
            GlucoseRecord.value < Config.GLUCOSE_LOW
        )
    ).count()

    return render_template(
        'admin/dashboard.html',
        total_patients=total_patients,
        total_doctors=total_doctors,
        recent_glucose=recent_glucose,
        abnormal_count=abnormal_count
    )


@admin_bp.route('/dashboard/chart_data')
@admin_required
def chart_data():
    today = datetime.utcnow().date()
    result = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        start = datetime.combine(day, datetime.min.time())
        end = datetime.combine(day, datetime.max.time())
        count = GlucoseRecord.query.filter(
            GlucoseRecord.measure_time >= start,
            GlucoseRecord.measure_time <= end
        ).count()
        result.append({'date': day.strftime('%m-%d'), 'count': count})

    return jsonify(result)


@admin_bp.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    if request.method == 'POST':
        form_action = request.form.get('form_action')

        if form_action == 'add_doctor':
            email = request.form.get('email', '').strip()
            name = request.form.get('name', '').strip()
            password = request.form.get('password', '')

            if not email or not password:
                flash('邮箱和密码不能为空。', 'danger')
            elif User.query.filter_by(email=email).first():
                flash('该邮箱已被注册。', 'danger')
            else:
                user = User(email=email, name=name, role='doctor')
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash(f'医生账号 {email} 创建成功！', 'success')

        return redirect(url_for('admin.users'))

    doctors = User.query.filter_by(role='doctor').order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', doctors=doctors)


@admin_bp.route('/users/<int:user_id>/reset_password', methods=['POST'])
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password', '').strip()
    if not new_password:
        flash('新密码不能为空。', 'danger')
    else:
        user.set_password(new_password)
        db.session.commit()
        flash(f'用户 {user.email} 的密码已重置。', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/patients', methods=['GET', 'POST'])
@admin_required
def patients():
    if request.method == 'POST':
        form_action = request.form.get('form_action')

        if form_action == 'add_patient':
            name = request.form.get('name', '').strip()
            gender = request.form.get('gender')
            age = request.form.get('age', type=int)
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            diabetes_type = request.form.get('diabetes_type', '').strip()
            doctor_id = request.form.get('doctor_id', type=int)

            if not name:
                flash('患者姓名不能为空。', 'danger')
            else:
                patient = Patient(
                    name=name,
                    gender=gender if gender else None,
                    age=age,
                    phone=phone if phone else None,
                    address=address if address else None,
                    diabetes_type=diabetes_type if diabetes_type else None,
                    doctor_id=doctor_id if doctor_id else None
                )
                db.session.add(patient)
                db.session.commit()
                flash(f'患者 {name} 添加成功！', 'success')

        return redirect(url_for('admin.patients'))

    search = request.args.get('search', '').strip()
    query = Patient.query
    if search:
        query = query.filter(Patient.name.ilike(f'%{search}%'))
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Patient.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    doctors = User.query.filter_by(role='doctor').order_by(User.name).all()
    return render_template('admin/patients.html', pagination=pagination, doctors=doctors, search=search)


@admin_bp.route('/patients/<int:patient_id>/delete', methods=['POST'])
@admin_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    name = patient.name
    try:
        GlucoseRecord.query.filter_by(patient_id=patient_id).delete()
        ExerciseRecord.query.filter_by(patient_id=patient_id).delete()
        Reminder.query.filter_by(patient_id=patient_id).delete()
        Consultation.query.filter_by(patient_id=patient_id).delete()
        FamilyMember.query.filter_by(patient_id=patient_id).delete()
        db.session.delete(patient)
        db.session.commit()
        flash(f'患者 {name} 及其关联记录已删除。', 'success')
    except Exception:
        db.session.rollback()
        current_app.logger.exception('删除患者 %s 时发生错误', patient_id)
        flash('删除失败，请稍后重试。', 'danger')
    return redirect(url_for('admin.patients'))


@admin_bp.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    doctors = User.query.filter_by(role='doctor').order_by(User.name).all()

    if request.method == 'POST':
        patient.name = request.form.get('name', '').strip() or patient.name
        gender = request.form.get('gender')
        patient.gender = gender if gender else None
        age = request.form.get('age', type=int)
        patient.age = age
        patient.phone = request.form.get('phone', '').strip() or None
        patient.address = request.form.get('address', '').strip() or None
        patient.diabetes_type = request.form.get('diabetes_type', '').strip() or None
        doctor_id = request.form.get('doctor_id', type=int)
        patient.doctor_id = doctor_id if doctor_id else None
        db.session.commit()
        flash(f'患者 {patient.name} 信息已更新。', 'success')
        return redirect(url_for('admin.patients'))

    return render_template('admin/edit_patient.html', patient=patient, doctors=doctors)
