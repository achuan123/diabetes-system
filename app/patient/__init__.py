from flask import Blueprint

patient_bp = Blueprint('patient', __name__)

from app.patient import routes  # noqa: F401, E402
