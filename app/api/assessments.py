from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Patient, RiskAssessment, Notification
from app.services import RiskAssessmentService, MessageService
from app.schemas import AssessmentResponseSchema
import logging

logger = logging.getLogger(__name__)

assessments_bp = Blueprint('assessments', __name__)

@assessments_bp.route('/assess-risk/<int:patient_id>', methods=['POST'])
def assess_risk(patient_id):
    """Assess risk for a patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # Perform risk assessment
        risk_data = RiskAssessmentService.assess_risk(patient)
        
        # Save risk assessment to database
        risk_assessment = RiskAssessment(
            patient_id=patient.id,
            risk_level=risk_data['risk_level'],
            heat_wave_risk=risk_data['heat_wave_risk'],
            risk_score=risk_data['risk_score']
        )
        risk_assessment.set_risk_factors(risk_data['factors'])
        risk_assessment.set_weather_data(risk_data['weather_data'])
        
        db.session.add(risk_assessment)
        db.session.commit()
        
        # Create notification
        notification = MessageService.create_notification(patient, risk_data)
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'risk_level': risk_data['risk_level'],
            'risk_score': risk_data['risk_score'],
            'factors': risk_data['factors'],
            'heat_wave_risk': risk_data['heat_wave_risk'],
            'weather_data': risk_data['weather_data'],
            'notification_created': notification is not None,
            'assessment_id': risk_assessment.id
        })
        
    except Exception as e:
        logger.error(f"Error assessing risk: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to assess risk'
        }), 500

@assessments_bp.route('/risk/<int:patient_id>', methods=['GET'])
def get_risk_assessment(patient_id):
    """Get latest risk assessment for a patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # Get latest risk assessment
        risk_assessment = RiskAssessment.query.filter_by(
            patient_id=patient_id
        ).order_by(RiskAssessment.assessment_date.desc()).first()
        
        if not risk_assessment:
            return jsonify({
                'success': False,
                'error': 'No risk assessment found'
            }), 404
        
        return jsonify({
            'success': True,
            'assessment': risk_assessment.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting risk assessment: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get risk assessment'
        }), 500

@assessments_bp.route('/risk/<int:patient_id>/history', methods=['GET'])
def get_risk_history(patient_id):
    """Get risk assessment history for a patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        risk_assessments = RiskAssessment.query.filter_by(
            patient_id=patient_id
        ).order_by(RiskAssessment.assessment_date.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'assessments': [ra.to_dict() for ra in risk_assessments.items],
            'total': risk_assessments.total,
            'pages': risk_assessments.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Error getting risk history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get risk history'
        }), 500
