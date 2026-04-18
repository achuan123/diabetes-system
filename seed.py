import random
import sys
import os
from datetime import datetime, timedelta

# Allow running from project root
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User, Patient, GlucoseRecord, ExerciseRecord, Reminder, Consultation, FamilyMember

app = create_app()

DOCTOR_NAMES = [
    '张医生', '李医生', '王医生', '刘医生', '陈医生',
    '杨医生', '赵医生', '黄医生', '周医生', '吴医生'
]

PATIENT_NAMES = [
    '赵建国', '钱秀英', '孙志远', '李淑华', '周文明',
    '吴美丽', '郑国华', '王凤英', '冯建华', '陈桂英',
    '楚天阔', '魏紫霞', '沈德才', '韩玉兰', '杨广平',
    '朱彩云', '秦志强', '许翠花', '何明德', '吕桂芬'
]

EXERCISE_TYPES = ['步行', '慢跑', '游泳', '骑车', '太极拳', '广场舞', '瑜伽', '爬山']
DIABETES_TYPES = ['2型糖尿病', '1型糖尿病', '2型糖尿病', '2型糖尿病', '2型糖尿病']
GENDERS = ['male', 'female']
PROVINCES = ['北京市朝阳区', '上海市浦东新区', '广州市天河区', '深圳市南山区', '成都市锦江区',
             '杭州市西湖区', '武汉市江汉区', '南京市玄武区', '重庆市渝中区', '西安市碑林区']
MEAL_STATUSES = ['before_meal', 'after_meal', 'fasting', 'random']
INTENSITIES = ['low', 'medium', 'high']
REMINDER_CONTENTS = [
    '请注意按时服药，避免漏服。',
    '建议增加每日步行量，目标每天7000步。',
    '本周血糖偏高，请减少碳水化合物摄入。',
    '请按时复诊，携带近期血糖记录。',
    '运动后注意补充适量食物，预防低血糖。',
    '近期低血糖发作频繁，请随身携带糖果。',
    '请定期监测血压，糖尿病患者需关注心血管健康。',
    '建议戒烟，吸烟会加重胰岛素抵抗。',
    '足部护理非常重要，每天检查双足是否有破损。',
    '本月要进行糖化血红蛋白检测，请预约检查。'
]


