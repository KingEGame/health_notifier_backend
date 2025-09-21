from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api import patients, assessments, notifications, health, health_facilities, emergency_notifications, risk_patients
