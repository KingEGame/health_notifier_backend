from flask import Blueprint, request, jsonify
from app.models.csv_models import csv_manager
from app.services import RiskAssessmentService, MessageService
import logging

logger = logging.getLogger(__name__)

csv_risk_patients_bp = Blueprint('csv_risk_patients', __name__)

@csv_risk_patients_bp.route('/risk-patients', methods=['GET'])
def get_risk_patients():
    """Get all patients with risk assessments and their risk levels"""
    try:
        # Get query parameters
        risk_level = request.args.get('risk_level')  # 'low', 'medium', 'high'
        location = request.args.get('location')  # zip_code
        include_ai_suggestions = request.args.get('include_ai_suggestions', 'false').lower() == 'true'
        
        # Get all patients
        patients = csv_manager.get_all_patients()
        
        if not patients:
            return jsonify({
                'success': True,
                'message': 'No patients found',
                'risk_patients': [],
                'summary': {
                    'total_patients': 0,
                    'risk_distribution': {'low': 0, 'medium': 0, 'high': 0},
                    'patients_at_risk': 0
                }
            })
        
        # Analyze each patient
        risk_patients = []
        risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
        patients_at_risk = 0
        
        for patient in patients:
            try:
                # Filter by location if specified
                if location and patient.zip_code != location:
                    continue
                
                # Perform risk assessment
                risk_data = RiskAssessmentService.assess_risk(patient)
                patient_risk_level = risk_data['risk_level']
                
                # Filter by risk level if specified
                if risk_level and patient_risk_level != risk_level:
                    continue
                
                risk_distribution[patient_risk_level] += 1
                
                if patient_risk_level in ['medium', 'high']:
                    patients_at_risk += 1
                
                # Prepare patient data
                patient_info = {
                    'patient_id': patient.id,
                    'name': patient.name,
                    'age': patient.age,
                    'zip_code': patient.zip_code,
                    'phone_number': patient.phone_number,
                    'email': patient.email,
                    'address': patient.address,
                    'pregnancy_weeks': patient.weeks_pregnant,
                    'pregnancy_icd10': patient.pregnancy_icd10,
                    'pregnancy_description': patient.pregnancy_description,
                    'comorbidity_icd10': patient.comorbidity_icd10,
                    'comorbidity_description': patient.comorbidity_description,
                    'risk_level': patient_risk_level,
                    'risk_score': risk_data['risk_score'],
                    'heat_wave_risk': risk_data.get('heat_wave_risk', False),
                    'risk_factors': risk_data.get('factors', {}),
                    'weather_conditions': risk_data.get('weather_data', {}),
                    'medications': patient.get_medications_list(),
                    'conditions': patient.get_conditions()
                }
                
                # Add AI suggestions if requested
                if include_ai_suggestions:
                    try:
                        from app.services.ai_service import AIService
                        ai_suggestions = AIService.get_risk_recommendations(patient, risk_data)
                        patient_info['ai_suggestions'] = ai_suggestions
                    except Exception as e:
                        logger.warning(f"Failed to get AI suggestions for patient {patient.id}: {e}")
                        patient_info['ai_suggestions'] = {
                            'error': 'AI suggestions unavailable',
                            'fallback_recommendations': _get_fallback_recommendations(patient_risk_level, risk_data)
                        }
                
                risk_patients.append(patient_info)
                
            except Exception as e:
                logger.warning(f"Error processing patient {patient.id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'risk_patients': risk_patients,
            'summary': {
                'total_patients': len(risk_patients),
                'risk_distribution': risk_distribution,
                'patients_at_risk': patients_at_risk,
                'filters_applied': {
                    'risk_level': risk_level,
                    'location': location,
                    'include_ai_suggestions': include_ai_suggestions
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting risk patients: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get risk patients'
        }), 500

@csv_risk_patients_bp.route('/risk-patients/<int:patient_id>', methods=['GET'])
def get_patient_risk_details(patient_id):
    """Get detailed risk information for a specific patient"""
    try:
        patient = csv_manager.get_patient_by_id(patient_id)
        
        if not patient:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        # Perform comprehensive risk assessment
        risk_data = RiskAssessmentService.assess_risk(patient)
        
        # Get AI suggestions
        ai_suggestions = None
        try:
            from app.services.ai_service import AIService
            ai_suggestions = AIService.get_risk_recommendations(patient, risk_data)
        except Exception as e:
            logger.warning(f"Failed to get AI suggestions for patient {patient_id}: {e}")
            ai_suggestions = {
                'error': 'AI suggestions unavailable',
                'fallback_recommendations': _get_fallback_recommendations(risk_data['risk_level'], risk_data)
            }
        
        # Get risk assessment history
        risk_history = csv_manager.get_risk_assessments_by_patient(patient_id)
        
        return jsonify({
            'success': True,
            'patient': {
                'patient_id': patient.id,
                'name': patient.name,
                'age': patient.age,
                'zip_code': patient.zip_code,
                'phone_number': patient.phone_number,
                'email': patient.email,
                'address': patient.address,
                'pregnancy_weeks': patient.weeks_pregnant,
                'pregnancy_icd10': patient.pregnancy_icd10,
                'pregnancy_description': patient.pregnancy_description,
                'comorbidity_icd10': patient.comorbidity_icd10,
                'comorbidity_description': patient.comorbidity_description,
                'medications': patient.get_medications_list(),
                'conditions': patient.get_conditions()
            },
            'current_risk': {
                'risk_level': risk_data['risk_level'],
                'risk_score': risk_data['risk_score'],
                'heat_wave_risk': risk_data.get('heat_wave_risk', False),
                'risk_factors': risk_data.get('factors', {}),
                'weather_conditions': risk_data.get('weather_data', {})
            },
            'ai_suggestions': ai_suggestions,
            'risk_history': [ra.to_dict() for ra in risk_history]
        })
        
    except Exception as e:
        logger.error(f"Error getting patient risk details: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get patient risk details'
        }), 500