def random_glucose():
    """Generate a glucose value, mostly normal, occasionally abnormal."""
    r = random.random()
    if r < 0.15:
        return round(random.uniform(11.2, 18.0), 1)
    elif r < 0.20:
        return round(random.uniform(2.5, 3.8), 1)
    else:
        return round(random.uniform(4.5, 10.5), 1)


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('Tables created.')

        # Admin user
        admin = User(email='admin@123.com', name='管理员', role='admin')
        admin.set_password('123456')
        db.session.add(admin)

        # Doctors
        doctors = []
        for i, name in enumerate(DOCTOR_NAMES, start=1):
            doc = User(
                email=f'Doctor{i}@123.com',
                name=name,
                role='doctor'
            )
            doc.set_password('123456')
            db.session.add(doc)
            doctors.append(doc)

        db.session.flush()
        print(f'Created 1 admin + {len(doctors)} doctors.')

        # Patients
        patients = []
        for i, pname in enumerate(PATIENT_NAMES):
            doctor = doctors[i % len(doctors)]
            patient = Patient(
                name=pname,
                gender=GENDERS[i % 2],
                age=random.randint(40, 75),
                phone=f'138{random.randint(10000000, 99999999)}',
                address=PROVINCES[i % len(PROVINCES)],
                diabetes_type=DIABETES_TYPES[i % len(DIABETES_TYPES)],
                doctor_id=doctor.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            patient.set_password('123456')
            db.session.add(patient)
            patients.append(patient)

        db.session.flush()
        print(f'Created {len(patients)} patients.')

        # Glucose records – 60 days, 1-3 per day
        now = datetime.utcnow()
        glucose_batch = []
        for patient in patients:
            for day_offset in range(60):
                day = now - timedelta(days=day_offset)
                records_per_day = random.randint(1, 3)
                for _ in range(records_per_day):
                    hour = random.choice([7, 9, 12, 14, 18, 21])
                    minute = random.randint(0, 59)
                    mtime = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    glucose_batch.append(GlucoseRecord(
                        patient_id=patient.id,
                        value=random_glucose(),
                        measure_time=mtime,
                        meal_status=random.choice(MEAL_STATUSES),
                        remark=None
                    ))

        db.session.bulk_save_objects(glucose_batch)
        print(f'Created {len(glucose_batch)} glucose records.')

        # Exercise records – 30 days, 1 per day occasionally skipping
        exercise_batch = []
        for patient in patients:
            for day_offset in range(30):
                if random.random() < 0.7:
                    day = now - timedelta(days=day_offset)
                    etype = random.choice(EXERCISE_TYPES)
                    duration = random.randint(20, 90)
                    intensity = random.choice(INTENSITIES)
                    cal_map = {'low': (80, 200), 'medium': (200, 400), 'high': (400, 700)}
                    lo, hi = cal_map[intensity]
                    calories = random.randint(lo, hi)
                    rtime = day.replace(hour=random.randint(6, 20), minute=random.randint(0, 59),
                                        second=0, microsecond=0)
                    exercise_batch.append(ExerciseRecord(
                        patient_id=patient.id,
                        exercise_type=etype,
                        duration=duration,
                        calories=calories,
                        intensity=intensity,
                        record_time=rtime
                    ))

        db.session.bulk_save_objects(exercise_batch)
        print(f'Created {len(exercise_batch)} exercise records.')

        # Reminders
        reminder_batch = []
        for i, patient in enumerate(patients):
            doctor = doctors[i % len(doctors)]
            num_reminders = random.randint(1, 3)
            for _ in range(num_reminders):
                reminder_batch.append(Reminder(
                    doctor_id=doctor.id,
                    patient_id=patient.id,
                    content=random.choice(REMINDER_CONTENTS),
                    level=random.choice(['low', 'medium', 'high', 'urgent']),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                ))

        db.session.bulk_save_objects(reminder_batch)
        print(f'Created {len(reminder_batch)} reminders.')

        # Consultations – a few sample exchanges per patient
        PATIENT_MESSAGES = [
            '医生，我最近血糖总是偏高，是不是需要调整药量？',
            '我前几天有些头晕，是低血糖的症状吗？',
            '请问我可以吃西瓜吗？听说含糖量高。',
            '我坚持步行锻炼，但血糖改善不明显，有什么建议？',
        ]
        DOCTOR_REPLIES = [
            '您好，建议您严格控制碳水化合物摄入，同时按时服药，下次复诊时我们详细讨论方案。',
            '头晕可能与低血糖有关，建议随身携带糖果，出现症状立即补充。',
            '西瓜含糖较高，建议少量食用，注意监测餐后血糖。',
            '运动很好！建议增加运动频率，每周5次以上，同时注意饮食控制。',
        ]
        consultation_batch = []
        for i, patient in enumerate(patients[:5]):
            doctor = doctors[i % len(doctors)]
            for j in range(random.randint(1, 2)):
                t = datetime.utcnow() - timedelta(days=random.randint(1, 14), hours=random.randint(0, 8))
                consultation_batch.append(Consultation(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    sender='patient',
                    content=PATIENT_MESSAGES[j % len(PATIENT_MESSAGES)],
                    created_at=t
                ))
                consultation_batch.append(Consultation(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    sender='doctor',
                    content=DOCTOR_REPLIES[j % len(DOCTOR_REPLIES)],
                    created_at=t + timedelta(hours=1)
                ))

        db.session.bulk_save_objects(consultation_batch)
        print(f'Created {len(consultation_batch)} consultation messages.')

        # Family members – 1-2 per patient for first 5 patients
        RELATIONS = ['配偶', '儿子', '女儿', '母亲', '父亲']
        FAMILY_NAMES = ['张伟', '李芳', '王明', '刘娜', '陈磊', '赵静', '孙辉', '周丽', '吴强', '郑敏']
        family_batch = []
        for i, patient in enumerate(patients[:8]):
            for j in range(random.randint(1, 2)):
                family_batch.append(FamilyMember(
                    patient_id=patient.id,
                    name=FAMILY_NAMES[(i + j) % len(FAMILY_NAMES)],
                    relation=RELATIONS[(i + j) % len(RELATIONS)],
                    phone=f'139{random.randint(10000000, 99999999)}'
                ))

        db.session.bulk_save_objects(family_batch)
        print(f'Created {len(family_batch)} family members.')

        db.session.commit()
        print('\n✅ Seed completed successfully!')
        print('   Admin:   admin@123.com / 123456')
        print('   Doctors: Doctor1@123.com ~ Doctor10@123.com / 123456')
        print('   Patients: use phone number + password 123456 to login at /patient/login')
        print('   (Run the app and check /admin/patients to find a patient\'s phone number)')


if __name__ == '__main__':
    seed()