@csv_risk_patients_bp.route('/risk-patients/summary', methods=['GET'])
def get_risk_summary():
    """Get summary of all patients' risk levels"""
    try:
        patients = csv_manager.get_all_patients()
        
        if not patients:
            return jsonify({
                'success': True,
                'summary': {
                    'total_patients': 0,
                    'risk_distribution': {'low': 0, 'medium': 0, 'high': 0},
                    'patients_at_risk': 0,
                    'extreme_heat_risk': 0,
                    'average_risk_score': 0
                }
            })
        
        risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
        patients_at_risk = 0
        extreme_heat_risk = 0
        total_risk_score = 0
        risk_scores = []
        
        for patient in patients:
            try:
                risk_data = RiskAssessmentService.assess_risk(patient)
                risk_level = risk_data['risk_level']
                risk_score = risk_data['risk_score']
                
                risk_distribution[risk_level] += 1
                total_risk_score += risk_score
                risk_scores.append(risk_score)
                
                if risk_level in ['medium', 'high']:
                    patients_at_risk += 1
                
                if risk_data.get('heat_wave_risk', False):
                    extreme_heat_risk += 1
                    
            except Exception as e:
                logger.warning(f"Error processing patient {patient.id}: {e}")
                continue
        
        average_risk_score = total_risk_score / len(patients) if patients else 0
        
        return jsonify({
            'success': True,
            'summary': {
                'total_patients': len(patients),
                'risk_distribution': risk_distribution,
                'patients_at_risk': patients_at_risk,
                'extreme_heat_risk': extreme_heat_risk,
                'average_risk_score': round(average_risk_score, 2),
                'risk_percentages': {
                    'low': round((risk_distribution['low'] / len(patients)) * 100, 1),
                    'medium': round((risk_distribution['medium'] / len(patients)) * 100, 1),
                    'high': round((risk_distribution['high'] / len(patients)) * 100, 1)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting risk summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get risk summary'
        }), 500

@csv_risk_patients_bp.route('/risk-patients/<int:patient_id>/comprehensive', methods=['GET'])
def get_comprehensive_risk_assessment(patient_id):
    """Get comprehensive risk assessment for a specific patient"""
    try:
        patient = csv_manager.get_patient_by_id(patient_id)
        
        if not patient:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        # Get comprehensive risk assessment
        comprehensive_risk = RiskAssessmentService.get_comprehensive_risk_assessment(patient)
        
        # Add AI suggestions if available
        try:
            from app.services.ai_service import AIService
            ai_suggestions = AIService.get_risk_recommendations(patient, comprehensive_risk['basic_risk'])
            comprehensive_risk['ai_suggestions'] = ai_suggestions
        except Exception as e:
            logger.warning(f"Failed to get AI suggestions for patient {patient_id}: {e}")
            comprehensive_risk['ai_suggestions'] = {
                'error': 'AI suggestions unavailable',
                'fallback_recommendations': _get_fallback_recommendations(
                    comprehensive_risk['basic_risk']['risk_level'], 
                    comprehensive_risk['basic_risk']
                )
            }
        
        return jsonify({
            'success': True,
            'comprehensive_assessment': comprehensive_risk
        })
        
    except Exception as e:
        logger.error(f"Error getting comprehensive risk assessment: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get comprehensive risk assessment'
        }), 500

def _get_fallback_recommendations(risk_level, risk_data):
    """Get fallback recommendations when AI service is unavailable"""
    recommendations = []
    
    if risk_level == 'high':
        recommendations.extend([
            "Immediate medical consultation recommended",
            "Monitor vital signs closely",
            "Avoid extreme weather conditions",
            "Ensure emergency contact is available"
        ])
    elif risk_level == 'medium':
        recommendations.extend([
            "Regular medical check-ups recommended",
            "Monitor symptoms closely",
            "Follow prescribed medication schedule",
            "Maintain healthy lifestyle"
        ])
    else:
        recommendations.extend([
            "Continue regular prenatal care",
            "Maintain healthy diet and exercise",
            "Stay hydrated",
            "Regular medical check-ups"
        ])
    
    # Add weather-specific recommendations
    if risk_data.get('heat_wave_risk', False):
        recommendations.extend([
            "Stay indoors during peak heat hours",
            "Ensure adequate hydration",
            "Use air conditioning if available",
            "Wear light, loose clothing"
        ])
    
    return recommendations
